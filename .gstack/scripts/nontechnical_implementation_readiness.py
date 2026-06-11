#!/usr/bin/env python3
"""Explain whether the current task is ready for implementation.

This helper is read-only and intended for Codex internal use. It translates the
current active task's workflow and internal checks into plain language for
nontechnical users.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from gstack_dashboard import (
    FLOW_SEQUENCE,
    active_boundary,
    parse_required_flow,
    parse_required_gates,
    read_text,
    stage_label,
    status_label,
)


PRE_IMPLEMENT_STAGES = (
    "requirement-brief",
    "plan-ceo-review",
    "requirement-freeze",
    "plan-eng-review",
    "domain-spec-readiness",
)
READY_STATUSES = {"done", "not-required"}
IMPLEMENT_BLOCKING_GATE_BEFORE = {
    "requirement-brief",
    "plan-ceo-review",
    "requirement-freeze",
    "prototype-freeze",
    "plan-eng-review",
    "domain-spec-readiness",
    "implement",
}
GATE_LABELS = {
    "data-access": "数据来源和权限检查",
    "data-query": "数据查询检查",
    "prototype-logic-extraction": "页面或原型逻辑归属检查",
    "data-knowledge-sync": "数据和接口知识回写检查",
    "subagent-plan": "协作分工检查",
    "doc-backfill": "文档补齐检查",
}


@dataclass(frozen=True)
class ImplementationReadiness:
    status: str
    current_task: str
    can_start_implementation: bool
    overall_judgment: str
    completed_preparation: list[str]
    missing_preparation: list[str]
    codex_next_actions: list[str]
    needs_user_confirmation: list[str]
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


def is_gate_relevant_before_implementation(gate: dict[str, str]) -> bool:
    required_before = gate.get("required_before", "")
    if not required_before:
        return True
    return required_before in IMPLEMENT_BLOCKING_GATE_BEFORE


def stage_summary(stage: str, status: str) -> str:
    return f"{stage_label(stage)}：{status_label(status)}"


def gate_summary(gate: dict[str, str]) -> str:
    return f"{gate_label(gate.get('gate_id', ''))}：{status_label(gate.get('status', 'missing'))}"


def user_confirmation_for(gates: list[dict[str, str]], missing_stages: list[str]) -> list[str]:
    confirmations: list[str] = []
    risky_gate_words = ("真实数据", "生产", "数据库", "线上", "权限", "授权", "外部服务")
    for gate in gates:
        status = gate.get("status", "missing")
        if status in READY_STATUSES:
            continue
        combined = " ".join(
            gate.get(key, "")
            for key in ("trigger_reason", "blocking_reason", "done_criteria")
        )
        if any(word in combined for word in risky_gate_words):
            confirmations.append("如果要继续涉及真实数据、生产环境、数据库、线上权限或外部服务，需要你确认业务范围和授权。")
            break
    if any("需求" in item for item in missing_stages):
        confirmations.append("如果需求目标、成功样子或本次不做范围还没说清，需要你补充业务判断。")
    if not confirmations:
        confirmations.append("暂时不需要你做技术操作；Codex 会先补齐可由本地证据证明的准备项。")
    return confirmations


def build_readiness() -> ImplementationReadiness:
    boundary = active_boundary()
    if boundary is None:
        return ImplementationReadiness(
            status="no-active-task",
            current_task="当前没有读到明确任务。",
            can_start_implementation=False,
            overall_judgment="现在还不能判断是否可以开始实现，因为 Codex 没有读到当前任务记录。",
            completed_preparation=[],
            missing_preparation=["需要先恢复或选择当前任务。"],
            codex_next_actions=["先恢复当前任务记录，再判断能否开始实现。"],
            needs_user_confirmation=["如果你知道要继续哪个任务，请直接说任务名称或目标。"],
            non_actions=default_non_actions(),
        )

    text = read_text(boundary)
    task = current_task_name(text, boundary)
    flow = parse_required_flow(text)
    gates = [gate for gate in parse_required_gates(text) if is_gate_relevant_before_implementation(gate)]

    completed: list[str] = []
    missing: list[str] = []
    missing_stage_labels: list[str] = []

    for stage in PRE_IMPLEMENT_STAGES:
        status = flow.get(stage, {}).get("status", "missing")
        summary = stage_summary(stage, status)
        if status in READY_STATUSES:
            completed.append(summary)
        else:
            missing.append(summary)
            missing_stage_labels.append(summary)

    for gate in gates:
        status = gate.get("status", "missing")
        summary = gate_summary(gate)
        if status in READY_STATUSES:
            completed.append(summary)
        else:
            missing.append(summary)

    implement_status = flow.get("implement", {}).get("status", "missing")
    qa_status = flow.get("qa", {}).get("status", "missing")
    can_start = not missing

    if implement_status == "done" and qa_status == "done":
        status = "already-complete"
        judgment = "当前任务已经完成实现和验收，不需要再判断是否开始实现。"
        next_actions = ["可以进入结果验收、交付说明，或开启下一段改进。"]
    elif implement_status == "done":
        status = "implementation-done-needs-acceptance"
        judgment = "当前任务已经完成实现，但还需要完成验收记录后才能收口。"
        next_actions = ["Codex 下一步应补齐验收记录，并说明你可以怎么看结果。"]
    elif can_start:
        status = "ready-to-implement"
        judgment = "当前任务的实现前准备已经就绪，可以进入实现。"
        next_actions = ["Codex 可以按当前任务范围开始实现，并在完成后补验收记录。"]
    else:
        status = "not-ready-to-implement"
        judgment = "当前任务还不能直接开始实现，需要先补齐准备项。"
        next_actions = [
            "Codex 会先补齐排在最前面的准备项。",
            "如果缺口涉及业务口径、真实数据、生产环境、数据库或外部服务，Codex 会单独问你确认。",
        ]

    return ImplementationReadiness(
        status=status,
        current_task=task,
        can_start_implementation=can_start or implement_status == "done",
        overall_judgment=judgment,
        completed_preparation=completed or ["还没有读到已完成的实现前准备。"],
        missing_preparation=missing or ["没有发现阻止开始实现的准备缺口。"],
        codex_next_actions=next_actions,
        needs_user_confirmation=user_confirmation_for(gates, missing_stage_labels) if missing else ["暂时不需要你确认。"],
        non_actions=default_non_actions(),
    )


def default_non_actions() -> list[str]:
    return [
        "不会要求你自己运行命令或阅读工程文档。",
        "不会直接操作真实数据、生产环境、数据库、破坏性命令或代码提交流程。",
        "不会把内部任务范围、内部检查、规格说明或内部数据直接丢给你判断。",
    ]


def render_user(result: ImplementationReadiness) -> str:
    lines = [
        "# 实现就绪检查",
        "",
        "当前任务：",
        f"- {result.current_task}",
        "",
        "整体判断：",
        f"- {result.overall_judgment}",
        "",
        "已经准备好：",
    ]
    lines.extend(f"- {item}" for item in result.completed_preparation)
    lines.extend(["", "还差什么："])
    lines.extend(f"- {item}" for item in result.missing_preparation)
    lines.extend(["", "Codex 的下一步："])
    lines.extend(f"- {item}" for item in result.codex_next_actions)
    lines.extend(["", "需要你确认："])
    lines.extend(f"- {item}" for item in result.needs_user_confirmation)
    lines.extend(["", "这次不会做什么："])
    lines.extend(f"- {item}" for item in result.non_actions)
    return "\n".join(lines)


def render_json(result: ImplementationReadiness) -> str:
    return json.dumps(asdict(result), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("user", "json"), default="user")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = build_readiness()
    if args.format == "json":
        print(render_json(result))
    else:
        print(render_user(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
