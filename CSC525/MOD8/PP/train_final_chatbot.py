"""Train, calibrate, and evaluate the final CSC525 customer-service chatbot."""

from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from chatbot_model import FeatureConfig, TfidfCentroidModel


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "model"
OUTPUT_DIR = BASE_DIR / "outputs"
TRAINING_PATH = DATA_DIR / "training_corpus.csv"
CALIBRATION_PATH = DATA_DIR / "calibration_messages.csv"
TEST_PATH = DATA_DIR / "test_messages.csv"
MODEL_PATH = MODEL_DIR / "chatbot_model.json"
OOD = "__out_of_domain__"
FALLBACK = "clarification_or_human_escalation"


CANDIDATE_CONFIGS = [
    FeatureConfig("word_unigrams", 1, 1, 0, 0, 2500),
    FeatureConfig("word_unigrams_bigrams", 1, 2, 0, 0, 5000),
    FeatureConfig("character_3_5", 0, 0, 3, 5, 8000),
    FeatureConfig("hybrid_word_char", 1, 2, 3, 5, 9000),
]
SCORE_THRESHOLDS = [round(value / 1000, 3) for value in range(20, 401, 20)]
MARGIN_THRESHOLDS = [0.0, 0.01, 0.02, 0.03, 0.04, 0.05, 0.07, 0.10, 0.13]


@dataclass(frozen=True)
class EvaluationRow:
    message_id: str
    message: str
    expected_route: str
    case_type: str
    predicted_route: str
    displayed_route: str
    accepted: bool
    score: float
    margin: float
    correct_decision: bool
    top_3_routes: str


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as file_obj:
        return list(csv.DictReader(file_obj))


def load_training_data() -> tuple[
    list[tuple[str, str]], dict[str, str], dict[str, str]
]:
    rows = read_csv(TRAINING_PATH)
    required = {
        "route_label",
        "source_category",
        "sample_question",
        "approved_answer",
    }
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"Training corpus must contain columns: {sorted(required)}")

    examples: list[tuple[str, str]] = []
    route_responses: dict[str, str] = {}
    route_display_names: dict[str, str] = {}
    for row in rows:
        route = row["route_label"].strip()
        question = row["sample_question"].strip()
        if not route or not question:
            continue
        examples.append((question, route))
        route_responses.setdefault(route, row["approved_answer"].strip())
        route_display_names.setdefault(route, row["source_category"].strip())
    return examples, route_responses, route_display_names


def augment_examples(examples: list[tuple[str, str]]) -> list[tuple[str, str]]:
    """Add route-neutral conversational framing without adding label keywords."""
    augmented: list[tuple[str, str]] = []
    for text, route in examples:
        sentence = text.strip()
        augmented.extend(
            [
                (sentence, route),
                (f"Please help me with this: {sentence}", route),
                (f"I am frustrated and need assistance. {sentence}", route),
            ]
        )
    return augmented


def load_evaluation_rows(path: Path) -> list[dict[str, str]]:
    rows = read_csv(path)
    required = {"message_id", "message", "expected_route", "case_type"}
    if not rows or not required.issubset(rows[0]):
        raise ValueError(f"Evaluation file must contain columns: {sorted(required)}")
    return rows


