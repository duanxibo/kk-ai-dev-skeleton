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

# Compatibility fallback has no project-specific paths or data gates.
DEFAULT_RUNTIME: dict[str, Any] = {
    "version": 1,
    "name": DEFAULT_ADAPTER,
    "paths": {},
    "commands": {},
    "gates": {},
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


def _validate_payload(payload: dict[str, Any]) -> None:
    """Validate before normalization so malformed fields never become silent defaults."""
    for section in ("loop_runtime", "online_flow_protocol", "runtime_bundle", "authorization", "smoke_tests", "evidence_policy"):
        if section in payload and not isinstance(payload[section], dict):
            raise ValueError(f"{section}: expected object")
    if "version" in payload and (not isinstance(payload["version"], int) or isinstance(payload["version"], bool)):
        raise ValueError("version: expected integer")
    if "name" in payload and (not isinstance(payload["name"], str) or not payload["name"].strip()):
        raise ValueError("name: expected non-empty string")
    if "non_actions" in payload and (not isinstance(payload["non_actions"], list)
            or any(not isinstance(v, str) for v in payload["non_actions"])):
        raise ValueError("non_actions: expected list of strings")
    for section in ("paths", "commands", "gates"):
        if section in payload and not isinstance(payload[section], dict):
            raise ValueError(f"{section}: expected object")
    paths = payload.get("paths", {})
    for key, value in paths.items():
        if key in PATH_VALUE_KEYS or key == "collaboration_root" or key.endswith("_prefix"):
            if not isinstance(value, str):
                raise ValueError(f"paths.{key}: expected string")
            values = [value]
        elif key in PATH_LIST_KEYS or key.endswith("_prefixes"):
            if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
                raise ValueError(f"paths.{key}: expected list of strings")
            values = value
        else:
            continue
        for value in values:
            normalized = _normalize_repo_path(value)
            if (not normalized or normalized.startswith("/") or ":" in normalized
                    or ".." in normalized.split("/")):
                raise ValueError(f"paths.{key}: expected non-empty repository-relative path")
    for key, value in payload.get("commands", {}).items():
        if not isinstance(value, str) and not (
            isinstance(value, list) and value and all(isinstance(v, str) and v for v in value)
        ):
            raise ValueError(f"commands.{key}: expected command string or non-empty string list")
    policy = payload.get("qa_policy")
    if policy is not None:
        if not isinstance(policy, dict):
            raise ValueError("qa_policy: expected object")
        keys = policy.get("acceptance_command_keys")
        if not isinstance(keys, list) or not keys or any(not isinstance(k, str) or not k for k in keys):
            raise ValueError("qa_policy.acceptance_command_keys: expected nonempty command key list")
        for key in keys:
            if not isinstance(payload.get("commands", {}).get(key), list):
                raise ValueError(f"qa_policy.acceptance_command_keys: commands.{key} must be an argv array")
    rules = payload.get("gates", {}).get("data_access_status_requirements", [])
    if not isinstance(rules, list):
        raise ValueError("gates.data_access_status_requirements: expected list")
    for index, rule in enumerate(rules):
        field = f"gates.data_access_status_requirements[{index}]"
        if not isinstance(rule, dict):
            raise ValueError(f"{field}: expected object")
        for key in ("prefixes", "statuses"):
            value = rule.get(key)
            if not isinstance(value, list) or not value or any(
                not isinstance(v, str) or not v.strip() for v in value
            ):
                raise ValueError(f"{field}.{key}: expected non-empty list of strings")
        for prefix in rule["prefixes"]:
            normalized = _normalize_repo_path(prefix)
            if normalized.startswith("/") or ":" in normalized or ".." in normalized.split("/"):
                raise ValueError(f"{field}.prefixes: expected repository-relative paths")
        if not isinstance(rule.get("reason"), str) or not rule["reason"].strip():
            raise ValueError(f"{field}.reason: expected non-empty string")
    if "implementation_prefixes" not in paths:
        raise ValueError("paths.implementation_prefixes: required list (use [] for a metadata-only adapter)")


def _normalize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    paths = payload.setdefault("paths", {})
    if not isinstance(paths, dict):
        payload["paths"] = {}
        paths = payload["paths"]

    for key in PATH_LIST_KEYS:
        if key not in paths:
            continue
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
    strict: bool = True,
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
            _validate_payload(loaded)
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

