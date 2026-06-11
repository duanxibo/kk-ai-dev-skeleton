#!/usr/bin/env python3
"""Build a draft starter package from a nontechnical complex request.

The script is deterministic. By default it only previews the package. Use
--write when Codex intentionally wants to persist draft evidence for follow-up
semantic review. It never connects to data sources, production, DB, or git.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from nontechnical_intake import IntakeSummary, build_summary


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_DIR = REPO_ROOT / ".gstack" / "requirements"
REVIEWS_DIR = REPO_ROOT / ".gstack" / "reviews"
BOUNDARIES_DIR = REPO_ROOT / ".gstack" / "task-boundaries"


@dataclass(frozen=True)
class StarterPaths:
    requirement: Path
    review: Path
    boundary: Path


@dataclass(frozen=True)
class StarterPackage:
    status: str
    status_reason: str
    recommended_lane: str
    can_write: bool
    written: bool
    summary: IntakeSummary
    forbidden_scopes: list[str]
    forbidden_paths: list[str]
    acceptance_checks: list[str]
    paths: dict[str, str]
    next_user_message: str


@dataclass(frozen=True)
class ForbiddenScopeRule:
    label: str
    path: str
    keywords: tuple[str, ...]


DEFAULT_FORBIDDEN_SCOPE_RULES = (
    ForbiddenScopeRule(
        label="受限业务模块",
        path="app/restricted-module/**",
        keywords=("受限业务模块", "受限业务治理", "restricted-module", "restricted module"),
    ),
)


def load_forbidden_scope_rules() -> tuple[ForbiddenScopeRule, ...]:
    config_path = REPO_ROOT / "adapters" / "default" / "forbidden-scopes.json"
    if not config_path.exists():
        return DEFAULT_FORBIDDEN_SCOPE_RULES
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return DEFAULT_FORBIDDEN_SCOPE_RULES

    rules: list[ForbiddenScopeRule] = []
    for item in payload.get("forbidden_scopes", []):
        label = str(item.get("label", "")).strip()
        path = str(item.get("path", "")).strip()
        keywords = tuple(str(keyword).strip() for keyword in item.get("keywords", []) if str(keyword).strip())
        if label and path and keywords:
            rules.append(ForbiddenScopeRule(label=label, path=path, keywords=keywords))
    return tuple(rules) or DEFAULT_FORBIDDEN_SCOPE_RULES


FORBIDDEN_SCOPE_RULES = load_forbidden_scope_rules()


def repo_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def slugify(raw: str) -> str:
    lowered = raw.strip().lower()
    lowered = re.sub(r"[^a-z0-9._\-\s]+", "-", lowered)
    lowered = re.sub(r"[\s_]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-.")
    return (lowered or "nontechnical-task")[:80].strip("-") or "nontechnical-task"


def bullet_lines(items: list[str], *, fallback: str = "待补") -> str:
    values = [item.strip() for item in items if item.strip()]
    if not values:
        values = [fallback]
    return "\n".join(f"- {item}" for item in values)


def indented_bullets(items: list[str], *, fallback: str = "待补") -> str:
    values = [item.strip() for item in items if item.strip()]
    if not values:
        values = [fallback]
    return "\n".join(f"  - {item}" for item in values)


def compact_text(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def text_has(raw: str, *keywords: str) -> bool:
    lowered = raw.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def infer_lane(summary: IntakeSummary) -> str:
    if summary.risks and summary.risk_confirmation_status != "safe-to-draft":
        return "blocked-until-confirmed"
    if summary.risks:
        return "standard-with-risk-controls"
    if not summary.can_continue:
        return "discovery"
    if summary.complexity in {"复杂需求", "高风险复杂需求"}:
        return "standard"
    if summary.complexity == "中等需求":
        return "standard"
    return "fast-lane-candidate"


def build_paths(run_date: str, topic: str) -> StarterPaths:
    slug = slugify(topic)
    return StarterPaths(
        requirement=REQUIREMENTS_DIR / f"{run_date}_{slug}-starter-requirement-draft.md",
        review=REVIEWS_DIR / f"{run_date}_{slug}-starter-review-draft.md",
        boundary=BOUNDARIES_DIR / f"{run_date}_{slug}-starter-boundary-draft.md",
    )


def path_payload(paths: StarterPaths) -> dict[str, str]:
    return {
        "requirement": repo_relative(paths.requirement),
        "review": repo_relative(paths.review),
        "boundary": repo_relative(paths.boundary),
    }


def detect_forbidden_scopes(*texts: str) -> tuple[list[str], list[str]]:
    haystack = " ".join(text for text in texts if text).lower()
    labels: list[str] = []
    paths: list[str] = []
    for rule in FORBIDDEN_SCOPE_RULES:
        if any(keyword.lower() in haystack for keyword in rule.keywords):
            labels.append(rule.label)
            paths.append(rule.path)
    return labels, paths


def build_acceptance_checks(
    args: argparse.Namespace,
    summary: IntakeSummary,
    forbidden_scopes: list[str],
) -> list[str]:
    raw_scope = " ".join(value for value in (args.raw, args.success, args.non_goal) if value)
    checks: list[str] = []

    if args.success:
        checks.append(f"第一眼能看到：{compact_text(args.success)}")
    else:
        checks.append("完成后第一眼看到的结果已经在正式任务范围里写清楚")

    if "用户可见页面能力" in summary.likely_surface:
        checks.append("页面上的关键入口、操作控件、空态和结果变化都能实际看见")
    if text_has(raw_scope, "搜索", "筛选", "排序"):
        checks.append("搜索、筛选或排序操作会真实改变结果，而不是只改变文案")
    if text_has(raw_scope, "导出"):
        checks.append("导出的文件能打开，并且内容对应当前任务约定的范围")
    if "数据查询 / 数据接入" in summary.likely_surface:
        checks.append("数据来源、字段口径、范围、权限和是否真实数据已经说清楚")
    if "后端接口 / 服务能力" in summary.likely_surface:
        checks.append("接口输入、输出、异常情况和复用边界已经说清楚")
    if "脚本 / 命令输出" in summary.likely_surface:
        checks.append("命令可以重复运行，失败时有明确提示和下一步")
    if "文档 / 协作说明" in summary.likely_surface:
        checks.append("文档说明了从哪里开始、下一步做什么、怎么验收")
    if text_has(raw_scope, "多人", "团队", "负责人"):
        checks.append("多人验收或团队状态只按已确认的协作方式展示，不伪装成实时同步")
    if args.non_goal:
        checks.append(f"明确不做的范围保持未触碰：{compact_text(args.non_goal)}")
    for scope in forbidden_scopes:
        checks.append(f"明确禁止的业务范围保持未触碰：{scope}")
    if summary.risks:
        if summary.risk_confirmation_status == "safe-to-draft":
            checks.append("高风险动作没有被执行，只完成了开发起点、任务范围和验收口径整理")
        else:
            checks.append("高风险动作只有在用户确认范围和授权后才允许继续")

    deduped: list[str] = []
    for check in checks:
        if check not in deduped:
            deduped.append(check)
    return deduped[:8]


def requirement_text(args: argparse.Namespace, summary: IntakeSummary, paths: StarterPaths) -> str:
    forbidden_scopes, forbidden_paths = detect_forbidden_scopes(args.raw, args.non_goal)
    acceptance_checks = build_acceptance_checks(args, summary, forbidden_scopes)
    return f"""# {args.title} Starter Requirement Draft

