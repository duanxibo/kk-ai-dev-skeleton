#!/usr/bin/env python3
"""Render a request-specific acceptance plan for a nontechnical user.

This helper is deterministic and read-only. It does not create formal evidence,
connect to data sources, run production actions, touch databases, open browsers,
or run git workflow actions. Codex uses it when the user asks how to accept or
verify a specific desired change, rather than the current active task.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass

from nontechnical_intake import IntakeSummary, build_summary
from nontechnical_task_starter import build_acceptance_checks, detect_forbidden_scopes, user_text


@dataclass(frozen=True)
class AcceptancePlan:
    status: str
    status_reason: str
    can_continue: bool
    summary: IntakeSummary
    acceptance_checks: list[str]
    user_actions_to_verify: list[str]
    expected_results: list[str]
    needs_user_confirmation: list[str]
    risk_notes: list[str]
    forbidden_scopes: list[str]
    next_user_message: str


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def acceptance_subject(raw: str) -> str:
    text = compact(raw)
    patterns = (
        r"[，,。？?\s]*(怎么验收|如何验收|验收标准是什么|验收标准|验收方式是什么|验收方式|验收清单)[。？?\s]*$",
        r"[，,。？?\s]*(怎么知道它真的好了|怎么知道真的好了|我怎么知道它好了|完成后怎么看|怎么判断)[。？?\s]*$",
        r"[，,。？?\s]*(acceptance criteria)[。？?\s]*$",
    )
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
    return text or compact(raw)


def status_for(summary: IntakeSummary) -> str:
    if summary.risks and summary.risk_confirmation_status != "safe-to-draft":
        return "pause-for-risk"
    if not summary.can_continue:
        return "needs-clarification"
    if summary.risks:
        return "controlled-acceptance-plan"
    return "ready-to-acceptance-plan"


def append_unique(items: list[str], value: str) -> None:
    cleaned = compact(value)
    if cleaned and cleaned not in items:
        items.append(cleaned)


def build_user_actions(checks: list[str], summary: IntakeSummary) -> list[str]:
    actions: list[str] = []
    for check in checks:
        if "第一眼能看到" in check:
            append_unique(actions, f"打开或查看目标结果，先确认第一眼结果符合：{check.split('：', 1)[-1]}")
        if "页面上的关键入口" in check:
            append_unique(actions, "在页面上依次尝试关键入口、操作控件、空态和结果变化。")
        if "搜索、筛选或排序" in check:
            append_unique(actions, "输入关键词、切换筛选条件或排序，并观察结果是否真实变化。")
        if "导出的文件" in check:
            append_unique(actions, "触发导出，打开导出的文件，核对内容是否对应当前筛选范围。")
        if "数据来源" in check:
            append_unique(actions, "让 Codex 展示数据来源、字段口径、范围、权限和是否真实数据。")
        if "接口输入" in check:
            append_unique(actions, "让 Codex 展示接口输入、输出、异常情况和复用边界的检查结果。")
        if "命令可以重复运行" in check:
            append_unique(actions, "重复运行命令，确认成功输出和失败提示都清楚。")
        if "文档说明" in check:
            append_unique(actions, "从说明入口重新走一遍，确认能找到下一步和验收方式。")
        if "多人验收" in check:
            append_unique(actions, "按已确认的协作方式，让不同角色或负责人查看状态与结果。")
        if "明确不做" in check or "明确禁止" in check:
            append_unique(actions, "检查这次明确不做或禁止的范围没有被改动。")
        if "高风险动作" in check:
            append_unique(actions, "确认高风险动作没有执行，或只停留在你确认的安全范围内。")
    if "数据查询 / 数据接入" in summary.likely_surface and not any("数据来源" in item for item in actions):
        append_unique(actions, "确认数据来源、字段口径和权限边界已经说清楚。")
    if not actions:
        append_unique(actions, "按验收清单逐条让 Codex 展示通过 / 未通过证据。")
    return actions[:8]


def build_expected_results(args: argparse.Namespace, checks: list[str], summary: IntakeSummary) -> list[str]:
    results: list[str] = []
    if args.success:
        append_unique(results, f"第一眼结果符合：{compact(args.success)}")
    for check in checks:
        if "页面上的关键入口" in check:
            append_unique(results, "页面入口、关键操作、空态和结果变化都能实际看见。")
        if "搜索、筛选或排序" in check:
            append_unique(results, "搜索、筛选或排序后，结果会随条件变化，而不是只改文案。")
        if "导出的文件" in check:
            append_unique(results, "导出文件能打开，内容对应当前任务约定的范围。")
        if "数据来源" in check:
            append_unique(results, "数据来源、字段口径、范围和权限边界清楚，没有把不确定数据当成已确认结果。")
        if "接口输入" in check:
            append_unique(results, "接口输入输出、异常情况和复用边界能对上用户目标。")
        if "命令可以重复运行" in check:
            append_unique(results, "命令可重复运行；失败时能看到明确提示和下一步。")
        if "文档说明" in check:
            append_unique(results, "文档能让用户重新找到入口、下一步和验收方式。")
        if "多人验收" in check:
            append_unique(results, "多人或团队状态只按已确认协作方式展示，不伪装成实时同步。")
        if "明确不做" in check or "明确禁止" in check:
            append_unique(results, "明确不做或禁止的范围保持未触碰。")
    if "不确定" == summary.likely_surface:
        append_unique(results, "先补清楚你要验收的是页面变化、数据结果、接口能力、脚本输出还是文档说明。")
    if not results:
        append_unique(results, "每条验收项都有能复查的通过 / 未通过说明。")
    return results[:8]


def confirmation_points(summary: IntakeSummary) -> list[str]:
    if summary.risks and summary.risk_confirmation_status != "safe-to-draft":
        return [summary.suggested_question]
    if not summary.can_continue:
        return [summary.suggested_question]
    points: list[str] = []
    points.extend(summary.missing_info)
    if "数据查询 / 数据接入" in summary.likely_surface:
        append_unique(points, "涉及真实数据或数据源选择时，需要你确认数据范围和权限。")
    if "后端接口 / 服务能力" in summary.likely_surface:
        append_unique(points, "如果接口口径影响业务结果，需要你确认口径。")
    if summary.risks and summary.risk_confirmation_status == "safe-to-draft":
        append_unique(points, "后续任何真实数据、生产环境、数据库或代码提交流程动作仍需你另行确认。")
    if not points:
        append_unique(points, "暂时没有需要你先确认的阻塞点。")
    return points


def risk_notes(summary: IntakeSummary) -> list[str]:
    if summary.risks:
        notes = list(summary.risks)
        if summary.risk_confirmation_status == "safe-to-draft":
            notes.append("这些风险已被限制为只整理范围和验收口径，不能直接执行。")
        else:
            notes.append("确认前不会执行真实数据、生产环境、数据库、破坏性命令或代码提交流程。")
        return notes
    return ["未命中真实数据、生产环境、数据库、破坏性命令或代码提交流程风险。"]


def next_user_message(plan: AcceptancePlan) -> str:
    if plan.status == "pause-for-risk":
        return f"我会先暂停高风险动作，只确认这个问题：{plan.needs_user_confirmation[0]}"
    if plan.status == "needs-clarification":
        return f"我会先补一个关键信息，再继续整理验收计划：{plan.needs_user_confirmation[0]}"
    if plan.status == "controlled-acceptance-plan":
        return "我可以给出受控验收计划，但只会整理范围和验收口径，不执行高风险动作。"
    return "我可以按这份清单帮你验收，并在需要你判断业务或权限时再问你。"


def build_acceptance_plan(args: argparse.Namespace) -> AcceptancePlan:
    summary_args = argparse.Namespace(**vars(args))
    summary_args.raw = acceptance_subject(args.raw)
    summary = build_summary(summary_args)
    check_args = argparse.Namespace(**vars(args))
    check_args.raw = summary_args.raw
    forbidden_scopes, _ = detect_forbidden_scopes(args.raw, args.non_goal)
    checks = build_acceptance_checks(check_args, summary, forbidden_scopes)
    status = status_for(summary)
    plan = AcceptancePlan(
        status=status,
        status_reason=summary.continue_reason,
        can_continue=summary.can_continue,
        summary=summary,
        acceptance_checks=checks,
        user_actions_to_verify=build_user_actions(checks, summary),
        expected_results=build_expected_results(args, checks, summary),
        needs_user_confirmation=confirmation_points(summary),
        risk_notes=risk_notes(summary),
        forbidden_scopes=forbidden_scopes,
        next_user_message="",
    )
    return AcceptancePlan(**{**asdict(plan), "summary": summary, "next_user_message": next_user_message(plan)})


def render_user(plan: AcceptancePlan) -> str:
    summary = plan.summary
    if plan.status in {"pause-for-risk", "needs-clarification"}:
        intro = "我会先停在安全的位置，不直接给可执行验收。"
        if plan.status == "needs-clarification":
            intro = "我会先补一个关键信息，再整理验收方式。"
        return "\n".join(
            [
                intro,
                "",
                f"我理解你想做的是：{user_text(summary.understood_goal)}",
                "",
                f"需要你确认：{user_text(plan.needs_user_confirmation[0])}",
                "",
                "确认前不会操作真实数据、生产环境、数据库、破坏性命令或代码提交流程。",
            ]
        )

    lines = [
        f"我理解你想做的是：{user_text(summary.understood_goal)}",
        "",
        "可以这样验收：",
        *[f"- {user_text(item)}" for item in plan.acceptance_checks],
        "",
        "你要实际看到 / 操作：",
        *[f"- {user_text(item)}" for item in plan.user_actions_to_verify],
        "",
        "预期应该看到：",
        *[f"- {user_text(item)}" for item in plan.expected_results],
        "",
        "需要你确认：",
        *[f"- {user_text(item)}" for item in plan.needs_user_confirmation],
        "",
        "风险说明：",
        *[f"- {user_text(item)}" for item in plan.risk_notes],
    ]
    if plan.forbidden_scopes:
        lines.extend(["", "我会避开这些范围：", *[f"- {scope}" for scope in plan.forbidden_scopes]])
    return "\n".join(lines)


def render_markdown(plan: AcceptancePlan) -> str:
    summary = plan.summary
    lines = [
        "# 非技术需求级验收计划",
        "",
        f"- 状态：{plan.status}",
        f"- 是否可继续：{'是' if plan.can_continue else '否'}",
        f"- 状态原因：{plan.status_reason}",
        f"- 我理解你想做的是：{summary.understood_goal}",
        f"- 可能实现表面：{summary.likely_surface}",
        "- 可以这样验收：",
        *[f"  - {item}" for item in plan.acceptance_checks],
        "- 用户要实际看到 / 操作：",
        *[f"  - {item}" for item in plan.user_actions_to_verify],
        "- 预期应该看到：",
        *[f"  - {item}" for item in plan.expected_results],
        "- 需要用户确认：",
        *[f"  - {item}" for item in plan.needs_user_confirmation],
        "- 风险说明：",
        *[f"  - {item}" for item in plan.risk_notes],
        f"- 给用户的下一句话：{plan.next_user_message}",
    ]
    return "\n".join(lines)


def render_json(plan: AcceptancePlan) -> str:
    return json.dumps(asdict(plan), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original plain-language request.")
    parser.add_argument("--audience", default="", help="Optional target user or usage context.")
    parser.add_argument("--success", default="", help="Optional visible success criteria.")
    parser.add_argument("--non-goal", default="", help="Optional explicit non-goals or forbidden scope.")
    parser.add_argument("--risk-confirmation", default="", help="Optional user confirmation constraining high-risk actions.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    plan = build_acceptance_plan(args)
    if args.format == "json":
        print(render_json(plan))
    elif args.format == "user":
        print(render_user(plan))
    else:
        print(render_markdown(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
