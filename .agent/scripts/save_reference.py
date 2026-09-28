"""Capture a raw project reference for the Agentic OS bridge."""

from __future__ import annotations

import argparse
import os
import re
from datetime import datetime
from pathlib import Path


PROJECT = "csu-global-ms-ai-ml-academic"
SOURCE_TYPES = ('docs', 'github', 'blog', 'paper', 'forum', 'vendor', 'other')
CONFIDENCE_LEVELS = ('high', 'medium', 'low')


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned[:80] or "reference"


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def ensure_unique_path(directory: Path, filename: str) -> Path:
    candidate = directory / filename
    if not candidate.exists():
        return candidate
    stem = candidate.stem
    suffix = candidate.suffix
    counter = 2
    while True:
        next_candidate = directory / f"{stem}-{counter}{suffix}"
        if not next_candidate.exists():
            return next_candidate
        counter += 1


def vault_reference_destination(root: Path, project: str) -> tuple[Path, Path] | None:
    wiki = root / "_wiki"
    candidates: list[tuple[Path, Path]] = []
    if wiki.exists() and wiki.is_dir():
        candidates.extend(
            [
                (wiki, wiki / "10_Sources" / "Raw" / "Project References" / project),
                (wiki, wiki / "raw_references" / project),
                (wiki, wiki / "00_LLM_Wiki" / "raw_references" / project),
            ]
        )

    env_vault = os.environ.get("AGENT_OS_VAULT_PATH")
    if env_vault:
        vault = Path(env_vault).expanduser()
        candidates.append((vault, vault / "10_Sources" / "Raw" / "Project References" / project))

    for vault_root, candidate in candidates:
        parent = candidate.parent
        if parent.exists() and parent.is_dir():
            return vault_root, candidate
    return None


def destination_dir(root: Path, project: str) -> tuple[Path, Path | None]:
    vault_destination = vault_reference_destination(root, project)
    if vault_destination is not None:
        vault_root, vault_dir = vault_destination
        return vault_dir, vault_root
    return root / ".agent" / "memory" / "raw_references", None


def render_reference(args: argparse.Namespace, captured_at: str) -> str:
    tags = ["project-reference", args.project]
    if args.tags:
        tags.extend(tag.strip() for tag in args.tags.split(",") if tag.strip())
    tag_lines = "\n".join(f"  - {tag}" for tag in tags)
    return f"""---
type: raw_reference
source_type: {yaml_quote(args.source_type)}
title: {yaml_quote(args.title)}
url: {yaml_quote(args.url)}
captured_at: {yaml_quote(captured_at)}
project: {yaml_quote(args.project)}
related_task: {yaml_quote(args.task)}
status: raw
ingestion_status: pending
confidence: {yaml_quote(args.confidence)}
tags:
{tag_lines}
---

# {args.title}

## Source URL

{args.url}

## Why This Was Referenced

{args.summary}

## Relevant Excerpt Or Summary

{args.summary}

## How It Affected The Task

{args.impact or "Pending follow-up."}

## Follow-Up Ingestion Notes

{args.follow_up or "Review whether this should become a source note in the Obsidian vault."}
"""


def append_reference_log(root: Path, note_path: Path, args: argparse.Namespace, captured_at: str) -> None:
    log_path = root / ".agent" / "memory" / "reference_log.md"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        display_path = note_path.relative_to(root)
    except ValueError:
        display_path = note_path
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(
            f"\n## {captured_at[:10]} - {args.title}\n\n"
            f"- Source type: {args.source_type}\n"
            f"- URL: {args.url}\n"
            f"- Task: {args.task}\n"
            f"- Confidence: {args.confidence}\n"
            f"- Note: `{display_path}`\n"
        )


def append_vault_reference_registry(vault_root: Path, note_path: Path, args: argparse.Namespace, captured_at: str) -> None:
    registry_path = vault_root / "00_System" / "project_reference_registry.md"
    if not registry_path.exists():
        registry_path.write_text(
            """---
type: registry
status: active
created: 2026-06-19
updated: 2026-06-19
tags:
  - agentic-os
  - project-references
---

# Project Reference Registry

Raw project references captured by repository bridges are listed here before deeper source-note ingestion.

| Captured | Project | Task | Title | Source Type | Confidence | Raw Reference | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
""",
            encoding="utf-8",
        )
    try:
        raw_link = note_path.relative_to(vault_root).as_posix()
    except ValueError:
        raw_link = note_path.as_posix()
    row = (
        f"| {captured_at[:10]} | {args.project} | {args.task} | {args.title} | "
        f"{args.source_type} | {args.confidence} | [[{raw_link}|Raw reference]] | pending-ingest |\n"
    )
    with registry_path.open("a", encoding="utf-8") as handle:
        handle.write(row)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--source-type", required=True, choices=SOURCE_TYPES)
    parser.add_argument("--task", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--confidence", required=True, choices=CONFIDENCE_LEVELS)
    parser.add_argument("--project", default=PROJECT)
    parser.add_argument("--impact", default="")
    parser.add_argument("--follow-up", default="")
    parser.add_argument("--tags", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = repo_root()
    captured_at = datetime.now().astimezone().isoformat(timespec="seconds")
    target_dir, vault_root = destination_dir(root, args.project)
    target_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{captured_at[:10]}-{slugify(args.title)}.md"
    note_path = ensure_unique_path(target_dir, filename)
    note_path.write_text(render_reference(args, captured_at), encoding="utf-8")
    append_reference_log(root, note_path, args, captured_at)
    if vault_root is not None:
        append_vault_reference_registry(vault_root, note_path, args, captured_at)
    print(f"Captured reference: {note_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
