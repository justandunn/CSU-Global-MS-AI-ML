"""Train a dependency-free retrieval baseline for the Module 5 PM.

This script implements the Module 4 Portfolio Milestone plan: a controlled
enterprise FAQ/SOP corpus is represented with TF-IDF features and customer
messages are routed by cosine similarity to the closest approved knowledge-base
entry.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


TOKEN_PATTERN = re.compile(r"[a-zA-Z][a-zA-Z0-9_']+")


@dataclass(frozen=True)
class KnowledgeEntry:
    record_id: str
    source_row_id: str
    route_label: str
    source_category: str
    text: str
    sample_question: str
    approved_answer: str


@dataclass
class RetrievalPrediction:
    row: KnowledgeEntry
    predicted_route: str
    matched_record_id: str
    matched_question: str
    matched_answer: str
    similarity: float
    correct: bool
    top_matches: list[tuple[str, str, float]]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Train and evaluate a TF-IDF retrieval chatbot baseline."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/custom_enterprise_faq_sop_corpus.csv"),
        help="FAQ/SOP CSV corpus path.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Directory where training outputs will be written.",
    )
    parser.add_argument("--text-column", default="combined_text")
    parser.add_argument("--label-column", default="route_label")
    parser.add_argument("--group-column", default="source_row_id")
    parser.add_argument("--seed", type=int, default=525)
    parser.add_argument("--test-group-ratio", type=float, default=0.40)
    parser.add_argument("--ngram-min", type=int, default=1)
    parser.add_argument("--ngram-max", type=int, default=1)
    parser.add_argument("--max-features", type=int, default=2500)
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.20,
        help="Draft threshold below which a chatbot should ask for clarification.",
    )
    return parser.parse_args()


def resolve_path(path: Path, base_dir: Path, for_output: bool = False) -> Path:
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists() or (for_output and cwd_path.parent.exists()):
        return cwd_path
    return base_dir / path


def tokenize(text: str) -> list[str]:
    return [match.group(0).lower() for match in TOKEN_PATTERN.finditer(text)]


def make_ngrams(tokens: list[str], ngram_min: int, ngram_max: int) -> list[str]:
    terms: list[str] = []
    for n in range(ngram_min, ngram_max + 1):
        if n <= 0 or len(tokens) < n:
            continue
        for index in range(len(tokens) - n + 1):
            terms.append(" ".join(tokens[index : index + n]))
    return terms


def load_entries(
    input_path: Path,
    text_column: str,
    label_column: str,
    group_column: str,
) -> list[KnowledgeEntry]:
    entries: list[KnowledgeEntry] = []
    with input_path.open("r", encoding="utf-8-sig", newline="") as file_obj:
        reader = csv.DictReader(file_obj)
        if not reader.fieldnames:
            raise ValueError("Input CSV does not contain headers.")
        missing = [
            column
            for column in (text_column, label_column, group_column)
            if column not in reader.fieldnames
        ]
        if missing:
            raise ValueError(f"Missing required columns: {missing}")
        for index, row in enumerate(reader, start=1):
            text = (row.get(text_column) or "").strip()
            route_label = (row.get(label_column) or "").strip()
            if not text or not route_label:
                continue
            record_id = (row.get("record_id") or f"record_{index:04d}").strip()
            entries.append(
                KnowledgeEntry(
                    record_id=record_id,
                    source_row_id=(row.get(group_column) or record_id).strip(),
                    route_label=route_label,
                    source_category=(row.get("source_category") or "").strip(),
                    text=text,
                    sample_question=(row.get("sample_question") or text).strip(),
                    approved_answer=(row.get("approved_answer") or "").strip(),
                )
            )
    if not entries:
        raise ValueError("No usable entries were loaded.")
    return entries


def stratified_group_split(
    entries: list[KnowledgeEntry],
    test_group_ratio: float,
    seed: int,
) -> tuple[list[KnowledgeEntry], list[KnowledgeEntry]]:
    if not 0 < test_group_ratio < 1:
        raise ValueError("--test-group-ratio must be between 0 and 1.")

    groups_by_route: dict[str, dict[str, list[KnowledgeEntry]]] = defaultdict(lambda: defaultdict(list))
    for entry in entries:
        groups_by_route[entry.route_label][entry.source_row_id].append(entry)

    rng = random.Random(seed)
    train_entries: list[KnowledgeEntry] = []
    test_entries: list[KnowledgeEntry] = []

    for route in sorted(groups_by_route):
        group_ids = sorted(groups_by_route[route])
        rng.shuffle(group_ids)
        test_count = max(1, round(len(group_ids) * test_group_ratio))
        if test_count >= len(group_ids):
            test_count = len(group_ids) - 1
        test_group_ids = set(group_ids[:test_count])
        for group_id in group_ids:
            destination = test_entries if group_id in test_group_ids else train_entries
            destination.extend(groups_by_route[route][group_id])

    return train_entries, test_entries


def feature_terms(entry: KnowledgeEntry, ngram_min: int, ngram_max: int) -> list[str]:
    return make_ngrams(tokenize(entry.text), ngram_min, ngram_max)


def build_vocabulary(
    entries: Iterable[KnowledgeEntry],
    ngram_min: int,
    ngram_max: int,
    max_features: int,
) -> list[str]:
    term_frequency: Counter[str] = Counter()
    document_frequency: Counter[str] = Counter()
    for entry in entries:
        terms = feature_terms(entry, ngram_min, ngram_max)
        term_frequency.update(terms)
        document_frequency.update(set(terms))

    ranked = sorted(
        term_frequency,
        key=lambda term: (-document_frequency[term], -term_frequency[term], term),
    )
    return ranked[:max_features] if max_features > 0 else ranked


class TfidfRetriever:
    def __init__(self, vocabulary: list[str], ngram_min: int, ngram_max: int) -> None:
        self.vocabulary = vocabulary
        self.vocabulary_set = set(vocabulary)
        self.ngram_min = ngram_min
        self.ngram_max = ngram_max
        self.idf: dict[str, float] = {}
        self.train_entries: list[KnowledgeEntry] = []
        self.train_vectors: list[dict[str, float]] = []

    def fit(self, entries: list[KnowledgeEntry]) -> None:
        self.train_entries = entries
        documents = [
            [
                term
                for term in feature_terms(entry, self.ngram_min, self.ngram_max)
                if term in self.vocabulary_set
            ]
            for entry in entries
        ]
        document_frequency: Counter[str] = Counter()
        for document in documents:
            document_frequency.update(set(document))
        total_documents = len(documents)
        self.idf = {
            term: math.log((total_documents + 1) / (document_frequency[term] + 1)) + 1
            for term in self.vocabulary
        }
        self.train_vectors = [self.vectorize_terms(document) for document in documents]

    def vectorize_terms(self, terms: list[str]) -> dict[str, float]:
        counts = Counter(term for term in terms if term in self.vocabulary_set)
        vector = {
            term: count * self.idf.get(term, 0.0)
            for term, count in counts.items()
            if term in self.idf
        }
        norm = math.sqrt(sum(value * value for value in vector.values()))
        if not norm:
            return vector
        return {term: value / norm for term, value in vector.items()}

    def vectorize_text(self, text: str) -> dict[str, float]:
        terms = make_ngrams(tokenize(text), self.ngram_min, self.ngram_max)
        return self.vectorize_terms(terms)

    @staticmethod
    def cosine_similarity(left: dict[str, float], right: dict[str, float]) -> float:
        if len(left) > len(right):
            left, right = right, left
        return sum(value * right.get(term, 0.0) for term, value in left.items())

    def predict(self, entry: KnowledgeEntry) -> RetrievalPrediction:
        query_vector = self.vectorize_text(entry.text)
        scored: list[tuple[KnowledgeEntry, float]] = []
        for train_entry, train_vector in zip(self.train_entries, self.train_vectors):
            scored.append((train_entry, self.cosine_similarity(query_vector, train_vector)))
        scored.sort(key=lambda item: item[1], reverse=True)
        best_entry, best_score = scored[0]
        top_matches = [
            (match.route_label, match.record_id, score)
            for match, score in scored[:3]
        ]
        return RetrievalPrediction(
            row=entry,
            predicted_route=best_entry.route_label,
            matched_record_id=best_entry.record_id,
            matched_question=best_entry.sample_question,
            matched_answer=best_entry.approved_answer,
            similarity=best_score,
            correct=best_entry.route_label == entry.route_label,
            top_matches=top_matches,
        )


def precision_recall_f1(tp: int, fp: int, fn: int) -> tuple[float, float, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if precision + recall
        else 0.0
    )
    return precision, recall, f1


def evaluate(predictions: list[RetrievalPrediction]) -> tuple[dict[str, object], list[dict[str, object]], list[dict[str, object]]]:
    labels = sorted(
        {prediction.row.route_label for prediction in predictions}
        | {prediction.predicted_route for prediction in predictions}
    )
    correct_count = sum(1 for prediction in predictions if prediction.correct)
    accuracy = correct_count / len(predictions) if predictions else 0.0
    similarities = [prediction.similarity for prediction in predictions]

    report_rows: list[dict[str, object]] = []
    for label in labels:
        tp = sum(1 for item in predictions if item.row.route_label == label and item.predicted_route == label)
        fp = sum(1 for item in predictions if item.row.route_label != label and item.predicted_route == label)
        fn = sum(1 for item in predictions if item.row.route_label == label and item.predicted_route != label)
        support = sum(1 for item in predictions if item.row.route_label == label)
        precision, recall, f1 = precision_recall_f1(tp, fp, fn)
        report_rows.append(
            {
                "route_label": label,
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
                "support": support,
            }
        )

    confusion_rows: list[dict[str, object]] = []
    for actual in labels:
        for predicted in labels:
            count = sum(
                1
                for item in predictions
                if item.row.route_label == actual and item.predicted_route == predicted
            )
            if count:
                confusion_rows.append(
                    {
                        "actual_route": actual,
                        "predicted_route": predicted,
                        "count": count,
                    }
                )

    metrics = {
        "test_rows": len(predictions),
        "correct_rows": correct_count,
        "accuracy": round(accuracy, 4),
        "macro_precision": round(sum(float(row["precision"]) for row in report_rows) / len(report_rows), 4),
        "macro_recall": round(sum(float(row["recall"]) for row in report_rows) / len(report_rows), 4),
        "macro_f1": round(sum(float(row["f1"]) for row in report_rows) / len(report_rows), 4),
        "mean_similarity": round(sum(similarities) / len(similarities), 4) if similarities else 0.0,
        "min_similarity": round(min(similarities), 4) if similarities else 0.0,
        "max_similarity": round(max(similarities), 4) if similarities else 0.0,
    }
    return metrics, report_rows, confusion_rows


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_prediction_rows(path: Path, predictions: list[RetrievalPrediction]) -> None:
    rows = []
    for prediction in predictions:
        rows.append(
            {
                "record_id": prediction.row.record_id,
                "sample_question": prediction.row.sample_question,
                "actual_route": prediction.row.route_label,
                "predicted_route": prediction.predicted_route,
                "correct": prediction.correct,
                "similarity": round(prediction.similarity, 4),
                "matched_record_id": prediction.matched_record_id,
                "matched_question": prediction.matched_question,
                "top_3_matches": "; ".join(
                    f"{route}:{record}:{score:.4f}"
                    for route, record, score in prediction.top_matches
                ),
            }
        )
    write_csv(
        path,
        rows,
        [
            "record_id",
            "sample_question",
            "actual_route",
            "predicted_route",
            "correct",
            "similarity",
            "matched_record_id",
            "matched_question",
            "top_3_matches",
        ],
    )


def write_summary(
    path: Path,
    metrics: dict[str, object],
    train_entries: list[KnowledgeEntry],
    test_entries: list[KnowledgeEntry],
    vocabulary_size: int,
    args: argparse.Namespace,
) -> None:
    lines = [
        "Module 5 Portfolio Milestone Retrieval Training Summary",
        f"Generated UTC: {datetime.now(timezone.utc).isoformat()}",
        "",
        "Model: TF-IDF cosine-similarity retrieval baseline",
        f"Training text field: {args.text_column}",
        f"Train rows: {len(train_entries)}",
        f"Test rows: {len(test_entries)}",
        f"Distinct routes: {len(set(entry.route_label for entry in train_entries + test_entries))}",
        f"Vocabulary size: {vocabulary_size}",
        "",
        "Hyperparameters:",
        f"- Random seed: {args.seed}",
        f"- Test source-group ratio: {args.test_group_ratio}",
        f"- N-gram range: ({args.ngram_min}, {args.ngram_max})",
        f"- Max features: {args.max_features}",
        f"- Draft similarity threshold: {args.similarity_threshold}",
        "",
        "Evaluation:",
        f"- Accuracy: {metrics['accuracy']}",
        f"- Macro precision: {metrics['macro_precision']}",
        f"- Macro recall: {metrics['macro_recall']}",
        f"- Macro F1: {metrics['macro_f1']}",
        f"- Mean similarity: {metrics['mean_similarity']}",
        f"- Correct rows: {metrics['correct_rows']} of {metrics['test_rows']}",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    base_dir = Path(__file__).resolve().parent
    input_path = resolve_path(args.input, base_dir)
    output_dir = resolve_path(args.output_dir, base_dir, for_output=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    entries = load_entries(
        input_path=input_path,
        text_column=args.text_column,
        label_column=args.label_column,
        group_column=args.group_column,
    )
    train_entries, test_entries = stratified_group_split(
        entries=entries,
        test_group_ratio=args.test_group_ratio,
        seed=args.seed,
    )
    vocabulary = build_vocabulary(
        entries=train_entries,
        ngram_min=args.ngram_min,
        ngram_max=args.ngram_max,
        max_features=args.max_features,
    )
    retriever = TfidfRetriever(
        vocabulary=vocabulary,
        ngram_min=args.ngram_min,
        ngram_max=args.ngram_max,
    )
    retriever.fit(train_entries)
    predictions = [retriever.predict(entry) for entry in test_entries]
    metrics, report_rows, confusion_rows = evaluate(predictions)
    below_threshold = sum(
        1 for prediction in predictions if prediction.similarity < args.similarity_threshold
    )

    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_path": str(input_path),
        "model_type": "TF-IDF cosine-similarity retrieval baseline",
        "feature_representation": f"lowercase {args.ngram_min}-{args.ngram_max} n-gram TF-IDF vectors",
        "training_text_column": args.text_column,
        "train_rows": len(train_entries),
        "test_rows": len(test_entries),
        "distinct_routes": len({entry.route_label for entry in entries}),
        "source_groups": len({entry.source_row_id for entry in entries}),
        "vocabulary_size": len(vocabulary),
        "hyperparameters": {
            "random_seed": args.seed,
            "test_group_ratio": args.test_group_ratio,
            "ngram_range": [args.ngram_min, args.ngram_max],
            "max_features": args.max_features,
            "similarity_threshold": args.similarity_threshold,
        },
        "metrics": metrics,
        "fallback_analysis": {
            "below_similarity_threshold": below_threshold,
            "threshold": args.similarity_threshold,
        },
    }

    (output_dir / "training_metrics.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    write_csv(
        output_dir / "route_report.csv",
        report_rows,
        ["route_label", "precision", "recall", "f1", "support"],
    )
    write_csv(
        output_dir / "confusion_matrix.csv",
        confusion_rows,
        ["actual_route", "predicted_route", "count"],
    )
    write_prediction_rows(output_dir / "retrieval_predictions.csv", predictions)
    write_summary(
        output_dir / "training_summary.txt",
        metrics,
        train_entries,
        test_entries,
        len(vocabulary),
        args,
    )

    print(f"Loaded rows: {len(entries)}")
    print(f"Train rows: {len(train_entries)}")
    print(f"Test rows: {len(test_entries)}")
    print(f"Vocabulary size: {len(vocabulary)}")
    print(f"Accuracy: {metrics['accuracy']}")
    print(f"Macro F1: {metrics['macro_f1']}")
    print(f"Mean similarity: {metrics['mean_similarity']}")
    print(f"Below threshold: {below_threshold}")
    print(f"Outputs: {output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
