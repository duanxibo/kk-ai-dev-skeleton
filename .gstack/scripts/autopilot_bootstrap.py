#!/usr/bin/env python3
"""Generate deterministic fast-lane scaffold files for a KK Dev Skeleton task.

The script only writes structure and repeated gate fields. Use --ai-reviewed
only after Codex has read the task context and confirmed the fast-lane claims.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from codex_mode import Mode, current_mode, parse_mode


REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_DIR = REPO_ROOT / ".gstack" / "requirements"
REVIEWS_DIR = REPO_ROOT / ".gstack" / "reviews"
BOUNDARIES_DIR = REPO_ROOT / ".gstack" / "task-boundaries"
LOCAL_POINTER = BOUNDARIES_DIR / "CURRENT.local.md"


@dataclass(frozen=True)
class EvidencePaths:
    requirement: Path
    review: Path
    boundary: Path


def repo_relative(path: Path) -> str:
    return path.relative_to(REPO_ROOT).as_posix()


def slugify(raw: str) -> str:
    lowered = raw.strip().lower()
    lowered = re.sub(r"[^a-z0-9._\-\s]+", "-", lowered)
    lowered = re.sub(r"[\s_]+", "-", lowered)
    lowered = re.sub(r"-+", "-", lowered).strip("-.")
    return (lowered or "fast-lane-task")[:80].strip("-") or "fast-lane-task"


def bullet_lines(items: list[str], *, fallback: str = "待补") -> str:
    values = [item.strip() for item in items if item.strip()]
    if not values:
        values = [fallback]
    return "\n".join(f"- {item}" for item in values)


def indented_bullets(items: list[str], *, fallback: str = "待补", indent: str = "  ") -> str:
    values = [item.strip() for item in items if item.strip()]
    if not values:
        values = [fallback]
    return "\n".join(f"{indent}- {item}" for item in values)


def reviewed_value(args: argparse.Namespace, reviewed: str, draft: str = "待 Codex 语义复核") -> str:
    return reviewed if args.ai_reviewed else draft


def ensure_can_write(paths: EvidencePaths, *, force: bool) -> None:
    existing = [path for path in (paths.requirement, paths.review, paths.boundary) if path.exists()]
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


def requirement_text(args: argparse.Namespace, paths: EvidencePaths, mode: Mode) -> str:
    state = "ready-for-implementation" if args.ai_reviewed else "draft-needs-codex-review"
    freeze_note = (
        "本文件已由 Codex 基于当前上下文复核，可同时作为 fast-lane 的 requirement brief 和 requirement freeze。"
        if args.ai_reviewed
        else "本文件由脚本生成为 draft；Codex 必须补充语义复核后，才能作为 requirement freeze。"
    )
    return f"""# {args.title} Fast-lane Requirement

- 需求名称：{args.title}
- 提出人：{args.requester}
- 日期：{args.date}
- 当前状态：`{state}`
- Flow Lane：`fast-lane`
- 协作模式：`{mode.label}`
- 关联 boundary：`{repo_relative(paths.boundary)}`
- 生成方式：
  `deterministic-scaffold`
- AI 语义复核：
  `{"yes" if args.ai_reviewed else "no"}`

## 需求一句话

- 用户要完成什么：{args.goal}

## 为什么可以走 fast-lane

- 范围小：
  `{reviewed_value(args, "是")}`
- 需求明确：
  `{reviewed_value(args, "是")}`
- 不涉及业务口径多解：
  `{reviewed_value(args, "是")}`
- 不涉及 DB schema、生产操作或 git workflow action：
  `{reviewed_value(args, "是")}`
- 可本地验证：
  `{reviewed_value(args, "是")}`

## 本次必须做

{bullet_lines(args.must)}

## 本次明确不做

{bullet_lines(args.non_goal)}

## 影响面

- 代码 / 文档路径：
{indented_bullets(args.allowed)}
- 数据 / 接口 / 权限：
  `不涉及`
