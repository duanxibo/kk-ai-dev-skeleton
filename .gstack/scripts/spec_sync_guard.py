#!/usr/bin/env python3
"""Guard that implementation changes are matched with spec sync evidence."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

from adapter_runtime import load_adapter_runtime


REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTER_RUNTIME = load_adapter_runtime(REPO_ROOT)
IMPLEMENTATION_PREFIXES = ADAPTER_RUNTIME.path_tuple("implementation_prefixes")
SPEC_PREFIXES = ADAPTER_RUNTIME.path_tuple("spec_prefixes")
STACK_BACKEND_IMPLEMENTATION_PREFIXES = ADAPTER_RUNTIME.path_tuple(
    "backend_implementation_prefixes"
)
BACKEND_TEST_PREFIXES = ADAPTER_RUNTIME.path_tuple("backend_test_prefixes")
BACKEND_DOMAIN_SPEC_PREFIX = ADAPTER_RUNTIME.path_value("backend_domain_spec_prefix")
DEPRECATED_BACKEND_SPEC_PREFIXES = ADAPTER_RUNTIME.path_tuple("deprecated_backend_spec_prefixes")
BOUNDARY_PREFIX = ".gstack/task-boundaries/"
REVIEW_PREFIX = ".gstack/reviews/"
QA_PREFIX = ".gstack/qa-reports/"
DESIGN_PREFIX = ".gstack/designs/"
ARTIFACT_PREFIXES = (BOUNDARY_PREFIX, REVIEW_PREFIX, QA_PREFIX)
SPEC_IMPACT_RE = re.compile(r"^\s*-\s*Spec Impact:\s*(?P<value>.*?)\s*$", re.IGNORECASE)
CURRENT_BOUNDARY_FILE = f"{BOUNDARY_PREFIX}CURRENT.md"
LOCAL_CURRENT_BOUNDARY_FILE = f"{BOUNDARY_PREFIX}CURRENT.local.md"
ACTIVE_BOUNDARY_ENV = "KK_ACTIVE_BOUNDARY"
BOUNDARY_LINK_RE = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<href>[^)]+)\)")
LOCAL_GSTACK_PROJECTS = Path.home() / ".gstack" / "projects"
REQUIRED_BOUNDARY_HEADERS = (
    "## Goal",
    "## Allowed Files",
    "## Forbidden Files",
    "## Functional Non-goals",
    "## User-visible Acceptance",
    "## Generated Artifact Policy",
    "## Decision Mode",
    "## Flow Lane",
    "## Autonomy Plan",
    "## Subagent Plan",
    "## Required Knowledge",
    "## Spec Sync Plan",
    "## Verification",
    "## Lessons To Write Back",
)
DECISION_MODE_RE = re.compile(
    r"^\s*-\s*Mode:\s*`?(自主执行(?:模式)?|关键确认(?:模式)?|手动控制(?:模式)?|autonomous|codex-led|checkpoint|manual)`?\s*$",
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
FAST_LANE_AI_REVIEWED_FLOW_IDS = (
    "requirement-brief",
    "requirement-freeze",
    "plan-ceo-review",
    "plan-eng-review",
)
DATA_ACCESS_TRIGGER_PREFIXES = ADAPTER_RUNTIME.path_tuple("data_access_trigger_prefixes")
DATA_KNOWLEDGE_SCHEMA_RE = re.compile(
    r"\b(CREATE\s+TABLE|ALTER\s+TABLE|CREATE\s+(?:UNIQUE\s+)?INDEX)\b",
    re.IGNORECASE,
)
DATA_KNOWLEDGE_API_RE = re.compile(
    r"(Controller|Dto|DTO|Request|Response|Api|API|Route|Handler)\.(java|js|ts)$"
)
DATA_KNOWLEDGE_PERSISTENCE_RE = re.compile(
    r"(Entity|Mapper|Repository|Dao|DAO)\.(java|js|ts|xml)$"
)
DATA_KNOWLEDGE_TEXT_SUFFIXES = {".java", ".js", ".sql", ".ts", ".xml"}
FRONTEND_HINT_PREFIXES = ADAPTER_RUNTIME.path_tuple("frontend_hint_prefixes")
PROTOTYPE_SOURCE_HINTS = (
    "前端",
    "原型",
    "mock",
    "fixture",
    "页面",
    "prototype",
    "frontend",
)
PROTOTYPE_REQUIRED_HINTS = (
    "backend-owned",
    "读模型",
    "service",
    "snapshot",
    "接口",
    "后端承接",
    "迁后端",
)
SUBAGENT_MODE_RE = re.compile(
    r"^\s*-\s*Mode:\s*`?(not-used|explore|review|execute|governance|mixed)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
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
LOCAL_DRAFT_RULES = (
    {
        "name": "design draft",
        "pattern_template": "*-{branch}-design-*.md",
        "repo_prefixes": (DESIGN_PREFIX,),
    },
    {
        "name": "eng-review test plan",
        "pattern_template": "*-{branch}-eng-review-test-plan-*.md",
        "repo_prefixes": (DESIGN_PREFIX, REVIEW_PREFIX),
    },
    {
        "name": "test outcome",
        "pattern_template": "*-{branch}-test-outcome-*.md",
        "repo_prefixes": (QA_PREFIX,),
    },
)


def is_repo_final_artifact(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.name == "README.md":
        return False

    lowered = path.stem.lower()
    if "示例_并非真源" in path.stem:
        return False
    if lowered.endswith("-example") or lowered.endswith("_example"):
        return False

    return True


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


def has_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def is_implementation_file(path: str) -> bool:
    if not has_prefix(path, IMPLEMENTATION_PREFIXES):
        return False
    return not path.endswith(".md")


def is_concrete_boundary_file(path: str) -> bool:
    if not path.startswith(BOUNDARY_PREFIX):
        return False
    return path not in {
        CURRENT_BOUNDARY_FILE,
        LOCAL_CURRENT_BOUNDARY_FILE,
        f"{BOUNDARY_PREFIX}README.md",
    }


def is_stack_backend_implementation_file(path: str) -> bool:
    return has_prefix(path, STACK_BACKEND_IMPLEMENTATION_PREFIXES) and not path.endswith(".md")


def is_generic_backend_implementation_file(path: str) -> bool:
    if path.endswith(".md"):
        return False
    if has_prefix(path, STACK_BACKEND_IMPLEMENTATION_PREFIXES):
        return True
    parts = path.split("/")
    if len(parts) < 3 or parts[0] != "stack":
        return False
    return any(part in {"backend", "server", "api", "service"} for part in parts[2:-1])


def is_frontend_implementation_file(path: str) -> bool:
    if path.endswith(".md"):
        return False
    if has_prefix(path, FRONTEND_HINT_PREFIXES):
        return True
    parts = path.split("/")
    return len(parts) >= 3 and parts[0] in {"stack", "baseline"} and any(
        part in {"frontend", "public", "app"} for part in parts[2:-1]
    )


def read_spec_impact(path: str) -> str | None:
    file_path = REPO_ROOT / path
    if not file_path.exists():
        return None
    if file_path.suffix.lower() not in {".md", ".txt"}:
        return None
    lines = file_path.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines):
        match = SPEC_IMPACT_RE.match(line)
        if match:
            value = match.group("value").strip().strip("`").lower()
            if value:
                return value
            for follow in lines[index + 1 :]:
                stripped = follow.strip().strip("`")
                if not stripped:
                    continue
                if stripped.startswith("- ") or stripped.startswith("##"):
                    return None
                return stripped.lower()
    return None


def read_text(path: str) -> str | None:
    file_path = REPO_ROOT / path
    if not file_path.exists():
        return None
    return file_path.read_text(encoding="utf-8")


def looks_like_data_knowledge_path(path: str) -> bool:
    lowered = path.lower()
    name = Path(path).name
    lowered_name = name.lower()
    if path.startswith(".gstack/knowledge/data-access/sources/"):
        return True
    if (
        DATA_KNOWLEDGE_API_RE.search(name)
        or DATA_KNOWLEDGE_PERSISTENCE_RE.search(name)
        or lowered_name in {"route.js", "routes.js"}
    ):
        return True
    if any(
        token in lowered
        for token in (
            "/controller/",
            "/controllers/",
            "/routes/",
            "/api/",
            "/dto/",
            "/request/",
            "/response/",
            "/mapper/",
            "/mappers/",
            "/repository/",
            "/repositories/",
            "/dao/",
            "/entity/",
            "/entities/",
            "/mybatis/",
        )
    ):
        return True
    if (
        "/db/migration/" in lowered
        or "/migrations/" in lowered
        or Path(path).suffix.lower() in DATA_KNOWLEDGE_TEXT_SUFFIXES
    ):
        return bool(DATA_KNOWLEDGE_SCHEMA_RE.search(read_text(path) or ""))
    return False


def resolve_boundary_reference(raw_ref: str, source_label: str) -> tuple[str | None, list[str]]:
    raw_ref = raw_ref.strip()
    if not raw_ref:
        return None, [f"{source_label} is empty."]

    raw_path = Path(raw_ref)
    if raw_path.is_absolute():
        target = raw_path.resolve()
    else:
        repo_candidate = (REPO_ROOT / raw_path).resolve()
        boundary_candidate = (REPO_ROOT / BOUNDARY_PREFIX / raw_path).resolve()
        target = repo_candidate if repo_candidate.exists() else boundary_candidate

    try:
        relative = target.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return None, [f"{source_label} points outside the repo."]

    if not relative.startswith(BOUNDARY_PREFIX):
        return None, [f"{source_label} must point to a boundary file under `{BOUNDARY_PREFIX}`."]
    if relative in {CURRENT_BOUNDARY_FILE, LOCAL_CURRENT_BOUNDARY_FILE}:
        return None, [f"{source_label} must point to a concrete boundary file, not a pointer file."]
    if not (REPO_ROOT / relative).exists():
        return None, [f"{source_label} points to a missing boundary file: `{relative}`."]
    return relative, []


def parse_boundary_pointer_file(path: str, *, strict: bool) -> tuple[str | None, list[str]]:
    text = read_text(path)
    if text is None:
        if strict:
            return None, [f"Missing boundary pointer file: `{path}`."]
        return None, []

    active_links: list[str] = []
    in_active_section = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Active Boundary":
            in_active_section = True
            continue
        if in_active_section and stripped.startswith("## "):
            break
        if not in_active_section:
            continue

        match = BOUNDARY_LINK_RE.search(stripped)
        if not match:
            continue

        active_links.append(match.group("href"))

    if not active_links:
        if strict:
            return None, [
                f"`{path}` must declare exactly one active boundary link under `## Active Boundary`."
            ]
        return None, []
    if len(active_links) > 1:
        joined = ", ".join(active_links)
        return None, [f"`{path}` declares multiple active boundaries: {joined}."]

    href = active_links[0]
    source_label = f"`{path}` Active Boundary"
    if strict:
        source_path = Path(path)
        href_path = (source_path.parent / href).as_posix()
        return resolve_boundary_reference(href_path, source_label)
    return resolve_boundary_reference(href, source_label)


def resolve_active_boundary() -> tuple[str | None, str | None, list[str], list[str]]:
    env_value = os.environ.get(ACTIVE_BOUNDARY_ENV, "").strip()
    if env_value:
        boundary, failures = resolve_boundary_reference(
            env_value, f"Environment variable `{ACTIVE_BOUNDARY_ENV}`"
        )
        return boundary, f"env:{ACTIVE_BOUNDARY_ENV}", failures, []

    local_pointer = REPO_ROOT / LOCAL_CURRENT_BOUNDARY_FILE
    if local_pointer.exists():
        boundary, failures = parse_boundary_pointer_file(LOCAL_CURRENT_BOUNDARY_FILE, strict=True)
        return boundary, LOCAL_CURRENT_BOUNDARY_FILE, failures, []

    current_boundary, current_failures = parse_boundary_pointer_file(
        CURRENT_BOUNDARY_FILE, strict=False
    )
    warnings: list[str] = []
    if current_failures:
        warnings.extend(current_failures)
    if current_boundary:
        warnings.append(
            f"Using legacy shared boundary pointer from `{CURRENT_BOUNDARY_FILE}`. Prefer letting `kk-task-kickoff` set the local active boundary."
        )
        return current_boundary, CURRENT_BOUNDARY_FILE, [], warnings

    warnings.append(
        "No active boundary pointer resolved. Prefer letting `kk-task-kickoff` set the local active boundary before implementation work."
    )
    return None, None, [], warnings


def validate_boundary_template(path: str) -> list[str]:
    text = read_text(path)
    if text is None:
        return [f"Boundary file missing: `{path}`."]

    missing_headers = [header for header in REQUIRED_BOUNDARY_HEADERS if header not in text]
    issues = [f"`{header}`" for header in missing_headers]
    if "## Decision Mode" in text and not DECISION_MODE_RE.search(text):
        issues.append("`Decision Mode` mode (`- Mode: 自主执行|关键确认|手动控制`)")
    if "## Flow Lane" in text and not FLOW_LANE_RE.search(text):
        issues.append("`Flow Lane` lane (`- Lane: fast-lane|standard|discovery`)")
    if "## Autonomy Plan" in text and not GOAL_MODE_RE.search(text):
        issues.append("`Autonomy Plan` goal mode (`- Goal Mode: enabled|not-used|ask-first`)")
    if "## Subagent Plan" in text and not SUBAGENT_MODE_RE.search(text):
        issues.append("`Subagent Plan` mode (`- Mode: ...`)")
    if not issues:
        return []
    missing = ", ".join(issues)
    return [f"Boundary file `{path}` is missing required sections: {missing}."]


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


def is_fast_lane_text(text: str) -> bool:
    lane_lines = [line.strip() for line in section_lines(text, "Flow Lane") if line.strip()]
    return bool(FAST_LANE_RE.search("\n".join(lane_lines)))


def fast_lane_evidence_issue(text: str) -> str | None:
    if FAST_LANE_DRAFT_RE.search(text):
        return "contains draft markers such as `draft-needs-codex-review`, `AI 语义复核: no`, or `pending-review`"
    if not AI_REVIEWED_YES_RE.search(text):
        return "is missing `AI 语义复核: yes`"
    return None


def gstack_flow_record(path: str, flow_id: str) -> tuple[str | None, str | None]:
    text = read_text(path)
    if text is None:
        return None, None

    in_flow_section = False
    in_target_flow = False
    status: str | None = None
    evidence: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## GStack Required Flow":
            in_flow_section = True
            continue
        if in_flow_section and stripped.startswith("## "):
            break
        if not in_flow_section:
            continue
        if stripped.startswith("- "):
            if in_target_flow:
                break
            in_target_flow = stripped == f"- {flow_id}:"
            continue
        if not in_target_flow:
            continue
        status_match = re.match(r"status:\s*`?(?P<status>[a-z-]+)`?", stripped)
        if status_match:
            status = status_match.group("status")
            continue
        evidence_match = re.match(r"evidence:\s*`?(?P<path>.*?)`?$", stripped)
        if evidence_match:
            evidence = evidence_match.group("path").strip().strip("`").strip('"')
    return status, evidence


def boundary_requires_user_visible_interaction(text: str) -> bool:
    if not text:
        return False
    return bool(USER_VISIBLE_YES_RE.search(text) or USER_VISIBLE_SURFACE_RE.search(text))


def validate_user_visible_qa_evidence(path: str) -> list[str]:
    text = read_text(path)
    if text is None or not boundary_requires_user_visible_interaction(text):
        return []

    qa_status, qa_evidence = gstack_flow_record(path, "qa")
    if qa_status != "done":
        return []
    if not qa_evidence or qa_evidence == "待补":
        return [
            f"Boundary `{path}` declares user-visible UI/HTML acceptance and marks QA done, but QA evidence path is missing."
        ]

    qa_text = read_text(qa_evidence)
    if qa_text is None:
        return [
            f"Boundary `{path}` declares user-visible UI/HTML acceptance and marks QA done, but QA evidence file is missing: `{qa_evidence}`."
        ]
    if QA_INTERACTION_EVIDENCE_RE.search(qa_text) or QA_BLOCKED_PARTIAL_RE.search(qa_text):
        return []
    return [
        f"Boundary `{path}` declares user-visible UI/HTML acceptance and marks QA done, but `{qa_evidence}` has no Browser / Chrome / Playwright / local HTTP server interaction evidence or explicit blocked / partial reason."
    ]


def validate_fast_lane_draft_guard(path: str) -> list[str]:
    text = read_text(path)
    if text is None or not is_fast_lane_text(text):
        return []

    failures: list[str] = []
    if FAST_LANE_DRAFT_RE.search(text):
        failures.append(
            f"Fast-lane boundary `{path}` still contains draft markers. "
            "Draft evidence cannot satisfy review/freeze gates before implementation."
        )

    checked_paths: set[str] = set()
    for flow_id in FAST_LANE_AI_REVIEWED_FLOW_IDS:
        status, evidence = gstack_flow_record(path, flow_id)
        if status != "done" or not evidence or evidence in checked_paths:
            continue
        checked_paths.add(evidence)

        evidence_text = read_text(evidence)
        if evidence_text is None:
            continue
        issue = fast_lane_evidence_issue(evidence_text)
        if issue:
            failures.append(
                f"Fast-lane evidence `{evidence}` for `{flow_id}` {issue}. "
                "Run Codex semantic review first, or regenerate the evidence with `autopilot_bootstrap.py --ai-reviewed`."
            )

    return failures


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


def validate_required_gates_presence(path: str) -> list[str]:
    text = read_text(path)
    if text is None:
        return []
    if "## Required Gates" not in text or "required_gates:" not in text:
        return [
            f"Boundary file `{path}` has no parsable `Required Gates` block. "
            "Initial rollout is warning-only; add it from `.gstack/templates/task-boundary.template.md`."
        ]
    warnings: list[str] = []
    if "gate_id: data-access" not in text:
        warnings.append(
            f"Boundary file `{path}` has no `data-access` gate. "
            "If data is not involved, mark it `not-required` with a trigger_reason."
        )
    prototype_gate = required_gate_block(text, "prototype-logic-extraction")
    if prototype_gate is None:
        warnings.append(
            f"Boundary file `{path}` has no `prototype-logic-extraction` gate. "
            "If frontend/prototype logic is not involved, mark it `not-required` with a trigger_reason."
        )
        return warnings
    if "owner: kk-task-kickoff" not in prototype_gate:
        warnings.append(
            f"Boundary file `{path}` prototype-logic-extraction gate should use `owner: kk-task-kickoff`."
        )
    if "required_before: plan-eng-review" not in prototype_gate:
        warnings.append(
            f"Boundary file `{path}` prototype-logic-extraction gate should use `required_before: plan-eng-review`."
        )
    return warnings


def data_access_gate_status(path: str) -> str | None:
    text = read_text(path)
    if text is None or "gate_id: data-access" not in text:
        return None
    in_gate = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- gate_id:"):
            in_gate = stripped == "- gate_id: data-access"
            continue
        if in_gate:
            match = re.match(r"status:\s*`?(?P<status>[a-z-]+)`?", stripped)
            if match:
                return match.group("status")
    return None


def required_gate_status(path: str, gate_id: str) -> tuple[str | None, str | None, str | None]:
    text = read_text(path)
    if text is None or f"gate_id: {gate_id}" not in text:
        return None, None, None
    in_gate = False
    status: str | None = None
    evidence_path: str | None = None
    blocking_reason: str | None = None
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- gate_id:"):
            if in_gate:
                break
            in_gate = stripped == f"- gate_id: {gate_id}"
            continue
        if not in_gate:
            continue
        status_match = re.match(r"status:\s*`?(?P<status>[a-z-]+)`?", stripped)
        if status_match:
            status = status_match.group("status")
            continue
        evidence_match = re.match(r"evidence_path:\s*`?(?P<path>.*?)`?$", stripped)
        if evidence_match:
            evidence_path = evidence_match.group("path").strip().strip('"')
            continue
        blocking_match = re.match(r"blocking_reason:\s*`?(?P<reason>.*?)`?$", stripped)
        if blocking_match:
            blocking_reason = blocking_match.group("reason").strip().strip('"')
    return status, evidence_path, blocking_reason


def gstack_flow_status(path: str, flow_id: str) -> str | None:
    text = read_text(path)
    if text is None:
        return None

    in_flow_section = False
    in_target_flow = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## GStack Required Flow":
            in_flow_section = True
            continue
        if in_flow_section and stripped.startswith("## "):
            break
        if not in_flow_section:
            continue
        if stripped.startswith("- "):
            if in_target_flow:
                break
            in_target_flow = stripped == f"- {flow_id}:"
            continue
        if not in_target_flow:
            continue
        status_match = re.match(r"status:\s*`?(?P<status>[a-z-]+)`?", stripped)
        if status_match:
            return status_match.group("status")
    return None


def infer_active_boundary_from_diff(concrete_boundary_files: list[str]) -> tuple[str | None, str | None]:
    ci_boundary, ci_reason = infer_active_boundary_from_github_event(concrete_boundary_files)
    if ci_boundary:
        return ci_boundary, ci_reason

    if len(concrete_boundary_files) == 1:
        return (
            concrete_boundary_files[0],
            f"No local active boundary pointer found. Auto-inferred active boundary from the only changed boundary file: `{concrete_boundary_files[0]}`.",
        )

    implementation_boundaries = [
        path for path in concrete_boundary_files if gstack_flow_status(path, "implement") == "done"
    ]
    if len(implementation_boundaries) == 1:
        return (
            implementation_boundaries[0],
            "No local active boundary pointer found. Auto-inferred active boundary from the only changed boundary file whose `implement` flow is `done`: "
            f"`{implementation_boundaries[0]}`.",
        )

    return None, None


def infer_active_boundary_from_github_event(
    concrete_boundary_files: list[str],
) -> tuple[str | None, str | None]:
    event_path = os.environ.get("GITHUB_EVENT_PATH", "").strip()
    if not event_path:
        return None, None

    try:
        event = json.loads(Path(event_path).read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError):
        return None, None

    pull_request = event.get("pull_request")
    if not isinstance(pull_request, dict):
        return None, None

    head = pull_request.get("head") if isinstance(pull_request.get("head"), dict) else {}
    context_parts = [
        str(pull_request.get("title") or ""),
        str(pull_request.get("body") or ""),
        str(head.get("ref") or ""),
    ]
    context_text = "\n".join(context_parts)
    if not context_text:
        return None, None

    referenced = [
        path
        for path in concrete_boundary_files
        if path in context_text or path.removeprefix(BOUNDARY_PREFIX) in context_text
    ]
    if len(referenced) == 1:
        return (
            referenced[0],
            "No local active boundary pointer found. Auto-inferred active boundary from GitHub pull request context: "
            f"`{referenced[0]}`.",
        )

    return None, None


def prototype_logic_trigger_files(files: list[str], boundary_text: str | None) -> list[str]:
    backend_files = [path for path in files if is_generic_backend_implementation_file(path)]
    frontend_files = [path for path in files if is_frontend_implementation_file(path)]
    triggers: list[str] = []
    if backend_files and frontend_files:
        triggers.extend(backend_files + frontend_files)
    if boundary_text and backend_files:
        lowered = boundary_text.lower()
        if any(hint.lower() in lowered for hint in PROTOTYPE_SOURCE_HINTS) and any(
            hint.lower() in lowered for hint in PROTOTYPE_REQUIRED_HINTS
        ):
            triggers.extend(backend_files)
    return sorted(set(triggers))


def current_branch_name() -> str:
    result = subprocess.run(
        ["git", "symbolic-ref", "--short", "-q", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    branch = result.stdout.strip()
    return branch or "head-detached"


def repo_slug_candidates() -> list[str]:
    candidates: list[str] = [REPO_ROOT.name]
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    remote = result.stdout.strip()
    match = re.search(r"[:/]([^/:]+)/([^/]+?)(?:\.git)?$", remote)
    if match:
        owner, repo = match.groups()
        slug = f"{owner}-{repo}"
        if slug not in candidates:
            candidates.insert(0, slug)
    return candidates


def latest_repo_artifact_mtime(prefixes: tuple[str, ...]) -> float | None:
    newest: float | None = None
    for prefix in prefixes:
        base = REPO_ROOT / prefix
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not is_repo_final_artifact(path):
                continue
            mtime = path.stat().st_mtime
            newest = mtime if newest is None else max(newest, mtime)
    return newest


def local_gstack_artifact_findings(branch: str) -> tuple[list[str], list[str]]:
    if not LOCAL_GSTACK_PROJECTS.exists():
        return [], []

    warnings: list[str] = []
    failures: list[str] = []
    project_dirs = [LOCAL_GSTACK_PROJECTS / slug for slug in repo_slug_candidates()]
    project_dirs = [path for path in project_dirs if path.exists()]
    if not project_dirs:
        return [], []

    for rule in LOCAL_DRAFT_RULES:
        pattern = rule["pattern_template"].format(branch=branch)
        local_matches: list[Path] = []
        for project_dir in project_dirs:
            local_matches.extend(project_dir.rglob(pattern))
        if not local_matches:
            continue

        newest_local = max(local_matches, key=lambda path: path.stat().st_mtime)
        newest_local_mtime = newest_local.stat().st_mtime
        repo_mtime = latest_repo_artifact_mtime(rule["repo_prefixes"])
        local_ref = newest_local.expanduser().as_posix().replace(str(Path.home()), "~", 1)
        repo_targets = ", ".join(f"`{prefix}`" for prefix in rule["repo_prefixes"])
        if repo_mtime is None or repo_mtime < newest_local_mtime:
            failures.append(
                f"Found newer local gstack {rule['name']} at `{local_ref}`, but no newer repo-native final artifact under {repo_targets}."
            )
        else:
            warnings.append(
                f"Local gstack {rule['name']} exists at `{local_ref}`; repo-native artifacts appear newer, so sync looks satisfied."
            )

    return warnings, failures


def normalize_impact(value: str | None) -> str | None:
    if value is None:
        return None
    aliases = {
        "updated": "updated",
        "not-required": "not-required",
        "pending": "pending",
        "none": "not-required",
        "no": "not-required",
    }
    return aliases.get(value, value)


def print_group(title: str, items: list[str]) -> None:
    print(f"{title}:")
    if not items:
        print("  - none")
        return
    for item in items:
        print(f"  - {item}")


def append_unique(items: list[str], item: str) -> None:
    if item not in items:
        items.append(item)


def print_next_steps(
    failures: list[str],
    *,
    implementation_files: list[str],
    stack_backend_files: list[str],
    backend_test_files: list[str],
    backend_domain_spec_files: list[str],
    deprecated_backend_spec_files: list[str],
    concrete_boundary_files: list[str],
    active_boundary: str | None,
    active_boundary_source: str | None,
    review_files: list[str],
    qa_files: list[str],
) -> None:
    text = "\n".join(failures)
    steps: list[str] = []

    if deprecated_backend_spec_files:
        append_unique(
            steps,
            "旧后端目录已冻结：把新规范移到 `docs/specs/<module>/`，不要继续写 `04_后端设计/`。",
        )
    if stack_backend_files and not backend_test_files:
        append_unique(
            steps,
            "后端代码改了，需要补测试：新增或更新 `app/backend/src/test/` 或 `tests/`。",
        )
    if stack_backend_files and not backend_domain_spec_files:
        append_unique(
            steps,
            "后端代码改了，需要补模块规范：更新 `docs/specs/<module>/backend.md`、`data.md` 或 `testing.md`。",
        )

    if "Spec Impact: pending" in text:
        append_unique(
            steps,
            "把 boundary / review / QA 里的 `Spec Impact: pending` 改成 `updated` 或 `not-required`，并写清原因。",
        )
    if "unsupported `Spec Impact`" in text:
        append_unique(
            steps,
            "修正 `Spec Impact`：只允许 `updated`、`not-required`、`pending`。",
        )
    if "no spec file changed" in text and "no artifact declares `Spec Impact: not-required`" in text:
        append_unique(
            steps,
            "实现改了但没改 spec：要么更新对应 `stack/specs/` 真源，要么在 active boundary / review / QA 中声明 `Spec Impact: not-required` 并写清原因；旧 `archive/baseline/` 只能作为证据来源。",
        )
    if "declares `Spec Impact: updated`, but no file changed" in text:
        append_unique(
            steps,
            "已经声明 spec 会更新，但没有改真源文档；请更新对应 `stack/specs/` 文件，或把声明改为 `not-required`。",
        )
    if "Spec files changed, but an artifact declares `Spec Impact: not-required`" in text:
        append_unique(
            steps,
            "spec 文件已经改了，不应再写 `not-required`；把对应过程文档的 `Spec Impact` 改成 `updated`。",
        )

    if implementation_files and not concrete_boundary_files:
        append_unique(
            steps,
            "实现代码改了，需要同步更新具体 task boundary：`.gstack/task-boundaries/YYYY-MM-DD_<task>.md`。",
        )
    if "no active boundary could be resolved" in text:
        append_unique(
            steps,
            "设置 active boundary：运行 `$kk-task-kickoff`，或执行 `bash .gstack/scripts/use_boundary.sh .gstack/task-boundaries/<your-boundary>.md`。",
        )
    if "Changed boundary files do not include the active boundary" in text:
        append_unique(
            steps,
            f"当前 active boundary 来自 `{active_boundary_source or 'unknown'}`；请把 `{active_boundary or '<active-boundary>'}` 加入本次 diff，或切换到本次任务的 boundary。",
        )
    if "missing required sections" in text:
        append_unique(
            steps,
            "补齐 active boundary 的必填章节，可参考 `.gstack/templates/task-boundary.template.md`。",
        )
    if "Subagent Plan" in text:
        append_unique(
            steps,
            "补 `## Subagent Plan`：小任务可写 `- Mode: not-used` 并说明原因；复杂任务先用 `$kk-subagent-orchestrator` 拆分读/评审/执行/治理 agent。",
        )
    if "Decision Mode" in text:
        append_unique(
            steps,
            "补 `## Decision Mode`：写 `- Mode: 自主执行|关键确认|手动控制`，并说明来源、内部枚举和原因。",
        )
    if "Flow Lane" in text:
        append_unique(
            steps,
            "补 `## Flow Lane`：写 `- Lane: fast-lane|standard|discovery`；fast-lane 任务还要补轻量 requirement / review evidence。",
        )
    if "Autonomy Plan" in text or "Goal Mode" in text:
        append_unique(
            steps,
            "补 `## Autonomy Plan`：写 Codex 可自动做什么、必须问什么，以及 `- Goal Mode: enabled|not-used|ask-first`。",
        )
    if "Fast-lane evidence" in text or "Fast-lane boundary" in text:
        append_unique(
            steps,
            "fast-lane evidence 仍是 draft：由 Codex 读取上下文完成语义复核后，补 `AI 语义复核: yes`，或用 `python3 .gstack/scripts/autopilot_bootstrap.py ... --ai-reviewed --activate` 重新生成。",
        )
    if "No changed review or QA artifact detected" in text and not (review_files or qa_files):
        append_unique(
            steps,
            "收口前补 review 或 QA evidence：结构/风险检查写 `.gstack/reviews/`，验收结果写 `.gstack/qa-reports/`。",
        )
    if "local gstack drafts" in text or "Found newer local gstack" in text:
        append_unique(
            steps,
            "本地 `~/.gstack/projects/...` 有更新草稿；请同步定稿到 repo-native `.gstack/designs/`、`.gstack/reviews/` 或 `.gstack/qa-reports/`。",
        )

    if active_boundary:
        append_unique(steps, f"优先修正当前 active boundary：`{active_boundary}`。")
    append_unique(steps, "修完后重跑：`python3 .gstack/scripts/spec_sync_guard.py`。")

    print("\n下一步建议:")
    for index, step in enumerate(steps, start=1):
        print(f"  {index}. {step}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that implementation changes have matching spec sync evidence."
    )
    parser.add_argument(
        "--base",
        default="HEAD",
        help="Git base ref used to calculate changed tracked files. Default: HEAD",
    )
    parser.add_argument(
        "--strict-evidence",
        action="store_true",
        help="Fail when implementation changed but no review or QA artifact changed.",
    )
    args = parser.parse_args()

    if not inside_git_worktree():
        active_boundary, active_boundary_source, active_boundary_failures, active_boundary_warnings = (
            resolve_active_boundary()
        )
        print("Git state:")
        print("  - not a git worktree; running static skeleton guard")
        print("Current active boundary:")
        print(f"  - {active_boundary or 'unresolved'}")
        print("Active boundary source:")
        print(f"  - {active_boundary_source or 'none'}")

        failures: list[str] = []
        warnings: list[str] = []
        failures.extend(active_boundary_failures)
        warnings.extend(active_boundary_warnings)
        if active_boundary:
            failures.extend(validate_boundary_template(active_boundary))
            failures.extend(validate_fast_lane_draft_guard(active_boundary))
            failures.extend(validate_user_visible_qa_evidence(active_boundary))
            warnings.extend(validate_required_gates_presence(active_boundary))
        else:
            warnings.append("No active boundary is set. Create one with `kk-task-kickoff` before implementation.")

        if failures:
            print("\nFAIL:")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        if warnings:
            print("\nPASS WITH WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
            return 0
        print("\nPASS: static skeleton guard passed.")
        return 0

    try:
        files = changed_files(args.base)
    except RuntimeError as exc:
        print(f"spec-sync guard failed to inspect git state: {exc}", file=sys.stderr)
        return 2

    implementation_files = [path for path in files if is_implementation_file(path)]
    stack_backend_files = [path for path in files if is_stack_backend_implementation_file(path)]
    backend_test_files = [
        path for path in files if has_prefix(path, BACKEND_TEST_PREFIXES) and not path.endswith(".md")
    ]
    backend_domain_spec_files = [
        path
        for path in files
        if path.startswith(BACKEND_DOMAIN_SPEC_PREFIX) and path.endswith(".md")
    ]
    deprecated_backend_spec_files = [
        path for path in files if has_prefix(path, DEPRECATED_BACKEND_SPEC_PREFIXES)
    ]
    spec_files = [path for path in files if has_prefix(path, SPEC_PREFIXES)]
    boundary_files = [path for path in files if path.startswith(BOUNDARY_PREFIX)]
    concrete_boundary_files = [path for path in boundary_files if is_concrete_boundary_file(path)]
    review_files = [path for path in files if path.startswith(REVIEW_PREFIX)]
    qa_files = [path for path in files if path.startswith(QA_PREFIX)]
    artifact_files = [path for path in files if has_prefix(path, ARTIFACT_PREFIXES)]
    active_boundary, active_boundary_source, active_boundary_failures, active_boundary_warnings = (
        resolve_active_boundary()
    )
    current_branch = current_branch_name()
    local_artifact_warnings, local_artifact_failures = local_gstack_artifact_findings(current_branch)

    statuses: dict[str, str] = {}
    for path in artifact_files:
        status = normalize_impact(read_spec_impact(path))
        if status:
            statuses[path] = status

    if not active_boundary:
        inferred_boundary, inferred_warning = infer_active_boundary_from_diff(concrete_boundary_files)
        if inferred_boundary:
            active_boundary = inferred_boundary
            active_boundary_source = "auto-inferred-from-diff"
        if inferred_warning:
            active_boundary_warnings.append(inferred_warning)

    print_group("Implementation files", implementation_files)
    print_group("Stack backend files", stack_backend_files)
    print_group("Backend tests", backend_test_files)
    print_group("Backend domain specs", backend_domain_spec_files)
    print_group("Deprecated backend specs", deprecated_backend_spec_files)
    print_group("Spec files", spec_files)
    print_group("Boundary / review / QA artifacts", artifact_files)
    print("Current active boundary:")
    print(f"  - {active_boundary or 'unresolved'}")
    print("Active boundary source:")
    print(f"  - {active_boundary_source or 'none'}")
    print("Current branch:")
    print(f"  - {current_branch}")

    print("Spec impact declarations:")
    if not statuses:
        print("  - none")
    else:
        for path, status in statuses.items():
            print(f"  - {path}: {status}")

    failures: list[str] = []
    warnings: list[str] = []
    failures.extend(active_boundary_failures)
    warnings.extend(active_boundary_warnings)
    if active_boundary:
        failures.extend(validate_boundary_template(active_boundary))
        failures.extend(validate_fast_lane_draft_guard(active_boundary))
        failures.extend(validate_user_visible_qa_evidence(active_boundary))
        warnings.extend(validate_required_gates_presence(active_boundary))
    warnings.extend(local_artifact_warnings)

    data_access_trigger_files = [path for path in files if has_prefix(path, DATA_ACCESS_TRIGGER_PREFIXES)]
    data_knowledge_trigger_files = [path for path in files if looks_like_data_knowledge_path(path)]
    if data_access_trigger_files:
        if active_boundary:
            status = data_access_gate_status(active_boundary)
            if status is None:
                warnings.append(
                    "Data-access-related files changed, but active boundary has no `data-access` gate."
                )
            elif status not in {"not-required", "planned", "done", "blocked", "deferred"}:
                warnings.append(
                    f"Data-access gate has unsupported status `{status}`. "
                    "Use not-required / planned / done / blocked / deferred."
                )
            elif status == "planned":
                warnings.append(
                    "Data-access-related files changed while `data-access` gate is still `planned`; "
                    "confirm it is not past its required_before stage."
                )
        else:
            warnings.append(
                "Data-access-related files changed, but no active boundary could be resolved."
            )

    if data_knowledge_trigger_files:
        if active_boundary:
            status, evidence_path, _blocking_reason = required_gate_status(
                active_boundary, "data-knowledge-sync"
            )
            if status is None:
                warnings.append(
                    "Data knowledge sync trigger files changed, but active boundary has no `data-knowledge-sync` gate."
                )
            elif status == "planned":
                warnings.append(
                    "`data-knowledge-sync` is still planned while trigger files changed; finish source/interface evidence before review."
                )
            elif status in {"done", "blocked", "deferred"} and (
                not evidence_path or evidence_path == "待补"
            ):
                warnings.append(
                    f"`data-knowledge-sync` is {status} but evidence_path is not set."
                )
        else:
            warnings.append(
                "Data knowledge sync trigger files changed, but no active boundary could be resolved."
            )

    active_boundary_text = read_text(active_boundary) if active_boundary else None
    prototype_logic_files = prototype_logic_trigger_files(files, active_boundary_text)
    if prototype_logic_files:
        if active_boundary:
            status, evidence_path, blocking_reason = required_gate_status(
                active_boundary, "prototype-logic-extraction"
            )
            if status is None:
                warnings.append(
                    "Frontend/prototype-to-backend files changed, but active boundary has no `prototype-logic-extraction` gate."
                )
            elif status == "not-required":
                warnings.append(
                    "`prototype-logic-extraction` is not-required while frontend/prototype-to-backend trigger files were detected; review the exclusion reason."
                )
            elif status == "planned":
                warnings.append(
                    "`prototype-logic-extraction` is still planned; evidence should be done / blocked / deferred before plan-eng-review."
                )
            elif status in {"done", "blocked", "deferred"} and (
                not evidence_path or evidence_path == "待补"
            ):
                warnings.append(
                    f"`prototype-logic-extraction` is {status} but evidence_path is not set."
                )
            if status == "deferred":
                reason = blocking_reason or ""
                if "批准" not in reason or "风险" not in reason or (
                    "删除条件" not in reason and "补齐" not in reason
                ):
                    warnings.append(
                        "`prototype-logic-extraction` deferred must include approval source, risk, and deletion criteria or follow-up completion path."
                    )
        else:
            warnings.append(
                "Frontend/prototype-to-backend files changed, but no active boundary could be resolved."
            )

    if deprecated_backend_spec_files:
        failures.append(
            "Deprecated backend spec directory changed. Do not write new backend specs under "
            "`docs/specs/archive/backend-legacy/`; use `docs/specs/<module>/`."
        )

    if not implementation_files:
        if failures:
            print("\nFAIL:")
            for failure in failures:
                print(f"  - {failure}")
            print_next_steps(
                failures,
                implementation_files=implementation_files,
                stack_backend_files=stack_backend_files,
                backend_test_files=backend_test_files,
                backend_domain_spec_files=backend_domain_spec_files,
                deprecated_backend_spec_files=deprecated_backend_spec_files,
                concrete_boundary_files=concrete_boundary_files,
                active_boundary=active_boundary,
                active_boundary_source=active_boundary_source,
                review_files=review_files,
                qa_files=qa_files,
            )
            return 1
        print("\nPASS: no implementation changes detected, spec sync guard is not blocking this diff.")
        return 0

    declared_updated = [path for path, status in statuses.items() if status == "updated"]
    declared_not_required = [path for path, status in statuses.items() if status == "not-required"]
    declared_pending = [path for path, status in statuses.items() if status == "pending"]
    declared_unknown = [
        path for path, status in statuses.items() if status not in {"updated", "not-required", "pending"}
    ]

    if declared_pending:
        failures.append(
            "Implementation changed but some artifacts still declare `Spec Impact: pending`."
        )

    if declared_unknown:
        failures.append(
            "Found unsupported `Spec Impact` value. Use only `updated`, `not-required`, or `pending`."
        )

    if stack_backend_files:
        if not backend_test_files:
            failures.append(
                "Stack backend code changed, but no backend test changed in this diff. "
                "Add or update tests under `app/backend/src/test/` or `tests/`."
            )
        if not backend_domain_spec_files:
            failures.append(
                "Stack backend code changed, but no backend domain spec changed in this diff. "
                "Document data model, API/interface, persistence, or test contract under "
                "`docs/specs/<module>/`."
            )

    if spec_files:
        if declared_not_required:
            failures.append(
                "Spec files changed, but an artifact declares `Spec Impact: not-required`."
            )
        if not declared_updated:
            warnings.append(
                "Spec files changed, but no boundary/review/QA artifact explicitly declares `Spec Impact: updated`."
            )
    else:
        if not declared_not_required:
            failures.append(
                "Implementation files changed, but no spec file changed and no artifact declares `Spec Impact: not-required`."
            )

    if declared_updated and not spec_files:
        failures.append(
            "An artifact declares `Spec Impact: updated`, but no file changed under the registered spec-truth prefixes."
        )

    if not concrete_boundary_files:
        failures.append(
            "Implementation changed, but no task boundary file changed. Update the active boundary before landing implementation work."
        )
    elif not active_boundary:
        failures.append(
            "Implementation changed, but no active boundary could be resolved. If this task only touches one boundary, include that boundary file in the diff; otherwise let `kk-task-kickoff` set the local active boundary."
        )
    elif active_boundary not in concrete_boundary_files:
        changed_boundaries = ", ".join(concrete_boundary_files)
        failures.append(
            f"Changed boundary files do not include the active boundary from `{active_boundary_source or 'active pointer'}`. Changed: {changed_boundaries}."
        )

    if not (review_files or qa_files):
        message = (
            "No changed review or QA artifact detected. Implementation completion should usually leave at least one repo-native evidence file."
        )
        if args.strict_evidence:
            failures.append(message)
        else:
            warnings.append(message)

    if local_artifact_failures:
        failures.extend(
            [
                "Implementation changed while newer local gstack drafts still appear unsynced to repo-native `.gstack/` final artifacts.",
                *local_artifact_failures,
            ]
        )

    if failures:
        print("\nFAIL:")
        for failure in failures:
            print(f"  - {failure}")
        if warnings:
            print("\nWarnings:")
            for warning in warnings:
                print(f"  - {warning}")
        print_next_steps(
            failures,
            implementation_files=implementation_files,
            stack_backend_files=stack_backend_files,
            backend_test_files=backend_test_files,
            backend_domain_spec_files=backend_domain_spec_files,
            deprecated_backend_spec_files=deprecated_backend_spec_files,
            concrete_boundary_files=concrete_boundary_files,
            active_boundary=active_boundary,
            active_boundary_source=active_boundary_source,
            review_files=review_files,
            qa_files=qa_files,
        )
        return 1

    if warnings:
        print("\nPASS WITH WARNINGS:")
        for warning in warnings:
            print(f"  - {warning}")
        return 0

    print("\nPASS: implementation changes are matched with spec sync evidence.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
