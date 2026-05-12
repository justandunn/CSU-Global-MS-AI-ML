"""
Hand-Made Shallow ANN in Python (NumPy)
--------------------------------------
CSC510 Module 3 Critical Thinking Assignment
Justan Dunn
Colorado State University Global
CSC510-1: Foundations of Artificial Intelligence
Professor Joseph Issa
02/01/2026

This script implements a basic 2-layer (1 hidden layer) artificial neural network
using NumPy. The network is trained using static backpropagation and gradient descent
to predict the next number in an arithmetic sequence.

Run:
    python ann_sequence_predictor.py
"""

from __future__ import annotations

import sys
import numpy as np


# ---------------------------
# Utility Functions
# ---------------------------

def set_seed(seed: int = 42) -> None:
    np.random.seed(seed)


def generate_arithmetic_sequences(
    n_samples: int,
    window: int,
    start_range: tuple[float, float] = (-50.0, 50.0),
    step_range: tuple[float, float] = (-10.0, 10.0),
) -> tuple[np.ndarray, np.ndarray]:
    """
    Generates training data for arithmetic sequences.
    X = first `window` values
    y = next value in the sequence
    """
    X = np.zeros((n_samples, window), dtype=np.float64)
    y = np.zeros((n_samples, 1), dtype=np.float64)

    for i in range(n_samples):
        a0 = np.random.uniform(*start_range)
        d = np.random.uniform(*step_range)
        seq = a0 + d * np.arange(window + 1)
        X[i] = seq[:window]
        y[i, 0] = seq[window]

    return X, y


def standardize(X: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = X.mean(axis=0, keepdims=True)
    std = X.std(axis=0, keepdims=True)
    std[std < 1e-8] = 1.0
    return (X - mean) / std, mean, std


def apply_standardization(X: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return (X - mean) / std


# ---------------------------
# Neural Network
# ---------------------------

class ShallowANN:
    """
    2-layer ANN:
    Input -> Hidden (tanh) -> Output (linear)
    """

    def __init__(self, n_inputs: int, n_hidden: int = 16, lr: float = 0.01):
        self.lr = lr

        # Xavier initialization
        self.W1 = np.random.randn(n_inputs, n_hidden) * np.sqrt(2 / n_inputs)
        self.b1 = np.zeros((1, n_hidden))

        self.W2 = np.random.randn(n_hidden, 1) * np.sqrt(2 / n_hidden)
        self.b2 = np.zeros((1, 1))

    @staticmethod
    def tanh(x: np.ndarray) -> np.ndarray:
        return np.tanh(x)

    @staticmethod
    def tanh_derivative(a: np.ndarray) -> np.ndarray:
        return 1.0 - a**2

    def forward(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        Z1 = X @ self.W1 + self.b1
        A1 = self.tanh(Z1)
        y_hat = A1 @ self.W2 + self.b2
        return A1, y_hat

    @staticmethod
    def mse(y_hat: np.ndarray, y: np.ndarray) -> float:
        return float(np.mean((y_hat - y) ** 2))

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 1500) -> None:
        m = X.shape[0]

        for epoch in range(1, epochs + 1):
            # Forward pass
            A1, y_hat = self.forward(X)

            # Loss
            loss = self.mse(y_hat, y)

            # Backpropagation
            dY = (2 / m) * (y_hat - y)
            dW2 = A1.T @ dY
            db2 = np.sum(dY, axis=0, keepdims=True)

            dA1 = dY @ self.W2.T
            dZ1 = dA1 * self.tanh_derivative(A1)
            dW1 = X.T @ dZ1
            db1 = np.sum(dZ1, axis=0, keepdims=True)

            # Gradient descent update
            self.W2 -= self.lr * dW2
            self.b2 -= self.lr * db2
            self.W1 -= self.lr * dW1
            self.b1 -= self.lr * db1

            if epoch == 1 or epoch % 200 == 0 or epoch == epochs:
                print(f"Epoch {epoch:4d}/{epochs} | MSE Loss: {loss:.6f}", flush=True)

    def predict(self, X: np.ndarray) -> np.ndarray:
        _, y_hat = self.forward(X)
        return y_hat


# ---------------------------
# User Input
# ---------------------------

def get_user_input(window: int) -> np.ndarray:
    print(f"\nEnter {window} numbers (comma or space separated):", end=" ", flush=True)
    raw = sys.stdin.readline().strip()

    if not raw:
        print("No input detected. Exiting.")
        sys.exit(1)

    raw = raw.replace(",", " ")
    values = raw.split()

    if len(values) != window:
        print(f"Expected {window} values. Exiting.")
        sys.exit(1)

    try:
        return np.array([float(v) for v in values]).reshape(1, window)
    except ValueError:
        print("Invalid numeric input. Exiting.")
        sys.exit(1)


# ---------------------------
# Main Program
# ---------------------------

def main() -> None:
    set_seed(42)

    print("\nHand-Made Shallow ANN (NumPy)")
    print("--------------------------------")

    window = 3
    epochs = 1500
    samples = 4000

    X, y = generate_arithmetic_sequences(samples, window)
    Xs, mean, std = standardize(X)

    ann = ShallowANN(n_inputs=window)
    print("\nTraining network...")
    ann.train(Xs, y, epochs=epochs)

    # Demo example
    idx = np.random.randint(0, samples)
    demo = X[idx].reshape(1, window)
    demo_std = apply_standardization(demo, mean, std)
    pred = ann.predict(demo_std)

    print("\nDemo Example")
    print("Input:", demo.flatten().tolist())
    print("Predicted next value:", round(float(pred[0, 0]), 4))

    # User prediction
    user_input = get_user_input(window)
    user_std = apply_standardization(user_input, mean, std)
    user_pred = ann.predict(user_std)

    print("\nYour Prediction")
    print("Input:", user_input.flatten().tolist())
    print("Predicted next value:", round(float(user_pred[0, 0]), 4))


if __name__ == "__main__":
    main()
