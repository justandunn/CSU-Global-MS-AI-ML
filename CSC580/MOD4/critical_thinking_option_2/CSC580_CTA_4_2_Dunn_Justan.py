"""CSC580 Module 4 Critical Thinking, Option 2: TensorFlow logistic regression."""
from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_ENABLE_ONEDNN_OPTS", "0")

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf

SEED = 5804
ROOT = Path(__file__).resolve().parent
OUTPUTS = ROOT / "evidence"


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    np.random.seed(SEED); tf.keras.utils.set_random_seed(SEED)
    x_zeros = np.random.multivariate_normal([-1, -1], np.eye(2), 50).astype("float32")
    x_ones = np.random.multivariate_normal([1, 1], np.eye(2), 50).astype("float32")
    x = np.vstack([x_zeros, x_ones])
    y = np.vstack([np.zeros((50, 1)), np.ones((50, 1))]).astype("float32")

    fig, ax = plt.subplots(figsize=(7, 6)); ax.scatter(*x_zeros.T, label="Class 0", alpha=.8)
    ax.scatter(*x_ones.T, label="Class 1", alpha=.8); ax.set(xlabel="x1", ylabel="x2", title="Synthetic Gaussian Classes")
    ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(OUTPUTS / "01_input_classes.png", dpi=180); plt.close(fig)

    inputs = tf.keras.Input(shape=(2,), name="features")
    probabilities = tf.keras.layers.Dense(1, activation="sigmoid", name="probability")(inputs)
    model = tf.keras.Model(inputs, probabilities, name="logistic_regression")
    model.compile(optimizer=tf.keras.optimizers.Adam(.05), loss="binary_crossentropy", metrics=["accuracy"])
    tensorboard = tf.keras.callbacks.TensorBoard(log_dir=str(ROOT / "logs"), histogram_freq=1)
    history = model.fit(x, y, epochs=200, batch_size=20, verbose=0, callbacks=[tensorboard])

    probs = model.predict(x, verbose=0).flatten(); predicted = (probs >= .5).astype(int)
    loss, accuracy = model.evaluate(x, y, verbose=0)
    weights, bias = model.layers[-1].get_weights()

    fig, ax = plt.subplots(figsize=(7, 6))
    correct = predicted == y.flatten().astype(int)
    ax.scatter(x[correct, 0], x[correct, 1], c=predicted[correct], cmap="coolwarm", alpha=.8, label="Correct")
    ax.scatter(x[~correct, 0], x[~correct, 1], facecolors="none", edgecolors="black", s=100, label="Misclassified")
    grid_x = np.linspace(x[:,0].min()-.5, x[:,0].max()+.5, 100)
    grid_y = -(weights[0,0] * grid_x + bias[0]) / weights[1,0]
    ax.plot(grid_x, grid_y, "k--", label="p = 0.50 boundary")
    ax.set(xlabel="x1", ylabel="x2", title="TensorFlow Logistic Regression Predictions")
    ax.grid(alpha=.3); ax.legend(); fig.tight_layout(); fig.savefig(OUTPUTS / "02_predictions_boundary.png", dpi=180); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5)); ax.plot(history.history["loss"], label="Cross-entropy loss")
    ax2 = ax.twinx(); ax2.plot(history.history["accuracy"], color="darkorange", label="Accuracy")
    ax.set(xlabel="Epoch", ylabel="Loss", title="Logistic Regression Training History"); ax2.set_ylabel("Accuracy")
    ax.grid(alpha=.3); fig.tight_layout(); fig.savefig(OUTPUTS / "03_training_history.png", dpi=180); plt.close(fig)

    results = {"tensorflow_version": tf.__version__, "seed": SEED, "samples": 100,
               "loss": float(loss), "accuracy": float(accuracy), "weights": weights.flatten().tolist(),
               "bias": float(bias[0]), "misclassified": int((~correct).sum())}
    (OUTPUTS / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
