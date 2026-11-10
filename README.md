# Indélébile : les arcanes de la preuve
[![CI](https://github.com/ItsJinmaa/indelebile/actions/workflows/ci.yml/badge.svg)](https://github.com/ItsJinmaa/indelebile/actions/workflows/ci.yml)

Service de notarisation multi-agents (projet Notaria, sujet 8).
Il prouve qu'une création (flash de tatouage, dessin, morceau, texte) existait
à une date donnée et n'a pas été retouchée depuis.

> Un journal Merkle, c'est un tatouage : on peut seulement ajouter de l'encre,
> jamais effacer, et toute retouche se voit.

**Règle d'or : le modèle de langage décide et explique, le code calcule.**

## Pourquoi ce projet

**Le problème.** Dans le milieu du tatouage et de l'art alternatif, le vol de
créations est courant : flashs de tatoueurs repris sans accord, dessins copiés
sur les réseaux sociaux, morceaux de groupes underground réutilisés sans crédit.

En France, le droit d'auteur naît automatiquement à la création : nul besoin de
déposer une œuvre pour en être l'auteur. La vraie difficulté, en cas de litige,
est de **prouver qu'on l'avait avant l'autre**.

**Ce qui existe.** L'enveloppe Soleau de l'INPI, la lettre recommandée envoyée
à soi-même, ou l'horodatage RFC 3161 par un tiers de confiance. Ces solutions
reposent toutes sur la confiance accordée à un organisme.

**Ce que fait Indélébile.** L'artiste dépose son œuvre dès qu'elle est finie.
Le service en calcule l'empreinte, la signe, et l'inscrit dans un journal
public infalsifiable (arbre de Merkle, comme la Certificate Transparency qui
sécurise les certificats du web). L'artiste peut ensuite demander, en langage
naturel : « Mon flash *Corbeau n°12* existait-il avant le 1er décembre ? »
L'agent répond uniquement à partir de preuves calculées, que **n'importe qui
peut revérifier** sans faire confiance au service.

| Indélébile prouve | Indélébile ne prouve pas |
|---|---|
| Que ce fichier exact existait à une date donnée | Qui est l'auteur (un voleur qui dépose en premier aura la date la plus ancienne) |
| Qu'il n'a pas été retouché depuis | Qu'un tribunal donnera raison à l'artiste : c'est un élément de preuve, pas un jugement |
| Que l'historique du journal n'a pas été réécrit | Qu'une œuvre *ressemblant* à une autre en est une copie |

> Projet pédagogique (module de cryptographie appliquée et IA agentique).
> Il démontre un principe ; ce n'est pas un service juridique en production.

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
