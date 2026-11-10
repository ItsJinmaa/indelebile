"""Signatures Ed25519, clé chiffrée au repos, rotation des clés.

Arcane : IV · L'Empereur, celui qui scelle.

Trois idées :
1. Signer = prouver que c'est bien NOUS qui avons publié cette racine.
2. La clé privée n'est jamais écrite en clair sur le disque : elle est chiffrée
   (AES-256-GCM) avec une clé dérivée d'une phrase secrète par Argon2id,
   une fonction volontairement lente et gourmande en mémoire pour décourager
   les attaques par force brute.
3. Rotation : quand on change de clé, l'ancienne clé signe un « acte de
   passation » qui désigne la nouvelle. Les anciennes racines restent
   vérifiables avec l'ancienne clé publique, conservée dans le trousseau.
"""

from __future__ import annotations

import base64
import hashlib
import json
import os
import struct
from dataclasses import dataclass, field

from argon2.low_level import Type, hash_secret_raw
from cryptography.exceptions import InvalidSignature, InvalidTag
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    NoEncryption,
    PrivateFormat,
    PublicFormat,
)

DOMAINE_TETE = b"INDELEBILE/tete-de-journal/v1"
DOMAINE_PASSATION = b"INDELEBILE/passation-de-cle/v1"
DOMAINE_EMPREINTE = b"INDELEBILE/depot/v1"

# Paramètres Argon2id (recommandation OWASP : m >= 19 Mio, t >= 2).
ARGON2_TEMPS = 3
ARGON2_MEMOIRE_KIO = 64 * 1024
ARGON2_PARALLELISME = 4


class PhraseSecreteIncorrecte(Exception):
    """La phrase secrète ne déchiffre pas la clé (ou le fichier a été altéré)."""


def _b64(x: bytes) -> str:
    return base64.b64encode(x).decode()


def _unb64(x: str) -> bytes:
    return base64.b64decode(x)


def octets_publics(cle: Ed25519PublicKey) -> bytes:
    return cle.public_bytes(Encoding.Raw, PublicFormat.Raw)


def identifiant_cle(cle: Ed25519PublicKey) -> str:
    """Identifiant court et stable d'une clé publique (16 caractères hexadécimaux)."""
    return hashlib.sha256(octets_publics(cle)).hexdigest()[:16]


# ---------------------------------------------------------------- clé au repos
def _deriver(phrase: str, sel: bytes, temps: int, memoire: int, parallelisme: int) -> bytes:
    return hash_secret_raw(
        phrase.encode(), sel, time_cost=temps, memory_cost=memoire,
        parallelism=parallelisme, hash_len=32, type=Type.ID,
    )


def chiffrer_cle(cle: Ed25519PrivateKey, phrase: str, *, memoire_kio: int = ARGON2_MEMOIRE_KIO) -> dict:
    """Renvoie un dictionnaire JSON-isable : la clé privée chiffrée + les paramètres."""
    sel, nonce = os.urandom(16), os.urandom(12)
    params = {"temps": ARGON2_TEMPS, "memoire_kio": memoire_kio, "parallelisme": ARGON2_PARALLELISME}
    cle_kdf = _deriver(phrase, sel, params["temps"], params["memoire_kio"], params["parallelisme"])
    brut = cle.private_bytes(Encoding.Raw, PrivateFormat.Raw, NoEncryption())
    kid = identifiant_cle(cle.public_key())
    chiffre = AESGCM(cle_kdf).encrypt(nonce, brut, kid.encode())
    return {
        "format": "indelebile-cle-v1",
        "kdf": "argon2id",
        "params": params,
        "sel": _b64(sel),
        "chiffrement": "aes-256-gcm",
        "nonce": _b64(nonce),
        "chiffre": _b64(chiffre),
        "identifiant": kid,
        "publique": _b64(octets_publics(cle.public_key())),
    }


def dechiffrer_cle(fichier: dict, phrase: str) -> Ed25519PrivateKey:
    p = fichier["params"]
    cle_kdf = _deriver(phrase, _unb64(fichier["sel"]), p["temps"], p["memoire_kio"], p["parallelisme"])
    try:
        brut = AESGCM(cle_kdf).decrypt(
            _unb64(fichier["nonce"]), _unb64(fichier["chiffre"]), fichier["identifiant"].encode()
        )
    except InvalidTag as e:
        raise PhraseSecreteIncorrecte("phrase secrète incorrecte ou fichier de clé altéré") from e
    return Ed25519PrivateKey.from_private_bytes(brut)


# ------------------------------------------------------- têtes de journal
@dataclass(frozen=True)
class TeteSignee:
    """Tête de journal signée : (taille, racine, horodatage) + signature."""

    taille: int
    racine: bytes
    horodatage: int  # secondes depuis 1970 (UTC)
    identifiant_cle: str
    signature: bytes

    def message(self) -> bytes:
        return message_tete(self.taille, self.racine, self.horodatage)

    def vers_dict(self) -> dict:
        return {
            "taille": self.taille,
            "racine": self.racine.hex(),
            "horodatage": self.horodatage,
            "identifiant_cle": self.identifiant_cle,
            "signature": _b64(self.signature),
        }

    @classmethod
    def depuis_dict(cls, d: dict) -> "TeteSignee":
        return cls(d["taille"], bytes.fromhex(d["racine"]), d["horodatage"],
                   d["identifiant_cle"], _unb64(d["signature"]))


