"""CSC580 Module 1 Critical Thinking Assignment, Option 2.

Train a linear-regression model on synthetic observations generated from a
user-defined linear equation containing four through eight variables. Compare
the model prediction with the equation's exact output for a user-supplied test
observation.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Sequence

import numpy as np
from numpy.typing import NDArray
from sklearn.linear_model import LinearRegression

MIN_VARIABLES = 4
MAX_VARIABLES = 8
DEFAULT_SAMPLE_COUNT = 100
DEFAULT_VALUE_LIMIT = 1_000
DEFAULT_SEED = 580


@dataclass(frozen=True)
class ModelResult:
    """Values needed to explain and validate a fitted regression model."""

    learned_coefficients: NDArray[np.float64]
    learned_intercept: float
    predicted_value: float
    actual_value: float
    absolute_error: float
    training_r_squared: float


def validate_variable_count(variable_count: int) -> None:
    """Raise ValueError unless the assignment's four-to-eight limit is met."""

    if not MIN_VARIABLES <= variable_count <= MAX_VARIABLES:
        raise ValueError(
            f"Variable count must be between {MIN_VARIABLES} and {MAX_VARIABLES}."
        )


def validate_vector(values: Sequence[float], expected_count: int, label: str) -> None:
    """Validate the length and finiteness of a numeric input vector."""

    if len(values) != expected_count:
        raise ValueError(f"{label} must contain exactly {expected_count} values.")
    if not np.isfinite(np.asarray(values, dtype=float)).all():
        raise ValueError(f"{label} must contain only finite numbers.")


def calculate_actual_value(
    coefficients: Sequence[float], inputs: Sequence[float]
) -> float:
    """Calculate the exact output of a zero-intercept linear equation."""

    validate_variable_count(len(coefficients))
    validate_vector(inputs, len(coefficients), "Test inputs")
    return float(np.dot(np.asarray(coefficients, dtype=float), inputs))


def generate_training_data(
    coefficients: Sequence[float],
    sample_count: int = DEFAULT_SAMPLE_COUNT,
    value_limit: int = DEFAULT_VALUE_LIMIT,
    seed: int = DEFAULT_SEED,
) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    """Generate deterministic training inputs and exact equation outputs."""

    validate_variable_count(len(coefficients))
    validate_vector(coefficients, len(coefficients), "Coefficients")
    if sample_count <= len(coefficients):
        raise ValueError("Sample count must exceed the number of variables.")
    if value_limit < 1:
        raise ValueError("Value limit must be at least 1.")

    random_generator = np.random.default_rng(seed)
    features = random_generator.integers(
        0,
        value_limit + 1,
        size=(sample_count, len(coefficients)),
    ).astype(np.float64)
    targets = features @ np.asarray(coefficients, dtype=np.float64)
    return features, targets


def train_and_evaluate(
    coefficients: Sequence[float],
    test_inputs: Sequence[float],
    sample_count: int = DEFAULT_SAMPLE_COUNT,
    value_limit: int = DEFAULT_VALUE_LIMIT,
    seed: int = DEFAULT_SEED,
) -> ModelResult:
    """Fit the model and compare its prediction with the exact equation."""

    validate_vector(test_inputs, len(coefficients), "Test inputs")
    features, targets = generate_training_data(
        coefficients=coefficients,
        sample_count=sample_count,
        value_limit=value_limit,
        seed=seed,
    )
    model = LinearRegression()
    model.fit(features, targets)

    test_array = np.asarray(test_inputs, dtype=np.float64).reshape(1, -1)
    predicted_value = float(model.predict(test_array)[0])
    actual_value = calculate_actual_value(coefficients, test_inputs)

    return ModelResult(
        learned_coefficients=np.asarray(model.coef_, dtype=np.float64),
        learned_intercept=float(model.intercept_),
        predicted_value=predicted_value,
        actual_value=actual_value,
        absolute_error=abs(predicted_value - actual_value),
        training_r_squared=float(model.score(features, targets)),
    )


def parse_number_list(raw_value: str, label: str) -> list[float]:
    """Convert a comma-separated string into floating-point values."""

    try:
        values = [float(item.strip()) for item in raw_value.split(",")]
    except ValueError as exc:
        raise ValueError(f"{label} must be a comma-separated list of numbers.") from exc
    if not values or any(not np.isfinite(value) for value in values):
        raise ValueError(f"{label} must contain only finite numbers.")
    return values


def prompt_for_values(label: str, expected_count: int | None = None) -> list[float]:
    """Prompt until a valid numeric vector with the expected length is entered."""

    while True:
        try:
            values = parse_number_list(input(f"{label}: "), label)
            if expected_count is not None:
                validate_vector(values, expected_count, label)
            return values
        except ValueError as exc:
            print(f"Input error: {exc}")


def build_argument_parser() -> argparse.ArgumentParser:
    """Build command-line arguments for interactive and reproducible runs."""

    parser = argparse.ArgumentParser(
        description="Fit a machine-learning model to a configurable linear equation."
    )
    parser.add_argument(
        "--coefficients",
        help="Comma-separated coefficients for four through eight variables.",
    )
    parser.add_argument(
        "--inputs",
        help="Comma-separated test inputs matching the coefficient count.",
    )
    parser.add_argument("--samples", type=int, default=DEFAULT_SAMPLE_COUNT)
    parser.add_argument("--value-limit", type=int, default=DEFAULT_VALUE_LIMIT)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    return parser


def main() -> int:
    """Run the assignment program and print an auditable result summary."""

    arguments = build_argument_parser().parse_args()
    try:
        coefficients = (
            parse_number_list(arguments.coefficients, "Coefficients")
            if arguments.coefficients
            else prompt_for_values(
                "Enter 4-8 coefficients separated by commas"
            )
        )
        validate_variable_count(len(coefficients))

        test_inputs = (
            parse_number_list(arguments.inputs, "Test inputs")
            if arguments.inputs
            else prompt_for_values(
                f"Enter {len(coefficients)} test inputs separated by commas",
                expected_count=len(coefficients),
            )
        )
        validate_vector(test_inputs, len(coefficients), "Test inputs")

        result = train_and_evaluate(
            coefficients=coefficients,
            test_inputs=test_inputs,
            sample_count=arguments.samples,
            value_limit=arguments.value_limit,
            seed=arguments.seed,
        )
    except ValueError as exc:
        print(f"Error: {exc}")
        return 2

    print("\nCSC580 Module 1 - Linear Equation Learning Results")
    print(f"Random seed: {arguments.seed}")
    print(f"Training samples: {arguments.samples}")
    print(f"Supplied coefficients: {np.asarray(coefficients)}")
    print(f"Learned coefficients: {np.round(result.learned_coefficients, 8)}")
    print(f"Learned intercept: {result.learned_intercept:.8f}")
    print(f"Training R-squared: {result.training_r_squared:.12f}")
    print(f"Predicted value: {result.predicted_value:.8f}")
    print(f"Actual value: {result.actual_value:.8f}")
    print(f"Absolute error: {result.absolute_error:.12f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

