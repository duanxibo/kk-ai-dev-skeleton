#!/usr/bin/env python3
"""Create a formal repo-native kickoff package from a nontechnical request.

This helper bridges the gap between a plain-language complex request and the
normal KK Dev Skeleton evidence flow. It is deterministic and local-only. It never
executes production, DB, real-data, destructive, external-service, or git
workflow actions.

Use --ai-reviewed only after Codex has read the current repo context and
confirmed the intake summary is semantically sound. Without --ai-reviewed the
script can preview the package, but refuses to write formal evidence.
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
from nontechnical_task_starter import (
    build_acceptance_checks,
    detect_forbidden_scopes,
    infer_lane,
    user_text,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_DIR = REPO_ROOT / ".gstack" / "requirements"
REVIEWS_DIR = REPO_ROOT / ".gstack" / "reviews"
BOUNDARIES_DIR = REPO_ROOT / ".gstack" / "task-boundaries"
QA_DIR = REPO_ROOT / ".gstack" / "qa-reports"
LOCAL_POINTER = BOUNDARIES_DIR / "CURRENT.local.md"


@dataclass(frozen=True)
class FormalPaths:
    requirement: Path
    review: Path
    boundary: Path
    qa: Path


@dataclass(frozen=True)
class FormalKickoffPackage:
    status: str
    status_reason: str
    recommended_lane: str
    can_write: bool
    written: bool
    activated: bool
    ai_reviewed: bool
    summary: IntakeSummary
    forbidden_scopes: list[str]
    forbidden_paths: list[str]
    acceptance_checks: list[str]
    paths: dict[str, str]
    next_user_message: str


def repo_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def slugify(raw: str) -> str:
    lowered = raw.strip().lower()
    lowered = re.sub(r"[^a-z0-9._\-\s]+", "-", lowered)
    lowered = re.sub(r"[\s_]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-.")
    return (lowered or "nontechnical-formal-task")[:80].strip("-") or "nontechnical-formal-task"


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


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def build_paths(run_date: str, topic: str) -> FormalPaths:
    slug = slugify(topic)
    return FormalPaths(
        requirement=REQUIREMENTS_DIR / f"{run_date}_{slug}-formal-requirement.md",
        review=REVIEWS_DIR / f"{run_date}_{slug}-formal-review.md",
        boundary=BOUNDARIES_DIR / f"{run_date}_{slug}.md",
        qa=QA_DIR / f"{run_date}_{slug}-qa.md",
    )


def path_payload(paths: FormalPaths) -> dict[str, str]:
    return {
        "requirement": repo_relative(paths.requirement),
        "review": repo_relative(paths.review),
        "boundary": repo_relative(paths.boundary),
        "qa": repo_relative(paths.qa),
    }


def needs_domain_spec(summary: IntakeSummary) -> bool:
    return any(
        label in summary.likely_surface
        for label in ("用户可见页面能力", "数据查询 / 数据接入", "后端接口 / 服务能力")
    )


def needs_data_access(summary: IntakeSummary) -> bool:
    return "数据查询 / 数据接入" in summary.likely_surface or any(
        "真实数据" in risk or "数据库" in risk or "生产" in risk for risk in summary.risks
    )


def normalize_lane(summary: IntakeSummary) -> str:
    lane = infer_lane(summary)
    if lane in {"blocked-until-confirmed", "discovery"}:
        return "discovery"
    if lane in {"standard", "standard-with-risk-controls"}:
        return "standard"
    return "fast-lane"


def review_ready(summary: IntakeSummary) -> bool:
    return not needs_data_access(summary) and not needs_domain_spec(summary)


def status_for(summary: IntakeSummary, ai_reviewed: bool) -> str:
    if summary.risks and summary.risk_confirmation_status != "safe-to-draft":
        return "pause-for-risk"
    if not summary.can_continue:
        return "needs-clarification"
    if not ai_reviewed:
        return "preview-needs-codex-review"
    if summary.risks:
        return "ready-to-write-with-risk-controls"
    return "ready-to-write"


def ensure_can_write(paths: FormalPaths, *, force: bool) -> None:
    existing = [path for path in (paths.requirement, paths.review, paths.boundary, paths.qa) if path.exists()]
    if existing and not force:
        joined = "\n".join(f"- {repo_relative(path)}" for path in existing)
        raise SystemExit(f"Refusing to overwrite existing files without --force:\n{joined}")


def active_boundary_text(boundary: Path) -> str:
    basename = boundary.name
    return "\n".join(
        [
            "# 当前本地 Active Boundary",
            "",
            "这个文件只用于当前机器 / 当前 worktree 的本地 active boundary 指针。",
            "",
            "它已加入 gitignore，不应提交。",
            "",
            "## Active Boundary",
            "",
            f"- [{basename}]({basename})",
            "",
        ]
    )


def requirement_text(
    args: argparse.Namespace,
    summary: IntakeSummary,
    paths: FormalPaths,
    lane: str,
    forbidden_scopes: list[str],
    forbidden_paths: list[str],
    acceptance_checks: list[str],
) -> str:
    return f"""# {args.title} Formal Requirement

