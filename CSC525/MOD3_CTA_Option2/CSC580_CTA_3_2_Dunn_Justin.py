"""CSC580 Module 3 Critical Thinking Assignment, Option 2.

Predict fuel efficiency from the UCI Auto MPG dataset with TensorFlow/Keras.
The script saves every requested screenshot plus evaluation artifacts in outputs/.
"""

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
DATA_URL = (
    "https://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/"
    "auto-mpg.data"
)
ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "outputs"
DATA_DIR = ROOT / "data"


def save_text_figure(text: str, title: str, path: Path, width: float = 11.0) -> None:
    """Save monospaced text as a readable PNG screenshot."""
    lines = text.count("\n") + 1
    height = max(3.0, min(10.0, 0.32 * lines + 1.4))
    fig, ax = plt.subplots(figsize=(width, height))
    ax.axis("off")
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold", pad=12)
    ax.text(0.01, 0.98, text, va="top", family="monospace", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight")
    plt.close(fig)


def load_dataset() -> pd.DataFrame:
    """Download, parse, clean, and one-hot encode the Auto MPG data."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    data_path = DATA_DIR / "auto-mpg.data"
    if not data_path.exists():
        urlretrieve(DATA_URL, data_path)

    columns = [
        "MPG",
        "Cylinders",
        "Displacement",
        "Horsepower",
        "Weight",
        "Acceleration",
        "Model Year",
        "Origin",
        "Car Name",
    ]
    raw = pd.read_csv(
        data_path,
        names=columns,
        na_values="?",
        comment="\t",
        sep=r"\s+",
    )
    raw = raw.drop(columns="Car Name")
    dataset = raw.dropna().copy()
    origin = dataset.pop("Origin").astype(int)
    dataset["USA"] = (origin == 1).astype(float)
    dataset["Europe"] = (origin == 2).astype(float)
    dataset["Japan"] = (origin == 3).astype(float)
    return dataset


def save_pairplot(train_dataset: pd.DataFrame) -> None:
    """Create a dependency-light pair plot for the required four variables."""
    cols = ["MPG", "Cylinders", "Displacement", "Weight"]
    axes = pd.plotting.scatter_matrix(
        train_dataset[cols],
        figsize=(10, 10),
        diagonal="kde",
        alpha=0.65,
        color="#1f77b4",
        grid=True,
    )
    for ax in axes.ravel():
        ax.tick_params(labelsize=7)
    plt.suptitle("Auto MPG Training Data: Pairwise Relationships", y=0.995, fontsize=14)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "02_pairplot.png", dpi=180)
    plt.close()


def build_model(input_size: int, loss: str) -> tf.keras.Model:
    """Build the required two-hidden-layer regression network."""
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Input(shape=(input_size,)),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(64, activation="relu"),
            tf.keras.layers.Dense(1),
        ]
    )
    model.compile(
        loss=loss,
        optimizer=tf.keras.optimizers.RMSprop(learning_rate=0.001),
        metrics=["mae", "mse"],
    )
    return model


def plot_history(history: pd.DataFrame, metric: str, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(history[metric], label=f"Training {metric.upper()}", color="#1f77b4")
    ax.plot(history[f"val_{metric}"], label=f"Validation {metric.upper()}", color="#d62728")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("MAE (MPG)" if metric == "mae" else "MSE (MPG squared)")
    ax.set_title(f"MSE-Loss Model: Training and Validation {metric.upper()}")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main() -> None:
    np.random.seed(SEED)
    tf.keras.utils.set_random_seed(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    dataset = load_dataset()
    save_text_figure(dataset.tail().to_string(), "Step 3: Tail of Cleaned Auto MPG Dataset", OUTPUT_DIR / "01_dataset_tail.png")

    train_dataset = dataset.sample(frac=0.8, random_state=0)
    test_dataset = dataset.drop(train_dataset.index)
    save_pairplot(train_dataset)

    train_stats = train_dataset.describe().transpose()
    train_stats_features = train_stats.drop(index="MPG")
    save_text_figure(
        train_stats_features.to_string(float_format=lambda value: f"{value:,.3f}"),
        "Step 8: Training Feature Statistics",
        OUTPUT_DIR / "03_training_statistics.png",
    )

    train_labels = train_dataset.pop("MPG")
    test_labels = test_dataset.pop("MPG")
    feature_mean = train_stats_features["mean"]
    feature_std = train_stats_features["std"]
    normed_train = (train_dataset - feature_mean) / feature_std
    normed_test = (test_dataset - feature_mean) / feature_std

    mse_model = build_model(len(train_dataset.columns), loss="mse")
    summary_lines: list[str] = []
    mse_model.summary(print_fn=summary_lines.append)
    save_text_figure("\n".join(summary_lines), "Step 14: TensorFlow Model Summary", OUTPUT_DIR / "04_model_summary.png")

    example_batch = normed_train.iloc[:10]
    example_result = mse_model.predict(example_batch, verbose=0).flatten()
    preview = pd.DataFrame({"Actual MPG": train_labels.iloc[:10].values, "Untrained Prediction": example_result})
    save_text_figure(
        preview.to_string(index=False, float_format=lambda value: f"{value:.3f}"),
        "Step 16: Predictions Before Training",
        OUTPUT_DIR / "05_untrained_predictions.png",
    )

    history_mse_obj = mse_model.fit(
        normed_train,
        train_labels,
        epochs=EPOCHS,
        validation_split=0.2,
        verbose=0,
        batch_size=32,
    )
    history_mse = pd.DataFrame(history_mse_obj.history)
    history_mse["epoch"] = history_mse_obj.epoch
    save_text_figure(
        history_mse.tail().to_string(index=False, float_format=lambda value: f"{value:.4f}"),
        "Step 20: Tail of 1,000-Epoch Training History",
        OUTPUT_DIR / "06_history_tail.png",
    )
    plot_history(history_mse, "mae", OUTPUT_DIR / "07_history_mae.png")
    plot_history(history_mse, "mse", OUTPUT_DIR / "08_history_mse.png")

    # Train a second, otherwise identical model to make the Step 22 comparison explicit.
    tf.keras.utils.set_random_seed(SEED)
    mae_model = build_model(len(train_dataset.columns), loss="mae")
    history_mae_obj = mae_model.fit(
        normed_train,
        train_labels,
        epochs=EPOCHS,
        validation_split=0.2,
        verbose=0,
        batch_size=32,
    )

    mse_eval = mse_model.evaluate(normed_test, test_labels, verbose=0, return_dict=True)
    mae_eval = mae_model.evaluate(normed_test, test_labels, verbose=0, return_dict=True)
    comparison = pd.DataFrame(
        [
            {"Model": "MSE loss", "Test MAE": mse_eval["mae"], "Test MSE": mse_eval["mse"], "Test RMSE": np.sqrt(mse_eval["mse"])},
            {"Model": "MAE loss", "Test MAE": mae_eval["mae"], "Test MSE": mae_eval["mse"], "Test RMSE": np.sqrt(mae_eval["mse"])},
        ]
    )
    save_text_figure(
        comparison.to_string(index=False, float_format=lambda value: f"{value:.3f}"),
        "Step 22: MAE-Loss and MSE-Loss Model Comparison",
        OUTPUT_DIR / "09_model_comparison.png",
    )

    predictions = mse_model.predict(normed_test, verbose=0).flatten()
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.scatter(test_labels, predictions, alpha=0.75, color="#1f77b4")
    bounds = [min(test_labels.min(), predictions.min()), max(test_labels.max(), predictions.max())]
    ax.plot(bounds, bounds, color="#d62728", linewidth=2, label="Perfect prediction")
    ax.set_xlabel("True MPG")
    ax.set_ylabel("Predicted MPG")
    ax.set_title("MSE-Loss Model: Predicted vs. True Fuel Efficiency")
    ax.grid(alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "10_predicted_vs_actual.png", dpi=180)
    plt.close(fig)

    residuals = test_labels.to_numpy() - predictions
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(residuals, bins=20, color="#1f77b4", edgecolor="white")
    ax.axvline(0, color="#d62728", linewidth=2)
    ax.set_xlabel("Prediction Error (True MPG - Predicted MPG)")
    ax.set_ylabel("Count")
    ax.set_title("MSE-Loss Model: Distribution of Prediction Errors")
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "11_residual_distribution.png", dpi=180)
    plt.close(fig)

    results = {
        "tensorflow_version": tf.__version__,
        "seed": SEED,
        "epochs_per_model": EPOCHS,
        "rows_after_cleaning": int(len(dataset)),
        "training_rows": int(len(train_dataset)),
        "test_rows": int(len(test_dataset)),
        "feature_count": int(len(train_dataset.columns)),
        "mse_loss_model": {key: float(value) for key, value in mse_eval.items()},
        "mae_loss_model": {key: float(value) for key, value in mae_eval.items()},
        "mse_loss_model_rmse": float(np.sqrt(mse_eval["mse"])),
        "mae_loss_model_rmse": float(np.sqrt(mae_eval["mse"])),
        "mse_model_mean_residual": float(np.mean(residuals)),
        "mse_model_residual_std": float(np.std(residuals, ddof=1)),
        "mse_model_best_validation_mae": float(history_mse["val_mae"].min()),
        "mse_model_best_validation_mse": float(history_mse["val_mse"].min()),
        "mae_model_best_validation_mae": float(min(history_mae_obj.history["val_mae"])),
    }
    (OUTPUT_DIR / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    comparison.to_csv(OUTPUT_DIR / "model_comparison.csv", index=False)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
