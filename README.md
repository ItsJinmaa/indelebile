# Indélébile : les arcanes de la preuve
[![CI](https://github.com/ItsJinmaa/indelebile/actions/workflows/ci.yml/badge.svg)](https://github.com/ItsJinmaa/indelebile/actions/workflows/ci.yml)

Service de notarisation multi-agents (projet Notaria, sujet 8).
Il prouve qu'une création (flash de tatouage, dessin, morceau, texte) existait
à une date donnée et n'a pas été retouchée depuis.

> Un journal Merkle, c'est un tatouage : on peut seulement ajouter de l'encre,
> jamais effacer, et toute retouche se voit.

**Règle d'or : le modèle de langage décide et explique, le code calcule.**

## Les arcanes

| Arcane | Agent | Rôle officiel |
|---|---|---|
| I · Le Bateleur | Le Pochoir | Réceptionniste |
| II · La Papesse | Le Tatoueur | Greffier |
| IV · L'Empereur | Le Sceau | Signataire |
| VII · Le Chariot | — | Orchestrateur |
| IX · L'Ermite | L'Oracle | Enquêteur |
| XI · La Justice | L'Inquisiteur | Vérificateur |
| XX · Le Jugement | Les Veilleurs | Témoins |

Menaces : XV · Le Diable (injection de prompt), XVI · La Tour (réécriture
d'historique), XVIII · La Lune (preuve hallucinée).

## Démarrage

```bash
make install   # installe les dépendances (uv)
make test      # lance les tests
make cover     # tests + couverture (seuil : 70 %)
```

## État

- [x] Journal Merkle RFC 9162 (racine, preuves d'inclusion et de cohérence)
- [x] Signatures Ed25519, clé chiffrée au repos (Argon2id + AES-256-GCM), rotation
- [x] Cartes des arcanes (`docs/arcanes/`, régénérées par `scripts/generer_arcanes.py`)
- [ ] Agents, orchestrateur, témoins, évaluation, publication (week-end du 14-15 novembre)

Auteur : Antoine Francoz · ORCID [0009-0003-8358-6640](https://orcid.org/0009-0003-8358-6640)