def evaluate(
    model: TfidfCentroidModel,
    rows: list[dict[str, str]],
    minimum_score: float,
    minimum_margin: float,
) -> tuple[dict[str, float | int], list[EvaluationRow]]:
    model.minimum_score = minimum_score
    model.minimum_margin = minimum_margin
    results: list[EvaluationRow] = []

    for row in rows:
        prediction = model.predict(row["message"])
        expected = row["expected_route"]
        is_ood = expected == OOD
        correct_decision = (
            (is_ood and not prediction.accepted)
            or (
                not is_ood
                and prediction.accepted
                and prediction.predicted_route == expected
            )
        )
        results.append(
            EvaluationRow(
                message_id=row["message_id"],
                message=row["message"],
                expected_route=expected,
                case_type=row["case_type"],
                predicted_route=prediction.predicted_route,
                displayed_route=(
                    prediction.predicted_route if prediction.accepted else FALLBACK
                ),
                accepted=prediction.accepted,
                score=round(prediction.score, 4),
                margin=round(prediction.margin, 4),
                correct_decision=correct_decision,
                top_3_routes="; ".join(
                    f"{route}:{score:.4f}" for route, score in prediction.ranking
                ),
            )
        )

    in_domain = [item for item in results if item.expected_route != OOD]
    out_of_domain = [item for item in results if item.expected_route == OOD]
    in_domain_accepted = [item for item in in_domain if item.accepted]
    correct_routes = [
        item for item in in_domain if item.predicted_route == item.expected_route
    ]
    correct_accepted = [
        item
        for item in in_domain_accepted
        if item.predicted_route == item.expected_route
    ]
    rejected_ood = [item for item in out_of_domain if not item.accepted]
    correct_decisions = [item for item in results if item.correct_decision]

    def ratio(numerator: int, denominator: int) -> float:
        return round(numerator / denominator, 4) if denominator else 0.0

    metrics: dict[str, float | int] = {
        "total_rows": len(results),
        "in_domain_rows": len(in_domain),
        "out_of_domain_rows": len(out_of_domain),
        "raw_route_accuracy": ratio(len(correct_routes), len(in_domain)),
        "in_domain_coverage": ratio(len(in_domain_accepted), len(in_domain)),
        "accepted_route_accuracy": ratio(
            len(correct_accepted), len(in_domain_accepted)
        ),
        "in_domain_decision_accuracy": ratio(
            len(correct_accepted), len(in_domain)
        ),
        "out_of_domain_rejection_rate": ratio(
            len(rejected_ood), len(out_of_domain)
        ),
        "overall_decision_accuracy": ratio(
            len(correct_decisions), len(results)
        ),
        "accepted_in_domain": len(in_domain_accepted),
        "correct_accepted_in_domain": len(correct_accepted),
        "rejected_out_of_domain": len(rejected_ood),
        "false_accept_out_of_domain": len(out_of_domain) - len(rejected_ood),
        "false_reject_in_domain": len(in_domain) - len(in_domain_accepted),
    }
    return metrics, results


def select_model(
    training_examples: list[tuple[str, str]],
    route_responses: dict[str, str],
    route_display_names: dict[str, str],
    calibration_rows: list[dict[str, str]],
) -> tuple[TfidfCentroidModel, list[dict[str, Any]], dict[str, Any]]:
    sweep_rows: list[dict[str, Any]] = []
    fitted_models: dict[str, TfidfCentroidModel] = {}

    for config in CANDIDATE_CONFIGS:
        model = TfidfCentroidModel(config)
        model.fit(training_examples, route_responses, route_display_names)
        fitted_models[config.name] = model
        for score_threshold in SCORE_THRESHOLDS:
            for margin_threshold in MARGIN_THRESHOLDS:
                metrics, _ = evaluate(
                    model,
                    calibration_rows,
                    score_threshold,
                    margin_threshold,
                )
                sweep_rows.append(
                    {
                        "config": config.name,
                        "vocabulary_size": len(model.vocabulary),
                        "minimum_score": score_threshold,
                        "minimum_margin": margin_threshold,
                        **metrics,
                    }
                )

    eligible = [
        row
        for row in sweep_rows
        if float(row["in_domain_coverage"]) >= 0.70
        and float(row["out_of_domain_rejection_rate"]) >= 0.60
    ]
    candidates = eligible or sweep_rows
    selected = max(
        candidates,
        key=lambda row: (
            float(row["overall_decision_accuracy"]),
            min(
                float(row["in_domain_decision_accuracy"]),
                float(row["out_of_domain_rejection_rate"]),
            ),
            float(row["accepted_route_accuracy"]),
            float(row["in_domain_coverage"]),
            -float(row["minimum_score"]),
            -float(row["minimum_margin"]),
        ),
    )
    selected_model = fitted_models[str(selected["config"])]
    selected_model.minimum_score = float(selected["minimum_score"])
    selected_model.minimum_margin = float(selected["minimum_margin"])
    return selected_model, sweep_rows, selected


def write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_predictions(path: Path, rows: list[EvaluationRow]) -> None:
    fieldnames = list(asdict(rows[0]).keys()) if rows else []
    write_csv(path, [asdict(row) for row in rows], fieldnames)


