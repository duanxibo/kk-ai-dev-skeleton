---
name: kk-dev-skeleton-adoption
description: Use when a user asks Codex to adopt, install, check, upgrade, or report KK Dev Skeleton for the current repository using natural language rather than manual commands.
---

# KK Dev Skeleton Adoption

This skill is the Codex-facing adoption connector for KK Dev Skeleton.

It does not replace the target repository's `AGENTS.md`, adapter, task boundary, or guard rules. It routes the user request into the repository-native adoption flow and calls the deterministic V1 helper when available.

## User Entry

Users should ask in natural language, for example:

```text
请把当前项目接入 KK Dev Skeleton。
```

Do not require business users to learn CLI flags. Commands are internal execution details that Codex may run and summarize.

## Workflow

1. Confirm the current repository context from local files, not from parent directory names or global skills.
2. Read local repo guidance when present:
   - `AGENTS.md`
   - `.gstack/README.md`
   - `.gstack/knowledge/CODEMAP.md`
   - `.gstack/knowledge/doc-placement.md`
   - `adapters/default/adapter.md`
   - `adapters/default/runtime.json`
3. If the target repository already contains `scripts/init_project.py`, call the V1 helper:
   - detect: `python3 scripts/init_project.py --adapter <adapter> --detect`
   - plan: `python3 scripts/init_project.py --adapter <adapter> --plan`
   - apply: `python3 scripts/init_project.py --adapter <adapter> --apply`
   - verify/report: `python3 scripts/init_project.py --adapter <adapter> --verify --report`
4. If the repository does not contain the helper, explain that the framework core or internal template must be added first. Ask for the approved skeleton source or template path only when it cannot be inferred from the current workspace.
5. Create or update project adapter files only after the target repository's task boundary permits that scope.
6. Summarize the result in user language:
   - what was detected
   - what was created or preserved
   - which checks passed or failed
   - what still needs human confirmation
   - the first low-risk pilot task

## Safety Rules

- Do not connect to real data by default.
- Do not perform production operations.
- Do not change database schema.
- Do not execute git workflow actions without explicit user approval.
- Do not overwrite an existing project adapter unless the user explicitly approves that scope.
- Do not create or modify marketplace files unless the user explicitly asks to install or publish the plugin.
- Do not treat one-off chat text as team source of truth; write repo-native evidence when changing the repository.

## Expected Outputs

When adoption succeeds, report:

- adapter path
- active boundary path
- V1 helper report summary
- guard and smoke status
- remaining missing information
- recommended first pilot task

When adoption is blocked, report the smallest missing input needed to continue.
