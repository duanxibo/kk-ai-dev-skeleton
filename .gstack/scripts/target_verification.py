#!/usr/bin/env python3
"""Run explicitly configured product checks, or install an opt-in acceptance CI."""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

CONFIG = '.gstack/target-verification.json'
WORKFLOW = '.github/workflows/kk-acceptance.yml'


def validate_argv(argv: object) -> list[str]:
    if not isinstance(argv, list) or not argv or not all(isinstance(v, str) and v.strip() and '\x00' not in v for v in argv):
        raise ValueError('verification command must be a nonempty JSON argv array')
    return argv


def configure(root: Path, argv: object) -> Path:
    argv = validate_argv(argv)
    path = root.resolve() / CONFIG
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError('configuration destination must remain inside repository')
    if path.exists():
        raise ValueError(f'{CONFIG} already exists; edit the reviewed configuration explicitly')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        json.dump({'version': 1, 'argv': argv}, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    return path


def run(root: Path) -> int:
    root = root.resolve()
    path = root / CONFIG
    if not path.is_file():
        raise ValueError(f'Product verification is not configured. Configure {CONFIG} with an explicit assertion-based test command; framework smoke checks do not verify your product.')
    payload = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(payload, dict) or payload.get('version') != 1:
        raise ValueError('unsupported target verification configuration')
    return subprocess.run(validate_argv(payload.get('argv')), cwd=root, shell=False).returncode


def install_target_ci(root: Path, boundary: str) -> Path:
    """Create a separate workflow; never modify a project's existing workflows."""
    relative = Path(boundary)
    root = root.resolve()
    if relative.is_absolute() or '..' in relative.parts or not (root / relative).resolve().is_relative_to(root):
        raise ValueError('CI boundary must be a safe repository-relative path')
    resolved_relative = (root / relative).resolve().relative_to(root)
    if not resolved_relative.as_posix().startswith('.gstack/task-boundaries/') or resolved_relative.suffix != '.md':
        raise ValueError('CI boundary must be a task-boundaries Markdown file')
    if not (root / relative).is_file():
        raise ValueError('CI boundary must exist before workflow installation')
    path = root / WORKFLOW
    if not path.resolve().is_relative_to(root):
        raise ValueError('workflow destination must remain inside repository')
    if path.exists():
        raise ValueError(f'{WORKFLOW} already exists; refusing to overwrite it')
    # JSON strings are valid YAML scalars; avoid shell interpolation of boundary input.
    command = ['python3', '.gstack/scripts/qa_verify.py', '--boundary', relative.as_posix()]
    runner = 'import subprocess; raise SystemExit(subprocess.run(' + repr(command) + ', check=False).returncode)'
    workflow = ('name: Product acceptance\non: [push, pull_request, workflow_dispatch]\n'
                'permissions:\n  contents: read\njobs:\n  acceptance:\n    runs-on: ubuntu-latest\n'
                '    timeout-minutes: 15\n    steps:\n      - uses: actions/checkout@v4\n'
                '      - uses: actions/setup-python@v5\n        with:\n          python-version: "3.11"\n'
                '      - name: Run configured product assertions and bind acceptance\n'
                '        shell: python\n        run: ' + json.dumps(runner) + '\n')
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as stream:
        stream.write(workflow)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--configure-command-json', help='Explicit product assertion argv; never inferred')
    group.add_argument('--install-ci-boundary', help='Opt-in CI workflow for an existing acceptance boundary')
    args = parser.parse_args()
    try:
        if args.configure_command_json is not None:
            print(configure(args.repo_root, json.loads(args.configure_command_json)))
            return 0
        if args.install_ci_boundary is not None:
            print(install_target_ci(args.repo_root, args.install_ci_boundary))
            return 0
        return run(args.repo_root)
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
