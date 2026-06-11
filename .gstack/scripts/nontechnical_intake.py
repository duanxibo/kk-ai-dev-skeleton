#!/usr/bin/env python3
"""Turn a plain-language request into a nontechnical intake summary.

This helper is deterministic. It does not decide business meaning, create
formal evidence, connect to data sources, or run git actions. Codex uses it as
an internal checklist before the normal kk-task-kickoff flow.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class KeywordRule:
    label: str
    keywords: tuple[str, ...]


@dataclass(frozen=True)
class IntakeSummary:
    raw_request: str
    understood_goal: str
    likely_surface: str
    surface_reason: str
    complexity: str
    complexity_reason: str
    recommended_path: str
    delivery_slices: list[str]
    first_safe_step: str
    risks: list[str]
    risk_confirmation: str
    risk_confirmation_status: str
    risk_controls: list[str]
    missing_info: list[str]
    suggested_question: str
    can_continue: bool
    continue_reason: str
    next_action: str


SURFACE_RULES = (
    KeywordRule("用户可见页面能力", ("页面", "看板", "刷新", "看不到", "筛选", "搜索", "排序", "按钮", "入口", "弹窗", "表格", "导出", "上传", "显示")),
    KeywordRule("数据查询 / 数据接入", ("数据", "同步", "查数", "SQL", "指标", "字段", "口径", "relational database", "analytics warehouse", "BI", "数据源", "真实数据")),
    KeywordRule("后端接口 / 服务能力", ("接口", "API", "后端", "服务", "DTO", "读模型", "持久化", "数据库表")),
    KeywordRule("脚本 / 命令输出", ("脚本", "命令", "CLI", "生成器", "批处理", "自动化")),
    KeywordRule("文档 / 协作说明", ("文档", "说明", "规则", "README", "流程", "模板", "指南")),
)

RISK_RULES = (
    KeywordRule("涉及真实数据，需要确认数据范围和权限", ("真实数据", "线上数据", "生产数据", "同步数据", "用户数据", "手机号", "open_id", "union_id")),
    KeywordRule("涉及生产环境，需要明确授权", ("线上", "生产", "发布", "部署", "prod", "production")),
    KeywordRule("涉及数据库或 schema，需要单独确认", ("数据库", "DB", "schema", "表结构", "migration", "DDL", "写库", "删表", "relational database", "analytics warehouse")),
    KeywordRule("涉及 git 工作流，需要用户明确批准", ("commit", "push", "pull", "merge", "rebase", "PR", "提交", "推送", "合并")),
    KeywordRule("可能是破坏性操作，需要暂停确认", ("删除", "清空", "覆盖", "回滚", "重置", "reset", "drop", "truncate")),
)

RISK_CONTROL_RULES = (
    KeywordRule("只整理需求、开发起点或验收口径，不执行高风险动作", ("只整理", "先整理", "需求", "验收口径", "开发起点", "草稿", "规划")),
    KeywordRule("限制为只读、本地或测试环境", ("只读", "本地", "测试环境", "sandbox", "dry-run", "dry run")),
    KeywordRule("不写入、不修改或不删除真实数据 / 数据库", ("不写", "不改", "不更新", "不删除", "不清空", "不写库", "不改数据库", "不写数据库")),
    KeywordRule("不操作线上 / 生产 / 发布 / 部署", ("不操作线上", "不操作生产", "不发布", "不部署", "不动线上", "不动生产")),
    KeywordRule("不执行 git workflow action", ("不提交", "不推送", "不合并", "不执行 git", "不做 git", "不创建 pr")),
)

BROAD_EXPERIENCE_PATTERNS = (
    "更适合不懂技术的人",
    "AI 开发流程",
    "AI开发流程",
    "更好用",
    "优化流程",
    "复杂需求开发",
    "软件开发骨架",
)

COMPLEX_REQUEST_PATTERNS = (
    "完整",
    "全流程",
    "复杂",
    "多角色",
    "多人",
    "权限",
    "审批",
    "工作流",
    "接入",
    "打通",
    "闭环",
    "数据同步",
    "迁移",
    "发布",
    "线上",
)

SUCCESS_HINTS = ("看到", "显示", "能", "可以", "完成", "通过", "结果", "成功", "验收", "不报错", "可用")
AUDIENCE_HINTS = ("给", "谁用", "用户", "运营", "财务", "审核", "产品", "工程", "不懂技术", "同事", "团队")
NON_GOAL_HINTS = ("不要", "不做", "不改", "别动", "不碰", "排除")


def contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def detect_surface_matches(raw: str) -> list[tuple[str, list[str]]]:
    matches: list[tuple[str, list[str]]] = []
    for rule in SURFACE_RULES:
        matched = [keyword for keyword in rule.keywords if keyword.lower() in raw.lower()]
        if matched:
            matches.append((rule.label, matched))
    return matches


def detect_surface(raw: str) -> tuple[str, str]:
    matches = detect_surface_matches(raw)
    if len(matches) > 1:
        labels = "、".join(label for label, _ in matches)
        matched_keywords = "、".join(keyword for _, keywords in matches for keyword in keywords[:2])
        return f"多表面复杂需求：{labels}", f"命中多类关键词：{matched_keywords}"
    if matches:
        label, matched = matches[0]
        return label, f"命中关键词：{'、'.join(matched[:4])}"
    return "不确定", "没有足够关键词判断是页面、数据、接口、脚本还是文档"


def detect_risks(raw: str) -> list[str]:
    risks: list[str] = []
    for rule in RISK_RULES:
        if contains_any(raw, rule.keywords):
            risks.append(rule.label)
    return risks


def detect_risk_controls(confirmation: str) -> list[str]:
    controls: list[str] = []
    for rule in RISK_CONTROL_RULES:
        if contains_any(confirmation, rule.keywords):
            controls.append(rule.label)
    return controls


def risk_confirmation_status(risks: list[str], confirmation: str, controls: list[str]) -> str:
    if not risks:
        return "not-required"
    if not confirmation:
        return "missing"
    if not controls:
        return "insufficient"
    return "safe-to-draft"


def is_broad_experience(raw: str) -> bool:
    return contains_any(raw, BROAD_EXPERIENCE_PATTERNS)


def detect_complexity(
    raw: str,
    risks: list[str],
    surface_matches: list[tuple[str, list[str]]],
) -> tuple[str, str]:
    signals: list[str] = []
    if len(surface_matches) > 1:
        signals.append("同时涉及多个实现表面")
    if contains_any(raw, COMPLEX_REQUEST_PATTERNS):
        signals.append("包含复杂需求关键词")
    if is_broad_experience(raw) and not surface_matches:
        signals.append("目标是宽泛体验改进")
    if len(raw) >= 80:
        signals.append("原始描述较长")
    if risks:
        signals.append("命中高风险信号")

    if risks and len(signals) >= 2:
        return "高风险复杂需求", "；".join(signals)
    if risks:
        return "高风险需求", "；".join(signals)
    if len(signals) >= 2:
        return "复杂需求", "；".join(signals)
    if signals:
        return "中等需求", "；".join(signals)
    return "小需求", "没有命中复杂度或高风险信号"


def recommend_path(
    complexity: str,
    missing: list[str],
    risks: list[str],
    confirmation_status: str,
) -> str:
    if risks and confirmation_status == "safe-to-draft":
        return "风险受控推进：只整理开发起点、任务范围和验收口径，不执行真实数据、生产、数据库或 git 操作。"
    if risks:
        return "先暂停确认：明确真实数据、生产、数据库、破坏性操作或 git 授权后再继续。"
    if missing:
        return "先发现澄清：补齐会影响产品结果的信息，再进入正式任务。"
    if complexity in {"复杂需求", "高风险复杂需求"}:
        return "标准推进：拆成阶段，先冻结需求和验收口径，再分段实现。"
    if complexity == "中等需求":
        return "小步推进：先做最小可验收切片，再根据结果扩展。"
    return "快速推进：范围明确且风险低，可以进入小范围实现。"


def build_delivery_slices(
    raw: str,
    likely_surface: str,
    risks: list[str],
    confirmation_status: str,
    risk_controls: list[str],
    missing: list[str],
    surface_matches: list[tuple[str, list[str]]],
) -> list[str]:
    slices: list[str] = []
    if risks and confirmation_status == "safe-to-draft":
        slices.append("先把用户确认的安全范围写入任务起点，只整理需求、边界和验收口径。")
        slices.append("在正式实现前再次确认真实数据、生产、数据库和代码提交流程不会被直接操作。")
        if risk_controls:
            slices.append("把风险控制项写入后续任务边界，作为不能越过的限制。")
    elif risks:
        slices.append("先确认风险范围和授权，不能直接操作真实数据、生产、数据库或 git。")
    elif missing:
        slices.append("先补齐目标用户、成功样子、不做范围或实现表面。")
    else:
        slices.append("先冻结一页需求：目标用户、成功样子、不做范围和验收方式。")

    labels = {label for label, _ in surface_matches}
    if "用户可见页面能力" in labels:
        slices.append("先交付最小可见路径：页面入口、关键操作和空态。")
    if "数据查询 / 数据接入" in labels:
        slices.append("再明确数据来源、字段口径、scope、权限和是否只读。")
    if "后端接口 / 服务能力" in labels:
        slices.append("再设计接口输入输出、异常策略和复用边界。")
    if "脚本 / 命令输出" in labels:
        slices.append("再补可重复运行的命令输出和失败提示。")
    if "文档 / 协作说明" in labels:
        slices.append("再同步协作说明和自然语言回归用例。")

    if likely_surface == "不确定":
        slices.append("确认期待看到的是页面变化、数据结果、接口能力、脚本输出还是文档说明。")
    if len(slices) == 1:
        slices.append("实现最小改动，并保留可复现验证命令。")
    slices.append("最后写入 QA evidence，用人话说明怎么验收。")
    return slices[:6]


def first_safe_step(risks: list[str], missing: list[str], question: str, delivery_slices: list[str]) -> str:
    if risks and delivery_slices and "安全范围" in delivery_slices[0]:
        return delivery_slices[0]
    if risks or missing:
        return f"先问用户：{question}"
    return delivery_slices[0]


def missing_info(raw: str, args: argparse.Namespace, likely_surface: str) -> list[str]:
    missing: list[str] = []
    if not args.audience and not contains_any(raw, AUDIENCE_HINTS):
        missing.append("目标用户或使用者不明确")
    if not args.success and not contains_any(raw, SUCCESS_HINTS):
        missing.append("成功后第一眼应该看到什么不明确")
    if not args.non_goal and not contains_any(raw, NON_GOAL_HINTS):
        missing.append("本次明确不做什么不明确")
    if likely_surface == "不确定":
        missing.append("实现表面不明确：页面、数据、接口、脚本还是文档")
    return missing


def suggested_question(raw: str, missing: list[str], risks: list[str], likely_surface: str) -> str:
    if risks:
        return "这会影响真实数据、生产环境、数据库或 git 操作吗？如果会，请先给出范围和授权。"
    if is_broad_experience(raw) and likely_surface not in {"用户可见页面能力", "数据查询 / 数据接入", "后端接口 / 服务能力"}:
        return "你最想先改善哪一段体验：提需求、看进度、验收结果，还是出错后怎么继续？"
    if "成功后第一眼应该看到什么不明确" in missing:
        return "完成后你第一眼希望看到什么，才算这件事真的可用了？"
    if "目标用户或使用者不明确" in missing:
        return "这个能力主要给谁用，在什么场景下用？"
    if "本次明确不做什么不明确" in missing:
        return "这次有哪些页面、数据或流程明确不要碰？"
    if "实现表面不明确：页面、数据、接口、脚本还是文档" in missing:
        return "你期待看到页面变化、数据结果、接口能力、脚本输出，还是文档说明？"
    return "信息已经足够进入下一步，Codex 可以先整理正式任务范围。"


def build_summary(args: argparse.Namespace) -> IntakeSummary:
    raw = compact(args.raw)
    if not raw:
        raise SystemExit("--raw cannot be empty")

    likely_surface, surface_reason = detect_surface(raw)
    risks = detect_risks(raw)
    confirmation = compact(getattr(args, "risk_confirmation", ""))
    risk_controls = detect_risk_controls(confirmation)
    confirmation_status = risk_confirmation_status(risks, confirmation, risk_controls)
    missing = missing_info(raw, args, likely_surface)
    surface_matches = detect_surface_matches(raw)
    complexity, complexity_reason = detect_complexity(raw, risks, surface_matches)
    recommended_path = recommend_path(complexity, missing, risks, confirmation_status)
    delivery_slices = build_delivery_slices(
        raw,
        likely_surface,
        risks,
        confirmation_status,
        risk_controls,
        missing,
        surface_matches,
    )
    question = suggested_question(raw, missing, risks, likely_surface)
    first_step = first_safe_step(risks, missing, question, delivery_slices)
    high_risk = bool(risks)
    broad_needs_question = is_broad_experience(raw) and likely_surface not in {
        "用户可见页面能力",
        "数据查询 / 数据接入",
        "后端接口 / 服务能力",
    }
    risk_allows_draft = high_risk and confirmation_status == "safe-to-draft"
    can_continue = (not high_risk or risk_allows_draft) and not missing and not broad_needs_question

    if high_risk and confirmation_status == "safe-to-draft":
        continue_reason = "高风险信号已被用户安全确认约束住；只能继续整理开发起点、任务范围和验收口径，不能执行真实数据、生产、数据库或 git 操作。"
        next_action = "进入 kk-task-kickoff，生成受控 requirement、review、boundary 和 QA 计划；任何真实数据、生产、DB 或 git 操作仍需另行确认。"
    elif high_risk:
        continue_reason = "存在高风险信号，必须先让用户确认范围和授权。"
        next_action = "暂停自动推进，只问上面的一个风险确认问题。"
    elif can_continue:
        continue_reason = f"目标、成功样子、范围和实现表面足够明确，且未命中高风险信号；推荐路径：{recommended_path}"
        next_action = "进入 kk-task-kickoff，生成正式 requirement、review、boundary 和 QA 计划，并按可交付切片推进。"
    else:
        continue_reason = "还缺少会影响产品结果或风险判断的信息。"
        next_action = "先问上面的一个业务问题，再进入正式任务。"

    goal_parts = [raw]
    if args.audience:
        goal_parts.append(f"给 {compact(args.audience)} 使用")
    if args.success:
        goal_parts.append(f"成功样子：{compact(args.success)}")
    if args.non_goal:
        goal_parts.append(f"本次不做：{compact(args.non_goal)}")

    return IntakeSummary(
        raw_request=raw,
        understood_goal="；".join(goal_parts),
        likely_surface=likely_surface,
        surface_reason=surface_reason,
        complexity=complexity,
        complexity_reason=complexity_reason,
        recommended_path=recommended_path,
        delivery_slices=delivery_slices,
        first_safe_step=first_step,
        risks=risks,
        risk_confirmation=confirmation,
        risk_confirmation_status=confirmation_status,
        risk_controls=risk_controls,
        missing_info=missing,
        suggested_question=question,
        can_continue=can_continue,
        continue_reason=continue_reason,
        next_action=next_action,
    )


def render_markdown(summary: IntakeSummary) -> str:
    risks = summary.risks or ["未命中真实数据、生产、DB、git 或破坏性操作风险"]
    missing = summary.missing_info or ["没有发现必须先追问的信息"]
    can_continue = "可以继续" if summary.can_continue else "先不要继续"
    lines = [
        "# 非技术需求入口摘要",
        "",
        f"- 我理解你想要的是：{summary.understood_goal}",
        f"- 可能的实现表面：{summary.likely_surface}",
        f"- 判断依据：{summary.surface_reason}",
        f"- 复杂度判断：{summary.complexity}",
        f"- 复杂度依据：{summary.complexity_reason}",
        f"- 推荐推进方式：{summary.recommended_path}",
        "- 可交付切片：",
        *[f"  - {item}" for item in summary.delivery_slices],
        f"- 第一安全步：{summary.first_safe_step}",
        "- 风险判断：",
        *[f"  - {item}" for item in risks],
        f"- 风险确认状态：{summary.risk_confirmation_status}",
        f"- 用户风险确认：{summary.risk_confirmation or '未提供'}",
        "- 风险控制项：",
        *[f"  - {item}" for item in (summary.risk_controls or ["无"])],
        "- 还缺的信息：",
        *[f"  - {item}" for item in missing],
        f"- 建议只问这一个问题：{summary.suggested_question}",
        f"- Codex 是否可继续：{can_continue}",
        f"- 原因：{summary.continue_reason}",
        f"- 下一步：{summary.next_action}",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original plain-language request.")
    parser.add_argument("--audience", default="", help="Optional target user or usage context.")
    parser.add_argument("--success", default="", help="Optional visible success criteria.")
    parser.add_argument("--non-goal", default="", help="Optional explicit non-goals or forbidden scope.")
    parser.add_argument("--risk-confirmation", default="", help="Optional user confirmation that constrains high-risk actions.")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    summary = build_summary(args)
    if args.format == "json":
        print(json.dumps(asdict(summary), ensure_ascii=False, indent=2))
    else:
        print(render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
