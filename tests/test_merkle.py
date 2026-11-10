"""Tests du journal Merkle.

Trois niveaux de confiance :
1. vecteurs connus (les mêmes entrées que la suite de tests de Certificate Transparency) ;
2. comparaison avec une implémentation « naïve » écrite directement depuis la RFC ;
3. une preuve falsifiée doit TOUJOURS être rejetée.
"""

import hashlib

import pytest

from indelebile.merkle import (
    JournalMerkle,
    hash_feuille,
    hash_noeud,
    verifier_coherence,
    verifier_inclusion,
)

# Entrées de test de Certificate Transparency (RFC 6962 / 9162).
ENTREES = [
    b"",
    b"\x00",
    b"\x10",
    b"\x20\x21",
    b"\x30\x31",
    b"\x40\x41\x42\x43",
    b"\x50\x51\x52\x53\x54\x55\x56\x57",
    b"\x60\x61\x62\x63\x64\x65\x66\x67\x68\x69\x6a\x6b\x6c\x6d\x6e\x6f",
]

# Racines attendues après 1, 2, ..., 8 ajouts.
RACINES_ATTENDUES = [
    "6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d",
    "fac54203e7cc696cf0dfcb42c92a1d9dbaf70ad9e621f4bd8d98662f00e3c125",
    "aeb6bcfe274b70a14fb067a5e5578264db0fa9b51af5e0ba159158f329e06e77",
    "d37ee418976dd95753c1c73862b9398fa2a2cf9b4ff0fdfe8b30cd95209614b7",
    "4e3bbb1f7b478dcfe71fb631631519a3bca12c9aefca1612bfce4c13a86264d4",
    "76e67dadbcdf1e10e1b74ddc608abd2f98dfb16fbce75277b5232a127f2087ef",
    "ddb89be403809e325750d3d263cd78929c2942b7942a34b77e122c9594a74c8c",
    "5dc9da79a70659a9ad559cb701ded9a2ab9d823aad2f4960cfe370eff4604328",
]


# --------------------------------------------------------------- référence naïve
def _k(n):
    k = 1
    while k * 2 < n:
        k *= 2
    return k


def mth(d):
    if not d:
        return hashlib.sha256(b"").digest()
    if len(d) == 1:
        return hash_feuille(d[0])
    k = _k(len(d))
    return hash_noeud(mth(d[:k]), mth(d[k:]))


def path(m, d):
    if len(d) <= 1:
        return []
    k = _k(len(d))
    if m < k:
        return path(m, d[:k]) + [mth(d[k:])]
    return path(m - k, d[k:]) + [mth(d[:k])]


def subproof(m, d, b):
    if m == len(d):
        return [] if b else [mth(d)]
    k = _k(len(d))
    if m <= k:
        return subproof(m, d[:k], b) + [mth(d[k:])]
    return subproof(m - k, d[k:], False) + [mth(d[:k])]


def journal_de(n):
    j = JournalMerkle()
    donnees = [f"oeuvre-{i}".encode() for i in range(n)]
    for x in donnees:
        j.ajouter(x)
    return j, donnees


# ------------------------------------------------------------------------ tests
def test_arbre_vide():
    assert JournalMerkle().racine().hex() == hashlib.sha256(b"").hexdigest()


def test_vecteurs_connus():
    j = JournalMerkle()
    for i, entree in enumerate(ENTREES):
        assert j.ajouter(entree) == i
        assert j.racine().hex() == RACINES_ATTENDUES[i]
    # Les anciennes racines restent calculables (journal historisé).
    for i in range(len(ENTREES)):
        assert j.racine(i + 1).hex() == RACINES_ATTENDUES[i]


def test_feuille_et_noeud_ont_des_prefixes_differents():
    a, b = hash_feuille(b"x"), hash_feuille(b"y")
    assert hash_feuille(a + b) != hash_noeud(a, b)


@pytest.mark.parametrize("n", range(1, 70))
def test_racine_identique_a_la_reference(n):
    j, d = journal_de(n)
    assert j.racine() == mth(d)


@pytest.mark.parametrize("n", [1, 2, 3, 5, 7, 8, 13, 32, 33, 64, 65])
def test_preuves_inclusion(n):
    j, d = journal_de(n)
    racine = j.racine()
    for m in range(n):
        preuve = j.preuve_inclusion(m)
        assert preuve == path(m, d)
        assert verifier_inclusion(hash_feuille(d[m]), m, n, preuve, racine)


@pytest.mark.parametrize("n", [2, 3, 7, 8, 9, 16, 21, 33])
def test_preuves_coherence(n):
    j, d = journal_de(n)
    for m in range(0, n + 1):
        preuve = j.preuve_coherence(m, n)
        if 0 < m < n:
            assert preuve == subproof(m, d[:n], True)
        assert verifier_coherence(m, n, j.racine(m), j.racine(n), preuve)


def test_inclusion_falsifiee_rejetee():
    j, d = journal_de(20)
    racine = j.racine()
    preuve = j.preuve_inclusion(6)
    bonne = hash_feuille(d[6])
    assert not verifier_inclusion(hash_feuille(b"retouche"), 6, 20, preuve, racine)
    assert not verifier_inclusion(bonne, 7, 20, preuve, racine)
    # Leçon apprise en écrivant ce test : la preuve seule ne « verrouille » pas la
    # taille du journal (un faux 21 avec la racine du 20 passerait). C'est pourquoi
    # la racine est TOUJOURS signée avec sa taille (tête de journal signée).
    assert verifier_inclusion(bonne, 6, 21, preuve, racine)
    j.ajouter(b"suivante")
    assert not verifier_inclusion(bonne, 6, 21, preuve, j.racine(21))
    assert not verifier_inclusion(bonne, 6, 20, preuve[:-1], racine)
    assert not verifier_inclusion(bonne, 25, 20, preuve, racine)
    preuve_alteree = [bytes(32)] + preuve[1:]
    assert not verifier_inclusion(bonne, 6, 20, preuve_alteree, racine)


def test_reecriture_historique_detectee():
    """Arcane XVI · La Tour : un journal « forké » doit être démasqué."""
    honnete, d = journal_de(10)
    ancienne_racine = honnete.racine(6)
    # L'attaquant réécrit l'œuvre n°3 puis continue le journal.
    fork = JournalMerkle()
    for i, x in enumerate(d):
        fork.ajouter(b"faux" if i == 3 else x)
    preuve = fork.preuve_coherence(6, 10)
    assert not verifier_coherence(6, 10, ancienne_racine, fork.racine(), preuve)


def test_coherence_cas_limites():
    j, _ = journal_de(8)
    r4, r8 = j.racine(4), j.racine(8)
    assert not verifier_coherence(4, 8, r4, r8, [])
    assert not verifier_coherence(5, 4, r4, r8, [])
    assert not verifier_coherence(0, 8, r4, r8, [b"x"])
    assert not verifier_coherence(8, 8, r4, r8, [])
    assert verifier_coherence(8, 8, r8, r8, [])
    assert not verifier_coherence(4, 8, r4, bytes(32), j.preuve_coherence(4, 8))


def test_arguments_invalides():
    j, _ = journal_de(4)
    with pytest.raises(ValueError):
        j.racine(5)
    with pytest.raises(ValueError):
        j.preuve_inclusion(4)
    with pytest.raises(ValueError):
        j.preuve_coherence(5, 4)