- 需求名称：{args.title}
- 日期：{args.date}
- 当前状态：`ready-for-kickoff`
- Flow Lane：`{lane}`
- 来源：`nontechnical_formal_kickoff.py`
- 关联 review：`{repo_relative(paths.review)}`
- 关联 boundary：`{repo_relative(paths.boundary)}`
- AI 语义复核：
  `yes`

## 用户原话

- {summary.raw_request}

## Codex 复核后的理解

- {summary.understood_goal}

## 推荐推进

- 实现表面：
  `{summary.likely_surface}`
- 判断依据：
  `{summary.surface_reason}`
- 复杂度：
  `{summary.complexity}`
- 推荐方式：
  `{summary.recommended_path}`
- 第一安全步：
  {summary.first_safe_step}

## 可交付切片

{bullet_lines(summary.delivery_slices)}

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
{indented_bullets(summary.risks or ["未命中真实数据、生产、DB、代码提交流程或破坏性操作风险"])}
- 还缺的信息：
{indented_bullets(summary.missing_info or ["没有发现必须先追问的信息"])}
- 推断的禁止业务范围：
{indented_bullets(forbidden_scopes or ["未推断出额外禁止业务范围"])}
- 推断的禁止路径：
{indented_bullets(forbidden_paths or ["未推断出额外禁止路径"])}

## 冻结结论

- 本文件已由 Codex 语义复核，可作为正式 kickoff 的 requirement brief / requirement freeze。
- 如果后续发现业务口径多解、数据权限不明、生产 / DB / 代码提交流程需求，必须暂停并回到用户确认。
"""


def review_text(
    args: argparse.Namespace,
    summary: IntakeSummary,
    paths: FormalPaths,
    lane: str,
    acceptance_checks: list[str],
) -> str:
    eng_ready = review_ready(summary)
    implementation_result = "是" if eng_ready else "否，先补专项门禁或 domain readiness"
    return f"""# {args.title} Formal Review

- 主题：{args.title}
- 日期：{args.date}
- Reviewer：Codex
- Flow Lane：`{lane}`
- 来源：`nontechnical_formal_kickoff.py`
- 关联 requirement：`{repo_relative(paths.requirement)}`
- 关联 boundary：`{repo_relative(paths.boundary)}`
- AI 语义复核：
  `yes`

## 结论

- 推荐结论：
  `pass-for-kickoff`
- 是否允许激活 boundary：
  `是`
- 是否允许直接进入实现：
  `{implementation_result}`

## CEO 视角检查

- 用户目标是否明确：
  `通过`
- 成功样子是否可验收：
  `通过`
- 是否存在高风险动作：
  `{ "是，已限制为只整理开工包" if summary.risks else "否" }`
- 用户侧验收清单：
{indented_bullets(acceptance_checks)}

## ENG 视角检查

- 实现表面：
  `{summary.likely_surface}`
- 推荐推进：
  `{summary.recommended_path}`
