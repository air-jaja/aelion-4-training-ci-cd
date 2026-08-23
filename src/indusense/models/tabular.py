from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

NON_FEATURE_COLUMNS: tuple[str, ...] = ("machine", "timestamp")


def select_features(
    df: pd.DataFrame,
    target_col: str,
    exclude: tuple[str, ...] = NON_FEATURE_COLUMNS,
) -> pd.DataFrame:
    cols = [col for col in (*exclude, target_col) if col in df.columns]
    return df.drop(columns=cols)


def train_model(
    x: pd.DataFrame,
    y: pd.Series,
    n_estimators: int = 200,
    random_state: int = 42,
) -> RandomForestClassifier:
    model = RandomForestClassifier(
        n_estimators=n_estimators,
        class_weight="balanced",
        random_state=random_state,
    )
    model.fit(x, y)
    return model


def predict_proba(model: Any, x: pd.DataFrame) -> np.ndarray:
    return model.predict_proba(x)[:, 1]


def save_model(model: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, path)


def load_model(path: Path) -> Any:
    return joblib.load(path)
