"""Frozen task acceptance mapped to designated adapter verification commands.

This validates coverage and execution, not the semantic quality of assertions.
Low-level execution receipts remain usable without a task; completion does not.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from adapter_runtime import load_adapter_runtime
from evidence_contract import field, qa_check, repo_file, section


@dataclass(frozen=True)
class AcceptancePlan:
    boundary_path: str
    digest: str
    criteria: list[dict]
    command_keys: list[str]

    def binding(self) -> dict:
        return {'boundary_path': self.boundary_path, 'digest': self.digest, 'criteria': self.criteria}


def scaffold(criteria: list[str]) -> str:
    payload = {'version': 1, 'criteria': [
        {'id': f'AC-{i + 1}', 'description': value, 'command_keys': []}
        for i, value in enumerate(criteria) if value.strip()
    ]}
    return '## Acceptance Verification\n```json\n' + json.dumps(payload, ensure_ascii=False) + '\n```\n'


def visible_criteria(text: str) -> list[tuple[str | None, str]]:
    """Read existing simple, field-based and subsection-based acceptance lists."""
    body = section(text, 'User-visible Acceptance')
    if not body:
        raise ValueError('User-visible Acceptance is required as the frozen criterion source')
    lines = body.splitlines()
    field_start = next((i for i, line in enumerate(lines) if re.match(r'^- Expected Visible Behavior:', line.strip()) and not line.startswith(' ')), None)
    heading_start = next((i for i, line in enumerate(lines) if line.strip() == '### Expected Visible Behavior'), None)
    items = []
    if field_start is not None:
        inline = lines[field_start].split(':', 1)[1].strip().strip('`')
        if inline:
            items.append(inline)
        for line in lines[field_start + 1:]:
            if line.startswith('- '):
                break
            if line.lstrip().startswith('- '):
                items.append(line.strip()[2:].strip().strip('`'))
    elif heading_start is not None:
        for line in lines[heading_start + 1:]:
            if line.startswith('### '):
                break
            if line.strip().startswith('- '):
                items.append(line.strip()[2:].strip().strip('`'))
    else:
        items = [line.strip()[2:].strip().strip('`') for line in lines if line.strip().startswith('- ')]
    if not items or any(not item for item in items):
        raise ValueError('frozen visible acceptance must contain nonempty criteria')
    result = []
    for item in items:
        match = re.match(r'^(AC-[A-Za-z0-9_-]+):\s*(.+)$', item)
        result.append((match[1] if match else None, match[2] if match else item))
    return result


def load_acceptance(root: Path, boundary: str | Path) -> AcceptancePlan:
    root = root.resolve()
    path = repo_file(root, str(boundary))
    relative = path.relative_to(root).as_posix()
    if not relative.startswith('.gstack/task-boundaries/') or path.suffix != '.md':
        raise ValueError('acceptance boundary must be a task-boundaries Markdown file')
    text = path.read_text(encoding='utf-8')
    block = section(text, 'Acceptance Verification')
    match = re.fullmatch(r'\s*```json\s*\n(.*?)\n```\s*', block, re.S)
    if not match:
        raise ValueError('task completion needs ## Acceptance Verification with a JSON criteria mapping; migrate legacy task evidence')
    payload = json.loads(match[1])
    if not isinstance(payload, dict) or type(payload.get('version')) is not int or payload['version'] != 1:
        raise ValueError('acceptance contract version must be 1')
    criteria = payload.get('criteria')
    if not isinstance(criteria, list) or not criteria:
        raise ValueError('acceptance criteria must be a nonempty list')
    runtime = load_adapter_runtime(root)
    policy = runtime.data.get('qa_policy', {})
    if not isinstance(policy, dict):
        raise ValueError('qa_policy must be an object')
    allowed = policy.get('acceptance_command_keys', ['qa_verify'])
    if not isinstance(allowed, list) or not allowed or not all(isinstance(k, str) and k for k in allowed):
        raise ValueError('qa_policy.acceptance_command_keys must designate project acceptance commands')
    normalized = []
    ids = set()
    command_keys = set()
    for item in criteria:
        if not isinstance(item, dict):
            raise ValueError('acceptance criterion must be an object')
        identifier = item.get('id')
        description = item.get('description')
        keys = item.get('command_keys')
        if not isinstance(identifier, str) or not re.fullmatch(r'[A-Za-z0-9_-]+', identifier) or identifier in ids:
            raise ValueError('acceptance IDs must be unique nonempty identifiers')
        if not isinstance(description, str) or not description.strip():
            raise ValueError(f'{identifier}: acceptance description is required')
        if not isinstance(keys, list) or not keys or not all(isinstance(k, str) and k for k in keys):
            raise ValueError(f'{identifier}: map this criterion to actual acceptance command_keys before QA')
        for key in keys:
            argv = runtime.commands().get(key)
            if key not in allowed:
                raise ValueError(f'{identifier}: {key} is not a designated acceptance command; infrastructure smoke cannot replace acceptance')
            if not isinstance(argv, list) or not argv or not all(isinstance(arg, str) and arg for arg in argv):
                raise ValueError(f'commands.{key}: configure actual project test argv before QA')
        ids.add(identifier)
        command_keys.update(keys)
        normalized.append({'id': identifier, 'description': description.strip(), 'command_keys': sorted(set(keys))})
    visible = visible_criteria(text)
    unmatched = list(normalized)
    for identifier, description in visible:
        match = next((item for item in unmatched if item['description'] == description.strip()
                      and (identifier is None or identifier == item['id'])), None)
        if match is None:
            raise ValueError('acceptance mapping omits or changes a frozen visible criterion: ' + description)
        unmatched.remove(match)
    if unmatched:
        raise ValueError('acceptance mapping contains criteria absent from frozen visible acceptance')
    normalized.sort(key=lambda c: c['id'])
    # QA/flow status and receipt paths may change after execution. Frozen task semantics may not.
    semantic_sections = {name: section(text, name).strip() for name in (
        'Goal', 'Allowed Files', 'Forbidden Files', 'Functional Non-goals',
        'User-visible Acceptance', 'Verification', 'Compact Requirement',
    )}
    canonical = json.dumps({'version': 1, 'criteria': normalized, 'task': semantic_sections},
                           sort_keys=True, ensure_ascii=False, separators=(',', ':'))
    return AcceptancePlan(relative, hashlib.sha256(canonical.encode()).hexdigest(), normalized, sorted(command_keys))


def qa_completion_check(root: Path, text: str, *, boundary: str | Path | None = None) -> tuple[bool, str]:
    valid, issue = qa_check(root, text)
    if not valid:
        return valid, issue
    try:
        refs = re.findall(r'^\s*-\s*Execution Receipt:\s*`?([^`\n]+)`?\s*$', text, re.M)
        receipts = [json.loads(repo_file(root, raw.strip()).read_text()) for raw in refs]
        explicit = field(text, 'Acceptance Boundary')
        first_binding = receipts[0].get('acceptance')
        if not isinstance(first_binding, dict):
            raise ValueError('execution-only receipt cannot complete acceptance; rerun qa_verify.py --boundary <task>')
        selected = str(boundary) if boundary is not None else explicit or first_binding.get('boundary_path')
        if not isinstance(selected, str) or not selected:
            raise ValueError('acceptance boundary is required')
        plan = load_acceptance(root, selected)
        if explicit and explicit != plan.boundary_path:
            raise ValueError('QA report references a different acceptance boundary')
        executed = set()
        for receipt in receipts:
            if receipt.get('schema_version') != 2 or receipt.get('acceptance') != plan.binding():
                raise ValueError('acceptance receipt is missing, belongs to another task or is stale; rerun bound verification')
            executed.update(run['command_key'] for run in receipt['runs'])
        missing = set(plan.command_keys) - executed
        if missing:
            raise ValueError('acceptance commands not executed: ' + ', '.join(sorted(missing)))
        return True, ''
    except (ValueError, TypeError, KeyError, OSError, RuntimeError) as exc:
        return False, str(exc)


def task_completion_check(root: Path, boundary: str | Path) -> tuple[bool, str]:
    """Verify current task evidence; stored done status alone is only a record."""
    try:
        path = repo_file(root, str(boundary))
        flow = section(path.read_text(encoding='utf-8'), 'GStack Required Flow')
        block = re.search(r'^- qa(?:-only)?:[^\n]*\n(.*?)(?=^- [a-z0-9/-]+:|\Z)', flow, re.M | re.S)
        if block is None:
            raise ValueError('task has no QA record')
        match = re.search(r'^[ \t]*evidence:[ \t]*(.*?)[ \t]*$', block[1], re.M)
        if match is None or not match[1].strip().strip('`'):
            raise ValueError('recorded QA completion has no evidence; verify acceptance before delivery')
        report = repo_file(root, match[1].strip().strip('`'))
        return qa_completion_check(root, report.read_text(encoding='utf-8'), boundary=path)
    except (ValueError, RuntimeError, OSError, TypeError) as exc:
        return False, str(exc)
