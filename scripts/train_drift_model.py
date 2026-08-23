# =============================================================================
# scripts/train_drift_model.py — Modèle « production » du TP drift (m31)
# Split TEMPOREL (m8 : les rolling features fuient en split aléatoire — mesuré
# ROC 0,93 aléatoire vs 0,82 temporel) · seuil GELÉ par le coût (m21) :
# FN (panne ratée) = 5 000 € ≫ FP (inspection) = 200 € → seuil* ≈ 200/5200 ≈ 0,038.
# Sorties : artifacts/drift_model.joblib + artifacts/drift_threshold.json (m22).
# =============================================================================
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import average_precision_score, confusion_matrix, roc_auc_score

RACINE = Path(__file__).resolve().parents[1]
COUT_FN, COUT_FP = 5000.0, 200.0


def main() -> None:
    ref = pd.read_csv(RACINE / "data" / "drift" / "reference.csv", parse_dates=["timestamp"])
    features = [
        c for c in ref.columns if c not in ("machine", "timestamp", "panne", "panne_v1", "panne_v2")
    ]
    tr = ref[ref["timestamp"] < "2025-12-01"]
    val = ref[ref["timestamp"] >= "2025-12-01"]
    print(
        f"Train {len(tr)} (aoû-nov) · validation TEMPORELLE {len(val)} (déc) · "
        f"{len(features)} features"
    )

    modele = HistGradientBoostingClassifier(random_state=42).fit(tr[features], tr["panne_v1"])
    proba = modele.predict_proba(val[features])[:, 1]
    pr_auc = float(average_precision_score(val["panne_v1"], proba))
    roc = float(roc_auc_score(val["panne_v1"], proba))

    meilleur, cout_min = 0.5, float("inf")
    for t in np.arange(0.02, 0.981, 0.01):
        yp = (proba >= t).astype(int)
        tn, fp, fn, tp = confusion_matrix(val["panne_v1"], yp).ravel()
        c = COUT_FN * fn + COUT_FP * fp
        if c < cout_min:
            meilleur, cout_min = round(float(t), 2), c
    yp = (proba >= meilleur).astype(int)
    tn, fp, fn, tp = confusion_matrix(val["panne_v1"], yp).ravel()

    art = RACINE / "artifacts"
    art.mkdir(exist_ok=True)
    joblib.dump(modele, art / "drift_model.joblib")
    (art / "drift_threshold.json").write_text(
        json.dumps(
            {
                "modele": "HistGradientBoostingClassifier(random_state=42)",
                "features": features,
                "seuil": meilleur,
                "cout_fn_eur": COUT_FN,
                "cout_fp_eur": COUT_FP,
                "validation": {
                    "periode": "décembre 2025 (split temporel, m8)",
                    "pr_auc": round(pr_auc, 4),
                    "roc_auc": round(roc, 4),
                    "rappel": round(tp / (tp + fn), 4),
                    "precision": round(tp / (tp + fp), 4),
                    "taux_alerte": round(float(yp.mean()), 4),
                },
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        f"Validation déc : PR-AUC {pr_auc:.3f} "
        f"(prévalence {val['panne_v1'].mean():.3f}) · ROC {roc:.3f}"
    )
    print(
        f"Seuil gelé {meilleur} (théorique {COUT_FP/(COUT_FP+COUT_FN):.3f}) : "
        f"rappel {tp/(tp+fn):.3f} · précision {tp/(tp+fp):.3f} · alerte {yp.mean():.2%}"
    )


if __name__ == "__main__":
    main()