def write_confusion_matrix(path: Path, rows: list[EvaluationRow]) -> None:
    counts: Counter[tuple[str, str]] = Counter()
    for row in rows:
        expected = FALLBACK if row.expected_route == OOD else row.expected_route
        counts[(expected, row.displayed_route)] += 1
    output = [
        {"expected_route": expected, "decision_route": decision, "count": count}
        for (expected, decision), count in sorted(counts.items())
    ]
    write_csv(path, output, ["expected_route", "decision_route", "count"])


def main() -> int:
    required_files = [TRAINING_PATH, CALIBRATION_PATH, TEST_PATH]
    missing = [str(path) for path in required_files if not path.exists()]
    if missing:
        raise FileNotFoundError(
            "Missing dataset files. Run build_final_datasets.py first: " + ", ".join(missing)
        )

    raw_examples, route_responses, route_display_names = load_training_data()
    training_examples = augment_examples(raw_examples)
    calibration_rows = load_evaluation_rows(CALIBRATION_PATH)
    test_rows = load_evaluation_rows(TEST_PATH)

    model, sweep_rows, selected = select_model(
        training_examples,
        route_responses,
        route_display_names,
        calibration_rows,
    )
    calibration_metrics, calibration_predictions = evaluate(
        model,
        calibration_rows,
        model.minimum_score,
        model.minimum_margin,
    )
    test_metrics, test_predictions = evaluate(
        model,
        test_rows,
        model.minimum_score,
        model.minimum_margin,
    )

    generated_at = datetime.now(timezone.utc).isoformat()
    model.metadata = {
        "generated_at_utc": generated_at,
        "raw_training_rows": len(raw_examples),
        "augmented_training_rows": len(training_examples),
        "distinct_routes": len(route_responses),
        "vocabulary_size": len(model.vocabulary),
        "calibration_rows": len(calibration_rows),
        "test_rows": len(test_rows),
        "calibration_metrics": calibration_metrics,
        "test_metrics": test_metrics,
        "evaluation_note": (
            "Calibration and test inputs contain raw customer messages only; "
            "route labels and curated keyword banks are not appended to inputs."
        ),
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_PATH.write_text(
        json.dumps(model.to_dict(), indent=2, sort_keys=True),
        encoding="utf-8",
    )
    metrics_payload = {
        "generated_at_utc": generated_at,
        "model_type": "supervised TF-IDF route-centroid classifier",
        "selected_config": model.config.to_dict(),
        "minimum_score": model.minimum_score,
        "minimum_margin": model.minimum_margin,
        "raw_training_rows": len(raw_examples),
        "augmented_training_rows": len(training_examples),
        "distinct_routes": len(route_responses),
        "vocabulary_size": len(model.vocabulary),
        "calibration_metrics": calibration_metrics,
        "test_metrics": test_metrics,
        "selection_record": selected,
    }
    (OUTPUT_DIR / "final_metrics.json").write_text(
        json.dumps(metrics_payload, indent=2),
        encoding="utf-8",
    )

    sweep_fields = list(sweep_rows[0].keys())
    write_csv(OUTPUT_DIR / "hyperparameter_sweep.csv", sweep_rows, sweep_fields)
    write_predictions(OUTPUT_DIR / "calibration_predictions.csv", calibration_predictions)
    write_predictions(OUTPUT_DIR / "test_predictions.csv", test_predictions)
    write_confusion_matrix(OUTPUT_DIR / "confusion_matrix.csv", test_predictions)

    print(f"Selected configuration: {model.config.name}")
    print(f"Vocabulary size: {len(model.vocabulary)}")
    print(f"Minimum score: {model.minimum_score:.3f}")
    print(f"Minimum margin: {model.minimum_margin:.3f}")
    print(
        "Calibration overall decision accuracy: "
        f"{float(calibration_metrics['overall_decision_accuracy']):.4f}"
    )
    print(
        "Final test overall decision accuracy: "
        f"{float(test_metrics['overall_decision_accuracy']):.4f}"
    )
    print(
        "Final test raw route accuracy: "
        f"{float(test_metrics['raw_route_accuracy']):.4f}"
    )
    print(
        "Final test out-of-domain rejection rate: "
        f"{float(test_metrics['out_of_domain_rejection_rate']):.4f}"
    )
    print(f"Model: {MODEL_PATH.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
