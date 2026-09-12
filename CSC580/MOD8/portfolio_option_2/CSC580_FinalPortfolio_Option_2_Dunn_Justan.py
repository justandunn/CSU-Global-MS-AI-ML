"""Train and evaluate an encoder-decoder LSTM for sequence prediction.

CSC580 Portfolio Project Option 2

The source contains six random integers from 1 through 50. The target is the
first three source integers in reverse order. A value of 0 is reserved as the
start-of-sequence token. The script creates deterministic training and
validation data, trains a Keras encoder-decoder model with teacher forcing,
builds separate inference models, evaluates 100 newly generated sequences,
and saves runtime evidence and figures.
"""

from __future__ import annotations

import json
import os
import platform
import random
import sys
import time
from pathlib import Path

os.environ.setdefault("TF_CPP_MIN_LOG_LEVEL", "2")
os.environ.setdefault("TF_DETERMINISTIC_OPS", "1")

import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from keras import Model
from keras.callbacks import EarlyStopping
from keras.layers import Dense, Input, LSTM
from keras.optimizers import Adam
from keras.utils import to_categorical


SEED = 580
N_FEATURES = 51  # Integers 1-50 plus start token 0.
N_STEPS_IN = 6
N_STEPS_OUT = 3
N_UNITS = 128
TRAIN_SAMPLES = 20_000
VALIDATION_SAMPLES = 2_000
TEST_SAMPLES = 100
MAX_EPOCHS = 40
BATCH_SIZE = 64
OUTPUT_DIR = Path(__file__).resolve().parent / "evidence"


def configure_reproducibility(seed: int = SEED) -> None:
    """Configure repeatable pseudo-random behavior where supported."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    tf.keras.utils.set_random_seed(seed)
    try:
        tf.config.experimental.enable_op_determinism()
    except Exception:
        # Deterministic operations are best effort across TensorFlow builds.
        pass


def generate_sequence(
    length: int, cardinality: int, rng: np.random.Generator
) -> list[int]:
    """Return random integers in [1, cardinality - 1]; zero stays reserved."""
    return rng.integers(1, cardinality, size=length).tolist()


def get_dataset(
    n_in: int,
    n_out: int,
    cardinality: int,
    n_samples: int,
    rng: np.random.Generator,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Create source, shifted decoder-input, and expected target sequences."""
    sources: list[list[int]] = []
    decoder_inputs: list[list[int]] = []
    targets: list[list[int]] = []

    for _ in range(n_samples):
        source = generate_sequence(n_in, cardinality, rng)
        target = list(reversed(source[:n_out]))
        target_in = [0] + target[:-1]
        sources.append(source)
        decoder_inputs.append(target_in)
        targets.append(target)

    source_array = np.asarray(sources, dtype=np.int32)
    decoder_array = np.asarray(decoder_inputs, dtype=np.int32)
    target_array = np.asarray(targets, dtype=np.int32)

    source_encoded = to_categorical(source_array, num_classes=cardinality)
    decoder_encoded = to_categorical(decoder_array, num_classes=cardinality)
    target_encoded = to_categorical(target_array, num_classes=cardinality)
    return (
        source_encoded.astype(np.float32),
        decoder_encoded.astype(np.float32),
        target_encoded.astype(np.float32),
        source_array,
        target_array,
    )


def define_models(
    n_input: int, n_output: int, n_units: int
) -> tuple[Model, Model, Model]:
    """Create the training model and the encoder/decoder inference models."""
    encoder_inputs = Input(shape=(None, n_input), name="encoder_input")
    encoder_lstm = LSTM(n_units, return_state=True, name="encoder_lstm")
    _, state_h, state_c = encoder_lstm(encoder_inputs)
    encoder_states = [state_h, state_c]

    decoder_inputs = Input(shape=(None, n_output), name="decoder_input")
    decoder_lstm = LSTM(
        n_units, return_sequences=True, return_state=True, name="decoder_lstm"
    )
    decoder_outputs, _, _ = decoder_lstm(
        decoder_inputs, initial_state=encoder_states
    )
    decoder_dense = Dense(n_output, activation="softmax", name="token_probability")
    decoder_outputs = decoder_dense(decoder_outputs)
    training_model = Model(
        [encoder_inputs, decoder_inputs], decoder_outputs, name="training_model"
    )

    encoder_model = Model(encoder_inputs, encoder_states, name="inference_encoder")

    decoder_state_input_h = Input(shape=(n_units,), name="decoder_state_h")
    decoder_state_input_c = Input(shape=(n_units,), name="decoder_state_c")
    decoder_state_inputs = [decoder_state_input_h, decoder_state_input_c]
    decoder_outputs, state_h, state_c = decoder_lstm(
        decoder_inputs, initial_state=decoder_state_inputs
    )
    decoder_outputs = decoder_dense(decoder_outputs)
    decoder_model = Model(
        [decoder_inputs] + decoder_state_inputs,
        [decoder_outputs, state_h, state_c],
        name="inference_decoder",
    )
    return training_model, encoder_model, decoder_model


