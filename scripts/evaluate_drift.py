# =============================================================================
# scripts/evaluate_drift.py — Ronde de surveillance d'une fenêtre (m31)
# Table PSI/KS (module indusense.monitoring.drift) + métriques au seuil GELÉ.
# Usage : uv run python scripts/evaluate_drift.py --fenetre 1 [--reference normale]
# =============================================================================
from __future__ import annotations

import argparse
import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score

from indusense.monitoring.drift import drift_table

RACINE = Path(__file__).resolve().parents[1]
DRIFT = RACINE / "data" / "drift"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fenetre", required=True, choices=["1", "2", "3", "janvier"])
    ap.add_argument("--reference", default="normale", choices=["normale", "haute", "train"])
    ap.add_argument("--machine", default=None)
    args = ap.parse_args()

    fic = {
        "normale": "reference_normale.csv",
        "haute": "reference_haute.csv",
        "train": "reference.csv",
    }
    df_ref = pd.read_csv(DRIFT / fic[args.reference])
    df_cur = pd.read_csv(DRIFT / f"fenetre_{args.fenetre}.csv")
    if args.machine:
        df_ref, df_cur = (
            df_ref[df_ref["machine"] == args.machine],
            df_cur[df_cur["machine"] == args.machine],
        )

    table = drift_table(df_ref, df_cur)
    aff = table.copy()
    aff["psi"] = aff["psi"].map(lambda v: f"{v:.3f}")
    aff["ks_pvalue"] = aff["ks_pvalue"].map(lambda v: f"{v:.2e}")
    print(
        f"\n=== PSI/KS fenêtre {args.fenetre} vs référence {args.reference}"
        f"{' · ' + args.machine if args.machine else ''} ==="
    )
    print(aff.to_string(index=False))

    modele = joblib.load(RACINE / "artifacts" / "drift_model.joblib")
    carte = json.loads((RACINE / "artifacts" / "drift_threshold.json").read_text(encoding="utf-8"))
    proba = modele.predict_proba(df_cur[carte["features"]])[:, 1]
    y = df_cur["panne_v1"].to_numpy()
    yp = (proba >= carte["seuil"]).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, yp).ravel()
    m = {
        "fenetre": args.fenetre,
        "reference": args.reference,
        "n": int(len(y)),
        "taux_panne": float(y.mean()),
        "taux_alerte": float(yp.mean()),
        "rappel": tp / (tp + fn) if tp + fn else 0.0,
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "pr_auc": float(average_precision_score(y, proba)),
        "roc_auc": float(roc_auc_score(y, proba)),
        "fn": int(fn),
        "tp": int(tp),
    }
    print(f"\n=== Modèle au seuil gelé {carte['seuil']} ===")
    print(
        f"  panne réelle {m['taux_panne']:.2%} · alerte {m['taux_alerte']:.2%} · "
        f"rappel {m['rappel']:.3f} · précision {m['precision']:.3f} · "
        f"ROC {m['roc_auc']:.3f} · FN={fn}"
    )

    rp = RACINE / "reports" / "drift"
    rp.mkdir(parents=True, exist_ok=True)
    table.to_csv(rp / f"psi_f{args.fenetre}_ref-{args.reference}.csv", index=False)
    suivi = rp / "suivi_fenetres.csv"
    ligne = pd.DataFrame([m])
    if suivi.exists():
        old = pd.read_csv(suivi, dtype={"fenetre": str})
        old = old[~((old["fenetre"] == m["fenetre"]) & (old["reference"] == m["reference"]))]
        ligne = pd.concat([old, ligne], ignore_index=True)
    ligne.to_csv(suivi, index=False)


if __name__ == "__main__":
    main()
