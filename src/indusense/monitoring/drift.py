# =============================================================================
# src/indusense/monitoring/drift.py — Détection de dérive des données (m31-32)
# -----------------------------------------------------------------------------
# ROLE : mesurer si les données COURANTES ressemblent encore aux données de
# RÉFÉRENCE (celles de l'entraînement). Deux outils complémentaires :
#   - PSI (Population Stability Index) : l'AMPLEUR du déplacement de masse ;
#   - test KS (Kolmogorov-Smirnov)     : la SIGNIFICATIVITÉ statistique.
# Règle du cours : on DÉCIDE sur l'ampleur (PSI + seuils), KS confirme.
# Lecture usuelle du PSI : < 0,10 RAS · 0,10-0,25 à surveiller · > 0,25 fort.
# =============================================================================
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

#: Seuils de lecture usuels du PSI (conventions credit scoring, cf. m31 §2.2).
SEUIL_PSI_SURVEILLER = 0.10
SEUIL_PSI_FORT = 0.25

#: Features capteurs surveillées par défaut (drift spec InduSense).
FEATURES_SURVEILLEES = ("temperature", "pressure_bar")


def psi(ref, cur, bins: int = 10) -> float:
    """Population Stability Index entre référence et fenêtre courante.

    Conventions (m31, à FIGER dans la drift spec) :
      - bins calculés sur la RÉFÉRENCE (grille stable dans le temps) ;
      - bords extrêmes ouverts (±inf) : une valeur courante HORS de la plage de
        la référence est comptée dans un bin de bord — sinon np.histogram la
        jette en silence et une dérive d'échelle devient invisible ;
      - lissage +1e-6 : évite ln(0) sur les bins vides ;
      - les NaN (vraies données capteurs !) sont écartés feature par feature.
    """
    ref = np.asarray(pd.Series(ref).dropna(), dtype=float)
    cur = np.asarray(pd.Series(cur).dropna(), dtype=float)
    edges = np.histogram_bin_edges(ref, bins=bins)
    edges[0], edges[-1] = -np.inf, np.inf
    p_ref = np.histogram(ref, edges)[0] / len(ref) + 1e-6
    p_cur = np.histogram(cur, edges)[0] / len(cur) + 1e-6
    return float(np.sum((p_cur - p_ref) * np.log(p_cur / p_ref)))


def ks_pvalue(ref, cur) -> float:
    """p-value du test KS à 2 échantillons (p ≈ 0 → distributions différentes).

    Attention à grands n : significatif ≠ important — voir psi() pour l'ampleur.
    """
    return float(stats.ks_2samp(pd.Series(ref).dropna(), pd.Series(cur).dropna()).pvalue)


def verdict_psi(valeur: float) -> str:
    """Verdict lisible selon les seuils du cours."""
    if valeur < SEUIL_PSI_SURVEILLER:
        return "OK RAS"
    if valeur < SEUIL_PSI_FORT:
        return "! à surveiller"
    return "!! dérive forte"


def drift_table(
    df_ref: pd.DataFrame,
    df_cur: pd.DataFrame,
    features=FEATURES_SURVEILLEES,
    bins: int = 10,
) -> pd.DataFrame:
    """Table de dérive : une ligne par feature (psi, ks_pvalue, verdict), tri PSI desc."""
    lignes = [
        {
            "feature": f,
            "psi": psi(df_ref[f], df_cur[f], bins=bins),
            "ks_pvalue": ks_pvalue(df_ref[f], df_cur[f]),
            "verdict": verdict_psi(psi(df_ref[f], df_cur[f], bins=bins)),
        }
        for f in features
    ]
    return pd.DataFrame(lignes).sort_values("psi", ascending=False).reset_index(drop=True)


def drift_report(
    df_ref: pd.DataFrame,
    df_cur: pd.DataFrame,
    features=FEATURES_SURVEILLEES,
    psi_threshold: float = SEUIL_PSI_FORT,
    bins: int = 10,
) -> dict:
    """Rapport machine (module 32) : {feature: {psi, ks_p, drift}} + verdict global.

    C'est le « rapport JSON maison » branché dans le flow après predict ;
    Evidently est l'alternative outillée (même contrat de sortie côté décision).
    """
    table = drift_table(df_ref, df_cur, features=features, bins=bins)
    contenu = {
        r["feature"]: {
            "psi": round(float(r["psi"]), 4),
            "ks_p": float(r["ks_pvalue"]),
            "drift": bool(r["psi"] > psi_threshold),
        }
        for r in table.to_dict("records")
    }
    contenu["_global"] = {"drift": any(v["drift"] for v in contenu.values())}
    return contenu
