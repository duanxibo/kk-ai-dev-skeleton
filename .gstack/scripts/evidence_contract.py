"""Shared content contract for compact/full engineering review and executed QA.

Receipts detect missing, failed and stale verification, not malicious authors.
Independent CI remains the trust boundary for code contributions.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

ENG_REQUIRED = (
    'AI 语义复核: yes', '## Codex 自主工程决策', '## 用户决策边界',
    '## 防技术甩锅检查', '## 验证计划',
)
ENG_FORBIDDEN = (
    '需要用户选择测试命令', '需要用户决定测试命令', '需要用户选择代码结构',
    '需要用户决定代码结构', '请用户选择技术方案', '请用户决定技术方案',
    '用户决定 subagent 角色', '用户选择 subagent 角色', '用户决定门禁恢复顺序',
    '用户选择门禁恢复顺序', '让用户选择测试命令', '让用户选择代码结构',
    'ask user to choose test commands', 'ask user to choose code structure',
    'ask user to choose subagent roles', 'ask user to choose gate recovery order',
)


def section(text: str, header: str) -> str:
    match = re.search(r'^## ' + re.escape(header) + r'\s*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    return match.group(1) if match else ''


def field(text: str, name: str) -> str:
    match = re.search(r'^[ \t]*-[ \t]*' + re.escape(name) + r':[ \t]*(.*?)[ \t]*$', text, re.M)
    return match.group(1).strip().strip('`') if match else ''


def is_compact(text: str) -> bool:
    return field(section(text, 'Flow Lane'), 'Lane') == 'fast-lane' and field(section(text, 'Compact Evidence'), 'Strategy') == 'compact'


def review_check(text: str) -> tuple[list[str], list[str], list[str]]:
    forbidden = [m for m in ENG_FORBIDDEN if m.lower() in text.lower()]
    if is_compact(text):
        review = section(text, 'Compact Review')
        required = ['AI 语义复核: yes', 'Result: pass', 'Scope', 'Verification plan',
                    'Engineering decisions', 'User decisions', 'Delegation check']
        missing = []
        for marker in required:
            if marker == 'AI 语义复核: yes':
                ok = field(section(text, 'Compact Evidence'), 'AI 语义复核') == 'yes'
            elif marker == 'Result: pass':
                ok = field(review, 'Result') == 'pass'
            else:
                ok = bool(field(review, marker))
            if not ok:
                missing.append(marker)
    else:
        required = list(ENG_REQUIRED)
        missing = [m for m in required if m not in text]
    if re.search(r'draft-needs-codex-review|pending-review|AI 语义复核:\s*`?no', text, re.I):
        missing.append('semantic review completed')
    return required, missing, forbidden


def repo_file(root: Path, raw: str) -> Path:
    p = (root / raw.strip().strip('`')).resolve()
    if not p.is_relative_to(root.resolve()) or not p.is_file():
        raise ValueError('evidence/log must be an existing file inside repository')
    return p


IGNORED_DIRS = {'.git', 'output', '.tmp', '__pycache__', '.venv', 'venv', 'node_modules',
                'dist', 'build', 'target', '.pytest_cache', '.mypy_cache', '.ruff_cache', '.codex-artifacts'}
EVIDENCE_DIRS = ('task-boundaries', 'requirements', 'reviews', 'qa-reports', 'learnings')


def source_fingerprint(root: Path) -> str:
    """Hash tracked plus nonignored new files; evidence/status writes do not stale QA."""
    result = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                            cwd=root, capture_output=True)
    if result.returncode == 0:
        names = {n.decode('utf-8', 'surrogateescape') for n in result.stdout.split(b'\0') if n}
    else:
        names = {p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()}
    digest = hashlib.sha256()
    for name in sorted(names):
        parts = Path(name).parts
        if any(p in IGNORED_DIRS for p in parts):
            continue
        if name.startswith('.gstack/') and len(parts) > 1 and parts[1] in EVIDENCE_DIRS:
            continue
        if name in {'.gstack/codex-mode.local.md', '.gstack/browse-audit.jsonl'}:
            continue
        path = root / name
        digest.update(name.encode('utf-8', 'surrogateescape') + b'\0')
        if path.is_symlink():
            # Never dereference out-of-repository symlinks.
            import os
            digest.update(b'link:' + os.readlink(path).encode())
        elif path.is_file():
            digest.update(path.read_bytes())
        else:
            digest.update(b'deleted')
    return digest.hexdigest()


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def qa_check(root: Path, text: str) -> tuple[bool, str]:
    """Require all referenced receipts to pass on the current source/config snapshot."""
    from adapter_runtime import load_adapter_runtime
    raw_paths = re.findall(r'^\s*-\s*Execution Receipt:\s*`?([^`\n]+)`?\s*$', text, re.M)
    if not raw_paths:
        return False, 'QA requires Execution Receipt from qa_verify.py; handwritten results are insufficient'
    try:
        current = source_fingerprint(root)
        runtime = load_adapter_runtime(root)
        for raw in raw_paths:
            path = repo_file(root, raw.strip())
            if not path.relative_to(root.resolve()).as_posix().startswith('output/qa/'):
                raise ValueError('receipt must be under output/qa/')
            receipt = json.loads(path.read_text())
            if not isinstance(receipt, dict):
                raise ValueError('receipt must be a JSON object')
            if receipt.get('schema_version') not in (1, 2) or receipt.get('status') != 'passed':
                raise ValueError('receipt is not a successful execution')
            if receipt.get('source_before') != current or receipt.get('source_after') != current:
                raise ValueError('QA receipt is stale or verification changed source; rerun verification')
            runs = receipt.get('runs')
            if not isinstance(runs, list) or not runs:
                raise ValueError('receipt has no command executions')
            for run in runs:
                if not isinstance(run, dict):
                    raise ValueError('each command execution must be a JSON object')
                configured = runtime.commands().get(run.get('command_key'))
                if not isinstance(configured, list) or not configured or run.get('argv') != configured:
                    raise ValueError('receipt command does not match current adapter allowlist')
                if type(run.get('exit_code')) is not int or run['exit_code'] != 0 or run.get('timed_out') is not False:
                    raise ValueError('verification failed or timed out')
                for key in ('stdout', 'stderr'):
                    log = repo_file(root, run[key + '_path'])
                    if not log.relative_to(root.resolve()).as_posix().startswith('output/qa/'):
                        raise ValueError('QA logs must be under output/qa/')
                    if sha256_file(log) != run[key + '_sha256']:
                        raise ValueError('verification log checksum mismatch')
        return True, ''
    except (ValueError, RuntimeError, KeyError, TypeError, OSError) as exc:
        return False, str(exc)


def parse_gates(text: str) -> list[dict[str, str]]:
    """Support existing block records and compact JSON flow mappings (valid YAML)."""
    gates = []
    current = None
    for raw in section(text, 'Required Gates').splitlines():
        line = raw.strip()
        if line.startswith('- {'):
            if current:
                gates.append(current)
                current = None
            try:
                payload = json.loads(line[2:])
                if not isinstance(payload, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in payload.items()):
                    raise ValueError('gate mappings must contain string fields')
                gates.append(payload)
            except (ValueError, TypeError):
                gates.append({'gate_id': '<invalid-inline-gate>', 'status': 'invalid'})
            continue
        item = re.match(r'^-\s*([a-z_]+):\s*(.*)$', line)
        value = re.match(r'^([a-z_]+):\s*(.*)$', line)
        if item:
            if current:
                gates.append(current)
            current = {item[1]: item[2].strip().strip('"\'`')}
        elif value and current is not None:
            current[value[1]] = value[2].strip().strip('"\'`')
    if current:
        gates.append(current)
    return gates


def gate_block(text: str, gate_id: str) -> str | None:
    for gate in parse_gates(text):
        if gate.get('gate_id') == gate_id:
            return '\n'.join(f'{key}: {value}' for key, value in gate.items())
    return None
