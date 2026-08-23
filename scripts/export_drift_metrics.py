# =============================================================================
# scripts/export_drift_metrics.py — Exporteur Prometheus du TP drift (m33)
# Expose sur :9109/metrics : indusense_drift_psi{feature,fenetre},
# indusense_drift_ks_pvalue{...}, indusense_drift_rappel{fenetre}, etc.
# Relit reports/drift/*.csv toutes les 15 s (relancez evaluate_drift → MAJ).
# Prometheus (stack compose du repo) le scrappe via host.docker.internal:9109
# (job « indusense-drift » ajouté dans monitoring/prometheus.yml).
# Usage : uv run python scripts/export_drift_metrics.py
# =============================================================================
from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd

try:
    from prometheus_client import Gauge, start_http_server
except ImportError:
    raise SystemExit(
        "prometheus-client manquant → uv add prometheus-client "
        "(ou pip install prometheus-client)"
    ) from None

RACINE = Path(__file__).resolve().parents[1]
RP = RACINE / "reports" / "drift"

PSI = Gauge(
    "indusense_drift_psi", "PSI par feature vs référence", ["feature", "fenetre", "reference"]
)
KSP = Gauge("indusense_drift_ks_pvalue", "p-value KS", ["feature", "fenetre", "reference"])
MET = {
    c: Gauge(f"indusense_drift_{c}", f"{c} au seuil gelé", ["fenetre"])
    for c in ("rappel", "precision", "taux_alerte", "taux_panne", "pr_auc", "roc_auc")
}


def publier() -> tuple[int, int]:
    n_psi = 0
    for f in RP.glob("psi_f*_ref-*.csv"):
        fen = f.stem.split("_")[1][1:]
        ref = f.stem.split("ref-")[1]
        for _, r in pd.read_csv(f).iterrows():
            PSI.labels(feature=r["feature"], fenetre=fen, reference=ref).set(float(r["psi"]))
            KSP.labels(feature=r["feature"], fenetre=fen, reference=ref).set(float(r["ks_pvalue"]))
        n_psi += 1
    n_eval = 0
    suivi = RP / "suivi_fenetres.csv"
    if suivi.exists():
        df = pd.read_csv(suivi, dtype={"fenetre": str})
        for _, r in df.iterrows():
            for c, g in MET.items():
                if c in r:
                    g.labels(fenetre=str(r["fenetre"])).set(float(r[c]))
        n_eval = len(df)
    return n_psi, n_eval


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=9109)
    ap.add_argument("--intervalle", type=float, default=15.0)
    ap.add_argument("--une-fois", action="store_true")
    args = ap.parse_args()
    start_http_server(args.port)
    print(f"Exporteur drift InduSense : http://localhost:{args.port}/metrics")
    while True:
        n_psi, n_eval = publier()
        print(f"  publié : {n_psi} tables PSI · {n_eval} évaluations")
        if args.une_fois:
            break
        time.sleep(args.intervalle)


if __name__ == "__main__":
    main()
