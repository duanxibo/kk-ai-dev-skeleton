#!/usr/bin/env python3
"""Recommend a safe first approach for nontechnical users.

This helper is deterministic and read-only. It recognizes phrases such as
"我不懂技术，你帮我选", "不要让我选技术方案", and "你替我决定第一步",
then produces a plain recommendation, tradeoff notes, and the first safe step.
It does not create task evidence, connect to data sources, operate production
systems, touch databases, or run git actions.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass


HIGH_RISK_NON_ACTIONS = [
    "不会连接真实数据或外部数据源。",
    "不会操作生产环境。",
    "不会写入或变更数据库。",
    "不会执行破坏性命令。",
    "不会执行代码提交流程。",
    "不会清理、删除或改写允许入仓的敏感配置。",
]


@dataclass(frozen=True)
class RecommendationResult:
    raw_request: str
    status: str
    recommended_option: str
    recommendation_reason: list[str]
    options_not_chosen_now: list[str]
    first_safe_step: str
    needs_user_confirmation: list[str]
    codex_next_actions: list[str]
    non_actions: list[str]


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def normalize(raw: str) -> str:
    return re.sub(r"\s+", "", raw.strip().lower())


def has_any(text: str, *keywords: str) -> bool:
    normalized = normalize(text)
    return any(normalize(keyword) in normalized for keyword in keywords)


def add_once(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def candidate_options(raw: str) -> list[str]:
    options: list[str] = []
    if has_any(raw, "页面", "可点击", "能点", "看板", "入口", "前端"):
        add_once(options, "先做最小可见页面 / 可点击路径")
    if has_any(raw, "接数据", "真实数据", "数据同步", "数据源", "接口", "后端"):
        add_once(options, "接真实数据 / 补接口")
    if has_any(raw, "导出"):
        add_once(options, "导出能力")
    if has_any(raw, "多人", "团队", "负责人"):
        add_once(options, "多人协作 / 团队状态")
    return options


def recommended_option_for(raw: str, options: list[str]) -> str:
    if has_any(raw, "先做页面", "页面", "可点击", "能点", "看板") or (
        "接真实数据 / 补接口" in options and "导出能力" in options
    ):
        return "先做最小可见页面 / 可点击路径"
    if has_any(raw, "不懂技术", "技术方案", "几种做法", "推荐一个", "替我决定", "选一个"):
        return "先固定目标和验收方式，再做最小可见路径"
    return "先固定目标和验收方式"


def recommendation_reason_for(recommended: str, raw: str) -> list[str]:
    if recommended == "先做最小可见页面 / 可点击路径":
        return [
            "这是非技术用户最容易验收的第一步：先看到入口、操作和结果变化。",
            "它不会一开始就依赖真实数据、数据库、生产环境或导出链路。",
            "页面路径跑通后，再接数据或导出时更容易判断哪里出了问题。",
        ]
    if recommended == "先固定目标和验收方式，再做最小可见路径":
        return [
            "你要求 Codex 替你选方案，所以第一步不应该让你选技术实现。",
            "先固定目标和验收方式，可以避免后面做成了但你不知道是否有用。",
            "随后优先做最小可见路径，让复杂需求先有一个能看、能点、能验收的版本。",
        ]
    return [
        "当前还缺具体业务目标，直接选技术实现容易选错方向。",
        "先固定目标和验收方式，是最小且可逆的安全步骤。",
    ]


def options_not_chosen(recommended: str, options: list[str]) -> list[str]:
    not_chosen: list[str] = []
    for option in options:
        if option != recommended:
            add_once(not_chosen, option)
    if recommended == "先做最小可见页面 / 可点击路径":
        if "接真实数据 / 补接口" not in not_chosen:
            add_once(not_chosen, "接真实数据 / 补接口")
        if "导出能力" not in not_chosen:
            add_once(not_chosen, "导出能力")
    return not_chosen


def first_safe_step_for(recommended: str) -> str:
    if recommended == "先做最小可见页面 / 可点击路径":
        return "先把用户能看到和操作的最小路径做出来，并用假数据或本地样例验证入口、操作和结果变化。"
    if recommended == "先固定目标和验收方式，再做最小可见路径":
        return "先把目标、给谁用、第一眼成功样子和本次不做范围写清楚，再进入最小可见版本。"
    return "先问一个业务结果问题：完成后第一眼看到什么，才算真的可用。"


def confirmations_for(raw: str, recommended: str) -> list[str]:
    confirmations: list[str] = []
    if recommended == "先固定目标和验收方式":
        confirmations.append("还需要你补一句业务目标或成功样子；Codex 不会让你选择技术方案。")
    else:
        confirmations.append("如果要开始实现，需要确认这个推荐方案可以作为当前任务的第一步。")
    if has_any(raw, "真实数据", "接数据", "数据同步", "接口", "后端"):
        confirmations.append("涉及真实数据、接口或后端时，后续需要单独确认数据范围、权限和口径。")
    if has_any(raw, "导出"):
        confirmations.append("导出建议后置；等页面或核心路径可验收后再确认导出格式和范围。")
    return confirmations


def codex_next_actions_for(recommended: str, options: list[str]) -> list[str]:
    actions = [
        "先把你的话转成推荐方案、暂不选择的方案和第一安全步。",
        "不要求你选择技术实现，只让你确认业务结果或权限风险。",
    ]
    if recommended == "先做最小可见页面 / 可点击路径":
        actions.append("把第一步收敛为可见、可点、可验收的路径。")
        actions.append("把真实数据、接口、导出或多人能力放到后续阶段逐项确认。")
    elif recommended == "先固定目标和验收方式，再做最小可见路径":
        actions.append("先补齐目标和验收口径，再进入最小可见版本。")
    if options:
        actions.append("本次识别到的候选方向：" + "、".join(options) + "。")
    return actions


def build_result(args: argparse.Namespace) -> RecommendationResult:
    raw = compact(args.raw)
    options = candidate_options(raw)
    recommended = recommended_option_for(raw, options)
    status = "recommendation-ready" if recommended != "先固定目标和验收方式" else "recommendation-needs-goal"
    return RecommendationResult(
        raw_request=raw,
        status=status,
        recommended_option=recommended,
        recommendation_reason=recommendation_reason_for(recommended, raw),
        options_not_chosen_now=options_not_chosen(recommended, options),
        first_safe_step=first_safe_step_for(recommended),
        needs_user_confirmation=confirmations_for(raw, recommended),
        codex_next_actions=codex_next_actions_for(recommended, options),
        non_actions=HIGH_RISK_NON_ACTIONS,
    )


def fallback(items: list[str], empty_text: str) -> list[str]:
    return items or [empty_text]


def render_user(result: RecommendationResult) -> str:
    lines = [
        "我会先给推荐方案，不让你选技术实现。",
        "",
        "推荐方案：",
        f"- {result.recommended_option}",
        "",
        "为什么推荐：",
        *[f"- {item}" for item in result.recommendation_reason],
        "",
        "暂不选择：",
        *[f"- {item}" for item in fallback(result.options_not_chosen_now, "暂时没有需要排除的候选方案。")],
        "",
        "第一安全步：",
        f"- {result.first_safe_step}",
        "",
        "Codex 的下一步：",
        *[f"- {item}" for item in result.codex_next_actions],
        "",
        "需要你确认：",
        *[f"- {item}" for item in result.needs_user_confirmation],
        "",
        "这次不会做什么：",
        *[f"- {item}" for item in result.non_actions],
    ]
    return "\n".join(lines)


def render_markdown(result: RecommendationResult) -> str:
    lines = [
        "# 非技术方案推荐说明",
        "",
        f"- 用户原话：{result.raw_request}",
        f"- 状态：{result.status}",
        f"- 推荐方案：{result.recommended_option}",
        "- 推荐理由：",
        *[f"  - {item}" for item in result.recommendation_reason],
        "- 暂不选择：",
        *[f"  - {item}" for item in fallback(result.options_not_chosen_now, "无")],
        f"- 第一安全步：{result.first_safe_step}",
        "- 需要用户确认：",
        *[f"  - {item}" for item in result.needs_user_confirmation],
        "- 不会执行：",
        *[f"  - {item}" for item in result.non_actions],
    ]
    return "\n".join(lines)


def render_json(result: RecommendationResult) -> str:
    return json.dumps(asdict(result), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original plain-language request.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = build_result(args)
    if args.format == "json":
        print(render_json(result))
    elif args.format == "user":
        print(render_user(result))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
