import numpy as np, textwrap, os, math, random, pathlib, json, pandas as pd
from pathlib import Path, PurePosixPath
code = r'''"""
Hand-Made Shallow ANN in Python (NumPy)
--------------------------------------
CSC510 Module 3 Critical Thinking Assignment

This script implements a basic 2-layer (1 hidden layer) neural network using NumPy,
trained via static backpropagation + gradient descent. The network learns to predict
the next number in an arithmetic sequence given a fixed-length window of prior values.

Requirements covered:
- Input layer accepts a matrix X and passes it on
- Hidden layer + activation (tanh)
- Output layer (linear)
- Weight matrices and bias vectors between layers
- Matrix multiplication, activation, output prediction
- Error + MSE loss
- Backprop gradient descent updates
- Trains >= 1,000 iterations (epochs)
- Accepts simple user input and prints the predicted next value

Run:
  python ann_sequence_predictor.py

Notes:
- This is intentionally simple and self-contained (no external ML libraries).
"""

from __future__ import annotations
import sys
import numpy as np


def set_seed(seed: int = 42) -> None:
    np.random.seed(seed)


def generate_arithmetic_sequences(
    n_samples: int,
    window: int,
    start_range: tuple[float, float] = (-50.0, 50.0),
    step_range: tuple[float, float] = (-10.0, 10.0),
) -> tuple[np.ndarray, np.ndarray]:
    """
    Create training pairs (X, y) where each example is:
      X = [a0, a1, ..., a_{window-1}]
      y = a_window
    for randomly generated arithmetic sequences.
    """
    X = np.zeros((n_samples, window), dtype=np.float64)
    y = np.zeros((n_samples, 1), dtype=np.float64)

    for i in range(n_samples):
        a0 = np.random.uniform(*start_range)
        d = np.random.uniform(*step_range)
        seq = a0 + d * np.arange(window + 1, dtype=np.float64)
        X[i, :] = seq[:window]
        y[i, 0] = seq[window]
    return X, y


def standardize_fit(X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return (mean, std) for standardization, with std floor to avoid divide-by-zero."""
    mean = X.mean(axis=0, keepdims=True)
    std = X.std(axis=0, keepdims=True)
    std = np.where(std < 1e-8, 1.0, std)
    return mean, std


def standardize_apply(X: np.ndarray, mean: np.ndarray, std: np.ndarray) -> np.ndarray:
    return (X - mean) / std


class ShallowANN:
    """
    2-layer ANN: input -> hidden (tanh) -> output (linear)
    """

    def __init__(self, n_in: int, n_hidden: int = 16, lr: float = 0.01) -> None:
        self.n_in = n_in
        self.n_hidden = n_hidden
        self.lr = lr

        # Xavier-like initialization for tanh
        limit1 = np.sqrt(6.0 / (n_in + n_hidden))
        self.W1 = np.random.uniform(-limit1, limit1, size=(n_in, n_hidden))
        self.b1 = np.zeros((1, n_hidden), dtype=np.float64)

        limit2 = np.sqrt(6.0 / (n_hidden + 1))
        self.W2 = np.random.uniform(-limit2, limit2, size=(n_hidden, 1))
        self.b2 = np.zeros((1, 1), dtype=np.float64)

    @staticmethod
    def tanh(x: np.ndarray) -> np.ndarray:
        return np.tanh(x)

    @staticmethod
    def tanh_derivative(tanh_x: np.ndarray) -> np.ndarray:
        # derivative of tanh(z) is 1 - tanh(z)^2
        return 1.0 - tanh_x ** 2

    def forward(self, X: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Feedforward:
          Z1 = XW1 + b1
          A1 = tanh(Z1)
          Z2 = A1W2 + b2
          yhat = Z2 (linear output)
        Returns (A1, yhat, tanh(A1) already applied)
        """
        Z1 = X @ self.W1 + self.b1
        A1 = self.tanh(Z1)
        yhat = A1 @ self.W2 + self.b2
        return A1, yhat, Z1

    @staticmethod
    def mse(yhat: np.ndarray, y: np.ndarray) -> float:
        return float(np.mean((yhat - y) ** 2))

    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 1500, verbose_every: int = 100) -> list[float]:
        """
        Train using full-batch gradient descent for simplicity.
        """
        losses: list[float] = []
        m = X.shape[0]

        for epoch in range(1, epochs + 1):
            # Forward
            A1, yhat, _Z1 = self.forward(X)

            # Loss
            loss = self.mse(yhat, y)
            losses.append(loss)

            # Backprop
            # dL/dyhat = 2*(yhat - y)/m
            dY = (2.0 / m) * (yhat - y)                    # (m, 1)

            # Output layer grads
            dW2 = A1.T @ dY                                 # (hidden, 1)
            db2 = np.sum(dY, axis=0, keepdims=True)         # (1, 1)

            # Hidden layer grads
            dA1 = dY @ self.W2.T                            # (m, hidden)
            dZ1 = dA1 * self.tanh_derivative(A1)            # (m, hidden)
            dW1 = X.T @ dZ1                                 # (in, hidden)
            db1 = np.sum(dZ1, axis=0, keepdims=True)        # (1, hidden)

            # Update
            self.W2 -= self.lr * dW2
            self.b2 -= self.lr * db2
            self.W1 -= self.lr * dW1
            self.b1 -= self.lr * db1

            if verbose_every and (epoch == 1 or epoch % verbose_every == 0 or epoch == epochs):
                print(f"Epoch {epoch:>4}/{epochs}  MSE Loss: {loss:.6f}")

        return losses

    def predict(self, X: np.ndarray) -> np.ndarray:
        _, yhat, _ = self.forward(X)
        return yhat


def parse_user_series(expected_len: int) -> np.ndarray:
    """
    Prompt for comma- or space-separated numbers of length expected_len.
    Returns shape (1, expected_len)
    """
    while True:
        raw = input(f"\nEnter {expected_len} numbers (comma or space separated), e.g. 1, 2, 3: ").strip()
        if not raw:
            print("Please enter a non-empty list of numbers.")
            continue

        # Normalize separators
        raw = raw.replace(",", " ")
        parts = [p for p in raw.split() if p]

        if len(parts) != expected_len:
            print(f"Expected {expected_len} numbers, but got {len(parts)}. Try again.")
            continue

        try:
            vals = np.array([float(p) for p in parts], dtype=np.float64).reshape(1, expected_len)
            return vals
        except ValueError:
            print("One or more entries were not valid numbers. Try again.")


def main() -> None:
    set_seed(42)

    print("\nHand-Made Shallow ANN (NumPy) — Next Number in a Series")
    print("--------------------------------------------------------")
    print("This program trains a simple 2-layer neural network with backpropagation")
    print("to predict the next number in an arithmetic sequence.\n")

    # Hyperparameters (kept simple)
    window = 3
    hidden = 16
    lr = 0.01
    epochs = 1500  # >= 1000 as required
    n_train = 4000

    # Generate training data
    X_train, y_train = generate_arithmetic_sequences(n_samples=n_train, window=window)

    # Standardize inputs (helps training stability)
    mean, std = standardize_fit(X_train)
    Xs = standardize_apply(X_train, mean, std)

    # Build + train network
    ann = ShallowANN(n_in=window, n_hidden=hidden, lr=lr)
    print("Training network...")
    ann.train(Xs, y_train, epochs=epochs, verbose_every=200)

    # Demonstrate on a random sample
    idx = np.random.randint(0, n_train)
    demo_x = X_train[idx:idx+1]
    demo_y = y_train[idx:idx+1]
    demo_xs = standardize_apply(demo_x, mean, std)
    pred = ann.predict(demo_xs)

    print("\nDemo Example:")
    print(f"  Input series: {demo_x.flatten().tolist()}")
    print(f"  True next:    {float(demo_y[0,0]):.4f}")
    print(f"  Predicted:    {float(pred[0,0]):.4f}")

    # User input prediction
    print("\nNow it's your turn.")
    user_x = parse_user_series(expected_len=window)
    user_xs = standardize_apply(user_x, mean, std)
    user_pred = ann.predict(user_xs)

    print("\nPrediction Result:")
    print(f"  Your input:   {user_x.flatten().tolist()}")
    print(f"  Predicted next value: {float(user_pred[0,0]):.4f}")

    print("\n(End of program.)")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(0)
'''