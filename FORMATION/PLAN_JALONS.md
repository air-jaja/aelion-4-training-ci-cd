# Plan local des douze jalons

Cadence visio : **09h00–12h30**, pause dejeuner **12h30–13h30**,
**13h30–17h00**. Chaque demi-journee contient 210 minutes, pause courte incluse.

| N° | Date et plage | Branche publiee au moment voulu | Contenu revele, sans solution future |
|---:|---|---|---|
| 01 | lun. 24/08, matin | `jalon/01-j1-matin-m23` | Socle fin S2, M23 : structure, package, anti-fuite, CLI |
| 02 | lun. 24/08, apres-midi | `jalon/02-j1-apres-midi-m24` | Stabilisation M23, M24 : qualite, tests, CI, versioning |
| 03 | mar. 25/08, matin | `jalon/03-j2-matin-m25` | Stabilisation M24, squelette FastAPI M25 |
| 04 | mar. 25/08, apres-midi | `jalon/04-j2-apres-midi-m26` | API M25 rejouable, atelier menaces et garde-fous M26 |
| 05 | mer. 26/08, matin | `jalon/05-j3-matin-m27` | API durcie, Dockerfile et preuves M27 |
| 06 | mer. 26/08, apres-midi | `jalon/06-j3-apres-midi-m28` | Image M27, Compose/smoke M28, amorce M29 |
| 07 | jeu. 27/08, matin | `jalon/07-j4-matin-m29-m30` | Stack M28, orchestration Prefect M29–M30 |
| 08 | jeu. 27/08, apres-midi | `jalon/08-j4-apres-midi-m31-m32-payguard` | Pipeline stabilise, bascule vers PayGuard adversarial |
| 09 | ven. 28/08, matin | `jalon/09-j5-matin-m31-m32-indusense` | Retour InduSense, fenetres et mesure du drift |
| 10 | ven. 28/08, apres-midi | `jalon/10-j5-apres-midi-m33-m34` | Drift stabilise, Prometheus/Grafana et runbook |
| 11 | sam. 29/08, matin | `jalon/11-j6-matin-gameday` | Stack observable, Game Day casse phases 0–2 |
| 12 | sam. 29/08, apres-midi | `jalon/12-j6-apres-midi-retex` | Game Day phases 3–6, preuves et post-mortem, sans corrige |

## Politique de revelation

- `main` reste le point de depart fin Sprint 2.
- Les branches locales de preparation se nomment `preparation/<jalon>`.
- Le formateur ne pousse qu'une branche a la fois vers `jalon/<jalon>`.
- Une branche n'apporte que l'etat necessaire au moment considere : le corrige
  d'une demi-journee peut devenir le prerequis de la suivante, jamais avant.
- J4 apres-midi utilise le depot PayGuard separe ; J6 utilise la branche cassee
  dediee. Le present depot n'integre aucune solution du Game Day.
