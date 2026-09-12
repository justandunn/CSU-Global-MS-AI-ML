"""Train and evaluate the CSC580 Module 2 video-game earnings model.

The program follows Option 2 of the Module 2 Critical Thinking Assignment:
it scales the supplied data, trains a dense Keras regression model for 50
epochs, evaluates the held-out test set, saves and reloads the model, and
predicts earnings for the proposed product.
"""

from __future__ import annotations

import json
import os
import random
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from tensorflow import keras


SEED = 580
EPOCHS = 50
BATCH_SIZE = 32
TARGET = "total_earnings"
FEATURES = [
    "critic_rating",
    "is_action",
    "is_exclusive_to_us",
    "is_portable",
    "is_role_playing",
    "is_sequel",
    "is_sports",
    "suitable_for_kids",
    "unit_price",
]

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "output"


def set_reproducible_seed() -> None:
    """Set seeds used by Python, NumPy, and TensorFlow."""

    random.seed(SEED)
    np.random.seed(SEED)
    tf.keras.utils.set_random_seed(SEED)
    try:
        tf.config.experimental.enable_op_determinism()
    except Exception:
        # Deterministic operations are best effort across TensorFlow builds.
        pass


def load_and_validate_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the supplied CSV files and enforce the assignment schema."""

    training = pd.read_csv(DATA_DIR / "sales_data_training.csv")
    testing = pd.read_csv(DATA_DIR / "sales_data_test.csv")
    proposed = pd.read_csv(DATA_DIR / "proposed_new_product.csv")

    expected_supervised = FEATURES[:8] + [TARGET, FEATURES[8]]
    if list(training.columns) != expected_supervised:
        raise ValueError(f"Unexpected training columns: {list(training.columns)}")
    if list(testing.columns) != expected_supervised:
        raise ValueError(f"Unexpected testing columns: {list(testing.columns)}")
    if list(proposed.columns) != FEATURES:
        raise ValueError(f"Unexpected proposed-product columns: {list(proposed.columns)}")

    for name, frame in {
        "training": training,
        "testing": testing,
        "proposed product": proposed,
    }.items():
        if frame.empty:
            raise ValueError(f"The {name} dataset is empty.")
        if frame.isna().any().any():
            raise ValueError(f"The {name} dataset contains missing values.")
        if not all(pd.api.types.is_numeric_dtype(dtype) for dtype in frame.dtypes):
            raise TypeError(f"The {name} dataset contains nonnumeric columns.")

    if len(proposed) != 1:
        raise ValueError("The proposed-product dataset must contain exactly one row.")

    return training, testing, proposed


def build_model() -> keras.Model:
    """Create the required nine-input, one-output dense regression model."""

    model = keras.Sequential(
        [
            keras.Input(shape=(len(FEATURES),), name="game_features"),
            keras.layers.Dense(50, activation="relu", name="hidden_1"),
            keras.layers.Dense(100, activation="relu", name="hidden_2"),
            keras.layers.Dense(50, activation="relu", name="hidden_3"),
            keras.layers.Dense(1, activation="linear", name="earnings_output"),
        ],
        name="video_game_earnings_regressor",
    )
    model.compile(
        optimizer=keras.optimizers.Adam(),
        loss="mean_squared_error",
        metrics=[keras.metrics.MeanAbsoluteError(name="mae")],
    )
    return model


def save_training_plot(history: keras.callbacks.History) -> None:
    """Save a readable training-loss figure for the written report."""

    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    epochs = np.arange(1, EPOCHS + 1)
    ax.plot(epochs, history.history["loss"], color="#1f4e79", linewidth=2)
    ax.set_title("Training Mean Squared Error by Epoch")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Scaled MSE")
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(OUTPUT_DIR / "training_loss.png", dpi=180)
    plt.close(fig)


def main() -> None:
    """Execute preprocessing, training, evaluation, and prediction."""

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    set_reproducible_seed()
    training, testing, proposed = load_and_validate_data()

    print("CSC580 Module 2 - Option 2: Predicting Future Sales")
    print(f"TensorFlow version: {tf.__version__}")
    print(f"Training rows: {len(training)} | Testing rows: {len(testing)}")
    print(f"Input features: {len(FEATURES)} | Missing values: 0")
    print(f"Random seed: {SEED}")

    feature_scaler = MinMaxScaler(feature_range=(0, 1))
    target_scaler = MinMaxScaler(feature_range=(0, 1))

    # Fit scalers on training data only to prevent test-data leakage.
    x_train = feature_scaler.fit_transform(training[FEATURES]).astype("float32")
    y_train = target_scaler.fit_transform(training[[TARGET]]).astype("float32")
    x_test = feature_scaler.transform(testing[FEATURES]).astype("float32")
    y_test = target_scaler.transform(testing[[TARGET]]).astype("float32")

    pd.DataFrame(x_train, columns=FEATURES).assign(
        total_earnings=y_train[:, 0]
    ).to_csv(OUTPUT_DIR / "sales_data_training_scaled.csv", index=False)
    pd.DataFrame(x_test, columns=FEATURES).assign(
        total_earnings=y_test[:, 0]
    ).to_csv(OUTPUT_DIR / "sales_data_testing_scaled.csv", index=False)
    joblib.dump(feature_scaler, OUTPUT_DIR / "feature_scaler.joblib")
    joblib.dump(target_scaler, OUTPUT_DIR / "target_scaler.joblib")

    model = build_model()
    model.summary()
    history = model.fit(
        x_train,
        y_train,
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        shuffle=True,
        verbose=2,
    )

    evaluation = model.evaluate(x_test, y_test, verbose=0, return_dict=True)
    scaled_mse = float(evaluation["loss"])

    scaled_predictions = model.predict(x_test, verbose=0)
    dollar_predictions = target_scaler.inverse_transform(scaled_predictions).reshape(-1)
    actual_dollars = testing[TARGET].to_numpy(dtype="float64")
    dollar_mse = float(mean_squared_error(actual_dollars, dollar_predictions))
    dollar_rmse = float(np.sqrt(dollar_mse))
    dollar_mae = float(mean_absolute_error(actual_dollars, dollar_predictions))

    model_path = OUTPUT_DIR / "trained_model.h5"
    model.save(model_path)
    reloaded_model = keras.models.load_model(model_path, compile=False)

    # The supplied proposed-product row is already scaled from zero to one.
    proposed_scaled = proposed[FEATURES].to_numpy(dtype="float32")
    if np.any(proposed_scaled < 0) or np.any(proposed_scaled > 1):
        raise ValueError("The proposed-product features are expected to be pre-scaled.")
    proposed_scaled_prediction = reloaded_model.predict(proposed_scaled, verbose=0)
    proposed_prediction = float(
        target_scaler.inverse_transform(proposed_scaled_prediction)[0, 0]
    )

    print(f"Test MSE (scaled): {scaled_mse:.8f}")
    print(f"Test MSE (dollars squared): {dollar_mse:,.2f}")
    print(f"Test RMSE (dollars): ${dollar_rmse:,.2f}")
    print(f"Test MAE (dollars): ${dollar_mae:,.2f}")
    print(f"Earnings Prediction for Proposed Product: ${proposed_prediction:,.2f}")
    print(f"Model saved and reloaded successfully: {model_path.name}")

    metrics = {
        "seed": SEED,
        "epochs": EPOCHS,
        "batch_size": BATCH_SIZE,
        "training_rows": int(len(training)),
        "testing_rows": int(len(testing)),
        "input_features": len(FEATURES),
        "scaled_test_mse": scaled_mse,
        "test_mse_dollars_squared": dollar_mse,
        "test_rmse_dollars": dollar_rmse,
        "test_mae_dollars": dollar_mae,
        "proposed_product_prediction_dollars": proposed_prediction,
        "tensorflow_version": tf.__version__,
    }
    (OUTPUT_DIR / "metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    pd.DataFrame(history.history).assign(epoch=np.arange(1, EPOCHS + 1)).to_csv(
        OUTPUT_DIR / "training_history.csv", index=False
    )
    pd.DataFrame(
        {
            "actual_earnings": actual_dollars,
            "predicted_earnings": dollar_predictions,
            "error": dollar_predictions - actual_dollars,
        }
    ).to_csv(OUTPUT_DIR / "test_predictions.csv", index=False)
    save_training_plot(history)


if __name__ == "__main__":
    main()

