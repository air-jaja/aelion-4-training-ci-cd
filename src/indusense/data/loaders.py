from __future__ import annotations

import re
from pathlib import Path

import pandas as pd
from loguru import logger

_DIGITS = re.compile(r"(\d+)")
_MACHINE_ROW = re.compile(
    r"\('([^']+)',\s*'([^']+)',\s*(\d+),\s*'([^']+)',\s*'([^']+)',\s*'([^']+)',\s*'([^']+)'\)"
)

CRITICALITY_ORDER: dict[str, int] = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}


def normalize_machine_id(raw: str) -> str:
    """Normalize raw machine identifiers to MACH-0N."""
    match = _DIGITS.search(str(raw))
    if not match:
        raise ValueError(f"machine_id sans numero : {raw!r}")
    return f"MACH-{int(match.group(1)):02d}"


def load_temperature(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep=";")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["machine"] = df["machine_id"].map(normalize_machine_id)
    return df[["machine", "timestamp", "temperature"]]


def load_pressure(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, sep="\t")
    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", utc=True).dt.tz_localize(None)
    df["machine"] = df["machine_id"].map(normalize_machine_id)
    return df[["machine", "timestamp", "pressure_bar"]]


def load_incidents(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["machine"] = df["machine_id"].map(normalize_machine_id)
    df["incident_ts"] = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str))
    return df[["machine", "incident_ts"]]


def load_machines(path: Path) -> pd.DataFrame:
    text = Path(path).read_text(encoding="utf-8")
    rows = [
        {
            "machine": normalize_machine_id(match.group(1)),
            "commissioning_date": pd.to_datetime(match.group(2)),
            "max_daily_capacity": int(match.group(3)),
            "model": match.group(4),
            "production_line": match.group(5),
            "location": match.group(6),
            "criticality": match.group(7),
        }
        for match in _MACHINE_ROW.finditer(text)
    ]
    if not rows:
        raise ValueError(f"Aucune machine trouvee dans {path}")
    return pd.DataFrame(rows)


def build_dataset(
    temp: pd.DataFrame,
    pres: pd.DataFrame,
    inc: pd.DataFrame,
    window_hours: int = 24,
    tolerance_minutes: int = 90,
) -> pd.DataFrame:
    """Join sensors and derive binary target `panne`.

    The `by="machine"` parameter is critical: without it, one machine can inherit
    the pressure value of another machine.
    """
    temp = temp.sort_values("timestamp")
    pres = pres.sort_values("timestamp")
    sensors = pd.merge_asof(
        temp,
        pres,
        on="timestamp",
        by="machine",
        direction="nearest",
        tolerance=pd.Timedelta(minutes=tolerance_minutes),
    )
    before = len(sensors)
    sensors = sensors.dropna(subset=["pressure_bar"])
    dropped = before - len(sensors)
    if dropped:
        logger.info(
            "merge_asof: {} rows without pressure under +/-{} min dropped ({:.2%})",
            dropped,
            tolerance_minutes,
            dropped / before,
        )

    sensors = sensors.sort_values(["machine", "timestamp"]).reset_index(drop=True)
    sensors["panne"] = 0
    window = pd.Timedelta(hours=window_hours)
    for row in inc.itertuples():
        mask = (
            (sensors["machine"] == row.machine)
            & (sensors["timestamp"] >= row.incident_ts - window)
            & (sensors["timestamp"] <= row.incident_ts)
        )
        sensors.loc[mask, "panne"] = 1
    return sensors


def add_machine_criticality(df: pd.DataFrame, machines: pd.DataFrame) -> pd.DataFrame:
    """Add static criticality for monitoring or segmentation, not baseline training."""
    levels = df["machine"].map(machines.set_index("machine")["criticality"].map(CRITICALITY_ORDER))
    out = df.copy()
    out["criticality_level"] = levels.fillna(CRITICALITY_ORDER["MEDIUM"]).astype("int64")
    return out
