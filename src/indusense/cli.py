from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import typer
from loguru import logger

from indusense import __version__
from indusense.config import settings
from indusense.data.loaders import build_dataset, load_incidents, load_pressure, load_temperature
from indusense.features.temporal import add_temporal_features
from indusense.models.tabular import (
    load_model,
    predict_proba,
    save_model,
    select_features,
    train_model,
)

app = typer.Typer(help="InduSense Sprint 3 starter CLI")


def _load_gold(data_dir: Path) -> pd.DataFrame:
    temp = load_temperature(data_dir / "capteurs_temperature.csv")
    pres = load_pressure(data_dir / "capteurs_pression.tsv")
    inc = load_incidents(data_dir / "releves_incidents.csv")
    dataset = build_dataset(temp, pres, inc, window_hours=settings.incident_window_hours)
    return add_temporal_features(dataset).dropna().reset_index(drop=True)


@app.command()
def check_data(data_dir: Path | None = None) -> None:
    """Load sample sources and print a short health summary."""
    data_dir = data_dir or settings.data_dir
    dataset = _load_gold(data_dir)
    typer.echo(f"rows={len(dataset)}")
    typer.echo(f"machines={dataset['machine'].nunique()}")
    typer.echo(f"panne_rate={dataset[settings.target_col].mean():.4f}")


@app.command()
def build_gold(data_dir: Path | None = None, out: Path | None = None) -> None:
    """Build and save the gold dataset from raw InduSense sources."""
    data_dir = data_dir or settings.data_dir
    out = out or settings.gold_dir / "gold_dataset.csv"
    dataset = _load_gold(data_dir)
    out.parent.mkdir(parents=True, exist_ok=True)
    dataset.to_csv(out, index=False)
    logger.info("Gold dataset written: {} rows -> {}", len(dataset), out)


@app.command()
def train(data_dir: Path | None = None, out: Path | None = None) -> None:
    """Train the baseline RandomForest model on sample data."""
    data_dir = data_dir or settings.data_dir
    out = out or settings.model_dir / "rf.joblib"
    dataset = _load_gold(data_dir)
    x = select_features(dataset, settings.target_col)
    y = dataset[settings.target_col]
    model = train_model(x, y, random_state=settings.random_seed)
    save_model(model, out)

    metadata = {
        "created_at": datetime.now(UTC).isoformat(),
        "package_version": __version__,
        "random_seed": settings.random_seed,
        "target_col": settings.target_col,
        "features": list(x.columns),
        "n_train_rows": int(len(dataset)),
        "panne_rate": round(float(y.mean()), 4),
        "dataset": str(data_dir),
    }
    metadata_path = out.parent / "model_metadata.json"
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    logger.info("Model trained on {} rows -> {}", len(dataset), out)
    logger.info("Metadata -> {}", metadata_path)


@app.command()
def predict(data_dir: Path | None = None, model_path: Path | None = None) -> None:
    """Score the latest observation per machine."""
    data_dir = data_dir or settings.data_dir
    model_path = model_path or settings.model_dir / "rf.joblib"
    if not model_path.exists():
        raise typer.BadParameter(f"Model not found: {model_path}. Run `indusense train` first.")

    dataset = _load_gold(data_dir).groupby("machine").tail(1)
    model = load_model(model_path)
    scores = predict_proba(model, select_features(dataset, settings.target_col))
    for machine, score in zip(dataset["machine"], scores, strict=False):
        typer.echo(f"{machine}: P(panne)={score:.3f}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
