#!/usr/bin/env bash
set -euo pipefail

if ! ROOT_DIR="$(git rev-parse --show-toplevel 2>/dev/null)"; then
  echo "[ERROR] This command must be run inside a git worktree." >&2
  echo "        Run 'git init' first if this skeleton is being used as a new repository." >&2
  exit 1
fi

cd "$ROOT_DIR"

git config core.hooksPath .githooks

chmod +x .githooks/pre-commit
chmod +x .githooks/pre-push
chmod +x .gstack/scripts/spec_sync_guard.py
chmod +x .gstack/scripts/team_flow_guard.py
chmod +x .gstack/scripts/gstack_doctor.py
chmod +x .gstack/scripts/sync_repo_skills.sh

echo "Installed repo-managed git hooks."
echo "core.hooksPath=$(git config core.hooksPath)"
echo "Active hooks: .githooks/pre-commit, .githooks/pre-push"
