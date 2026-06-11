#!/usr/bin/env python3
"""Explain how Codex will pause current work after a nontechnical request.

This helper is deterministic and read-only. It turns "pause / stop for now"
style prompts into user-facing language. It does not write local mode, change
task state, delete edits, reset files, create evidence, connect to data
sources, operate production systems, or run git actions.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from gstack_dashboard import active_boundary, read_text, summarize_boundary


@dataclass(frozen=True)
class PauseBrief:
    raw_request: str
    status: str
    current_task: str
    pause_understanding: str
    preserved_context: list[str]
    stopped_actions: list[str]
    resume_options: list[str]
    needs_user_confirmation: list[str]
    non_actions: list[str]


def compact(raw: str) -> str:
    return " ".join(raw.strip().split())


def default_non_actions() -> list[str]:
    return [
        "不会继续修改文件、运行新的实现步骤或推进当前任务。",
        "不会删除、撤销、reset、回滚或清理已有改动。",
        "不会连接真实数据、生产环境、数据库、外部服务或执行破坏性命令。",
        "不会执行代码提交流程。",
        "不会写入或切换以后默认协作模式。",
    ]


def preserved_for_active_task() -> list[str]:
    return [
        "当前任务记录仍然保留，之后可以继续读取。",
        "已经生成的需求、评审、边界和验收记录不会因为暂停自动删除。",
        "当前本地工作树不会因为暂停自动回滚。",
    ]


def build_pause_brief(args: argparse.Namespace) -> PauseBrief:
    raw = compact(args.raw)
    active = active_boundary()
    if active is None:
        return PauseBrief(
            raw_request=raw,
            status="no-active-task",
            current_task="当前没有读到明确任务。",
            pause_understanding="我会按暂停处理；现在没有明确 active task，所以不会继续推进任何具体任务。",
            preserved_context=[
                "如果之前有任务记录，Codex 需要先恢复或识别它，之后才能继续。",
                "暂停不会自动删除文件或回滚改动。",
            ],
            stopped_actions=[
                "不继续进入实现、验证、文档同步或其他推进步骤。",
                "不把这句话当成新的需求开工。",
            ],
            resume_options=[
                "之后可以说“继续做”，让 Codex 先恢复当前任务。",
                "也可以直接说明要继续哪件事。",
            ],
            needs_user_confirmation=["暂时不需要；只有你要恢复、撤销或执行高风险动作时才需要再确认。"],
            non_actions=default_non_actions(),
        )

    text = read_text(active)
    summary = summarize_boundary(active, active)
    task = summary.task.strip() or "当前任务"
    stopped = [
        "不继续推进当前任务的下一阶段。",
        "不把“暂停”理解成“撤销”或“删除”。",
        "不把“暂停”理解成“切换以后默认模式”。",
    ]
    if summary.current_step_key != "complete":
        stopped.append(f"当前阶段停在：{summary.current_step_label}。")
    else:
        stopped.append("当前任务记录显示已收口；暂停后不会自动开启下一段优化。")

    return PauseBrief(
        raw_request=raw,
        status="paused",
        current_task=task,
        pause_understanding="我会按“先暂停当前推进”处理，而不是当成新需求、继续推进或协作模式切换。",
        preserved_context=preserved_for_active_task(),
        stopped_actions=stopped,
        resume_options=[
            "之后说“继续做”，Codex 会按当前任务记录继续判断下一步。",
            "说“现在需要我确认什么”，Codex 会先列出是否等你拍板。",
            "如果你想撤销或删除改动，需要单独明确说撤销范围；这会另行确认。",
        ],
        needs_user_confirmation=["暂时不需要你确认；我会先停止继续推进。"],
        non_actions=default_non_actions(),
    )


def render_user(brief: PauseBrief) -> str:
    lines = [
        "# 暂停说明",
        "",
        "我会先暂停。",
        "",
        "当前任务：",
        f"- {brief.current_task}",
        "",
        "我对这句话的理解：",
        f"- {brief.pause_understanding}",
        "",
        "暂停后不会继续做什么：",
        *[f"- {item}" for item in brief.stopped_actions],
        "",
        "已经保留的内容：",
        *[f"- {item}" for item in brief.preserved_context],
        "",
        "之后怎么恢复：",
        *[f"- {item}" for item in brief.resume_options],
        "",
        "需要你确认：",
        *[f"- {item}" for item in brief.needs_user_confirmation],
        "",
        "这次不会做什么：",
        *[f"- {item}" for item in brief.non_actions],
    ]
    return "\n".join(lines)


def render_markdown(brief: PauseBrief) -> str:
    lines = [
        "# 非技术暂停说明",
        "",
        f"- 状态：{brief.status}",
        f"- 当前任务：{brief.current_task}",
        f"- 暂停理解：{brief.pause_understanding}",
        "- 已保留内容：",
        *[f"  - {item}" for item in brief.preserved_context],
        "- 暂停后不继续：",
        *[f"  - {item}" for item in brief.stopped_actions],
        "- 恢复方式：",
        *[f"  - {item}" for item in brief.resume_options],
        "- 需要用户确认：",
        *[f"  - {item}" for item in brief.needs_user_confirmation],
        "- 不执行动作：",
        *[f"  - {item}" for item in brief.non_actions],
    ]
    return "\n".join(lines)


def render_json(brief: PauseBrief) -> str:
    return json.dumps(asdict(brief), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's pause-style request.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    brief = build_pause_brief(args)
    if args.format == "json":
        print(render_json(brief))
    elif args.format == "user":
        print(render_user(brief))
    else:
        print(render_markdown(brief))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
