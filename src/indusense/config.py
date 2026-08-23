from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


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


settings = Settings()
