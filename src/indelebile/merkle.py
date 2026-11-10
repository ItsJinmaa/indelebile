"""Journal append-only en arbre de Merkle, conforme au principe de la RFC 9162.

Arcane : II · La Papesse, gardienne du registre.

Idée en une phrase : chaque œuvre déposée devient une « feuille » ; les feuilles
sont hachées deux par deux jusqu'à une seule empreinte, la racine. Modifier une
seule feuille change la racine : c'est un tatouage, on ne retouche pas sans que
ça se voie.

Points clés de la RFC 9162 :
- une feuille est hachée avec le préfixe 0x00, un nœud interne avec 0x01
  (sinon un attaquant pourrait faire passer un nœud pour une feuille) ;
- l'arbre n'est pas forcément complet : on coupe toujours à la plus grande
  puissance de 2 strictement inférieure au nombre d'éléments.
"""

from __future__ import annotations

import hashlib

PREFIXE_FEUILLE = b"\x00"
PREFIXE_NOEUD = b"\x01"


def _sha256(donnees: bytes) -> bytes:
    return hashlib.sha256(donnees).digest()


def hash_feuille(donnees: bytes) -> bytes:
    """Empreinte d'une feuille : SHA-256(0x00 || données)."""
    return _sha256(PREFIXE_FEUILLE + donnees)


def hash_noeud(gauche: bytes, droite: bytes) -> bytes:
    """Empreinte d'un nœud interne : SHA-256(0x01 || gauche || droite)."""
    return _sha256(PREFIXE_NOEUD + gauche + droite)


def _plus_grande_puissance_de_2_inferieure(n: int) -> int:
    """Plus grand k = 2^i tel que k < n (n >= 2)."""
    k = 1
    while k * 2 < n:
        k *= 2
    return k


