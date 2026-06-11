#!/usr/bin/env python3
"""Render a plain-language execution plan for a nontechnical request.

This helper is deterministic and read-only. It does not create formal evidence,
connect to data sources, run production actions, touch databases, or run git
workflow actions. Codex uses it to explain how a complex request will move from
idea to implementation and acceptance without exposing internal workflow terms.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass

from nontechnical_intake import IntakeSummary, build_summary
from nontechnical_task_starter import build_acceptance_checks, detect_forbidden_scopes, user_text


PLAN_ONLY_KEYWORDS = (
    "拆任务",
    "拆成几个小任务",
    "拆成小任务",
    "任务拆解",
    "拆解任务",
    "排优先级",
    "排一下优先级",
    "优先级",
    "定顺序",
    "里程碑",
    "阶段怎么验收",
    "每个阶段怎么验收",
    "每一步验收",
    "每一步怎么验收",
    "先做哪几个",
)


@dataclass(frozen=True)
class PlanPhase:
    title: str
    codex_action: str
    user_visible_result: str


@dataclass(frozen=True)
class ExecutionPlan:
    status: str
    status_reason: str
    can_continue: bool
    summary: IntakeSummary
    phases: list[PlanPhase]
    codex_can_do: list[str]
    needs_user_confirmation: list[str]
    acceptance_checks: list[str]
    risk_notes: list[str]
    forbidden_scopes: list[str]
    next_user_message: str


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def has_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def is_plan_only_request(raw: str) -> bool:
    return has_any(raw, PLAN_ONLY_KEYWORDS)


def plan_subject(raw: str) -> str:
    text = compact(raw)
    patterns = (
        r"[，,。？?\s]*(你会怎么推进|你会怎么做|会怎么做|怎么推进|怎么安排)[。？?\s]*$",
        r"[，,。？?\s]*(请)?(给我)?(一份)?(执行计划|开发计划|实施计划|推进计划|推进顺序|路线图)[。？?\s]*$",
        r"[，,。？?\s]*(什么时候需要我确认|需要我确认什么)[。？?\s]*$",
    )
    for pattern in patterns:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE).strip()
    return text or compact(raw)


def status_for(summary: IntakeSummary, *, plan_only: bool) -> str:
    if summary.risks and summary.risk_confirmation_status != "safe-to-draft":
        return "pause-for-risk"
    if plan_only:
        return "ready-to-plan"
    if not summary.can_continue:
        return "needs-clarification"
    if summary.risks:
        return "controlled-plan"
    return "ready-to-plan"


def status_reason_for(summary: IntakeSummary, *, plan_only: bool) -> str:
    if plan_only and not summary.can_continue and not summary.risks:
        return "用户要求拆任务、排优先级或里程碑计划；可以先给出阶段框架，但正式开工前仍需补齐关键业务信息。"
    return summary.continue_reason


def phase_from_slice(slice_text: str, surface: str) -> PlanPhase:
    text = compact(slice_text)
    if "安全范围" in text or "风险" in text:
        return PlanPhase(
            title="先锁定安全范围",
            codex_action="把你允许和不允许的事先写清楚，只整理范围和验收口径。",
            user_visible_result="你会看到哪些高风险动作不会被执行。",
        )
    if "补齐目标用户" in text or "实现表面" in text:
        return PlanPhase(
            title="先补齐关键信息",
            codex_action="确认给谁用、第一眼成功样子、本次不做什么，以及最终是页面、数据、接口、脚本还是文档结果。",
            user_visible_result="你会看到一个能继续拆任务的清晰目标，而不是一串工程术语。",
        )
    if "期待看到的是页面变化" in text:
        return PlanPhase(
            title="确认交付表面",
            codex_action="先判断这次用户要验收的是页面变化、数据结果、接口能力、脚本输出还是文档说明。",
            user_visible_result="你会知道每个阶段应该看哪里、点哪里或检查什么结果。",
        )
    if "需求" in text or "验收" in text and "写入" not in text:
        return PlanPhase(
            title="先固定目标和验收方式",
            codex_action="整理目标用户、成功样子、本次不做什么，以及完成后怎么判断真的好了。",
            user_visible_result="你会看到一份不需要工程术语也能读懂的任务说明。",
        )
    if "可见路径" in text or "页面入口" in text:
        return PlanPhase(
            title="再做最小可见版本",
            codex_action="优先做用户能直接看到或操作的最小路径，避免一开始把复杂需求摊太大。",
            user_visible_result="你能看到入口、关键操作、空态和结果变化。",
        )
    if "数据" in text or "字段" in text or "只读" in text:
        return PlanPhase(
            title="再确认数据边界",
            codex_action="确认数据来源、字段口径、范围、权限，以及是否只能只读探索。",
            user_visible_result="你会知道哪些数据能用、哪些不能直接动。",
        )
    if "接口" in text or "输入输出" in text:
        return PlanPhase(
            title="再确认接口边界",
            codex_action="确认输入、输出、异常情况和复用边界，再进入实现。",
            user_visible_result="你会看到接口能力和页面目标如何对应。",
        )
    if "命令" in text or "失败提示" in text:
        return PlanPhase(
            title="再补可重复运行路径",
            codex_action="保留可重复运行的本地检查和失败后的下一步提示。",
            user_visible_result="你能知道失败时 Codex 会继续查什么。",
        )
    if "QA" in text or "验收记录" in text or "evidence" in text:
        return PlanPhase(
            title="最后验收并记录",
            codex_action="运行本地检查，并把结果写成可复查的验收记录。",
            user_visible_result="你会看到做了什么、怎么验收、是否通过和剩余风险。",
        )
    if "文档" in text or "说明" in text:
        return PlanPhase(
            title="再同步说明",
            codex_action="把入口、步骤和验收方式同步到长期说明里。",
            user_visible_result="你能从项目说明中重新找到这套用法。",
        )
    return PlanPhase(
        title="推进一个可验收切片",
        codex_action=text,
        user_visible_result=f"你会看到这一阶段的结果和验收方式。当前判断：{surface}",
    )


def build_phases(summary: IntakeSummary) -> list[PlanPhase]:
    phases: list[PlanPhase] = []
    seen: set[str] = set()
    for delivery_slice in summary.delivery_slices:
        phase = phase_from_slice(delivery_slice, summary.likely_surface)
        if phase.title not in seen:
            phases.append(phase)
            seen.add(phase.title)
    if not phases:
        phases.append(
            PlanPhase(
                title="先整理目标",
                codex_action="把你想要的结果转成可实现、可验收的小步骤。",
                user_visible_result="你会看到下一步做什么以及完成后怎么判断。",
            )
        )
    return phases[:5]


def codex_can_do(summary: IntakeSummary) -> list[str]:
    actions = [
        "把目标、使用者、成功样子和不做范围整理成任务起点。",
        "把复杂需求拆成几个可以分别验收的阶段。",
        "在本地运行能证明结果的检查，并把通过 / 未通过说清楚。",
    ]
    if "用户可见页面能力" in summary.likely_surface:
        actions.append("优先验证用户看得见、点得动、能判断结果变化的部分。")
    if "数据查询 / 数据接入" in summary.likely_surface:
        actions.append("先把数据来源、字段口径、权限和只读 / 写入边界说清楚。")
    if "后端接口 / 服务能力" in summary.likely_surface:
        actions.append("先把接口输入、输出、异常和复用边界说清楚。")
    if summary.risks and summary.risk_confirmation_status == "safe-to-draft":
        actions.append("只在你确认的安全范围内整理计划，不执行高风险动作。")
    return actions


def confirmation_points(summary: IntakeSummary, *, plan_only: bool = False) -> list[str]:
    if summary.risks and summary.risk_confirmation_status != "safe-to-draft":
        return [summary.suggested_question]
    if plan_only and not summary.can_continue:
        return [summary.suggested_question]
    points: list[str] = []
    points.extend(summary.missing_info)
    if "数据查询 / 数据接入" in summary.likely_surface:
        points.append("涉及真实数据或数据源选择时，需要你确认数据范围和权限。")
    if "后端接口 / 服务能力" in summary.likely_surface:
        points.append("如果接口口径影响业务结果，需要你确认口径。")
    if not points:
        points.append("暂时没有需要你先确认的阻塞点。")
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


def acceptance_for_plan_only(summary: IntakeSummary, acceptance_checks: list[str]) -> list[str]:
    if summary.can_continue:
        return acceptance_checks
    generic = [
        "每个小任务都有明确的用户可见结果。",
        "每个阶段都有一个实际操作或检查方式，用来判断这一阶段是否完成。",
        "高风险或需要授权的事项会被单独标出来，不会混在普通任务里直接执行。",
    ]
    if acceptance_checks and acceptance_checks != ["完成后第一眼看到的结果已经在正式任务范围里写清楚"]:
        return [*acceptance_checks, *generic]
    return generic


def next_user_message(plan: ExecutionPlan) -> str:
    if plan.status == "pause-for-risk":
        return f"我会先暂停高风险动作，只确认这个问题：{plan.needs_user_confirmation[0]}"
    if plan.status == "needs-clarification":
        return f"我会先补一个关键信息，再继续推进：{plan.needs_user_confirmation[0]}"
    if plan.status == "ready-to-plan" and not plan.summary.can_continue:
        return f"我可以先给出拆解框架；正式开工前还需要确认：{plan.needs_user_confirmation[0]}"
    if plan.status == "controlled-plan":
        return "我可以给出受控执行计划，但只会整理范围和验收口径，不执行高风险动作。"
    return "我可以按这份计划继续推进，并在需要你判断业务或权限时再问你。"


def build_execution_plan(args: argparse.Namespace) -> ExecutionPlan:
    summary_args = argparse.Namespace(**vars(args))
    summary_args.raw = plan_subject(args.raw)
    summary = build_summary(summary_args)
    plan_only = is_plan_only_request(args.raw)
    forbidden_scopes, _ = detect_forbidden_scopes(args.raw, args.non_goal)
    acceptance_checks = build_acceptance_checks(args, summary, forbidden_scopes)
    if plan_only:
        acceptance_checks = acceptance_for_plan_only(summary, acceptance_checks)
    status = status_for(summary, plan_only=plan_only)
    can_continue = summary.can_continue or (plan_only and not summary.risks)
    plan = ExecutionPlan(
        status=status,
        status_reason=status_reason_for(summary, plan_only=plan_only),
        can_continue=can_continue,
        summary=summary,
        phases=build_phases(summary),
        codex_can_do=codex_can_do(summary),
        needs_user_confirmation=confirmation_points(summary, plan_only=plan_only),
        acceptance_checks=acceptance_checks,
        risk_notes=risk_notes(summary),
        forbidden_scopes=forbidden_scopes,
        next_user_message="",
    )
    return ExecutionPlan(**{**asdict(plan), "summary": summary, "phases": plan.phases, "next_user_message": next_user_message(plan)})


def render_user(plan: ExecutionPlan) -> str:
    summary = plan.summary
    if plan.status in {"pause-for-risk", "needs-clarification"}:
        return "\n".join(
            [
                "我会先停在安全的位置，不直接开始执行。",
                "",
                f"我理解你想做的是：{user_text(summary.understood_goal)}",
                "",
                f"需要你确认：{user_text(plan.needs_user_confirmation[0])}",
                "",
                "确认前不会操作真实数据、生产环境、数据库、破坏性命令或代码提交流程。",
            ]
        )

    lines = [
        "我会按这份执行计划推进：",
        "",
        f"我理解你想做的是：{user_text(summary.understood_goal)}",
        "",
        "推进顺序：",
    ]
    for index, phase in enumerate(plan.phases, start=1):
        lines.extend(
            [
                f"{index}. {user_text(phase.title)}",
                f"   Codex 会做：{user_text(phase.codex_action)}",
                f"   结果：{user_text(phase.user_visible_result)}",
            ]
        )
    lines.extend(["", "Codex 可以自动处理："])
    lines.extend(f"- {user_text(item)}" for item in plan.codex_can_do)
    lines.extend(["", "需要你确认："])
    lines.extend(f"- {user_text(item)}" for item in plan.needs_user_confirmation)
    lines.extend(["", "完成后可以这样验收："])
    lines.extend(f"- {user_text(item)}" for item in plan.acceptance_checks)
    lines.extend(["", "风险说明："])
    lines.extend(f"- {user_text(item)}" for item in plan.risk_notes)
    if plan.forbidden_scopes:
        lines.extend(["", "我会避开这些范围："])
        lines.extend(f"- {scope}" for scope in plan.forbidden_scopes)
    return "\n".join(lines)


def render_json(plan: ExecutionPlan) -> str:
    return json.dumps(asdict(plan), ensure_ascii=False, indent=2)


def render_markdown(plan: ExecutionPlan) -> str:
    summary = plan.summary
    lines = [
        "# 非技术执行计划",
        "",
        f"- 状态：{plan.status}",
        f"- 是否可继续：{'是' if plan.can_continue else '否'}",
        f"- 状态原因：{plan.status_reason}",
        f"- 我理解你想做的是：{summary.understood_goal}",
        f"- 可能实现表面：{summary.likely_surface}",
        "- 推进顺序：",
    ]
    for index, phase in enumerate(plan.phases, start=1):
        lines.extend(
            [
                f"  {index}. {phase.title}",
                f"     - Codex 会做：{phase.codex_action}",
                f"     - 用户会看到：{phase.user_visible_result}",
            ]
        )
    lines.extend(
        [
            "- Codex 可以自动处理：",
            *[f"  - {item}" for item in plan.codex_can_do],
            "- 需要用户确认：",
            *[f"  - {item}" for item in plan.needs_user_confirmation],
            "- 完成后可以这样验收：",
            *[f"  - {item}" for item in plan.acceptance_checks],
            "- 风险说明：",
            *[f"  - {item}" for item in plan.risk_notes],
            f"- 给用户的下一句话：{plan.next_user_message}",
        ]
    )
    return "\n".join(lines)


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
    plan = build_execution_plan(args)
    if args.format == "json":
        print(render_json(plan))
    elif args.format == "user":
        print(render_user(plan))
    else:
        print(render_markdown(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
