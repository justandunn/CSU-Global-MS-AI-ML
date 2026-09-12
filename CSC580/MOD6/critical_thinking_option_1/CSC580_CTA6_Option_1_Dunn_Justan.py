"""CSC580 Module 6 Critical Thinking Assignment, Option 1.

Train and evaluate a convolutional neural network on CIFAR-10. Evidence files,
metrics, predictions, and the saved model are written beside the script.
"""
from __future__ import annotations

import json
import os
import platform
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import ConfusionMatrixDisplay, classification_report, confusion_matrix

SEED = 580
ROOT = Path(__file__).resolve().parent
EVIDENCE = ROOT / "evidence"
MODEL_PATH = ROOT / "cifar10_cnn.keras"
CLASS_NAMES = ["airplane", "automobile", "bird", "cat", "deer", "dog", "frog", "horse", "ship", "truck"]


def build_model() -> tf.keras.Model:
    inputs = tf.keras.Input(shape=(32, 32, 3), name="cifar10_image")
    x = tf.keras.layers.RandomFlip("horizontal", seed=SEED)(inputs)
    x = tf.keras.layers.RandomTranslation(0.08, 0.08, seed=SEED)(x)
    x = tf.keras.layers.Conv2D(32, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv2D(32, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.MaxPooling2D()(x)
    x = tf.keras.layers.Dropout(0.20, seed=SEED)(x)
    x = tf.keras.layers.Conv2D(64, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Conv2D(64, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.MaxPooling2D()(x)
    x = tf.keras.layers.Dropout(0.30, seed=SEED)(x)
    x = tf.keras.layers.Conv2D(128, 3, padding="same", activation="relu")(x)
    x = tf.keras.layers.GlobalAveragePooling2D()(x)
    x = tf.keras.layers.Dense(128, activation="relu")(x)
    x = tf.keras.layers.Dropout(0.40, seed=SEED)(x)
    outputs = tf.keras.layers.Dense(10, activation="softmax", name="class_probabilities")(x)
    return tf.keras.Model(inputs, outputs, name="cifar10_cnn")


def main() -> None:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    tf.keras.utils.set_random_seed(SEED)
    tf.config.experimental.enable_op_determinism()

    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0
    y_train = y_train.squeeze()
    y_test = y_test.squeeze()

    fig, axes = plt.subplots(2, 5, figsize=(10, 4.8))
    for class_id, ax in enumerate(axes.ravel()):
        idx = int(np.flatnonzero(y_train == class_id)[0])
        ax.imshow(x_train[idx])
        ax.set_title(CLASS_NAMES[class_id])
        ax.axis("off")
    fig.suptitle("Representative CIFAR-10 Training Images", fontweight="bold")
    fig.tight_layout()
    fig.savefig(EVIDENCE / "01_cifar10_samples.png", dpi=180)
    plt.close(fig)

    model = build_model()
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    callbacks = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=3, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=2, min_lr=1e-5),
    ]
    history = model.fit(
        x_train,
        y_train,
        validation_split=0.10,
        epochs=10,
        batch_size=128,
        shuffle=True,
        callbacks=callbacks,
        verbose=2,
    )

    test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=0)
    probabilities = model.predict(x_test, batch_size=256, verbose=0)
    predictions = probabilities.argmax(axis=1)
    cm = confusion_matrix(y_test, predictions, labels=range(10))
    report = classification_report(y_test, predictions, target_names=CLASS_NAMES, output_dict=True, zero_division=0)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))
    epochs = np.arange(1, len(history.history["loss"]) + 1)
    axes[0].plot(epochs, history.history["loss"], label="Training")
    axes[0].plot(epochs, history.history["val_loss"], label="Validation")
    axes[0].set(title="Cross-Entropy Loss", xlabel="Epoch", ylabel="Loss")
    axes[0].legend()
    axes[1].plot(epochs, history.history["accuracy"], label="Training")
    axes[1].plot(epochs, history.history["val_accuracy"], label="Validation")
    axes[1].set(title="Classification Accuracy", xlabel="Epoch", ylabel="Accuracy", ylim=(0, 1))
    axes[1].legend()
    fig.tight_layout()
    fig.savefig(EVIDENCE / "02_training_history.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(10, 9))
    ConfusionMatrixDisplay(cm, display_labels=CLASS_NAMES).plot(ax=ax, cmap="Blues", colorbar=False, xticks_rotation=45)
    ax.set_title("CIFAR-10 Test Confusion Matrix")
    fig.tight_layout()
    fig.savefig(EVIDENCE / "03_confusion_matrix.png", dpi=180)
    plt.close(fig)

    rng = np.random.default_rng(SEED)
    selected = rng.choice(len(x_test), size=20, replace=False)
    fig, axes = plt.subplots(4, 5, figsize=(11, 9))
    for idx, ax in zip(selected, axes.ravel()):
        actual = CLASS_NAMES[int(y_test[idx])]
        predicted = CLASS_NAMES[int(predictions[idx])]
        confidence = float(probabilities[idx, predictions[idx]])
        ax.imshow(x_test[idx])
        ax.set_title(f"A: {actual}\nP: {predicted} ({confidence:.0%})", color="green" if actual == predicted else "red", fontsize=9)
        ax.axis("off")
    fig.suptitle("Representative Held-Out Test Predictions", fontweight="bold")
    fig.tight_layout()
    fig.savefig(EVIDENCE / "04_test_predictions.png", dpi=180)
    plt.close(fig)

    model.save(MODEL_PATH)
    results = {
        "seed": SEED,
        "python_version": platform.python_version(),
        "tensorflow_version": tf.__version__,
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "epochs_completed": int(len(history.history["loss"])),
        "best_validation_accuracy": float(max(history.history["val_accuracy"])),
        "test_loss": float(test_loss),
        "test_accuracy": float(test_accuracy),
        "parameters": int(model.count_params()),
        "classification_report": report,
        "confusion_matrix": cm.tolist(),
    }
    (EVIDENCE / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    (EVIDENCE / "training_history.json").write_text(json.dumps(history.history, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
