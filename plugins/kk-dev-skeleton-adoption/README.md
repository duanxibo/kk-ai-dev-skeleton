# KK Dev Skeleton Adoption Plugin

This is a repo-local Codex plugin source for internal productization.

It packages the KK Dev Skeleton adoption workflow as a Codex-discoverable skill. The user-facing entry remains natural language: users ask Codex to adopt KK Dev Skeleton, and Codex calls the target repository's deterministic V1 helper behind the scenes.

## Contents

- `.codex-plugin/plugin.json`: plugin manifest.
- `skills/kk-dev-skeleton-adoption/SKILL.md`: adoption workflow.
- `scripts/check_update.py`: non-blocking checker that compares the installed plugin version with the GitHub `main` version and prints an upgrade reminder when the local plugin is stale.
- `scripts/README.md`: notes about plugin-side and target-repository executable behavior.

## Scope

This source directory is not an installed marketplace by itself. It is intended to be used later by an internal marketplace, install package, or team distribution process.

Do not write personal marketplace entries from this repository source unless the user explicitly asks for that installation workflow.

## Update Reminder

The plugin skill should run `scripts/check_update.py` at the start of adoption, check, upgrade, and report requests. The checker is intentionally non-blocking: it reminds users to refresh `kk-dev-skeleton-internal` when a newer GitHub version exists, but it does not auto-install or auto-upgrade anything.
