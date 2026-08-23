# 05 — J3 matin — M27

Objectif : construire une image deterministe qui contient le modele (variante A)
et s'execute sans privileges inutiles.

Recu par le jalon : API durcie, `.dockerignore`, Dockerfile de travail et scripts
de verification Windows/macOS. Aucun Compose complet.

A faire : lire chaque couche, construire, lancer, tester health/ready, inspecter
l'utilisateur non-root et comparer le digest.

Preuve :

```powershell
docker build -t indusense-api:m27 .
docker run --rm -d --name indusense-m27 -p 8000:8000 --env-file .env indusense-api:m27
Invoke-RestMethod http://127.0.0.1:8000/health
docker inspect indusense-m27 --format '{{.Config.User}}'
docker stop indusense-m27
```

Rattrapage sans Docker : lire le Dockerfile et faire valider les preuves par un
binome ; aucun installateur improvise pendant la sequence.