def predict_sequence(
    inference_encoder: Model,
    inference_decoder: Model,
    source: np.ndarray,
    n_steps: int,
    cardinality: int,
) -> np.ndarray:
    """Autoregressively decode one target token at a time."""
    state_h, state_c = inference_encoder.predict(source, verbose=0)
    target_sequence = np.zeros((1, 1, cardinality), dtype=np.float32)
    target_sequence[0, 0, 0] = 1.0
    outputs: list[np.ndarray] = []

    for _ in range(n_steps):
        probabilities, state_h, state_c = inference_decoder.predict(
            [target_sequence, state_h, state_c], verbose=0
        )
        token = int(np.argmax(probabilities[0, 0]))
        one_hot = np.zeros((1, 1, cardinality), dtype=np.float32)
        one_hot[0, 0, token] = 1.0
        outputs.append(one_hot[0, 0])
        target_sequence = one_hot

    return np.asarray(outputs, dtype=np.float32)


def one_hot_decode(encoded_sequence: np.ndarray) -> list[int]:
    """Convert one-hot or probability vectors to readable integer tokens."""
    return [int(np.argmax(vector)) for vector in encoded_sequence]


def save_training_history(history: tf.keras.callbacks.History) -> None:
    """Save learning curves as evidence of convergence and generalization."""
    figure, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    axes[0].plot(history.history["loss"], label="Training")
    axes[0].plot(history.history["val_loss"], label="Validation")
    axes[0].set_title("Categorical Cross-Entropy Loss")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].legend()
    axes[0].grid(alpha=0.25)

    axes[1].plot(history.history["accuracy"], label="Training")
    axes[1].plot(history.history["val_accuracy"], label="Validation")
    axes[1].set_title("Token Accuracy")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Accuracy")
    axes[1].set_ylim(0, 1.02)
    axes[1].legend()
    axes[1].grid(alpha=0.25)
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / "02_training_history.png", dpi=180)
    plt.close(figure)


def save_prediction_examples(records: list[dict[str, object]]) -> None:
    """Save a readable table image of representative held-out predictions."""
    rows = [
        [
            str(record["source"]),
            str(record["target"]),
            str(record["prediction"]),
            "Correct" if record["exact_match"] else "Incorrect",
        ]
        for record in records[:10]
    ]
    figure, axis = plt.subplots(figsize=(12, 4.8))
    axis.axis("off")
    table = axis.table(
        cellText=rows,
        colLabels=["Source sequence", "Expected target", "Predicted target", "Result"],
        cellLoc="center",
        loc="center",
        colWidths=[0.38, 0.22, 0.22, 0.14],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 1.55)
    for column in range(4):
        table[(0, column)].set_facecolor("#D9EAF7")
        table[(0, column)].set_text_props(weight="bold")
    axis.set_title("Held-Out Sequence Predictions", fontsize=14, weight="bold", pad=18)
    figure.tight_layout()
    figure.savefig(OUTPUT_DIR / "03_prediction_examples.png", dpi=180, bbox_inches="tight")
    plt.close(figure)


