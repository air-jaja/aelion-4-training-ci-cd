from pathlib import Path

import pandas as pd
import pytest

from indusense.data.loaders import (
    build_dataset,
    load_incidents,
    load_pressure,
    load_temperature,
    normalize_machine_id,
)

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample"


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("MACH-01", "MACH-01"),
        ("MACH_01", "MACH-01"),
        ("M-06", "MACH-06"),
        ("M-2", "MACH-02"),
        ("M_07", "MACH-07"),
    ],
)
def test_normalize_machine_id_variants(raw, expected):
    assert normalize_machine_id(raw) == expected


def test_normalize_machine_id_without_number_raises():
    with pytest.raises(ValueError):
        normalize_machine_id("NOPE")


def test_build_dataset_has_binary_target():
    temp = load_temperature(SAMPLE / "capteurs_temperature.csv")
    pres = load_pressure(SAMPLE / "capteurs_pression.tsv")
    inc = load_incidents(SAMPLE / "releves_incidents.csv")

    dataset = build_dataset(temp, pres, inc, window_hours=24)

    assert {"machine", "timestamp", "temperature", "pressure_bar", "panne"} <= set(dataset.columns)
    assert set(dataset["panne"].unique()) <= {0, 1}
    assert 0 < dataset["panne"].mean() < 0.5


def test_merge_asof_never_matches_other_machine():
    temp = pd.DataFrame(
        {
            "machine": ["MACH-01", "MACH-02"],
            "timestamp": pd.to_datetime(["2026-01-01 12:00", "2026-01-01 12:01"]),
            "temperature": [50.0, 60.0],
        }
    )
    pres = pd.DataFrame(
        {
            "machine": ["MACH-02", "MACH-01"],
            "timestamp": pd.to_datetime(["2026-01-01 12:00", "2026-01-01 20:00"]),
            "pressure_bar": [180.0, 999.0],
        }
    )
    inc = pd.DataFrame(columns=["machine", "incident_ts"])

    dataset = build_dataset(temp, pres, inc, window_hours=24, tolerance_minutes=90)

    assert list(dataset["machine"]) == ["MACH-02"]
    assert dataset.iloc[0]["pressure_bar"] == 180.0
