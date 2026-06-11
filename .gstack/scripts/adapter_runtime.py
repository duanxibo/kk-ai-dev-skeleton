#!/usr/bin/env python3
"""Load machine-readable project adapter runtime settings."""

from __future__ import annotations

import copy
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTER_ENV = "KK_ADAPTER"
ADAPTER_RUNTIME_ENV = "KK_ADAPTER_RUNTIME"
DEFAULT_ADAPTER = "default"

PATH_LIST_KEYS = {
    "implementation_prefixes",
    "spec_prefixes",
    "prototype_prefixes",
    "backend_implementation_prefixes",
    "backend_test_prefixes",
    "deprecated_backend_spec_prefixes",
    "data_access_trigger_prefixes",
    "frontend_hint_prefixes",
    "prototype_logic_evidence_prefixes",
}
PATH_VALUE_KEYS = {
    "backend_domain_spec_prefix",
    "boundary_prefix",
    "requirement_prefix",
    "review_prefix",
    "ceo_review_prefix",
    "eng_review_prefix",
    "qa_prefix",
    "design_prefix",
    "domain_spec_prefix",
}

DEFAULT_RUNTIME: dict[str, Any] = {
    "version": 1,
    "name": DEFAULT_ADAPTER,
    "paths": {
        "implementation_prefixes": [
            "app/backend/",
            "app/frontend/",
            "scripts/",
            "tests/",
            "fixtures/",
            "app/restricted-module/server/",
            "app/restricted-module/public/",
            "app/restricted-module/scripts/",
            "app/restricted-module/tests/",
            "app/restricted-module/fixtures/",
            "archive/baseline/example-baseline/app/",
            "archive/baseline/example-baseline/scripts/",
            "archive/baseline/example-baseline/templates/",
            "archive/baseline/example-baseline/seeds/",
        ],
        "spec_prefixes": [
            "docs/specs/",
            "app/restricted-module/docs/",
            "app/restricted-module/specs/",
            "archive/baseline/example-baseline/docs/",
        ],
        "prototype_prefixes": [
            "archive/baseline/example-baseline/app/",
            "archive/baseline/example-baseline/scripts/",
            "archive/baseline/example-baseline/templates/",
            "archive/baseline/example-baseline/seeds/",
        ],
        "backend_implementation_prefixes": [
            "app/backend/src/main/",
            "app/backend/pom.xml",
            "app/restricted-module/server/",
        ],
        "backend_test_prefixes": [
            "app/backend/src/test/",
            "tests/",
            "app/restricted-module/tests/",
        ],
        "backend_domain_spec_prefix": "docs/specs/",
        "deprecated_backend_spec_prefixes": [
            "docs/specs/archive/backend-legacy/",
        ],
        "boundary_prefix": ".gstack/task-boundaries/",
        "requirement_prefix": ".gstack/requirements/",
        "review_prefix": ".gstack/reviews/",
        "ceo_review_prefix": ".gstack/reviews/",
        "eng_review_prefix": ".gstack/reviews/",
        "qa_prefix": ".gstack/qa-reports/",
        "design_prefix": ".gstack/designs/",
        "domain_spec_prefix": "docs/specs/",
        "data_access_trigger_prefixes": [
            "app/backend/src/main/",
            "app/restricted-module/server/",
            "docs/specs/",
            "app/restricted-module/docs/",
            "app/restricted-module/specs/",
            "app/frontend/",
            "app/restricted-module/public/",
            ".gstack/templates/data-interface-design.template.md",
            ".gstack/knowledge/data-access/source-registry.md",
            ".gstack/knowledge/data-access/sources/",
            ".gstack/knowledge/data-access/sql-drafts/",
            ".gstack/knowledge/data-access/requirement-gaps/",
        ],
        "frontend_hint_prefixes": [
            "archive/baseline/example-baseline/app/",
            "app/frontend/",
            "app/restricted-module/public/",
        ],
        "prototype_logic_evidence_prefixes": [
            ".gstack/designs/",
            ".gstack/reviews/",
            ".gstack/knowledge/",
            ".gstack/knowledge/data-access/",
            "app/",
            "docs/specs/",
            "stack/",
            "archive/baseline/",
            "baseline/",
        ],
    },
    "commands": {
        "dev_stack_entry": "scripts/dev_stack.sh",
        "init_project": "scripts/init_project.py",
        "doctor": ["python3", ".gstack/scripts/gstack_doctor.py", "check"],
        "dashboard": ["python3", ".gstack/scripts/gstack_dashboard.py", "show"],
    },
    "gates": {
        "data_access_status_requirements": [
            {
                "prefixes": ["app/backend/src/main/", "app/restricted-module/server/"],
                "statuses": ["done", "blocked", "deferred"],
                "reason": "business data implementation paths require `data-access` done / blocked / deferred",
            },
            {
                "prefixes": [
                    "docs/specs/",
                    "app/restricted-module/docs/",
                    "app/restricted-module/specs/",
                ],
                "statuses": ["done", "not-required"],
                "reason": "interface/spec/data docs require `data-access` done or reasoned not-required",
            },
            {
                "prefixes": ["app/frontend/", "app/restricted-module/public/"],
                "statuses": ["done", "not-required", "blocked", "deferred"],
                "reason": "frontend data wiring requires `data-access` evidence or reasoned not-required",
            },
            {
                "prefixes": [".gstack/templates/data-interface-design.template.md"],
                "statuses": ["done", "planned"],
                "reason": "data-interface design changes require `data-access` done or planned",
            },
        ],
    },
}


