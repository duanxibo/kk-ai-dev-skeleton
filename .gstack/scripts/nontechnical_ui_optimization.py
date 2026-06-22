#!/usr/bin/env python3
"""Explain the automatic UI optimization safeguards for terse user requests.

This helper is deterministic and read-only. It does not create evidence, edit
UI files, open browsers, connect to services, touch databases, or run code
workflow actions. Codex uses it to prove that a short request such as
"进行 UI 优化" enters the UI quality workflow without asking the user to name
internal skills or gates.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class UiOptimizationPlan:
    raw_request: str
    status: str
    user_goal: str
    codex_will_do: list[str]
    protected_scope: list[str]
    internal_chain: list[str]
    evidence_to_create: list[str]
    acceptance_focus: list[str]
    needs_user_confirmation: bool
    user_question: str


def optional_context(label: str, value: str) -> str:
    return f"{label}: {value}" if value else ""


def build_plan(args: argparse.Namespace) -> UiOptimizationPlan:
    context = [
        optional_context("使用者", args.audience),
        optional_context("成功样子", args.success),
        optional_context("本次不做", args.non_goal),
    ]
    context = [item for item in context if item]
    goal = "优化当前项目的用户可见界面质量"
    if context:
        goal = f"{goal}；" + "；".join(context)

    return UiOptimizationPlan(
        raw_request=args.raw,
        status="ui-optimization-ready",
        user_goal=goal,
        codex_will_do=[
            "先识别要优化的页面、目标用户、使用频率和第一眼要看懂的内容。",
            "先做 UI 设计梳理，明确页面类型、信息架构、主流程、组件计划、视觉方向、状态和响应式策略。",
            "在已声明的任务范围内实现页面视觉、布局、信息层级、状态展示和响应式优化。",
            "实现后做视觉复核，检查页面类型是否匹配、信息层级是否清楚、组件状态是否完整、移动端是否安全。",
            "最后做浏览器验收，实际打开页面操作关键控件，记录验收结果。",
        ],
        protected_scope=[
            "不改 API 合同。",
            "不改数据合同。",
            "不改 runner 逻辑。",
            "不接真实服务、真实数据、生产环境或数据库。",
            "不执行代码提交流程，除非用户另行明确授权。",
        ],
        internal_chain=[
            "kk-task-kickoff",
            "kk-ui-design-kickoff",
            "implementation",
            "kk-ui-polish-review",
            "browser-qa",
        ],
        evidence_to_create=[
            "requirement / review / task boundary",
            "UI design brief",
            "UI polish review",
            "browser QA report",
        ],
        acceptance_focus=[
            "第一眼是否能看懂页面目的。",
            "主流程是否更清楚。",
            "关键控件是否可见、可操作、有状态反馈。",
            "桌面和移动端是否没有明显遮挡、溢出或错位。",
            "优化后是否仍保持原有 API、数据合同和 runner 行为不变。",
        ],
        needs_user_confirmation=False,
        user_question="",
    )


def render_user(plan: UiOptimizationPlan) -> str:
    lines = [
        "# UI 优化开工说明",
        "",
        "我会把这句话当成用户可见界面的优化任务处理。",
        "",
        "Codex 会自动做：",
    ]
    lines.extend(f"- {item}" for item in plan.codex_will_do)
    lines.extend(["", "这次默认不会做："])
    lines.extend(f"- {item}" for item in plan.protected_scope)
    lines.extend(["", "完成后会这样验收："])
    lines.extend(f"- {item}" for item in plan.acceptance_focus)
    lines.extend(
        [
            "",
            "需要你确认：",
            "- 暂时不需要；Codex 会先根据当前项目和页面自己补齐任务范围。",
        ]
    )
    return "\n".join(lines)


def render_json(plan: UiOptimizationPlan) -> str:
    return json.dumps(asdict(plan), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original plain-language request.")
    parser.add_argument("--audience", default="", help="Optional target user or usage context.")
    parser.add_argument("--success", default="", help="Optional visible success criteria.")
    parser.add_argument("--non-goal", default="", help="Optional explicit non-goals or forbidden scope.")
    parser.add_argument("--format", choices=("user", "json"), default="user")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = build_plan(args)
    print(render_json(plan) if args.format == "json" else render_user(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
