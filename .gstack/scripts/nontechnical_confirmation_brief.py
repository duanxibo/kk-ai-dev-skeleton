#!/usr/bin/env python3
"""Explain what the user needs to confirm for the current task.

This helper is read-only and intended for Codex internal use. It translates the
current active task's state into a concise confirmation brief for nontechnical
users.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from gstack_dashboard import (
    active_boundary,
    parse_required_flow,
    parse_required_gates,
    read_text,
    stage_label,
    status_label,
)


READY_STATUSES = {"done", "not-required"}
HIGH_RISK_WORDS = ("真实数据", "生产", "数据库", "线上", "外部服务", "发布", "代码提交流程", "破坏性")
BUSINESS_STAGES = {"requirement-brief", "requirement-freeze", "plan-ceo-review"}
TECHNICAL_STAGES = {"plan-eng-review", "domain-spec-readiness", "implement", "qa"}
GATE_LABELS = {
    "data-access": "数据范围或权限",
    "data-query": "数据查询口径",
    "prototype-logic-extraction": "页面或原型逻辑归属",
    "data-knowledge-sync": "数据和接口知识回写",
    "subagent-plan": "协作分工",
    "doc-backfill": "文档补齐",
}


@dataclass(frozen=True)
class ConfirmationBrief:
    status: str
    current_task: str
    waiting_for_user: bool
    confirmation_items: list[str]
    suggested_replies: list[str]
    codex_next_actions: list[str]
    non_actions: list[str]


def clean(raw: str) -> str:
    return raw.strip().strip("`").strip('"').strip("'").strip()


def current_task_name(text: str, path: Path) -> str:
    for line in text.splitlines()[:20]:
        match = re.match(r"^\s*-\s*(?:Task|任务)\s*[:：]\s*(?P<value>.*?)\s*$", line, re.I)
        if match and clean(match.group("value")):
            return clean(match.group("value"))
    for line in text.splitlines()[:3]:
        if line.startswith("# "):
            return clean(line[2:])
    return path.stem


def gate_label(gate_id: str) -> str:
    return GATE_LABELS.get(gate_id, "内部检查")


def contains_high_risk(text: str) -> bool:
    return any(word in text for word in HIGH_RISK_WORDS)


def first_unready_stage(flow: dict[str, dict[str, str]]) -> tuple[str, str] | None:
    for stage in (
        "requirement-brief",
        "plan-ceo-review",
        "requirement-freeze",
        "plan-eng-review",
        "domain-spec-readiness",
        "implement",
        "qa",
    ):
        status = flow.get(stage, {}).get("status", "missing")
        if status not in READY_STATUSES:
            return stage, status
    return None


def confirmation_from_stage(stage: str, status: str, record: dict[str, str]) -> str | None:
    note = record.get("note", "") or record.get("evidence", "")
    if status == "blocked":
        if contains_high_risk(note):
            return "这里可能涉及真实数据、生产环境、数据库、发布、外部服务或代码提交流程，需要你确认业务范围和授权。"
        return f"{stage_label(stage)}卡住了，需要你确认阻塞原因是否符合当前业务目标。"
    if stage in BUSINESS_STAGES:
        return "需要你确认业务目标、成功后第一眼看到什么，以及这次明确不做什么。"
    if stage in TECHNICAL_STAGES and contains_high_risk(note):
        return "需要你确认高风险范围：真实数据、生产环境、数据库、外部服务、发布或代码提交流程是否允许继续。"
    return None


def confirmation_from_gate(gate: dict[str, str]) -> str | None:
    status = gate.get("status", "missing")
    if status in READY_STATUSES:
        return None
    combined = " ".join(
        gate.get(key, "")
        for key in ("trigger_reason", "blocking_reason", "done_criteria")
    )
    label = gate_label(gate.get("gate_id", ""))
    if contains_high_risk(combined):
        return f"{label}还没确认；如果要继续，需要你确认业务范围、数据权限或高风险授权。"
    if status == "blocked":
        return f"{label}卡住了，需要你确认当前任务是否继续按这个范围推进。"
    return None


def unique(items: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for item in items:
        if item in seen:
            continue
        result.append(item)
        seen.add(item)
    return result


def default_non_actions() -> list[str]:
    return [
        "不会要求你自己运行命令或阅读工程文档。",
        "不会直接操作真实数据、生产环境、数据库、破坏性命令或代码提交流程。",
        "不会把内部任务范围、内部检查、规格说明或内部数据直接丢给你判断。",
    ]


def build_brief() -> ConfirmationBrief:
    boundary = active_boundary()
    if boundary is None:
        return ConfirmationBrief(
            status="no-active-task",
            current_task="当前没有读到明确任务。",
            waiting_for_user=True,
            confirmation_items=["需要先确认你要继续哪个任务。"],
            suggested_replies=["可以直接回复：继续哪个任务，或把目标再说一遍。"],
            codex_next_actions=["Codex 会先恢复当前任务记录，再判断是否需要你确认业务问题。"],
            non_actions=default_non_actions(),
        )

    text = read_text(boundary)
    task = current_task_name(text, boundary)
    flow = parse_required_flow(text)
    gates = parse_required_gates(text)
    confirmations: list[str] = []

    unready = first_unready_stage(flow)
    if unready is not None:
        stage, status = unready
        confirmation = confirmation_from_stage(stage, status, flow.get(stage, {}))
        if confirmation:
            confirmations.append(confirmation)

    for gate in gates:
        confirmation = confirmation_from_gate(gate)
        if confirmation:
            confirmations.append(confirmation)

    confirmations = unique(confirmations)
    waiting = bool(confirmations)
    if waiting:
        status = "needs-user-confirmation"
        replies = [
            "如果这个判断正确，可以直接回复“确认，按这个范围继续”。",
            "如果范围不对，请直接说“这次不要碰...”或“先只做...”。",
            "如果涉及真实数据、生产、数据库、外部服务或代码提交流程，请明确说允许范围和禁止范围。",
        ]
        actions = ["Codex 会等你确认后，再继续推进对应范围。"]
    else:
        status = "no-user-confirmation-needed"
        confirmations = ["暂时不需要你确认。"]
        replies = ["你可以直接说“继续做”，Codex 会按当前任务范围推进。"]
        actions = ["Codex 可以继续处理当前任务中可由本地证据证明的下一步。"]

    if unready is not None and unready[0] in TECHNICAL_STAGES and not waiting:
        actions.append(f"当前下一步是{stage_label(unready[0])}（{status_label(unready[1])}）。")

    return ConfirmationBrief(
        status=status,
        current_task=task,
        waiting_for_user=waiting,
        confirmation_items=confirmations,
        suggested_replies=replies,
        codex_next_actions=actions,
        non_actions=default_non_actions(),
    )


def render_user(result: ConfirmationBrief) -> str:
    lines = [
        "# 确认事项说明",
        "",
        "当前任务：",
        f"- {result.current_task}",
        "",
        "现在是否等你确认：",
        "- 现在需要你确认。" if result.waiting_for_user else "- 暂时不需要你确认。",
        "",
        "需要你确认：",
    ]
    lines.extend(f"- {item}" for item in result.confirmation_items)
    lines.extend(["", "你可以这样回复："])
    lines.extend(f"- {item}" for item in result.suggested_replies)
    lines.extend(["", "Codex 的下一步："])
    lines.extend(f"- {item}" for item in result.codex_next_actions)
    lines.extend(["", "这次不会做什么："])
    lines.extend(f"- {item}" for item in result.non_actions)
    return "\n".join(lines)


def render_json(result: ConfirmationBrief) -> str:
    return json.dumps(asdict(result), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("user", "json"), default="user")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = build_brief()
    if args.format == "json":
        print(render_json(result))
    else:
        print(render_user(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
