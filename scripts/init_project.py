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
    "archive/README.md",
    "archive/baseline/README.md",
    "blueprint/README.md",
    "blueprint/00_阅读入口.md",
    "shared/README.md",
    ".gstack/designs/README.md",
    ".gstack/migrations/README.md",
)
STACK_TEMPLATE_ROOT = "stack/default/"
ROOT_CODE_CANDIDATES = (
    "src",
    "app",
    "prisma",
    "e2e",
    "apps",
    "packages",
    "services",
    "backend",
    "frontend",
    "package.json",
    "pnpm-lock.yaml",
    "package-lock.json",
    "yarn.lock",
    "next.config.js",
    "next.config.mjs",
    "next.config.ts",
    "vite.config.js",
    "vite.config.ts",
    "vitest.config.js",
    "vitest.config.ts",
    "playwright.config.js",
    "playwright.config.ts",
    "docker-compose.yml",
    "docker-compose.yaml",
)
WORKSPACE_LAYER_FILES = {
    "archive/README.md": """# Archive

`archive/` 是历史归档层，只用于追溯旧原型、旧实现、旧规格、废弃方案或历史迁移快照。

不要把 `archive/` 当默认实现来源。采纳历史材料前，先在 requirement、review、task boundary 或当前 stack spec 中说明采纳项和放弃项。
""",
    "archive/baseline/README.md": """# Baseline Archive

`archive/baseline/` 保存历史原型、旧 demo、旧页面行为、旧 mock、旧 fixture 或 baseline snapshot。

公共骨架不提供真实 baseline 内容。真实项目如需保留旧原型，应放入自己的脱敏或授权材料。
""",
    "blueprint/README.md": """# Blueprint

`blueprint/` 是前置蓝图层，用于记录系统初始构想、核心对象、设计原则、阶段演进和关键取舍。

蓝图不替代当前 stack spec；被采纳的内容必须同步到 `stack/<project>/specs/`、adapter 或 `.gstack/` evidence。
""",
    "blueprint/00_阅读入口.md": """# Blueprint 阅读入口

从这里开始阅读项目蓝图。

`blueprint/` 可以帮助澄清方向，但不替代当前 stack spec。
""",
    "blueprint/topic.template.md": """# Blueprint Topic

- 主题：
- 日期：
- 状态：`draft / active / superseded / archived`
- 负责人：

## 背景

## 初始判断

## 待验证问题

## 采纳出口
""",
    "shared/README.md": """# Shared

`shared/` 存放跨模块或跨阶段复用的共享输入、脱敏 fixtures 和中间产物。

不要默认放真实客户数据、生产导出、密钥、未脱敏 Excel / CSV。
""",
    ".gstack/designs/README.md": """# Designs

`.gstack/designs/` 存放 repo-native 设计过程产物，例如工程设计草案、架构调整计划和原型逻辑抽取设计。

正式产品 / API / 数据 / UI 真源应进入 `stack/<project>/specs/` 或 adapter。
""",
    ".gstack/migrations/README.md": """# Migrations

`.gstack/migrations/` 存放 repo-native 迁移计划和迁移记录。

迁移计划应说明来源、目标、允许改动、禁止改动、验证方式、回滚方式和剩余风险。
""",
}
WORKSPACE_LAYER_KEEP_DIRS = (
    "shared/raw-inputs",
    "shared/fixtures",
    "shared/generated",
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
    stack_dir: Path
    created: bool
    replaced: bool
    stack_created: bool
    root_code_paths: tuple[str, ...]
    message: str


@dataclass(frozen=True)
class UpgradeApplyResult:
    adapter: str
    adapter_dir: Path
    stack_dir: Path
    applied: bool
    blocked: bool
    stack_created: bool
    root_code_paths: tuple[str, ...]
    message: str


def slugify(raw: str) -> str:
    value = raw.strip().lower()
    value = re.sub(r"[^a-z0-9._\-\s]+", "-", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-.")
    return value or "project"


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def rewrite_stack_template_paths(value: Any, name: str) -> Any:
    if isinstance(value, dict):
        return {key: rewrite_stack_template_paths(item, name) for key, item in value.items()}
    if isinstance(value, list):
        return [rewrite_stack_template_paths(item, name) for item in value]
    if isinstance(value, str):
        return value.replace(STACK_TEMPLATE_ROOT, f"stack/{name}/")
    return value


def stack_dir_for(name: str) -> Path:
    return REPO_ROOT / "stack" / name


def root_code_paths() -> tuple[str, ...]:
    return tuple(
        candidate for candidate in ROOT_CODE_CANDIDATES if (REPO_ROOT / candidate).exists()
    )


def write_text_if_missing(relative_path: str, content: str) -> bool:
    path = REPO_ROOT / relative_path
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
    return True


def ensure_workspace_layers() -> tuple[str, ...]:
    created: list[str] = []
    for relative_path, content in WORKSPACE_LAYER_FILES.items():
        if write_text_if_missing(relative_path, content):
            created.append(relative_path)
    for relative_dir in WORKSPACE_LAYER_KEEP_DIRS:
        path = REPO_ROOT / relative_dir
        path.mkdir(parents=True, exist_ok=True)
        keep = path / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")
            created.append(f"{relative_dir}/.gitkeep")
    return tuple(created)


def collect_strings(value: Any) -> list[str]:
    if isinstance(value, dict):
        strings: list[str] = []
        for item in value.values():
            strings.extend(collect_strings(item))
        return strings
    if isinstance(value, list):
        strings = []
        for item in value:
            strings.extend(collect_strings(item))
        return strings
    if isinstance(value, str):
        return [value]
    return []


def inspect_runtime_stack_alignment(adapter: str) -> tuple[bool | None, str | None]:
    runtime_path = REPO_ROOT / "adapters" / adapter / "runtime.json"
    if not runtime_path.exists():
        return None, "runtime.json missing"
    try:
        payload = json.loads(runtime_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return False, f"runtime.json invalid: {exc}"

    stack_prefix = f"stack/{adapter}/"
    return any(stack_prefix in item for item in collect_strings(payload)), None


def ensure_stack_layout(name: str) -> tuple[Path, bool]:
    stack_dir = stack_dir_for(name)
    created = not stack_dir.exists()
    stack_dir.mkdir(parents=True, exist_ok=True)

    readme = stack_dir / "README.md"
    if not readme.exists():
        readme.write_text(
            "\n".join(
                [
                    f"# {name} Stack",
                    "",
                    "这个目录是当前项目的应用真源层。",
                    "",
                    "- `specs/`: 产品、接口、数据、UI 和测试口径。",
                    "- `src/`: 应用源码。",
                    "- `tests/`: 应用级测试。",
                    "- `fixtures/`: 脱敏 fixtures 和示例数据。",
                    "- `scripts/`: 项目专属脚本。",
                    "",
                    "初始化不会自动移动已有根目录代码。若项目已有 `src/`、`prisma/`、"
                    "`e2e/` 或根目录配置文件，请让 Codex 先生成迁移计划，再分步迁入本目录。",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    specs_dir = stack_dir / "specs"
    specs_dir.mkdir(parents=True, exist_ok=True)
    specs_readme = specs_dir / "README.md"
    if not specs_readme.exists():
        specs_readme.write_text(
            "\n".join(
                [
                    f"# {name} Specs",
                    "",
                    "这里沉淀当前项目的产品语义、接口契约、数据模型、UI 行为和测试口径。",
                    "",
                ]
            ),
            encoding="utf-8",
        )

    for child in ("src", "tests", "fixtures", "scripts"):
        child_dir = stack_dir / child
        child_dir.mkdir(parents=True, exist_ok=True)
        keep = child_dir / ".gitkeep"
        if not keep.exists():
            keep.write_text("", encoding="utf-8")

    return stack_dir, created


def update_runtime_name(adapter_dir: Path, name: str) -> None:
    runtime_path = adapter_dir / "runtime.json"
    if not runtime_path.exists():
        return
    payload = json.loads(runtime_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise RuntimeError(f"{repo_relative(runtime_path)} must contain a JSON object")
    payload = rewrite_stack_template_paths(payload, name)
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
    ensure_workspace_layers()
    stack_dir, stack_created = ensure_stack_layout(name)
    candidates = root_code_paths()
    if target.exists() and not force:
        return ApplyResult(
            adapter_dir=target,
            stack_dir=stack_dir,
            created=False,
            replaced=False,
            stack_created=stack_created,
            root_code_paths=candidates,
            message=(
                f"Adapter already exists: {repo_relative(target)}. "
                f"默认不会覆盖；已确保 stack layout: {repo_relative(stack_dir)}。"
                "如需替换必须显式传 --force。"
            ),
        )

    replaced = target.exists()
    adapter_dir = create_adapter(name, force=force)
    return ApplyResult(
        adapter_dir=adapter_dir,
        stack_dir=stack_dir,
        created=not replaced,
        replaced=replaced,
        stack_created=stack_created,
        root_code_paths=candidates,
        message=(
            f"已{'替换' if replaced else '创建'} adapter: {repo_relative(adapter_dir)}；"
            f"已确保 stack layout: {repo_relative(stack_dir)}"
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
    stack_dir = stack_dir_for(adapter)
    runtime_stack_aligned, runtime_stack_alignment_error = inspect_runtime_stack_alignment(
        adapter
    )
    core_present = [path for path in CORE_REQUIRED_PATHS if (REPO_ROOT / path).exists()]
    core_missing = [path for path in CORE_REQUIRED_PATHS if not (REPO_ROOT / path).exists()]
    return {
        "repo_root": REPO_ROOT.as_posix(),
        "adapter": adapter,
        "adapter_dir": repo_relative(adapter_dir),
        "adapter_exists": adapter_dir.exists(),
        "adapter_md_exists": (adapter_dir / "adapter.md").exists(),
        "runtime_json_exists": (adapter_dir / "runtime.json").exists(),
        "runtime_stack_aligned": runtime_stack_aligned,
        "runtime_stack_alignment_error": runtime_stack_alignment_error,
        "default_adapter_exists": DEFAULT_ADAPTER.exists(),
        "active_boundary": read_active_boundary(),
        "git_worktree": is_git_worktree(),
        "stack_dir": repo_relative(stack_dir),
        "stack_dir_exists": stack_dir.exists(),
        "stack_specs_exists": (stack_dir / "specs").exists(),
        "stack_src_exists": (stack_dir / "src").exists(),
        "workspace_layers": {
            "archive": (REPO_ROOT / "archive" / "README.md").exists(),
            "archive_baseline": (
                REPO_ROOT / "archive" / "baseline" / "README.md"
            ).exists(),
            "blueprint": (REPO_ROOT / "blueprint" / "README.md").exists(),
            "shared": (REPO_ROOT / "shared" / "README.md").exists(),
            "gstack_designs": (REPO_ROOT / ".gstack" / "designs" / "README.md").exists(),
            "gstack_migrations": (
                REPO_ROOT / ".gstack" / "migrations" / "README.md"
            ).exists(),
        },
        "root_code_paths": list(root_code_paths()),
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

    if state.get("stack_dir_exists"):
        steps.append(f"保留现有 {state['stack_dir']}，后续新代码默认进入该 stack 目录。")
    else:
        steps.append(f"创建 {state['stack_dir']}，作为应用源码、spec、测试和 fixtures 的默认真源目录。")

    root_paths = state.get("root_code_paths") or []
    if root_paths:
        joined = "、".join(f"`{path}`" for path in root_paths)
        steps.append(
            f"检测到根目录已有代码或配置：{joined}。不自动移动；先让 Codex 生成迁移计划，再分步迁入 stack。"
        )

    missing_layers = [
        name for name, exists in state.get("workspace_layers", {}).items() if not exists
    ]
    if missing_layers:
        steps.append(
            "补齐公共 workspace layers：`blueprint/`、`archive/`、`shared/`、"
            "`.gstack/designs/` 和 `.gstack/migrations/`。"
        )
    else:
        steps.append("公共 workspace layers 已具备。")

    steps.extend(
        [
            "让 Codex 根据用户自然语言补全 adapter 里的项目目标、路径、命令和风险规则。",
            "把 adapter runtime 的实现、spec 和测试前缀改为 `stack/<project>/...`，根目录旧路径只作为迁移候选。",
            "运行 doctor、spec sync guard、team flow guard、Required Gates audit 和 natural language smoke。",
            "生成接入总结：已完成项、缺失项、风险和第一个低风险试点任务。",
        ]
    )
    return steps


def plan_project_upgrade(adapter: str, state: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []

    if state["core_missing"]:
        items.append(
            {
                "id": "framework-core-files",
                "status": "planned",
                "safe_apply": False,
                "title": "同步 framework core 文件",
                "detail": (
                    "当前仓库缺少部分 framework core 文件。需要先生成文件级 diff / 合并计划；"
                    "不要新建项目，也不要全量覆盖已有项目。"
                ),
            }
        )
    else:
        items.append(
            {
                "id": "framework-core-files",
                "status": "done",
                "safe_apply": False,
                "title": "framework core 文件已具备",
                "detail": "当前仓库具备骨架核心入口文件。",
            }
        )

    if not state["adapter_exists"]:
        items.append(
            {
                "id": "project-adapter",
                "status": "blocked",
                "safe_apply": False,
                "title": "当前项目还没有 adapter",
                "detail": (
                    "这不是已有项目升级场景；请先走首次接入计划。"
                    "不要把升级流程当作重新初始化。"
                ),
            }
        )
    elif not state["adapter_md_exists"] or not state["runtime_json_exists"]:
        items.append(
            {
                "id": "project-adapter",
                "status": "planned",
                "safe_apply": False,
                "title": "修复 adapter 缺失文件",
                "detail": "保留现有 adapter 内容，补齐缺失的 adapter.md 或 runtime.json 前先生成合并计划。",
            }
        )
    else:
        items.append(
            {
                "id": "project-adapter",
                "status": "done",
                "safe_apply": False,
                "title": "保留现有 adapter",
                "detail": f"已检测到 adapters/{adapter}，升级流程不会默认覆盖。",
            }
        )

    stack_ready = (
        state["stack_dir_exists"]
        and state["stack_specs_exists"]
        and state["stack_src_exists"]
    )
    if stack_ready:
        items.append(
            {
                "id": "stack-layout",
                "status": "done",
                "safe_apply": True,
                "title": "stack layout 已存在",
                "detail": f"{state['stack_dir']} 已具备 specs/src 基础目录。",
            }
        )
    else:
        items.append(
            {
                "id": "stack-layout",
                "status": "planned",
                "safe_apply": True,
                "title": "创建缺失的 stack layout",
                "detail": (
                    f"可安全创建 {state['stack_dir']} 及 specs/src/tests/fixtures/scripts；"
                    "不会移动已有业务代码。"
                ),
                "command": f"python3 scripts/init_project.py --adapter {adapter} --upgrade-apply",
            }
        )

    if state["runtime_stack_aligned"] is True:
        items.append(
            {
                "id": "adapter-runtime-stack-routing",
                "status": "done",
                "safe_apply": False,
                "title": "adapter runtime 已包含 stack 路由",
                "detail": f"runtime.json 已引用 stack/{adapter}/。",
            }
        )
    elif state["runtime_stack_aligned"] is False:
        items.append(
            {
                "id": "adapter-runtime-stack-routing",
                "status": "planned",
                "safe_apply": False,
                "title": "检查 adapter runtime 路由",
                "detail": (
                    "runtime.json 尚未引用当前 stack 路径，或文件不可解析。"
                    "需要 Codex 生成合并计划，不自动覆盖项目 adapter。"
                ),
            }
        )
    else:
        items.append(
            {
                "id": "adapter-runtime-stack-routing",
                "status": "blocked",
                "safe_apply": False,
                "title": "无法检查 adapter runtime 路由",
                "detail": state["runtime_stack_alignment_error"] or "runtime 状态未知。",
            }
        )

    root_paths = state.get("root_code_paths") or []
    if root_paths:
        items.append(
            {
                "id": "root-code-migration",
                "status": "planned",
                "safe_apply": False,
                "title": "生成根目录代码迁移计划",
                "detail": (
                    "检测到根目录代码或配置："
                    + "、".join(f"`{path}`" for path in root_paths)
                    + "。升级流程不会自动移动；应先生成迁移计划。"
                ),
            }
        )
    else:
        items.append(
            {
                "id": "root-code-migration",
                "status": "done",
                "safe_apply": False,
                "title": "未发现根目录迁移候选",
                "detail": "当前没有检测到需要迁移复核的常见根目录代码路径。",
            }
        )

    items.append(
        {
            "id": "plugin-update-reminder",
            "status": "done",
            "safe_apply": False,
            "title": "插件更新提醒已由插件自身提供",
            "detail": "该能力随插件更新生效，不需要修改目标项目。",
        }
    )
    return items


def apply_project_upgrade(adapter: str) -> UpgradeApplyResult:
    state = detect_project(adapter)
    adapter_dir = REPO_ROOT / "adapters" / adapter
    stack_dir = stack_dir_for(adapter)
    candidates = root_code_paths()

    if not state["adapter_exists"]:
        return UpgradeApplyResult(
            adapter=adapter,
            adapter_dir=adapter_dir,
            stack_dir=stack_dir,
            applied=False,
            blocked=True,
            stack_created=False,
            root_code_paths=candidates,
            message=(
                f"未发现 adapters/{adapter}。这是首次接入缺口，不是已有项目升级；"
                "请先生成接入计划。"
            ),
        )

    ensure_workspace_layers()
    stack_dir, stack_created = ensure_stack_layout(adapter)
    message = (
        f"已安全确保 {repo_relative(stack_dir)} layout。"
        "未覆盖 adapter，未移动根目录业务代码。"
    )
    if candidates:
        message += " 已检测到根目录迁移候选，请继续生成迁移计划。"

    return UpgradeApplyResult(
        adapter=adapter,
        adapter_dir=adapter_dir,
        stack_dir=stack_dir,
        applied=True,
        blocked=False,
        stack_created=stack_created,
        root_code_paths=candidates,
        message=message,
    )


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
            f"3. 将后续应用代码、spec、测试和 fixtures 默认放入 `stack/{adapter}/`；已有根目录代码先生成迁移计划，不自动搬迁。",
            "4. 让 Codex 运行内部接入验证：`python3 scripts/init_project.py --adapter "
            f"{adapter} --verify --report`。",
            "5. 把自然语言接入提示发给使用者；脚本由 Codex 在后台调用。",
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
            f"- stack dir: `{state['stack_dir']}`",
            f"- stack dir exists: `{str(state['stack_dir_exists']).lower()}`",
            f"- stack specs exists: `{str(state['stack_specs_exists']).lower()}`",
            f"- stack src exists: `{str(state['stack_src_exists']).lower()}`",
            "- workspace layers:",
            *[
                f"  - {name}: `{str(exists).lower()}`"
                for name, exists in state["workspace_layers"].items()
            ],
            f"- root code path count: `{len(state['root_code_paths'])}`",
            f"- core missing count: `{len(missing)}`",
    ]
    if state["root_code_paths"]:
        lines.append("- root code paths needing migration review:")
        lines.extend(f"  - `{path}`" for path in state["root_code_paths"])
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


def render_upgrade_plan(adapter: str, state: dict[str, Any]) -> str:
    items = plan_project_upgrade(adapter, state)
    lines = [
        "已有项目增量升级计划",
        "",
        f"- adapter: `{adapter}`",
        f"- stack dir: `{state['stack_dir']}`",
        "- 原则：不新建项目、不重新接入、不默认覆盖 adapter、不自动移动业务代码。",
        "",
        "升级项：",
    ]
    for index, item in enumerate(items, 1):
        safe = "yes" if item["safe_apply"] else "no"
        lines.extend(
            [
                f"{index}. {item['title']}",
                f"   - id: `{item['id']}`",
                f"   - status: `{item['status']}`",
                f"   - safe apply: `{safe}`",
                f"   - detail: {item['detail']}",
            ]
        )
        if item.get("command"):
            lines.append(f"   - command: `{item['command']}`")
    return "\n".join(lines)


def render_apply_result(result: ApplyResult) -> str:
    lines = [
        "接入应用结果",
        "",
        f"- adapter dir: `{repo_relative(result.adapter_dir)}`",
        f"- stack dir: `{repo_relative(result.stack_dir)}`",
        f"- created: `{str(result.created).lower()}`",
        f"- replaced: `{str(result.replaced).lower()}`",
        f"- stack created: `{str(result.stack_created).lower()}`",
        f"- message: {result.message}",
    ]
    if result.root_code_paths:
        lines.extend(
            [
                "- migration candidates:",
                *[f"  - `{path}`" for path in result.root_code_paths],
            ]
        )
    return "\n".join(lines)


def render_upgrade_apply_result(result: UpgradeApplyResult) -> str:
    lines = [
        "已有项目安全升级结果",
        "",
        f"- adapter: `{result.adapter}`",
        f"- adapter dir: `{repo_relative(result.adapter_dir)}`",
        f"- stack dir: `{repo_relative(result.stack_dir)}`",
        f"- applied: `{str(result.applied).lower()}`",
        f"- blocked: `{str(result.blocked).lower()}`",
        f"- stack created: `{str(result.stack_created).lower()}`",
        f"- message: {result.message}",
    ]
    if result.root_code_paths:
        lines.extend(
            [
                "- migration candidates:",
                *[f"  - `{path}`" for path in result.root_code_paths],
            ]
        )
    return "\n".join(lines)


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
    upgrade_plan: list[dict[str, Any]] | None = None,
    upgrade_result: UpgradeApplyResult | None = None,
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
    if upgrade_plan is not None:
        lines.extend(["", render_upgrade_plan(adapter, state)])
    if upgrade_result is not None:
        lines.extend(["", render_upgrade_apply_result(upgrade_result)])
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
        "--upgrade-plan",
        action="store_true",
        help="Render an incremental upgrade plan for an already adopted project without writing files.",
    )
    parser.add_argument(
        "--upgrade-apply",
        action="store_true",
        help="Apply safe incremental upgrades for an already adopted project. Never overwrites adapters or moves app code.",
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
        (
            args.detect,
            args.plan,
            args.apply,
            args.upgrade_plan,
            args.upgrade_apply,
            args.verify,
            args.report,
        )
    )

    apply_result: ApplyResult | None = None
    upgrade_result: UpgradeApplyResult | None = None
    verification_results: list[CommandRun] | None = None

    if args.apply:
        apply_result = apply_adapter(adapter, force=args.force)
        adapter_dir = apply_result.adapter_dir
    elif args.upgrade_apply:
        upgrade_result = apply_project_upgrade(adapter)
        adapter_dir = upgrade_result.adapter_dir
    elif args.create_adapter:
        ensure_workspace_layers()
        stack_dir, stack_created = ensure_stack_layout(adapter)
        candidates = root_code_paths()
        adapter_dir = create_adapter(adapter, force=args.force)
        apply_result = ApplyResult(
            adapter_dir=adapter_dir,
            stack_dir=stack_dir,
            created=True,
            replaced=args.force,
            stack_created=stack_created,
            root_code_paths=candidates,
            message=(
                f"已创建 adapter: {repo_relative(adapter_dir)}；"
                f"已确保 stack layout: {repo_relative(stack_dir)}"
            ),
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
        if args.upgrade_plan or args.upgrade_apply or args.report:
            payload["upgrade_plan"] = plan_project_upgrade(adapter, state)
        if apply_result is not None:
            payload["apply"] = {
                "adapter_dir": repo_relative(apply_result.adapter_dir),
                "stack_dir": repo_relative(apply_result.stack_dir),
                "created": apply_result.created,
                "replaced": apply_result.replaced,
                "stack_created": apply_result.stack_created,
                "root_code_paths": list(apply_result.root_code_paths),
                "message": apply_result.message,
            }
        if upgrade_result is not None:
            payload["upgrade_apply"] = {
                "adapter": upgrade_result.adapter,
                "adapter_dir": repo_relative(upgrade_result.adapter_dir),
                "stack_dir": repo_relative(upgrade_result.stack_dir),
                "applied": upgrade_result.applied,
                "blocked": upgrade_result.blocked,
                "stack_created": upgrade_result.stack_created,
                "root_code_paths": list(upgrade_result.root_code_paths),
                "message": upgrade_result.message,
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
                upgrade_plan=plan_project_upgrade(adapter, state)
                if args.upgrade_plan or args.upgrade_apply
                else None,
                upgrade_result=upgrade_result,
                verification_results=verification_results,
            )
        )
    else:
        if args.detect:
            output_blocks.append(render_detection(state))
        if args.plan:
            output_blocks.append(render_plan(adapter, state))
        if args.upgrade_plan:
            output_blocks.append(render_upgrade_plan(adapter, state))
        if apply_result is not None:
            output_blocks.append(render_apply_result(apply_result))
        if upgrade_result is not None:
            output_blocks.append(render_upgrade_apply_result(upgrade_result))
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
