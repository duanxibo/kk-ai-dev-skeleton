#!/usr/bin/env python3
"""Explain natural-language requirement scope changes.

This helper is deterministic and read-only. It recognizes phrases such as
"先不要做导出", "只保留搜索和筛选", "不接真实数据，先做可点击页面",
"先做原型 / demo / 静态页面，不接接口", and "受限业务模块可以动，但不要动数据库",
then produces a plain user-facing scope-change explanation. It does not rewrite
existing task evidence, touch business code, connect to data sources, operate on
production systems, or run git actions.
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
class ScopeChangeResult:
    raw_request: str
    status: str
    change_type: str
    included_now: list[str]
    excluded_now: list[str]
    deferred_later: list[str]
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


def detect_included(raw: str) -> list[str]:
    included: list[str] = []
    if has_any(raw, "搜索"):
        add_once(included, "搜索")
    if has_any(raw, "筛选", "过滤"):
        add_once(included, "筛选")
    if has_any(raw, "原型", "prototype"):
        add_once(included, "原型")
    if has_any(raw, "demo", "演示版本", "演示版"):
        add_once(included, "demo")
    if has_any(raw, "静态页面", "静态页"):
        add_once(included, "静态页面")
    if has_any(raw, "可点击", "能点", "点击页面", "能点的版本", "可点击原型", "能点的 demo", "能点的demo"):
        add_once(included, "可点击页面")
    if has_any(raw, "假数据", "数据先用假的", "数据用假的", "用假数据", "假的数据", "mock", "mock 数据", "模拟数据"):
        add_once(included, "假数据 / mock 数据")
    if has_any(raw, "受限业务模块可以动", "可以动受限业务模块", "受限业务模块能动"):
        add_once(included, "受限业务模块")
    if has_any(raw, "导出") and not has_any(raw, "不要做导出", "先不要做导出", "不做导出", "去掉导出"):
        add_once(included, "导出")
    if has_any(raw, "只保留") and not included:
        add_once(included, "用户明确保留的范围")
    return included


def detect_excluded(raw: str) -> list[str]:
    excluded: list[str] = []
    if has_any(raw, "不要做导出", "先不要做导出", "不做导出", "去掉导出"):
        add_once(excluded, "导出")
    if has_any(raw, "不要动数据库", "不动数据库", "不写数据库", "不引入数据库", "不要数据库"):
        add_once(excluded, "数据库")
    if has_any(raw, "不接真实数据", "暂时不接真实数据", "先不接真实数据", "不接线上数据"):
        add_once(excluded, "真实数据接入")
    if has_any(raw, "假数据", "数据先用假的", "数据用假的", "用假数据", "假的数据", "mock", "mock 数据", "模拟数据"):
        add_once(excluded, "真实数据接入")
    if has_any(raw, "不接接口", "先不接接口", "暂时不接接口", "不连接口", "不调用接口", "不接后端"):
        add_once(excluded, "接口接入")
    if has_any(raw, "不要动受限业务模块", "不动受限业务模块"):
        add_once(excluded, "受限业务模块")
    if has_any(raw, "先不要", "先不做") and not excluded:
        add_once(excluded, "用户明确说先不做的范围")
    return excluded


def detect_deferred(raw: str) -> list[str]:
    deferred: list[str] = []
    if has_any(raw, "后面再接真实数据", "以后再接真实数据", "后续再接真实数据", "之后再接真实数据"):
        add_once(deferred, "真实数据接入")
    if has_any(raw, "后面再接接口", "以后再接接口", "后续再接接口", "之后再接接口"):
        add_once(deferred, "接口接入")
    if has_any(raw, "后面再做导出", "以后再做导出", "后续再做导出"):
        add_once(deferred, "导出")
    return deferred


def change_type_for(raw: str, included: list[str], excluded: list[str], deferred: list[str]) -> str:
    if has_any(raw, "受限业务模块可以动", "可以动受限业务模块", "加上", "新增"):
        return "scope-expansion"
    if has_any(raw, "可点击", "能点", "原型", "prototype", "demo", "静态页面", "静态页", "假数据", "数据用假的", "用假数据", "mock", "模拟数据", "不接接口") or deferred:
        return "prototype-first"
    if excluded and included:
        return "scope-adjustment"
    if excluded:
        return "scope-reduction"
    return "scope-change"


def confirmations_for(change_type: str, included: list[str], excluded: list[str], deferred: list[str]) -> list[str]:
    confirmations: list[str] = []
    if change_type == "scope-expansion":
        confirmations.append("你正在放开或新增范围；实施前需要确认这个新范围确实覆盖当前任务。")
    else:
        confirmations.append("如果要把这次调整写进当前任务记录或开始实现，需要确认用这个新范围覆盖之前的范围。")
    if "受限业务模块" in included:
        confirmations.append("受限业务模块属于独立业务范围；真正实施前需要确认本轮允许触碰它。")
    if "真实数据接入" in excluded or "真实数据接入" in deferred:
        confirmations.append("真实数据接入会留到后续任务；本轮只按不接真实数据处理。")
    if "数据库" in excluded:
        confirmations.append("数据库保持禁止范围；本轮不会写库、改表或引入数据库。")
    return confirmations


def next_actions_for(change_type: str, included: list[str], excluded: list[str], deferred: list[str]) -> list[str]:
    actions = ["先把这次范围调整转成清晰的保留范围、排除范围和后续范围。"]
    if included:
        actions.append("把本轮要做的内容收敛到：" + "、".join(included) + "。")
    if excluded:
        actions.append("把本轮先不做的内容标清楚：" + "、".join(excluded) + "。")
    if deferred:
        actions.append("把后续再做的内容单独列出：" + "、".join(deferred) + "。")
    if change_type == "prototype-first":
        actions.append("按可点击 / mock 数据版本理解，不把它当成真实数据接入任务。")
        if any(item in included for item in ("原型", "demo", "静态页面")) or "接口接入" in excluded:
            actions.append("把原型 / demo / 静态页面当作先看效果的版本，不把它当成接口接入任务。")
    return actions


def build_result(args: argparse.Namespace) -> ScopeChangeResult:
    raw = compact(args.raw)
    included = detect_included(raw)
    excluded = detect_excluded(raw)
    deferred = detect_deferred(raw)
    change_type = change_type_for(raw, included, excluded, deferred)
    status = "scope-change-ready" if included or excluded or deferred else "scope-change-needs-detail"

    return ScopeChangeResult(
        raw_request=raw,
        status=status,
        change_type=change_type,
        included_now=included,
        excluded_now=excluded,
        deferred_later=deferred,
        needs_user_confirmation=confirmations_for(change_type, included, excluded, deferred),
        codex_next_actions=next_actions_for(change_type, included, excluded, deferred),
        non_actions=HIGH_RISK_NON_ACTIONS,
    )


def fallback(items: list[str], empty_text: str) -> list[str]:
    return items or [empty_text]


def render_user(result: ScopeChangeResult) -> str:
    lines = [
        "我会按需求范围调整处理。",
        "",
        "这次先做 / 保留：",
        *[f"- {item}" for item in fallback(result.included_now, "还需要从你的话里确认具体保留范围。")],
        "",
        "这次先不做 / 排除：",
        *[f"- {item}" for item in fallback(result.excluded_now, "没有识别到明确排除范围。")],
    ]
    if result.deferred_later:
        lines.extend(["", "后续再做：", *[f"- {item}" for item in result.deferred_later]])
    lines.extend(
        [
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
    )
    return "\n".join(lines)


def render_markdown(result: ScopeChangeResult) -> str:
    lines = [
        "# 非技术需求范围调整说明",
        "",
        f"- 用户原话：{result.raw_request}",
        f"- 状态：{result.status}",
        f"- 调整类型：{result.change_type}",
        "- 本轮保留：",
        *[f"  - {item}" for item in fallback(result.included_now, "未识别")],
        "- 本轮排除：",
        *[f"  - {item}" for item in fallback(result.excluded_now, "未识别")],
        "- 后续再做：",
        *[f"  - {item}" for item in fallback(result.deferred_later, "未识别")],
        "- 需要用户确认：",
        *[f"  - {item}" for item in result.needs_user_confirmation],
        "- 不会执行：",
        *[f"  - {item}" for item in result.non_actions],
    ]
    return "\n".join(lines)


def render_json(result: ScopeChangeResult) -> str:
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
