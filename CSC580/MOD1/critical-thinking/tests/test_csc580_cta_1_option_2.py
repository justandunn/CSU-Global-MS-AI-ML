"""Automated tests for CSC580 Module 1 Critical Thinking Option 2."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SOURCE_DIRECTORY = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(SOURCE_DIRECTORY))

from csc580_cta_1_option_2 import (  # noqa: E402
    calculate_actual_value,
    generate_training_data,
    train_and_evaluate,
    validate_variable_count,
)


class LinearEquationLearnerTests(unittest.TestCase):
    """Verify calculation, validation, reproducibility, and model accuracy."""

    def test_actual_value_for_four_variables(self) -> None:
        self.assertEqual(calculate_actual_value([1, 2, 3, 4], [10, 20, 30, 40]), 300)

    def test_variable_count_rejects_out_of_range_values(self) -> None:
        for invalid_count in (3, 9):
            with self.subTest(invalid_count=invalid_count):
                with self.assertRaises(ValueError):
                    validate_variable_count(invalid_count)

    def test_training_generation_is_reproducible(self) -> None:
        first_features, first_targets = generate_training_data([1, 2, 3, 4], seed=580)
        second_features, second_targets = generate_training_data([1, 2, 3, 4], seed=580)
        self.assertTrue((first_features == second_features).all())
        self.assertTrue((first_targets == second_targets).all())

    def test_model_recovers_equation(self) -> None:
        result = train_and_evaluate(
            coefficients=[1, 2, 3, 4],
            test_inputs=[10, 20, 30, 40],
            sample_count=100,
            seed=580,
        )
        self.assertAlmostEqual(result.predicted_value, result.actual_value, places=7)
        self.assertAlmostEqual(result.training_r_squared, 1.0, places=12)
        self.assertLess(result.absolute_error, 1e-7)


if __name__ == "__main__":
    unittest.main()

