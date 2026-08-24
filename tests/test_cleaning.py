from pathlib import Path

import pandas as pd
import pytest

from indusense.data.loaders import load_pressure
from indusense.features.cleaning import PHYSICAL_BOUNDS, clean_sensor_data, resolve_bounds

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "sample"


def _frame(rows: list[tuple[str, str, float]]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "machine": [row[0] for row in rows],
            "timestamp": pd.to_datetime([row[1] for row in rows]),
            "temperature": [row[2] for row in rows],
        }
    )


def test_duplicates_keep_last_reading():
    df = _frame(
        [
            ("MACH-01", "2025-01-01 00:00", 50.0),
            ("MACH-01", "2025-01-01 00:00", 51.0),
        ]
    )
    out = clean_sensor_data(df, value_col="temperature")

    assert len(out) == 1
    assert out.loc[0, "temperature"] == 51.0


def test_sort_happens_before_dedup():
    """Unsorted input must yield the same result as sorted input."""
    rows = [
        ("MACH-01", "2025-01-01 01:00", 60.0),
        ("MACH-01", "2025-01-01 00:00", 50.0),
        ("MACH-01", "2025-01-01 00:00", 51.0),
    ]
    out = clean_sensor_data(_frame(rows), value_col="temperature")

    assert list(out["temperature"]) == [51.0, 60.0]
    assert out["timestamp"].is_monotonic_increasing


def test_out_of_range_value_is_dropped_before_dedup():
    """The aberrant reading must not evict the valid one at the same timestamp."""
    df = _frame(
        [
            ("MACH-01", "2025-01-01 00:00", 48.0),
            ("MACH-01", "2025-01-01 00:00", 9999.0),
        ]
    )
    out = clean_sensor_data(df, value_col="temperature")

    assert len(out) == 1
    assert out.loc[0, "temperature"] == 48.0


def test_missing_values_are_dropped():
    df = _frame(
        [
            ("MACH-01", "2025-01-01 00:00", 48.0),
            ("MACH-01", "2025-01-01 01:00", float("nan")),
        ]
    )
    out = clean_sensor_data(df, value_col="temperature")

    assert len(out) == 1
    assert not out["temperature"].isna().any()


def test_machines_are_not_mixed():
    df = _frame(
        [
            ("MACH-02", "2025-01-01 00:00", 70.0),
            ("MACH-01", "2025-01-01 00:00", 50.0),
        ]
    )
    out = clean_sensor_data(df, value_col="temperature")

    assert len(out) == 2
    assert list(out["machine"]) == ["MACH-01", "MACH-02"]


def test_input_frame_is_not_mutated():
    df = _frame(
        [
            ("MACH-01", "2025-01-01 00:00", 50.0),
            ("MACH-01", "2025-01-01 00:00", 51.0),
        ]
    )
    snapshot = df.copy()
    clean_sensor_data(df, value_col="temperature")

    pd.testing.assert_frame_equal(df, snapshot)


def test_index_is_reset():
    df = _frame(
        [
            ("MACH-01", "2025-01-01 02:00", 50.0),
            ("MACH-01", "2025-01-01 00:00", 51.0),
            ("MACH-01", "2025-01-01 01:00", 52.0),
        ]
    )
    out = clean_sensor_data(df, value_col="temperature")

    assert list(out.index) == [0, 1, 2]


def test_missing_column_raises():
    df = pd.DataFrame({"machine": ["MACH-01"], "timestamp": pd.to_datetime(["2025-01-01"])})
    with pytest.raises(ValueError):
        clean_sensor_data(df, value_col="temperature")


def test_explicit_bounds_override_physical_defaults():
    df = _frame(
        [
            ("MACH-01", "2025-01-01 00:00", 48.0),
            ("MACH-01", "2025-01-01 01:00", 90.0),
        ]
    )
    out = clean_sensor_data(df, value_col="temperature", bounds=(40.0, 60.0))

    assert list(out["temperature"]) == [48.0]


def test_inverted_bounds_raise():
    with pytest.raises(ValueError):
        resolve_bounds("temperature", bounds=(60.0, 40.0))


def test_unknown_column_has_open_bounds():
    low, high = resolve_bounds("vibration_mm_s")

    assert low == float("-inf")
    assert high == float("inf")
    assert "vibration_mm_s" not in PHYSICAL_BOUNDS


def test_real_pressure_source_has_duplicates_removed():
    """The shipped TSV really does contain repeated (machine, timestamp) pairs."""
    pres = load_pressure(SAMPLE / "capteurs_pression.tsv")
    assert pres.duplicated(["machine", "timestamp"]).any()

    out = clean_sensor_data(pres, value_col="pressure_bar")

    assert not out.duplicated(["machine", "timestamp"]).any()
    assert len(out) < len(pres)
