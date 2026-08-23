# Mode d'emploi du parcours progressif

## Une seule fois, au debut du Sprint 3

Dans VS Code, ouvrir **Terminal > Nouveau terminal**, puis saisir :

```powershell
git clone https://github.com/thomasfesq/CISIA_24082026_Parcours.git
cd CISIA_24082026_Parcours
git switch -c prenom-nom
uv sync --frozen --extra dev
uv run pytest -q
```

Remplacer `prenom-nom` par un nom de branche personnel, sans espace ni accent.
Ne pas travailler directement sur `main` ou sur une branche `jalon/...`.

## Au debut de chaque demi-journee

1. Enregistrer son travail actuel :

```powershell
git status
git add -A
git commit -m "travail avant nouveau jalon"
```

2. Lancer le jalon annonce par le formateur, par exemple :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\formation\mettre_a_niveau.ps1 -Jalon 03-j2-matin-m25
```

Le script effectue bien un `git pull` du jalon officiel. Avant cela, il cree une
branche locale `sauvegarde/...` pointant sur l'etat courant. Il ne supprime ni ne
reecrit aucun commit.

3. Verifier l'etat recu :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\formation\verifier_jalon.ps1 -Jalon 03-j2-matin-m25
```

## Si une fusion entre en conflit

Le script annule la fusion et conserve le travail dans la branche d'origine et
dans la branche `sauvegarde/...`. Pour repartir immediatement du jalon officiel
sans perdre cette copie :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\formation\mettre_a_niveau.ps1 -Jalon 03-j2-matin-m25 -Rattrapage
```

Le mode rattrapage cree une nouvelle branche `rattrapage/...`. Il ne fait aucun
`reset --hard` et ne supprime rien. Le formateur pourra ensuite recuperer un
fichier precis depuis la branche de sauvegarde.

## Sur macOS ou Linux

```bash
bash scripts/formation/mettre_a_niveau.sh 03-j2-matin-m25
```

## Regles communes

- Les jalons sont cumulatifs, mais un jalon futur n'est publie qu'au moment prevu.
- Une branche `jalon/...` est une reference en lecture seule ; on travaille sur
  sa branche personnelle.
- Aucun secret ne doit entrer dans Git. Utiliser `.env`, jamais `.env.example`,
  pour une vraie valeur locale.
- En cas de retard important, privilegier le mode rattrapage au bricolage d'un
  historique : le travail precedent reste consultable et recuperable.
