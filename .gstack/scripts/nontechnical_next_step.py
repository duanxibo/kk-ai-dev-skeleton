#!/usr/bin/env python3
"""Generate the next plain-language reply for a nontechnical user request.

This helper is deterministic and read-only. It routes the user's utterance,
runs the matching local helper, and sanitizes the result for user-facing use.
It does not create formal evidence, connect to data sources, open browsers,
run production actions, touch databases, or run git actions.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from nontechnical_intent_router import IntentRoute, build_route, user_text as router_user_text


REPO_ROOT = Path(__file__).resolve().parents[2]
SMOKE_RECURSION_ENV = "KK_NATURAL_LANGUAGE_SMOKE_ACTIVE"


@dataclass(frozen=True)
class NextStepResult:
    raw_request: str
    intent: str
    internal_entry: str
    helper_entry: str
    helper_status: str
    needs_user_confirmation: bool
    user_response: str


def optional_arg(flag: str, value: str) -> list[str]:
    return [flag, value] if value else []


def run_command(
    command: list[str],
    *,
    allow_nonzero: bool = False,
    env: dict[str, str] | None = None,
) -> tuple[str, str]:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    output = result.stdout.strip() or result.stderr.strip()
    if result.returncode != 0 and not allow_nonzero:
        return "failed", output or "内部检查没有返回结果。"
    return "ok" if result.returncode == 0 else "partial", output


def python_command(*args: str) -> list[str]:
    return [sys.executable, *args]


def starter_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        *optional_arg("--audience", args.audience),
        *optional_arg("--success", args.success),
        *optional_arg("--non-goal", args.non_goal),
        *optional_arg("--risk-confirmation", args.risk_confirmation),
        "--topic",
        args.topic or "nontechnical-next-step",
        "--dry-run",
        "--format",
        "user",
    ]


def formal_kickoff_args(args: argparse.Namespace) -> list[str]:
    command_args = [
        "--raw",
        args.raw,
        *optional_arg("--audience", args.audience),
        *optional_arg("--success", args.success),
        *optional_arg("--non-goal", args.non_goal),
        *optional_arg("--risk-confirmation", args.risk_confirmation),
        "--topic",
        args.topic or "nontechnical-formal-kickoff-preview",
        "--dry-run",
        "--format",
        "user",
    ]
    if args.ai_reviewed:
        command_args.append("--ai-reviewed")
    return command_args


def execution_plan_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        *optional_arg("--audience", args.audience),
        *optional_arg("--success", args.success),
        *optional_arg("--non-goal", args.non_goal),
        *optional_arg("--risk-confirmation", args.risk_confirmation),
        "--format",
        "user",
    ]


def acceptance_plan_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        *optional_arg("--audience", args.audience),
        *optional_arg("--success", args.success),
        *optional_arg("--non-goal", args.non_goal),
        *optional_arg("--risk-confirmation", args.risk_confirmation),
        "--format",
        "user",
    ]


def visible_change_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def ci_failure_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def continue_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def team_sync_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def delivery_summary_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def mode_control_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def recommendation_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def first_use_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def scope_change_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def page_change_brief_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def requirement_brief_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def requirement_readiness_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def ui_optimization_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        *optional_arg("--audience", args.audience),
        *optional_arg("--success", args.success),
        *optional_arg("--non-goal", args.non_goal),
        "--format",
        "user",
    ]


def task_list_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def home_args(args: argparse.Namespace) -> list[str]:
    return ["--format", "user"]


def implementation_readiness_args(args: argparse.Namespace) -> list[str]:
    return ["--format", "user"]


def confirmation_brief_args(args: argparse.Namespace) -> list[str]:
    return ["--format", "user"]


def confirmation_response_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def pause_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def undo_request_args(args: argparse.Namespace) -> list[str]:
    return [
        "--raw",
        args.raw,
        "--format",
        "user",
    ]


def sanitize_user_output(text: str) -> str:
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
        "user 输出": "用户看到的说明",
    }
    cleaned_lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue
        if "内部记录：" in stripped:
            continue
        if ".gstack/" in stripped:
            continue
        if "python3 " in stripped:
            if stripped.startswith("刷新或重新生成"):
                cleaned_lines.append("刷新或重新生成：让 Codex 重新检查当前任务。")
            continue
        cleaned_lines.append(line)
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\.gstack/[^\s，。)）]+", "内部记录", cleaned)
    cleaned = re.sub(r"`[^`]*\.gstack[^`]*`", "内部记录", cleaned)
    for old, new in replacements.items():
        cleaned = cleaned.replace(old, new)
    cleaned = cleaned.replace("或 代码提交流程", "或代码提交流程")
    cleaned = cleaned.replace("本地输出 输出", "本地输出")
    cleaned = cleaned.replace("验收记录 记录", "验收记录")
    cleaned = cleaned.replace("验收记录 报告", "验收报告")
    cleaned = cleaned.replace("内部 路径", "内部路径")
    cleaned = cleaned.replace("内部数据 输出", "内部数据")
    cleaned = cleaned.replace("代码提交流程 时", "代码提交流程时")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned or "Codex 会先检查当前任务状态，再用人话说明下一步。"


def helper_for_route(route: IntentRoute, args: argparse.Namespace) -> tuple[str, str, str]:
    if route.intent == "nontechnical_home":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_home.py", *home_args(args))
        )
        return "nontechnical_home.user", status, output
    if route.intent == "implementation_readiness":
        status, output = run_command(
            python_command(
                ".gstack/scripts/nontechnical_implementation_readiness.py",
                *implementation_readiness_args(args),
            )
        )
        return "nontechnical_implementation_readiness.user", status, output
    if route.intent == "confirmation_brief":
        status, output = run_command(
            python_command(
                ".gstack/scripts/nontechnical_confirmation_brief.py",
                *confirmation_brief_args(args),
            )
        )
        return "nontechnical_confirmation_brief.user", status, output
    if route.intent == "confirmation_response":
        status, output = run_command(
            python_command(
                ".gstack/scripts/nontechnical_confirmation_response.py",
                *confirmation_response_args(args),
            )
        )
        return "nontechnical_confirmation_response.user", status, output
    if route.intent == "pause_current_task":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_pause.py", *pause_args(args))
        )
        return "nontechnical_pause.user", status, output
    if route.intent == "undo_request":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_undo_request.py", *undo_request_args(args))
        )
        return "nontechnical_undo_request.user", status, output
    if route.intent == "mode_control":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_mode_control.py", *mode_control_args(args))
        )
        return "nontechnical_mode_control.user", status, output
    if route.intent == "recommendation":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_recommendation.py", *recommendation_args(args))
        )
        return "nontechnical_recommendation.user", status, output
    if route.intent == "first_use_guide":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_first_use.py", *first_use_args(args))
        )
        return "nontechnical_first_use.user", status, output
    if route.intent == "scope_change":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_scope_change.py", *scope_change_args(args))
        )
        return "nontechnical_scope_change.user", status, output
    if route.intent == "page_change_brief":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_page_change_brief.py", *page_change_brief_args(args))
        )
        return "nontechnical_page_change_brief.user", status, output
    if route.intent == "requirement_brief":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_requirement_brief.py", *requirement_brief_args(args))
        )
        return "nontechnical_requirement_brief.user", status, output
    if route.intent == "requirement_readiness":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_requirement_readiness.py", *requirement_readiness_args(args))
        )
        return "nontechnical_requirement_readiness.user", status, output
    if route.intent == "ui_optimization_kickoff":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_ui_optimization.py", *ui_optimization_args(args))
        )
        return "nontechnical_ui_optimization.user", status, output
    if route.intent == "progress_status":
        status, output = run_command(python_command(".gstack/scripts/gstack_dashboard.py", "explain"))
        return "gstack_dashboard.explain", status, output
    if route.intent == "completion_verify":
        status, output = run_command(python_command(".gstack/scripts/gstack_dashboard.py", "verify"))
        return "gstack_dashboard.verify", status, output
    if route.intent == "error_recovery":
        status, output = run_command(
            python_command(".gstack/scripts/gstack_doctor.py", "explain"),
            allow_nonzero=True,
        )
        return "gstack_doctor.explain", status, output
    if route.intent == "natural_language_smoke":
        if os.environ.get(SMOKE_RECURSION_ENV) == "1":
            return (
                "natural_language_dev_smoke.user",
                "ok",
                "非技术开发关键路径检查会由 Codex 运行本地回归，并用人话说明是否通过、覆盖了什么、是否需要你确认。",
            )
        status, output = run_command(
            python_command(".gstack/scripts/natural_language_dev_smoke.py", "--format", "user"),
            env={**os.environ, SMOKE_RECURSION_ENV: "1"},
        )
        return "natural_language_dev_smoke.user", status, output
    if route.intent in {"complex_task_starter", "controlled_starter"}:
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_task_starter.py", *starter_args(args))
        )
        return "nontechnical_task_starter.user", status, output
    if route.intent == "formal_kickoff_preview":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_formal_kickoff.py", *formal_kickoff_args(args))
        )
        return "nontechnical_formal_kickoff.user", status, output
    if route.intent == "execution_plan":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_execution_plan.py", *execution_plan_args(args))
        )
        return "nontechnical_execution_plan.user", status, output
    if route.intent == "acceptance_plan":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_acceptance_plan.py", *acceptance_plan_args(args))
        )
        return "nontechnical_acceptance_plan.user", status, output
    if route.intent == "visible_change_troubleshoot":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_visible_change.py", *visible_change_args(args))
        )
        return "nontechnical_visible_change.user", status, output
    if route.intent == "ci_failure_explain":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_ci_failure.py", *ci_failure_args(args))
        )
        return "nontechnical_ci_failure.user", status, output
    if route.intent == "continue_current_task":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_continue.py", *continue_args(args))
        )
        return "nontechnical_continue.user", status, output
    if route.intent == "team_sync_explain":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_team_sync.py", *team_sync_args(args))
        )
        return "nontechnical_team_sync.user", status, output
    if route.intent == "delivery_summary":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_delivery_summary.py", *delivery_summary_args(args))
        )
        return "nontechnical_delivery_summary.user", status, output
    if route.intent == "task_list_explain":
        status, output = run_command(
            python_command(".gstack/scripts/nontechnical_task_list.py", *task_list_args(args))
        )
        return "nontechnical_task_list.user", status, output
    return route.internal_entry, "ok", router_user_text(route)


def build_next_step(args: argparse.Namespace) -> NextStepResult:
    route = build_route(args)
    helper_entry, helper_status, helper_output = helper_for_route(route, args)
    return NextStepResult(
        raw_request=route.raw_request,
        intent=route.intent,
        internal_entry=route.internal_entry,
        helper_entry=helper_entry,
        helper_status=helper_status,
        needs_user_confirmation=route.needs_user_confirmation,
        user_response=sanitize_user_output(helper_output),
    )


def render_json(result: NextStepResult) -> str:
    return json.dumps(asdict(result), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original plain-language request.")
    parser.add_argument("--audience", default="", help="Optional target user or usage context.")
    parser.add_argument("--success", default="", help="Optional visible success criteria.")
    parser.add_argument("--non-goal", default="", help="Optional explicit non-goals or forbidden scope.")
    parser.add_argument("--risk-confirmation", default="", help="Optional user confirmation that constrains high-risk actions.")
    parser.add_argument("--topic", default="", help="Optional starter preview topic.")
    parser.add_argument(
        "--ai-reviewed",
        action="store_true",
        help="Allow formal kickoff preview to say Codex has semantically reviewed the request; still read-only.",
    )
    parser.add_argument("--format", choices=("user", "json"), default="user")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = build_next_step(args)
    if args.format == "json":
        print(render_json(result))
    else:
        print(result.user_response)
    return 0 if result.helper_status in {"ok", "partial"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
