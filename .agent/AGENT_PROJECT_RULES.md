---
type: agent_project_rules
status: active
created: 2026-09-28
updated: 2026-09-28
project: csu-global-ms-ai-ml-academic
tags:
  - agentic-os
  - project-memory
  - rules
---

# CSU Global MS AI/ML coursework Agent Project Rules

These rules define the project-local memory bridge for `csu-global-ms-ai-ml-academic`. They supplement the repository README, local project docs, and the Obsidian Agentic OS vault.

## Before Major Work

For a major task, goal, refactor, schema change, data workflow, or multi-step implementation:

1. Read this file.
2. Read `README.md` or the project-specific entry docs.
3. Read relevant project memory:
   - `.agent/memory/lessons_learned.md`
   - `.agent/memory/decision_log.md`
   - `.agent/memory/project_log.md`
   - `.agent/memory/reference_log.md`
4. Read the Obsidian vault context when available:
   - `_wiki/index.md`, if `_wiki` exists.
   - `%AGENT_OS_VAULT_PATH%\index.md`, if `AGENT_OS_VAULT_PATH` is set.
5. Verify the selected Git profile before commits or pushes.

## Project Boundary

Preserve academic integrity, assignment constraints, citation details, and rubric context.

## Repo Policy

Expected Git profile: `school`

Use the school GitHub remote and school identity; protect main; keep coursework changes in assignment-scoped branches or worktrees.

## Reference Capture

When an external reference materially affects implementation or reasoning, capture it with:

```powershell
python .\.agent\scripts\save_reference.py `
  --title "Reference title" `
  --url "https://example.com/reference" `
  --source-type "docs" `
  --task "Task name" `
  --summary "Why it mattered" `
  --confidence "high"
```

If `_wiki` or `AGENT_OS_VAULT_PATH` is available, the script writes to the vault under:

```text
10_Sources/Raw/Project References/csu-global-ms-ai-ml-academic/
```

Otherwise it writes to:

```text
.agent/memory/raw_references/
```

## Postmortem Capture

After meaningful work, append a postmortem with:

```powershell
python .\.agent\scripts\postmortem.py `
  --task "Task name" `
  --what-changed "What changed" `
  --why "Why it changed" `
  --files-touched "Files or folders touched" `
  --validation "Commands or checks run" `
  --issues "Issues encountered" `
  --lessons "Reusable lessons, or none" `
  --decisions "Durable decisions, or none" `
  --references "References captured, or none"
```

## Decision Rules

- Record architecture, dependency, schema, orchestration, security, and workflow decisions in `.agent/memory/decision_log.md`.
- Record reusable errors, validation lessons, and project-specific gotchas in `.agent/memory/lessons_learned.md`.
- Record every meaningful project task in `.agent/memory/project_log.md`.
- Keep memory concise and evidence-based.

## Bridge Validation

Run:

```powershell
python .\.agent\scripts\validate_bridge.py
```

Use `--require-vault` only after `_wiki` or `AGENT_OS_VAULT_PATH` is intentionally configured.

## Approval Gates

Stop for explicit user approval before:

- Destructive file operations.
- Sensitive data exposure.
- Production database writes.
- Credential changes.
- Publishing or pushing private material.
- Changes that weaken existing governance gates.
