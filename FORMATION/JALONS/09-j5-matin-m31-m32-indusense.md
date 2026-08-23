# 09 — J5 matin — M31–M32 InduSense

> Windows, macOS ou Linux : suivre la section drift InduSense du
> [guide multiplateforme](../GUIDE_MULTIPLATEFORME_APPRENANT.md).

Objectif : transferer la methode de drift vers les capteurs InduSense.

Recu par le jalon : donnees de reference et fenetres, fiche TP, scripts de travail
et modele de rapport. Aucun dashboard final.

A faire : choisir la reference, calculer PSI par feature et fenetre, separer
drift de donnees et baisse de performance, eviter toute reponse automatique.

Preuve :

```powershell
uv run python scripts/drift_windows.py
uv run python scripts/evaluate_drift.py
uv run pytest tests/test_drift_monitoring.py -q
```

Rattrapage : une reference, une fenetre, une feature, une decision ; les fenetres
supplementaires forment la reserve.

### Garde-fou Windows : chemin court

Le TP autonome doit etre place dans un chemin court, par exemple
`C:\CISIA\tp_drift_indusense`. Un checkout tres profond peut depasser la limite
de chargement d'une extension compilee scikit-learn et produire un trompeur
`ModuleNotFoundError: ..._datasets_pair` alors que le fichier est present.
Deplacer/copier le TP vers un chemin court, puis relancer `uv sync --frozen
--extra dev`; ne pas modifier le lock pour masquer ce probleme de chemin.
