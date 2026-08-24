"""Nettoyage des séries capteurs, en amont de la construction du Gold."""

from __future__ import annotations

import math

import pandas as pd
from loguru import logger

PHYSICAL_BOUNDS: dict[str, tuple[float, float]] = {
    "temperature": (0.0, 150.0),
    "pressure_bar": (0.0, 300.0),
}

_NO_BOUNDS = (-math.inf, math.inf)


def resolve_bounds(
    value_col: str,
    bounds: tuple[float, float] | None = None,
) -> tuple[float, float]:
    """Return explicit bounds, else the physical default, else an open interval."""
    low, high = bounds if bounds is not None else PHYSICAL_BOUNDS.get(value_col, _NO_BOUNDS)
    if low > high:
        raise ValueError(f"Bornes incoherentes pour {value_col!r} : low={low} > high={high}")
    return float(low), float(high)


def clean_sensor_data(
    df: pd.DataFrame,
    value_col: str,
    group_col: str = "machine",
    timestamp_col: str = "timestamp",
    bounds: tuple[float, float] | None = None,
    keep: str = "last",
) -> pd.DataFrame:
    """Clean one sensor series: drop NaN, out-of-range values and duplicates.

    Order matters twice. Bounds are applied before de-duplication, otherwise an
    out-of-range reading may survive and evict the valid one. Sorting comes
    before de-duplication, otherwise `keep="last"` depends on file order.
    """
    required = {group_col, timestamp_col, value_col}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Colonnes manquantes : {sorted(missing)}")

    low, high = resolve_bounds(value_col, bounds)

    out = df.copy()
    initial = len(out)

    out = out.dropna(subset=[group_col, timestamp_col, value_col])
    dropped_na = initial - len(out)

    inside = out[value_col].between(low, high)
    dropped_range = int((~inside).sum())
    out = out[inside]

    out = out.sort_values([group_col, timestamp_col], kind="mergesort")

    before_dedup = len(out)
    out = out.drop_duplicates(subset=[group_col, timestamp_col], keep=keep)
    dropped_dup = before_dedup - len(out)

    if dropped_na or dropped_range or dropped_dup:
        logger.info(
            "clean_sensor_data[{}]: {} -> {} lignes (NaN={}, hors [{}, {}]={}, doublons={})",
            value_col,
            initial,
            len(out),
            dropped_na,
            low,
            high,
            dropped_range,
            dropped_dup,
        )
    return out.reset_index(drop=True)