- 需求名称：{args.title}
- 日期：{args.date}
- 当前状态：`draft-needs-codex-review`
- 来源：`nontechnical_task_starter.py`
- 关联 review：`{repo_relative(paths.review)}`
- 关联 boundary：`{repo_relative(paths.boundary)}`
- AI 语义复核：
  `no`

## 用户原话

- {summary.raw_request}

## Codex 初步理解

- {summary.understood_goal}

## 复杂度与推荐推进

- 可能的实现表面：
  `{summary.likely_surface}`
- 判断依据：
  `{summary.surface_reason}`
- 复杂度判断：
  `{summary.complexity}`
- 复杂度依据：
  `{summary.complexity_reason}`
- 推荐推进方式：
  `{summary.recommended_path}`

## 可交付切片

{bullet_lines(summary.delivery_slices)}

## 第一安全步

- {summary.first_safe_step}

## 验收清单

{bullet_lines(acceptance_checks)}

## 风险确认与控制

- 风险确认状态：
  `{summary.risk_confirmation_status}`
- 用户风险确认：
  `{summary.risk_confirmation or "未提供"}`
- 风险控制项：
{indented_bullets(summary.risk_controls or ["无"])}

## 风险与缺口

- 风险：
{indented_bullets(summary.risks or ["未命中真实数据、生产、DB、git 或破坏性操作风险"])}
- 还缺的信息：
{indented_bullets(summary.missing_info or ["没有发现必须先追问的信息"])}
- 推断的禁止业务范围：
{indented_bullets(forbidden_scopes or ["未推断出额外禁止业务范围"])}
- 推断的禁止路径：
{indented_bullets(forbidden_paths or ["未推断出额外禁止路径"])}
- 建议只问这一个问题：
  `{summary.suggested_question}`

