# [PÉDAGOGIE] ============================================================================
# [PÉDAGOGIE] FICHIER — src/indusense/config.py
# [PÉDAGOGIE] MODULE  — M23–M26 — configuration typée et séparation code/environnement
# [PÉDAGOGIE] RÔLE    — Rassembler les paramètres variables, leurs valeurs par défaut et leur
# [PÉDAGOGIE]           validation.
# [PÉDAGOGIE] THÉORIE — une configuration typée échoue tôt plutôt que loin de la cause
# [PÉDAGOGIE]           • les chemins sont résolus depuis une racine stable
# [PÉDAGOGIE]           • secrets et réglages d'environnement ne doivent pas être codés en dur
# [PÉDAGOGIE] À VOIR  — Afficher les valeurs non sensibles effectivement chargées et tester les
# [PÉDAGOGIE]           valeurs invalides.
# [PÉDAGOGIE] PIÈGE   — Ne jamais journaliser une clé API, un mot de passe ou un jeton complet.
# [PÉDAGOGIE] GARDE   — Toutes les lignes marquées [PÉDAGOGIE] sont des commentaires : elles
# [PÉDAGOGIE]           guident la lecture sans changer l'exécution.
# [PÉDAGOGIE] ============================================================================

# [PÉDAGOGIE] DÉPENDANCE — pathlib : manipule les chemins sans dépendre du séparateur
# [PÉDAGOGIE] Windows/Linux/macOS.
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# [PÉDAGOGIE] TYPE `Settings` — regroupe un état cohérent et le contrat des opérations associées.
# [PÉDAGOGIE] THÉORIE — nommer ce type rend les invariants visibles et facilite les tests à la
# [PÉDAGOGIE] frontière.
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="INDUSENSE_",
        env_file=".env",
        extra="ignore",
    )

    data_dir: Path = Path("data/raw")
    gold_dir: Path = Path("data/gold")
    model_dir: Path = Path("artifacts/models")
    random_seed: int = 42
    target_col: str = "panne"
    incident_window_hours: int = 24


# [PÉDAGOGIE] CONSTANTE / CONTRAT — cette valeur nommée centralise un choix partagé au lieu de le
# [PÉDAGOGIE] disperser.
settings = Settings()
