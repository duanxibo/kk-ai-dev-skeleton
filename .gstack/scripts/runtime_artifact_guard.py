#!/usr/bin/env python3
"""Fail if local/runtime artifacts are tracked by git."""

from __future__ import annotations

import fnmatch
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_PATTERNS = (
    "node_modules/**",
    "dist/**",
    "build/**",
    "target/**",
    ".vite/**",
    ".codex-artifacts/**",
    ".playwright-mcp/**",
    ".playwright-cli/**",
    ".gstack/browse-audit.jsonl",
    ".gstack/task-boundaries/CURRENT.local.md",
    ".gstack/codex-mode.local.md",
    "stack/account-tools/**",
    "stack/cash-account/node_modules/**",
    "app/backend/target/**",
)

FORBIDDEN_SUFFIXES = (
    "/node_modules/",
    "/.vite/",
    "/dist/",
    "/build/",
    "/target/",
)

ALLOWED_PATTERNS = (
    ".env.example",
    "**/.env.example",
    "**/.env.test.example",
    "**/.env.prod.example",
    "**/.env.production.example",
    ".github/**",
    "app/restricted-module/public/assets/**",
    ".gstack/data-access/.env.local",
    ".gstack/data-access/config.local.yaml",
)


def git_ls_files() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [item.decode("utf-8") for item in result.stdout.split(b"\0") if item]


def git_deleted_files() -> set[str]:
    result = subprocess.run(
        ["git", "ls-files", "--deleted", "-z"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return {item.decode("utf-8") for item in result.stdout.split(b"\0") if item}


def matches_any(path: str, patterns: tuple[str, ...]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def is_forbidden(path: str) -> bool:
    if matches_any(path, ALLOWED_PATTERNS):
        return False
    if matches_any(path, FORBIDDEN_PATTERNS):
        return True
    normalized = f"/{path}/"
    return any(suffix in normalized for suffix in FORBIDDEN_SUFFIXES)


def main() -> int:
    deleted = git_deleted_files()
    tracked = [path for path in git_ls_files() if path not in deleted]
    violations = sorted(path for path in tracked if is_forbidden(path))
    if violations:
        print("Runtime artifact guard failed. Tracked local/runtime files:")
        for path in violations:
            print(f"- {path}")
        print()
        print("Move these files out of the repo, add a narrow .gitignore rule, or document an explicit exception.")
        return 1
    print(f"Runtime artifact guard passed: scanned {len(tracked)} tracked files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
