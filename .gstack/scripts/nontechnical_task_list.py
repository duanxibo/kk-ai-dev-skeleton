#!/usr/bin/env python3
"""Explain task inventory for nontechnical users.

This helper is deterministic and read-only. It reads repo-native task boundary
evidence through gstack_dashboard, then turns "show unfinished tasks" style
prompts into a plain task overview. It does not write shared dashboard/status
files, edit task evidence, connect to services, touch databases, clear allowed
sensitive configuration, or run code workflow actions.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass

from gstack_dashboard import dashboard_payload


@dataclass(frozen=True)
class TaskListItem:
    task: str
    status: str
    progress: str
    next_step: str
    blocked: bool
    active: bool


@dataclass(frozen=True)
class TaskListResult:
    raw_request: str
    status: str
    total_tasks: int
    open_tasks: int
    blocked_tasks: int
    visible_tasks: int
    tasks: list[TaskListItem]
    source_note: str
    codex_next_actions: list[str]
    needs_user_confirmation: list[str]
    non_actions: list[str]


def compact(raw: str) -> str:
    return " ".join(raw.strip().split())


def non_actions() -> list[str]:
    return [
        "不会创建共享任务状态文件。",
        "不会改写任何历史任务记录或任务状态。",
        "不会引入数据库、权限系统或实时多人同步。",
        "不会连接真实数据、生产环境、数据库或外部服务。",
        "不会执行代码提交流程。",
        "不会清理、删除或改写允许入仓的敏感配置。",
    ]


def task_action(item: dict[str, object]) -> str:
    if item.get("blocked"):
        return "先处理卡住原因；如果涉及业务口径、真实数据、生产或权限，再请你确认。"
    next_step = str(item.get("next_step_label") or item.get("current_step") or "下一步")
    return f"继续完成{next_step}。"


def task_status(item: dict[str, object]) -> str:
    if item.get("blocked"):
        return str(item.get("current_step") or "卡住")
    return str(item.get("current_step") or "未知阶段")


def clean_task_name(raw: object) -> str:
    name = str(raw or "未命名任务").strip()
    name = re.sub(r"(?i)^\s*task\s+boundary\s*[:：]\s*", "", name).strip()
    name = re.sub(r"(?i)\s+boundary\s*$", "", name).strip()
    return name or "未命名任务"


def build_item(item: dict[str, object]) -> TaskListItem:
    return TaskListItem(
        task=clean_task_name(item.get("task")),
        status=task_status(item),
        progress=str(item.get("progress") or "0/7"),
        next_step=task_action(item),
        blocked=bool(item.get("blocked")),
        active=bool(item.get("active")),
    )


def build_result(args: argparse.Namespace) -> TaskListResult:
    raw = compact(args.raw)
    limit = max(args.limit, 1)
    query = args.query or ""
    all_payload = dashboard_payload(
        limit=None,
        active_only=False,
        open_only=False,
        blocked_only=False,
        stage="",
        query=query,
        sort="attention",
    )
    open_payload = dashboard_payload(
        limit=limit,
        active_only=False,
        open_only=True,
        blocked_only=False,
        stage="",
        query=query,
        sort="attention",
    )
    blocked_payload = dashboard_payload(
        limit=None,
        active_only=False,
        open_only=True,
        blocked_only=True,
        stage="",
        query=query,
        sort="attention",
    )
    tasks = [build_item(item) for item in open_payload.get("tasks", []) if isinstance(item, dict)]
    open_count = int(open_payload.get("matched_tasks") or 0)
    blocked_count = int(blocked_payload.get("matched_tasks") or 0)
    status = "has-open-tasks" if open_count else "no-open-tasks"
    if query and not open_count:
        status = "no-matching-open-tasks"
    return TaskListResult(
        raw_request=raw,
        status=status,
        total_tasks=int(all_payload.get("total_tasks") or 0),
        open_tasks=open_count,
        blocked_tasks=blocked_count,
        visible_tasks=len(tasks),
        tasks=tasks,
        source_note="这个概览只读取当前本机仓库当前分支已有的任务记录，不代表实时多人同步状态。",
        codex_next_actions=next_actions(status, open_count, blocked_count, query),
        needs_user_confirmation=confirmation(status),
        non_actions=non_actions(),
    )


def next_actions(status: str, open_count: int, blocked_count: int, query: str) -> list[str]:
    if status == "no-matching-open-tasks":
        return [
            f"当前关键词“{query}”没有匹配到未完成任务，可以换一个关键词或查看全部未完成任务。",
            "如果你要继续某一项，告诉我任务名称里的关键词即可。",
        ]
    if status == "no-open-tasks":
        return [
            "当前没有未完成任务；如果你要继续优化骨架，Codex 会开启下一段最小改进并补齐任务记录。",
        ]
    actions = ["优先看当前任务、卡住任务和未完成任务。"]
    if blocked_count:
        actions.append(f"有 {blocked_count} 个任务显示卡住；Codex 会先区分本地可修复问题和需要你确认的问题。")
    if open_count:
        actions.append("如果你要继续其中一项，直接说任务名称里的关键词即可。")
        actions.append("这只是本机当前分支的只读概览，不会改写任务状态。")
    return actions


def confirmation(status: str) -> list[str]:
    if status == "no-matching-open-tasks":
        return ["暂时不需要；如果要缩小范围，可以补一个任务关键词。"]
    return ["暂时不需要；这只是只读任务概览。"]


def render_user(result: TaskListResult) -> str:
    lines = [
        "任务概览：",
        f"- 当前任务记录总数：{result.total_tasks}",
        f"- 未完成任务：{result.open_tasks}",
        f"- 卡住任务：{result.blocked_tasks}",
        f"- 本次先展示：{result.visible_tasks}",
        "",
        result.source_note,
    ]
    if result.tasks:
        lines.extend(["", "优先看的任务："])
        for index, item in enumerate(result.tasks, start=1):
            marker = "当前任务，" if item.active else ""
            blocked = "，卡住" if item.blocked else ""
            lines.append(f"{index}. {item.task}")
            lines.append(f"   - 状态：{marker}{item.status}{blocked}")
            lines.append(f"   - 进度：{item.progress}")
            lines.append(f"   - 建议下一步：{item.next_step}")
    else:
        lines.extend(["", "优先看的任务：", "- 当前没有匹配的未完成任务。"])

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


def render_markdown(result: TaskListResult) -> str:
    lines = [
        "# 非技术任务清单",
        "",
        f"- 状态：{result.status}",
        f"- 当前任务记录总数：{result.total_tasks}",
        f"- 未完成任务：{result.open_tasks}",
        f"- 卡住任务：{result.blocked_tasks}",
        f"- 本次展示：{result.visible_tasks}",
        f"- 来源说明：{result.source_note}",
        "- 任务：",
    ]
    if result.tasks:
        for item in result.tasks:
            lines.append(f"  - {item.task}｜{item.status}｜{item.progress}｜{'卡住' if item.blocked else '正常'}")
    else:
        lines.append("  - 当前没有匹配的未完成任务")
    lines.extend(
        [
            "- Codex 的下一步：",
            *[f"  - {item}" for item in result.codex_next_actions],
            "- 需要用户确认：",
            *[f"  - {item}" for item in result.needs_user_confirmation],
            "- 不执行动作：",
            *[f"  - {item}" for item in result.non_actions],
        ]
    )
    return "\n".join(lines)


def render_json(result: TaskListResult) -> str:
    return json.dumps(asdict(result), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's task-list request.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    parser.add_argument("--limit", type=int, default=5, help="Number of open tasks to show.")
    parser.add_argument("--query", default="", help="Optional task keyword filter.")
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