## 本 draft 不能直接代表什么

- 不能代表需求已冻结。
- 不能代表 plan review 已通过。
- 不能代表可以直接进入实现。
- Codex 必须继续按 `kk-task-kickoff` 做语义复核、正式 boundary 和 QA plan。
"""


def review_text(args: argparse.Namespace, summary: IntakeSummary, paths: StarterPaths, lane: str) -> str:
    forbidden_scopes, forbidden_paths = detect_forbidden_scopes(args.raw, args.non_goal)
    acceptance_checks = build_acceptance_checks(args, summary, forbidden_scopes)
    return f"""# {args.title} Starter Review Draft

- 主题：{args.title}
- 日期：{args.date}
- Reviewer：Codex
- 来源：`nontechnical_task_starter.py`
- 关联 requirement：`{repo_relative(paths.requirement)}`
- 关联 boundary：`{repo_relative(paths.boundary)}`
- AI 语义复核：
  `no`

## 结论

- 推荐结论：
  `draft-needs-codex-review`
- 建议 Flow Lane：
  `{lane}`
- 是否允许进入实现：
  `否，必须先完成 Codex 语义复核和正式 task kickoff`

## CEO 视角检查

- 用户目标是否已被初步复述：
  `是`
- 是否存在多个实现表面：
  `{ "是" if "多表面" in summary.likely_surface else "否" }`
- 是否有必须先暂停的高风险：
  `{ "是" if summary.risks else "否" }`
- 用户侧下一步：
  `{summary.first_safe_step}`
- 用户侧验收清单：
{indented_bullets(acceptance_checks)}
- 风险确认状态：
  `{summary.risk_confirmation_status}`
- 风险控制项：
{indented_bullets(summary.risk_controls or ["无"])}

## ENG 视角检查

- 实现表面：
  `{summary.likely_surface}`
- 推荐推进方式：
  `{summary.recommended_path}`
- 必须先建立正式 evidence：
  - requirement brief / freeze
  - plan review
  - task boundary
  - Required Gates
  - QA evidence
- 推断的禁止路径：
{indented_bullets(forbidden_paths or ["未推断出额外禁止路径"])}

## 风险与退出条件

- 如涉及真实数据、生产、数据库、破坏性命令或 git workflow action，必须先获得用户明确确认。
- 如涉及业务口径多解，必须先进入 discovery，不得直接实现。
"""


def boundary_text(args: argparse.Namespace, summary: IntakeSummary, paths: StarterPaths, lane: str) -> str:
    forbidden_scopes, forbidden_paths = detect_forbidden_scopes(args.raw, args.non_goal)
    acceptance_checks = build_acceptance_checks(args, summary, forbidden_scopes)
    return f"""# {args.title} Starter Boundary Draft

