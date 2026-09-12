"""CSC580 Module 5 Critical Thinking Assignment, Option 2.

Build and evaluate a reproducible random forest classifier for the Iris dataset.
The script saves every required output as evidence for the accompanying report.
"""
from __future__ import annotations

import json
import platform
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from sklearn.datasets import load_iris
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import ConfusionMatrixDisplay, accuracy_score, classification_report, confusion_matrix

SEED = 0
ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"


def save_text_figure(text: str, title: str, filename: str, height: float = 4.0) -> None:
    fig, ax = plt.subplots(figsize=(10, height))
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=13, fontweight="bold", pad=12)
    ax.text(0.01, 0.98, text, va="top", family="monospace", fontsize=10)
    fig.tight_layout()
    fig.savefig(EVIDENCE / filename, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    np.random.seed(SEED)

    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["species"] = pd.Categorical.from_codes(iris.target, iris.target_names)
    save_text_figure(df.head().to_string(), "Iris Dataset: First Five Rows", "01_dataset_head.png")

    # Follow the assignment's reproducible 75 percent random-mask split.
    df["is_train"] = np.random.uniform(0, 1, len(df)) <= 0.75
    train = df[df["is_train"]].copy()
    test = df[~df["is_train"]].copy()
    split_text = f"Number of observations in training data: {len(train)}\nNumber of observations in test data: {len(test)}\n\n{df.head().to_string()}"
    save_text_figure(split_text, "Reproducible Training and Test Split", "02_train_test_split.png", 4.8)

    features = list(df.columns[:4])
    y = pd.factorize(train["species"], sort=False)[0]
    preprocessing_text = f"Feature columns:\n{features}\n\nEncoded training targets (first 30):\n{y[:30]}"
    save_text_figure(preprocessing_text, "Features and Encoded Target", "03_preprocessing.png")

    classifier = RandomForestClassifier(n_estimators=100, n_jobs=2, random_state=SEED)
    classifier.fit(train[features], y)

    predictions = classifier.predict(test[features])
    probabilities = classifier.predict_proba(test[features])
    target_names = np.asarray(iris.target_names)
    actual = pd.Categorical(test["species"], categories=iris.target_names).codes
    comparison = pd.DataFrame({"actual": test["species"].astype(str), "predicted": target_names[predictions]})
    probability_df = pd.DataFrame(probabilities, columns=[f"P({name})" for name in iris.target_names], index=test.index)
    save_text_figure(probability_df.head(10).round(4).to_string(), "Predicted Probabilities: First Ten Test Observations", "04_predicted_probabilities.png", 5.2)
    save_text_figure(comparison.head().to_string(), "Actual and Predicted Species: First Five Test Observations", "05_actual_vs_predicted.png")

    cm = confusion_matrix(actual, predictions, labels=[0, 1, 2])
    fig, ax = plt.subplots(figsize=(7, 6))
    ConfusionMatrixDisplay(cm, display_labels=iris.target_names).plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title("Random Forest Confusion Matrix")
    fig.tight_layout()
    fig.savefig(EVIDENCE / "06_confusion_matrix.png", dpi=180)
    plt.close(fig)

    importance = pd.DataFrame({"feature": features, "importance": classifier.feature_importances_}).sort_values("importance")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(importance["feature"], importance["importance"], color="#2E74B5")
    ax.set_xlabel("Mean decrease in impurity")
    ax.set_title("Random Forest Feature Importance")
    fig.tight_layout()
    fig.savefig(EVIDENCE / "07_feature_importance.png", dpi=180)
    plt.close(fig)

    report = classification_report(actual, predictions, target_names=iris.target_names, output_dict=True, zero_division=0)
    results = {
        "seed": SEED,
        "python_version": platform.python_version(),
        "numpy_version": np.__version__,
        "pandas_version": pd.__version__,
        "scikit_learn_version": sklearn.__version__,
        "training_rows": int(len(train)),
        "test_rows": int(len(test)),
        "accuracy": float(accuracy_score(actual, predictions)),
        "confusion_matrix": cm.tolist(),
        "feature_importance": dict(zip(features, classifier.feature_importances_.tolist())),
        "classification_report": report,
    }
    (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    comparison.to_csv(EVIDENCE / "predictions.csv", index=True)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
