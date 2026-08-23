# =============================================================================
# tests/test_drift_monitoring.py — Tests du module de dérive (m31-32)
# Aucune donnée réelle requise : distributions synthétiques contrôlées.
# =============================================================================
from __future__ import annotations

import numpy as np
import pandas as pd

from indusense.monitoring.drift import drift_report, drift_table, ks_pvalue, psi, verdict_psi


def test_psi_quasi_nul_sur_distributions_identiques():
    rng = np.random.default_rng(0)
    assert psi(rng.normal(0, 1, 20_000), rng.normal(0, 1, 5_000)) < 0.05


def test_psi_detecte_un_decalage_d_un_ecart_type():
    rng = np.random.default_rng(2)
    assert psi(rng.normal(0, 1, 20_000), rng.normal(1, 1, 5_000)) > 0.25


def test_psi_compte_les_valeurs_hors_plage_de_reference():
    # La moitié de la masse courante sort de la plage de la référence : une
    # implémentation à bins fermés sous-estime (~0,35) voire annule (~0) le PSI.
    ref = np.linspace(0.0, 1.0, 5_000)
    cur = np.concatenate([np.linspace(0.0, 1.0, 1_000), np.full(1_000, 5.0)])
    assert psi(ref, cur) > 0.8


def test_psi_ignore_les_nan_capteurs():
    rng = np.random.default_rng(3)
    ref = rng.normal(50, 4, 10_000)
    ref[::50] = np.nan  # trous de capteur réalistes
    assert psi(ref, rng.normal(50, 4, 3_000)) < 0.05


def test_ks_pvalue_coherente():
    rng = np.random.default_rng(4)
    assert ks_pvalue(rng.normal(0, 1, 4_000), rng.normal(0, 1, 4_000)) > 0.001
    assert ks_pvalue(rng.normal(0, 1, 4_000), rng.normal(1, 1, 4_000)) < 1e-6


def test_verdicts_suivent_les_seuils_du_cours():
    assert "RAS" in verdict_psi(0.05)
    assert "surveiller" in verdict_psi(0.18)
    assert "forte" in verdict_psi(0.60)


def test_drift_table_structure_et_tri():
    rng = np.random.default_rng(5)
    df_ref = pd.DataFrame({"a": rng.normal(0, 1, 5_000), "b": rng.normal(0, 1, 5_000)})
    df_cur = pd.DataFrame({"a": rng.normal(0, 1, 2_000), "b": rng.normal(2, 1, 2_000)})
    table = drift_table(df_ref, df_cur, features=("a", "b"))
    assert list(table.columns) == ["feature", "psi", "ks_pvalue", "verdict"]
    assert table.loc[0, "feature"] == "b"  # tri PSI décroissant


def test_drift_report_contrat_module32():
    rng = np.random.default_rng(6)
    df_ref = pd.DataFrame({"a": rng.normal(0, 1, 5_000), "b": rng.normal(0, 1, 5_000)})
    df_cur = pd.DataFrame({"a": rng.normal(0, 1, 2_000), "b": rng.normal(2, 1, 2_000)})
    rapport = drift_report(df_ref, df_cur, features=("a", "b"))
    assert rapport["b"]["drift"] is True and rapport["a"]["drift"] is False
    assert rapport["_global"]["drift"] is True
    assert set(rapport["a"]) == {"psi", "ks_p", "drift"}
