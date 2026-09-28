"""Validate the csu-global-ms-ai-ml-academic Agentic OS project memory bridge."""

from __future__ import annotations

import argparse
import ast
import os
from pathlib import Path


PROJECT = "csu-global-ms-ai-ml-academic"

REQUIRED_FILES = [
    ".agent/AGENT_PROJECT_RULES.md",
    ".agent/README.md",
    ".agent/memory/lessons_learned.md",
    ".agent/memory/project_log.md",
    ".agent/memory/decision_log.md",
    ".agent/memory/reference_log.md",
    ".agent/templates/reference_note_template.md",
    ".agent/templates/postmortem_template.md",
    ".agent/scripts/save_reference.py",
    ".agent/scripts/postmortem.py",
    ".agent/scripts/validate_bridge.py",
]

REQUIRED_DIRS = [
    ".agent/memory",
    ".agent/memory/raw_references",
    ".agent/scripts",
    ".agent/templates",
]

FORBIDDEN_TOKEN_PARTS = [
    ("password", "="),
    ("api", "_key", "="),
    ("secret", "="),
    ("token", "="),
    ("BEGIN", " PRIVATE", " KEY"),
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def vault_path(root: Path) -> Path | None:
    wiki = root / "_wiki"
    if wiki.exists() and wiki.is_dir():
        return wiki
    env_vault = os.environ.get("AGENT_OS_VAULT_PATH")
    if env_vault:
        candidate = Path(env_vault).expanduser()
        if candidate.exists() and candidate.is_dir():
            return candidate
    return None


def check_python_syntax(path: Path) -> str | None:
    try:
        ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return f"{path}: syntax error at line {exc.lineno}: {exc.msg}"
    return None


def check_forbidden_tokens(root: Path) -> list[str]:
    issues: list[str] = []
    forbidden_tokens = ["".join(parts) for parts in FORBIDDEN_TOKEN_PARTS]
    for path in (root / ".agent").rglob("*"):
        if not path.is_file():
            continue
        if path.suffix.lower() not in {".md", ".py"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        lowered = text.lower()
        for token in forbidden_tokens:
            needle = token.lower()
            if needle in lowered:
                issues.append(f"{path.relative_to(root)} contains forbidden token pattern: {token}")
    return issues


def validate(require_vault: bool) -> tuple[list[str], list[str]]:
    root = repo_root()
    errors: list[str] = []
    warnings: list[str] = []
    for rel in REQUIRED_DIRS:
        path = root / rel
        if not path.exists() or not path.is_dir():
            errors.append(f"missing required directory: {rel}")
    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.exists() or not path.is_file():
            errors.append(f"missing required file: {rel}")
    for rel in [".agent/scripts/save_reference.py", ".agent/scripts/postmortem.py", ".agent/scripts/validate_bridge.py"]:
        path = root / rel
        if path.exists():
            syntax_error = check_python_syntax(path)
            if syntax_error:
                errors.append(syntax_error)
    pycache_dirs = [path for path in (root / ".agent").rglob("__pycache__") if path.is_dir()]
    for path in pycache_dirs:
        errors.append(f"generated Python cache directory should be removed: {path.relative_to(root)}")
    project_log = root / ".agent" / "memory" / "project_log.md"
    if project_log.exists() and "## " not in project_log.read_text(encoding="utf-8", errors="replace"):
        warnings.append("project log has no postmortem entries yet")
    errors.extend(check_forbidden_tokens(root))
    vault = vault_path(root)
    if require_vault and vault is None:
        errors.append("vault connection required but neither _wiki nor AGENT_OS_VAULT_PATH resolved")
    elif vault is None:
        warnings.append("vault connection not configured; bridge will use .agent/memory/raw_references fallback")
        ref_notes = list((root / ".agent" / "memory" / "raw_references").glob("*.md"))
        if not ref_notes:
            warnings.append("no fallback raw reference notes found")
    else:
        vault_index = vault / "index.md"
        if not vault_index.exists():
            warnings.append(f"vault path resolved but index.md is missing: {vault}")
        expected_raw_parent = vault / "10_Sources" / "Raw" / "Project References"
        if not expected_raw_parent.exists():
            warnings.append(f"vault project-reference parent does not exist yet: {expected_raw_parent}")
    return errors, warnings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-vault", action="store_true", help="Fail if _wiki or AGENT_OS_VAULT_PATH does not resolve.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors, warnings = validate(require_vault=args.require_vault)
    print(f"project={PROJECT}")
    print(f"errors={len(errors)}")
    for error in errors:
        print(f"ERROR: {error}")
    print(f"warnings={len(warnings)}")
    for warning in warnings:
        print(f"WARNING: {warning}")
    if errors:
        return 1
    print("bridge_status=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