- Task: {slugify(args.topic)}-starter
- 负责人: Codex
- 日期: {args.date}
- 来源：`nontechnical_task_starter.py`

## Goal

- {summary.understood_goal}

## Draft Status

- Status:
  `draft-needs-codex-review`
- Suggested Lane:
  `{lane}`
- Can Continue:
  `{ "yes" if summary.can_continue else "no" }`
- Continue Reason:
  {summary.continue_reason}

## First Safe Step

- {summary.first_safe_step}

## Delivery Slices

{bullet_lines(summary.delivery_slices)}

## Acceptance Checks

{bullet_lines(acceptance_checks)}

## Risk Confirmation

- Status:
  `{summary.risk_confirmation_status}`
- User Confirmation:
  {summary.risk_confirmation or "未提供"}
- Risk Controls:
{bullet_lines(summary.risk_controls or ["无"])}

## Risks

{bullet_lines(summary.risks or ["未命中真实数据、生产、DB、git 或破坏性操作风险"])}

## Inferred Forbidden Scopes

{bullet_lines(forbidden_scopes or ["未推断出额外禁止业务范围"])}

## Inferred Forbidden Paths

{bullet_lines(forbidden_paths or ["未推断出额外禁止路径"])}

## Forbidden Files

{bullet_lines(forbidden_paths or ["待正式 task kickoff 复核后填写"])}

## Missing Info

{bullet_lines(summary.missing_info or ["没有发现必须先追问的信息"])}

## Suggested User Question

- {summary.suggested_question}

## Mandatory Follow-up Before Implementation

- Codex 必须把本 draft 转成正式 task boundary。
- Codex 必须补齐正式 requirement、review、Required Gates、Subagent Plan 和 QA plan。
- 如果用户确认进入正式开发，正式 boundary 才能成为 active boundary。

## Forbidden Until Confirmed