- spec impact：
  `{args.spec_impact}`

## 冻结结论

- {freeze_note}
- 如果后续发现需求有多解、影响面扩大或需要业务口径确认，必须退出 fast-lane，回到 standard / discovery 流程。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Flow Lane`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `{repo_relative(paths.review)}`。
"""


def review_text(args: argparse.Namespace, paths: EvidencePaths, mode: Mode) -> str:
    spec_targets = args.spec_target or ["不适用"]
    no_spec_reason = (
        "本次为小范围改动，不改变产品语义、数据口径、接口、前端、后端或测试口径。"
        if args.spec_impact == "not-required"
        else "见 Expected Spec Targets。"
    )
    review_result = "pass" if args.ai_reviewed else "draft-needs-codex-review"
    implementation_result = "是" if args.ai_reviewed else "否，需 Codex 补充语义复核后再进入实现"
    review_method = (
        "Codex 已读取当前任务上下文并确认 fast-lane 前提成立。"
        if args.ai_reviewed
        else "脚本仅生成 review 骨架；尚未完成 Codex 语义复核。"
    )
    return f"""# {args.title} Fast-lane Review

- 主题：{args.title}
- 日期：{args.date}
- Reviewer：Codex
- Flow Lane：`fast-lane`
- 协作模式：`{mode.label}`
- 关联 requirement：`{repo_relative(paths.requirement)}`
- 关联 boundary：`{repo_relative(paths.boundary)}`
- 生成方式：
  `deterministic-scaffold`
- AI 语义复核：
  `{"yes" if args.ai_reviewed else "no"}`

## 结论

- 推荐结论：
  `{review_result}`
- 是否允许进入实现：
  `{implementation_result}`
- 复核说明：
  {review_method}

## CEO 视角检查

- 用户目标是否明确：
  `{reviewed_value(args, "通过")}`
- 是否有多个合理产品方向需要用户选择：
  `{reviewed_value(args, "否")}`
- 本次是否控制在最小可交付范围：
  `{reviewed_value(args, "通过")}`
- 明确不做：
{indented_bullets(args.non_goal)}

## ENG 视角检查

- 改动路径是否清晰：
  `{reviewed_value(args, "通过")}`
- 是否涉及接口、数据模型、持久化或跨模块契约：
  `{reviewed_value(args, "否")}`
- 是否需要 subagent：
  `{reviewed_value(args, "否，见 Subagent Plan")}`
- 是否需要 goal mode：
  `{reviewed_value(args, "否，见 Autonomy Plan")}`

## Spec Sync Check

- Spec Impact:
  `{args.spec_impact}`
- Expected Spec Targets:
{indented_bullets(spec_targets)}
- If Not Required, Why:
  - {no_spec_reason}

## 验证计划

- 需要运行的测试 / 脚本 / 页面验证：
{indented_bullets(args.verification)}

## 风险与退出条件

- 如果实现中发现范围扩大、业务口径多解、真实数据或接口不确定、生产 / DB / git action 需求，立即退出 fast-lane 并提示用户。
"""


def boundary_text(args: argparse.Namespace, paths: EvidencePaths, mode: Mode) -> str:
    forbidden = args.forbidden or [
        "stack/** 以外的非本任务路径",
        "数据库配置、真实凭证、`.env*`、`.gstack/data-access/*.local.*`",
        "git workflow action，除非用户另行明确批准",
    ]
    allowed = [
        repo_relative(paths.requirement),
        repo_relative(paths.review),
        repo_relative(paths.boundary),
        ".gstack/qa-reports/<pending-qa-report>.md",
        *args.allowed,
    ]
    spec_targets = args.spec_target or ["不适用"]
    no_spec_reason = (
        "本次 fast-lane 小需求不改变 stack domain 产品或工程真源。"
        if args.spec_impact == "not-required"
        else "见 Expected Spec Targets。"
    )
    flow_done_status = "done" if args.ai_reviewed else "pending"
    freeze_status = "done" if args.ai_reviewed else "pending"
    domain_status = (
        "not-required"
        if args.ai_reviewed and args.spec_impact == "not-required"
        else "pending"
    )
    subagent_mode = "not-used" if args.ai_reviewed else "pending-review"
    goal_mode = "not-used" if args.ai_reviewed else "pending-review"
    gate_status = "not-required" if args.ai_reviewed else "pending"
    subagent_gate_status = "done" if args.ai_reviewed else "pending"
    scaffold_reason = (
        "Codex 语义复核后确认 fast-lane 任务范围明确，按当前协作模式自动生成最小 evidence。"
        if args.ai_reviewed
        else "脚本仅生成 deterministic scaffold；需 Codex 语义复核后才能把 review / freeze / gates 标记为完成。"
    )
    return f"""# {args.title} Task Boundary

- Task: {args.title}
- 负责人: Codex
- 日期: {args.date}
- 相关 issue / doc: `{repo_relative(paths.requirement)}`

## Goal

- {args.goal}

## Allowed Files

{bullet_lines(allowed)}

## Forbidden Files

{bullet_lines(forbidden)}

## Functional Non-goals

{bullet_lines(args.non_goal)}

## Decision Mode

- Mode: `{mode.label}`
- Source:
  `{"user-this-task" if args.mode else mode.source}`
- Internal Enum:
  `{mode.enum}`
- Reason:
  {scaffold_reason}

## Flow Lane

- Lane: `fast-lane`
- Reason:
  小需求 / 明确改动，无业务口径多解、生产操作、DB schema 或 git workflow action。
- Evidence Strategy:
  - 使用 fast-lane requirement、fast-lane review、boundary 和 QA evidence。

## Autonomy Plan

- Codex May Do Without Asking:
  - 补齐 fast-lane evidence。
  - 在 Allowed Files 内实现。
  - 运行本地验证和门禁。
- Codex Must Ask Before:
  - 业务口径多解。
  - 触碰 Forbidden Files。
  - 生产操作、DB schema 变更、真实数据写入、破坏性命令或 git workflow action。
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户`
- Goal Mode:
  `{goal_mode}`
  {"fast-lane 小任务默认不启用持续 goal。" if args.ai_reviewed else "待 Codex 复核任务规模后确认是否需要 goal mode。"}
- Local Restart:
  `{args.local_restart}`

## Subagent Plan

- Mode: `{subagent_mode}`
- Reason:
  {"fast-lane 小任务默认由 main agent 直接完成；如实现中范围扩大，再退出 fast-lane 并重新规划。" if args.ai_reviewed else "待 Codex 复核任务规模、写范围和验证面后确认是否使用 subagent。"}
- Main Agent Owns:
  - 流程控制、active boundary、最终集成、最终答复
- Candidate Subagents:
  - name: `not-used`
    role: `reviewer`
    trigger stage: `review`
    write scope: `read-only`
    forbidden paths:
      - `stack/**`
    output evidence: `.gstack/qa-reports/<pending-qa-report>.md`
    status: `not-used`
- Result Integration:
  - 本轮验证结果写入 QA 报告和 final summary。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `{repo_relative(paths.requirement)}`
- plan-ceo-review:
  status: {flow_done_status}
  evidence: `{repo_relative(paths.review)}`
- requirement-freeze:
  status: {freeze_status}
  evidence: `{repo_relative(paths.requirement)}`
  note: fast-lane requirement 同时作为 requirement freeze。
- plan-eng-review:
  status: {flow_done_status}
  evidence: `{repo_relative(paths.review)}`
- domain-spec-readiness:
  status: {domain_status}
  evidence: `{repo_relative(paths.boundary)}`
  note: {no_spec_reason}
- implement:
  status: pending
  evidence: `{repo_relative(paths.boundary)}`
- qa:
  status: pending
  command: qa-only
  evidence: `.gstack/qa-reports/<pending-qa-report>.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "{"AI 已确认 fast-lane 不涉及真实数据、接口、查数或数据源选择；如实现中发现涉及，必须退出 fast-lane 或改为 planned" if args.ai_reviewed else "脚本占位：待 Codex 确认是否涉及真实数据、接口、查数或数据源选择"}"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: {gate_status}
    evidence_path: "{repo_relative(paths.boundary)}"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确本任务不涉及数据源 / 接口 / 查数"
  - gate_id: data-query
    trigger_reason: "{"AI 已确认 fast-lane 不涉及复杂查数或高风险指标" if args.ai_reviewed else "脚本占位：待 Codex 确认是否涉及复杂查数或高风险指标"}"
    owner: kk-data-query
    required_before: plan-eng-review
    status: {gate_status}
    evidence_path: "{repo_relative(paths.boundary)}"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不需要 Query Brief、SQL 或查询 review"
  - gate_id: prototype-logic-extraction
    trigger_reason: "{"AI 已确认 fast-lane 不涉及前端 / 原型业务逻辑迁后端" if args.ai_reviewed else "脚本占位：待 Codex 确认是否涉及前端 / 原型业务逻辑迁后端"}"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: {gate_status}
    evidence_path: "{repo_relative(paths.boundary)}"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确没有前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: {subagent_gate_status}
    evidence_path: "{repo_relative(paths.boundary)}"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；本轮不使用 subagent"
  - gate_id: doc-backfill
    trigger_reason: "{"AI 已确认 fast-lane 不是代码已有但文档缺失的 backfill 场景" if args.ai_reviewed else "脚本占位：待 Codex 确认是否属于 doc-backfill 场景"}"
    owner: kk-doc-backfill
    required_before: review
    status: {gate_status}
    evidence_path: "{repo_relative(paths.boundary)}"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "新增文档同步创建，不需要从代码反推"
  - gate_id: data-knowledge-sync
    trigger_reason: "{"AI 已确认 fast-lane 不新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection" if args.ai_reviewed else "脚本占位：待 Codex 确认是否新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection"}"
    owner: kk-doc-sync
    required_before: review
    status: {gate_status}
    evidence_path: "{repo_relative(paths.boundary)}"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据知识同步"
```

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/workflows/codex-autopilot.md`
- `.gstack/templates/fast-lane-requirement.template.md`
- `.gstack/templates/fast-lane-review.template.md`

## Spec Sync Plan

- Spec Impact:
  `{args.spec_impact}`
- Expected Spec Targets:
{indented_bullets(spec_targets)}
- Prototype Logic Evidence Sync:
  不适用。
- Allowed No-Spec-Change Reason:
  {no_spec_reason}

## Verification

{bullet_lines(args.verification)}

## Lessons To Write Back

- 如发现新坑，写入 `.gstack/knowledge/` 或 `.gstack/rules/`。

## 本地激活

- 自动激活时由 `python3 .gstack/scripts/autopilot_bootstrap.py ... --activate` 写入本机 `CURRENT.local.md`。
"""


def write_files(paths: EvidencePaths, args: argparse.Namespace, mode: Mode) -> None:
    paths.requirement.parent.mkdir(parents=True, exist_ok=True)
    paths.review.parent.mkdir(parents=True, exist_ok=True)
    paths.boundary.parent.mkdir(parents=True, exist_ok=True)
    paths.requirement.write_text(requirement_text(args, paths, mode), encoding="utf-8")
    paths.review.write_text(review_text(args, paths, mode), encoding="utf-8")
    paths.boundary.write_text(boundary_text(args, paths, mode), encoding="utf-8")
    if args.activate:
        LOCAL_POINTER.write_text(active_boundary_text(paths.boundary), encoding="utf-8")


def build_paths(run_date: str, slug: str) -> EvidencePaths:
    return EvidencePaths(
        requirement=REQUIREMENTS_DIR / f"{run_date}_{slug}-fast-lane-requirement.md",
        review=REVIEWS_DIR / f"{run_date}_{slug}-fast-lane-review.md",
        boundary=BOUNDARIES_DIR / f"{run_date}_{slug}.md",
    )


def run_guard(paths: EvidencePaths) -> None:
    result = subprocess.run(
        [sys.executable, ".gstack/scripts/spec_sync_guard.py"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="", file=sys.stderr)
        raise SystemExit(result.returncode)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", required=True, help="Short slug-like topic for filenames.")
    parser.add_argument("--title", help="Human-readable task title. Defaults to --topic.")
    parser.add_argument("--goal", required=True, help="One-sentence task goal.")
    parser.add_argument("--requester", default="用户")
    parser.add_argument("--date", default=date.today().isoformat())
    parser.add_argument("--mode", help="自主执行 / 关键确认 / 手动控制. Defaults to current mode.")
    parser.add_argument("--allowed", action="append", default=[], help="Allowed path. Repeatable.")
    parser.add_argument("--forbidden", action="append", default=[], help="Forbidden path. Repeatable.")
    parser.add_argument("--must", action="append", default=[], help="Must-do item. Repeatable.")
    parser.add_argument("--non-goal", action="append", default=[], help="Non-goal item. Repeatable.")
    parser.add_argument(
        "--verification",
        action="append",
        default=[],
        help="Verification command or check. Repeatable.",
    )
    parser.add_argument(
        "--spec-impact",
        choices=("updated", "not-required", "pending"),
        default="not-required",
    )
    parser.add_argument("--spec-target", action="append", default=[], help="Expected spec target.")
    parser.add_argument(
        "--local-restart",
        choices=("allowed", "not-required", "ask-first"),
        default="not-required",
    )
    parser.add_argument("--activate", action="store_true", help="Set generated boundary active locally.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing generated files.")
    parser.add_argument("--dry-run", action="store_true", help="Print planned files and do not write.")
    parser.add_argument(
        "--ai-reviewed",
        action="store_true",
        help="Mark evidence as reviewed. Use only after Codex has read context and confirmed fast-lane claims.",
    )
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--run-guard", action="store_true", help="Run spec_sync_guard.py after writing.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.title = args.title or args.topic
    slug = slugify(args.topic)
    paths = build_paths(args.date, slug)
    mode = parse_mode(args.mode, source="user-this-task") if args.mode else current_mode()
    ensure_can_write(paths, force=args.force)

    payload = {
        "mode": mode.label,
        "internal_enum": mode.enum,
        "files": {
            "requirement": repo_relative(paths.requirement),
            "review": repo_relative(paths.review),
            "boundary": repo_relative(paths.boundary),
        },
        "activate": args.activate,
        "dry_run": args.dry_run,
        "ai_reviewed": args.ai_reviewed,
    }
    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2) if args.format == "json" else format_summary(payload))
        return 0

    write_files(paths, args, mode)
    if args.run_guard:
        run_guard(paths)
    print(json.dumps(payload, ensure_ascii=False, indent=2) if args.format == "json" else format_summary(payload))
    return 0


def format_summary(payload: dict[str, object]) -> str:
    files = payload["files"]  # type: ignore[assignment]
    assert isinstance(files, dict)
    lines = [
        f"- Mode: `{payload['mode']}`",
        f"- Internal Enum: `{payload['internal_enum']}`",
        f"- Dry Run: `{str(payload['dry_run']).lower()}`",
        f"- Activate: `{str(payload['activate']).lower()}`",
        f"- AI Reviewed: `{str(payload['ai_reviewed']).lower()}`",
        "- Files:",
    ]
    lines.extend(f"  - {key}: `{value}`" for key, value in files.items())
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