- 是否需要 data-access gate：
  `{ "是" if needs_data_access(summary) else "否" }`
- 是否需要后续 domain spec readiness：
  `{ "是" if needs_domain_spec(summary) else "否" }`
- 直接实现限制：
  未完成后续门禁前，不得操作真实数据、生产、数据库、破坏性命令或代码提交流程。

## Spec Sync Check

- Spec Impact:
  `pending`
- Expected Spec Targets:
  - 当前任务归属的 `docs/specs/<module>/` 或 `.gstack/knowledge/` 协作真源
- If Not Required, Why:
  - 只有确认不改变产品语义、接口、数据、前端或后端行为时，后续 boundary 才能改为 `not-required`。

## 验证计划

- 当前阶段验证：
  - 检查正式 requirement / review / boundary 已生成。
  - 检查 high-risk 动作未被授权执行。
  - 检查用户验收清单已保留。
- 实现阶段验证：
  - 由后续 active boundary 根据具体页面、接口、数据或脚本补充。
"""


def required_gates_text(summary: IntakeSummary, paths: FormalPaths) -> str:
    data_status = "planned" if needs_data_access(summary) else "not-required"
    data_reason = (
        "需求涉及数据、真实数据、生产或数据库风险；正式实现前必须进入 data-access gate。"
        if data_status == "planned"
        else "本次开工包未命中数据源、接口或查数触发条件。"
    )
    data_query_status = "planned" if "SQL" in summary.raw_request or "查数" in summary.raw_request else "not-required"
    plan_block = "需要在实现前补齐专项门禁" if data_status == "planned" else ""
    return f"""```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "{data_reason}"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: {data_status}
    evidence_path: "{repo_relative(paths.boundary)}"
    evidence_section: "Required Gates"
    blocking_reason: "{plan_block}"
    done_criteria: "明确数据意图、数据源、scope、接口输入输出和只读 / 写入边界"
  - gate_id: data-query
    trigger_reason: "仅在需要 SQL、查数或指标验证时触发"
    owner: kk-data-query
    required_before: plan-eng-review
    status: {data_query_status}
    evidence_path: "{repo_relative(paths.boundary)}"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "需要查数时已有 Query Brief、只读 SQL 草案和 review"
  - gate_id: prototype-logic-extraction
    trigger_reason: "当前只是 kickoff 包；若后续后端承接页面 / 原型 / mock 逻辑， successor boundary 必须改为 planned"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: "{repo_relative(paths.boundary)}"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "本阶段没有后端承接前端 / 原型逻辑"
  - gate_id: data-knowledge-sync
    trigger_reason: "当前只是 kickoff 包；未新增后端 API、DTO、migration、表、读模型或 projection"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: "{repo_relative(paths.boundary)}"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "本阶段没有新增数据知识需要同步"
```"""


def boundary_text(
    args: argparse.Namespace,
    summary: IntakeSummary,
    paths: FormalPaths,
    lane: str,
    forbidden_paths: list[str],
    acceptance_checks: list[str],
) -> str:
    eng_ready = review_ready(summary)
    plan_eng_status = "done" if eng_ready else "pending"
    domain_status = "done" if eng_ready else "pending"
    plan_note = (
        "本任务不涉及数据、接口、页面或后端 domain readiness。"
        if eng_ready
        else "正式实现前必须补齐专项门禁和对应 domain spec readiness。"
    )
    forbidden = [
        *forbidden_paths,
        "真实数据写入",
        "生产环境操作",
        "DB schema 变更",
        "破坏性命令",
        "git workflow action，除非用户另行明确批准",
    ]
    return f"""# {args.title} Task Boundary

- Task: {slugify(args.topic or args.raw)}
- 负责人: Codex
- 日期: {args.date}
- 来源：`nontechnical_formal_kickoff.py`
- 相关 issue / doc:
  - `{repo_relative(paths.requirement)}`
  - `{repo_relative(paths.review)}`

## Goal

- {summary.understood_goal}

## Allowed Files

