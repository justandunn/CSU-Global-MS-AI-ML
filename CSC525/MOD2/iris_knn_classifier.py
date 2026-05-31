#!/usr/bin/env python3
"""
Option #1: KNN Classifier with Iris Data
Justan E Dunn
Colorado State University Global
CSC525 - Principles of Machine Learning
Professor Dong Nguyen
05/24/2026

This program builds a simple K-Nearest Neighbors classifier from the provided
Iris CSV file and predicts the iris class from four numeric measurements:

1. Sepal length
2. Sepal width
3. Petal length
4. Petal width

Example:
    python iris_knn_classifier.py 5.1 3.5 1.4 0.2

Optional:
    python iris_knn_classifier.py 5.1 3.5 1.4 0.2 --k 5 --details
"""

from __future__ import annotations

import argparse
import csv
import math
from collections import Counter, defaultdict
from pathlib import Path
from typing import Sequence, TypeAlias


FeatureVector: TypeAlias = list[float]
TrainingRecord: TypeAlias = tuple[FeatureVector, str]
NeighborRecord: TypeAlias = tuple[float, str, FeatureVector]

FEATURE_COLUMNS: tuple[str, str, str, str] = (
    "SepalLength",
    "SepalWidth",
    "PetalLength",
    "PetalWidth",
)
LABEL_COLUMN = "Name"


def load_iris_data(csv_path: Path) -> list[TrainingRecord]:
    """
    Load iris data from a CSV file.

    Returns:
        A list of tuples in the form:
        ([sepal_length, sepal_width, petal_length, petal_width], label)
    """
    data: list[TrainingRecord] = []
    required_columns = list(FEATURE_COLUMNS) + [LABEL_COLUMN]

    with csv_path.open(mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)

        # csv.DictReader.fieldnames can be None before a header row is read.
        # Storing it after this check prevents BasedPyright/Pylance from warning.
        fieldnames = reader.fieldnames
        if fieldnames is None:
            raise ValueError("CSV file does not contain a header row.")

        missing_columns = [
            column for column in required_columns
            if column not in fieldnames
        ]
        if missing_columns:
            raise ValueError(
                "CSV file is missing required columns: "
                + ", ".join(missing_columns)
            )

        for row in reader:
            try:
                features: FeatureVector = []
                for column in FEATURE_COLUMNS:
                    raw_value = row.get(column)
                    if raw_value is None:
                        raise ValueError(f"Missing value for column {column}.")
                    features.append(float(raw_value))

                raw_label = row.get(LABEL_COLUMN)
                if raw_label is None:
                    raise ValueError(f"Missing value for column {LABEL_COLUMN}.")

                label = raw_label.strip()
                data.append((features, label))
            except ValueError as error:
                raise ValueError(f"Invalid data row: {row}") from error

    if not data:
        raise ValueError("The CSV file did not contain any usable data rows.")

    return data


def euclidean_distance(point_a: Sequence[float], point_b: Sequence[float]) -> float:
    """
    Calculate Euclidean distance between two points.
    """
    squared_differences = [
        (value_a - value_b) ** 2
        for value_a, value_b in zip(point_a, point_b)
    ]
    return math.sqrt(sum(squared_differences))


def predict_knn(
    training_data: Sequence[TrainingRecord],
    query_point: Sequence[float],
    k: int = 5,
) -> tuple[str, list[NeighborRecord], Counter[str]]:
    """
    Predict the class label for a query point using K-Nearest Neighbors.

    Tie-breaking:
    1. Highest vote count wins.
    2. If tied, the class with the lowest average distance wins.
    3. If still tied, alphabetical order is used for consistency.
    """
    if k <= 0:
        raise ValueError("k must be a positive integer.")

    if k > len(training_data):
        raise ValueError("k cannot be larger than the number of training records.")

    distances: list[NeighborRecord] = []

    for features, label in training_data:
        distance = euclidean_distance(query_point, features)
        distances.append((distance, label, features))

    distances.sort(key=lambda record: record[0])
    nearest_neighbors = distances[:k]

    vote_counts: Counter[str] = Counter(label for _, label, _ in nearest_neighbors)

    distances_by_label: defaultdict[str, list[float]] = defaultdict(list)
    for distance, label, _ in nearest_neighbors:
        distances_by_label[label].append(distance)

    ranked_labels = sorted(
        vote_counts.keys(),
        key=lambda label: (
            -vote_counts[label],
            sum(distances_by_label[label]) / len(distances_by_label[label]),
            label,
        ),
    )

    predicted_label = ranked_labels[0]
    return predicted_label, nearest_neighbors, vote_counts


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Predict iris type using a manually implemented KNN classifier."
    )

    parser.add_argument("sepal_length", nargs="?", type=float, help="Sepal length in cm")
    parser.add_argument("sepal_width", nargs="?", type=float, help="Sepal width in cm")
    parser.add_argument("petal_length", nargs="?", type=float, help="Petal length in cm")
    parser.add_argument("petal_width", nargs="?", type=float, help="Petal width in cm")

    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of nearest neighbors to use. Default is 5.",
    )

    parser.add_argument(
        "--csv",
        default="data_iris.csv",
        help="Path to the Iris CSV file. Default is data_iris.csv.",
    )

    parser.add_argument(
        "--details",
        action="store_true",
        help="Show nearest neighbors and vote counts.",
    )

    return parser.parse_args()


def prompt_for_missing_values(args: argparse.Namespace) -> list[float]:
    """
    If the user did not provide all four measurements as command-line arguments,
    prompt for them interactively.
    """
    raw_values: list[float | None] = [
        args.sepal_length,
        args.sepal_width,
        args.petal_length,
        args.petal_width,
    ]

    prompts = [
        "Enter sepal length in cm: ",
        "Enter sepal width in cm: ",
        "Enter petal length in cm: ",
        "Enter petal width in cm: ",
    ]

    final_values: list[float] = []

    for index, value in enumerate(raw_values):
        while value is None:
            try:
                value = float(input(prompts[index]))
            except ValueError:
                print("Please enter a valid floating point number.")

        final_values.append(value)

    return final_values


def resolve_csv_path(csv_argument: str) -> Path:
    """
    Locate the CSV file. First check the path provided by the user. Then check
    the folder where this Python script is located.
    """
    provided_path = Path(csv_argument)

    if provided_path.exists():
        return provided_path

    script_folder_path = Path(__file__).resolve().parent / csv_argument
    if script_folder_path.exists():
        return script_folder_path

    raise FileNotFoundError(
        f"Could not find CSV file: {csv_argument}. "
        "Place data_iris.csv in the same folder as this script or pass --csv."
    )


def main() -> None:
    args = parse_arguments()
    query_point = prompt_for_missing_values(args)
    csv_path = resolve_csv_path(str(args.csv))

    training_data = load_iris_data(csv_path)
    predicted_label, nearest_neighbors, vote_counts = predict_knn(
        training_data,
        query_point,
        k=int(args.k),
    )

    print("\nKNN Iris Classification Result")
    print("------------------------------")
    print(f"Input measurements: {query_point}")
    print(f"k value: {args.k}")
    print(f"Predicted iris type: {predicted_label}")

    if bool(args.details):
        print("\nVote counts:")
        for label, count in vote_counts.most_common():
            print(f"  {label}: {count}")

        print("\nNearest neighbors:")
        for rank, (distance, label, features) in enumerate(nearest_neighbors, start=1):
            print(
                f"  {rank}. Distance={distance:.4f}, "
                f"Label={label}, Features={features}"
            )


if __name__ == "__main__":
    main()
