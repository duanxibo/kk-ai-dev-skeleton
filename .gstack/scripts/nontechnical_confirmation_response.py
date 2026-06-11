#!/usr/bin/env python3
"""Explain how Codex interprets a terse nontechnical confirmation safely.

This helper is deterministic and read-only. It turns "I confirm / OK / agree"
style prompts into user-facing language. It does not advance task state, modify
files, connect to data sources, operate production systems, or run git actions.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass

from gstack_dashboard import active_boundary, read_text, summarize_boundary


HIGH_RISK_WORDS = (
    "真实数据",
    "生产",
    "线上",
    "数据库",
    "外部服务",
    "发布",
    "代码提交流程",
    "git",
    "删除",
    "撤销",
    "reset",
    "回滚",
    "清理",
    "破坏性",
)


@dataclass(frozen=True)
class ConfirmationResponseBrief:
    raw_request: str
    status: str
    current_task: str
    response_understanding: str
    can_confirm: list[str]
    still_needs_clarity: list[str]
    safe_next_actions: list[str]
    suggested_replies: list[str]
    non_actions: list[str]


def compact(raw: str) -> str:
    return " ".join(raw.strip().split())


def contains_high_risk(text: str) -> bool:
    lowered = text.lower()
    return any(word.lower() in lowered for word in HIGH_RISK_WORDS)


def default_non_actions() -> list[str]:
    return [
        "不会把一句“我确认 / 可以 / 同意”当成真实数据、生产环境、数据库或外部服务授权。",
        "不会把模糊确认当成删除、撤销、强制回退、回滚或清理改动的授权。",
        "不会执行代码提交流程。",
        "不会推进当前任务状态、修改文件或进入实现。",
        "不会清理敏感配置或改写以后默认协作模式。",
    ]


def default_safe_actions() -> list[str]:
    return [
        "先复述我理解的确认范围，让你检查是否正确。",
        "继续做只读整理：确认当前任务、列出下一步、补齐需要你判断的问题。",
        "如果下一步涉及高风险动作，先停下来问你更明确的范围和授权。",
    ]


def suggested_replies_for(high_risk: bool) -> list[str]:
    replies = [
        "确认，按当前低风险整理范围继续，不操作真实数据、不写数据库、不发布、不提交。",
        "确认，只先给计划和影响说明，不改文件。",
        "我还没确认高风险动作，只是确认你理解的方向。",
    ]
    if high_risk:
        replies.extend(
            [
                "允许查看影响范围，但不允许执行删除、回滚或清理。",
                "允许继续到下一步，但禁止真实数据、生产、数据库和代码提交流程。",
            ]
        )
    else:
        replies.append("确认，继续做下一步；如果遇到高风险动作再问我。")
    return replies


def build_confirmation_response(args: argparse.Namespace) -> ConfirmationResponseBrief:
    raw = compact(args.raw)
    active = active_boundary()
    if active is None:
        return ConfirmationResponseBrief(
            raw_request=raw,
            status="no-active-task",
            current_task="当前没有读到明确任务。",
            response_understanding="我会把这句话理解为你愿意继续沟通，但现在没有明确任务，不能判断你确认的是哪件事。",
            can_confirm=["可以确认你愿意继续当前对话。"],
            still_needs_clarity=[
                "需要先说明你确认的是哪个任务或哪一条建议。",
                "如果涉及真实数据、生产、数据库、撤销、删除或代码提交流程，需要明确允许范围和禁止范围。",
            ],
            safe_next_actions=["先恢复或识别当前任务，再复述需要确认的范围。"],
            suggested_replies=suggested_replies_for(high_risk=True),
            non_actions=default_non_actions(),
        )

    text = read_text(active)
    summary = summarize_boundary(active, active)
    task = summary.task.strip() or "当前任务"
    high_risk = contains_high_risk(text)
    stage = summary.current_step_label
    can_confirm = [
        "可以确认你看到了上一条说明，并愿意让 Codex 继续处理低风险的整理、复述或检查。",
        "可以确认 Codex 对当前方向的理解大体正确。",
    ]
    still_needs = [
        "如果你确认的是具体范围，请直接说清楚：确认哪一部分、哪些不碰。",
        "如果你只是想继续低风险整理，可以明确说“不操作真实数据、不写数据库、不发布、不提交”。",
        f"当前记录显示阶段在：{stage}；如果要进入下一步，需要确认这一阶段对应的范围是否正确。",
    ]
    if high_risk:
        still_needs.append(
            "当前任务记录包含高风险词或禁止动作；一句“我确认”不能自动授权真实数据、生产、数据库、删除、回滚或代码提交流程。"
        )

    return ConfirmationResponseBrief(
        raw_request=raw,
        status="needs-confirmation-scope",
        current_task=task,
        response_understanding=(
            "我会把这句话理解为：你可能同意继续，但确认范围还不够具体；"
            "它不能自动代表高风险授权。"
        ),
        can_confirm=can_confirm,
        still_needs_clarity=still_needs,
        safe_next_actions=default_safe_actions(),
        suggested_replies=suggested_replies_for(high_risk=high_risk),
        non_actions=default_non_actions(),
    )


def render_user(brief: ConfirmationResponseBrief) -> str:
    lines = [
        "# 确认回复说明",
        "",
        "当前任务：",
        f"- {brief.current_task}",
        "",
        "我对这句话的理解：",
        f"- {brief.response_understanding}",
        "",
        "这句话可以确认什么：",
        *[f"- {item}" for item in brief.can_confirm],
        "",
        "还需要说清楚什么：",
        *[f"- {item}" for item in brief.still_needs_clarity],
        "",
        "Codex 可以先安全做什么：",
        *[f"- {item}" for item in brief.safe_next_actions],
        "",
        "你可以这样回复：",
        *[f"- {item}" for item in brief.suggested_replies],
        "",
        "这次不会做什么：",
        *[f"- {item}" for item in brief.non_actions],
    ]
    return "\n".join(lines)


def render_markdown(brief: ConfirmationResponseBrief) -> str:
    lines = [
        "# 非技术确认回复说明",
        "",
        f"- 状态：{brief.status}",
        f"- 当前任务：{brief.current_task}",
        f"- 确认理解：{brief.response_understanding}",
        "- 可以确认：",
        *[f"  - {item}" for item in brief.can_confirm],
        "- 仍需明确：",
        *[f"  - {item}" for item in brief.still_needs_clarity],
        "- 安全下一步：",
        *[f"  - {item}" for item in brief.safe_next_actions],
        "- 建议回复：",
        *[f"  - {item}" for item in brief.suggested_replies],
        "- 不执行动作：",
        *[f"  - {item}" for item in brief.non_actions],
    ]
    return "\n".join(lines)


def render_json(brief: ConfirmationResponseBrief) -> str:
    return json.dumps(asdict(brief), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's terse confirmation response.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    brief = build_confirmation_response(args)
    if args.format == "json":
        print(render_json(brief))
    elif args.format == "user":
        print(render_user(brief))
    else:
        print(render_markdown(brief))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