- `{repo_relative(paths.requirement)}`
- `{repo_relative(paths.review)}`
- `{repo_relative(paths.boundary)}`
- `{repo_relative(paths.qa)}`
- 待后续 plan-eng-review 明确的实现路径

## Forbidden Files

{bullet_lines(forbidden)}

## Functional Non-goals

- 不执行真实数据、生产、数据库、破坏性命令或代码提交流程动作。
- 不在未完成专项门禁前进入正式实现。
- 不把 kickoff 包误称为业务功能已完成。

## User-visible Acceptance

- User-visible Change:
  `yes`
- Expected Visible Behavior:
{indented_bullets(acceptance_checks)}
- User Actions To Verify:
  - 用户能看到 Codex 已把目标、分段推进、风险和验收方式整理成正式开工包。
- Required Evidence:
  - `{repo_relative(paths.qa)}`

## Generated Artifact Policy

- Surface Type:
  `repo-native-kickoff-package`
- Acceptance URL:
  `不适用`
- Refresh / Regeneration:
  `重新运行 nontechnical_formal_kickoff.py，并由 Codex 转述结果。`
- If No Visible Change:
  本阶段不是页面实现；验收看 requirement、review、boundary、QA evidence 和后续任务状态说明。
- Required Interaction Evidence:
  `不适用`

## Decision Mode

- Mode: `自主执行`
- Source:
  `repo-default`
- Internal Enum:
  `codex-led`
- Reason:
  Codex 已复核用户自然语言输入，且本阶段只生成 repo-native 开工包。

## Flow Lane

- Lane: `{lane}`
- Reason:
  {summary.recommended_path}

## Autonomy Plan

- Codex May Do Without Asking:
  - 继续补齐本 kickoff 包的本地 evidence。
  - 运行本地验证、guard 和自然语言 smoke。
