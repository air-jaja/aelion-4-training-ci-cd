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

# `RACINE` rend le script indépendant du dossier courant du terminal. On part
# du chemin réel de CE fichier, puis on remonte d'un niveau jusqu'au dépôt.
RACINE = Path(__file__).resolve().parents[1]

# Les coûts traduisent la priorité métier : rater une panne coûte ici 25 fois
# plus cher que déclencher une inspection inutile. Ces valeurs pilotent le choix
# du seuil ; elles ne modifient pas l'entraînement du classifieur lui-même.
COUT_FN, COUT_FP = 5000.0, 200.0


def main() -> None:
    # ---------------------------------------------------------------------
    # 1. Charger la référence et définir le contrat d'entrée du modèle.
    # ---------------------------------------------------------------------
    # `parse_dates` convertit immédiatement la colonne timestamp en dates
    # pandas. Les comparaisons temporelles qui suivent sont donc chronologiques,
    # et non de simples comparaisons alphabétiques de chaînes.
    ref = pd.read_csv(RACINE / "data" / "drift" / "reference.csv", parse_dates=["timestamp"])

    # Les features sont déduites du fichier pour garder l'ordre réel des
    # colonnes. On retire les identifiants, le temps et toutes les variantes de
    # cible : fournir l'une de ces cibles à X créerait une fuite de données.
    features = [
        c for c in ref.columns if c not in ("machine", "timestamp", "panne", "panne_v1", "panne_v2")
    ]

    # ---------------------------------------------------------------------
    # 2. Faire un split TEMPOREL, comme en vraie mise en production.
    # ---------------------------------------------------------------------
    # Le modèle apprend sur août-novembre, puis est évalué sur le futur
    # (décembre). On ne mélange jamais aléatoirement futur et passé : sinon les
    # features glissantes peuvent rendre l'évaluation artificiellement facile.
    tr = ref[ref["timestamp"] < "2025-12-01"]
    val = ref[ref["timestamp"] >= "2025-12-01"]
    print(
        f"Train {len(tr)} (aoû-nov) · validation TEMPORELLE {len(val)} (déc) · "
        f"{len(features)} features"
    )

    # ---------------------------------------------------------------------
    # 3. Entraîner puis produire des PROBABILITÉS sur la validation.
    # ---------------------------------------------------------------------
    # La graine fixe rend l'expérience reproductible. `fit` apprend uniquement
    # sur `tr`; `val` reste hors entraînement et joue le rôle du futur inconnu.
    modele = HistGradientBoostingClassifier(random_state=42).fit(tr[features], tr["panne_v1"])

    # `predict_proba` renvoie deux colonnes : P(classe 0), puis P(classe 1).
    # `[:, 1]` sélectionne donc la probabilité de panne pour chaque ligne.
    proba = modele.predict_proba(val[features])[:, 1]

    # PR-AUC est prioritaire quand les pannes sont rares ; ROC-AUC complète la
    # lecture. Les deux utilisent les probabilités, donc ne dépendent pas encore
    # du seuil de décision métier.
    pr_auc = float(average_precision_score(val["panne_v1"], proba))
    roc = float(roc_auc_score(val["panne_v1"], proba))

    # ---------------------------------------------------------------------
    # 4. Choisir UNE FOIS le seuil qui minimise le coût métier.
    # ---------------------------------------------------------------------
    # On initialise avec un seuil classique (0,5) et un coût infini : le premier
    # seuil testé sera nécessairement meilleur et deviendra la référence.
    meilleur, cout_min = 0.5, float("inf")

    # On explore 0,02 à 0,98 par pas de 0,01. Pour chaque candidat, on transforme
    # les probabilités en décisions, puis on chiffre FN et FP en euros.
    for t in np.arange(0.02, 0.981, 0.01):
        # Comparaison vectorisée : True/False devient 1/0 avec `astype(int)`.
        yp = (proba >= t).astype(int)

        # `.ravel()` déplie la matrice [[TN, FP], [FN, TP]] en quatre valeurs.
        tn, fp, fn, tp = confusion_matrix(val["panne_v1"], yp).ravel()

        # Les vrais positifs et vrais négatifs ne génèrent pas de coût dans ce
        # scénario simplifié ; seuls FN et FP interviennent dans l'arbitrage.
        c = COUT_FN * fn + COUT_FP * fp
        if c < cout_min:
            # On mémorise à la fois le seuil gagnant et son coût afin que les
            # itérations suivantes puissent le battre — ou le laisser en place.
            meilleur, cout_min = round(float(t), 2), c

    # On recalcule la décision finale et sa matrice au SEUIL RETENU. Ces valeurs
    # serviront aux métriques inscrites dans la carte de seuil.
    yp = (proba >= meilleur).astype(int)
    tn, fp, fn, tp = confusion_matrix(val["panne_v1"], yp).ravel()

    # ---------------------------------------------------------------------
    # 5. Persister le modèle ET sa règle de décision comme un même contrat.
    # ---------------------------------------------------------------------
    # `exist_ok=True` rend la création idempotente : relancer le script ne plante
    # pas si le dossier artifacts existe déjà.
    art = RACINE / "artifacts"
    art.mkdir(exist_ok=True)

    # joblib sérialise l'objet scikit-learn. Ce fichier seul ne suffit toutefois
    # pas : il faut aussi conserver l'ordre des features et le seuil gelé.
    joblib.dump(modele, art / "drift_model.joblib")

    # Le JSON voisin joue le rôle d'une mini model card exécutable. Une future
    # évaluation relira exactement ces features et ce seuil, sans les recalculer
    # sur les données courantes — ce qui éviterait toute mesure honnête du drift.
    (art / "drift_threshold.json").write_text(
        json.dumps(
            {
                "modele": "HistGradientBoostingClassifier(random_state=42)",
                "features": features,
                "seuil": meilleur,
                "cout_fn_eur": COUT_FN,
                "cout_fp_eur": COUT_FP,
                "validation": {
                    # Les métriques ci-dessous décrivent le run de validation
                    # ayant permis de choisir le seuil ; elles servent de base
                    # de comparaison aux fenêtres de production ultérieures.
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

    # ---------------------------------------------------------------------
    # 6. Afficher une preuve lisible dans le terminal du TP.
    # ---------------------------------------------------------------------
    # La prévalence rappelle la baseline naïve de la PR-AUC : une PR-AUC doit
    # toujours être interprétée relativement à la rareté de la classe positive.
    print(
        f"Validation déc : PR-AUC {pr_auc:.3f} "
        f"(prévalence {val['panne_v1'].mean():.3f}) · ROC {roc:.3f}"
    )
    # Le seuil théorique coût_FP/(coût_FP+coût_FN) sert de repère ; le seuil
    # empirique vient, lui, de la minimisation sur la validation temporelle.
    print(
        f"Seuil gelé {meilleur} (théorique {COUT_FP/(COUT_FP+COUT_FN):.3f}) : "
        f"rappel {tp/(tp+fn):.3f} · précision {tp/(tp+fp):.3f} · alerte {yp.mean():.2%}"
    )


if __name__ == "__main__":
    main()
