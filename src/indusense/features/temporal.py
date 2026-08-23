from __future__ import annotations

import pandas as pd


def add_temporal_features(
    df: pd.DataFrame,
    group_col: str = "machine",
    timestamp_col: str = "timestamp",
    value_cols: tuple[str, ...] = ("temperature", "pressure_bar"),
    lags: tuple[int, ...] = (1, 3, 6),
    windows: tuple[int, ...] = (3, 6),
) -> pd.DataFrame:
    """Add lag and rolling features per machine without temporal leakage."""
    required = {group_col, timestamp_col, *value_cols}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes : {sorted(missing)}")

    df = df.sort_values([group_col, timestamp_col]).reset_index(drop=True).copy()
    for col in value_cols:
        grouped = df.groupby(group_col)[col]
        for lag in lags:
            df[f"{col}_lag{lag}"] = grouped.shift(lag)
        for window in windows:
            df[f"{col}_roll{window}_mean"] = grouped.transform(
                lambda series, window=window: series.shift(1).rolling(window).mean()
            )
    return df