- Codex Must Ask Before:
  - 业务口径多解。
  - 真实数据、生产、数据库、破坏性命令或代码提交流程动作。
  - 扩大到未声明的业务路径。
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户。`
- Goal Mode:
  `enabled`
  该 boundary 可作为持续目标下的一段正式推进入口。
- Local Restart:
  `not-required`

## Subagent Plan

- Mode: `not-used`
- Reason:
  kickoff 包生成阶段由主 agent 直接完成；后续实现阶段如范围较大，再用 kk-subagent-orchestrator 拆分。
- Main Agent Owns:
  - requirement、review、boundary、QA evidence、后续门禁收口
- Candidate Subagents:
  - name: `not-used`
    role: `reviewer`
    trigger stage: `review`
    write scope: `read-only`
    forbidden paths:
      - `stack/**`
    output evidence: `{repo_relative(paths.qa)}`
    status: `not-used`

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `{repo_relative(paths.requirement)}`
- plan-ceo-review:
  status: done
  evidence: `{repo_relative(paths.review)}`
- requirement-freeze:
  status: done
  evidence: `{repo_relative(paths.requirement)}`
  note: Codex 已语义复核用户目标、验收清单和不做范围。
- plan-eng-review:
  status: {plan_eng_status}
  evidence: `{repo_relative(paths.review)}`
  note: {plan_note}
- domain-spec-readiness:
  status: {domain_status}
  evidence: `{repo_relative(paths.review)}`
  note: {plan_note}
- implement:
  status: pending
  evidence: `{repo_relative(paths.boundary)}`
- qa:
  status: pending
  command: qa-only
  evidence: `{repo_relative(paths.qa)}`

## Required Gates

{required_gates_text(summary, paths)}

## Verification

- `python3 .gstack/scripts/gstack_dashboard.py explain`
- `python3 .gstack/scripts/gstack_dashboard.py verify`
- 后续实现阶段按具体表面补充页面、接口、数据或脚本验证。

## Lessons To Write Back

- pending

## Spec Sync Plan

- Spec Impact:
  `pending`
- Expected Spec Targets:
  - 当前任务归属的 `docs/specs/<module>/` 或 `.gstack/knowledge/` 协作真源
- If Not Required, Why:
  `后续 plan-eng-review 确认不改变产品、接口、数据、前端或后端语义时才能改为 not-required。`
"""


def qa_text(args: argparse.Namespace, package: FormalKickoffPackage) -> str:
    return f"""# {args.title} Kickoff QA

- 日期: {args.date}
- 结论: pending

## 当前阶段

- 已生成正式 kickoff package。
- 下一步需要按 active boundary 补齐后续 plan-eng-review、domain-spec-readiness、实现和 QA。

## 初始验收清单

{bullet_lines(package.acceptance_checks)}

## 风险

- 真实数据、生产、数据库、破坏性命令和代码提交流程仍未授权执行。
- 本 QA 是 kickoff 阶段占位，不代表业务实现已完成。
"""


def write_package(
    args: argparse.Namespace,
    package: FormalKickoffPackage,
    paths: FormalPaths,
    lane: str,
) -> None:
    ensure_can_write(paths, force=args.force)
    paths.requirement.parent.mkdir(parents=True, exist_ok=True)
    paths.review.parent.mkdir(parents=True, exist_ok=True)
    paths.boundary.parent.mkdir(parents=True, exist_ok=True)
    paths.qa.parent.mkdir(parents=True, exist_ok=True)
    summary = package.summary
    paths.requirement.write_text(
        requirement_text(
            args,
            summary,
            paths,
            lane,
            package.forbidden_scopes,
            package.forbidden_paths,
            package.acceptance_checks,
        ),
        encoding="utf-8",
    )
    paths.review.write_text(review_text(args, summary, paths, lane, package.acceptance_checks), encoding="utf-8")
    paths.boundary.write_text(
        boundary_text(args, summary, paths, lane, package.forbidden_paths, package.acceptance_checks),
        encoding="utf-8",
    )
    paths.qa.write_text(qa_text(args, package), encoding="utf-8")
    if args.activate:
        LOCAL_POINTER.write_text(active_boundary_text(paths.boundary), encoding="utf-8")


def next_user_message(summary: IntakeSummary, can_write: bool, ai_reviewed: bool) -> str:
    if summary.risks and summary.risk_confirmation_status != "safe-to-draft":
        return f"我先不生成正式开工包，需要先确认：{summary.suggested_question}"
    if not summary.can_continue:
        return f"我先不生成正式开工包，还需要你确认：{summary.suggested_question}"
    if not ai_reviewed:
        return "我可以先预览正式开工包，但写入前需要 Codex 完成语义复核。"
    if can_write and summary.risks:
        return "我可以生成正式开工包，但只会整理范围和验收口径，不会执行高风险动作。"
    if can_write:
        return "我可以生成正式开工包，并把后续任务边界准备好。"
    return "我会先预览开工包，再决定是否能继续。"


def build_formal_package(args: argparse.Namespace) -> FormalKickoffPackage:
    summary = build_summary(args)
    paths = build_paths(args.date, args.topic or args.raw)
    forbidden_scopes, forbidden_paths = detect_forbidden_scopes(args.raw, args.non_goal)
    acceptance_checks = build_acceptance_checks(args, summary, forbidden_scopes)
    lane = normalize_lane(summary)
    status = status_for(summary, args.ai_reviewed)
    can_write = summary.can_continue and args.ai_reviewed
    if args.write and not can_write:
        raise SystemExit("Refusing to write formal kickoff package: request is risky, incomplete, or not AI-reviewed.")

    package = FormalKickoffPackage(
        status=status,
        status_reason=summary.continue_reason,
        recommended_lane=lane,
        can_write=can_write,
        written=False,
        activated=False,
        ai_reviewed=args.ai_reviewed,
        summary=summary,
        forbidden_scopes=forbidden_scopes,
        forbidden_paths=forbidden_paths,
        acceptance_checks=acceptance_checks,
        paths=path_payload(paths),
        next_user_message=next_user_message(summary, can_write, args.ai_reviewed),
    )
    if args.write:
        write_package(args, package, paths, lane)
        package = FormalKickoffPackage(
            **{
                **asdict(package),
                "summary": summary,
                "written": True,
                "activated": bool(args.activate),
            }
        )
    return package


def render_markdown(package: FormalKickoffPackage) -> str:
    summary = package.summary
    lines = [
        "# 非技术正式开工包",
        "",
        f"- 状态：{package.status}",
        f"- 建议推进：{summary.recommended_path}",
        f"- 建议推进方式：{package.recommended_lane}",
        f"- Codex 语义复核：{'是' if package.ai_reviewed else '否'}",
        f"- 是否可写入正式开工包：{'是' if package.can_write else '否'}",
        f"- 是否已写入：{'是' if package.written else '否'}",
        f"- 是否已激活：{'是' if package.activated else '否'}",
        f"- 我理解你想要的是：{summary.understood_goal}",
        f"- 可能的实现表面：{summary.likely_surface}",
        f"- 第一安全步：{summary.first_safe_step}",
        "- 可交付切片：",
        *[f"  - {item}" for item in summary.delivery_slices],
        "- 完成后可以这样验收：",
        *[f"  - {item}" for item in package.acceptance_checks],
        "- 风险判断：",
        *[f"  - {item}" for item in (summary.risks or ["未命中真实数据、生产、DB、代码提交流程或破坏性操作风险"])],
        "- 正式文件：",
        *[f"  - {key}: `{value}`" for key, value in package.paths.items()],
        f"- 给用户的下一句话：{package.next_user_message}",
    ]
    return "\n".join(lines)


def render_user(package: FormalKickoffPackage) -> str:
    summary = package.summary
    if package.status in {"pause-for-risk", "needs-clarification"}:
        return "\n".join(
            [
                "我先不生成正式开工包。",
                "",
                f"我理解你想做的是：{user_text(summary.understood_goal)}",
                "",
                f"还需要你确认：{user_text(summary.suggested_question)}",
                "",
                "在确认前，我不会操作真实数据、生产环境、数据库、破坏性命令或代码提交流程。",
            ]
        )
    lines = [
        "我可以把这件事整理成正式开工包。" if package.can_write else "我可以先预览正式开工包。",
        "",
        f"我理解你想做的是：{user_text(summary.understood_goal)}",
        "",
        "我会先按这些步骤推进：",
        *[f"- {user_text(item)}" for item in summary.delivery_slices],
        "",
        "完成后可以这样验收：",
        *[f"- {user_text(item)}" for item in package.acceptance_checks],
        "",
        "这一步只整理目标、范围、风险和验收方式，不会直接操作真实数据、生产环境、数据库、破坏性命令或代码提交流程。",
    ]
    if not package.ai_reviewed:
        lines.append("写入正式任务前，Codex 还需要先完成语义复核。")
    return "\n".join(lines)


def render_json(package: FormalKickoffPackage) -> str:
    return json.dumps(asdict(package), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original plain-language request.")
    parser.add_argument("--audience", default="", help="Optional target user or usage context.")
    parser.add_argument("--success", default="", help="Optional visible success criteria.")
    parser.add_argument("--non-goal", default="", help="Optional explicit non-goals or forbidden scope.")
    parser.add_argument("--risk-confirmation", default="", help="Optional user confirmation constraining high-risk actions.")
    parser.add_argument("--topic", default="", help="Filename topic. Defaults to --raw.")
    parser.add_argument("--title", default="", help="Human-readable task title.")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--ai-reviewed", action="store_true", help="Allow formal write after Codex semantic review.")
    parser.add_argument("--write", action="store_true", help="Persist formal requirement/review/boundary/QA evidence.")
    parser.add_argument("--activate", action="store_true", help="Set CURRENT.local.md to the generated boundary when writing.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated evidence.")
    parser.add_argument("--dry-run", action="store_true", help="Preview only; disables --write and --activate.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.topic = args.topic or args.raw
    args.title = args.title or "非技术正式开工包"
    if args.dry_run:
        args.write = False
        args.activate = False
    package = build_formal_package(args)
    if args.format == "json":
        print(render_json(package))
    elif args.format == "user":
        print(render_user(package))
    else:
        print(render_markdown(package))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
