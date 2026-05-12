"""
CSC510 Module 6 Critical Thinking Assignment (110 pts)
Naive Bayes Classifier (scikit-learn) + Manual Posterior Computation

Rubric coverage:
- Frequency table (counts) from dataset
- Likelihood table P(feature=value | class)
- Posterior probability for each class
- Laplacian correction (add-one smoothing)
- Displays probability prediction for user input
- Uses scikit-learn Naive Bayes (MultinomialNB) and shows predict_proba

HOW TO RUN / TEST
-----------------
1) Install deps once (in the same interpreter you run with):
     python -m pip install scikit-learn pandas numpy

2) Run:
     python CSC510_MOD6_NaiveBayes_InventoryRisk.py

3) Suggested test input (good for screenshot):
   DemandVar=high, LeadTime=long, Criticality=high, SupplierRel=low
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from sklearn.preprocessing import OneHotEncoder
from sklearn.naive_bayes import MultinomialNB


def build_dataset() -> pd.DataFrame:
    rows = [
        ("low",  "short",  "low",  "high", "Low"),
        ("low",  "short",  "high", "high", "Low"),
        ("low",  "medium", "low",  "high", "Low"),
        ("low",  "medium", "high", "high", "Low"),
        ("med",  "short",  "low",  "high", "Low"),
        ("med",  "medium", "low",  "high", "Low"),
        ("med",  "short",  "high", "high", "Low"),
        ("med",  "medium", "high", "high", "High"),

        ("high", "medium", "high", "low",  "High"),
        ("high", "long",   "high", "low",  "High"),
        ("high", "long",   "high", "high", "High"),
        ("high", "long",   "low",  "low",  "High"),
        ("high", "medium", "low",  "low",  "High"),
        ("med",  "long",   "high", "low",  "High"),
        ("med",  "long",   "low",  "low",  "High"),
        ("low",  "long",   "high", "low",  "High"),
    ]
    return pd.DataFrame(
        rows,
        columns=["DemandVar", "LeadTime", "Criticality", "SupplierRel", "StockoutRisk"],
    )


def frequency_tables(df: pd.DataFrame, features: List[str], target: str) -> Dict[str, pd.DataFrame]:
    classes = sorted(df[target].unique())
    tables: Dict[str, pd.DataFrame] = {}

    for f in features:
        ct = pd.crosstab(df[f], df[target])
        for c in classes:
            if c not in ct.columns:
                ct[c] = 0
        tables[f] = ct[classes]

    return tables


def likelihood_tables_with_laplace(
    freq_tables: Dict[str, pd.DataFrame],
    df: pd.DataFrame,
    features: List[str],
    target: str,
    alpha: float = 1.0,
) -> Dict[str, pd.DataFrame]:
    classes = sorted(df[target].unique())
    class_counts = df[target].value_counts().to_dict()

    likelihoods: Dict[str, pd.DataFrame] = {}
    for f in features:
        ft = freq_tables[f].copy()
        V = ft.shape[0]  # possible values count for feature f
        lk = ft.astype(float)

        for c in classes:
            denom = float(np.asarray(class_counts[c]).item()) + float(np.asarray(alpha).item()) * float(np.asarray(V).item())
            lk[c] = (ft[c].astype(float) + float(np.asarray(alpha).item())) / denom

        likelihoods[f] = lk

    return likelihoods


def priors(df: pd.DataFrame, target: str) -> Dict[str, float]:
    counts = df[target].value_counts()
    total = float(np.asarray(counts.sum()).item())
    return {str(cls): float(np.asarray(counts[cls] / total).item()) for cls in counts.index}


def manual_posterior(
    user_x: Dict[str, str],
    prior: Dict[str, float],
    likelihoods: Dict[str, pd.DataFrame],
    classes: List[str],
) -> Tuple[Dict[str, float], Dict[str, float]]:
    unnorm: Dict[str, float] = {}

    for c in classes:
        p = float(np.asarray(prior[c]).item())
        for f, v in user_x.items():
            lk_table = likelihoods[f]
            if v not in lk_table.index:
                raise ValueError(
                    f"Value '{v}' not in training for feature '{f}'. Valid: {list(lk_table.index)}"
                )
            p *= float(np.asarray(lk_table.loc[v, c]).item())
        unnorm[c] = p

    total = float(np.asarray(sum(unnorm.values())).item())
    norm: Dict[str, float] = {c: (unnorm[c] / total if total > 0 else 0.0) for c in classes}
    return unnorm, norm


def sklearn_multinomial_nb(
    df: pd.DataFrame,
    features: List[str],
    target: str,
    user_x: Dict[str, str],
) -> Tuple[str, Dict[str, float], List[str]]:
    X = df[features].copy()
    y = df[target].copy()

    enc = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    X_enc = enc.fit_transform(X)

    model = MultinomialNB(alpha=1.0)  # Laplace-style smoothing
    model.fit(X_enc, y)

    user_df = pd.DataFrame([user_x])[features]
    user_enc = enc.transform(user_df)

    proba_arr = model.predict_proba(user_enc)[0]
    classes = [str(c) for c in model.classes_]
    pred = str(model.predict(user_enc)[0])

    proba: Dict[str, float] = {classes[i]: float(np.asarray(proba_arr[i]).item()) for i in range(len(classes))}
    return pred, proba, classes


def prompt_choice(label: str, options: List[str]) -> str:
    opts = "/".join(options)
    while True:
        raw = input(f"{label} ({opts}): ").strip().lower()
        if raw in options:
            return raw
        print(f"Please choose one of: {options}")


def main() -> None:
    df = build_dataset()
    features = ["DemandVar", "LeadTime", "Criticality", "SupplierRel"]
    target = "StockoutRisk"
    classes = sorted([str(c) for c in df[target].unique()])

    print("\nCSC510 Module 6 — Naive Bayes Classifier (Inventory Risk)")
    print("=========================================================")
    print("\nDataset preview:")
    print(df.head(8).to_string(index=False))

    # 1) Frequency tables
    freq = frequency_tables(df, features, target)
    print("\n1) FREQUENCY TABLES (counts by feature value and class)")
    print("------------------------------------------------------")
    for f in features:
        print(f"\nFeature: {f}")
        print(freq[f].to_string())

    # 2) Likelihood tables with Laplace smoothing
    alpha = 1.0
    lk = likelihood_tables_with_laplace(freq, df, features, target, alpha=alpha)
    print("\n2) LIKELIHOOD TABLES with Laplacian correction (add-one)")
    print("--------------------------------------------------------")
    print(f"Laplace alpha = {alpha}")
    for f in features:
        print(f"\nFeature: {f}  =>  P({f}=value | class)")
        print(lk[f].to_string(float_format=lambda x: f"{float(np.asarray(x).item()):.4f}"))

    # 3) Priors
    pr = priors(df, target)
    print("\n3) CLASS PRIORS  P(class)")
    print("------------------------")
    for c in classes:
        print(f"P({c}) = {pr[c]:.4f}")

    # User input
    print("\nNow enter a test case for classification.")
    print("Sample (good for screenshot): DemandVar=high, LeadTime=long, Criticality=high, SupplierRel=low\n")

    user_x: Dict[str, str] = {
        "DemandVar": prompt_choice("Demand variability", ["low", "med", "high"]),
        "LeadTime": prompt_choice("Lead time", ["short", "medium", "long"]),
        "Criticality": prompt_choice("SKU criticality", ["low", "high"]),
        "SupplierRel": prompt_choice("Supplier reliability", ["low", "high"]),
    }

    # 4) Manual posterior
    unnorm, norm = manual_posterior(user_x, pr, lk, classes)
    print("\n4) POSTERIOR COMPUTATION (Manual Naive Bayes)")
    print("--------------------------------------------")
    print("Posterior ∝ P(class) * Π P(feature=value | class)\n")
    print("Input:")
    for k, v in user_x.items():
        print(f"  {k} = {v}")

    print("\nUnnormalized posteriors:")
    for c in classes:
        print(f"  score({c}) = {unnorm[c]:.10f}")

    print("\nNormalized posteriors (probabilities):")
    for c in classes:
        print(f"  P({c} | x) = {norm[c]:.4f}")

    manual_pred = max(classes, key=lambda c: norm[c])
    print(f"\nManual prediction: {manual_pred}")

    # 5) scikit-learn prediction
    sk_pred, sk_proba, sk_classes = sklearn_multinomial_nb(df, features, target, user_x)
    print("\n5) scikit-learn MultinomialNB Prediction")
    print("---------------------------------------")
    print("Model: MultinomialNB(alpha=1.0) with one-hot encoding")
    for c in sk_classes:
        print(f"  P({c} | x) = {sk_proba[c]:.4f}")
    print(f"scikit-learn prediction: {sk_pred}")

    print("\n(End of program.)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")