#!/usr/bin/env python3
"""Explain what to do when a nontechnical user cannot see page changes.

This helper is deterministic and read-only. It reads the current active task
boundary and generated dashboard summary, then turns the visible-change
troubleshooting path into user-facing language. It does not open browsers,
connect to services, write evidence, touch databases, or run git actions.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path

from gstack_dashboard import (
    active_boundary,
    first_task_line,
    parse_section_field_items,
    parse_section_field_value,
    plain_text,
    read_text,
    summarize_boundary,
)


@dataclass(frozen=True)
class VisibleChangeTroubleshoot:
    raw_request: str
    status: str
    status_reason: str
    task: str
    task_done: bool
    surface_type: str
    view_locations: list[str]
    refresh_or_regenerate: list[str]
    if_still_old: list[str]
    codex_next_actions: list[str]
    needs_user_confirmation: list[str]
    next_user_message: str


def compact(raw: str) -> str:
    return " ".join(raw.strip().split())


def is_useful(value: str) -> bool:
    cleaned = compact(value)
    return bool(cleaned) and cleaned not in {"不适用", "not-applicable", "none", "无"}


def user_safe_path_hint(raw: str) -> str:
    text = plain_text(raw)
    if ".gstack/" in text or text.startswith("/"):
        return "当前任务记录里的查看位置"
    if "output/" in text:
        return "最新生成的本地页面"
    return text


def user_text(raw: str) -> str:
    text = plain_text(raw)
    if "python3 " in text:
        text = "让 Codex 重新检查当前任务并重新生成最新输出。"
    else:
        text = user_safe_path_hint(text)
    replacements = {
        "CLI": "本地输出",
        "QA": "验收记录",
        "smoke": "关键路径检查",
        "boundary": "任务范围",
        "gate": "内部检查",
        "spec": "规格说明",
        "JSON": "内部数据",
        ".gstack": "内部记录",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = text.replace("验收记录 报告", "验收报告")
    text = text.replace("本地输出 输出", "本地输出")
    return text


def append_unique(items: list[str], value: str) -> None:
    cleaned = compact(user_text(value))
    if cleaned and cleaned not in items:
        items.append(cleaned)


def surface_is_page(surface_type: str, acceptance_url: str) -> bool:
    text = f"{surface_type} {acceptance_url}".lower()
    page_tokens = ("html", "ui", "page", "browser", "web", "页面", "可视化", "网页")
    cli_tokens = ("cli", "command", "user-output", "脚本", "命令", "文档", "docs")
    if any(token in text for token in page_tokens):
        return True
    if any(token in text for token in cli_tokens):
        return False
    return is_useful(acceptance_url)


def build_view_locations(text: str, surface_type: str, acceptance_url: str) -> list[str]:
    locations: list[str] = []
    if is_useful(acceptance_url):
        append_unique(locations, user_safe_path_hint(acceptance_url))
    else:
        append_unique(locations, "当前任务没有写页面验收地址，先不要只靠刷新页面判断。")

    actions = parse_section_field_items(text, "User-visible Acceptance", "User Actions To Verify")
    for action in actions[:2]:
        append_unique(locations, action)

    if not surface_is_page(surface_type, acceptance_url):
        append_unique(locations, "当前任务记录显示这可能不是页面改动，刷新页面看不到变化可能是正常的。")
    return locations[:5]


def build_refresh_steps(text: str, surface_type: str) -> list[str]:
    steps: list[str] = []
    refresh = parse_section_field_value(text, "Generated Artifact Policy", "Refresh / Regeneration")
    if is_useful(refresh):
        append_unique(steps, refresh)
    if "html" in surface_type.lower() or "页面" in surface_type or "网页" in surface_type:
        append_unique(steps, "确认打开的是最新生成的页面；旧页面或旧临时文件不会自动更新。")
        append_unique(steps, "如果页面由本地服务提供，先让 Codex 确认服务是否已重新启动或重新构建。")
    else:
        append_unique(steps, "让 Codex 重新生成当前任务的输出或验收说明，再按当前任务记录查看。")
    return steps[:5]


def build_if_still_old(text: str, surface_type: str, acceptance_url: str, task_done: bool) -> list[str]:
    reasons: list[str] = []
    no_visible = parse_section_field_value(text, "Generated Artifact Policy", "If No Visible Change")
    if is_useful(no_visible):
        append_unique(reasons, no_visible)
    if not task_done:
        append_unique(reasons, "当前任务还没有完成最终收口，页面不一定已经有可见变化。")
    if not surface_is_page(surface_type, acceptance_url):
        append_unique(reasons, "这轮可能不是页面变更，刷新页面看不到变化不等于任务失败。")
    append_unique(reasons, "可能打开了旧页面、旧临时文件或旧端口。")
    append_unique(reasons, "可能还没有重新生成静态页面，或浏览器仍在显示缓存。")
    return reasons[:6]


def build_codex_actions(surface_type: str, acceptance_url: str) -> list[str]:
    actions: list[str] = [
        "先核对当前任务记录里的查看位置和验收方式。",
        "再判断这轮是不是页面改动；如果不是页面改动，就改用正确的输出或说明验收。",
    ]
    if surface_is_page(surface_type, acceptance_url):
        actions.extend(
            [
                "如果是生成页面，重新生成最新页面并让浏览器打开最新版本。",
                "如果是本地运行页面，确认本地服务、构建和刷新路径是否对应当前任务。",
                "需要真实页面交互时，Codex 会用浏览器工具实际打开并操作验证。",
            ]
        )
    else:
        actions.append("如果当前任务只是脚本、文档或本地输出，Codex 会直接转述正确验收入口。")
    return actions[:6]


def build_confirmations(has_active: bool, surface_type: str, acceptance_url: str) -> list[str]:
    if not has_active:
        return ["需要先恢复或创建当前任务记录。"]
    confirmations = ["暂时不需要；Codex 可以先按当前任务记录排查。"]
    if surface_is_page(surface_type, acceptance_url):
        confirmations.append("如果你方便，把你打开的页面地址或截图发给我，我可以对照当前任务记录判断是不是旧页面。")
    else:
        confirmations.append("如果你确实期待页面变化，请告诉我你打开的是哪个页面；这可能需要另建页面任务。")
    return confirmations


def build_troubleshoot(args: argparse.Namespace) -> VisibleChangeTroubleshoot:
    raw = compact(args.raw)
    active = active_boundary()
    if not active:
        return VisibleChangeTroubleshoot(
            raw_request=raw,
            status="no-active-task",
            status_reason="当前没有本地 active task，无法判断应该看哪个页面或输出。",
            task="",
            task_done=False,
            surface_type="",
            view_locations=["当前没有设置本地任务，所以还不能判断你刷新的是不是正确页面。"],
            refresh_or_regenerate=["让 Codex 先恢复或创建当前任务记录。"],
            if_still_old=["没有当前任务记录时，刷新页面是否有变化不能作为可靠验收。"],
            codex_next_actions=["先恢复当前任务记录，再读取验收和刷新说明。"],
            needs_user_confirmation=["如果你知道这次任务名称或页面地址，可以告诉我；否则 Codex 会先检查本地任务记录。"],
            next_user_message="我需要先恢复当前任务记录，再判断为什么看不到变化。",
        )

    text = read_text(active)
    summary = summarize_boundary(active, active)
    surface_type = parse_section_field_value(text, "Generated Artifact Policy", "Surface Type")
    acceptance_url = parse_section_field_value(text, "Generated Artifact Policy", "Acceptance URL")
    task_done = summary.current_step_key == "complete"
    task = first_task_line(text, Path(active))
    page_surface = surface_is_page(surface_type, acceptance_url)
    status = "page-troubleshoot-ready" if page_surface else "not-page-change"
    reason = "当前任务记录包含页面或可视化查看信息。" if page_surface else "当前任务记录不像页面变更，刷新页面看不到变化可能正常。"
    return VisibleChangeTroubleshoot(
        raw_request=raw,
        status=status,
        status_reason=reason,
        task=task,
        task_done=task_done,
        surface_type=surface_type or "未填写",
        view_locations=build_view_locations(text, surface_type, acceptance_url),
        refresh_or_regenerate=build_refresh_steps(text, surface_type),
        if_still_old=build_if_still_old(text, surface_type, acceptance_url, task_done),
        codex_next_actions=build_codex_actions(surface_type, acceptance_url),
        needs_user_confirmation=build_confirmations(True, surface_type, acceptance_url),
        next_user_message="我会先按当前任务记录排查你看的位置、刷新方式和是否属于页面改动。",
    )


def render_user(plan: VisibleChangeTroubleshoot) -> str:
    if plan.status == "no-active-task":
        lines = [
            "我先不能判断为什么页面没变化，因为当前没有可用的任务记录。",
            "",
            "Codex 的下一步：",
            *[f"- {item}" for item in plan.codex_next_actions],
            "",
            "需要你确认：",
            *[f"- {item}" for item in plan.needs_user_confirmation],
        ]
        return "\n".join(lines)

    lines = [
        "我先按当前任务排查可见变化。",
        "",
        f"当前任务：{plan.task}",
        f"判断：{plan.status_reason}",
        "",
        "先确认你看的地方：",
        *[f"- {item}" for item in plan.view_locations],
        "",
        "怎么刷新 / 重新生成：",
        *[f"- {item}" for item in plan.refresh_or_regenerate],
        "",
        "如果刷新后还是旧的：",
        *[f"- {item}" for item in plan.if_still_old],
        "",
        "Codex 的下一步：",
        *[f"- {item}" for item in plan.codex_next_actions],
        "",
        "需要你确认：",
        *[f"- {item}" for item in plan.needs_user_confirmation],
    ]
    return "\n".join(lines)


def render_markdown(plan: VisibleChangeTroubleshoot) -> str:
    lines = [
        "# 非技术可见变化排查",
        "",
        f"- 状态：{plan.status}",
        f"- 状态原因：{plan.status_reason}",
        f"- 当前任务：{plan.task or '未找到'}",
        f"- 当前任务是否完成：{'是' if plan.task_done else '否'}",
        f"- Surface Type：{plan.surface_type or '未填写'}",
        "- 先确认你看的地方：",
        *[f"  - {item}" for item in plan.view_locations],
        "- 怎么刷新 / 重新生成：",
        *[f"  - {item}" for item in plan.refresh_or_regenerate],
        "- 如果刷新后还是旧的：",
        *[f"  - {item}" for item in plan.if_still_old],
        "- Codex 的下一步：",
        *[f"  - {item}" for item in plan.codex_next_actions],
        "- 需要用户确认：",
        *[f"  - {item}" for item in plan.needs_user_confirmation],
    ]
    return "\n".join(lines)


def render_json(plan: VisibleChangeTroubleshoot) -> str:
    return json.dumps(asdict(plan), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's visible-change complaint.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    plan = build_troubleshoot(args)
    if args.format == "json":
        print(render_json(plan))
    elif args.format == "user":
        print(render_user(plan))
    else:
        print(render_markdown(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
