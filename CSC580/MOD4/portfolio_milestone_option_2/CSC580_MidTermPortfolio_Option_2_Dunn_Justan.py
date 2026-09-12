"""CSC580 Module 4 Portfolio Milestone, Option 2: early-stopped Auto MPG model."""
from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.request import urlretrieve

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf

SEED = 101
EPOCHS = 1000
PATIENCE = 10
ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "evidence"
DATA = ROOT / "data" / "auto-mpg.data"
DATA_URL = "https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data"


def load_data() -> pd.DataFrame:
    DATA.parent.mkdir(parents=True, exist_ok=True)
    if not DATA.exists():
        urlretrieve(DATA_URL, DATA)
    columns = ["MPG", "Cylinders", "Displacement", "Horsepower", "Weight",
               "Acceleration", "Model Year", "Origin", "Car Name"]
    frame = pd.read_csv(DATA, names=columns, na_values="?", comment="\t", sep=r"\s+")
    frame = frame.drop(columns="Car Name").dropna().copy()
    origin = frame.pop("Origin").astype(int)
    for code, name in [(1, "USA"), (2, "Europe"), (3, "Japan")]:
        frame[name] = (origin == code).astype(float)
    return frame


def build_model(feature_count: int) -> tf.keras.Model:
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(feature_count,)),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(64, activation="relu"),
        tf.keras.layers.Dense(1),
    ])
    model.compile(loss="mse", optimizer=tf.keras.optimizers.RMSprop(0.001), metrics=["mae", "mse"])
    return model


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    np.random.seed(SEED)
    tf.keras.utils.set_random_seed(SEED)
    dataset = load_data()
    train = dataset.sample(frac=0.8, random_state=0)
    test = dataset.drop(train.index)
    train_labels = train.pop("MPG")
    test_labels = test.pop("MPG")
    stats = train.describe().transpose()
    norm_train = (train - stats["mean"]) / stats["std"]
    norm_test = (test - stats["mean"]) / stats["std"]

    model = build_model(len(train.columns))
    early_stop = tf.keras.callbacks.EarlyStopping(
        monitor="val_loss", patience=PATIENCE, restore_best_weights=True
    )
    history_obj = model.fit(
        norm_train, train_labels, epochs=EPOCHS, validation_split=0.2,
        verbose=0, batch_size=32, callbacks=[early_stop]
    )
    history = pd.DataFrame(history_obj.history)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(history["mae"], label="Training MAE")
    ax.plot(history["val_mae"], label="Validation MAE")
    ax.set(xlabel="Epoch", ylabel="MAE (MPG)", title="Auto MPG Training with Early Stopping")
    ax.set_ylim(0, 10); ax.grid(alpha=.3); ax.legend(); fig.tight_layout()
    fig.savefig(OUTPUTS / "01_early_stopping_mae.png", dpi=180); plt.close(fig)

    evaluation = model.evaluate(norm_test, test_labels, verbose=0, return_dict=True)
    evaluation_text = (
        f"TensorFlow {tf.__version__}\nTraining stopped after {len(history)} epochs "
        f"(maximum {EPOCHS}; patience {PATIENCE}).\n"
        f"Testing set Mean Abs Error: {evaluation['mae']:.2f} MPG\n"
        f"Testing set Mean Squared Error: {evaluation['mse']:.2f} MPG^2\n"
        f"Testing set Root Mean Squared Error: {np.sqrt(evaluation['mse']):.2f} MPG"
    )
    fig, ax = plt.subplots(figsize=(9, 3)); ax.axis("off")
    ax.text(.02, .92, evaluation_text, va="top", family="monospace", fontsize=12)
    fig.tight_layout(); fig.savefig(OUTPUTS / "02_test_evaluation.png", dpi=180); plt.close(fig)

    predictions = model.predict(norm_test, verbose=0).flatten()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(test_labels, predictions, alpha=.75)
    lims = [0, 50]; ax.set_xlim(lims); ax.set_ylim(lims); ax.plot(lims, lims, color="crimson")
    ax.set(xlabel="True Values (MPG)", ylabel="Predictions (MPG)", title="True vs. Predicted MPG")
    ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(OUTPUTS / "03_true_vs_predicted.png", dpi=180); plt.close(fig)

    errors = predictions - test_labels.to_numpy()
    fig, ax = plt.subplots(figsize=(8, 5)); ax.hist(errors, bins=25, edgecolor="white")
    ax.axvline(0, color="crimson", linewidth=2)
    ax.set(xlabel="Prediction Error (MPG)", ylabel="Count", title="Distribution of Test Prediction Errors")
    ax.grid(axis="y", alpha=.3); fig.tight_layout(); fig.savefig(OUTPUTS / "04_error_distribution.png", dpi=180); plt.close(fig)

    results = {
        "tensorflow_version": tf.__version__, "seed": SEED, "rows": len(dataset),
        "training_rows": len(train), "test_rows": len(test), "epochs_completed": len(history),
        "best_epoch": int(history["val_loss"].idxmin() + 1),
        "best_validation_mae": float(history["val_mae"].min()),
        "test_mae": float(evaluation["mae"]), "test_mse": float(evaluation["mse"]),
        "test_rmse": float(np.sqrt(evaluation["mse"])),
        "mean_error": float(errors.mean()), "error_std": float(errors.std(ddof=1)),
        "median_error": float(np.median(errors)),
    }
    (OUTPUTS / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
