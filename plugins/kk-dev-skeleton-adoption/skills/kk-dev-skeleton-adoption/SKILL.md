---
name: kk-dev-skeleton-adoption
description: Use when a user asks Codex to adopt, install, check, upgrade, or report KK Dev Skeleton for the current repository using natural language rather than manual commands.
---

# KK Dev Skeleton Adoption

This skill is the Codex-facing adoption connector for KK Dev Skeleton.

It does not replace the target repository's `AGENTS.md`, adapter, task boundary, or guard rules. It routes the user request into the repository-native adoption flow and calls the deterministic V9 helper when available.

## User Entry

Users should ask in natural language, for example:

```text
请把当前项目接入 KK Dev Skeleton。
```

For an already adopted project, users should ask:

```text
请按最新版 KK Dev Skeleton 升级当前项目。先生成增量升级计划，不要重新接入新项目。
```

Do not require business users to learn CLI flags. Commands are internal execution details that Codex may run and summarize.

## Workflow

0. Run the non-blocking plugin update check before any adoption, install, check, upgrade, or report workflow:
   - Resolve the plugin root from this skill directory.
   - Run `python3 ../../scripts/check_update.py --format text`.
   - If it reports `outdated`, tell the user that a newer plugin is available and recommend refreshing `kk-dev-skeleton-internal` before continuing.
   - If it reports `unknown`, do not block the current task; mention the check failure only when the user asked about plugin update status or installation freshness.
   - Never auto-run marketplace upgrade, plugin reinstall, or git workflow actions without user approval.
1. Confirm the current repository context from local files, not from parent directory names or global skills.
2. Read local repo guidance when present:
   - `AGENTS.md`
   - `.gstack/README.md`
   - `.gstack/knowledge/CODEMAP.md`
   - `.gstack/knowledge/doc-placement.md`
   - `adapters/default/adapter.md`
   - `adapters/default/runtime.json`
3. If the target repository already contains `scripts/init_project.py`, call the V9 helper:
   - detect: `python3 scripts/init_project.py --adapter <adapter> --detect`
   - plan: `python3 scripts/init_project.py --adapter <adapter> --plan`
   - apply: `python3 scripts/init_project.py --adapter <adapter> --apply`
   - portable core dry-run: `python3 scripts/init_project.py --adapter <adapter> --apply-core --dry-run --report`
   - portable core apply: `python3 scripts/init_project.py --adapter <adapter> --apply-core --report`
   - explicit runtime dry-run: `python3 scripts/init_project.py --adapter <adapter> --apply-runtime --dry-run --report`
   - explicit runtime apply: `python3 scripts/init_project.py --adapter <adapter> --apply-runtime --report`
   - adapter rewrite dry-run: `python3 scripts/init_project.py --adapter <adapter> --project-name <name> --rewrite-adapter --dry-run --report`
   - adapter rewrite apply: `python3 scripts/init_project.py --adapter <adapter> --project-name <name> --rewrite-adapter --report`
   - schema guard: `python3 scripts/init_project.py --adapter <adapter> --validate-adapter --report`
   - verify/report: `python3 scripts/init_project.py --adapter <adapter> --verify --verify-core --verify-runtime --report`
   - isolated pilot: `python3 scripts/init_project.py --adapter <adapter> --pilot --report`
   The helper should create or preserve adapter metadata, portable core files, and the explicit runtime script bundle while keeping target project files intact by default.
   If it detects root-level application paths such as `src/`, `prisma/`, `e2e/`, `app/`,
   `packages/`, or root framework config files, do not silently treat that scattered layout as
   final. Report them as migration candidates and ask Codex to create a migration plan before
   moving application code.
4. Existing Project Upgrade:
   - Use this lane when the user asks to apply new plugin / skeleton capabilities to a repository that was already adopted.
   - Do not tell the user to create a new project or rerun first-time adoption.
   - First run `--detect`, `--plan`, and `--validate-adapter --report`.
   - Run `--apply-core --dry-run --report`, `--apply-runtime --dry-run --report`, and `--rewrite-adapter --dry-run --report` to form an incremental plan.
   - Only apply safe, idempotent create-missing changes within the active task boundary.
   - Never overwrite adapter files, move root-level application code, sync runtime scripts over existing target files, or change marketplace/plugin installation state without a separate explicit plan and user approval.
   - If the target helper is older and lacks these flags, do not ask the user to create a new project. Explain that the project helper is stale, then generate a compatibility upgrade plan: preserve the current adapter, list missing portable core/runtime files, list root-level migration candidates, and propose syncing the latest helper as a separate reviewed change.
5. If the repository does not contain the helper, explain that the framework core or internal template must be added first. Ask for the approved skeleton source or template path only when it cannot be inferred from the current workspace.
6. Create or update project adapter files only after the target repository's task boundary permits that scope.
7. Summarize the result in user language:
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
- stack path
- plugin update check status
- existing project upgrade plan status, when relevant
- active boundary path
- V9 helper report summary
- guard and smoke status
- root-level migration candidates, if any
- remaining missing information
- recommended first pilot task

When adoption is blocked, report the smallest missing input needed to continue.
