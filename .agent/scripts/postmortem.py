"""Append project postmortems, lessons, and decisions for the Agentic OS bridge."""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


EMPTY_VALUES = {"", "none", "n/a", "na"}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def is_present(value: str) -> bool:
    return value.strip().lower() not in EMPTY_VALUES


def postmortem_entry(args: argparse.Namespace, date_text: str) -> str:
    return f"""
## {date_text} - {args.task}

### What Changed

{args.what_changed}

### Why It Changed

{args.why}

### Files Touched

{args.files_touched}

### Tests Or Validation Run

{args.validation}

### Issues Encountered

{args.issues}

### Reusable Lessons

{args.lessons}

### Decisions Made

{args.decisions}

### References Captured

{args.references}
"""


def append(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(text)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--what-changed", required=True)
    parser.add_argument("--why", required=True)
    parser.add_argument("--files-touched", required=True)
    parser.add_argument("--validation", required=True)
    parser.add_argument("--issues", required=True)
    parser.add_argument("--lessons", required=True)
    parser.add_argument("--decisions", required=True)
    parser.add_argument("--references", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    date_text = datetime.now().astimezone().date().isoformat()
    memory = root / ".agent" / "memory"
    append(memory / "project_log.md", postmortem_entry(args, date_text))
    if is_present(args.lessons):
        append(memory / "lessons_learned.md", f"\n## {date_text} - {args.task}\n\n{args.lessons}\n")
    if is_present(args.decisions):
        append(memory / "decision_log.md", f"\n## {date_text} - {args.task}\n\n{args.decisions}\n")
    print(f"Appended postmortem: {memory / 'project_log.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
