#!/usr/bin/env python3
"""Warning-first audit for task-boundary Required Gates blocks."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

from adapter_runtime import load_adapter_runtime


REPO_ROOT = Path(__file__).resolve().parents[2]
ADAPTER_RUNTIME = load_adapter_runtime(REPO_ROOT)
BOUNDARY_PREFIX = ".gstack/task-boundaries/"
CURRENT_BOUNDARY_FILE = f"{BOUNDARY_PREFIX}CURRENT.md"
LOCAL_CURRENT_BOUNDARY_FILE = f"{BOUNDARY_PREFIX}CURRENT.local.md"
ACTIVE_BOUNDARY_ENV = "KK_ACTIVE_BOUNDARY"
BOUNDARY_LINK_RE = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<href>[^)]+)\)")

ALLOWED_STATUSES = {"not-required", "planned", "done", "blocked", "deferred"}
ALLOWED_OWNERS = {
    "kk-task-kickoff",
    "kk-data-kickoff",
    "kk-data-query",
    "kk-subagent-orchestrator",
    "kk-doc-backfill",
    "kk-doc-sync",
    "kk-ui-design-kickoff",
    "kk-ui-polish-review",
    "template-review",
}
ALLOWED_REQUIRED_BEFORE = {
    "requirement-brief",
    "plan-ceo-review",
    "requirement-freeze",
    "plan-eng-review",
    "domain-spec-readiness",
    "implement",
    "review",
    "qa",
}
REQUIRED_GATE_KEYS = {
    "gate_id",
    "trigger_reason",
    "owner",
    "required_before",
    "status",
    "evidence_path",
    "evidence_section",
    "blocking_reason",
    "done_criteria",
}

DATA_ACCESS_TRIGGER_PREFIXES = ADAPTER_RUNTIME.path_tuple("data_access_trigger_prefixes")
FRONTEND_HINT_PREFIXES = ADAPTER_RUNTIME.path_tuple("frontend_hint_prefixes")
BACKEND_IMPLEMENTATION_PREFIXES = ADAPTER_RUNTIME.path_tuple("backend_implementation_prefixes")
PROTOTYPE_LOGIC_EVIDENCE_PREFIXES = ADAPTER_RUNTIME.path_tuple(
    "prototype_logic_evidence_prefixes"
)
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
FLOW_STAGE_ORDER = [
    "requirement-brief",
    "plan-ceo-review",
    "requirement-freeze",
    "plan-eng-review",
    "domain-spec-readiness",
    "implement",
    "qa",
]
FLOW_STAGE_INDEX = {stage: index for index, stage in enumerate(FLOW_STAGE_ORDER)}

DATA_ACCESS_STATUS_REQUIREMENTS = ADAPTER_RUNTIME.data_access_status_requirements()


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


def is_concrete_boundary(path: str) -> bool:
    if not path.startswith(BOUNDARY_PREFIX) or not path.endswith(".md"):
        return False
    if path in {CURRENT_BOUNDARY_FILE, LOCAL_CURRENT_BOUNDARY_FILE, f"{BOUNDARY_PREFIX}README.md"}:
        return False
    return True


def has_prefix(path: str, prefixes: tuple[str, ...]) -> bool:
    return any(path.startswith(prefix) for prefix in prefixes)


def is_generic_backend_path(path: str) -> bool:
    if has_prefix(path, BACKEND_IMPLEMENTATION_PREFIXES):
        return True
    parts = path.split("/")
    if len(parts) < 3 or parts[0] != "stack":
        return False
    return any(part in {"backend", "server", "api", "service"} for part in parts[2:-1])


def is_frontend_path(path: str) -> bool:
    if has_prefix(path, FRONTEND_HINT_PREFIXES):
        return True
    parts = path.split("/")
    return len(parts) >= 3 and parts[0] in {"stack", "baseline"} and any(
        part in {"frontend", "public", "app"} for part in parts[2:-1]
    )


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
        text = read_text(path) or ""
        return bool(DATA_KNOWLEDGE_SCHEMA_RE.search(text))
    return False


def read_text(path: str) -> str | None:
    file_path = REPO_ROOT / path
    if not file_path.exists():
        return None
    return file_path.read_text(encoding="utf-8")


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
        return None, [f"{source_label} must point to a boundary under `{BOUNDARY_PREFIX}`."]
    if relative in {CURRENT_BOUNDARY_FILE, LOCAL_CURRENT_BOUNDARY_FILE}:
        return None, [f"{source_label} must point to a concrete boundary file."]
    if not (REPO_ROOT / relative).exists():
        return None, [f"{source_label} points to missing boundary `{relative}`."]
    return relative, []


def parse_boundary_pointer_file(path: str) -> tuple[str | None, list[str]]:
    text = read_text(path)
    if text is None:
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
        if match:
            active_links.append(match.group("href"))

    if not active_links:
        return None, []
    if len(active_links) > 1:
        return None, [f"`{path}` declares multiple active boundaries."]
    href_path = (Path(path).parent / active_links[0]).as_posix()
    return resolve_boundary_reference(href_path, f"`{path}` Active Boundary")


def resolve_active_boundary() -> tuple[str | None, str | None, list[str]]:
    env_value = os.environ.get(ACTIVE_BOUNDARY_ENV, "").strip()
    if env_value:
        boundary, warnings = resolve_boundary_reference(
            env_value, f"Environment variable `{ACTIVE_BOUNDARY_ENV}`"
        )
        return boundary, f"env:{ACTIVE_BOUNDARY_ENV}", warnings

    if (REPO_ROOT / LOCAL_CURRENT_BOUNDARY_FILE).exists():
        boundary, warnings = parse_boundary_pointer_file(LOCAL_CURRENT_BOUNDARY_FILE)
        return boundary, LOCAL_CURRENT_BOUNDARY_FILE, warnings

    boundary, warnings = parse_boundary_pointer_file(CURRENT_BOUNDARY_FILE)
    if boundary:
        warnings.append(
            f"Using legacy shared pointer `{CURRENT_BOUNDARY_FILE}`; prefer local active boundary."
        )
        return boundary, CURRENT_BOUNDARY_FILE, warnings
    return None, None, warnings


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


def parse_required_flow_statuses(text: str) -> dict[str, str]:
    statuses: dict[str, str] = {}
    current_stage: str | None = None
    for raw_line in section_lines(text, "GStack Required Flow"):
        stripped = raw_line.strip()
        stage_match = re.match(r"^-\s*(?P<stage>[a-z0-9/-]+):\s*$", stripped)
        if stage_match:
            current_stage = stage_match.group("stage")
            continue
        if current_stage:
            status_match = re.match(r"^status:\s*`?(?P<status>[a-z-]+)", stripped)
            if status_match:
                statuses[current_stage] = status_match.group("status")
    return statuses


def clean_value(value: str) -> str:
    return value.strip().strip('"').strip("'").strip()


def parse_required_gates(text: str) -> list[dict[str, str]]:
    lines = section_lines(text, "Required Gates")
    gates: list[dict[str, str]] = []
    current: dict[str, str] | None = None

    for raw_line in lines:
        line = raw_line.strip()
        if not line or line in {"```yaml", "```"} or line == "required_gates:":
            continue
        item_match = re.match(r"^-\s*(?P<key>[a-z_]+):\s*(?P<value>.*)$", line)
        field_match = re.match(r"^(?P<key>[a-z_]+):\s*(?P<value>.*)$", line)
        if item_match:
            if current:
                gates.append(current)
            current = {item_match.group("key"): clean_value(item_match.group("value"))}
            continue
        if field_match and current is not None:
            current[field_match.group("key")] = clean_value(field_match.group("value"))
    if current:
        gates.append(current)
    return gates


def validate_gate(boundary: str, gate: dict[str, str]) -> list[str]:
    gate_id = gate.get("gate_id", "<missing-gate-id>")
    warnings: list[str] = []
    missing = sorted(REQUIRED_GATE_KEYS - set(gate))
    if missing:
        warnings.append(f"{boundary}: gate `{gate_id}` missing keys: {', '.join(missing)}.")

    status = gate.get("status", "")
    owner = gate.get("owner", "")
    required_before = gate.get("required_before", "")
    evidence_path = gate.get("evidence_path", "")
    trigger_reason = gate.get("trigger_reason", "")
    blocking_reason = gate.get("blocking_reason", "")
    done_criteria = gate.get("done_criteria", "")

    if status and status not in ALLOWED_STATUSES:
        warnings.append(f"{boundary}: gate `{gate_id}` has invalid status `{status}`.")
    if owner and owner not in ALLOWED_OWNERS:
        warnings.append(f"{boundary}: gate `{gate_id}` has invalid owner `{owner}`.")
    if required_before and required_before not in ALLOWED_REQUIRED_BEFORE:
        warnings.append(f"{boundary}: gate `{gate_id}` has invalid required_before `{required_before}`.")
    if status == "done":
        if not evidence_path or evidence_path == "待补":
            warnings.append(f"{boundary}: gate `{gate_id}` is done but evidence_path is not set.")
        elif not (REPO_ROOT / evidence_path).exists():
            warnings.append(f"{boundary}: gate `{gate_id}` evidence missing: `{evidence_path}`.")
    if status == "not-required" and (not trigger_reason or trigger_reason in {"无", "n/a", "NA"}):
        warnings.append(f"{boundary}: gate `{gate_id}` not-required must explain trigger_reason.")
    if status in {"blocked", "deferred"} and not blocking_reason:
        warnings.append(f"{boundary}: gate `{gate_id}` {status} must include blocking_reason.")
    if gate_id == "prototype-logic-extraction":
        warnings.extend(validate_prototype_logic_gate(boundary, gate))
    if gate_id == "data-knowledge-sync":
        if owner and owner not in {"kk-doc-sync", "kk-doc-backfill"}:
            warnings.append(
                f"{boundary}: gate `data-knowledge-sync` owner should be `kk-doc-sync` or `kk-doc-backfill`, got `{owner}`."
            )
        if required_before and required_before not in {"review", "qa"}:
            warnings.append(
                f"{boundary}: gate `data-knowledge-sync` required_before should usually be `review` or `qa`, got `{required_before}`."
            )
    if not done_criteria:
        warnings.append(f"{boundary}: gate `{gate_id}` missing done_criteria.")
    return warnings


def validate_prototype_logic_gate(boundary: str, gate: dict[str, str]) -> list[str]:
    warnings: list[str] = []
    status = gate.get("status", "")
    owner = gate.get("owner", "")
    required_before = gate.get("required_before", "")
    evidence_path = gate.get("evidence_path", "")
    trigger_reason = gate.get("trigger_reason", "")
    blocking_reason = gate.get("blocking_reason", "")

    if owner and owner != "kk-task-kickoff":
        warnings.append(
            f"{boundary}: gate `prototype-logic-extraction` owner must be `kk-task-kickoff`, got `{owner}`."
        )
    if required_before and required_before != "plan-eng-review":
        warnings.append(
            f"{boundary}: gate `prototype-logic-extraction` required_before must be `plan-eng-review`, got `{required_before}`."
        )
    if status in {"planned", "done", "blocked", "deferred"} and (
        not evidence_path or evidence_path == "待补"
    ):
        warnings.append(
            f"{boundary}: gate `prototype-logic-extraction` is {status} but evidence_path is not set."
        )
    if status == "not-required" and (
        not trigger_reason or trigger_reason in {"无", "n/a", "NA", "不涉及"}
    ):
        warnings.append(
            f"{boundary}: gate `prototype-logic-extraction` not-required must explain why frontend/prototype logic is excluded."
        )
    if status == "deferred":
        required_words = ("批准", "风险")
        missing_words = [word for word in required_words if word not in blocking_reason]
        if missing_words:
            warnings.append(
                f"{boundary}: gate `prototype-logic-extraction` deferred blocking_reason must include approval source and risk."
            )
        if "删除条件" not in blocking_reason and "补齐" not in blocking_reason:
            warnings.append(
                f"{boundary}: gate `prototype-logic-extraction` deferred blocking_reason must include deletion criteria or follow-up completion path."
            )
    if status != "not-required" and evidence_path and evidence_path != "待补" and not has_prefix(
        evidence_path, PROTOTYPE_LOGIC_EVIDENCE_PREFIXES
    ):
        warnings.append(
            f"{boundary}: gate `prototype-logic-extraction` evidence_path `{evidence_path}` should be repo-native design, knowledge, baseline, or stack evidence."
        )
    return warnings


def validate_gate_flow_conflicts(
    boundary: str, gates: list[dict[str, str]], flow_statuses: dict[str, str]
) -> list[str]:
    warnings: list[str] = []
    if not flow_statuses:
        return warnings
    implement_status = flow_statuses.get("implement")
    for gate in gates:
        gate_id = gate.get("gate_id", "<missing-gate-id>")
        status = gate.get("status", "")
        required_before = gate.get("required_before", "")
        required_index = FLOW_STAGE_INDEX.get(required_before)
        if status in {"blocked", "planned"} and implement_status in {"in-progress", "done"}:
            warnings.append(
                f"{boundary}: gate `{gate_id}` is {status}, but GStack Required Flow implement is `{implement_status}`."
            )
        if required_index is None:
            continue
        for stage, stage_status in flow_statuses.items():
            stage_index = FLOW_STAGE_INDEX.get(stage)
            if stage_index is None:
                continue
            if stage_index >= required_index and stage_status == "done" and status == "planned":
                warnings.append(
                    f"{boundary}: gate `{gate_id}` is still planned after `{stage}` reached done; required_before is `{required_before}`."
                )
                break
    return warnings


def matching_data_access_requirements(files: list[str]) -> list[tuple[set[str], str]]:
    matches: list[tuple[set[str], str]] = []
    for prefixes, statuses, reason in DATA_ACCESS_STATUS_REQUIREMENTS:
        if any(has_prefix(path, prefixes) for path in files):
            matches.append((statuses, reason))
    return matches


def prototype_logic_trigger_files(files: list[str], boundary_text: str | None) -> list[str]:
    backend_files = [path for path in files if is_generic_backend_path(path) and not path.endswith(".md")]
    frontend_files = [path for path in files if is_frontend_path(path) and not path.endswith(".md")]
    triggers: list[str] = []
    if backend_files and frontend_files:
        triggers.extend(backend_files + frontend_files)
    if boundary_text and backend_files:
        lowered = boundary_text.lower()
        source_hit = any(hint.lower() in lowered for hint in PROTOTYPE_SOURCE_HINTS)
        required_hit = any(hint.lower() in lowered for hint in PROTOTYPE_REQUIRED_HINTS)
        if source_hit and required_hit:
            triggers.extend(backend_files)
    return sorted(set(triggers))


def audit_boundary(boundary: str) -> tuple[list[dict[str, str]], list[str]]:
    text = read_text(boundary)
    if text is None:
        return [], [f"Boundary missing: `{boundary}`."]
    gates = parse_required_gates(text)
    warnings: list[str] = []
    if not gates:
        warnings.append(f"{boundary}: missing parsable `## Required Gates` block.")
        return gates, warnings
    seen: set[str] = set()
    for gate in gates:
        gate_id = gate.get("gate_id", "")
        if gate_id in seen:
            warnings.append(f"{boundary}: duplicate gate_id `{gate_id}`.")
        seen.add(gate_id)
        warnings.extend(validate_gate(boundary, gate))
    warnings.extend(validate_gate_flow_conflicts(boundary, gates, parse_required_flow_statuses(text)))
    return gates, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Required Gates blocks. Warning-first.")
    parser.add_argument("--base", default="HEAD", help="Git base ref for changed-file scan.")
    parser.add_argument("--boundary", action="append", default=[], help="Concrete boundary to audit.")
    args = parser.parse_args()

    if not inside_git_worktree():
        active_boundary, active_source, warnings = resolve_active_boundary()
        boundaries = list(dict.fromkeys(args.boundary + ([active_boundary] if active_boundary else [])))
        print("[required-gates] git state: not a git worktree; running static boundary audit")
        print("[required-gates] active boundary:", active_boundary or "unresolved")
        print("[required-gates] active boundary source:", active_source or "none")
        print("[required-gates] audited boundaries:")
        if boundaries:
            for boundary in boundaries:
                print(f"  - {boundary}")
        else:
            print("  - none")

        for boundary in boundaries:
            _gates, boundary_warnings = audit_boundary(boundary)
            warnings.extend(boundary_warnings)

        if warnings:
            print("\n[required-gates] WARN:")
            for warning in warnings:
                print(f"  - {warning}")
            print("\n[required-gates] static warning-first mode: returning success.")
            return 0

        print("\n[required-gates] PASS: static Required Gates audit passed.")
        return 0

    try:
        files = changed_files(args.base)
    except RuntimeError as exc:
        print(f"[required-gates] failed to inspect git state: {exc}", file=sys.stderr)
        return 2

    active_boundary, active_source, warnings = resolve_active_boundary()
    changed_boundaries = [
        path
        for path in files
        if is_concrete_boundary(path)
    ]
    boundaries = list(
        dict.fromkeys(args.boundary + changed_boundaries + ([active_boundary] if active_boundary else []))
    )
    data_trigger_files = [path for path in files if has_prefix(path, DATA_ACCESS_TRIGGER_PREFIXES)]
    data_knowledge_trigger_files = [path for path in files if looks_like_data_knowledge_path(path)]
    active_boundary_text = read_text(active_boundary) if active_boundary else None
    prototype_trigger_files = prototype_logic_trigger_files(files, active_boundary_text)

    print("[required-gates] changed files:", len(files))
    print("[required-gates] active boundary:", active_boundary or "unresolved")
    print("[required-gates] active boundary source:", active_source or "none")
    print("[required-gates] audited boundaries:")
    if boundaries:
        for boundary in boundaries:
            print(f"  - {boundary}")
    else:
        print("  - none")

    all_gates: dict[str, list[dict[str, str]]] = {}
    for boundary in boundaries:
        gates, boundary_warnings = audit_boundary(boundary)
        all_gates[boundary] = gates
        warnings.extend(boundary_warnings)

    if data_trigger_files:
        print("[required-gates] data-access trigger files:")
        for path in data_trigger_files[:20]:
            print(f"  - {path}")
        if active_boundary:
            active_gates = all_gates.get(active_boundary, [])
            data_access = [gate for gate in active_gates if gate.get("gate_id") == "data-access"]
            if not data_access:
                warnings.append(
                    f"Data-related diff detected, but active boundary `{active_boundary}` has no `data-access` gate."
                )
            else:
                data_access_gate = data_access[0]
                status = data_access_gate.get("status", "")
                required_before = data_access_gate.get("required_before", "")
                for allowed_statuses, reason in matching_data_access_requirements(data_trigger_files):
                    if status not in allowed_statuses:
                        warnings.append(
                            f"Data-related diff rule violation for active boundary `{active_boundary}`: "
                            f"{reason}; current data-access status is `{status}`."
                        )
                if any(
                    path == ".gstack/templates/data-interface-design.template.md"
                    for path in data_trigger_files
                ):
                    if required_before not in {"requirement-brief", "plan-ceo-review", "requirement-freeze", "plan-eng-review"}:
                        warnings.append(
                            f"Data-interface design changed, but data-access required_before is `{required_before}`; "
                            "it must be no later than `plan-eng-review`."
                        )
        else:
            warnings.append("Data-related diff detected, but no active boundary could be resolved.")

    if prototype_trigger_files:
        print("[required-gates] prototype-logic-extraction trigger files:")
        for path in prototype_trigger_files[:20]:
            print(f"  - {path}")
        if active_boundary:
            active_gates = all_gates.get(active_boundary, [])
            prototype_gates = [
                gate for gate in active_gates if gate.get("gate_id") == "prototype-logic-extraction"
            ]
            if not prototype_gates:
                warnings.append(
                    f"Frontend/prototype-to-backend diff detected, but active boundary `{active_boundary}` has no `prototype-logic-extraction` gate."
                )
            else:
                gate = prototype_gates[0]
                status = gate.get("status", "")
                if status == "not-required":
                    warnings.append(
                        f"Active boundary `{active_boundary}` marks `prototype-logic-extraction` not-required while trigger files were detected; review the exclusion reason."
                    )
                elif status == "planned":
                    warnings.append(
                        f"Active boundary `{active_boundary}` still has `prototype-logic-extraction` planned; evidence must be done / blocked / deferred before plan-eng-review."
                    )
        else:
            warnings.append(
                "Frontend/prototype-to-backend diff detected, but no active boundary could be resolved."
            )

    if data_knowledge_trigger_files:
        print("[required-gates] data-knowledge-sync trigger files:")
        for path in data_knowledge_trigger_files[:20]:
            print(f"  - {path}")
        if active_boundary:
            active_gates = all_gates.get(active_boundary, [])
            sync_gates = [
                gate for gate in active_gates if gate.get("gate_id") == "data-knowledge-sync"
            ]
            if not sync_gates:
                warnings.append(
                    f"Data knowledge sync diff detected, but active boundary `{active_boundary}` has no `data-knowledge-sync` gate."
                )
            else:
                status = sync_gates[0].get("status", "")
                if status == "planned":
                    warnings.append(
                        f"Data knowledge sync diff detected while active boundary `{active_boundary}` still has `data-knowledge-sync` planned; finish evidence before review."
                    )
        else:
            warnings.append("Data knowledge sync diff detected, but no active boundary could be resolved.")

    if warnings:
        print("\n[required-gates] WARN:")
        for warning in warnings:
            print(f"  - {warning}")
        print("\n[required-gates] warning-first mode: returning success while rules stabilize.")
        return 0

    print("\n[required-gates] PASS: Required Gates blocks are parseable.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
