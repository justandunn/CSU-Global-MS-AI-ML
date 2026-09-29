"""Augment a text dataset for CSC525 Module 5 Critical Thinking Project.

The script is intentionally dependency-free so it can run in a standard Python
environment. It accepts a CSV, TSV, or TXT file; detects the text column when
one is not provided; and writes an augmented CSV plus a JSON run summary.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import random
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable


LOGGER = logging.getLogger("text_dataset_augmenter")

TEXT_COLUMN_CANDIDATES = (
    "instruction",
    "question",
    "query",
    "utterance",
    "message",
    "text",
    "prompt",
    "content",
    "body",
)

PLACEHOLDER_PATTERN = re.compile(
    r"(\{\{[^{}]+\}\}|https?://\S+|www\.\S+|[\w.+-]+@[\w-]+\.[\w.-]+)"
)

PHRASE_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    ("can you", "could you"),
    ("could you", "can you"),
    ("i need", "i would like"),
    ("i want", "i would like"),
    ("help me", "assist me"),
    ("tell me", "let me know"),
    ("find out", "check"),
    ("check on", "review"),
    ("order", "purchase"),
    ("purchase", "order"),
    ("shipping", "delivery"),
    ("shipment", "delivery"),
    ("refund", "reimbursement"),
    ("invoice", "bill"),
    ("account", "profile"),
    ("change", "update"),
    ("problem", "issue"),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create an augmented CSV from a text dataset."
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input CSV, TSV, or TXT file. Defaults to the first file in data/raw.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output augmented CSV. Defaults to data/augmented/<input>_augmented.csv.",
    )
    parser.add_argument(
        "--text-column",
        default=None,
        help="Text column to augment. If omitted, the script detects one.",
    )
    parser.add_argument(
        "--augmentations-per-row",
        type=int,
        default=2,
        help="Number of augmented variants to create for each source row.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=525,
        help="Random seed for deterministic augmentation.",
    )
    parser.add_argument(
        "--summary",
        type=Path,
        default=None,
        help="Optional JSON summary path. Defaults to outputs/augmentation_summary.json.",
    )
    parser.add_argument(
        "--no-originals",
        action="store_true",
        help="Do not include original rows in the augmented output.",
    )
    parser.add_argument(
        "--max-rows",
        type=int,
        default=None,
        help="Optional row limit for quick testing.",
    )
    return parser.parse_args()


def resolve_default_input(base_dir: Path) -> Path:
    search_dirs = (base_dir / "data" / "raw", base_dir)
    suffixes = (".csv", ".tsv", ".txt")
    for folder in search_dirs:
        if not folder.exists():
            continue
        for suffix in suffixes:
            matches = sorted(folder.glob(f"*{suffix}"))
            if matches:
                return matches[0]
    raise FileNotFoundError(
        "No input file was provided and no CSV, TSV, or TXT file was found in data/raw."
    )


def resolve_user_path(path: Path, base_dir: Path, for_output: bool = False) -> Path:
    if path.is_absolute():
        return path
    cwd_path = Path.cwd() / path
    if cwd_path.exists() or (for_output and cwd_path.parent.exists()):
        return cwd_path
    return base_dir / path


def read_dataset(input_path: Path, max_rows: int | None) -> tuple[list[dict[str, str]], list[str]]:
    if input_path.suffix.lower() in {".csv", ".tsv"}:
        delimiter = "\t" if input_path.suffix.lower() == ".tsv" else ","
        with input_path.open("r", encoding="utf-8-sig", newline="") as file_obj:
            reader = csv.DictReader(file_obj, delimiter=delimiter)
            if not reader.fieldnames:
                raise ValueError(f"{input_path} does not contain a header row.")
            rows = []
            for idx, row in enumerate(reader):
                if max_rows is not None and idx >= max_rows:
                    break
                rows.append({key: value or "" for key, value in row.items()})
            return rows, list(reader.fieldnames)

    if input_path.suffix.lower() == ".txt":
        rows = []
        with input_path.open("r", encoding="utf-8") as file_obj:
            for idx, line in enumerate(file_obj):
                if max_rows is not None and idx >= max_rows:
                    break
                text = line.strip()
                if text:
                    rows.append({"row_id": str(idx + 1), "text": text})
        return rows, ["row_id", "text"]

    raise ValueError("Input file must be a CSV, TSV, or TXT file.")


def detect_text_column(rows: list[dict[str, str]], fieldnames: list[str]) -> str:
    lower_lookup = {name.lower(): name for name in fieldnames}
    for candidate in TEXT_COLUMN_CANDIDATES:
        if candidate in lower_lookup:
            return lower_lookup[candidate]

    best_name = ""
    best_score = -1.0
    for name in fieldnames:
        if name.lower().endswith(("id", "url", "label", "category", "intent")):
            continue
        values = [row.get(name, "").strip() for row in rows if row.get(name, "").strip()]
        if not values:
            continue
        avg_len = sum(len(value) for value in values) / len(values)
        word_bonus = sum(1 for value in values if " " in value) / len(values)
        score = avg_len + (20 * word_bonus)
        if score > best_score:
            best_name = name
            best_score = score

    if not best_name:
        raise ValueError("Unable to detect a text column. Provide --text-column.")
    return best_name


def protect_placeholders(text: str) -> tuple[str, dict[str, str]]:
    replacements: dict[str, str] = {}

    def replace(match: re.Match[str]) -> str:
        token = f"__PLACEHOLDER_{len(replacements)}__"
        replacements[token] = match.group(0)
        return token

    return PLACEHOLDER_PATTERN.sub(replace, text), replacements


def restore_placeholders(text: str, replacements: dict[str, str]) -> str:
    restored = text
    for token, value in replacements.items():
        restored = restored.replace(token, value)
    return restored


def match_case(source: str, replacement: str) -> str:
    if source.isupper():
        return replacement.upper()
    if source[:1].isupper():
        return replacement[:1].upper() + replacement[1:]
    return replacement


def phrase_replacement(text: str, rng: random.Random) -> tuple[str, str]:
    protected_text, placeholders = protect_placeholders(text)
    candidates: list[tuple[re.Match[str], str]] = []

    for phrase, replacement in PHRASE_REPLACEMENTS:
        pattern = re.compile(rf"\b{re.escape(phrase)}\b", re.IGNORECASE)
        for match in pattern.finditer(protected_text):
            candidates.append((match, replacement))

    if not candidates:
        return customer_support_frame(text, rng)

    match, replacement = rng.choice(candidates)
    replacement_text = match_case(match.group(0), replacement)
    updated = (
        protected_text[: match.start()]
        + replacement_text
        + protected_text[match.end() :]
    )
    return (
        restore_placeholders(updated, placeholders),
        f"Replaced '{match.group(0)}' with '{replacement_text}'.",
    )


def polite_request_frame(text: str, rng: random.Random) -> tuple[str, str]:
    clean = text.strip()
    frames = (
        "Please help me with this request: {text}",
        "Could you please assist with this request: {text}",
        "I need support with the following request: {text}",
    )
    return rng.choice(frames).format(text=clean), "Added a polite service-request frame."


def customer_support_frame(text: str, rng: random.Random) -> tuple[str, str]:
    clean = text.strip()
    frames = (
        "I am contacting customer support because {text}",
        "In the customer support chat, I need help because {text}",
        "For this support case, {text}",
    )
    framed = rng.choice(frames).format(text=clean)
    return framed, "Added customer-support context around the original request."


def next_step_frame(text: str, rng: random.Random) -> tuple[str, str]:
    clean = text.strip()
    frames = (
        "I would like the next step for this support issue: {text}",
        "Could you help route this customer service request: {text}",
        "Please review this customer support request: {text}",
    )
    return rng.choice(frames).format(text=clean), "Added a next-step support framing phrase."


Augmenter = Callable[[str, random.Random], tuple[str, str]]


AUGMENTERS: tuple[tuple[str, Augmenter], ...] = (
    ("phrase_replacement", phrase_replacement),
    ("polite_request_frame", polite_request_frame),
    ("customer_support_frame", customer_support_frame),
    ("next_step_frame", next_step_frame),
)


def source_row_id(row: dict[str, str], index: int) -> str:
    for candidate in ("sample_id", "row_id", "id", "uuid"):
        value = row.get(candidate, "").strip()
        if value:
            return value
    return f"source_{index:05d}"


def augment_rows(
    rows: list[dict[str, str]],
    fieldnames: list[str],
    text_column: str,
    augmentations_per_row: int,
    include_originals: bool,
    rng: random.Random,
) -> tuple[list[dict[str, str]], Counter[str]]:
    if augmentations_per_row < 1:
        raise ValueError("--augmentations-per-row must be at least 1.")

    augmented_rows: list[dict[str, str]] = []
    method_counts: Counter[str] = Counter()

    for index, row in enumerate(rows, start=1):
        original_text = row.get(text_column, "").strip()
        if not original_text:
            continue
        row_id = source_row_id(row, index)

        if include_originals:
            original = dict(row)
            original.update(
                {
                    "augmentation_record_id": f"{row_id}__original",
                    "source_row_id": row_id,
                    "is_augmented": "false",
                    "augmentation_type": "original",
                    "augmentation_note": "Original unmodified source row.",
                    "original_text": original_text,
                }
            )
            augmented_rows.append(original)
            method_counts["original"] += 1

        used_texts = {original_text}
        for aug_index in range(augmentations_per_row):
            method_name, augmenter = AUGMENTERS[(index + aug_index) % len(AUGMENTERS)]
            new_text, note = augmenter(original_text, rng)

            attempts = 0
            while new_text in used_texts and attempts < len(AUGMENTERS):
                method_name, augmenter = AUGMENTERS[(index + aug_index + attempts + 1) % len(AUGMENTERS)]
                new_text, note = augmenter(original_text, rng)
                attempts += 1

            if new_text in used_texts:
                new_text, note = polite_request_frame(original_text, rng)
                method_name = "polite_request_frame"

            used_texts.add(new_text)
            augmented = dict(row)
            augmented[text_column] = new_text
            augmented.update(
                {
                    "augmentation_record_id": f"{row_id}__aug{aug_index + 1:02d}",
                    "source_row_id": row_id,
                    "is_augmented": "true",
                    "augmentation_type": method_name,
                    "augmentation_note": note,
                    "original_text": original_text,
                }
            )
            augmented_rows.append(augmented)
            method_counts[method_name] += 1

    return augmented_rows, method_counts


def write_csv(output_path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    metadata_fields = [
        "augmentation_record_id",
        "source_row_id",
        "is_augmented",
        "augmentation_type",
        "augmentation_note",
        "original_text",
    ]
    output_fields = [name for name in fieldnames if name not in metadata_fields] + metadata_fields
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as file_obj:
        writer = csv.DictWriter(file_obj, fieldnames=output_fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_summary(
    summary_path: Path,
    input_path: Path,
    output_path: Path,
    text_column: str,
    source_count: int,
    output_count: int,
    method_counts: Counter[str],
    seed: int,
) -> None:
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "input_path": str(input_path),
        "output_path": str(output_path),
        "text_column": text_column,
        "source_rows_read": source_count,
        "output_rows_written": output_count,
        "augmented_rows_created": output_count - method_counts.get("original", 0),
        "augmentation_method_counts": dict(sorted(method_counts.items())),
        "random_seed": seed,
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stdout,
    )


def main() -> int:
    configure_logging()
    args = parse_args()

    base_dir = Path(__file__).resolve().parent
    input_path = args.input or resolve_default_input(base_dir)
    input_path = resolve_user_path(input_path, base_dir)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    output_path = args.output or (
        base_dir / "data" / "augmented" / f"{input_path.stem}_augmented.csv"
    )
    output_path = resolve_user_path(output_path, base_dir, for_output=True)
    summary_path = args.summary or (base_dir / "outputs" / "augmentation_summary.json")
    summary_path = resolve_user_path(summary_path, base_dir, for_output=True)

    rows, fieldnames = read_dataset(input_path, args.max_rows)
    if not rows:
        raise ValueError("No rows were read from the input dataset.")

    text_column = args.text_column or detect_text_column(rows, fieldnames)
    if text_column not in fieldnames:
        raise ValueError(f"Text column '{text_column}' was not found in the dataset.")

    rng = random.Random(args.seed)
    output_rows, method_counts = augment_rows(
        rows=rows,
        fieldnames=fieldnames,
        text_column=text_column,
        augmentations_per_row=args.augmentations_per_row,
        include_originals=not args.no_originals,
        rng=rng,
    )

    write_csv(output_path, output_rows, fieldnames)
    write_summary(
        summary_path=summary_path,
        input_path=input_path,
        output_path=output_path,
        text_column=text_column,
        source_count=len(rows),
        output_count=len(output_rows),
        method_counts=method_counts,
        seed=args.seed,
    )

    LOGGER.info("Input rows read: %s", len(rows))
    LOGGER.info("Text column augmented: %s", text_column)
    LOGGER.info("Output rows written: %s", len(output_rows))
    LOGGER.info("Augmentation methods: %s", dict(sorted(method_counts.items())))
    LOGGER.info("Augmented dataset: %s", output_path)
    LOGGER.info("Run summary: %s", summary_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
