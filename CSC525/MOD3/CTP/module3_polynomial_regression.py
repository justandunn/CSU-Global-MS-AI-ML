"""Module 3 Critical Thinking Project: Polynomial regression.

Option 2 predicts salary from years of experience using a degree-2 polynomial
regression model. The script validates the local CSV, trains the model,
prints evaluation results, and saves a fitted-curve figure.

This version uses NumPy's least-squares polynomial fit, which is sufficient for
the assignment's polynomial regression requirement and keeps the script compact.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "data" / "years_experience_salary.csv"
OUTPUT_DIR = PROJECT_DIR / "outputs"
PLOT_PATH = OUTPUT_DIR / "polynomial_regression_fit.png"
REQUIRED_COLUMNS = ("YearsExperience", "Salary")
RANDOM_STATE = 42
POLYNOMIAL_DEGREE = 2


def load_salary_data(path: Path) -> tuple[np.ndarray, np.ndarray]:
    """Load and validate the salary CSV.

    Returns:
        Two one-dimensional NumPy arrays: years of experience and salary.
    """
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    years: list[float] = []
    salaries: list[float] = []
    with path.open(newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("Dataset has no header row.")

        missing_columns = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")

        for row_number, row in enumerate(reader, start=2):
            try:
                year_value = float(row["YearsExperience"])
                salary_value = float(row["Salary"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Non-numeric data found on CSV row {row_number}: {row}") from exc

            if year_value < 0 or salary_value <= 0:
                raise ValueError(f"Unexpected negative/zero value on CSV row {row_number}: {row}")

            years.append(year_value)
            salaries.append(salary_value)

    if len(years) < 5:
        raise ValueError("Dataset must contain at least five rows for a meaningful train/test split.")

    return np.array(years, dtype=float), np.array(salaries, dtype=float)


def split_train_test(row_count: int, test_size: float = 0.20) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(RANDOM_STATE)
    indices = rng.permutation(row_count)
    test_count = max(1, round(row_count * test_size))
    test_indices = np.sort(indices[:test_count])
    train_indices = np.sort(indices[test_count:])
    return train_indices, test_indices


def predict_salary(coefficients: np.ndarray, years: np.ndarray) -> np.ndarray:
    return np.polyval(coefficients, years)


def calculate_metrics(actual: np.ndarray, predicted: np.ndarray) -> tuple[float, float, float]:
    residuals = actual - predicted
    rmse = float(np.sqrt(np.mean(residuals**2)))
    mae = float(np.mean(np.abs(residuals)))
    ss_res = float(np.sum(residuals**2))
    ss_tot = float(np.sum((actual - np.mean(actual)) ** 2))
    r_squared = 1.0 - (ss_res / ss_tot)
    return r_squared, rmse, mae


def save_regression_plot(
    years: np.ndarray,
    salaries: np.ndarray,
    coefficients: np.ndarray,
    output_path: Path,
) -> None:
    width, height = 1200, 760
    margin_left, margin_right = 110, 70
    margin_top, margin_bottom = 90, 110
    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()

    x_min, x_max = float(years.min()), float(years.max())
    y_min, y_max = float(salaries.min()), float(salaries.max())
    y_padding = (y_max - y_min) * 0.12
    y_min -= y_padding
    y_max += y_padding

    def map_x(value: float) -> float:
        return margin_left + ((value - x_min) / (x_max - x_min)) * plot_width

    def map_y(value: float) -> float:
        return margin_top + (1.0 - ((value - y_min) / (y_max - y_min))) * plot_height

    # Grid, axes, and tick labels.
    for tick in np.linspace(x_min, x_max, 6):
        x_coord = map_x(float(tick))
        draw.line([(x_coord, margin_top), (x_coord, height - margin_bottom)], fill="#E5E7EB")
        draw.text((x_coord - 12, height - margin_bottom + 16), f"{tick:.1f}", fill="#111827", font=font)

    for tick in np.linspace(y_min, y_max, 6):
        y_coord = map_y(float(tick))
        draw.line([(margin_left, y_coord), (width - margin_right, y_coord)], fill="#E5E7EB")
        draw.text((20, y_coord - 7), f"${tick:,.0f}", fill="#111827", font=font)

    draw.rectangle(
        [(margin_left, margin_top), (width - margin_right, height - margin_bottom)],
        outline="#111827",
        width=2,
    )

    # Observed values.
    for x_value, y_value in zip(years, salaries):
        x_coord = map_x(float(x_value))
        y_coord = map_y(float(y_value))
        draw.ellipse(
            [(x_coord - 5, y_coord - 5), (x_coord + 5, y_coord + 5)],
            fill="#1F77B4",
            outline="#0F3D63",
        )

    # Fitted polynomial curve.
    x_curve = np.linspace(x_min, x_max, 240)
    y_curve = predict_salary(coefficients, x_curve)
    points = [(map_x(float(x_value)), map_y(float(y_value))) for x_value, y_value in zip(x_curve, y_curve)]
    draw.line(points, fill="#D62728", width=4)

    draw.text((margin_left, 30), "Polynomial Regression: Salary by Years of Experience", fill="#111827", font=font)
    draw.text((width // 2 - 70, height - 50), "Years of Experience", fill="#111827", font=font)
    draw.text((margin_left, height - 28), "Blue points = observed salaries; red curve = degree-2 polynomial fit.", fill="#374151", font=font)
    draw.text((20, 56), "Salary (USD)", fill="#111827", font=font)
    draw.text((width - 330, 32), "Model: y = ax^2 + bx + c", fill="#374151", font=font)

    image.save(output_path)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    years, salaries = load_salary_data(DATA_PATH)
    train_indices, test_indices = split_train_test(len(years))

    x_train = years[train_indices]
    y_train = salaries[train_indices]
    x_test = years[test_indices]
    y_test = salaries[test_indices]

    coefficients = np.polyfit(x_train, y_train, deg=POLYNOMIAL_DEGREE)

    y_pred = predict_salary(coefficients, x_test)
    r2, rmse, mae = calculate_metrics(y_test, y_pred)

    save_regression_plot(years, salaries, coefficients, PLOT_PATH)

    candidate_years = np.array([2.5, 5.0, 7.5, 10.0], dtype=float)
    candidate_predictions = predict_salary(coefficients, candidate_years)

    print("CSC525 Module 3 Critical Thinking Project")
    print("Option 2: Simple Polynomial Regression in Python")
    print("=" * 58)
    print(f"Dataset: {DATA_PATH.name}")
    print(f"Rows loaded: {len(years)}")
    print(f"Model: degree-{POLYNOMIAL_DEGREE} NumPy polynomial least-squares regression")
    print(f"Equation: salary = ({coefficients[0]:,.4f} * years^2) + ({coefficients[1]:,.4f} * years) + ({coefficients[2]:,.4f})")
    print(f"Train/Test split: {len(x_train)} training rows / {len(x_test)} test rows")
    print()
    print("Model evaluation on held-out test data")
    print(f"R-squared: {r2:.4f}")
    print(f"RMSE: ${rmse:,.2f}")
    print(f"MAE: ${mae:,.2f}")
    print()
    print("Sample salary predictions")
    for years_value, salary in zip(candidate_years, candidate_predictions):
        print(f"{years_value:>4.1f} years of experience -> predicted salary ${salary:,.2f}")
    print()
    print(f"Saved regression figure: {PLOT_PATH}")


if __name__ == "__main__":
    main()
