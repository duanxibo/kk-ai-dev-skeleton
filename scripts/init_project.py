#!/usr/bin/env python3
"""Codex-facing project adoption helper for KK Dev Skeleton.

Business users should start adoption by asking Codex in natural language.
This script is the deterministic execution layer Codex can call behind that
conversation: detect, plan, apply, verify, and report.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ADAPTER = REPO_ROOT / "adapters" / "default"
ACTIVE_BOUNDARY = REPO_ROOT / ".gstack" / "task-boundaries" / "CURRENT.local.md"
CORE_REQUIRED_PATHS = (
    "AGENTS.md",
    "README.md",
    "COMPANY_ADOPTION_GUIDE.md",
    "CODEX_ADOPTION_CONNECTOR.md",
    ".gstack/README.md",
    ".gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md",
    ".gstack/scripts/gstack_doctor.py",
    ".gstack/scripts/spec_sync_guard.py",
    ".gstack/scripts/team_flow_guard.py",
    ".gstack/scripts/required_gates_audit.py",
    ".gstack/scripts/natural_language_dev_smoke.py",
    "scripts/init_project.py",
    "scripts/dev_stack.sh",
    "adapters/default/adapter.md",
    "adapters/default/runtime.json",
)


@dataclass(frozen=True)
class CommandRun:
    name: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


@dataclass(frozen=True)
class ApplyResult:
    adapter_dir: Path
    created: bool
    replaced: bool
    message: str


def slugify(raw: str) -> str:
    value = raw.strip().lower()
    value = re.sub(r"[^a-z0-9._\-\s]+", "-", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-.")
    return value or "project"


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def update_runtime_name(adapter_dir: Path, name: str) -> None:
    runtime_path = adapter_dir / "runtime.json"
    if not runtime_path.exists():
        return
    payload = json.loads(runtime_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{repo_relative(runtime_path)} must contain a JSON object")
    payload["name"] = name
    payload["description"] = (
        f"{name} 项目的机器可读 adapter runtime。请按真实项目路径、命令和 gate 规则改写。"
    )
    runtime_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def create_adapter(name: str, *, force: bool) -> Path:
    target = REPO_ROOT / "adapters" / name
    if target.exists():
        if not force:
            raise SystemExit(
                f"Adapter already exists: {repo_relative(target)}. Use --force to replace it."
            )
        shutil.rmtree(target)
    shutil.copytree(DEFAULT_ADAPTER, target)
    update_runtime_name(target, name)
    return target


def apply_adapter(name: str, *, force: bool) -> ApplyResult:
    target = REPO_ROOT / "adapters" / name
    if target.exists() and not force:
        return ApplyResult(
            adapter_dir=target,
            created=False,
            replaced=False,
            message=(
                f"Adapter already exists: {repo_relative(target)}. "
                "默认不会覆盖；如需替换必须显式传 --force。"
            ),
        )

    replaced = target.exists()
    adapter_dir = create_adapter(name, force=force)
    return ApplyResult(
        adapter_dir=adapter_dir,
        created=not replaced,
        replaced=replaced,
        message=(
            f"已{'替换' if replaced else '创建'} adapter: {repo_relative(adapter_dir)}"
        ),
    )


def read_active_boundary() -> str | None:
    if not ACTIVE_BOUNDARY.exists():
        return None
    for line in ACTIVE_BOUNDARY.read_text(encoding="utf-8").splitlines():
        match = re.search(r"\]\(([^)]+)\)", line)
        if match:
            return f".gstack/task-boundaries/{match.group(1)}"
    return None


def is_git_worktree() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def detect_project(adapter: str) -> dict[str, Any]:
    adapter_dir = REPO_ROOT / "adapters" / adapter
    core_present = [path for path in CORE_REQUIRED_PATHS if (REPO_ROOT / path).exists()]
    core_missing = [path for path in CORE_REQUIRED_PATHS if not (REPO_ROOT / path).exists()]
    return {
        "repo_root": REPO_ROOT.as_posix(),
        "adapter": adapter,
        "adapter_dir": repo_relative(adapter_dir),
        "adapter_exists": adapter_dir.exists(),
        "adapter_md_exists": (adapter_dir / "adapter.md").exists(),
        "runtime_json_exists": (adapter_dir / "runtime.json").exists(),
        "default_adapter_exists": DEFAULT_ADAPTER.exists(),
        "active_boundary": read_active_boundary(),
        "git_worktree": is_git_worktree(),
        "core_present": core_present,
        "core_missing": core_missing,
    }


def plan_adoption(state: dict[str, Any]) -> list[str]:
    steps: list[str] = []
    if state["core_missing"]:
        steps.append("补齐缺失的 framework core 文件。")
    else:
        steps.append("framework core 文件已具备。")

    if not state["adapter_exists"]:
        steps.append(
            f"创建 adapters/{state['adapter']}，从 adapters/default 复制 adapter 模板。"
        )
    elif not state["adapter_md_exists"] or not state["runtime_json_exists"]:
        steps.append("修复 adapter 缺失文件，确保 adapter.md 和 runtime.json 同时存在。")
    else:
        steps.append(f"保留现有 adapters/{state['adapter']}，不默认覆盖。")

    steps.extend(
        [
            "让 Codex 根据用户自然语言补全 adapter 里的项目目标、路径、命令和风险规则。",
            "运行 doctor、spec sync guard、team flow guard、Required Gates audit 和 natural language smoke。",
            "生成接入总结：已完成项、缺失项、风险和第一个低风险试点任务。",
        ]
    )
    return steps


def verify_commands(boundary: str | None = None) -> list[tuple[str, list[str]]]:
    active_boundary = boundary or read_active_boundary()
    commands: list[tuple[str, list[str]]] = [
        ("doctor", [sys.executable, ".gstack/scripts/gstack_doctor.py", "check"]),
        ("spec-sync", [sys.executable, ".gstack/scripts/spec_sync_guard.py"]),
        (
            "team-flow",
            [
                sys.executable,
                ".gstack/scripts/team_flow_guard.py",
                "--mode",
                "audit",
                "--base",
                "HEAD",
            ],
        ),
        ("required-gates", [sys.executable, ".gstack/scripts/required_gates_audit.py"]),
        (
            "natural-language-smoke",
            [sys.executable, ".gstack/scripts/natural_language_dev_smoke.py"],
        ),
    ]
    if active_boundary:
        commands[3][1].extend(["--boundary", active_boundary])
    return commands


def run_command(name: str, command: list[str], *, adapter: str) -> CommandRun:
    env = {**os.environ, "KK_ADAPTER": adapter}
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    return CommandRun(
        name=name,
        command=command,
        returncode=result.returncode,
        stdout=result.stdout,
        stderr=result.stderr,
    )


def run_verification(adapter: str, *, boundary: str | None = None) -> list[CommandRun]:
    return [
        run_command(name, command, adapter=adapter)
        for name, command in verify_commands(boundary)
    ]


def run_doctor(adapter: str) -> int:
    result = run_command(
        "doctor",
        [sys.executable, ".gstack/scripts/gstack_doctor.py", "check"],
        adapter=adapter,
    )
    print_command_run(result)
    return result.returncode


def render_next_steps(adapter: str, adapter_dir: Path) -> str:
    return "\n".join(
        [
            "初始化完成。",
            "",
            "下一步：",
            f"1. 修改 `{repo_relative(adapter_dir / 'adapter.md')}`，写入项目目标、真源路径、命令和风险规则。",
            f"2. 修改 `{repo_relative(adapter_dir / 'runtime.json')}`，写入机器可读的 paths / commands / gates。",
            "3. 让 Codex 运行内部接入验证：`python3 scripts/init_project.py --adapter "
            f"{adapter} --verify --report`。",
            "4. 把自然语言接入提示发给使用者；脚本由 Codex 在后台调用。",
        ]
    )


def render_detection(state: dict[str, Any]) -> str:
    missing = state["core_missing"]
    lines = [
        "接入状态检测",
        "",
        f"- repo root: `{state['repo_root']}`",
        f"- adapter: `{state['adapter']}`",
        f"- adapter dir: `{state['adapter_dir']}`",
        f"- adapter exists: `{str(state['adapter_exists']).lower()}`",
        f"- adapter.md exists: `{str(state['adapter_md_exists']).lower()}`",
        f"- runtime.json exists: `{str(state['runtime_json_exists']).lower()}`",
        f"- default adapter exists: `{str(state['default_adapter_exists']).lower()}`",
        f"- active boundary: `{state['active_boundary'] or 'not-found'}`",
        f"- git worktree: `{str(state['git_worktree']).lower()}`",
        f"- core missing count: `{len(missing)}`",
    ]
    if missing:
        lines.append("- core missing:")
        lines.extend(f"  - `{path}`" for path in missing)
    return "\n".join(lines)


def render_plan(adapter: str, state: dict[str, Any]) -> str:
    lines = [
        "接入计划",
        "",
        f"- adapter: `{adapter}`",
        "- 用户入口：对 Codex 说自然语言接入请求。",
        "- 执行方式：Codex 调用内部 helper；业务用户不手动执行脚本。",
        "",
        "步骤：",
    ]
    lines.extend(f"{index}. {step}" for index, step in enumerate(plan_adoption(state), 1))
    return "\n".join(lines)


def render_apply_result(result: ApplyResult) -> str:
    return "\n".join(
        [
            "接入应用结果",
            "",
            f"- adapter dir: `{repo_relative(result.adapter_dir)}`",
            f"- created: `{str(result.created).lower()}`",
            f"- replaced: `{str(result.replaced).lower()}`",
            f"- message: {result.message}",
        ]
    )


def render_verification(results: list[CommandRun]) -> str:
    lines = ["接入验证结果", ""]
    for item in results:
        status = "pass" if item.ok else "fail"
        command = " ".join(item.command)
        lines.extend(
            [
                f"- {item.name}: `{status}`",
                f"  command: `{command}`",
                f"  exit: `{item.returncode}`",
            ]
        )
        if item.stdout.strip():
            first_line = item.stdout.strip().splitlines()[0]
            lines.append(f"  stdout: {first_line}")
        if item.stderr.strip():
            first_line = item.stderr.strip().splitlines()[0]
            lines.append(f"  stderr: {first_line}")
    return "\n".join(lines)


def render_report(
    adapter: str,
    state: dict[str, Any],
    *,
    apply_result: ApplyResult | None = None,
    verification_results: list[CommandRun] | None = None,
) -> str:
    lines = [
        "KK Dev Skeleton 接入报告",
        "",
        render_detection(state),
        "",
        render_plan(adapter, state),
    ]
    if apply_result is not None:
        lines.extend(["", render_apply_result(apply_result)])
    if verification_results is not None:
        lines.extend(["", render_verification(verification_results)])
    lines.extend(
        [
            "",
            "建议的第一个低风险试点任务：",
            "- 让 Codex 修改一处非核心文档说明，并生成 requirement、review、boundary 和 QA evidence。",
        ]
    )
    return "\n".join(lines)


def print_command_run(result: CommandRun) -> None:
    if result.stdout:
        print(result.stdout.rstrip())
    if result.stderr:
        print(result.stderr.rstrip(), file=sys.stderr)


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--adapter",
        default="default",
        help="Adapter name under adapters/. Use a short ASCII slug.",
    )
    parser.add_argument(
        "--create-adapter",
        action="store_true",
        help="Copy adapters/default to adapters/<adapter> if it does not exist.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing adapter when used with --create-adapter.",
    )
    parser.add_argument(
        "--run-doctor",
        action="store_true",
        help="Run gstack doctor after adapter initialization.",
    )
    parser.add_argument(
        "--detect",
        action="store_true",
        help="Detect current adoption state without writing files.",
    )
    parser.add_argument(
        "--plan",
        action="store_true",
        help="Render a Codex-facing adoption plan without writing files.",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply safe adoption changes. Creates the adapter if missing; does not overwrite without --force.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run the adoption verification chain.",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Render a combined adoption report.",
    )
    parser.add_argument(
        "--boundary",
        default="",
        help="Optional concrete task boundary path for Required Gates audit.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format for detect/plan/apply/verify/report.",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    adapter = slugify(args.adapter)
    adapter_dir = REPO_ROOT / "adapters" / adapter
    has_v1_action = any(
        (args.detect, args.plan, args.apply, args.verify, args.report)
    )

    apply_result: ApplyResult | None = None
    verification_results: list[CommandRun] | None = None

    if args.apply:
        apply_result = apply_adapter(adapter, force=args.force)
        adapter_dir = apply_result.adapter_dir
    elif args.create_adapter:
        adapter_dir = create_adapter(adapter, force=args.force)
        apply_result = ApplyResult(
            adapter_dir=adapter_dir,
            created=True,
            replaced=args.force,
            message=f"已创建 adapter: {repo_relative(adapter_dir)}",
        )

    if not has_v1_action and not adapter_dir.exists():
        raise SystemExit(
            f"Adapter does not exist: {repo_relative(adapter_dir)}. "
            "Use --create-adapter to create it from adapters/default."
        )

    if args.verify:
        verification_results = run_verification(
            adapter,
            boundary=args.boundary.strip() or None,
        )

    state = detect_project(adapter)
    output_blocks: list[str] = []

    if args.format == "json":
        payload: dict[str, Any] = {
            "adapter": adapter,
            "state": state,
        }
        if args.plan or args.report:
            payload["plan"] = plan_adoption(state)
        if apply_result is not None:
            payload["apply"] = {
                "adapter_dir": repo_relative(apply_result.adapter_dir),
                "created": apply_result.created,
                "replaced": apply_result.replaced,
                "message": apply_result.message,
            }
        if verification_results is not None:
            payload["verification"] = [
                {
                    "name": item.name,
                    "command": item.command,
                    "returncode": item.returncode,
                    "ok": item.ok,
                    "stdout": item.stdout,
                    "stderr": item.stderr,
                }
                for item in verification_results
            ]
        print_json(payload)
    elif args.report:
        print(
            render_report(
                adapter,
                state,
                apply_result=apply_result,
                verification_results=verification_results,
            )
        )
    else:
        if args.detect:
            output_blocks.append(render_detection(state))
        if args.plan:
            output_blocks.append(render_plan(adapter, state))
        if apply_result is not None:
            output_blocks.append(render_apply_result(apply_result))
        if verification_results is not None:
            output_blocks.append(render_verification(verification_results))

        if output_blocks:
            print("\n\n".join(output_blocks))
        elif not has_v1_action:
            print(render_next_steps(adapter, adapter_dir))

    if args.run_doctor:
        doctor_status = run_doctor(adapter)
        if doctor_status != 0:
            return doctor_status

    if verification_results and any(not item.ok for item in verification_results):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
