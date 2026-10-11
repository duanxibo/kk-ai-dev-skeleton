#!/usr/bin/env python3
"""Audit code files that the active adapter would otherwise silently ignore."""
from __future__ import annotations
import argparse
import json
import os
import subprocess
from pathlib import Path
from adapter_runtime import ADAPTER_ENV, ADAPTER_RUNTIME_ENV, load_adapter_runtime

SOURCE_SUFFIXES = frozenset({'.py', '.sh', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs', '.rb', '.php', '.cs', '.cpp', '.c', '.h', '.swift', '.kt', '.vue', '.svelte', '.html', '.sql'})
IGNORED_COMPONENTS = frozenset({'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build', 'target', '.next', 'coverage', 'output'})


def load_coverage_runtime(root: Path):
    """Source identity requires repo-owned markers; explicit adapters always win."""
    source = all((root / path).is_file() for path in (
        'adapters/skeleton/runtime.json', 'scripts/init_project.py',
        'plugins/kk-dev-skeleton-adoption/.codex-plugin/plugin.json'))
    explicit = os.environ.get(ADAPTER_ENV, '').strip() or os.environ.get(ADAPTER_RUNTIME_ENV, '').strip()
    return load_adapter_runtime(root, adapter='skeleton' if source and not explicit else None)


def source_files(root: Path) -> list[str]:
    result = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root, capture_output=True, check=False)
    if result.returncode == 0:
        paths = result.stdout.decode('utf-8', errors='surrogateescape').split('\0')
    else:
        paths = [p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()]
    return sorted(set(p for p in paths if p and Path(p).suffix.lower() in SOURCE_SUFFIXES
                      and not any(part in IGNORED_COMPONENTS for part in Path(p).parts)))


def uncovered_sources(root: Path, runtime, files: list[str] | None = None) -> list[str]:
    prefixes = (runtime.path_tuple('implementation_prefixes')
                + runtime.path_tuple('demo_prefixes') + runtime.path_tuple('archive_prefixes')
                + runtime.path_tuple('prototype_prefixes'))
    # Portable collaboration helpers are framework infrastructure, not application code.
    infrastructure = ('.gstack/scripts/',)
    infrastructure_files = {'scripts/init_project.py'}
    return [path for path in (source_files(root) if files is None else files)
            if path not in infrastructure_files
            if Path(path).suffix.lower() in SOURCE_SUFFIXES
            and not any(path.startswith(prefix) for prefix in prefixes + infrastructure)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        runtime = load_coverage_runtime(args.repo_root)
        missing = uncovered_sources(args.repo_root, runtime)
    except RuntimeError as exc:
        print(json.dumps({'status':'fail', 'error': str(exc)}))
        return 2
    print(json.dumps({'status': 'fail' if missing else 'pass', 'adapter':runtime.adapter_name, 'uncovered_sources':missing}, ensure_ascii=False, indent=2))
    return 1 if missing else 0

if __name__ == '__main__':
    raise SystemExit(main())
