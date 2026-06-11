#!/usr/bin/env python3
"""Explain how Codex handles a nontechnical undo / revert request safely.

This helper is deterministic and read-only. It turns "undo / revert / go back"
style prompts into user-facing language. It does not delete edits, reset files,
revert commits, create evidence, connect to data sources, operate production
systems, or run git actions.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from gstack_dashboard import active_boundary, summarize_boundary


@dataclass(frozen=True)
class UndoRequestBrief:
    raw_request: str
    status: str
    current_task: str
    request_understanding: str
    required_scope: list[str]
    safe_next_actions: list[str]
    suggested_replies: list[str]
    needs_user_confirmation: list[str]
    non_actions: list[str]


def compact(raw: str) -> str:
    return " ".join(raw.strip().split())


def default_required_scope() -> list[str]:
    return [
        "要撤销的是哪一部分：刚才这一小步、上一轮全部改动、某个页面变化，还是某个具体文件 / 功能。",
        "撤销后希望回到什么状态：完全回到修改前、只去掉某个入口、还是只先看撤销方案。",
        "是否允许 Codex 修改文件；如果只是想先看影响范围，可以明确说“不改文件，只给撤销计划”。",
    ]


def default_safe_next_actions() -> list[str]:
    return [
        "先查看当前本地改动，列出哪些内容可能会被撤销。",
        "把每一项可能撤销的影响用人话说明清楚。",
        "给出一个撤销计划，等你确认范围后再决定是否实际执行。",
    ]


def default_suggested_replies() -> list[str]:
    return [
        "只先给撤销计划，不改文件。",
        "只撤销刚才这个入口，其他改动保留。",
        "撤销上一轮全部改动，但先列出会影响哪些内容。",
        "不要撤销了，只是暂停，之后我再说继续。",
    ]


def default_non_actions() -> list[str]:
    return [
        "不会自动删除文件、清理改动、reset、回滚或恢复到旧版本。",
        "不会把“撤销”当成“暂停”后继续保留推进，也不会假装已经撤销完成。",
        "不会连接真实数据、生产环境、数据库、外部服务或执行破坏性命令。",
        "不会执行代码提交流程。",
        "不会清理敏感配置或改写以后默认协作模式。",
    ]


def build_undo_request_brief(args: argparse.Namespace) -> UndoRequestBrief:
    raw = compact(args.raw)
    active = active_boundary()
    if active is None:
        return UndoRequestBrief(
            raw_request=raw,
            status="no-active-task",
            current_task="当前没有读到明确任务。",
            request_understanding="我会把这句话理解为撤销 / 回滚请求；因为没有明确当前任务，不能直接判断要撤销哪一部分。",
            required_scope=default_required_scope(),
            safe_next_actions=[
                "先恢复或识别你想撤销的任务。",
                *default_safe_next_actions(),
            ],
            suggested_replies=default_suggested_replies(),
            needs_user_confirmation=[
                "需要你确认撤销范围；没有范围确认前，Codex 只能先看影响和给计划。",
            ],
            non_actions=default_non_actions(),
        )

    summary = summarize_boundary(active, active)
    task = summary.task.strip() or "当前任务"
    current_stage = summary.current_step_label
    return UndoRequestBrief(
        raw_request=raw,
        status="needs-undo-scope",
        current_task=task,
        request_understanding=(
            "我会把这句话理解为：你可能想撤销某个改动，但还不能直接执行，"
            "因为撤销可能删除文件、丢掉已有工作或影响当前任务记录。"
        ),
        required_scope=[
            *default_required_scope(),
            f"当前记录显示阶段在：{current_stage}；如果只想撤销这个阶段的改动，请直接说明。",
        ],
        safe_next_actions=default_safe_next_actions(),
        suggested_replies=default_suggested_replies(),
        needs_user_confirmation=[
            "需要你确认撤销范围。",
            "如果确认后涉及删除、回滚、reset 或代码提交流程，还需要再次明确授权。",
        ],
        non_actions=default_non_actions(),
    )


def render_user(brief: UndoRequestBrief) -> str:
    lines = [
        "# 撤销请求说明",
        "",
        "当前任务：",
        f"- {brief.current_task}",
        "",
        "我对这句话的理解：",
        f"- {brief.request_understanding}",
        "",
        "需要先确认的范围：",
        *[f"- {item}" for item in brief.required_scope],
        "",
        "Codex 可以先安全做什么：",
        *[f"- {item}" for item in brief.safe_next_actions],
        "",
        "你可以这样回复：",
        *[f"- {item}" for item in brief.suggested_replies],
        "",
        "需要你确认：",
        *[f"- {item}" for item in brief.needs_user_confirmation],
        "",
        "这次不会做什么：",
        *[f"- {item}" for item in brief.non_actions],
    ]
    return "\n".join(lines)


def render_markdown(brief: UndoRequestBrief) -> str:
    lines = [
        "# 非技术撤销请求说明",
        "",
        f"- 状态：{brief.status}",
        f"- 当前任务：{brief.current_task}",
        f"- 请求理解：{brief.request_understanding}",
        "- 需要先确认的范围：",
        *[f"  - {item}" for item in brief.required_scope],
        "- 安全下一步：",
        *[f"  - {item}" for item in brief.safe_next_actions],
        "- 建议回复：",
        *[f"  - {item}" for item in brief.suggested_replies],
        "- 需要用户确认：",
        *[f"  - {item}" for item in brief.needs_user_confirmation],
        "- 不执行动作：",
        *[f"  - {item}" for item in brief.non_actions],
    ]
    return "\n".join(lines)


def render_json(brief: UndoRequestBrief) -> str:
    return json.dumps(asdict(brief), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's undo / revert-style request.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    brief = build_undo_request_brief(args)
    if args.format == "json":
        print(render_json(brief))
    elif args.format == "user":
        print(render_user(brief))
    else:
        print(render_markdown(brief))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
