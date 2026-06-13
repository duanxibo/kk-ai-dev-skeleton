#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

REMOVE_TG_LINKS=0
SKIP_SKILLS=0
SKIP_HOOKS=0

usage() {
  cat <<'EOF'
Usage:
  bash scripts/setup_local_codex.sh [options]

Options:
  --remove-tg-links  Remove old tg-* skill symlinks from $CODEX_HOME/skills.
  --skip-skills      Skip repo-native kk-* skill sync.
  --skip-hooks       Skip git hooks installation.
  -h, --help         Show this help.

This script is the deterministic local setup layer Codex can run behind the
natural-language adoption flow. Ordinary partners do not need to memorize it.
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --remove-tg-links)
      REMOVE_TG_LINKS=1
      ;;
    --skip-skills)
      SKIP_SKILLS=1
      ;;
    --skip-hooks)
      SKIP_HOOKS=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

cd "$REPO_ROOT"

if [ "$SKIP_SKILLS" -eq 0 ]; then
  if [ "$REMOVE_TG_LINKS" -eq 1 ]; then
    bash .gstack/scripts/sync_repo_skills.sh --remove-tg-links
  else
    bash .gstack/scripts/sync_repo_skills.sh
  fi
else
  echo "[SKIP] repo-native skill sync"
fi

if [ "$SKIP_HOOKS" -eq 0 ]; then
  if git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    bash .gstack/scripts/install_git_hooks.sh
  else
    echo "[SKIP] git hooks installation (not a git worktree)"
  fi
else
  echo "[SKIP] git hooks installation"
fi

python3 .gstack/scripts/gstack_doctor.py check