def main() -> None:
    """Run the complete training, inference, evaluation, and evidence workflow."""
    start_time = time.perf_counter()
    configure_reproducibility()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    train_rng = np.random.default_rng(SEED)
    validation_rng = np.random.default_rng(SEED + 1)
    test_rng = np.random.default_rng(SEED + 2)

    x_train, decoder_train, y_train, _, _ = get_dataset(
        N_STEPS_IN, N_STEPS_OUT, N_FEATURES, TRAIN_SAMPLES, train_rng
    )
    x_validation, decoder_validation, y_validation, _, _ = get_dataset(
        N_STEPS_IN, N_STEPS_OUT, N_FEATURES, VALIDATION_SAMPLES, validation_rng
    )

    training_model, inference_encoder, inference_decoder = define_models(
        N_FEATURES, N_FEATURES, N_UNITS
    )
    training_model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )

    early_stopping = EarlyStopping(
        monitor="val_loss", patience=5, restore_best_weights=True, verbose=1
    )
    history = training_model.fit(
        [x_train, decoder_train],
        y_train,
        validation_data=([x_validation, decoder_validation], y_validation),
        epochs=MAX_EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=[early_stopping],
        verbose=2,
    )
    save_training_history(history)

    x_test, _, y_test, raw_sources, raw_targets = get_dataset(
        N_STEPS_IN, N_STEPS_OUT, N_FEATURES, TEST_SAMPLES, test_rng
    )
    records: list[dict[str, object]] = []
    correct = 0
    for index in range(TEST_SAMPLES):
        prediction_encoded = predict_sequence(
            inference_encoder,
            inference_decoder,
            x_test[index : index + 1],
            N_STEPS_OUT,
            N_FEATURES,
        )
        prediction = one_hot_decode(prediction_encoded)
        target = raw_targets[index].tolist()
        exact_match = prediction == target
        correct += int(exact_match)
        records.append(
            {
                "source": raw_sources[index].tolist(),
                "target": target,
                "prediction": prediction,
                "exact_match": exact_match,
            }
        )

    exact_match_accuracy = correct / TEST_SAMPLES
    elapsed_seconds = time.perf_counter() - start_time
    save_prediction_examples(records)

    summary = {
        "seed": SEED,
        "python_version": platform.python_version(),
        "tensorflow_version": tf.__version__,
        "keras_version": tf.keras.__version__,
        "numpy_version": np.__version__,
        "configuration": {
            "n_features": N_FEATURES,
            "input_steps": N_STEPS_IN,
            "output_steps": N_STEPS_OUT,
            "lstm_units": N_UNITS,
            "training_samples": TRAIN_SAMPLES,
            "validation_samples": VALIDATION_SAMPLES,
            "test_samples": TEST_SAMPLES,
            "batch_size": BATCH_SIZE,
            "maximum_epochs": MAX_EPOCHS,
            "epochs_completed": len(history.history["loss"]),
        },
        "training": {
            "final_loss": float(history.history["loss"][-1]),
            "final_accuracy": float(history.history["accuracy"][-1]),
            "final_validation_loss": float(history.history["val_loss"][-1]),
            "final_validation_accuracy": float(history.history["val_accuracy"][-1]),
        },
        "evaluation": {
            "correct_sequences": correct,
            "total_sequences": TEST_SAMPLES,
            "exact_match_accuracy": exact_match_accuracy,
        },
        "elapsed_seconds": elapsed_seconds,
    }
    (OUTPUT_DIR / "results.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    output_lines = [
        "CSC580 Final Portfolio Option 2 - Encoder-Decoder LSTM",
        "=" * 62,
        f"Python: {platform.python_version()}",
        f"TensorFlow: {tf.__version__}",
        f"Keras: {tf.keras.__version__}",
        f"NumPy: {np.__version__}",
        f"Seed: {SEED}",
        f"Training shape: source={x_train.shape}, decoder={decoder_train.shape}, target={y_train.shape}",
        f"Validation shape: source={x_validation.shape}, decoder={decoder_validation.shape}, target={y_validation.shape}",
        f"Epochs completed: {len(history.history['loss'])}",
        f"Final validation loss: {history.history['val_loss'][-1]:.6f}",
        f"Final validation token accuracy: {history.history['val_accuracy'][-1]:.4%}",
        f"Held-out exact-match accuracy: {correct}/{TEST_SAMPLES} ({exact_match_accuracy:.2%})",
        f"Elapsed seconds: {elapsed_seconds:.2f}",
        "",
        "Held-out predictions",
        "-" * 62,
    ]
    for record in records:
        output_lines.append(
            f"X={record['source']} y={record['target']} "
            f"yhat={record['prediction']} exact_match={record['exact_match']}"
        )
    output_text = "\n".join(output_lines) + "\n"
    (Path(__file__).resolve().parent / "CSC580_Option_2_runtime_predictions.txt").write_text(
        output_text, encoding="utf-8"
    )
    print(output_text)

    if exact_match_accuracy < 0.95:
        raise RuntimeError(
            f"Exact-match accuracy {exact_match_accuracy:.2%} is below the 95% QA threshold."
        )


if __name__ == "__main__":
    main()
