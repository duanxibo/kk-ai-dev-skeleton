#!/usr/bin/env python3
"""Guard the fixed KK Dev Skeleton gstack command sequence."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from adapter_runtime import load_adapter_runtime

try:
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:  # Python < 3.11
    tomllib = None

TOML_DECODE_ERROR = tomllib.TOMLDecodeError if tomllib is not None else ValueError


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = ".gstack/workflows/team-development-flow.toml"
LOCAL_CURRENT_BOUNDARY_FILE = ".gstack/task-boundaries/CURRENT.local.md"
CURRENT_BOUNDARY_FILE = ".gstack/task-boundaries/CURRENT.md"
ACTIVE_BOUNDARY_ENV = "KK_ACTIVE_BOUNDARY"
BOUNDARY_LINK_RE = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<href>[^)]+)\)")
SUBAGENT_MODE_RE = re.compile(
    r"^\s*-\s*Mode:\s*`?(not-used|explore|review|execute|governance|mixed)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
DECISION_MODE_RE = re.compile(
    r"^\s*-\s*Mode:\s*`?(自主执行(?:模式)?|关键确认(?:模式)?|手动控制(?:模式)?|codex-led|checkpoint|manual)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
FLOW_LANE_RE = re.compile(
    r"^\s*-\s*Lane:\s*`?(fast-lane|standard|discovery)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
FAST_LANE_RE = re.compile(
    r"^\s*-\s*Lane:\s*`?fast-lane`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
GOAL_MODE_RE = re.compile(
    r"^\s*-\s*Goal Mode:\s*`?(enabled|not-used|ask-first)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
FAST_LANE_DRAFT_RE = re.compile(
    r"(draft-needs-codex-review|待\s*Codex\s*语义复核|pending-review|AI\s*语义复核\s*[：:]\s*`?(?:no|yes\s*/\s*no)`?)",
    re.IGNORECASE,
)
AI_REVIEWED_YES_RE = re.compile(
    r"AI\s*语义复核\s*[：:]\s*`?yes`?\s*(?:\r?\n|$)",
    re.IGNORECASE,
)
FAST_LANE_AI_REVIEWED_COMMANDS = (
    "requirement-brief",
    "requirement-freeze",
    "plan-ceo-review",
    "plan-eng-review",
)
USER_VISIBLE_YES_RE = re.compile(
    r"User-visible Change\s*:\s*`?(yes|是)`?",
    re.IGNORECASE,
)
USER_VISIBLE_SURFACE_RE = re.compile(
    r"Surface Type\s*:\s*`?(static-generated-html|dev-server-page|production-page)`?",
    re.IGNORECASE,
)
QA_INTERACTION_EVIDENCE_RE = re.compile(
    r"\b(Browser|Chrome|Playwright|local HTTP server|本地 HTTP server|http://127\.0\.0\.1|http://localhost)\b",
    re.IGNORECASE,
)
QA_BLOCKED_PARTIAL_RE = re.compile(
    r"\b(blocked|partial|阻断|部分|无法验收|无法完成|blocked / partial reason)\b",
    re.IGNORECASE,
)


def run_git(args: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {' '.join(args)} failed")
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def strip_comment(line: str) -> str:
    in_quote = False
    result: list[str] = []
    for char in line:
        if char == '"':
            in_quote = not in_quote
        if char == "#" and not in_quote:
            break
        result.append(char)
    return "".join(result).strip()


def parse_toml_value(raw: str) -> Any:
    value = raw.strip().rstrip(",").strip()
    if value in {"true", "false"}:
        return value == "true"
    if re.fullmatch(r"\d+", value):
        return int(value)
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_toml_value(item.strip()) for item in inner.split(",") if item.strip()]
    return value


def parse_toml_fallback(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    current: dict[str, Any] = root
    lines = text.splitlines()
    index = 0
    while index < len(lines):
        line = strip_comment(lines[index])
        index += 1
        if not line:
            continue
        if line.startswith("[") and line.endswith("]"):
            current = root
            for part in line[1:-1].split("."):
                current = current.setdefault(part, {})
            continue
        if "=" not in line:
            continue
        key, raw_value = [part.strip() for part in line.split("=", 1)]
        if raw_value.startswith("[") and not raw_value.endswith("]"):
            parts = [raw_value]
            while index < len(lines):
                next_line = strip_comment(lines[index])
                index += 1
                if next_line:
                    parts.append(next_line)
                if next_line.endswith("]"):
                    break
            raw_value = " ".join(parts)
        current[key] = parse_toml_value(raw_value)
    return root


def load_config(path: str) -> dict[str, Any]:
    text = (REPO_ROOT / path).read_text(encoding="utf-8")
    if tomllib is not None:
        return tomllib.loads(text)
    return parse_toml_fallback(text)


def apply_adapter_runtime(config: dict[str, Any]) -> dict[str, Any]:
    runtime = load_adapter_runtime(REPO_ROOT)
    paths_config = config.setdefault("paths", {})
    if not isinstance(paths_config, dict):
        paths_config = {}
        config["paths"] = paths_config

    runtime_path_mapping = {
        "implementation_prefixes": runtime.path_tuple("implementation_prefixes"),
        "prototype_prefixes": runtime.path_tuple("prototype_prefixes"),
        "stack_backend_prefixes": runtime.path_tuple("backend_implementation_prefixes"),
        "backend_test_prefixes": runtime.path_tuple("backend_test_prefixes"),
        "deprecated_backend_spec_prefixes": runtime.path_tuple("deprecated_backend_spec_prefixes"),
    }
    for key, value in runtime_path_mapping.items():
        if value:
            paths_config[key] = list(value)

    backend_spec_prefix = runtime.path_value("backend_domain_spec_prefix")
    if backend_spec_prefix:
        paths_config["backend_domain_spec_prefix"] = backend_spec_prefix
    boundary_prefix = runtime.path_value("boundary_prefix")
    if boundary_prefix:
        paths_config["boundary_prefix"] = boundary_prefix
    domain_spec_prefix = runtime.path_value("domain_spec_prefix")
    if domain_spec_prefix:
        paths_config["domain_spec_prefix"] = domain_spec_prefix

    commands = config.setdefault("commands", {})
    if (
        isinstance(commands, dict)
        and "domain-spec-readiness" in commands
        and isinstance(commands["domain-spec-readiness"], dict)
    ):
        spec_prefixes = runtime.path_tuple("spec_prefixes")
        if spec_prefixes:
            commands["domain-spec-readiness"]["evidence_prefixes"] = list(spec_prefixes)
    return config


def has_prefix(path: str, prefixes: list[str]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def sample_paths(paths: list[str], limit: int = 10) -> list[str]:
    if len(paths) <= limit:
        return paths
    return [*paths[:limit], f"... {len(paths) - limit} more"]


def staged_files() -> list[str]:
    return run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMR", "--"])


def changed_files(base_ref: str) -> list[str]:
    tracked = run_git(["diff", "--name-only", base_ref, "--"])
    untracked = run_git(["ls-files", "--others", "--exclude-standard"])
    return sorted(set(tracked + untracked))


def inside_git_worktree() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def resolve_boundary_reference(
    raw_ref: str, source_label: str, boundary_prefix: str
) -> tuple[str | None, str | None]:
    raw_ref = raw_ref.strip()
    if not raw_ref:
        return None, f"{source_label} is empty."

    raw_path = Path(raw_ref)
    if raw_path.is_absolute():
        target = raw_path.resolve()
    else:
        repo_candidate = (REPO_ROOT / raw_path).resolve()
        boundary_candidate = (REPO_ROOT / boundary_prefix / raw_path).resolve()
        target = repo_candidate if repo_candidate.exists() else boundary_candidate

    try:
        relative = target.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return None, f"{source_label} points outside the repo."

    if not relative.startswith(boundary_prefix):
        return None, f"{source_label} must point under `{boundary_prefix}`."
    if relative.endswith("CURRENT.md") or relative.endswith("CURRENT.local.md"):
        return None, f"{source_label} must point to a concrete boundary file."
    if not (REPO_ROOT / relative).exists():
        return None, f"{source_label} points to a missing boundary file: `{relative}`."
    return relative, None


def parse_boundary_pointer_file(
    path: str, boundary_prefix: str
) -> tuple[str | None, str | None]:
    file_path = REPO_ROOT / path
    if not file_path.exists():
        return None, None

    active_links: list[str] = []
    in_active_section = False
    for line in file_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "## Active Boundary":
            in_active_section = True
            continue
        if in_active_section and stripped.startswith("## "):
            break
        if not in_active_section:
            continue
        match = BOUNDARY_LINK_RE.search(stripped)
        if match:
            active_links.append(match.group("href"))

    if not active_links:
        return None, None
    if len(active_links) > 1:
        joined = ", ".join(active_links)
        return None, f"`{path}` declares multiple active boundaries: {joined}."

    href_path = (Path(path).parent / active_links[0]).as_posix()
    return resolve_boundary_reference(href_path, f"`{path}` Active Boundary", boundary_prefix)


def resolve_active_boundary(boundary_prefix: str) -> tuple[str | None, str | None, str | None]:
    env_value = os.environ.get(ACTIVE_BOUNDARY_ENV, "").strip()
    if env_value:
        boundary, error = resolve_boundary_reference(
            env_value, f"Environment variable `{ACTIVE_BOUNDARY_ENV}`", boundary_prefix
        )
        return boundary, f"env:{ACTIVE_BOUNDARY_ENV}", error

    boundary, error = parse_boundary_pointer_file(LOCAL_CURRENT_BOUNDARY_FILE, boundary_prefix)
    if boundary or error:
        return boundary, LOCAL_CURRENT_BOUNDARY_FILE, error

    boundary, error = parse_boundary_pointer_file(CURRENT_BOUNDARY_FILE, boundary_prefix)
    if boundary or error:
        return boundary, CURRENT_BOUNDARY_FILE, error

    return None, None, None


def section_lines(text: str, header: str) -> list[str]:
    lines = text.splitlines()
    result: list[str] = []
    in_section = False
    for line in lines:
        if line.strip() == f"## {header}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            result.append(line.rstrip())
    return result


def clean(raw: str) -> str:
    return raw.strip().strip("`").strip()


def parse_required_flow(text: str) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    current: str | None = None
    inline_re = re.compile(r"^\s*-\s*(?P<name>[a-z0-9/-]+):\s*(?P<value>.*?)\s*$", re.I)
    field_re = re.compile(r"^\s*(?P<key>status|command|evidence|note):\s*(?P<value>.*?)\s*$", re.I)

    for line in section_lines(text, "GStack Required Flow"):
        inline_match = inline_re.match(line)
        if inline_match:
            current = inline_match.group("name")
            records.setdefault(current, {})
            inline_value = clean(inline_match.group("value"))
            if inline_value:
                records[current]["status"] = inline_value
            continue

        if current is None:
            continue

        field_match = field_re.match(line)
        if field_match:
            records[current][field_match.group("key").lower()] = clean(field_match.group("value"))
            continue

        evidence_match = re.match(r"^\s*-\s*(?P<value>`?[^`]+`?)\s*$", line)
        if evidence_match and "evidence" not in records[current]:
            records[current]["evidence"] = clean(evidence_match.group("value"))

    return records


def evidence_ok(command: str, record: dict[str, str], config: dict[str, Any]) -> tuple[bool, str | None]:
    evidence = record.get("evidence", "")
    if not evidence:
        return False, "missing evidence path"

    evidence = evidence.split()[0].strip().strip("`")
    command_config = config["commands"].get(command, {})
    allowed_prefixes = command_config.get("evidence_prefixes", [])
    if allowed_prefixes and not has_prefix(evidence, allowed_prefixes):
        return False, f"evidence `{evidence}` is outside allowed prefixes: {', '.join(allowed_prefixes)}"

    for needle in command_config.get("filename_contains", []):
        if needle not in Path(evidence).name:
            return False, f"evidence filename must contain `{needle}`"

    if not (REPO_ROOT / evidence).exists():
        return False, f"evidence file missing: `{evidence}`"
    return True, None


def evidence_path(record: dict[str, str]) -> str:
    return record.get("evidence", "").split()[0].strip().strip("`")


def command_candidates(command: str, config: dict[str, Any], *, allow_qa_only: bool) -> list[str]:
    candidates = [command]
    alternatives = config.get("command_alternatives", {}).get(command, [])
    candidates.extend(as_list(alternatives))
    if command == "qa" and allow_qa_only and "qa-only" not in candidates:
        candidates.append("qa-only")
    return candidates


def get_command_record(
    records: dict[str, dict[str, str]],
    command: str,
    config: dict[str, Any],
    *,
    allow_qa_only: bool,
) -> tuple[str | None, dict[str, str] | None]:
    for candidate in command_candidates(command, config, allow_qa_only=allow_qa_only):
        record = records.get(candidate)
        if record:
            return candidate, record
    return None, None


def command_status_satisfies(
    records: dict[str, dict[str, str]],
    command: str,
    config: dict[str, Any],
) -> bool:
    for candidate in command_candidates(command, config, allow_qa_only=True):
        status = records.get(candidate, {}).get("status", "")
        if status in {"done", "not-required"}:
            return True
    return False


def command_marked_done(
    records: dict[str, dict[str, str]],
    command: str,
    config: dict[str, Any],
) -> bool:
    return any(
        records.get(candidate, {}).get("status", "") == "done"
        for candidate in command_candidates(command, config, allow_qa_only=True)
    )


def validate_flow_order(records: dict[str, dict[str, str]], config: dict[str, Any]) -> list[str]:
    failures: list[str] = []
    sequence = as_list(config.get("required_sequence", []))
    for index, command in enumerate(sequence):
        if not command_marked_done(records, command, config):
            continue
        for previous in sequence[:index]:
            if command_status_satisfies(records, previous, config):
                continue
            failures.append(
                f"`{command}` is marked `done`, but previous required stage `{previous}` is not done."
            )
    return failures


def validate_subagent_plan(text: str, boundary: str) -> list[str]:
    lines = [line.strip() for line in section_lines(text, "Subagent Plan") if line.strip()]
    if not lines:
        return [f"Active boundary `{boundary}` is missing `## Subagent Plan`."]
    joined = "\n".join(lines)
    if not SUBAGENT_MODE_RE.search(joined):
        return [
            f"Active boundary `{boundary}` must declare a subagent mode with `- Mode: not-used|explore|review|execute|governance|mixed`."
        ]
    return []


def validate_decision_mode(text: str, boundary: str) -> list[str]:
    failures: list[str] = []
    decision_lines = [line.strip() for line in section_lines(text, "Decision Mode") if line.strip()]
    if not decision_lines:
        failures.append(f"Active boundary `{boundary}` is missing `## Decision Mode`.")
    elif not DECISION_MODE_RE.search("\n".join(decision_lines)):
        failures.append(
            f"Active boundary `{boundary}` must declare a decision mode with `- Mode: 自主执行|关键确认|手动控制`."
        )

    lane_lines = [line.strip() for line in section_lines(text, "Flow Lane") if line.strip()]
    if not lane_lines:
        failures.append(f"Active boundary `{boundary}` is missing `## Flow Lane`.")
    elif not FLOW_LANE_RE.search("\n".join(lane_lines)):
        failures.append(
            f"Active boundary `{boundary}` must declare a flow lane with `- Lane: fast-lane|standard|discovery`."
        )

    autonomy_lines = [line.strip() for line in section_lines(text, "Autonomy Plan") if line.strip()]
    if not autonomy_lines:
        failures.append(f"Active boundary `{boundary}` is missing `## Autonomy Plan`.")
    elif not GOAL_MODE_RE.search("\n".join(autonomy_lines)):
        failures.append(
            f"Active boundary `{boundary}` must declare goal mode with `- Goal Mode: enabled|not-used|ask-first`."
        )
    return failures


def is_fast_lane(text: str) -> bool:
    lane_lines = [line.strip() for line in section_lines(text, "Flow Lane") if line.strip()]
    return bool(FAST_LANE_RE.search("\n".join(lane_lines)))


def fast_lane_evidence_issue(text: str) -> str | None:
    if FAST_LANE_DRAFT_RE.search(text):
        return "contains draft markers such as `draft-needs-codex-review`, `AI 语义复核: no`, or `pending-review`"
    if not AI_REVIEWED_YES_RE.search(text):
        return "is missing `AI 语义复核: yes`"
    return None


def validate_fast_lane_ai_review(
    boundary_text: str,
    records: dict[str, dict[str, str]],
    config: dict[str, Any],
    boundary: str,
) -> list[str]:
    if not is_fast_lane(boundary_text):
        return []

    failures: list[str] = []
    if FAST_LANE_DRAFT_RE.search(boundary_text):
        failures.append(
            f"Active boundary `{boundary}` is fast-lane but still contains draft markers. "
            "Run Codex semantic review first, or regenerate the evidence with `autopilot_bootstrap.py --ai-reviewed`."
        )

    checked_paths: set[str] = set()
    for command in FAST_LANE_AI_REVIEWED_COMMANDS:
        _record_name, record = get_command_record(
            records,
            command,
            config,
            allow_qa_only=True,
        )
        if not record or record.get("status", "") != "done":
            continue

        path = evidence_path(record)
        if not path or path in checked_paths:
            continue
        checked_paths.add(path)

        file_path = REPO_ROOT / path
        if not file_path.exists() or file_path.suffix.lower() not in {".md", ".txt"}:
            continue

        issue = fast_lane_evidence_issue(file_path.read_text(encoding="utf-8"))
        if issue:
            failures.append(
                f"Fast-lane evidence `{path}` for `{command}` {issue}. "
                "Draft evidence cannot satisfy review/freeze gates before implementation."
            )

    return failures


def boundary_requires_user_visible_interaction(text: str) -> bool:
    return bool(USER_VISIBLE_YES_RE.search(text) or USER_VISIBLE_SURFACE_RE.search(text))


def validate_user_visible_qa_evidence(
    boundary_text: str,
    records: dict[str, dict[str, str]],
    config: dict[str, Any],
    boundary: str,
) -> list[str]:
    if not boundary_requires_user_visible_interaction(boundary_text):
        return []

    _record_name, record = get_command_record(
        records,
        "qa",
        config,
        allow_qa_only=True,
    )
    if not record or record.get("status", "") != "done":
        return []

    path = evidence_path(record)
    if not path:
        return [
            f"Active boundary `{boundary}` declares user-visible UI/HTML acceptance and marks QA done, but QA evidence path is missing."
        ]
    file_path = REPO_ROOT / path
    if not file_path.exists():
        return [
            f"Active boundary `{boundary}` declares user-visible UI/HTML acceptance and marks QA done, but QA evidence file is missing: `{path}`."
        ]
    text = file_path.read_text(encoding="utf-8")
    if QA_INTERACTION_EVIDENCE_RE.search(text) or QA_BLOCKED_PARTIAL_RE.search(text):
        return []
    return [
        f"Active boundary `{boundary}` declares user-visible UI/HTML acceptance and marks QA done, but `{path}` has no Browser / Chrome / Playwright / local HTTP server interaction evidence or explicit blocked / partial reason."
    ]


def required_gate_block(text: str, gate_id: str) -> str | None:
    lines = text.splitlines()
    in_required_gates = False
    in_target_gate = False
    block: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == "## Required Gates":
            in_required_gates = True
            continue
        if in_required_gates and stripped.startswith("## "):
            break
        if not in_required_gates:
            continue
        if stripped.startswith("- gate_id:"):
            if in_target_gate:
                break
            in_target_gate = stripped == f"- gate_id: {gate_id}"
        if in_target_gate:
            block.append(stripped)
    if not block:
        return None
    return "\n".join(block)


def validate_required_gates_presence(text: str, boundary: str) -> list[str]:
    if "## Required Gates" not in text or "required_gates:" not in text:
        return [
            f"Active boundary `{boundary}` has no parsable `Required Gates` block. "
            "Initial rollout is warning-only; add it from `.gstack/templates/task-boundary.template.md`."
        ]
    warnings: list[str] = []
    if "gate_id: data-access" not in text:
        warnings.append(
            f"Active boundary `{boundary}` has no `data-access` gate. "
            "If data is not involved, mark it `not-required` with a trigger_reason."
        )
    prototype_gate = required_gate_block(text, "prototype-logic-extraction")
    if prototype_gate is None:
        warnings.append(
            f"Active boundary `{boundary}` has no `prototype-logic-extraction` gate. "
            "If frontend/prototype logic is not involved, mark it `not-required` with a trigger_reason."
        )
        return warnings
    if "owner: kk-task-kickoff" not in prototype_gate:
        warnings.append(
            f"Active boundary `{boundary}` prototype-logic-extraction gate should use `owner: kk-task-kickoff`."
        )
    if "required_before: plan-eng-review" not in prototype_gate:
        warnings.append(
            f"Active boundary `{boundary}` prototype-logic-extraction gate should use `required_before: plan-eng-review`."
        )
    return warnings


def validate_commands(
    records: dict[str, dict[str, str]],
    required: list[str],
    config: dict[str, Any],
    *,
    allow_qa_only: bool,
) -> list[str]:
    failures: list[str] = []
    for command in required:
        record_name, record = get_command_record(
            records,
            command,
            config,
            allow_qa_only=allow_qa_only,
        )
        if not record:
            candidates = command_candidates(command, config, allow_qa_only=allow_qa_only)
            candidate_text = "` or `".join(candidates)
            failures.append(f"Missing required gstack command record: `{candidate_text}`.")
            continue

        status = record.get("status", "")
        required_status = config["commands"].get(command, {}).get("required_status", "done")
        if status != required_status:
            failures.append(
                f"Required command `{command}` must be `{required_status}`, got `{status or 'missing'}`."
            )
            continue

        evidence_valid, evidence_error = evidence_ok(command, record, config)
        if not evidence_valid:
            failures.append(
                f"Required command `{record_name or command}` has invalid evidence: {evidence_error}."
            )
    return failures


def append_unique(items: list[str], item: str) -> None:
    if item not in items:
        items.append(item)


def stage_next_steps(stage: str) -> list[str]:
    stage_steps = {
        "requirement-brief": [
            "补需求描述：按 `.gstack/templates/requirement-brief.template.md` 新建 `.gstack/requirements/YYYY-MM-DD_<topic>-requirement-brief.md`。",
            "把 active boundary 的 `GStack Required Flow` 中 `requirement-brief` 改为 `status: done`，并把 evidence 指向这份 brief。",
        ],
        "plan-ceo-review": [
            "基于 requirement brief 执行 `/plan-ceo-review`，把结论沉淀到 `.gstack/reviews/` 或 `.gstack/designs/`。",
            "在 active boundary 中把 `plan-ceo-review` 标为 `done`，evidence 指向对应 review 文档。",
        ],
        "requirement-freeze": [
            "补需求冻结或原型冻结：按 `.gstack/templates/requirement-freeze.template.md` 新建 `.gstack/requirements/YYYY-MM-DD_<topic>-requirement-freeze.md`，或补 `prototype-freeze` 记录。",
            "在 active boundary 中登记 `requirement-freeze` 或 `prototype-freeze` 的 `status: done` 和 evidence。",
        ],
        "prototype-freeze": [
            "补原型冻结：按 `.gstack/templates/requirement-freeze.template.md` 新建 `.gstack/requirements/YYYY-MM-DD_<topic>-prototype-freeze.md`，或引用已冻结的 `archive/baseline/example-baseline/docs/` 文档。",
            "在 active boundary 中登记 `prototype-freeze` 的 `status: done` 和 evidence。",
        ],
        "plan-eng-review": [
            "执行 `/plan-eng-review`，重点确认接口、数据模型、状态、测试和风险。",
            "把评审结论沉淀到 `.gstack/reviews/`，并在 active boundary 中登记 evidence。",
        ],
        "domain-spec-readiness": [
            "补 domain spec readiness：更新 `docs/specs/<module>/` 下的需求、数据、接口、前端、后端或测试口径。",
            "在 active boundary 中把 `domain-spec-readiness` 标为 `done`，evidence 指向对应 domain spec 文件。",
        ],
        "implement": [
            "实现完成后更新 active boundary：把 `implement` 标为 `done`，evidence 指向本次具体 boundary。",
        ],
        "qa": [
            "运行 `/qa-only` 或 `/qa`，把结果保存到 `.gstack/qa-reports/`。",
            "在 active boundary 中把 `qa` 标为 `done`，`command` 写 `qa` 或 `qa-only`，evidence 指向 QA 报告。",
        ],
        "qa-only": [
            "运行 `/qa-only`，把结果保存到 `.gstack/qa-reports/`。",
            "在 active boundary 中把 `qa` 或 `qa-only` 标为 `done`，evidence 指向 QA 报告。",
        ],
    }
    return stage_steps.get(stage, [])


def print_next_steps(
    failures: list[str],
    *,
    mode: str,
    config: dict[str, Any],
    boundary: str | None,
    flow_files: list[str],
    prototype_files: list[str],
    stack_backend_files: list[str],
    backend_test_files: list[str],
    backend_domain_spec_files: list[str],
    deprecated_backend_spec_files: list[str],
) -> None:
    steps: list[str] = []
    text = "\n".join(failures)

    if "active task boundary" in text or "active boundary" in text:
        append_unique(
            steps,
            "先确定当前任务边界：运行 `$kk-task-kickoff`，或执行 `bash .gstack/scripts/use_boundary.sh .gstack/task-boundaries/<your-boundary>.md`。",
        )

    if "missing `## GStack Required Flow`" in text or "GStack Required Flow" in text:
        append_unique(
            steps,
            "补齐 active boundary 的 `## GStack Required Flow`，可参考 `.gstack/templates/task-boundary.template.md`。",
        )
    if "Subagent Plan" in text or "subagent mode" in text:
        append_unique(
            steps,
            "补 `## Subagent Plan`：小任务可写 `- Mode: not-used` 并说明原因；复杂任务先用 `$kk-subagent-orchestrator` 拆分读/评审/执行/治理 agent。",
        )
    if "Decision Mode" in text or "decision mode" in text:
        append_unique(
            steps,
            "补 `## Decision Mode`：写 `- Mode: 自主执行|关键确认|手动控制`，并说明来源、内部枚举和原因。",
        )
    if "Flow Lane" in text or "flow lane" in text:
        append_unique(
            steps,
            "补 `## Flow Lane`：写 `- Lane: fast-lane|standard|discovery`；小需求 fast-lane 还要补 fast-lane requirement / review evidence。",
        )
    if "Autonomy Plan" in text or "Goal Mode" in text or "goal mode" in text:
        append_unique(
            steps,
            "补 `## Autonomy Plan`：写 Codex 可自动做什么、必须问什么，以及 `- Goal Mode: enabled|not-used|ask-first`。",
        )
    if "Fast-lane evidence" in text or "fast-lane but still contains draft markers" in text:
        append_unique(
            steps,
            "fast-lane evidence 仍是 draft：由 Codex 读取上下文完成语义复核后，补 `AI 语义复核: yes`，或用 `python3 .gstack/scripts/autopilot_bootstrap.py ... --ai-reviewed --activate` 重新生成。",
        )

    mentioned_stages = set(re.findall(r"`([a-z0-9/-]+)`", text))
    if prototype_files and "domain-spec-readiness" not in mentioned_stages:
        mentioned_stages.add("domain-spec-readiness")
    for stage in config.get("required_sequence", []):
        if stage in mentioned_stages:
            for item in stage_next_steps(stage):
                append_unique(steps, item)
    for stage in ("prototype-freeze", "qa-only"):
        if stage in mentioned_stages:
            for item in stage_next_steps(stage):
                append_unique(steps, item)

    if stack_backend_files and not backend_test_files:
        append_unique(
            steps,
            "后端实现改动需要补测试：新增或更新 `app/backend/src/test/` 或 `tests/` 下的测试。",
        )
    if stack_backend_files and not backend_domain_spec_files:
        append_unique(
            steps,
            "后端实现改动需要补规范：在 `docs/specs/<module>/` 下更新 `backend.md`、`data.md` 或 `testing.md`。",
        )
    if deprecated_backend_spec_files:
        append_unique(
            steps,
            "不要继续写旧后端目录；把新内容迁到 `docs/specs/<module>/`，旧 `04_后端设计/` 只保留作冻结参考。",
        )

    if "invalid evidence" in text or "evidence file missing" in text:
        append_unique(
            steps,
            "检查 evidence 路径是否写错、文件是否已经创建，并确保路径使用 repo-relative 格式。",
        )

    if boundary:
        append_unique(steps, f"修正后更新 active boundary：`{boundary}`。")
    elif flow_files:
        append_unique(steps, "修正后让 active boundary 指向本次具体 boundary，而不是 `CURRENT.md`。")

    rerun = (
        "python3 .gstack/scripts/team_flow_guard.py --mode pre-commit"
        if mode == "pre-commit"
        else "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD"
    )
    append_unique(steps, f"修完后重跑：`{rerun}`。")

    print("\n[gstack-flow] 下一步建议:")
    for index, step in enumerate(steps, start=1):
        print(f"  {index}. {step}")


def run_static_boundary_audit(config: dict[str, Any]) -> int:
    paths_config = config.get("paths", {})
    boundary_prefix = str(paths_config.get("boundary_prefix", ".gstack/task-boundaries/"))
    boundary, boundary_source, boundary_error = resolve_active_boundary(boundary_prefix)
    failures: list[str] = []
    warnings: list[str] = []

    print("[gstack-flow] git state: not a git worktree; running static boundary audit")
    print(f"[gstack-flow] required sequence: {' -> '.join(config['required_sequence'])}")
    print(f"[gstack-flow] active boundary: {boundary or 'unresolved'}")
    print(f"[gstack-flow] active boundary source: {boundary_source or 'none'}")

    if boundary_error:
        failures.append(boundary_error)
    if not boundary:
        warnings.append(
            "No active boundary is set. Create one with `kk-task-kickoff` before implementation."
        )
    else:
        boundary_text = (REPO_ROOT / boundary).read_text(encoding="utf-8")
        records = parse_required_flow(boundary_text)
        if not records:
            failures.append(f"Active boundary `{boundary}` is missing `## GStack Required Flow`.")
        failures.extend(validate_decision_mode(boundary_text, boundary))
        failures.extend(validate_subagent_plan(boundary_text, boundary))
        failures.extend(validate_fast_lane_ai_review(boundary_text, records, config, boundary))
        failures.extend(validate_user_visible_qa_evidence(boundary_text, records, config, boundary))
        warnings.extend(validate_required_gates_presence(boundary_text, boundary))
        failures.extend(validate_flow_order(records, config))

    if failures:
        print("\n[gstack-flow] FAIL:")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    if warnings:
        print("\n[gstack-flow] PASS WITH WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
        return 0

    print("\n[gstack-flow] PASS: static required gstack command chain is satisfied.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Check the fixed KK Dev Skeleton gstack command chain.")
    parser.add_argument("--mode", choices=("pre-commit", "pre-push", "audit"), default="audit")
    parser.add_argument("--base", default="HEAD", help="Base ref for pre-push/audit diff.")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    args = parser.parse_args()

    try:
        config = apply_adapter_runtime(load_config(args.config))
        if not inside_git_worktree():
            return run_static_boundary_audit(config)
        files = staged_files() if args.mode == "pre-commit" else changed_files(args.base)
    except (RuntimeError, OSError, TOML_DECODE_ERROR) as exc:
        print(f"[gstack-flow] failed to inspect flow state: {exc}", file=sys.stderr)
        return 2

    paths_config = config.get("paths", {})
    implementation_prefixes = as_list(paths_config.get("implementation_prefixes"))
    prototype_prefixes = as_list(paths_config.get("prototype_prefixes"))
    stack_backend_prefixes = as_list(paths_config.get("stack_backend_prefixes"))
    backend_test_prefixes = as_list(paths_config.get("backend_test_prefixes"))
    backend_domain_spec_prefix = str(paths_config.get("backend_domain_spec_prefix", ""))
    deprecated_backend_spec_prefixes = as_list(paths_config.get("deprecated_backend_spec_prefixes"))

    implementation_files = [
        path
        for path in files
        if has_prefix(path, implementation_prefixes) and not path.endswith(".md")
    ]
    prototype_files = [
        path
        for path in files
        if has_prefix(path, prototype_prefixes) and not path.endswith(".md")
    ]
    stack_backend_files = [
        path
        for path in files
        if has_prefix(path, stack_backend_prefixes) and not path.endswith(".md")
    ]
    backend_test_files = [
        path
        for path in files
        if has_prefix(path, backend_test_prefixes) and not path.endswith(".md")
    ]
    backend_domain_spec_files = [
        path
        for path in files
        if backend_domain_spec_prefix
        and path.startswith(backend_domain_spec_prefix)
        and path.endswith(".md")
    ]
    deprecated_backend_spec_files = [
        path
        for path in files
        if has_prefix(path, deprecated_backend_spec_prefixes)
    ]

    controlled_files = (
        implementation_files
        + prototype_files
        + stack_backend_files
        + deprecated_backend_spec_files
    )
    if not controlled_files:
        print(f"[gstack-flow] PASS: no flow-controlled files in {args.mode} scope.")
        return 0

    failures: list[str] = []
    warnings: list[str] = []

    if deprecated_backend_spec_files:
        failures.append(
            "The legacy backend spec directory `docs/specs/archive/backend-legacy/` is frozen. "
            "Write new backend specs under `docs/specs/<module>/`."
        )

    if stack_backend_files and not backend_test_files:
        failures.append(
            "Stack backend code changed, but no backend test changed in the same scope. "
            "Add or update tests under `app/backend/src/test/` or `tests/`."
        )

    if stack_backend_files and not backend_domain_spec_files:
        failures.append(
            "Stack backend code changed, but no backend domain spec changed in the same scope. "
            "Document data model, API/interface, persistence, or test contract under "
            "`docs/specs/<module>/`."
        )

    records: dict[str, dict[str, str]] = {}
    boundary: str | None = None
    boundary_source: str | None = None
    boundary_text = ""
    flow_files = implementation_files + prototype_files
    if flow_files:
        boundary, boundary_source, boundary_error = resolve_active_boundary(
            str(paths_config.get("boundary_prefix", ".gstack/task-boundaries/"))
        )
        if boundary_error:
            failures.append(boundary_error)
        if not boundary:
            failures.append(
                "Flow-controlled changes require an active task boundary with `GStack Required Flow` records."
            )
        else:
            boundary_text = (REPO_ROOT / boundary).read_text(encoding="utf-8")
            records = parse_required_flow(boundary_text)
            if not records:
                failures.append(f"Active boundary `{boundary}` is missing `## GStack Required Flow`.")
            failures.extend(validate_decision_mode(boundary_text, boundary))
            failures.extend(validate_subagent_plan(boundary_text, boundary))
            failures.extend(validate_fast_lane_ai_review(boundary_text, records, config, boundary))
            failures.extend(validate_user_visible_qa_evidence(boundary_text, records, config, boundary))
            warnings.extend(validate_required_gates_presence(boundary_text, boundary))

    if records:
        failures.extend(validate_flow_order(records, config))

    if records and implementation_files:
        if args.mode == "pre-commit":
            required = config["pre_commit_requires_before_implementation"]
        else:
            required = config["pre_push_requires"]
        failures.extend(
            validate_commands(
                records,
                required,
                config,
                allow_qa_only=True,
            )
        )

    if records and prototype_files:
        failures.extend(
            validate_commands(
                records,
                ["domain-spec-readiness"],
                config,
                allow_qa_only=True,
            )
        )

    print(f"[gstack-flow] mode: {args.mode}")
    print(f"[gstack-flow] required sequence: {' -> '.join(config['required_sequence'])}")
    print(f"[gstack-flow] implementation files: {len(implementation_files)}")
    for path in sample_paths(implementation_files):
        print(f"  - {path}")
    print(f"[gstack-flow] prototype files: {len(prototype_files)}")
    for path in sample_paths(prototype_files):
        print(f"  - {path}")
    print(f"[gstack-flow] stack backend files: {len(stack_backend_files)}")
    for path in sample_paths(stack_backend_files):
        print(f"  - {path}")
    print(f"[gstack-flow] backend tests: {len(backend_test_files)}")
    for path in sample_paths(backend_test_files):
        print(f"  - {path}")
    print(f"[gstack-flow] backend domain specs: {len(backend_domain_spec_files)}")
    for path in sample_paths(backend_domain_spec_files):
        print(f"  - {path}")
    print(f"[gstack-flow] deprecated backend specs: {len(deprecated_backend_spec_files)}")
    for path in sample_paths(deprecated_backend_spec_files):
        print(f"  - {path}")
    if flow_files:
        print(f"[gstack-flow] active boundary: {boundary or 'unresolved'}")
        print(f"[gstack-flow] active boundary source: {boundary_source or 'none'}")

    if failures:
        print("\n[gstack-flow] FAIL:")
        for failure in failures:
            print(f"  - {failure}")
        print_next_steps(
            failures,
            mode=args.mode,
            config=config,
            boundary=boundary,
            flow_files=flow_files,
            prototype_files=prototype_files,
            stack_backend_files=stack_backend_files,
            backend_test_files=backend_test_files,
            backend_domain_spec_files=backend_domain_spec_files,
            deprecated_backend_spec_files=deprecated_backend_spec_files,
        )
        return 1

    if warnings:
        print("\n[gstack-flow] PASS WITH WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
        return 0

    print("\n[gstack-flow] PASS: required gstack command chain is satisfied.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