- 真实数据写入
- 生产环境操作
- DB schema 变更
- 破坏性命令
- git workflow action
- 未经业务确认的产品口径取舍
"""


def ensure_can_write(paths: StarterPaths, *, force: bool) -> None:
    existing = [path for path in (paths.requirement, paths.review, paths.boundary) if path.exists()]
    if existing and not force:
        joined = "\n".join(f"- {repo_relative(path)}" for path in existing)
        raise SystemExit(f"Refusing to overwrite existing files without --force:\n{joined}")


def write_package(args: argparse.Namespace, summary: IntakeSummary, paths: StarterPaths, lane: str) -> None:
    ensure_can_write(paths, force=args.force)
    paths.requirement.parent.mkdir(parents=True, exist_ok=True)
    paths.review.parent.mkdir(parents=True, exist_ok=True)
    paths.boundary.parent.mkdir(parents=True, exist_ok=True)
    paths.requirement.write_text(requirement_text(args, summary, paths), encoding="utf-8")
    paths.review.write_text(review_text(args, summary, paths, lane), encoding="utf-8")
    paths.boundary.write_text(boundary_text(args, summary, paths, lane), encoding="utf-8")


def next_user_message(summary: IntakeSummary, lane: str) -> str:
    if summary.risks and summary.risk_confirmation_status == "safe-to-draft":
        return "我可以先整理开发起点、任务范围和验收口径，但不会执行真实数据、生产、数据库或代码提交流程操作。"
    if summary.risks:
        return f"这件事涉及风险，先不要执行。我需要你确认：{summary.suggested_question}"
    if not summary.can_continue:
        return f"我先不进入实现，还缺一个会影响结果的信息：{summary.suggested_question}"
    if lane == "standard":
        return "我会先把复杂需求拆成正式任务范围和验收口径，再按最小可见路径、数据/接口边界和 QA evidence 分段推进。"
    return "这看起来可以进入小范围任务，但 Codex 仍要先完成正式 task kickoff 和 QA plan。"


def build_package(args: argparse.Namespace) -> StarterPackage:
    summary = build_summary(args)
    lane = infer_lane(summary)
    paths = build_paths(args.date, args.topic or args.raw)
    forbidden_scopes, forbidden_paths = detect_forbidden_scopes(args.raw, args.non_goal)
    acceptance_checks = build_acceptance_checks(args, summary, forbidden_scopes)
    can_write = summary.can_continue
    written = False
    if args.write:
        if not can_write:
            raise SystemExit("Refusing to write draft package: request is risky or missing required clarification.")
        write_package(args, summary, paths, lane)
        written = True
    if can_write and summary.risks:
        status = "ready-to-draft-with-risk-controls"
    elif can_write:
        status = "ready-to-draft"
    else:
        status = "pause-for-risk" if summary.risks else "needs-clarification"
    return StarterPackage(
        status=status,
        status_reason=summary.continue_reason,
        recommended_lane=lane,
        can_write=can_write,
        written=written,
        summary=summary,
        forbidden_scopes=forbidden_scopes,
        forbidden_paths=forbidden_paths,
        acceptance_checks=acceptance_checks,
        paths=path_payload(paths),
        next_user_message=next_user_message(summary, lane),
    )


def render_markdown(package: StarterPackage) -> str:
    summary = package.summary
    lines = [
        "# 非技术复杂需求起始包",
        "",
        f"- 状态：{package.status}",
        f"- 建议推进：{summary.recommended_path}",
        f"- 建议 lane：{package.recommended_lane}",
        f"- 是否可写入草稿：{'是' if package.can_write else '否'}",
        f"- 是否已写入：{'是' if package.written else '否'}",
        f"- 我理解你想要的是：{summary.understood_goal}",
        f"- 可能的实现表面：{summary.likely_surface}",
        f"- 复杂度判断：{summary.complexity}",
        "- 可交付切片：",
        *[f"  - {item}" for item in summary.delivery_slices],
        f"- 第一安全步：{summary.first_safe_step}",
        "- 验收清单：",
        *[f"  - {item}" for item in package.acceptance_checks],
        "- 风险判断：",
        *[f"  - {item}" for item in (summary.risks or ["未命中真实数据、生产、DB、git 或破坏性操作风险"])],
        f"- 风险确认状态：{summary.risk_confirmation_status}",
        f"- 用户风险确认：{summary.risk_confirmation or '未提供'}",
        "- 风险控制项：",
        *[f"  - {item}" for item in (summary.risk_controls or ["无"])],
        "- 推断的禁止业务范围：",
        *[f"  - {item}" for item in (package.forbidden_scopes or ["未推断出额外禁止业务范围"])],
        "- 推断的禁止路径：",
        *[f"  - {item}" for item in (package.forbidden_paths or ["未推断出额外禁止路径"])],
        "- 草稿文件：",
        *[f"  - {key}: `{value}`" for key, value in package.paths.items()],
        f"- 给用户的下一句话：{package.next_user_message}",
    ]
    return "\n".join(lines)


def user_text(value: str) -> str:
    replacements = {
        "先冻结一页需求": "先固定一页需求",
        "冻结需求": "固定需求",
        "冻结": "固定",
        "scope": "范围",
        "QA evidence": "验收记录",
        "git workflow action": "代码提交流程",
        "git 流程": "代码提交流程",
        "git 操作": "代码提交流程",
        "真实数据 / 数据库": "真实数据或数据库",
        "线上 / 生产 / 发布 / 部署": "线上、生产、发布或部署",
    }
    result = value
    for old, new in replacements.items():
        result = result.replace(old, new)
    result = result.replace("写入 验收记录", "写入验收记录")
    result = result.replace("或 代码提交流程", "或代码提交流程")
    result = result.replace("不执行 代码提交流程", "不执行代码提交流程")
    return result


def render_user(package: StarterPackage) -> str:
    summary = package.summary
    forbidden_scope_line = ""
    if package.forbidden_scopes:
        forbidden_scope_line = "我也会避开这些范围：" + "、".join(package.forbidden_scopes) + "。"
    if summary.risks and summary.risk_confirmation_status == "safe-to-draft":
        lines = [
            "我可以先整理开发起点，但不会执行高风险动作。",
            "",
            f"我理解你想做的是：{user_text(summary.understood_goal)}",
            "",
            "我会按你确认的安全范围推进：",
            *[f"- {user_text(item)}" for item in summary.risk_controls],
            "",
            "完成后可以这样验收：",
            *[f"- {user_text(item)}" for item in package.acceptance_checks],
            "",
            "这次只会准备任务范围、开发起点和验收口径，不会操作线上数据、生产环境、数据库、破坏性命令或代码提交流程。",
        ]
        if forbidden_scope_line:
            lines.append(forbidden_scope_line)
        return "\n".join(lines)

    if summary.risks:
        lines = [
            "我先不执行这件事。",
            "",
            f"我理解你想做的是：{user_text(summary.understood_goal)}",
            "",
            "原因是它涉及真实数据、线上环境、数据库或类似高风险操作，需要先确认范围和授权。",
            f"我需要你确认一个问题：{user_text(summary.suggested_question)}",
            "",
            "在确认前，我不会操作线上数据、生产环境、数据库、破坏性命令或代码提交流程。",
        ]
        if forbidden_scope_line:
            lines.append(forbidden_scope_line)
        return "\n".join(lines)

    if not summary.can_continue:
        lines = [
            "我先不进入实现。",
            "",
            f"我理解你想做的是：{user_text(summary.understood_goal)}",
            "",
            "现在还缺一个会影响结果的信息。",
            f"我需要你确认：{user_text(summary.suggested_question)}",
            "",
            "确认后，我会再把它拆成可以验收的几步来推进。",
        ]
        if forbidden_scope_line:
            lines.append(forbidden_scope_line)
        return "\n".join(lines)

    lines = [
        f"我理解你想做的是：{user_text(summary.understood_goal)}",
        "",
        "我会先把它拆成几步来推进：",
        *[f"- {user_text(item)}" for item in summary.delivery_slices],
        "",
        f"第一步我会先做：{user_text(summary.first_safe_step)}",
        "",
        "完成后可以这样验收：",
        *[f"- {user_text(item)}" for item in package.acceptance_checks],
        "",
        "这次我会先准备开发起点和验收口径，不会直接碰真实数据、生产环境、数据库结构、破坏性命令或代码提交流程。",
        "如果后续需要这些高风险动作，我会停下来让你确认。",
    ]
    if forbidden_scope_line:
        lines.append(forbidden_scope_line)
    return "\n".join(lines)


def render_json(package: StarterPackage) -> str:
    payload: dict[str, Any] = asdict(package)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original plain-language request.")
    parser.add_argument("--audience", default="", help="Optional target user or usage context.")
    parser.add_argument("--success", default="", help="Optional visible success criteria.")
    parser.add_argument("--non-goal", default="", help="Optional explicit non-goals or forbidden scope.")
    parser.add_argument("--risk-confirmation", default="", help="Optional user confirmation that constrains high-risk actions.")
    parser.add_argument("--topic", default="", help="Optional filename topic. Defaults to --raw.")
    parser.add_argument("--title", default="", help="Optional human-readable draft title.")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--write", action="store_true", help="Persist draft starter evidence.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing draft starter evidence.")
    parser.add_argument("--dry-run", action="store_true", help="Preview only. Kept for explicit CI readability.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.topic = args.topic or args.raw
    args.title = args.title or "非技术复杂需求起始包"
    if args.dry_run:
        args.write = False
    package = build_package(args)
    if args.format == "json":
        print(render_json(package))
    elif args.format == "user":
        print(render_user(package))
    else:
        print(render_markdown(package))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
