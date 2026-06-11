#!/usr/bin/env python3
"""Explain team-state sync limits for nontechnical users.

This helper is deterministic and read-only. It explains what is possible when
a user asks for team task-state sync, especially with a no-database constraint.
It does not create evidence, connect to services, touch databases, modify
restricted-module, clear sensitive configuration, or run git actions.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class TeamSyncPlan:
    raw_request: str
    status: str
    understood_goal: str
    no_database_requested: bool
    forbidden_business_scopes: list[str]
    feasibility_notes: list[str]
    recommended_path: list[str]
    codex_next_actions: list[str]
    needs_user_confirmation: list[str]
    non_actions: list[str]
    next_user_message: str


def compact(raw: str) -> str:
    return " ".join(raw.strip().split())


def has_any(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def no_database_requested(text: str) -> bool:
    return has_any(
        text,
        (
            "不要引入数据库",
            "不引入数据库",
            "不要数据库",
            "不新增数据库",
            "不加数据库",
            "no database",
            "without database",
        ),
    )


def forbidden_scopes(text: str) -> list[str]:
    scopes: list[str] = []
    if has_any(text, ("不要动受限业务模块", "不动受限业务模块", "避开受限业务模块", "不要碰受限业务模块", "restricted-module")):
        scopes.append("受限业务模块")
    return scopes


def build_feasibility(no_db: bool) -> list[str]:
    if no_db:
        return [
            "不引入数据库或共享服务时，不能承诺实时多人同步。",
            "不能承诺权限控制、可靠负责人筛选、跨成员写入或所有人本地状态实时一致。",
            "可行路线是基于仓库里的任务记录生成只读状态视图；团队成员同步代码后重新生成查看。",
        ]
    return [
        "团队实时同步通常需要共享数据库、服务或外部协作系统。",
        "在没有明确授权前，Codex 不会引入数据库、服务、权限系统或跨成员写入。",
        "可先确认是否接受基于仓库任务记录的只读生成视图。",
    ]


def build_recommended_path(no_db: bool, scopes: list[str]) -> list[str]:
    path = [
        "先确认你是否接受“无数据库、基于仓库记录的只读生成视图”。",
        "如果接受，Codex 后续可以只整理当前仓库已有任务记录，并生成团队可查看的状态说明。",
        "如果你需要实时协同、权限、负责人筛选或跨成员写入，就需要另起 discovery / standard 任务定义数据库、服务和权限边界。",
    ]
    if scopes:
        path.append("后续实现或说明都保持避开你禁止的业务范围。")
    return path


def build_codex_actions(no_db: bool, scopes: list[str]) -> list[str]:
    actions = [
        "先把这句话按团队状态同步需求处理，而不是泛化成数据库风险问题。",
        "说明无数据库路线能做什么、不能做什么。",
        "只问一个会影响产品方向的问题：是否接受 repo evidence 只读生成视图。",
    ]
    if no_db:
        actions.append("如果你接受无数据库路线，后续再进入正式任务边界和验收计划。")
    if scopes:
        actions.append("后续会继续避开受限业务模块。")
    return actions


def build_confirmations(no_db: bool) -> list[str]:
    if no_db:
        return ["你是否接受这种无数据库的 repo evidence 只读生成视图？"]
    return ["你是想要无数据库的只读生成视图，还是要进入需要数据库 / 服务 / 权限设计的实时同步方案？"]


def build_non_actions(scopes: list[str]) -> list[str]:
    actions = [
        "不会引入数据库、共享服务、权限系统或实时多人同步实现。",
        "不会直接操作真实数据、生产环境、数据库、外部服务或破坏性命令。",
        "不会执行代码提交流程。",
        "不会清理、删除或改写项目已允许随仓库携带的敏感配置。",
    ]
    if scopes:
        actions.append("不会触碰受限业务模块。")
    return actions


def build_plan(args: argparse.Namespace) -> TeamSyncPlan:
    raw = compact(args.raw)
    no_db = no_database_requested(raw)
    scopes = forbidden_scopes(raw)
    return TeamSyncPlan(
        raw_request=raw,
        status="needs-sync-model-confirmation" if no_db else "needs-sync-scope-confirmation",
        understood_goal="团队任务状态同步",
        no_database_requested=no_db,
        forbidden_business_scopes=scopes,
        feasibility_notes=build_feasibility(no_db),
        recommended_path=build_recommended_path(no_db, scopes),
        codex_next_actions=build_codex_actions(no_db, scopes),
        needs_user_confirmation=build_confirmations(no_db),
        non_actions=build_non_actions(scopes),
        next_user_message="我会先解释团队状态同步的能力边界，再等你确认无数据库路线是否可接受。",
    )


def render_user(plan: TeamSyncPlan) -> str:
    lines = [
        "我先把它当成团队状态同步需求处理。",
        "",
        "关键判断：",
        *[f"- {item}" for item in plan.feasibility_notes],
        "",
        "可行路线：",
        *[f"- {item}" for item in plan.recommended_path],
        "",
        "Codex 的下一步：",
        *[f"- {item}" for item in plan.codex_next_actions],
        "",
        "需要你确认：",
        *[f"- {item}" for item in plan.needs_user_confirmation],
        "",
        "这次不会做什么：",
        *[f"- {item}" for item in plan.non_actions],
    ]
    return "\n".join(lines)


def render_markdown(plan: TeamSyncPlan) -> str:
    lines = [
        "# 非技术团队同步解释",
        "",
        f"- 状态：{plan.status}",
        f"- 理解目标：{plan.understood_goal}",
        f"- 是否要求不引入数据库：{'是' if plan.no_database_requested else '否'}",
        "- 禁止业务范围：",
        *[f"  - {item}" for item in (plan.forbidden_business_scopes or ["未填写"])],
        "- 能力边界：",
        *[f"  - {item}" for item in plan.feasibility_notes],
        "- 可行路线：",
        *[f"  - {item}" for item in plan.recommended_path],
        "- Codex 的下一步：",
        *[f"  - {item}" for item in plan.codex_next_actions],
        "- 需要用户确认：",
        *[f"  - {item}" for item in plan.needs_user_confirmation],
        "- 不执行动作：",
        *[f"  - {item}" for item in plan.non_actions],
    ]
    return "\n".join(lines)


def render_json(plan: TeamSyncPlan) -> str:
    return json.dumps(asdict(plan), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's team-sync request.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    plan = build_plan(args)
    if args.format == "json":
        print(render_json(plan))
    elif args.format == "user":
        print(render_user(plan))
    else:
        print(render_markdown(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
