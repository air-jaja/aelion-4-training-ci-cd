# Provenance du socle

Il n'existe pas, dans les archives locales auditees, un unique depot qui soit a
la fois une fin Sprint 2 pure, un paquet M22 complet et le point de depart Git
reellement remis aux apprenants. Le parcours utilise donc deux references sans
les fusionner.

## A — Point de depart operationnel

- Archive historique : `indusense-sprint3-starter.zip`.
- Taille : 1 113 943 octets ; 30 fichiers.
- SHA-256 :
  `1450B5A03797E27B217A26201290698DC651175691F2F9A945D57E2F6771D178`.
- Equivalent Git historique : commit `0d02af0`, message
  `Add InduSense Sprint 3 starter package`.
- Univers : RF starter, 1 896 lignes, prevalence `0.1055`.

C'est le point de depart retenu ici parce qu'il est executable et correspond a
ce qui a effectivement lance le Sprint 3 precedent. Il contient deja un package
`src/`, une CLI, des tests, une CI et pre-commit : ce sont des amorces M23/M24,
pas des productions a attribuer au nouveau groupe.

Limite connue : la metadata historique ne satisfait pas seule toute la DoD M22
(`threshold_validated`, `git_commit` et `gold_sha256` manquent), et la model card
ainsi que le contrat I/O ne sont pas dans cette archive.

## B — Reference semantique fin Sprint 2

- Dossier local : `OLD repo/GIT Marine/indusense_ml_dl-main/indusense_ml_dl-main`.
- Empreinte d'arbre deterministe :
  `FDB95046AFC65EEEC18D89DC4EEFD69741F3C193FCE0D4B19E9744FDCE4F6C7E`.
- Contenu : notebooks ML/DL, MLflow, SHAP, Optuna, CodeCarbon, arbitrages et
  model card, sans FastAPI, Docker, Prefect, monitoring, drift ou CI Sprint 3.
- Univers : reference Marine distincte, donnee a 16,6 % a 24 h dans la trame.

Cette reference explique ce que le Sprint 2 a produit, mais n'est ni un snapshot
Git apprenant ni un starter Python 3.13 complet. Ses chiffres ne doivent jamais
etre colles sur le modele RF du point A.

## Decision pedagogique

Le depot de progression clone l'etat A pour garantir un demarrage commun et
cite l'etat B comme provenance semantique. Il ne copie aucun artefact Marine et
n'annonce jamais que les deux univers sont identiques. Chaque jalon ajoute
uniquement le delta necessaire a sa demi-journee.
