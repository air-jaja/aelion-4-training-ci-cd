# 🚨 BRIEFING — lundi 08 h 02, atelier InduSense

Vendredi soir, « une petite maintenance » a été faite sur le dépôt de production InduSense.
Depuis, l'installation échoue chez les nouveaux arrivants, le pipeline de données perd des mesures
et Grafana est injoignable. Un rapport d'astreinte affirme aussi que l'API refuse des clés valides :
**cette affirmation est à vérifier**, comme toute information d'incident.

Détail troublant : le dernier état visible dans l'onglet Actions est vert. Demandez-vous si un
contrôle a réellement tourné sur la branche de maintenance et si un statut vert prouve encore
quelque chose.

Version de travail auditée :

- branche `J6-gameday` : `dcf9a97abb6475c79f30d2a52ec3e9a3a9103bf3` ;
- état certifié `v1.0-sain` : `412c96d97811a8f2e5deb8409f59441411deb771`.

Mission du jour, par ordre de priorité :

1. rendre l'environnement réinstallable et la documentation conforme ;
2. obtenir une suite de tests entièrement verte, avec des tests identiques à `v1.0-sain` ;
3. rendre l'API saine et le pipeline conforme aux chiffres certifiés : environ
   **65 625 lignes et 1,76 % de résidu** ;
4. remettre en service API, Prometheus et Grafana ;
5. expliquer ce que la CI pouvait réellement détecter et restaurer un contrôle honnête ;
6. livrer une branche de réparation, une PR draft, un post-mortem et une restitution de 4 min.

Indices autorisés : le tag `v1.0-sain` est le dernier état certifié ; les chiffres de référence sont
dans votre pas à pas ; les tests sont un contrat, mais un contrat se relit. Procédez toujours ainsi :
**diagnostiquer → corriger → prouver → commiter**.
