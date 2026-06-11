#!/usr/bin/env python3
"""Render a plain-language home entry for Codex-led development.

The helper is read-only and intended for Codex internal use. Nontechnical users
ask Codex to open the development home; Codex runs this helper and presents the
plain-language output.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class HelperStatus:
    name: str
    status: str


@dataclass(frozen=True)
class HomeResult:
    status: str
    current_task: str
    current_state: str
    next_step: str
    options: list[str]
    complex_request_template: list[str]
    acceptance_summary: list[str]
    recovery_summary: list[str]
    non_actions: list[str]
    helper_status: list[HelperStatus]


def python_command(*args: str) -> list[str]:
    return [sys.executable, *args]


def run_command(command: list[str], *, allow_nonzero: bool = False) -> tuple[str, str]:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout.strip() or result.stderr.strip()
    if result.returncode != 0 and not allow_nonzero:
        return "failed", output
    return "ok" if result.returncode == 0 else "partial", output


def strip_internal_terms(text: str) -> str:
    replacements = {
        "git workflow action": "代码提交流程",
        "git 操作": "代码提交流程",
        "git": "代码提交流程",
        "commit / push / merge / PR": "代码提交流程",
        "raw JSON": "内部数据",
        "JSON": "内部数据",
        "boundary": "任务范围",
        "gate": "内部检查",
        "spec": "规格说明",
        "lane": "推进方式",
        "QA": "验收记录",
        "CLI": "本地输出",
        "evidence": "记录",
        ".gstack": "内部",
    }
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if "内部记录：" in stripped:
            continue
        if ".gstack/" in stripped:
            continue
        if "python3 " in stripped:
            continue
        cleaned_lines.append(line)
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\.gstack/[^\s，。)）]+", "内部记录", cleaned)
    cleaned = re.sub(r"`[^`]*\.gstack[^`]*`", "内部记录", cleaned)
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    cleaned = cleaned.replace("或 代码提交流程", "或代码提交流程")
    cleaned = cleaned.replace("验收记录 记录", "验收记录")
    return cleaned.strip()


def value_after_prefix(text: str, prefix: str, fallback: str) -> str:
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            value = stripped[len(prefix) :].strip()
            return strip_internal_terms(value) or fallback
    return fallback


def bullet_items_after_header(text: str, header: str, limit: int = 4) -> list[str]:
    lines = text.splitlines()
    in_section = False
    items: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped == header:
            in_section = True
            continue
        if in_section and stripped.startswith("## "):
            break
        if not in_section:
            continue
        if stripped.startswith("- "):
            item = strip_internal_terms(stripped[2:])
            if item:
                items.append(item)
        if len(items) >= limit:
            break
    return items


def build_home() -> HomeResult:
    dashboard_status, dashboard = run_command(python_command(".gstack/scripts/gstack_dashboard.py", "explain"))
    verify_status, verify = run_command(python_command(".gstack/scripts/gstack_dashboard.py", "verify"))
    doctor_status, doctor = run_command(
        python_command(".gstack/scripts/gstack_doctor.py", "explain"),
        allow_nonzero=True,
    )

    current_task = value_after_prefix(dashboard, "当前任务：", "当前没有读到明确任务。")
    current_state = value_after_prefix(dashboard, "状态：", "Codex 会先检查当前任务状态。")
    next_step = value_after_prefix(dashboard, "下一步：", "继续识别当前最安全的下一步。")

    acceptance_summary = bullet_items_after_header(verify, "你可以这样验收：", limit=3)
    if not acceptance_summary:
        acceptance_summary = ["让 Codex 说明完成后你要看哪里、做什么、预期看到什么。"]

    recovery_summary = bullet_items_after_header(doctor, "## 你现在需要做什么", limit=3)
    if not recovery_summary:
        recovery_summary = ["暂时不需要你做技术操作；Codex 会先检查当前协作状态。"]

    return HomeResult(
        status="home-ready",
        current_task=current_task,
        current_state=current_state,
        next_step=next_step,
        options=[
            "继续当前任务：直接说“继续做”。",
            "开始复杂需求：直接说“我要做...”，或照填下面几行。",
            "验收当前结果：直接说“我怎么知道它真的好了”。",
            "出错后恢复：直接说“出错了，帮我看下一步怎么办”。",
            "检查关键路径：直接说“帮我检查非技术开发关键路径”。",
        ],
        complex_request_template=[
            "谁会用：",
            "他们想完成什么：",
            "成功后第一眼要看到什么：",
            "用户会怎么操作：",
            "数据从哪里来，是否可以先用假数据：",
            "这次不要碰什么：",
            "完成后我会怎么验收：",
        ],
        acceptance_summary=acceptance_summary,
        recovery_summary=recovery_summary,
        non_actions=[
            "不会要求你自己运行命令或阅读工程文档。",
            "不会直接操作真实数据、生产环境、数据库、破坏性命令或代码提交流程。",
            "不会把内部任务范围、内部检查、规格说明或内部数据直接丢给你判断。",
        ],
        helper_status=[
            HelperStatus("current-task", dashboard_status),
            HelperStatus("acceptance", verify_status),
            HelperStatus("recovery", doctor_status),
        ],
    )


def render_user(result: HomeResult) -> str:
    lines = [
        "# 非技术开发首页",
        "",
        "当前任务：",
        f"- {result.current_task}",
        "",
        "现在状态：",
        f"- {result.current_state}",
        "",
        "Codex 的下一步：",
        f"- {result.next_step}",
        "",
        "你现在可以：",
    ]
    lines.extend(f"- {item}" for item in result.options)
    lines.extend(["", "开始复杂需求可以这样发："])
    lines.extend(f"- {item}" for item in result.complex_request_template)
    lines.extend(["", "验收当前结果："])
    lines.extend(f"- {item}" for item in result.acceptance_summary)
    lines.extend(["", "出错后怎么继续："])
    lines.extend(f"- {item}" for item in result.recovery_summary)
    lines.extend(["", "这次不会做什么："])
    lines.extend(f"- {item}" for item in result.non_actions)
    return "\n".join(lines)


def render_json(result: HomeResult) -> str:
    return json.dumps(asdict(result), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("user", "json"), default="user")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = build_home()
    if args.format == "json":
        print(render_json(result))
    else:
        print(render_user(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
