#!/usr/bin/env python3
"""Explain how Codex will continue after a terse nontechnical user prompt.

This helper is deterministic and read-only. It reads the current active task
boundary and generated dashboard summary, then turns "continue / do the first
step" style prompts into user-facing language. It does not create evidence,
connect to services, touch databases, clear sensitive configuration, or run git
actions.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from gstack_dashboard import active_boundary, read_text, summarize_boundary


STAGE_ACTIONS = {
    "requirement-brief": "先补齐当前任务的目标、范围和最小验收标准。",
    "plan-ceo-review": "先确认这件事值得做、范围不跑偏，再进入工程判断。",
    "requirement-freeze": "先冻结本轮需求和不做范围，避免继续时把范围扩大。",
    "plan-eng-review": "先确认实现路径、风险和验证计划，再进入实际修改。",
    "domain-spec-readiness": "先确认需要同步的真源文档，或写明本轮不需要改业务规格。",
    "implement": "继续完成当前任务的实现和文档同步。",
    "qa": "继续运行验证，把结果写入验收记录。",
    "complete": "当前任务已经收口；继续推进时会开启下一段最小优化，而不是重复追问这段任务的成功样子。",
}


@dataclass(frozen=True)
class ContinuePlan:
    raw_request: str
    status: str
    status_reason: str
    task: str
    task_done: bool
    current_stage: str
    progress: str
    codex_next_actions: list[str]
    needs_user_confirmation: list[str]
    non_actions: list[str]
    next_user_message: str


def compact(raw: str) -> str:
    return " ".join(raw.strip().split())


def safe_task_name(task: str) -> str:
    return task.strip() or "当前任务"


def confirmation_for(status: str, blocked: bool) -> list[str]:
    if status == "no-active-task":
        return ["需要你告诉我这次要继续哪件事，或让我先恢复当前任务记录。"]
    if blocked:
        return ["当前任务记录显示有卡住项；Codex 会先修本地能证明的问题，涉及业务口径、真实数据、生产、数据库或代码提交流程时再问你。"]
    return ["暂时不需要；Codex 可以先在当前任务范围内继续推进本地可证明步骤，不会每一步都等你再说“继续”。"]


def non_actions() -> list[str]:
    return [
        "不会直接操作真实数据、生产环境、数据库、外部服务或破坏性命令。",
        "不会执行代码提交流程。",
        "不会清理、删除或改写项目已允许随仓库携带的敏感配置。",
    ]


def actions_for_stage(stage: str, task_done: bool, blocked: bool) -> list[str]:
    actions: list[str] = []
    if blocked:
        actions.append("先看当前任务为什么卡住，并优先修复本地可以证明的问题。")
    actions.append(STAGE_ACTIONS.get(stage, "继续完成当前任务的下一步。"))
    actions.append("工程实现顺序、测试组合、文档同步、门禁恢复和 subagent 分工由 Codex 在任务范围内自主决定。")
    if not task_done:
        actions.append("继续时会保持原有任务范围，不把它当成一个全新需求重新追问。")
        actions.append("完成后会重新运行验证，并把结果写入验收记录。")
    else:
        actions.append("如果你是说继续优化整个骨架，Codex 会选择下一条未覆盖的非技术用户体验继续做。")
        actions.append("下一段仍会先补最小任务范围和验收口径，再实现和验证。")
    return actions


def build_continue_plan(args: argparse.Namespace) -> ContinuePlan:
    raw = compact(args.raw)
    active = active_boundary()
    if not active:
        return ContinuePlan(
            raw_request=raw,
            status="no-active-task",
            status_reason="当前没有本地 active task，无法判断应该继续哪件事。",
            task="",
            task_done=False,
            current_stage="未找到当前任务",
            progress="0/7",
            codex_next_actions=[
                "先恢复或创建当前任务记录。",
                "再判断是继续上一件事、开启下一段优化，还是需要你补一句具体目标。",
            ],
            needs_user_confirmation=confirmation_for("no-active-task", False),
            non_actions=non_actions(),
            next_user_message="我需要先恢复当前任务记录，再继续推进。",
        )

    text = read_text(active)
    summary = summarize_boundary(active, active)
    task_done = summary.current_step_key == "complete"
    status = "current-task-complete" if task_done else "continue-current-task"
    reason = "当前任务记录已经显示全部完成。" if task_done else "当前任务记录还有未完成阶段，可以继续推进。"
    return ContinuePlan(
        raw_request=raw,
        status=status,
        status_reason=reason,
        task=safe_task_name(summary.task),
        task_done=task_done,
        current_stage=summary.current_step_label,
        progress=summary.progress,
        codex_next_actions=actions_for_stage(summary.current_step_key, task_done, summary.blocked),
        needs_user_confirmation=confirmation_for(status, summary.blocked),
        non_actions=non_actions(),
        next_user_message="我会按继续推进处理，不把这句话当成一个全新的需求澄清。",
    )


def render_user(plan: ContinuePlan) -> str:
    if plan.status == "no-active-task":
        lines = [
            "我会按继续推进处理，但现在还缺当前任务记录。",
            "",
            "Codex 的下一步：",
            *[f"- {item}" for item in plan.codex_next_actions],
            "",
            "需要你确认：",
            *[f"- {item}" for item in plan.needs_user_confirmation],
            "",
            "这次不会做什么：",
            *[f"- {item}" for item in plan.non_actions],
        ]
        return "\n".join(lines)

    lines = [
        "我会按继续推进处理。",
        "",
        f"当前任务：{plan.task}",
        f"当前状态：{plan.status_reason}",
        f"当前阶段：{plan.current_stage}",
        f"进度：{plan.progress}",
        "",
        "Codex 的下一步：",
        *[f"- {item}" for item in plan.codex_next_actions],
        "",
        "需要你确认：",
        *[f"- {item}" for item in plan.needs_user_confirmation],
        "",
        "这次不会做什么：",
        *[f"- {item}" for item in plan.non_actions],
    ]
    return "\n".join(lines)


def render_markdown(plan: ContinuePlan) -> str:
    lines = [
        "# 非技术继续推进说明",
        "",
        f"- 状态：{plan.status}",
        f"- 状态原因：{plan.status_reason}",
        f"- 当前任务：{plan.task or '未找到'}",
        f"- 当前任务是否完成：{'是' if plan.task_done else '否'}",
        f"- 当前阶段：{plan.current_stage}",
        f"- 进度：{plan.progress}",
        "- Codex 的下一步：",
        *[f"  - {item}" for item in plan.codex_next_actions],
        "- 需要用户确认：",
        *[f"  - {item}" for item in plan.needs_user_confirmation],
        "- 不执行动作：",
        *[f"  - {item}" for item in plan.non_actions],
    ]
    return "\n".join(lines)


def render_json(plan: ContinuePlan) -> str:
    return json.dumps(asdict(plan), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's continue-style request.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    plan = build_continue_plan(args)
    if args.format == "json":
        print(render_json(plan))
    elif args.format == "user":
        print(render_user(plan))
    else:
        print(render_markdown(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
