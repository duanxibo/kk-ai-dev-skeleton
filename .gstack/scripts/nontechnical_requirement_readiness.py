#!/usr/bin/env python3
"""Check whether a nontechnical requirement description is ready to start.

This helper is deterministic and read-only. It does not create formal
requirement evidence, inspect code, connect to data sources, touch databases,
operate production systems, or run code workflow actions.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass


NON_ACTIONS = [
    "不会创建正式业务需求或正式任务范围。",
    "不会修改页面、后端、接口或数据模型。",
    "不会连接真实数据或外部数据源。",
    "不会操作生产环境。",
    "不会写入或变更数据库。",
    "不会执行破坏性命令。",
    "不会执行代码提交流程。",
    "不会清理、删除或改写允许入仓的敏感配置。",
]

FIELD_RULES: tuple[tuple[str, str, tuple[str, ...], str], ...] = (
    (
        "audience",
        "谁会用",
        ("谁会用", "使用者", "用户", "运营", "业务", "同事", "团队", "负责人"),
        "补一句主要使用者是谁，以及他们在什么场景下用。",
    ),
    (
        "goal",
        "想完成什么",
        ("想完成", "他们想完成", "我要", "我想", "希望", "目标", "完成", "做一个", "实现"),
        "补一句你希望系统帮用户完成哪件具体工作。",
    ),
    (
        "current_pain",
        "现在的问题",
        ("现在的问题", "当前问题", "痛点", "为什么要改", "不好用", "太慢", "看不懂", "容易错", "人工"),
        "补一句现在为什么要改，哪里慢、乱、看不懂或容易错。",
    ),
    (
        "visible_success",
        "成功后第一眼",
        ("成功后第一眼", "第一眼", "看到", "应该看到", "页面", "结果", "看板", "提示", "按钮"),
        "补一句完成后第一眼应该看到什么。",
    ),
    (
        "user_flow",
        "用户怎么操作",
        ("用户会这样操作", "这样操作", "从哪里", "点", "输入", "选择", "筛选", "搜索", "导出", "打开"),
        "补一句用户会从哪里进入、点什么、输入什么、最后看到什么。",
    ),
    (
        "data_source",
        "数据来源",
        ("数据来源", "数据从哪里", "假数据", "模拟数据", "mock", "表格", "文件", "接口", "现有页面数据", "不接真实数据"),
        "补一句数据从哪里来；如果先不用真实数据，也请明确说先用假数据。",
    ),
    (
        "non_goal",
        "这次不做",
        ("这次不做", "不要碰", "不碰", "不做", "不改", "先不做", "排除", "不接真实数据", "不写数据库", "不发布", "不提交"),
        "补一句这次明确不做或不要碰什么。",
    ),
    (
        "risk_scope",
        "风险或权限",
        ("是否涉及", "线上", "生产", "数据库", "真实数据", "外部服务", "发布", "提交", "不操作线上", "不写数据库", "不发布", "不提交"),
        "补一句是否涉及真实数据、生产、数据库、外部服务、发布或代码提交流程。",
    ),
    (
        "acceptance",
        "怎么验收",
        ("我会这样验收", "怎么验收", "验收", "判断", "算完成", "预期", "符合条件", "能看到"),
        "补一句完成后你会怎样判断它真的好了。",
    ),
)

CRITICAL_FIELDS = ("audience", "goal", "visible_success", "non_goal", "risk_scope", "acceptance")

RISK_KEYWORDS = (
    "真实数据",
    "线上",
    "生产",
    "数据库",
    "外部服务",
    "发布",
    "提交",
    "代码提交流程",
)

SAFE_CONTROL_KEYWORDS = (
    "不接真实数据",
    "不操作真实数据",
    "不操作线上",
    "不碰线上",
    "不碰生产",
    "不写数据库",
    "不改数据库",
    "不发布",
    "不提交",
    "不涉及",
    "暂时都不涉及",
    "只整理需求",
    "只整理验收",
    "只做可点击",
    "先用假数据",
    "数据用假的",
    "假数据",
    "mock",
)


@dataclass(frozen=True)
class FieldCheck:
    key: str
    label: str
    present: bool
    evidence: str
    suggestion: str


@dataclass(frozen=True)
class RequirementReadiness:
    raw_request: str
    status: str
    readiness_label: str
    can_preview_kickoff: bool
    field_checks: list[FieldCheck]
    present_fields: list[str]
    missing_fields: list[str]
    priority_missing: list[str]
    risk_signals: list[str]
    risk_controls: list[str]
    codex_next_actions: list[str]
    needs_user_confirmation: list[str]
    non_actions: list[str]


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def has_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def evidence_for(text: str, keywords: tuple[str, ...]) -> str:
    lowered = text.lower()
    for keyword in keywords:
        if keyword.lower() in lowered:
            return keyword
    return ""


def risk_matches(text: str) -> list[str]:
    lowered = text.lower()
    return [keyword for keyword in RISK_KEYWORDS if keyword.lower() in lowered]


def control_matches(text: str) -> list[str]:
    lowered = text.lower()
    return [keyword for keyword in SAFE_CONTROL_KEYWORDS if keyword.lower() in lowered]


def build_field_checks(raw: str) -> list[FieldCheck]:
    checks: list[FieldCheck] = []
    for key, label, keywords, suggestion in FIELD_RULES:
        evidence = evidence_for(raw, keywords)
        checks.append(
            FieldCheck(
                key=key,
                label=label,
                present=bool(evidence),
                evidence=evidence,
                suggestion=suggestion,
            )
        )
    return checks


def determine_status(
    checks: list[FieldCheck],
    risks: list[str],
    controls: list[str],
) -> tuple[str, str, bool, list[str], list[str]]:
    present_by_key = {check.key: check.present for check in checks}
    missing = [check for check in checks if not check.present]
    missing_critical = [check for check in missing if check.key in CRITICAL_FIELDS]
    priority_missing = missing_critical[:3] or missing[:3]

    if risks and not controls:
        return (
            "pause-for-risk-confirmation",
            "先别开工；需要先确认真实数据、生产、数据库、外部服务、发布或代码提交流程的范围。",
            False,
            [check.label for check in missing],
            [check.suggestion for check in priority_missing],
        )

    if not missing_critical:
        if missing:
            return (
                "almost-ready",
                "核心信息已经够开工预览；再补齐下面信息会让后续更稳。",
                True,
                [check.label for check in missing],
                [check.suggestion for check in priority_missing],
            )
        return (
            "ready-for-kickoff-preview",
            "信息已经足够进入开工预览。",
            True,
            [],
            [],
        )

    if present_by_key.get("goal") and present_by_key.get("visible_success"):
        return (
            "needs-key-info",
            "方向已经能看出来，但还缺开工前必须确认的信息。",
            False,
            [check.label for check in missing],
            [check.suggestion for check in priority_missing],
        )

    return (
        "needs-basic-info",
        "目前还不像一份可开工需求，需要先补基础信息。",
        False,
        [check.label for check in missing],
        [check.suggestion for check in priority_missing],
    )


def next_actions(status: str, can_preview: bool, risks: list[str], controls: list[str]) -> list[str]:
    if status == "pause-for-risk-confirmation":
        return [
            "先只整理需求，不进入实现。",
            "请先确认风险范围：是否允许接触真实数据、生产环境、数据库、外部服务、发布或代码提交流程。",
            "如果只允许先规划，请补一句“只整理需求和验收口径，不操作线上数据、不写数据库、不发布、不提交”。",
        ]
    if can_preview:
        actions = [
            "Codex 可以先把这些信息整理成开工预览。",
            "如果你同意继续，Codex 会再做语义复核、任务边界和验收计划。",
            "如果涉及真实数据、生产、数据库、外部服务或代码提交流程，会先停下来确认。",
        ]
        if controls:
            actions.insert(1, "已看到你写了风险限制；后续会按这些限制推进，不会越过它们。")
        return actions
    return [
        "先补齐下面最关键的缺失信息。",
        "你不需要一次写完整；补 1-3 句最关键内容即可。",
        "补完后 Codex 可以再次检查是否足够进入开工预览。",
    ]


def confirmations(status: str, priority_missing: list[str]) -> list[str]:
    if status == "pause-for-risk-confirmation":
        return ["请确认本次是否只允许先整理需求和验收口径，不操作真实数据、生产、数据库、外部服务、发布或代码提交流程。"]
    if priority_missing:
        return priority_missing
    return ["暂时不需要；这份描述已经可以先进入开工预览。"]


def build_readiness(args: argparse.Namespace) -> RequirementReadiness:
    raw = compact(args.raw)
    checks = build_field_checks(raw)
    risks = risk_matches(raw)
    controls = control_matches(raw)
    status, label, can_preview, missing, priority_missing = determine_status(checks, risks, controls)
    return RequirementReadiness(
        raw_request=raw,
        status=status,
        readiness_label=label,
        can_preview_kickoff=can_preview,
        field_checks=checks,
        present_fields=[check.label for check in checks if check.present],
        missing_fields=missing,
        priority_missing=priority_missing,
        risk_signals=risks,
        risk_controls=controls,
        codex_next_actions=next_actions(status, can_preview, risks, controls),
        needs_user_confirmation=confirmations(status, priority_missing),
        non_actions=NON_ACTIONS,
    )


def render_user(readiness: RequirementReadiness) -> str:
    present = readiness.present_fields or ["暂时还没有看到足够明确的需求字段。"]
    missing = readiness.priority_missing or ["没有必须补充的关键信息。"]
    risks = readiness.risk_signals or ["暂时没有看到必须暂停的高风险信号。"]
    controls = readiness.risk_controls or ["暂时没有看到明确的风险限制；如果涉及高风险动作，需要补充限制。"]
    lines = [
        "我先帮你做需求完整度检查。",
        "",
        f"整体判断：{readiness.readiness_label}",
        "",
        "已经说清楚：",
        *[f"- {item}" for item in present],
        "",
        "还需要补充：",
        *[f"- {item}" for item in missing],
        "",
        "风险确认：",
        *[f"- {item}" for item in risks],
        "",
        "已看到的风险限制：",
        *[f"- {item}" for item in controls],
        "",
        "Codex 的下一步：",
        *[f"- {item}" for item in readiness.codex_next_actions],
        "",
        "需要你确认：",
        *[f"- {item}" for item in readiness.needs_user_confirmation],
        "",
        "这次不会做什么：",
        *[f"- {item}" for item in readiness.non_actions],
    ]
    return "\n".join(lines)


def render_markdown(readiness: RequirementReadiness) -> str:
    lines = [
        "# 非技术需求完整度检查",
        "",
        f"- 用户原话：{readiness.raw_request}",
        f"- 状态：{readiness.status}",
        f"- 判断：{readiness.readiness_label}",
        f"- 是否可进入开工预览：{'是' if readiness.can_preview_kickoff else '否'}",
        "- 字段检查：",
    ]
    for check in readiness.field_checks:
        state = "present" if check.present else "missing"
        lines.append(f"  - {check.label}: {state}; evidence={check.evidence or 'none'}")
    lines.extend(
        [
            "- 优先补充：",
            *[f"  - {item}" for item in (readiness.priority_missing or ["无"])],
            "- 风险信号：",
            *[f"  - {item}" for item in (readiness.risk_signals or ["无"])],
            "- 风险限制：",
            *[f"  - {item}" for item in (readiness.risk_controls or ["无"])],
            "- Codex 下一步：",
            *[f"  - {item}" for item in readiness.codex_next_actions],
            "- 需要用户确认：",
            *[f"  - {item}" for item in readiness.needs_user_confirmation],
            "- 不会执行：",
            *[f"  - {item}" for item in readiness.non_actions],
        ]
    )
    return "\n".join(lines)


def render_json(readiness: RequirementReadiness) -> str:
    return json.dumps(asdict(readiness), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's filled or partial requirement description.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    readiness = build_readiness(args)
    if args.format == "json":
        print(render_json(readiness))
    elif args.format == "user":
        print(render_user(readiness))
    else:
        print(render_markdown(readiness))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
