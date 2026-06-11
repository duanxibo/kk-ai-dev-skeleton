#!/usr/bin/env python3
"""Render a generated gstack task dashboard.

The dashboard is a read-only view over repo-native evidence. It intentionally
does not write .gstack/dashboard.* or any shared aggregate status file.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
BOUNDARY_DIR = REPO_ROOT / ".gstack" / "task-boundaries"
DEFAULT_HTML_OUTPUT = REPO_ROOT / "output" / "gstack-dashboard" / "latest.html"
LOCAL_POINTER = BOUNDARY_DIR / "CURRENT.local.md"
SHARED_POINTER = BOUNDARY_DIR / "CURRENT.md"
ACTIVE_BOUNDARY_ENV = "KK_ACTIVE_BOUNDARY"
BOUNDARY_LINK_RE = re.compile(r"\[(?P<label>[^\]]+)\]\((?P<href>[^)]+)\)")
FLOW_SEQUENCE = (
    "requirement-brief",
    "plan-ceo-review",
    "requirement-freeze",
    "plan-eng-review",
    "domain-spec-readiness",
    "implement",
    "qa",
)
FLOW_STAGE_DETAILS = {
    "requirement-brief": ("需求说明", "写清任务目标、范围和最小验收标准"),
    "plan-ceo-review": ("产品评审", "确认目标值得做，范围不跑偏"),
    "requirement-freeze": ("需求 / 原型冻结", "确认本轮边界可以进入工程实现"),
    "plan-eng-review": ("工程评审", "确认实现路径、风险和验证计划"),
    "domain-spec-readiness": ("规格就绪", "确认需要同步的真源文档已明确或不需要变更"),
    "implement": ("实现", "按任务边界修改代码、脚本或文档"),
    "qa": ("验收", "运行验证并沉淀 QA evidence"),
}
STATUS_LABELS = {
    "done": "已完成",
    "not-required": "不需要",
    "pending": "待处理",
    "missing": "缺失",
    "planned": "已计划",
    "blocked": "卡住",
    "deferred": "延后",
    "in-progress": "进行中",
}


@dataclass(frozen=True)
class StageSummary:
    key: str
    label: str
    description: str
    status: str
    status_label: str
    evidence: str


@dataclass(frozen=True)
class TaskSummary:
    boundary: str
    task: str
    owner: str
    owner_source: str
    lane: str
    mode: str
    current_step_key: str
    current_step_label: str
    current_step: str
    progress: str
    next_step: str
    next_step_label: str
    qa_status: str
    implement_status: str
    blocked: bool
    blocked_reasons: list[str]
    stages: list[StageSummary]
    active: bool
    evidence_missing: list[str]


@dataclass(frozen=True)
class DashboardFilters:
    limit: int | None
    active_only: bool
    open_only: bool
    blocked_only: bool
    stage: str
    query: str
    sort: str


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def clean(raw: str) -> str:
    return raw.strip().strip("`").strip('"').strip("'").strip()


def normalize_status(raw: str) -> str:
    value = clean(raw)
    normalized = value.lower()
    for status in sorted(STATUS_LABELS, key=len, reverse=True):
        if normalized == status:
            return status
        suffix = normalized[len(status) : len(status) + 1]
        if normalized.startswith(status) and suffix in {"`", " ", ",", "，", ".", "。", ":", "：", ";", "；"}:
            return status
    return value


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


def parse_active_links(pointer: Path) -> list[str]:
    if not pointer.exists():
        return []
    active_links: list[str] = []
    in_active_section = False
    for line in read_text(pointer).splitlines():
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
    return active_links


def resolve_boundary_reference(raw_ref: str, pointer: Path | None) -> Path | None:
    raw = Path(raw_ref.strip())
    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        if pointer is not None:
            candidates.append(pointer.parent / raw)
        candidates.append(REPO_ROOT / raw)
        candidates.append(BOUNDARY_DIR / raw)
        candidates.append(BOUNDARY_DIR / raw.name)

    for candidate in candidates:
        resolved = candidate.resolve()
        try:
            relative = resolved.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            continue
        if (
            relative.startswith(".gstack/task-boundaries/")
            and resolved.exists()
            and resolved.name not in {"CURRENT.md", "CURRENT.local.md", "README.md"}
        ):
            return resolved
    return None


def active_boundary() -> Path | None:
    env_value = os.environ.get(ACTIVE_BOUNDARY_ENV, "").strip()
    if env_value:
        return resolve_boundary_reference(env_value, None)

    pointer = LOCAL_POINTER if LOCAL_POINTER.exists() else SHARED_POINTER
    links = parse_active_links(pointer)
    if len(links) != 1:
        return None
    return resolve_boundary_reference(links[0], pointer)


def boundary_files() -> list[Path]:
    excluded = {"CURRENT.md", "CURRENT.local.md", "README.md"}
    return sorted(
        (
            path
            for path in BOUNDARY_DIR.glob("*.md")
            if path.name not in excluded and path.is_file()
        ),
        key=lambda path: path.name,
        reverse=True,
    )


def parse_bullet_field(lines: list[str], key: str) -> str:
    pattern = re.compile(rf"^\s*-\s*{re.escape(key)}\s*[:：]\s*(?P<value>.*?)\s*$")
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match:
            continue
        value = clean(match.group("value"))
        if value:
            return value
        for follow in lines[index + 1 :]:
            stripped = follow.strip()
            if not stripped:
                continue
            if stripped.startswith("- "):
                return ""
            return clean(stripped)
    return ""


def parse_section_field_items(text: str, header: str, key: str) -> list[str]:
    items: list[str] = []
    in_field = False
    pattern = re.compile(rf"^\s*-\s*{re.escape(key)}\s*[:：]\s*(?P<value>.*?)\s*$")
    for line in section_lines(text, header):
        match = pattern.match(line)
        if match:
            in_field = True
            inline_value = clean(match.group("value"))
            if inline_value:
                items.append(inline_value)
            continue
        if not in_field:
            continue
        if line.startswith("- "):
            break
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("- "):
            items.append(clean(stripped[2:]))
        else:
            items.append(clean(stripped))
    return [item for item in items if item]


def parse_section_field_value(text: str, header: str, key: str) -> str:
    values = parse_section_field_items(text, header, key)
    return values[0] if values else ""


def parse_header_field(text: str, keys: list[str]) -> str:
    key_pattern = "|".join(re.escape(key) for key in keys)
    pattern = re.compile(rf"^\s*-\s*(?:{key_pattern})\s*[:：]\s*(?P<value>.*?)\s*$", re.I)
    lines = text.splitlines()[:20]
    for index, line in enumerate(lines):
        match = pattern.match(line)
        if not match:
            continue
        value = clean(match.group("value"))
        if value:
            return value
        for follow in lines[index + 1 :]:
            stripped = follow.strip()
            if not stripped:
                continue
            if stripped.startswith("- "):
                return ""
            return clean(stripped)
    return ""


def parse_required_flow(text: str) -> dict[str, dict[str, str]]:
    records: dict[str, dict[str, str]] = {}
    current: str | None = None
    stage_re = re.compile(r"^\s*-\s*(?P<name>[a-z0-9/-]+):\s*(?P<value>.*?)\s*$", re.I)
    field_re = re.compile(r"^\s*(?P<key>status|command|evidence|note):\s*(?P<value>.*?)\s*$", re.I)

    for line in section_lines(text, "GStack Required Flow"):
        stage_match = stage_re.match(line)
        if stage_match:
            current = stage_match.group("name")
            records.setdefault(current, {})
            inline_value = clean(stage_match.group("value"))
            if inline_value:
                records[current]["status"] = normalize_status(inline_value)
            continue
        if current is None:
            continue
        field_match = field_re.match(line)
        if field_match:
            key = field_match.group("key").lower()
            value = clean(field_match.group("value"))
            records[current][key] = normalize_status(value) if key == "status" else value
    return records


def parse_required_gates(text: str) -> list[dict[str, str]]:
    gates: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    gate_re = re.compile(r"^\s*-\s*gate_id\s*:\s*(?P<value>.*?)\s*$", re.I)
    field_re = re.compile(
        r"^\s*(?P<key>trigger_reason|owner|required_before|status|evidence_path|evidence_section|blocking_reason|done_criteria)\s*:\s*(?P<value>.*?)\s*$",
        re.I,
    )

    for line in section_lines(text, "Required Gates"):
        if line.strip().startswith("```"):
            continue
        gate_match = gate_re.match(line)
        if gate_match:
            current = {"gate_id": clean(gate_match.group("value"))}
            gates.append(current)
            continue
        if current is None:
            continue
        field_match = field_re.match(line)
        if field_match:
            key = field_match.group("key").lower()
            value = clean(field_match.group("value"))
            current[key] = normalize_status(value) if key == "status" else value
    return gates


def stage_status(records: dict[str, dict[str, str]], stage: str) -> str:
    return records.get(stage, {}).get("status", "missing")


def status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status or "未知")


def stage_label(stage: str) -> str:
    return FLOW_STAGE_DETAILS.get(stage, (stage, ""))[0]


def stage_description(stage: str) -> str:
    return FLOW_STAGE_DETAILS.get(stage, ("", ""))[1]


def display_evidence_path(raw: str) -> str:
    return "；".join(evidence_path_tokens(raw))


def evidence_path_tokens(raw: str) -> list[str]:
    value = clean(raw)
    if not value or "<" in value or ">" in value:
        return []
    if value.lower() in {"none", "n/a", "null", "待补", "不适用"}:
        return []

    normalized = value.replace("`", " ")
    tokens: list[str] = []
    for part in re.split(r"[\s,，;；]+", normalized):
        token = part.strip().strip("`'\"").rstrip(".,，;；")
        if not token:
            continue
        if token.lower() in {"none", "n/a", "null", "待补", "不适用"}:
            continue
        if token.startswith(("http://", "https://")):
            continue
        if "/" not in token and not Path(token).suffix:
            continue
        tokens.append(token)
    return tokens


def evidence_missing(records: dict[str, dict[str, str]]) -> list[str]:
    missing: list[str] = []
    for stage, record in records.items():
        status = record.get("status", "")
        if status not in {"done", "not-required"}:
            continue
        for evidence in evidence_path_tokens(record.get("evidence", "")):
            if not (REPO_ROOT / evidence).exists():
                missing.append(f"{stage}: {evidence}")
    return missing


def next_step(records: dict[str, dict[str, str]]) -> str:
    for stage in FLOW_SEQUENCE:
        status = stage_status(records, stage)
        if status not in {"done", "not-required"}:
            return stage
    return "complete"


def next_step_label(records: dict[str, dict[str, str]]) -> str:
    step = next_step(records)
    if step == "complete":
        return "全部完成"
    return stage_label(step)


def current_step(records: dict[str, dict[str, str]]) -> str:
    step = next_step(records)
    if step == "complete":
        return "全部完成"
    status = stage_status(records, step)
    return f"{stage_label(step)}（{status_label(status)}）"


def summarize_stages(records: dict[str, dict[str, str]]) -> list[StageSummary]:
    stages: list[StageSummary] = []
    for stage in FLOW_SEQUENCE:
        record = records.get(stage, {})
        status = record.get("status", "missing")
        stages.append(
            StageSummary(
                key=stage,
                label=stage_label(stage),
                description=stage_description(stage),
                status=status,
                status_label=status_label(status),
                evidence=display_evidence_path(record.get("evidence", "")),
            )
        )
    return stages


def progress(records: dict[str, dict[str, str]]) -> str:
    completed = sum(1 for stage in FLOW_SEQUENCE if stage_status(records, stage) in {"done", "not-required"})
    return f"{completed}/{len(FLOW_SEQUENCE)}"


def blocked_reasons(records: dict[str, dict[str, str]], gates: list[dict[str, str]]) -> list[str]:
    reasons: list[str] = []
    for stage, record in records.items():
        if record.get("status") != "blocked":
            continue
        reason = record.get("note") or record.get("evidence") or "blocked"
        reasons.append(f"flow {stage}: {reason}")
    for gate in gates:
        if gate.get("status") != "blocked":
            continue
        gate_id = gate.get("gate_id") or "unknown-gate"
        reason = gate.get("blocking_reason") or gate.get("trigger_reason") or "blocked"
        reasons.append(f"gate {gate_id}: {reason}")
    return reasons


def first_task_line(text: str, path: Path) -> str:
    task = parse_header_field(text, ["Task", "任务"])
    if task:
        return task
    for line in text.splitlines()[:12]:
        match = re.match(r"^\s*-\s*Task\s*[:：]\s*(?P<value>.+?)\s*$", line)
        if match:
            return clean(match.group("value"))
    for line in text.splitlines()[:3]:
        if line.startswith("# "):
            return clean(line[2:])
    return path.stem


def owner_and_source(text: str) -> tuple[str, str]:
    owner = parse_header_field(text, ["负责人", "Owner"])
    if owner:
        return owner, "来自 task boundary 顶部的负责人字段，不是 git 提交人"
    return "未填写", "task boundary 顶部没有负责人字段"


def summarize_boundary(path: Path, active: Path | None) -> TaskSummary:
    text = read_text(path)
    records = parse_required_flow(text)
    gates = parse_required_gates(text)
    blockers = blocked_reasons(records, gates)
    lane = parse_bullet_field(section_lines(text, "Flow Lane"), "Lane") or "unknown"
    mode = parse_bullet_field(section_lines(text, "Decision Mode"), "Mode") or "unknown"
    owner, owner_source = owner_and_source(text)
    next_key = next_step(records)
    return TaskSummary(
        boundary=repo_relative(path),
        task=first_task_line(text, path),
        owner=owner,
        owner_source=owner_source,
        lane=lane,
        mode=mode,
        current_step_key=next_key,
        current_step_label=current_step(records),
        current_step=current_step(records),
        progress=progress(records),
        next_step=next_key,
        next_step_label=next_step_label(records),
        qa_status=stage_status(records, "qa"),
        implement_status=stage_status(records, "implement"),
        blocked=bool(blockers),
        blocked_reasons=blockers,
        stages=summarize_stages(records),
        active=bool(active and path.resolve() == active.resolve()),
        evidence_missing=evidence_missing(records),
    )


def task_is_open(summary: TaskSummary) -> bool:
    return summary.current_step_key != "complete"


def task_matches_query(summary: TaskSummary, query: str) -> bool:
    normalized_query = query.strip().lower()
    if not normalized_query:
        return True
    haystack = " ".join(
        [
            summary.task,
            summary.owner,
            summary.boundary,
            summary.current_step,
            summary.lane,
            summary.mode,
        ]
    ).lower()
    return normalized_query in haystack


def apply_filters(summaries: list[TaskSummary], filters: DashboardFilters) -> list[TaskSummary]:
    result: list[TaskSummary] = []
    for summary in summaries:
        if filters.active_only and not summary.active:
            continue
        if filters.open_only and not task_is_open(summary):
            continue
        if filters.blocked_only and not summary.blocked:
            continue
        if filters.stage and summary.current_step_key != filters.stage:
            continue
        if not task_matches_query(summary, filters.query):
            continue
        result.append(summary)
    return result


def sort_summaries(summaries: list[TaskSummary], sort: str) -> list[TaskSummary]:
    if sort == "task":
        return sorted(summaries, key=lambda item: (not item.active, item.task.lower(), item.boundary))
    if sort == "recent":
        return sorted(summaries, key=lambda item: not item.active)
    return sorted(
        summaries,
        key=lambda item: (
            not item.active,
            not item.blocked,
            not task_is_open(item),
        ),
    )


def stage_filter_label(stage: str) -> str:
    if stage == "complete":
        return "全部完成"
    return stage_label(stage) if stage else "全部阶段"


def filter_summary(filters: dict[str, object]) -> str:
    parts: list[str] = []
    if filters.get("active_only"):
        parts.append("只看当前任务")
    if filters.get("open_only"):
        parts.append("只看未完成")
    if filters.get("blocked_only"):
        parts.append("只看卡住")
    stage = str(filters.get("stage") or "")
    if stage:
        parts.append(f"阶段：{stage_filter_label(stage)}")
    query = str(filters.get("query") or "")
    if query:
        parts.append(f"关键词：{query}")
    parts.append(f"排序：{filters.get('sort')}")
    return "；".join(parts)


def dashboard_payload(
    *,
    limit: int | None,
    active_only: bool,
    open_only: bool,
    blocked_only: bool,
    stage: str,
    query: str,
    sort: str,
) -> dict[str, object]:
    active = active_boundary()
    files = [active] if active_only and active else boundary_files()
    summaries = [summarize_boundary(path, active) for path in files if path is not None]
    filters = DashboardFilters(
        limit=limit,
        active_only=active_only,
        open_only=open_only,
        blocked_only=blocked_only,
        stage=stage,
        query=query.strip(),
        sort=sort,
    )
    filtered_summaries = apply_filters(summaries, filters)
    visible_summaries = sort_summaries(filtered_summaries, sort)
    if limit is not None:
        visible_summaries = visible_summaries[:limit]
    return {
        "generated_view": True,
        "conflict_policy": "Do not commit shared dashboard/status aggregate files; regenerate this view from repo-native evidence.",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "active_boundary": repo_relative(active) if active else None,
        "total_tasks": len(summaries),
        "matched_tasks": len(filtered_summaries),
        "visible_tasks": len(visible_summaries),
        "filters": asdict(filters),
        "tasks": [asdict(summary) for summary in visible_summaries],
    }


def table_escape(raw: str) -> str:
    return raw.replace("|", "\\|").replace("\n", " ")


def render_markdown(payload: dict[str, object]) -> str:
    tasks = payload["tasks"]
    assert isinstance(tasks, list)
    filters = payload.get("filters", {})
    assert isinstance(filters, dict)
    lines = [
        "# 任务状态",
        "",
        "本页是生成视图，只读取本机仓库当前分支上的 repo-native evidence；不要提交 `.gstack/dashboard.*` 或共享 status 聚合文件。",
        "",
        "负责人来自 task boundary 顶部的 `负责人` / `Owner` 字段，不是 git 提交人。",
        "",
        f"- 本机当前任务: `{payload['active_boundary'] or 'none'}`",
        f"- 生成时间: `{payload['generated_at']}`",
        f"- 筛选条件: {filter_summary(filters)}",
        f"- 匹配任务: `{payload.get('visible_tasks', len(tasks))}/{payload.get('matched_tasks', len(tasks))}`，总任务: `{payload.get('total_tasks', len(tasks))}`",
        "",
    ]
    if not tasks:
        lines.extend(["没有匹配的任务。"])
        return "\n".join(lines)
    lines.extend(
        [
            "| 当前 | 任务 | 负责人 | 负责人来源 | 当前阶段 | 进度 | 是否卡住 | 7 个阶段 | 任务文档 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for item in tasks:
        assert isinstance(item, dict)
        stages = item.get("stages", [])
        assert isinstance(stages, list)
        stage_summary = "；".join(
            f"{stage.get('label', '')}: {stage.get('status_label', '')}"
            for stage in stages
            if isinstance(stage, dict)
        )
        lines.append(
            "| {active} | {task} | {owner} | {owner_source} | {current_step} | `{progress}` | {blocked} | {stages} | `{boundary}` |".format(
                active="是" if item["active"] else "",
                task=table_escape(str(item["task"])),
                owner=table_escape(str(item["owner"])),
                owner_source=table_escape(str(item["owner_source"])),
                current_step=table_escape(str(item["current_step"])),
                progress=table_escape(str(item["progress"])),
                blocked="卡住" if item["blocked"] else "正常",
                stages=table_escape(stage_summary),
                boundary=table_escape(str(item["boundary"])),
            )
        )
        blockers = item.get("blocked_reasons", [])
        if blockers:
            lines.append(f"|  | 卡住原因: {table_escape('; '.join(map(str, blockers)))} |  |  |  |  |  |  |  |")
        missing = item.get("evidence_missing", [])
        if missing:
            lines.append(f"|  | 证据缺失: {table_escape(', '.join(map(str, missing)))} |  |  |  |  |  |  |  |")
    return "\n".join(lines)


def render_explanation(payload: dict[str, object]) -> str:
    tasks = payload["tasks"]
    assert isinstance(tasks, list)
    filters = payload.get("filters", {})
    assert isinstance(filters, dict)
    active_only = bool(filters.get("active_only"))

    if not tasks:
        if active_only and not payload.get("active_boundary"):
            return "\n".join(
                [
                    "当前没有设置本地任务。",
                    "下一步：让 Codex 先恢复或创建当前任务记录，然后再继续推进。",
                    "需要你确认：暂时不需要，除非要判断新的业务范围或生产操作。",
                ]
            )
        return "\n".join(
            [
                "当前没有匹配的任务。",
                "下一步：调整筛选条件，或让 Codex 检查本地任务记录是否已经同步。",
                "需要你确认：暂时不需要。",
            ]
        )

    lines: list[str] = []
    if not active_only:
        matched = int(payload.get("matched_tasks", len(tasks)))
        visible = int(payload.get("visible_tasks", len(tasks)))
        if visible == matched:
            lines.append(f"当前共找到 {visible} 个匹配任务。")
        else:
            lines.append(f"当前显示 {visible} 个匹配任务，共匹配 {matched} 个。")
        lines.append("")

    for item_index, item in enumerate(tasks, start=1):
        assert isinstance(item, dict)
        prefix = "" if active_only or len(tasks) == 1 else f"{item_index}. "
        task = str(item.get("task") or "未命名任务")
        progress_value = str(item.get("progress") or "0/7")
        current_step_key = str(item.get("current_step_key") or "")
        next_step_label_value = str(item.get("next_step_label") or item.get("current_step") or "未知")
        blocked = bool(item.get("blocked"))
        warnings = item.get("evidence_missing") or []
        reasons = item.get("blocked_reasons") or []

        if current_step_key == "complete":
            state_line = "已完成，没有卡住。"
            next_line = "下一步：这项任务已经收口，可以继续开启下一段改进。"
            confirm_line = "需要你确认：不需要。"
        elif blocked:
            state_line = f"还没完成，目前卡在 {next_step_label_value}。"
            reason_text = "；".join(human_blocker(reason) for reason in reasons) if reasons else "任务记录显示有卡住项，但没有写明原因"
            next_line = f"下一步：先处理卡住原因：{reason_text}。"
            confirm_line = "需要你确认：如果卡住原因涉及业务口径、真实数据、生产环境或权限，Codex 会单独问你；否则先由 Codex 继续处理。"
        else:
            state_line = f"还没完成，目前进行到 {next_step_label_value}。"
            next_line = f"下一步：继续完成 {next_step_label_value}。"
            confirm_line = "需要你确认：暂时不需要，Codex 可以继续推进。"

        lines.extend(
            [
                f"{prefix}当前任务：{task}",
                f"状态：{state_line}",
                f"进度：{progress_value} 个步骤。",
                next_line,
                confirm_line,
            ]
        )

        if warnings:
            lines.append(f"注意：内部证据有 {len(warnings)} 处找不到，完成判断可能不可靠，Codex 需要先修正记录。")

        if item_index != len(tasks):
            lines.append("")

    return "\n".join(lines)


def render_verification(payload: dict[str, object]) -> str:
    tasks = payload["tasks"]
    assert isinstance(tasks, list)
    filters = payload.get("filters", {})
    assert isinstance(filters, dict)
    active_only = bool(filters.get("active_only"))

    if not tasks:
        if active_only and not payload.get("active_boundary"):
            return "\n".join(
                [
                    "当前没有设置本地任务，所以还不能生成验收说明。",
                    "下一步：让 Codex 先恢复或创建当前任务记录。",
                ]
            )
        return "\n".join(
            [
                "当前没有匹配的任务，所以还不能生成验收说明。",
                "下一步：调整筛选条件，或让 Codex 检查本地任务记录是否已经同步。",
            ]
        )

    lines: list[str] = []
    if not active_only:
        matched = int(payload.get("matched_tasks", len(tasks)))
        visible = int(payload.get("visible_tasks", len(tasks)))
        lines.append(f"当前显示 {visible} 个任务的验收说明，共匹配 {matched} 个。")
        lines.append("")

    for item_index, item in enumerate(tasks, start=1):
        assert isinstance(item, dict)
        prefix = "" if active_only or len(tasks) == 1 else f"{item_index}. "
        task = str(item.get("task") or "未命名任务")
        boundary = str(item.get("boundary") or "")
        boundary_text = read_text(REPO_ROOT / boundary) if boundary and (REPO_ROOT / boundary).exists() else ""
        expected = parse_section_field_items(boundary_text, "User-visible Acceptance", "Expected Visible Behavior")
        actions = parse_section_field_items(boundary_text, "User-visible Acceptance", "User Actions To Verify")
        required_evidence = parse_section_field_items(boundary_text, "User-visible Acceptance", "Required Evidence")
        refresh = parse_section_field_value(boundary_text, "Generated Artifact Policy", "Refresh / Regeneration")
        no_visible = parse_section_field_value(boundary_text, "Generated Artifact Policy", "If No Visible Change")
        acceptance_url = parse_section_field_value(boundary_text, "Generated Artifact Policy", "Acceptance URL")
        qa_status = str(item.get("qa_status") or "missing")
        current_step_key = str(item.get("current_step_key") or "")
        qa_evidence = ""
        for stage in item.get("stages", []):
            if isinstance(stage, dict) and stage.get("key") == "qa":
                qa_evidence = str(stage.get("evidence") or "")
                break

        complete_line = "已完成，可以按下面步骤验收。" if current_step_key == "complete" else "还没有完成最终收口，下面是当前任务记录里的验收计划。"
        lines.extend(
            [
                f"{prefix}当前任务：{task}",
                f"完成状态：{complete_line}",
            ]
        )

        if acceptance_url and acceptance_url != "不适用":
            lines.append(f"查看位置：{plain_text(acceptance_url)}")

        lines.append("你可以这样验收：")
        for action in actions or ["查看本轮输出或让 Codex 按当前任务记录转述验收结果。"]:
            lines.append(f"- {plain_text(action)}")

        lines.append("预期应该看到：")
        for expectation in expected or ["当前任务记录没有写明可见预期，Codex 需要先补充验收口径。"]:
            lines.append(f"- {plain_text(expectation)}")

        if refresh and refresh != "不适用":
            lines.append(f"刷新或重新生成：{plain_text(refresh)}")

        if no_visible and no_visible != "不适用":
            lines.append(f"如果看不到变化：{plain_text(no_visible)}")

        qa_label = status_label(qa_status)
        if qa_status == "done":
            qa_line = "QA 已记录。"
        elif qa_status in {"planned", "pending", "missing"}:
            qa_line = "QA 还没完成，完成判断不能只靠口头说明。"
        else:
            qa_line = f"QA 状态是{qa_label}。"
        if qa_evidence:
            qa_line = f"{qa_line} 内部记录：{qa_evidence}"
        lines.append(f"验收证据：{qa_line}")

        if required_evidence:
            lines.append("需要保留的证据：")
            for evidence in required_evidence:
                lines.append(f"- {plain_text(evidence)}")

        warnings = item.get("evidence_missing") or []
        if warnings:
            lines.append(f"注意：内部证据有 {len(warnings)} 处找不到，验收说明可能不可靠，Codex 需要先修正记录。")

        if item_index != len(tasks):
            lines.append("")

    return "\n".join(lines)


def plain_text(raw: object) -> str:
    return str(raw).replace("`", "")


def human_blocker(raw: object) -> str:
    text = str(raw)
    flow_match = re.match(r"^flow\s+(?P<stage>[a-z0-9/-]+):\s*(?P<reason>.*)$", text)
    if flow_match:
        stage = flow_match.group("stage")
        reason = flow_match.group("reason") or "未写明原因"
        return f"{stage_label(stage)}阶段：{reason}"
    gate_match = re.match(r"^gate\s+(?P<gate>[a-z0-9/-]+):\s*(?P<reason>.*)$", text)
    if gate_match:
        reason = gate_match.group("reason") or "未写明原因"
        return f"前置检查：{reason}"
    return text


def html_escape(raw: object) -> str:
    return html.escape(str(raw), quote=True)


def css_class_token(raw: object) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", str(raw).lower()).strip("-") or "unknown"


def render_html(payload: dict[str, object]) -> str:
    tasks = payload["tasks"]
    assert isinstance(tasks, list)
    filters = payload.get("filters", {})
    assert isinstance(filters, dict)
    initial_status_filter = "blocked" if filters.get("blocked_only") else "open" if filters.get("open_only") else "all"
    selected_stage = str(filters.get("stage") or "")
    selected_sort = str(filters.get("sort") or "attention")
    stage_options = ['<option value="">全部阶段</option>']
    for stage_key in FLOW_SEQUENCE:
        stage_options.append(
            '<option value="{value}"{selected}>{label}</option>'.format(
                value=html_escape(stage_key),
                selected=" selected" if selected_stage == stage_key else "",
                label=html_escape(stage_label(stage_key)),
            )
        )
    stage_options.append(
        '<option value="complete"{selected}>全部完成</option>'.format(
            selected=" selected" if selected_stage == "complete" else ""
        )
    )
    sort_options = [
        ("attention", "优先处理"),
        ("recent", "最近任务"),
        ("task", "任务名称"),
    ]
    sort_option_html = "".join(
        '<option value="{value}"{selected}>{label}</option>'.format(
            value=html_escape(value),
            selected=" selected" if selected_sort == value else "",
            label=html_escape(label),
        )
        for value, label in sort_options
    )
    cards: list[str] = []
    for card_index, item in enumerate(tasks):
        assert isinstance(item, dict)
        active = '<span class="badge badge-active">当前</span>' if item["active"] else ""
        blocked = (
            '<span class="badge badge-blocked">卡住</span>'
            if item["blocked"]
            else '<span class="badge badge-clear">正常</span>'
        )
        reasons = item.get("blocked_reasons") or []
        warnings = item.get("evidence_missing") or []
        stages = item.get("stages") or []
        assert isinstance(stages, list)
        is_open = item.get("current_step_key") != "complete"
        stages_search = " ".join(
            f"{stage.get('label', '')} {stage.get('status_label', '')}"
            for stage in stages
            if isinstance(stage, dict)
        )
        search_text = " ".join(
            [
                str(item.get("task", "")),
                str(item.get("owner", "")),
                str(item.get("boundary", "")),
                str(item.get("current_step", "")),
                str(item.get("lane", "")),
                str(item.get("mode", "")),
                stages_search,
            ]
        )
        progress_parts: list[str] = []
        stage_detail_parts: list[str] = []
        for index, stage in enumerate(stages, start=1):
            assert isinstance(stage, dict)
            status_class = css_class_token(stage.get("status", "unknown"))
            progress_parts.append(
                """
                <li class="progress-step stage-{status_class}" title="{description}">
                  <span class="step-index">{index}</span>
                  <span class="step-label">{label}</span>
                  <span class="step-status">{status_label}</span>
                </li>
                """.format(
                    status_class=status_class,
                    index=index,
                    label=html_escape(stage.get("label", "")),
                    status_label=html_escape(stage.get("status_label", "")),
                    description=html_escape(stage.get("description", "")),
                )
            )
            stage_detail_parts.append(
                """
                <div class="stage-detail-row stage-{status_class}">
                  <div class="stage-detail-name">{index}. {label}</div>
                  <div class="stage-detail-status">{status_label}</div>
                  <div class="stage-detail-desc">{description}</div>
                  <div class="stage-detail-doc">{evidence}</div>
                </div>
                """.format(
                    status_class=status_class,
                    index=index,
                    label=html_escape(stage.get("label", "")),
                    status_label=html_escape(stage.get("status_label", "")),
                    description=html_escape(stage.get("description", "")),
                    evidence=(
                        f"<code>{html_escape(stage.get('evidence', ''))}</code>"
                        if stage.get("evidence")
                        else ""
                    ),
                )
            )
        progress_html = '<ol class="progress-strip">{}</ol>'.format("".join(progress_parts))
        stage_details_html = """
        <details class="stage-details">
          <summary>展开 7 阶段说明</summary>
          <div class="stage-detail-list">
            <div class="stage-detail-header">
              <div>阶段</div>
              <div>状态</div>
              <div>说明</div>
              <div>文档路径</div>
            </div>
            {stage_details}
          </div>
        </details>
        """.format(stage_details="".join(stage_detail_parts))
        alert_parts: list[str] = []
        if reasons:
            alert_parts.append(
                '<div class="detail detail-blocked">卡住原因：{}</div>'.format(
                    html_escape("; ".join(map(str, reasons)))
                )
            )
        if warnings:
            alert_parts.append(
                '<div class="detail detail-warning">证据缺失：{}</div>'.format(
                    html_escape(", ".join(map(str, warnings)))
                )
            )
        alerts = "".join(alert_parts)
        active_class = "task-card-active" if item["active"] else ""
        cards.append(
            """
            <article class="task-card {active_class}"
              data-index="{card_index}"
              data-active="{data_active}"
              data-open="{data_open}"
              data-blocked="{data_blocked}"
              data-current-step-key="{current_step_key}"
              data-task="{task_attr}"
              data-boundary="{boundary_attr}"
              data-search="{search_text}">
              <div class="task-card-head">
                <div class="task-title-block">
                  <div class="badge-row">{active}{blocked}</div>
                  <h2>{task}</h2>
                  <div class="task-meta">协作路径：{lane} / {mode}</div>
                </div>
                <div class="current-step-box">
                  <span>当前阶段</span>
                  <strong>{current_step}</strong>
                  <small>进度 {progress}</small>
                </div>
              </div>
              <div class="task-info-grid">
                <div>
                  <span>负责人</span>
                  <strong>{owner}</strong>
                  <small>{owner_source}</small>
                </div>
                <div>
                  <span>任务文档</span>
                  <code>{boundary}</code>
                </div>
              </div>
              {alerts}
              {progress_html}
              {stage_details_html}
            </article>
            """.format(
                active_class=active_class,
                card_index=card_index,
                data_active=str(bool(item["active"])).lower(),
                data_open=str(bool(is_open)).lower(),
                data_blocked=str(bool(item["blocked"])).lower(),
                current_step_key=html_escape(item.get("current_step_key", "")),
                task_attr=html_escape(item.get("task", "")),
                boundary_attr=html_escape(item.get("boundary", "")),
                search_text=html_escape(search_text),
                active=active,
                blocked=blocked,
                task=html_escape(item["task"]),
                lane=html_escape(item["lane"]),
                mode=html_escape(item["mode"]),
                owner=html_escape(item["owner"]),
                owner_source=html_escape(item["owner_source"]),
                current_step=html_escape(item["current_step"]),
                progress=html_escape(item["progress"]),
                boundary=html_escape(item["boundary"]),
                alerts=alerts,
                progress_html=progress_html,
                stage_details_html=stage_details_html,
            )
        )
    empty_state_attr = "" if not cards else " hidden"
    filter_chips = []
    for label in filter_summary(filters).split("；"):
        if label:
            filter_chips.append(f'<span class="filter-chip">{html_escape(label)}</span>')
    dashboard_script = """
  <script>
    (() => {
      const taskList = document.getElementById("taskList");
      const cards = Array.from(taskList.querySelectorAll(".task-card"));
      const searchInput = document.getElementById("taskSearch");
      const stageFilter = document.getElementById("stageFilter");
      const sortFilter = document.getElementById("sortFilter");
      const clearButton = document.getElementById("clearFilters");
      const statusButtons = Array.from(document.querySelectorAll("[data-filter-view]"));
      const visibleCount = document.getElementById("visibleCount");
      const matchedCount = document.getElementById("matchedCount");
      const totalCount = document.getElementById("totalCount");
      const emptyState = document.getElementById("emptyState");
      let statusFilter = (statusButtons.find((button) => button.classList.contains("is-active")) || statusButtons[0]).dataset.filterView || "all";

      const boolValue = (value) => value === "true";
      const cardInfo = (card) => ({
        active: boolValue(card.dataset.active) ? 1 : 0,
        blocked: boolValue(card.dataset.blocked) ? 1 : 0,
        open: boolValue(card.dataset.open) ? 1 : 0,
        index: Number(card.dataset.index || 0),
        task: card.dataset.task || "",
        boundary: card.dataset.boundary || "",
      });

      const currentState = () => ({
        query: searchInput.value.trim().toLowerCase(),
        stage: stageFilter.value,
        sort: sortFilter.value,
        status: statusFilter,
      });

      const matchesCard = (card, state) => {
        if (state.status === "open" && card.dataset.open !== "true") {
          return false;
        }
        if (state.status === "blocked" && card.dataset.blocked !== "true") {
          return false;
        }
        if (state.stage && card.dataset.currentStepKey !== state.stage) {
          return false;
        }
        if (state.query && !(card.dataset.search || "").toLowerCase().includes(state.query)) {
          return false;
        }
        return true;
      };

      const sortedCards = (state) => cards.slice().sort((left, right) => {
        const a = cardInfo(left);
        const b = cardInfo(right);
        if (a.active !== b.active) {
          return b.active - a.active;
        }
        if (state.sort === "task") {
          const byTask = a.task.localeCompare(b.task, "zh-Hans");
          return byTask || a.boundary.localeCompare(b.boundary, "zh-Hans");
        }
        if (state.sort === "recent") {
          return b.boundary.localeCompare(a.boundary, "zh-Hans") || a.index - b.index;
        }
        if (a.blocked !== b.blocked) {
          return b.blocked - a.blocked;
        }
        if (a.open !== b.open) {
          return b.open - a.open;
        }
        return a.index - b.index;
      });

      const syncStatusButtons = () => {
        statusButtons.forEach((button) => {
          const active = button.dataset.filterView === statusFilter;
          button.classList.toggle("is-active", active);
          button.setAttribute("aria-pressed", active ? "true" : "false");
        });
      };

      const applyFilters = () => {
        const state = currentState();
        let visible = 0;
        syncStatusButtons();
        sortedCards(state).forEach((card) => {
          taskList.appendChild(card);
          const matched = matchesCard(card, state);
          card.hidden = !matched;
          if (matched) {
            visible += 1;
          }
        });
        visibleCount.textContent = String(visible);
        matchedCount.textContent = String(cards.length);
        totalCount.textContent = totalCount.dataset.total || String(cards.length);
        emptyState.hidden = visible !== 0;
      };

      searchInput.addEventListener("input", applyFilters);
      stageFilter.addEventListener("change", applyFilters);
      sortFilter.addEventListener("change", applyFilters);
      statusButtons.forEach((button) => {
        button.addEventListener("click", () => {
          statusFilter = button.dataset.filterView || "all";
          applyFilters();
        });
      });
      clearButton.addEventListener("click", () => {
        searchInput.value = "";
        stageFilter.value = "";
        sortFilter.value = "attention";
        statusFilter = "all";
        applyFilters();
        searchInput.focus();
      });

      applyFilters();
    })();
  </script>
