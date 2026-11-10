"""Tests des signatures, de la clé chiffrée au repos et de la rotation."""

import json

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from indelebile.merkle import JournalMerkle
from indelebile.signature import (
    PhraseSecreteIncorrecte,
    TeteSignee,
    Trousseau,
    chiffrer_cle,
    dechiffrer_cle,
    identifiant_cle,
    message_depot,
    signer_depot,
    signer_tete,
    verifier_signature,
)

PETITE_MEMOIRE = 8 * 1024  # Argon2 allégé pour que les tests restent rapides


def test_cle_chiffree_aller_retour():
    cle = Ed25519PrivateKey.generate()
    fichier = chiffrer_cle(cle, "corbeau-noir-42", memoire_kio=PETITE_MEMOIRE)
    texte = json.dumps(fichier)
    assert "corbeau" not in texte
    relue = dechiffrer_cle(json.loads(texte), "corbeau-noir-42")
    assert identifiant_cle(relue.public_key()) == fichier["identifiant"]


def test_mauvaise_phrase_secrete_rejetee():
    fichier = chiffrer_cle(Ed25519PrivateKey.generate(), "bonne", memoire_kio=PETITE_MEMOIRE)
    with pytest.raises(PhraseSecreteIncorrecte):
        dechiffrer_cle(fichier, "mauvaise")


def test_fichier_cle_altere_rejete():
    fichier = chiffrer_cle(Ed25519PrivateKey.generate(), "bonne", memoire_kio=PETITE_MEMOIRE)
    fichier["identifiant"] = "0" * 16  # lié au chiffrement comme donnée associée
    with pytest.raises(PhraseSecreteIncorrecte):
        dechiffrer_cle(fichier, "bonne")


def test_tete_signee_verifiee_et_alteration_detectee():
    cle = Ed25519PrivateKey.generate()
    j = JournalMerkle()
    for i in range(5):
        j.ajouter(f"flash-{i}".encode())
    trousseau = Trousseau.initial(cle.public_key(), 1000)
    tete = signer_tete(cle, len(j), j.racine(), 2000)
    assert trousseau.verifier_tete(tete)
    assert trousseau.verifier_tete(TeteSignee.depuis_dict(tete.vers_dict()))
    falsifiee = TeteSignee(6, tete.racine, tete.horodatage, tete.identifiant_cle, tete.signature)
    assert not trousseau.verifier_tete(falsifiee)
    inconnue = TeteSignee(5, tete.racine, 2000, "inconnue", tete.signature)
    assert not trousseau.verifier_tete(inconnue)
    avant = signer_tete(cle, 5, j.racine(), 999)
    assert not trousseau.verifier_tete(avant)


def test_signature_depot():
    cle = Ed25519PrivateKey.generate()
    sig = signer_depot(cle, b"\x01" * 32, 1234)
    assert verifier_signature(cle.public_key(), sig, message_depot(b"\x01" * 32, 1234))
    assert not verifier_signature(cle.public_key(), sig, message_depot(b"\x02" * 32, 1234))


def test_rotation_garde_les_anciennes_racines_verifiables():
    ancienne, nouvelle = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    t = Trousseau.initial(ancienne.public_key(), 0)
    tete_avant = signer_tete(ancienne, 3, b"\xaa" * 32, 100)
    nid = t.rotation(ancienne, nouvelle.public_key(), 500)
    assert t.active == nid
    tete_apres = signer_tete(nouvelle, 9, b"\xbb" * 32, 600)
    assert t.chaine_valide()
    assert t.verifier_tete(tete_avant)
    assert t.verifier_tete(tete_apres)
    # L'ancienne clé ne doit plus pouvoir signer après sa retraite.
    assert not t.verifier_tete(signer_tete(ancienne, 10, b"\xcc" * 32, 700))
    # Le trousseau survit à la sauvegarde.
    relu = Trousseau.depuis_json(t.vers_json())
    assert relu.verifier_tete(tete_avant) and relu.verifier_tete(tete_apres)


def test_rotation_par_une_cle_non_active_refusee():
    a, b = Ed25519PrivateKey.generate(), Ed25519PrivateKey.generate()
    t = Trousseau.initial(a.public_key(), 0)
    with pytest.raises(ValueError):
        t.rotation(b, b.public_key(), 10)


def test_passation_forgee_detectee():
    a, b, pirate = (Ed25519PrivateKey.generate() for _ in range(3))
    t = Trousseau.initial(a.public_key(), 0)
    t.rotation(a, b.public_key(), 10)
    # Un attaquant remplace la nouvelle clé par la sienne dans le fichier.
    donnees = json.loads(t.vers_json())
    from indelebile.signature import _b64, octets_publics

    donnees[1]["publique"] = _b64(octets_publics(pirate.public_key()))
    donnees[1]["identifiant"] = identifiant_cle(pirate.public_key())
    t_pirate = Trousseau.depuis_json(json.dumps(donnees))
    assert not t_pirate.chaine_valide()
    assert not t_pirate.verifier_tete(signer_tete(pirate, 1, b"\x00" * 32, 20))


def test_identifiant_incoherent_refuse():
    t = Trousseau.initial(Ed25519PrivateKey.generate().public_key(), 0)
    donnees = json.loads(t.vers_json())
    donnees[0]["identifiant"] = "f" * 16
    with pytest.raises(ValueError):
        Trousseau.depuis_json(json.dumps(donnees))
