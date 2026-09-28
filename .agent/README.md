---
type: project_memory_readme
status: active
created: 2026-09-28
updated: 2026-09-28
project: csu-global-ms-ai-ml-academic
tags:
  - agentic-os
  - project-memory
  - readme
---

# CSU Global MS AI/ML coursework Project Memory Bridge

This `.agent` folder is the file-based memory bridge for `csu-global-ms-ai-ml-academic`.

## Purpose

The bridge lets Codex and future agents:

- Read project rules before major work.
- Capture external references used during implementation.
- Write postmortems after meaningful work.
- Preserve reusable lessons and durable decisions.
- Keep sensitive data out of Codex-facing memory.
- Connect project work back to the Obsidian vault when a vault path is available.

## Folder Layout

```text
.agent/
  AGENT_PROJECT_RULES.md
  README.md
  memory/
    lessons_learned.md
    project_log.md
    decision_log.md
    reference_log.md
    raw_references/
  scripts/
    save_reference.py
    postmortem.py
    validate_bridge.py
  templates/
    reference_note_template.md
    postmortem_template.md
```

## Vault Connection

The scripts detect the vault in this order:

1. A repo-local `_wiki` junction or symlink.
2. The `AGENT_OS_VAULT_PATH` environment variable.
3. Fallback to `.agent/memory/raw_references/`.

When a vault connection exists, raw references are written to:

```text
10_Sources/Raw/Project References/csu-global-ms-ai-ml-academic/
```

Vault-connected captures also append:

```text
00_System/project_reference_registry.md
```

## Operating Rule

The repo remains the execution layer. Obsidian is the cross-project memory layer. This bridge is the explicit handoff between the two.

## Validation

```powershell
python .\.agent\scripts\validate_bridge.py
python .\.agent\scripts\validate_bridge.py --require-vault
```