def _est_puissance_de_2(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


class JournalMerkle:
    """Journal où l'on peut seulement ajouter (append-only).

    Pour tenir 100 000 documents, on garde en mémoire les empreintes de tous les
    sous-arbres complets (tailles 1, 2, 4, 8...). Calculer une racine ou une
    preuve coûte alors environ log2(n) opérations au lieu de n.
    """

    def __init__(self) -> None:
        # niveaux[h][i] = empreinte du sous-arbre complet de taille 2^h
        # qui commence à la feuille i * 2^h.
        self._niveaux: list[list[bytes]] = [[]]

    # ------------------------------------------------------------------ ajout
    def __len__(self) -> int:
        return len(self._niveaux[0])

    def ajouter(self, donnees: bytes) -> int:
        """Ajoute une feuille et renvoie son index (0, 1, 2...)."""
        return self.ajouter_hash_feuille(hash_feuille(donnees))

    def ajouter_hash_feuille(self, empreinte: bytes) -> int:
        index = len(self)
        self._niveaux[0].append(empreinte)
        # Comme un compteur binaire : chaque paire complète crée un parent.
        h = 0
        while len(self._niveaux[h]) % 2 == 0:
            gauche, droite = self._niveaux[h][-2], self._niveaux[h][-1]
            if h + 1 == len(self._niveaux):
                self._niveaux.append([])
            self._niveaux[h + 1].append(hash_noeud(gauche, droite))
            h += 1
        return index

    def hash_feuille_a(self, index: int) -> bytes:
        return self._niveaux[0][index]

    # ---------------------------------------------------------------- racines
    def _sous_arbre(self, debut: int, fin: int) -> bytes:
        """MTH(D[debut:fin]) au sens de la RFC 9162."""
        n = fin - debut
        if n == 0:
            return _sha256(b"")
        if _est_puissance_de_2(n) and debut % n == 0:
            h = n.bit_length() - 1
            return self._niveaux[h][debut // n]
        k = _plus_grande_puissance_de_2_inferieure(n)
        return hash_noeud(self._sous_arbre(debut, debut + k), self._sous_arbre(debut + k, fin))

    def racine(self, taille: int | None = None) -> bytes:
        """Racine de l'arbre tel qu'il était quand il contenait `taille` feuilles."""
        taille = len(self) if taille is None else taille
        if not 0 <= taille <= len(self):
            raise ValueError(f"taille {taille} hors du journal (0..{len(self)})")
        return self._sous_arbre(0, taille)

    # ------------------------------------------------------ preuve d'inclusion
    def preuve_inclusion(self, index: int, taille: int | None = None) -> list[bytes]:
        """PATH(index, D[taille]) : les empreintes « sœurs » du chemin feuille → racine."""
        taille = len(self) if taille is None else taille
        if not 0 <= index < taille <= len(self):
            raise ValueError("index ou taille invalide pour une preuve d'inclusion")
        return self._chemin(index, 0, taille)

    def _chemin(self, m: int, debut: int, fin: int) -> list[bytes]:
        n = fin - debut
        if n == 1:
            return []
        k = _plus_grande_puissance_de_2_inferieure(n)
        if m < k:
            return self._chemin(m, debut, debut + k) + [self._sous_arbre(debut + k, fin)]
        return self._chemin(m - k, debut + k, fin) + [self._sous_arbre(debut, debut + k)]

    # ----------------------------------------------------- preuve de cohérence
    def preuve_coherence(self, ancienne: int, nouvelle: int | None = None) -> list[bytes]:
        """PROOF(ancienne, D[nouvelle]) : prouve que l'ancien journal est un début du nouveau."""
        nouvelle = len(self) if nouvelle is None else nouvelle
        if not 0 <= ancienne <= nouvelle <= len(self):
            raise ValueError("tailles invalides pour une preuve de cohérence")
        if ancienne == 0 or ancienne == nouvelle:
            return []
        return self._sous_preuve(ancienne, 0, nouvelle, True)

    def _sous_preuve(self, m: int, debut: int, fin: int, complet: bool) -> list[bytes]:
        n = fin - debut
        if m == n:
            return [] if complet else [self._sous_arbre(debut, fin)]
        k = _plus_grande_puissance_de_2_inferieure(n)
        if m <= k:
            return self._sous_preuve(m, debut, debut + k, complet) + [self._sous_arbre(debut + k, fin)]
        return self._sous_preuve(m - k, debut + k, fin, False) + [self._sous_arbre(debut, debut + k)]


# ---------------------------------------------------------------------------
# Vérification : n'utilise QUE la preuve et la racine, jamais le journal.
# C'est ce qui permet à un tiers de vérifier sans faire confiance au serveur.
# ---------------------------------------------------------------------------


def verifier_inclusion(
    hash_de_la_feuille: bytes, index: int, taille: int, preuve: list[bytes], racine: bytes
) -> bool:
    """Algorithme de la RFC 9162, section 2.1.3.2."""
    if index >= taille or index < 0:
        return False
    fn, sn = index, taille - 1
    r = hash_de_la_feuille
    for p in preuve:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            r = hash_noeud(p, r)
            if not fn & 1:
                while not fn & 1 and fn != 0:
                    fn >>= 1
                    sn >>= 1
        else:
            r = hash_noeud(r, p)
        fn >>= 1
        sn >>= 1
    return sn == 0 and r == racine


def verifier_coherence(
    ancienne_taille: int,
    nouvelle_taille: int,
    ancienne_racine: bytes,
    nouvelle_racine: bytes,
    preuve: list[bytes],
) -> bool:
    """Algorithme de la RFC 9162, section 2.1.4.2."""
    if not 0 <= ancienne_taille <= nouvelle_taille:
        return False
    if ancienne_taille == 0:
        return preuve == []
    if ancienne_taille == nouvelle_taille:
        return preuve == [] and ancienne_racine == nouvelle_racine
    if not preuve:
        return False
    chemin = list(preuve)
    if _est_puissance_de_2(ancienne_taille):
        chemin.insert(0, ancienne_racine)
    fn, sn = ancienne_taille - 1, nouvelle_taille - 1
    while fn & 1:
        fn >>= 1
        sn >>= 1
    fr = sr = chemin[0]
    for c in chemin[1:]:
        if sn == 0:
            return False
        if fn & 1 or fn == sn:
            fr = hash_noeud(c, fr)
            sr = hash_noeud(c, sr)
            if not fn & 1:
                while not fn & 1 and fn != 0:
                    fn >>= 1
                    sn >>= 1
        else:
            sr = hash_noeud(sr, c)
        fn >>= 1
        sn >>= 1
    return fr == ancienne_racine and sr == nouvelle_racine and sn == 0
