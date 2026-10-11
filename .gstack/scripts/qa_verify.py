#!/usr/bin/env python3
"""Execute explicit adapter verification argv and record source-bound QA receipts."""
from __future__ import annotations

import argparse
import json
import subprocess
import uuid
from datetime import datetime, timezone
from pathlib import Path

from adapter_runtime import load_adapter_runtime
from evidence_contract import source_fingerprint, sha256_file


def verify(root: Path, keys: list[str], timeout: int = 300) -> tuple[Path, dict]:
    root = root.resolve()
    runtime = load_adapter_runtime(root)
    commands = []
    # Validate the entire request before executing any command. No Markdown/shell execution.
    for key in keys:
        argv = runtime.commands().get(key)
        if not isinstance(argv, list) or not argv or not all(isinstance(v, str) and v for v in argv):
            raise ValueError(f'commands.{key} must be a nonempty argv array in active adapter')
        commands.append((key, argv))
    if not commands or timeout < 1:
        raise ValueError('at least one command and positive timeout are required')
    directory = root / 'output/qa' / uuid.uuid4().hex
    directory.mkdir(parents=True)
    if not directory.resolve().is_relative_to(root):
        raise ValueError('QA output must remain inside repository')
    receipt = {'schema_version': 1, 'started_at': datetime.now(timezone.utc).isoformat(),
               'source_before': source_fingerprint(root), 'runs': []}
    for index, (key, argv) in enumerate(commands):
        stdout = directory / f'{index}.stdout.log'
        stderr = directory / f'{index}.stderr.log'
        timed_out = False
        with stdout.open('wb') as out, stderr.open('wb') as err:
            try:
                result = subprocess.run(argv, cwd=root, stdout=out, stderr=err, timeout=timeout, shell=False)
                code = result.returncode
            except subprocess.TimeoutExpired:
                timed_out, code = True, -1
            except OSError as exc:
                err.write(str(exc).encode())
                code = -1
        receipt['runs'].append({'command_key': key, 'argv': argv, 'exit_code': code,
                                'timed_out': timed_out, 'stdout_path': stdout.relative_to(root).as_posix(),
                                'stderr_path': stderr.relative_to(root).as_posix(),
                                'stdout_sha256': sha256_file(stdout), 'stderr_sha256': sha256_file(stderr)})
        if code != 0:
            break
    receipt['source_after'] = source_fingerprint(root)
    receipt['finished_at'] = datetime.now(timezone.utc).isoformat()
    receipt['status'] = ('passed' if len(receipt['runs']) == len(commands)
                         and all(r['exit_code'] == 0 for r in receipt['runs'])
                         and receipt['source_before'] == receipt['source_after'] else 'failed')
    path = directory / 'receipt.json'
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + '\n')
    return path, receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument('--command-key', action='append', required=True,
                        help='Exact active adapter commands key; repeat for multiple checks')
    parser.add_argument('--timeout-seconds', type=int, default=300)
    args = parser.parse_args()
    try:
        path, receipt = verify(args.repo_root, args.command_key, args.timeout_seconds)
    except (ValueError, RuntimeError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')
    print(json.dumps({'status': receipt['status'], 'execution_receipt': path.relative_to(args.repo_root.resolve()).as_posix()}))
    return 0 if receipt['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
