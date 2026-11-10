# Journal de bord

> Ce journal raconte comment j'ai fait le projet, erreurs comprises.
> et corrigé moi-même (voir AI_USAGE.md).

---

## Mardi 10 novembre 2026 : jour 1

### Le choix du sujet (9 h 40)

Je suis un étudiant débutant en crypto. Au départ je pensais prendre Vigenère, le sujet
qui me parlait le plus, mais finalement j'ai décidé de me challenger et de partir sur quelque chose d'autre. Moi je
voulais un sujet qui me permettait de me l'approprier.

Du coup j'ai pris le sujet **Notaria** : prouver qu'un document existait à une date et
qu'il a pas été modifié. Ça a l'air technique dit comme ça, mais au fond c'est
juste des empreintes, des signatures et un arbre de Merkle.

Je suis TDAH donc j'ai tout découpé en toutes petites étapes, une action à la
fois.

### L'idée qui rend le projet à moi

Ce que j'aime : la musique alternative, le piercing, le tatouage, le dessin,
l'art

Et là le déclic : **un journal Merkle, c'est un tatouage**. Tu peux que rajouter
de l'encre, jamais effacer, et si quelqu'un retouche, ça se voit. C'est
exactement la propriété « append-only » demandée par le sujet.

Le projet s'appelle donc **Indélébile**. Le cas d'usage c'est un vrai problème
dans mon milieu : les flashs de tatoueurs volés sur les réseaux sociaux, les dessins
copiés, les morceaux repris sans crédit. Indélébile prouve « ce dessin existait
le 3 mars et il a pas bougé depuis ».

j'ai donc voulu associer **une carte de tarot à chaque agent** afin de continuer de m'approprier le projet.
Par exemple l'Ermite pour l'Enquêteur, parce que sa lanterne éclaire que ce qui est prouvé. Le reste reste
dans le noir : « non prouvable ». Et les menaces ont aussi leurs cartes : la
Tour pour la réécriture d'historique, la Lune pour l'IA qui hallucine, le Diable
pour l'injection de prompt.

### L'installation (ce qui a coincé)

- Mon PC : Acer avec Ryzen 7 et 32 Go de RAM. C'est le double du max demandé,
  donc je dois faire gaffe à ce que ça tourne aussi sur un PC de 8 Go.
- WSL et Ubuntu étaient déjà installés.
- Ollama voulait pas s'installer, il manquait `zstd`.

### Anecdote 1 : l'IA s'est (un peu) trompée dès le premier test

J'ai demandé à qwen2.5:3b d'expliquer SHA-256 en une phrase. Il a répondu que
l'empreinte est générée « de manière unique » pour chaque fichier.

C'est **légèrement faux**. Deux fichiers différents *peuvent* avoir la même
empreinte (une collision). C'est juste tellement improbable qu'en pratique ça
arrive pas.

C'est exactement pour ça que le sujet dit « le modèle décide et explique, le
code calcule ». L'IA peut être approximative, donc on lui confie jamais les
calculs.

### Anecdote 2 : un test qui a planté pour une bonne raison

Pendant l'écriture des tests de l'arbre de Merkle, un test a échoué. Il
vérifiait qu'une preuve d'inclusion pour un journal de 20 éléments était refusée
si on mentait en disant « 21 ». Et en fait non, elle passait.

Ce que j'ai compris : **la preuve toute seule verrouille pas la taille du
journal.** Un tricheur pourrait mentir dessus. La solution : toujours signer la
racine **avec** sa taille. Ça ira dans mon modèle de menace.

### Ce qui marche à la fin de la journée

- Dépôt GitHub public : `ItsJinmaa/indelebile`
- Arbre de Merkle (RFC 9162) vérifié avec les vecteurs officiels de Certificate
  Transparency. 100 000 documents en 0,2 s, preuves de 17 éléments, soit log2 de
  100 000.
- Signatures Ed25519, clé privée chiffrée avec une phrase secrète, rotation des
  clés.
- 104 tests, 98,5 % de couverture (il en faut 70).
- Intégration continue : GitHub relance tous les tests à chaque envoi. Premier
  passage vert en 13 secondes.
- Les 10 cartes de tarot, générées par un script.

Prochaine étape : les agents
