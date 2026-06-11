#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
BOUNDARY_DIR="${REPO_ROOT}/.gstack/task-boundaries"
LOCAL_POINTER="${BOUNDARY_DIR}/CURRENT.local.md"

usage() {
  cat <<'EOF'
Usage:
  bash .gstack/scripts/use_boundary.sh <boundary-file>

Examples:
  bash .gstack/scripts/use_boundary.sh .gstack/task-boundaries/2026-05-18_local-active-boundary-pointer.md
  bash .gstack/scripts/use_boundary.sh 2026-05-18_local-active-boundary-pointer.md
EOF
}

if [ "${1:-}" = "" ]; then
  usage
  exit 1
fi

INPUT_PATH="$1"

TARGET_RELATIVE="$(python3 - <<'PY' "$REPO_ROOT" "$INPUT_PATH"
from pathlib import Path
import sys

repo_root = Path(sys.argv[1]).resolve()
input_path = sys.argv[2]
boundary_dir = repo_root / ".gstack" / "task-boundaries"

raw = Path(input_path)
if raw.is_absolute():
    candidate = raw.resolve()
else:
    repo_candidate = (repo_root / raw).resolve()
    boundary_candidate = (boundary_dir / raw).resolve()
    candidate = repo_candidate if repo_candidate.exists() else boundary_candidate

try:
    relative = candidate.relative_to(repo_root)
except ValueError:
    print("ERROR: boundary file must stay inside the repo", file=sys.stderr)
    sys.exit(1)

relative_posix = relative.as_posix()
if not relative_posix.startswith(".gstack/task-boundaries/"):
    print("ERROR: boundary file must be under .gstack/task-boundaries/", file=sys.stderr)
    sys.exit(1)
if relative_posix.endswith("CURRENT.md") or relative_posix.endswith("CURRENT.local.md"):
    print("ERROR: choose a concrete boundary file, not CURRENT.md/CURRENT.local.md", file=sys.stderr)
    sys.exit(1)
if not candidate.exists():
    print(f"ERROR: boundary file not found: {relative_posix}", file=sys.stderr)
    sys.exit(1)

print(relative_posix)
PY
)"

TARGET_BASENAME="$(basename "$TARGET_RELATIVE")"

cat > "$LOCAL_POINTER" <<EOF
# 当前本地 Active Boundary

这个文件只用于当前机器 / 当前 worktree 的本地 active boundary 指针。

它已加入 gitignore，不应提交。

## Active Boundary

- [$TARGET_BASENAME]($TARGET_BASENAME)
EOF

echo "[OK] Local active boundary -> ${TARGET_RELATIVE}"
echo "[OK] Wrote ${LOCAL_POINTER}"
