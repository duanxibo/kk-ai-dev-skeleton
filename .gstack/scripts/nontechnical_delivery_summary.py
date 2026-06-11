#!/usr/bin/env python3
"""Generate a shareable delivery summary for nontechnical users.

This helper is deterministic and read-only. It summarizes the current active
task or a queried task from repo-native evidence, then renders a plain-language
completion note suitable for a team update. It does not create evidence, connect
to services, touch databases, clean sensitive configuration, or run git actions.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass

from gstack_dashboard import (
    REPO_ROOT,
    dashboard_payload,
    parse_section_field_items,
    read_text,
    status_label,
)


@dataclass(frozen=True)
class DeliverySummary:
    raw_request: str
    status: str
    status_reason: str
    task: str
    task_done: bool
    progress: str
    current_stage: str
    changed_items: list[str]
    acceptance_actions: list[str]
    expected_results: list[str]
    verification_status: str
    risks_and_non_actions: list[str]
    needs_user_confirmation: list[str]
    non_actions: list[str]
    next_user_message: str


def compact(raw: str) -> str:
    return " ".join(raw.strip().split())


def section_lines(text: str, header: str) -> list[str]:
    lines = text.splitlines()
    result: list[str] = []
    in_section = False
    for line in lines:
        if line.strip() == f"## {header}":
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            result.append(line.rstrip())
    return result


def clean_item(raw: str) -> str:
    cleaned = raw.strip().strip("- ").strip().strip('"').strip("'")
    if cleaned.startswith("`") and cleaned.endswith("`"):
        cleaned = cleaned[1:-1]
    return cleaned.strip()


def section_bullets(text: str, header: str) -> list[str]:
    items: list[str] = []
    for line in section_lines(text, header):
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue
        item = clean_item(stripped[2:])
        if item:
            items.append(item)
    return items


def looks_internal_path(text: str) -> bool:
    internal_tokens = (
        ".gstack/",
        "stack/",
        "archive/",
        "shared/",
        "blueprint/",
        ".github/",
        ".gitignore",
        "CURRENT.local.md",
        ".env",
    )
    if any(token in text for token in internal_tokens):
        return True
    return bool(
        re.search(
            r"(^|\s)(\.gstack/|stack/|archive/|shared/|blueprint/|\.github/|CURRENT\.local\.md)",
            text,
        )
        or "/**" in text
    )


def humanize_internal_detail(text: str) -> str:
    if any(token in text for token in ("python3", "bash ", "scripts/", ".py", ".sh", "--")):
        return "按项目说明运行初始化和自检命令。"
    if any(
        token in text
        for token in ("adapter runtime", "runtime.json", "adapter.md", "README", "doctor", "default adapter")
    ):
        return "团队可以按项目说明创建项目适配配置，并完成自检。"
    if "kk-task-kickoff" in text or "kk-data" in text:
        return "核心工作流要求读取的文件已经补齐。"
    if "core / adapter / runtime" in text:
        return "框架核心、项目适配和后续产品化边界已经说清楚。"
    if "不真正修改已有业务任务" in text and any(word in text for word in ("requirement", "boundary", "scope")):
        return "不会真正改写已有业务任务的目标、范围或实现。"
    if any(word in text for word in ("boundary", "gate", "spec", "raw JSON", "JSON", "lane", "内部 check id")):
        if "不暴露" in text or "不展示" in text:
            return "输出保持人话，不展示内部工程细节。"
        replacements = {
            "requirement": "需求记录",
            "boundary": "任务范围记录",
            "scope": "范围",
            "gate": "内部检查",
            "spec": "规格说明",
            "raw JSON": "内部数据",
            "JSON": "内部数据",
            "lane": "推进方式",
            "内部 check id": "内部检查编号",
        }
        result = text
        for old, new in replacements.items():
            result = result.replace(old, new)
        return result
    if any(word in text for word in ("GitHub API", "commit", "push", "merge", "pull", "rebase", "reset", "git workflow action", "git")):
        return "不会执行代码提交流程。"
    return text


def user_safe_items(items: list[str], fallback: str, *, limit: int = 5) -> list[str]:
    safe: list[str] = []
    for item in items:
        cleaned = clean_item(item)
        if not cleaned or looks_internal_path(cleaned):
            continue
        cleaned = humanize_internal_detail(cleaned)
        cleaned = cleaned.replace("git workflow action", "代码提交流程")
        cleaned = cleaned.replace("git", "代码提交流程")
        cleaned = cleaned.replace("DB", "数据库")
        cleaned = cleaned.replace("CLI", "命令行工具")
        cleaned = cleaned.replace("package manager", "包管理器")
        cleaned = cleaned.replace("repo-native evidence", "任务记录")
        cleaned = cleaned.replace("repo evidence", "任务记录")
        if cleaned not in safe:
            safe.append(cleaned)
        if len(safe) >= limit:
            break
    return safe or [fallback]


def standard_non_actions() -> list[str]:
    return [
        "不会直接操作真实数据、生产环境、数据库、外部服务或破坏性命令。",
        "不会执行代码提交流程。",
        "不会清理、删除或改写项目已允许随仓库携带的敏感配置。",
    ]


def dashboard_for(args: argparse.Namespace) -> dict[str, object]:
    if args.query:
        return dashboard_payload(
            limit=1,
            active_only=False,
            open_only=False,
            blocked_only=False,
            stage="",
            query=args.query,
            sort="attention",
        )
    return dashboard_payload(
        limit=1,
        active_only=True,
        open_only=False,
        blocked_only=False,
        stage="",
        query="",
        sort="attention",
    )


def qa_line(item: dict[str, object]) -> str:
    qa_status = str(item.get("qa_status") or "missing")
    if qa_status == "done":
        return "验收记录已完成。"
    if qa_status in {"planned", "pending", "missing"}:
        return "验收记录还没完成，这份说明只能作为当前进展总结。"
    return f"验收记录状态是{status_label(qa_status)}。"


def build_no_task_summary(raw: str, query: str) -> DeliverySummary:
    reason = "没有找到匹配任务。" if query else "当前没有设置本地任务。"
    return DeliverySummary(
        raw_request=raw,
        status="no-task",
        status_reason=reason,
        task="",
        task_done=False,
        progress="0/7",
        current_stage="未找到当前任务",
        changed_items=["还不能可靠生成完成说明，因为没有找到当前任务记录。"],
        acceptance_actions=["先让 Codex 恢复或创建当前任务记录，再生成交付总结。"],
        expected_results=["恢复任务记录后，交付总结会包含完成状态、改动内容、验收方式和风险说明。"],
        verification_status="验收记录暂不可用。",
        risks_and_non_actions=["在没有任务记录前，不会编造已完成内容或验收结论。"],
        needs_user_confirmation=["需要先确认要总结哪一项任务，或让 Codex 恢复当前任务记录。"],
        non_actions=standard_non_actions(),
        next_user_message="我需要先找到当前任务记录，才能生成可靠的团队完成说明。",
    )


def build_delivery_summary(args: argparse.Namespace) -> DeliverySummary:
    raw = compact(args.raw)
    payload = dashboard_for(args)
    tasks = payload.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        return build_no_task_summary(raw, args.query)

    item = tasks[0]
    assert isinstance(item, dict)
    task = str(item.get("task") or "未命名任务")
    boundary = str(item.get("boundary") or "")
    boundary_path = REPO_ROOT / boundary if boundary else None
    boundary_text = read_text(boundary_path) if boundary_path and boundary_path.exists() else ""
    current_step = str(item.get("current_step_key") or "")
    current_stage = str(item.get("current_step") or "未知")
    task_done = current_step == "complete"
    progress = str(item.get("progress") or "0/7")

    expected = parse_section_field_items(boundary_text, "User-visible Acceptance", "Expected Visible Behavior")
    actions = parse_section_field_items(boundary_text, "User-visible Acceptance", "User Actions To Verify")
    non_goals = section_bullets(boundary_text, "Functional Non-goals")
    status_reason = "当前任务记录显示已经完成。" if task_done else f"当前任务还没有全部完成，目前在{current_stage}。"
    confirmations = (
        ["暂时不需要；这份说明可以作为当前交付总结。"]
        if task_done
        else ["当前任务还没全部收口；如果要发给团队，请标注为当前进展总结而不是最终完成说明。"]
    )

    return DeliverySummary(
        raw_request=raw,
        status="ready-to-share" if task_done else "progress-summary",
        status_reason=status_reason,
        task=task,
        task_done=task_done,
        progress=progress,
        current_stage=current_stage,
        changed_items=user_safe_items(expected, "当前任务记录没有写明交付变化，Codex 需要先补充可见结果。"),
        acceptance_actions=user_safe_items(actions, "查看本轮输出或让 Codex 按当前任务记录转述验收结果。"),
        expected_results=user_safe_items(expected, "能看到与本次任务目标一致的结果。"),
        verification_status=qa_line(item),
        risks_and_non_actions=user_safe_items(
            [*non_goals, *standard_non_actions()],
            "本次只按当前任务范围总结，不扩展到真实数据、生产、数据库或代码提交流程。",
            limit=6,
        ),
        needs_user_confirmation=confirmations,
        non_actions=standard_non_actions(),
        next_user_message="我会把当前任务记录转成一段可以给团队看的完成说明。",
    )


def render_user(summary: DeliverySummary) -> str:
    lines = [
        "可以直接这样发给团队：",
        "",
    ]
    if summary.status == "no-task":
        lines.extend(
            [
                "本次交付：暂时无法确认",
                f"当前状态：{summary.status_reason}",
                "",
                "Codex 的下一步：",
                *[f"- {item}" for item in summary.acceptance_actions],
                "",
                "需要你确认：",
                *[f"- {item}" for item in summary.needs_user_confirmation],
                "",
                "这次不会做什么：",
                *[f"- {item}" for item in summary.non_actions],
            ]
        )
        return "\n".join(lines)

    lines.extend(
        [
            f"本次交付：{summary.task}",
            f"当前状态：{summary.status_reason}",
            f"进度：{summary.progress}",
            "",
            "这次改了什么：",
            *[f"- {item}" for item in summary.changed_items],
            "",
            "怎么验收：",
            *[f"- {item}" for item in summary.acceptance_actions],
            "",
            "预期应该看到：",
            *[f"- {item}" for item in summary.expected_results],
            "",
            f"验收记录：{summary.verification_status}",
            "",
            "风险和未做：",
            *[f"- {item}" for item in summary.risks_and_non_actions],
            "",
            "需要你确认：",
            *[f"- {item}" for item in summary.needs_user_confirmation],
        ]
    )
    return "\n".join(lines)


def render_markdown(summary: DeliverySummary) -> str:
    lines = [
        "# 非技术交付总结",
        "",
        f"- 状态：{summary.status}",
        f"- 状态原因：{summary.status_reason}",
        f"- 当前任务：{summary.task or '未找到'}",
        f"- 是否完成：{'是' if summary.task_done else '否'}",
        f"- 当前阶段：{summary.current_stage}",
        f"- 进度：{summary.progress}",
        "- 这次改了什么：",
        *[f"  - {item}" for item in summary.changed_items],
        "- 怎么验收：",
        *[f"  - {item}" for item in summary.acceptance_actions],
        "- 预期应该看到：",
        *[f"  - {item}" for item in summary.expected_results],
        f"- 验收记录：{summary.verification_status}",
        "- 风险和未做：",
        *[f"  - {item}" for item in summary.risks_and_non_actions],
        "- 需要用户确认：",
        *[f"  - {item}" for item in summary.needs_user_confirmation],
        "- 不执行动作：",
        *[f"  - {item}" for item in summary.non_actions],
    ]
    return "\n".join(lines)


def render_json(summary: DeliverySummary) -> str:
    return json.dumps(asdict(summary), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's delivery-summary request.")
    parser.add_argument("--query", default="", help="Optional task query for deterministic checks.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    summary = build_delivery_summary(args)
    if args.format == "json":
        print(render_json(summary))
    elif args.format == "user":
        print(render_user(summary))
    else:
        print(render_markdown(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