@dataclass(frozen=True)
class AdapterRuntime:
    repo_root: Path
    adapter_name: str
    adapter_dir: Path
    runtime_file: Path
    data: dict[str, Any]
    warnings: tuple[str, ...]

    @property
    def exists(self) -> bool:
        return self.runtime_file.exists()

    def paths(self) -> dict[str, Any]:
        value = self.data.get("paths", {})
        return value if isinstance(value, dict) else {}

    def commands(self) -> dict[str, Any]:
        value = self.data.get("commands", {})
        return value if isinstance(value, dict) else {}

    def gates(self) -> dict[str, Any]:
        value = self.data.get("gates", {})
        return value if isinstance(value, dict) else {}

    def path_tuple(self, key: str, default: tuple[str, ...] = ()) -> tuple[str, ...]:
        value = self.paths().get(key)
        if value is None:
            return default
        if isinstance(value, list):
            return tuple(str(item) for item in value if str(item).strip())
        if isinstance(value, str) and value.strip():
            return (value.strip(),)
        return default

    def path_value(self, key: str, default: str = "") -> str:
        value = self.paths().get(key)
        if value is None:
            return default
        return str(value).strip()

    def command_value(self, key: str, default: Any = None) -> Any:
        return self.commands().get(key, default)

    def data_access_status_requirements(
        self,
    ) -> tuple[tuple[tuple[str, ...], set[str], str], ...]:
        raw_items = self.gates().get("data_access_status_requirements", [])
        if not isinstance(raw_items, list):
            return ()
        parsed: list[tuple[tuple[str, ...], set[str], str]] = []
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            prefixes = _string_tuple(item.get("prefixes"))
            statuses = set(_string_tuple(item.get("statuses")))
            reason = str(item.get("reason", "")).strip()
            if prefixes and statuses and reason:
                parsed.append((prefixes, statuses, reason))
        return tuple(parsed)


def _string_tuple(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, list):
        return tuple(str(item).strip() for item in value if str(item).strip())
    if isinstance(value, str) and value.strip():
        return (value.strip(),)
    return ()


def _normalize_repo_path(raw: str) -> str:
    value = raw.strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    return value


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    paths = payload.setdefault("paths", {})
    if not isinstance(paths, dict):
        payload["paths"] = {}
        paths = payload["paths"]

    for key in PATH_LIST_KEYS:
        paths[key] = [_normalize_repo_path(item) for item in _string_tuple(paths.get(key))]
    for key in PATH_VALUE_KEYS:
        if key in paths:
            paths[key] = _normalize_repo_path(str(paths.get(key, "")))

    gates = payload.setdefault("gates", {})
    if isinstance(gates, dict):
        for item in gates.get("data_access_status_requirements", []) or []:
            if isinstance(item, dict):
                item["prefixes"] = [
                    _normalize_repo_path(prefix) for prefix in _string_tuple(item.get("prefixes"))
                ]
                item["statuses"] = list(_string_tuple(item.get("statuses")))
    return payload


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def _adapter_dir(repo_root: Path, adapter: str | None) -> Path:
    raw = (adapter or os.environ.get(ADAPTER_ENV) or DEFAULT_ADAPTER).strip()
    if not raw:
        raw = DEFAULT_ADAPTER

    candidate = Path(raw)
    if candidate.is_absolute():
        return candidate if candidate.is_dir() else candidate.parent
    if raw.startswith("adapters/"):
        return repo_root / raw
    return repo_root / "adapters" / raw


def load_adapter_runtime(
    repo_root: Path = REPO_ROOT,
    adapter: str | None = None,
    *,
    strict: bool = False,
) -> AdapterRuntime:
    repo_root = repo_root.resolve()
    runtime_override = os.environ.get(ADAPTER_RUNTIME_ENV, "").strip()
    if runtime_override:
        runtime_file = (repo_root / runtime_override).resolve()
        if Path(runtime_override).is_absolute():
            runtime_file = Path(runtime_override).resolve()
        adapter_dir = runtime_file.parent
    else:
        adapter_dir = _adapter_dir(repo_root, adapter).resolve()
        runtime_file = adapter_dir / "runtime.json"

    warnings: list[str] = []
    payload = copy.deepcopy(DEFAULT_RUNTIME)
    if runtime_file.exists():
        try:
            loaded = json.loads(runtime_file.read_text(encoding="utf-8"))
            if not isinstance(loaded, dict):
                raise ValueError("runtime root must be a JSON object")
            payload = _deep_merge(payload, loaded)
        except (OSError, json.JSONDecodeError, ValueError) as exc:
            message = f"adapter runtime invalid: {runtime_file}: {exc}"
            if strict:
                raise RuntimeError(message) from exc
            warnings.append(message)
    else:
        message = f"adapter runtime missing: {runtime_file}"
        if strict:
            raise RuntimeError(message)
        warnings.append(message)

    payload = _normalize_payload(payload)
    name = str(payload.get("name") or adapter_dir.name or DEFAULT_ADAPTER)
    return AdapterRuntime(
        repo_root=repo_root,
        adapter_name=name,
        adapter_dir=adapter_dir,
        runtime_file=runtime_file,
        data=payload,
        warnings=tuple(warnings),
    )

