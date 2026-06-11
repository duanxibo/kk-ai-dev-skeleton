#!/usr/bin/env python3
"""Guide a nontechnical user from an idea to a kickoff-ready request.

This helper is deterministic and read-only. It composes existing
nontechnical helpers instead of creating formal evidence, connecting data
sources, running production actions, touching databases, or running git
workflow actions.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


GUIDED_TEMPLATE = """# 复杂需求向导

你可以先照填下面 6 行，信息不完整也可以先发：

谁会用：
想完成什么：
成功后第一眼看到：
用户会怎么操作：
数据从哪里来：
这次不要碰：
怎么验收：

Codex 的下一步：
- 如果信息还不够，会先告诉你优先补哪一项。
- 如果信息已经够，会先给推进顺序、确认点和验收方式。
- 如果你明确说正式开工，Codex 做完语义复核后会先给只读开工预览。

这次不会做什么：
- 不连接真实数据。
- 不操作生产环境。
- 不写数据库。
- 不发布。
- 不执行代码提交流程。
"""


@dataclass(frozen=True)
class GuidedKickoffResult:
    raw_request: str
    stage: str
    helper_entry: str
    helper_status: str
    needs_user_confirmation: bool
    user_response: str


def optional_arg(flag: str, value: str) -> list[str]:
    return [flag, value] if value else []


def effective_risk_confirmation(args: argparse.Namespace) -> str:
    if args.risk_confirmation:
        return args.risk_confirmation
    non_goal = args.non_goal
    has_risk_word = any(word in non_goal for word in ("真实数据", "生产", "线上", "数据库", "发布", "提交"))
    has_limit_word = any(word in non_goal for word in ("不", "不要", "不改", "不碰", "不操作", "不写"))
    if has_risk_word and has_limit_word:
        return "只允许先整理需求和验收口径，不操作真实数据，不写数据库，不操作生产环境，不发布，不提交。"
    return ""


def python_command(*args: str) -> list[str]:
    return [sys.executable, *args]


def run_command(command: list[str]) -> tuple[str, str]:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    output = result.stdout.strip() or result.stderr.strip()
    return ("ok" if result.returncode == 0 else "failed", output or "内部检查没有返回结果。")


def build_common_args(args: argparse.Namespace, *, output_format: str) -> list[str]:
    return [
        "--raw",
        args.raw,
        *optional_arg("--audience", args.audience),
        *optional_arg("--success", args.success),
        *optional_arg("--non-goal", args.non_goal),
        *optional_arg("--risk-confirmation", effective_risk_confirmation(args)),
        "--format",
        output_format,
    ]


def parse_json_or_empty(text: str) -> dict:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def request_text_for_readiness(args: argparse.Namespace) -> str:
    parts = [args.raw.strip()]
    if args.audience:
        parts.append(f"谁会用：{args.audience}")
    if args.success:
        parts.append(f"成功后第一眼看到：{args.success}")
        parts.append(f"怎么验收：{args.success}")
    if args.non_goal:
        parts.append(f"这次不要碰：{args.non_goal}")
    risk_confirmation = effective_risk_confirmation(args)
    if risk_confirmation:
        parts.append(f"风险确认：{risk_confirmation}")
    return "；".join(part for part in parts if part)


def readiness(args: argparse.Namespace) -> tuple[str, str, dict]:
    status, output = run_command(
        python_command(
            ".gstack/scripts/nontechnical_requirement_readiness.py",
            "--raw",
            request_text_for_readiness(args),
            "--format",
            "json",
        )
    )
    return status, output, parse_json_or_empty(output)


def render_guided_user(args: argparse.Namespace) -> GuidedKickoffResult:
    if not args.raw.strip():
        return GuidedKickoffResult(
            raw_request="",
            stage="template",
            helper_entry="nontechnical_guided_kickoff.template",
            helper_status="ok",
            needs_user_confirmation=False,
            user_response=GUIDED_TEMPLATE.strip(),
        )

    readiness_status, readiness_output, readiness_json = readiness(args)
    if readiness_status != "ok":
        return GuidedKickoffResult(
            raw_request=args.raw,
            stage="readiness-check",
            helper_entry="nontechnical_requirement_readiness.user",
            helper_status=readiness_status,
            needs_user_confirmation=True,
            user_response=readiness_output,
        )

    if not readiness_json.get("can_preview_kickoff", False):
        status, output = run_command(
            python_command(
                ".gstack/scripts/nontechnical_requirement_readiness.py",
                "--raw",
                request_text_for_readiness(args),
                "--format",
                "user",
            )
        )
        return GuidedKickoffResult(
            raw_request=args.raw,
            stage="readiness-check",
            helper_entry="nontechnical_requirement_readiness.user",
            helper_status=status,
            needs_user_confirmation=True,
            user_response=output,
        )

    if args.formal:
        command_args = [
            ".gstack/scripts/nontechnical_formal_kickoff.py",
            "--raw",
            args.raw,
            *optional_arg("--audience", args.audience),
            *optional_arg("--success", args.success),
            *optional_arg("--non-goal", args.non_goal),
            *optional_arg("--risk-confirmation", effective_risk_confirmation(args)),
            "--topic",
            args.topic,
            "--dry-run",
            "--format",
            "user",
        ]
        if args.ai_reviewed:
            command_args.append("--ai-reviewed")
        status, output = run_command(python_command(*command_args))
        return GuidedKickoffResult(
            raw_request=args.raw,
            stage="formal-kickoff-preview",
            helper_entry="nontechnical_formal_kickoff.user",
            helper_status=status,
            needs_user_confirmation=not args.ai_reviewed,
            user_response=output,
        )

    status, output = run_command(
        python_command(
            ".gstack/scripts/nontechnical_execution_plan.py",
            *build_common_args(args, output_format="user"),
        )
    )
    return GuidedKickoffResult(
        raw_request=args.raw,
        stage="execution-plan",
        helper_entry="nontechnical_execution_plan.user",
        helper_status=status,
        needs_user_confirmation=bool(readiness_json.get("needs_user_confirmation")),
        user_response=output,
    )


def render_json(result: GuidedKickoffResult) -> str:
    return json.dumps(asdict(result), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", default="", help="User's plain-language request. Omit to print the guided template.")
    parser.add_argument("--audience", default="", help="Optional target user or usage context.")
    parser.add_argument("--success", default="", help="Optional visible success criteria.")
    parser.add_argument("--non-goal", default="", help="Optional explicit non-goals or forbidden scope.")
    parser.add_argument("--risk-confirmation", default="", help="Optional user confirmation that constrains high-risk actions.")
    parser.add_argument("--topic", default="guided-kickoff-preview", help="Optional formal kickoff preview topic.")
    parser.add_argument(
        "--formal",
        action="store_true",
        help="Show a read-only formal kickoff preview when the request is complete enough.",
    )
    parser.add_argument(
        "--ai-reviewed",
        action="store_true",
        help="Allow the formal preview to say Codex has semantically reviewed the request; still read-only.",
    )
    parser.add_argument("--format", choices=("user", "json"), default="user")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = render_guided_user(args)
    if args.format == "json":
        print(render_json(result))
    else:
        print(result.user_response)
    return 0 if result.helper_status == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