"""
    return """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>任务状态</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fa;
      --surface: #ffffff;
      --text: #1f2933;
      --muted: #667085;
      --line: #d9dee7;
      --active-bg: #e8f2ff;
      --active-text: #175cd3;
      --clear-bg: #e8f7ef;
      --clear-text: #067647;
      --blocked-bg: #fff1f0;
      --blocked-text: #b42318;
      --warning-bg: #fff8e6;
      --warning-text: #93370d;
      --pending-bg: #f2f4f7;
      --pending-text: #475467;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      font-size: 14px;
      line-height: 1.45;
    }}
    main {{
      width: min(1280px, calc(100% - 32px));
      margin: 28px auto;
    }}
    header {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 18px;
    }}
    h1 {{
      margin: 0 0 4px;
      font-size: 24px;
      letter-spacing: 0;
    }}
    .meta {{
      margin: 0;
      color: var(--muted);
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 12px;
      color: #344054;
      word-break: break-word;
    }}
    .task-list {{
      display: grid;
      gap: 14px;
    }}
    .filter-panel {{
      display: grid;
      gap: 10px;
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px 14px;
      margin-bottom: 14px;
    }}
    .filter-controls {{
      display: grid;
      grid-template-columns: minmax(220px, 1fr) auto minmax(150px, 180px) minmax(130px, 150px) auto;
      gap: 8px;
      align-items: center;
    }}
    .filter-meta-row {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      min-height: 24px;
    }}
    .search-input,
    .filter-select {{
      width: 100%;
      height: 36px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #ffffff;
      color: var(--text);
      font: inherit;
    }}
    .search-input {{
      padding: 0 10px;
    }}
    .filter-select {{
      padding: 0 8px;
    }}
    .search-input:focus,
    .filter-select:focus,
    .filter-button:focus,
    .clear-button:focus {{
      outline: 2px solid #84caff;
      outline-offset: 1px;
    }}
    .segmented-control {{
      display: grid;
      grid-template-columns: repeat(3, minmax(56px, 1fr));
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      min-width: 188px;
      height: 36px;
      background: #ffffff;
    }}
    .filter-button,
    .clear-button {{
      border: 0;
      background: #ffffff;
      color: var(--muted);
      font: inherit;
      font-size: 12px;
      font-weight: 700;
      cursor: pointer;
      white-space: nowrap;
    }}
    .filter-button + .filter-button {{
      border-left: 1px solid var(--line);
    }}
    .filter-button.is-active {{
      background: var(--active-bg);
      color: var(--active-text);
    }}
    .clear-button {{
      height: 36px;
      padding: 0 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
    }}
    .clear-button:hover,
    .filter-button:hover {{
      color: var(--text);
    }}
    .filter-chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
    }}
    .filter-chip {{
      display: inline-flex;
      align-items: center;
      min-height: 24px;
      padding: 3px 8px;
      border-radius: 999px;
      background: #f2f4f7;
      color: #344054;
      font-size: 12px;
      font-weight: 600;
    }}
    .filter-count {{
      color: var(--muted);
      font-size: 12px;
      white-space: nowrap;
    }}
    [hidden] {{
      display: none !important;
    }}
    .empty-state {{
      background: var(--surface);
      border: 1px dashed var(--line);
      border-radius: 8px;
      padding: 24px;
      color: var(--muted);
      text-align: center;
    }}
    .task-card {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    .task-card-active {{
      border-color: #84caff;
      box-shadow: inset 3px 0 0 var(--active-text);
    }}
    .task-card-head {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(180px, 240px);
      gap: 18px;
      align-items: start;
    }}
    .task-title-block h2 {{
      margin: 8px 0 0;
      font-size: 18px;
      line-height: 1.35;
      letter-spacing: 0;
    }}
    .badge-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      min-height: 22px;
    }}
    .badge {{
      display: inline-flex;
      align-items: center;
      min-height: 22px;
      padding: 2px 8px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      white-space: nowrap;
    }}
    .badge-active {{ background: var(--active-bg); color: var(--active-text); }}
    .badge-clear {{ background: var(--clear-bg); color: var(--clear-text); }}
    .badge-blocked {{ background: var(--blocked-bg); color: var(--blocked-text); }}
    .current-step-box {{
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 12px;
      background: #fbfcfe;
    }}
    .current-step-box span,
    .task-info-grid span {{
      display: block;
      color: var(--muted);
      font-size: 12px;
      margin-bottom: 4px;
    }}
    .current-step-box strong {{
      display: block;
      font-size: 18px;
      line-height: 1.35;
    }}
    .current-step-box small,
    .task-info-grid small {{
      display: block;
      margin-top: 5px;
      color: var(--muted);
      font-size: 12px;
    }}
    .task-info-grid {{
      display: grid;
      grid-template-columns: minmax(160px, 220px) minmax(0, 1fr);
      gap: 12px;
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px solid var(--line);
    }}
    .detail {{
      margin-top: 10px;
      font-size: 12px;
    }}
    .task-meta,
    .owner-source {{
      margin-top: 6px;
      color: var(--muted);
      font-size: 12px;
    }}
    .detail-blocked {{ color: var(--blocked-text); }}
    .detail-warning {{ color: var(--warning-text); }}
    .progress-strip {{
      display: grid;
      grid-template-columns: repeat(7, minmax(88px, 1fr));
      gap: 6px;
      margin: 16px 0 0;
      padding: 0;
      list-style: none;
    }}
    .progress-step {{
      min-height: 48px;
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 7px 8px;
      background: #ffffff;
      display: grid;
      grid-template-columns: auto minmax(0, 1fr);
      gap: 2px 6px;
      align-items: center;
    }}
    .step-index {{
      width: 20px;
      height: 20px;
      border-radius: 999px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      background: var(--pending-bg);
      color: var(--pending-text);
      font-size: 11px;
      font-weight: 700;
    }}
    .step-label {{
      min-width: 0;
      color: var(--text);
      font-size: 12px;
      font-weight: 700;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }}
    .step-status {{
      grid-column: 2;
      color: var(--pending-text);
      font-size: 11px;
    }}
    .stage-done .step-index,
    .stage-not-required .step-index {{
      background: var(--clear-bg);
      color: var(--clear-text);
    }}
    .stage-blocked .step-index {{
      background: var(--blocked-bg);
      color: var(--blocked-text);
    }}
    .stage-missing .step-index,
    .stage-pending .step-index {{
      background: var(--warning-bg);
      color: var(--warning-text);
    }}
    .stage-done .step-status,
    .stage-not-required .step-status {{ color: var(--clear-text); }}
    .stage-blocked .step-status {{ color: var(--blocked-text); }}
    .stage-missing .step-status,
    .stage-pending .step-status {{ color: var(--warning-text); }}
    .stage-details {{
      margin-top: 10px;
    }}
    .stage-details summary {{
      cursor: pointer;
      color: var(--muted);
      font-size: 12px;
      user-select: none;
    }}
    .stage-detail-list {{
      margin-top: 10px;
      border-top: 1px solid var(--line);
    }}
    .stage-detail-header {{
      display: grid;
      grid-template-columns: 150px 72px minmax(220px, 1fr) minmax(280px, 1.2fr);
      gap: 10px;
      padding: 8px 0;
      border-bottom: 1px solid var(--line);
      color: var(--muted);
      font-size: 12px;
      font-weight: 700;
    }}
    .stage-detail-row {{
      display: grid;
      grid-template-columns: 150px 72px minmax(220px, 1fr) minmax(280px, 1.2fr);
      gap: 10px;
      padding: 8px 0;
      border-bottom: 1px solid var(--line);
      font-size: 12px;
    }}
    .stage-detail-name {{
      font-weight: 700;
    }}
    .stage-detail-status {{
      color: var(--muted);
    }}
    .stage-detail-desc {{
      color: var(--muted);
    }}
    .stage-detail-doc code {{
      color: #344054;
      white-space: normal;
      overflow-wrap: anywhere;
    }}
    .note {{
      margin-top: 12px;
      color: var(--muted);
      font-size: 12px;
    }}
    @media (max-width: 900px) {{
      main {{
        width: min(100% - 20px, 1280px);
      }}
      header,
      .task-card-head,
      .task-info-grid,
      .filter-panel,
      .filter-controls {{
        grid-template-columns: 1fr;
      }}
      .filter-meta-row {{
        align-items: flex-start;
        flex-direction: column;
      }}
      .segmented-control {{
        min-width: 0;
      }}
      header {{
        align-items: flex-start;
      }}
      .progress-strip {{
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }}
      .stage-detail-header,
      .stage-detail-row {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <div>
        <h1>任务状态</h1>
        <p class="meta">本机当前任务：<code>{active_boundary}</code></p>
        <p class="meta">本页只读取本机当前分支的 `.gstack/task-boundaries`；负责人来自任务文档，不是 git 提交人。</p>
      </div>
      <p class="meta">生成时间：<code>{generated_at}</code></p>
    </header>
    <section class="filter-panel">
      <div class="filter-controls">
        <input id="taskSearch" class="search-input" type="search" value="{initial_query}" placeholder="搜索任务、负责人、阶段或文档路径" aria-label="搜索任务">
        <div class="segmented-control" role="group" aria-label="状态筛选">
          <button type="button" class="filter-button {all_status_class}" data-filter-view="all" aria-pressed="{all_pressed}">全部</button>
          <button type="button" class="filter-button {open_status_class}" data-filter-view="open" aria-pressed="{open_pressed}">未完成</button>
          <button type="button" class="filter-button {blocked_status_class}" data-filter-view="blocked" aria-pressed="{blocked_pressed}">卡住</button>
        </div>
        <select id="stageFilter" class="filter-select" aria-label="阶段筛选">
          {stage_options}
        </select>
        <select id="sortFilter" class="filter-select" aria-label="排序">
          {sort_options}
        </select>
        <button id="clearFilters" class="clear-button" type="button">清空</button>
      </div>
      <div class="filter-meta-row">
        <div class="filter-chips" aria-label="生成条件">{filter_chips}</div>
        <div class="filter-count">显示 <span id="visibleCount">{visible_tasks}</span> / 本页 <span id="matchedCount">{visible_tasks}</span> / 总计 <span id="totalCount" data-total="{total_tasks}">{total_tasks}</span></div>
      </div>
    </section>
    <section id="taskList" class="task-list">
{cards}
      <div id="emptyState" class="empty-state"{empty_state_attr}>当前筛选没有匹配任务。</div>
    </section>
    <p class="note">生成视图，不提交共享 `.gstack/dashboard.*` 或全局 status 聚合文件；同事能看到哪些任务，取决于他们本机 checkout 的分支和已同步的 repo-native evidence。</p>
  </main>
{dashboard_script}
</body>
</html>
""".format(
        active_boundary=html_escape(payload["active_boundary"] or "none"),
        generated_at=html_escape(payload["generated_at"]),
        initial_query=html_escape(filters.get("query", "")),
        all_status_class="is-active" if initial_status_filter == "all" else "",
        open_status_class="is-active" if initial_status_filter == "open" else "",
        blocked_status_class="is-active" if initial_status_filter == "blocked" else "",
        all_pressed="true" if initial_status_filter == "all" else "false",
        open_pressed="true" if initial_status_filter == "open" else "false",
        blocked_pressed="true" if initial_status_filter == "blocked" else "false",
        stage_options="\n          ".join(stage_options),
        sort_options=sort_option_html,
        filter_chips="".join(filter_chips),
        visible_tasks=html_escape(payload.get("visible_tasks", len(tasks))),
        matched_tasks=html_escape(payload.get("matched_tasks", len(tasks))),
        total_tasks=html_escape(payload.get("total_tasks", len(tasks))),
        cards="\n".join(cards),
        empty_state_attr=empty_state_attr,
        dashboard_script=dashboard_script,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("show", help="Render a generated dashboard to stdout.")
    show.add_argument("--format", choices=("markdown", "json", "html"), default="markdown")
    show.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum generated tasks. Defaults to all tasks for HTML and 12 for markdown/json.",
    )
    show.add_argument("--active-only", action="store_true")
    show.add_argument("--open-only", action="store_true", help="Only show tasks that are not complete.")
    show.add_argument("--blocked-only", action="store_true", help="Only show tasks with blocked flow or gates.")
    show.add_argument(
        "--stage",
        choices=(*FLOW_SEQUENCE, "complete"),
        default="",
        help="Only show tasks whose current stage matches this value.",
    )
    show.add_argument("--query", default="", help="Search task title, owner, current step, lane, mode, or boundary path.")
    show.add_argument(
        "--sort",
        choices=("attention", "recent", "task"),
        default="attention",
        help="attention: current/blocked/open first; recent: newest boundary first; task: title order.",
    )
    explain = subparsers.add_parser(
        "explain",
        help="Explain current task status in plain language for nontechnical users.",
    )
    explain.add_argument(
        "--all",
        action="store_true",
        help="Explain all matching tasks instead of only the active task.",
    )
    explain.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum generated tasks. Defaults to 1 for current-task mode and all tasks for --all.",
    )
    explain.add_argument("--open-only", action="store_true", help="Only explain tasks that are not complete.")
    explain.add_argument("--blocked-only", action="store_true", help="Only explain tasks with blocked flow or gates.")
    explain.add_argument(
        "--stage",
        choices=(*FLOW_SEQUENCE, "complete"),
        default="",
        help="Only explain tasks whose current stage matches this value.",
    )
    explain.add_argument("--query", default="", help="Search task title, owner, current step, lane, mode, or boundary path.")
    explain.add_argument(
        "--sort",
        choices=("attention", "recent", "task"),
        default="attention",
        help="attention: current/blocked/open first; recent: newest boundary first; task: title order.",
    )
    verify = subparsers.add_parser(
        "verify",
        help="Explain how to verify task completion in plain language.",
    )
    verify.add_argument(
        "--all",
        action="store_true",
        help="Explain verification for all matching tasks instead of only the active task.",
    )
    verify.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum generated tasks. Defaults to 1 for current-task mode and 12 for --all or --query.",
    )
    verify.add_argument("--open-only", action="store_true", help="Only explain tasks that are not complete.")
    verify.add_argument("--blocked-only", action="store_true", help="Only explain tasks with blocked flow or gates.")
    verify.add_argument(
        "--stage",
        choices=(*FLOW_SEQUENCE, "complete"),
        default="",
        help="Only explain tasks whose current stage matches this value.",
    )
    verify.add_argument("--query", default="", help="Search task title, owner, current step, lane, mode, or boundary path.")
    verify.add_argument(
        "--sort",
        choices=("attention", "recent", "task"),
        default="attention",
        help="attention: current/blocked/open first; recent: newest boundary first; task: title order.",
    )
    write_html = subparsers.add_parser(
        "write-html",
        help="Write the latest generated HTML dashboard to a stable gitignored file.",
    )
    write_html.add_argument(
        "--output",
        default=DEFAULT_HTML_OUTPUT.as_posix(),
        help="Output HTML path. Defaults to output/gstack-dashboard/latest.html.",
    )
    write_html.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum generated tasks. Defaults to all tasks.",
    )
    write_html.add_argument("--active-only", action="store_true")
    write_html.add_argument("--open-only", action="store_true", help="Only show tasks that are not complete.")
    write_html.add_argument("--blocked-only", action="store_true", help="Only show tasks with blocked flow or gates.")
    write_html.add_argument(
        "--stage",
        choices=(*FLOW_SEQUENCE, "complete"),
        default="",
        help="Only show tasks whose current stage matches this value.",
    )
    write_html.add_argument("--query", default="", help="Search task title, owner, current step, lane, mode, or boundary path.")
    write_html.add_argument(
        "--sort",
        choices=("attention", "recent", "task"),
        default="attention",
        help="attention: current/blocked/open first; recent: newest boundary first; task: title order.",
    )
    return parser


def render_payload_from_args(args: argparse.Namespace, *, default_limit: int | None) -> dict[str, object]:
    limit = default_limit if args.limit is None else max(1, args.limit)
    return dashboard_payload(
        limit=limit,
        active_only=args.active_only,
        open_only=args.open_only,
        blocked_only=args.blocked_only,
        stage=args.stage,
        query=args.query,
        sort=args.sort,
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "show":
        payload = render_payload_from_args(args, default_limit=None if args.format == "html" else 12)
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        elif args.format == "html":
            print(render_html(payload))
        else:
            print(render_markdown(payload))
        return 0
    if args.command == "explain":
        default_limit = 12 if args.all else 1
        payload = dashboard_payload(
            limit=default_limit if args.limit is None else max(1, args.limit),
            active_only=not args.all,
            open_only=args.open_only,
            blocked_only=args.blocked_only,
            stage=args.stage,
            query=args.query,
            sort=args.sort,
        )
        print(render_explanation(payload))
        return 0
    if args.command == "verify":
        active_only = not args.all and not args.query
        default_limit = 1 if active_only else 12
        payload = dashboard_payload(
            limit=default_limit if args.limit is None else max(1, args.limit),
            active_only=active_only,
            open_only=args.open_only,
            blocked_only=args.blocked_only,
            stage=args.stage,
            query=args.query,
            sort=args.sort,
        )
        print(render_verification(payload))
        return 0
    if args.command == "write-html":
        output_path = Path(args.output)
        if not output_path.is_absolute():
            output_path = REPO_ROOT / output_path
        payload = render_payload_from_args(args, default_limit=None)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(render_html(payload), encoding="utf-8")
        try:
            display_path = output_path.resolve().relative_to(REPO_ROOT).as_posix()
        except ValueError:
            display_path = output_path.resolve().as_posix()
        print(display_path)
        print("Generated view only. Re-run this command and refresh the browser to see new repo evidence.")
        return 0
    parser.error("unhandled command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
