# Jalon actuel : 00-fin-sprint2

Etat de depart normalise, avant toute activite du Sprint 3.

- Source locale de provenance : historique du precedent fil rouge InduSense.
- Arbre de reference initial : commit historique `0d02af0` du starter Sprint 3
  precedent, lui-meme construit a la charniere des modules 1 a 22.
- Donnees, modele RF, metadata, package minimal et tests sont presents.
- Aucune API, image Docker, orchestration Prefect, mesure de drift ou solution de
  Game Day n'est revelee dans ce jalon.

Preuve attendue :

```powershell
uv sync --frozen --extra dev
uv run pytest -q
uv run ruff check .
uv run indusense --help
```