def message_tete(taille: int, racine: bytes, horodatage: int) -> bytes:
    """Message exact qui est signé. Le préfixe de domaine empêche de réutiliser
    une signature d'un autre contexte (ex. : faire passer un dépôt pour une tête)."""
    return DOMAINE_TETE + struct.pack(">QQ", taille, horodatage) + racine


def signer_tete(cle: Ed25519PrivateKey, taille: int, racine: bytes, horodatage: int) -> TeteSignee:
    sig = cle.sign(message_tete(taille, racine, horodatage))
    return TeteSignee(taille, racine, horodatage, identifiant_cle(cle.public_key()), sig)


def message_depot(empreinte: bytes, horodatage: int) -> bytes:
    return DOMAINE_EMPREINTE + struct.pack(">Q", horodatage) + empreinte


def signer_depot(cle: Ed25519PrivateKey, empreinte: bytes, horodatage: int) -> bytes:
    """Outil `signer` du Signataire : signe l'empreinte + l'horodatage d'une œuvre."""
    return cle.sign(message_depot(empreinte, horodatage))


def verifier_signature(publique: Ed25519PublicKey, signature: bytes, message: bytes) -> bool:
    try:
        publique.verify(signature, message)
        return True
    except InvalidSignature:
        return False


# ------------------------------------------------------------------ trousseau
@dataclass
class EntreeTrousseau:
    publique: Ed25519PublicKey
    valide_depuis: int
    valide_jusqu_a: int | None = None  # None = clé active
    passation: bytes | None = None  # signature de l'ancienne clé désignant celle-ci


def message_passation(ancienne: str, nouvelle: Ed25519PublicKey, date: int) -> bytes:
    return DOMAINE_PASSATION + ancienne.encode() + octets_publics(nouvelle) + struct.pack(">Q", date)


@dataclass
class Trousseau:
    """Toutes les clés publiques, anciennes comprises, et la chaîne de passations."""

    entrees: dict[str, EntreeTrousseau] = field(default_factory=dict)
    ordre: list[str] = field(default_factory=list)

    @classmethod
    def initial(cls, publique: Ed25519PublicKey, date: int) -> "Trousseau":
        t = cls()
        kid = identifiant_cle(publique)
        t.entrees[kid] = EntreeTrousseau(publique, date)
        t.ordre.append(kid)
        return t

    @property
    def active(self) -> str:
        return self.ordre[-1]

    def rotation(self, ancienne_privee: Ed25519PrivateKey, nouvelle: Ed25519PublicKey, date: int) -> str:
        """L'ancienne clé signe la passation, puis est retirée (mais conservée)."""
        ancien_id = identifiant_cle(ancienne_privee.public_key())
        if ancien_id != self.active:
            raise ValueError("seule la clé active peut désigner sa successeure")
        acte = ancienne_privee.sign(message_passation(ancien_id, nouvelle, date))
        self.entrees[ancien_id].valide_jusqu_a = date
        nid = identifiant_cle(nouvelle)
        self.entrees[nid] = EntreeTrousseau(nouvelle, date, None, acte)
        self.ordre.append(nid)
        return nid

    def chaine_valide(self) -> bool:
        """Chaque clé après la première doit avoir été désignée par la précédente."""
        for precedent, courant in zip(self.ordre, self.ordre[1:]):
            e = self.entrees[courant]
            msg = message_passation(precedent, e.publique, e.valide_depuis)
            if e.passation is None or not verifier_signature(self.entrees[precedent].publique, e.passation, msg):
                return False
        return True

    def verifier_tete(self, tete: TeteSignee) -> bool:
        """Valide si : clé connue, chaîne de passation intacte, signature correcte,
        et tête signée pendant la période de validité de la clé."""
        e = self.entrees.get(tete.identifiant_cle)
        if e is None or not self.chaine_valide():
            return False
        if tete.horodatage < e.valide_depuis:
            return False
        if e.valide_jusqu_a is not None and tete.horodatage > e.valide_jusqu_a:
            return False
        return verifier_signature(e.publique, tete.signature, tete.message())

    def vers_json(self) -> str:
        return json.dumps(
            [
                {
                    "identifiant": kid,
                    "publique": _b64(octets_publics(self.entrees[kid].publique)),
                    "valide_depuis": self.entrees[kid].valide_depuis,
                    "valide_jusqu_a": self.entrees[kid].valide_jusqu_a,
                    "passation": _b64(self.entrees[kid].passation) if self.entrees[kid].passation else None,
                }
                for kid in self.ordre
            ],
            indent=2,
        )

    @classmethod
    def depuis_json(cls, texte: str) -> "Trousseau":
        t = cls()
        for d in json.loads(texte):
            pub = Ed25519PublicKey.from_public_bytes(_unb64(d["publique"]))
            if identifiant_cle(pub) != d["identifiant"]:
                raise ValueError("identifiant de clé incohérent avec la clé publique")
            t.entrees[d["identifiant"]] = EntreeTrousseau(
                pub, d["valide_depuis"], d["valide_jusqu_a"],
                _unb64(d["passation"]) if d["passation"] else None,
            )
            t.ordre.append(d["identifiant"])
        return t
