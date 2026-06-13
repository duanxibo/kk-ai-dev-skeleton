#!/usr/bin/env python3
"""检查本地 KK Dev Skeleton gstack 协作状态。

doctor 默认保守运行。`check` 只报告状态；`fix` 只更新已 gitignore 的本地运行文件，
例如 CURRENT.local.md。
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
import sys
from dataclasses import dataclass, asdict
from pathlib import Path

from adapter_runtime import ADAPTER_ENV, ADAPTER_RUNTIME_ENV, load_adapter_runtime


REPO_ROOT = Path(__file__).resolve().parents[2]
BOUNDARY_DIR = REPO_ROOT / ".gstack" / "task-boundaries"
LOCAL_POINTER = BOUNDARY_DIR / "CURRENT.local.md"
SHARED_POINTER = BOUNDARY_DIR / "CURRENT.md"
ACTIVE_BOUNDARY_ENV = "KK_ACTIVE_BOUNDARY"
CODEX_MODE_FILE = REPO_ROOT / ".gstack" / "codex-mode.local.md"
GIT_HOOKS_DIR = REPO_ROOT / ".githooks"
REQUIRED_HOOKS = ("pre-commit", "pre-push")
REQUIRED_SKILLS = (
    "kk-task-kickoff",
    "kk-natural-language-dev",
    "kk-codex-mode",
    "kk-doc-sync",
    "kk-doc-lifecycle",
    "kk-doc-backfill",
    "kk-data-kickoff",
    "kk-data-query",
    "kk-subagent-orchestrator",
)
REQUIRED_SCRIPTS = (
    "adapter_runtime.py",
    "spec_sync_guard.py",
    "team_flow_guard.py",
    "required_gates_audit.py",
    "rule_manager.py",
    "autopilot_bootstrap.py",
    "codex_mode.py",
    "gstack_dashboard.py",
    "nontechnical_intake.py",
    "nontechnical_task_starter.py",
    "natural_language_dev_smoke.py",
)
REQUIRED_CORE_DOCS = (
    "AGENTS.md",
    "README.md",
    "QUICK_START_FOR_PARTNERS.md",
    "COMPANY_ADOPTION_GUIDE.md",
    "CODEX_ADOPTION_CONNECTOR.md",
    ".gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md",
    ".gstack/README.md",
    ".gstack/knowledge/CODEMAP.md",
    ".gstack/knowledge/doc-placement.md",
    ".gstack/knowledge/context-isolation.md",
    ".gstack/knowledge/ai-programming-framework.md",
    ".gstack/knowledge/implementation-guide.md",
    ".gstack/knowledge/qa-dimensions.md",
    ".gstack/knowledge/data-access/README.md",
    ".gstack/knowledge/data-access/source-registry.md",
    ".gstack/knowledge/data-access/query-access-guide.md",
    ".gstack/entrypoints/product-manager.md",
    ".gstack/entrypoints/engineer.md",
    ".gstack/task-boundaries/CURRENT.md",
    "adapters/default/adapter.md",
    "adapters/default/runtime.json",
    "plugins/PARTNER_INSTALL.md",
    "plugins/MARKETPLACE_INSTALL.md",
    "plugins/ADMIN_INSTALL_CHECKLIST.md",
    "scripts/setup_local_codex.sh",
    "blueprint/README.md",
    "archive/README.md",
    "archive/baseline/README.md",
    "shared/README.md",
)
CONTEXT_RISK_PARENT_PATTERNS = ("tian" + "gong",)
EXTERNAL_SKILL_PREFIXES = ("tg-",)


@dataclass(frozen=True)
class CheckResult:
    check_id: str
    status: str
    message: str
    details: list[str]
    fixable: bool = False


@dataclass(frozen=True)
class PointerState:
    source: str | None
    href: str | None
    resolved_boundary: str | None
    canonical: bool
    warnings: list[str]
    failures: list[str]


def repo_relative(path: Path) -> str:
    return path.resolve().relative_to(REPO_ROOT).as_posix()


def display_path(path: Path) -> str:
    try:
        return repo_relative(path)
    except ValueError:
        return path.as_posix()


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def pointer_text(boundary: Path) -> str:
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


def parse_active_links(pointer: Path) -> list[str]:
    if not pointer.exists():
        return []
    active_links: list[str] = []
    in_active_section = False
    for line in pointer.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped == "## Active Boundary":
            in_active_section = True
            continue
        if in_active_section and stripped.startswith("## "):
            break
        if not in_active_section:
            continue
        open_paren = stripped.find("](")
        close_paren = stripped.find(")", open_paren + 2)
        if open_paren >= 0 and close_paren > open_paren:
            active_links.append(stripped[open_paren + 2 : close_paren])
    return active_links


def concrete_boundary_files() -> list[Path]:
    excluded = {"CURRENT.md", "CURRENT.local.md", "README.md"}
    return sorted(
        path
        for path in BOUNDARY_DIR.glob("*.md")
        if path.name not in excluded and path.is_file()
    )


def resolve_boundary_reference(raw_ref: str, pointer: Path | None) -> tuple[Path | None, list[str]]:
    raw_ref = raw_ref.strip()
    if not raw_ref:
        return None, ["active boundary 链接为空"]

    raw = Path(raw_ref)
    candidates: list[Path] = []
    if raw.is_absolute():
        candidates.append(raw)
    else:
        if pointer is not None:
            candidates.append(pointer.parent / raw)
        candidates.append(REPO_ROOT / raw)
        candidates.append(BOUNDARY_DIR / raw)
        candidates.append(BOUNDARY_DIR / raw.name)

    for candidate in candidates:
        resolved = candidate.resolve()
        try:
            relative = resolved.relative_to(REPO_ROOT).as_posix()
        except ValueError:
            continue
        if relative.startswith(".gstack/task-boundaries/") and resolved.exists():
            if resolved.name in {"CURRENT.md", "CURRENT.local.md", "README.md"}:
                return None, ["active boundary 必须指向具体 boundary 文件"]
            return resolved, []

    rendered = ", ".join(
        candidate.resolve().as_posix()
        for candidate in candidates[:4]
    )
    return None, [f"active boundary 目标不存在；尝试过: {rendered}"]


def inspect_pointer() -> PointerState:
    env_value = os.environ.get(ACTIVE_BOUNDARY_ENV, "").strip()
    if env_value:
        boundary, failures = resolve_boundary_reference(env_value, None)
        return PointerState(
            source=f"env:{ACTIVE_BOUNDARY_ENV}",
            href=env_value,
            resolved_boundary=repo_relative(boundary) if boundary else None,
            canonical=True,
            warnings=[],
            failures=failures,
        )

    pointer = LOCAL_POINTER if LOCAL_POINTER.exists() else SHARED_POINTER
    source = repo_relative(pointer)
    if not pointer.exists():
        return PointerState(
            source=None,
            href=None,
            resolved_boundary=None,
            canonical=False,
            warnings=["未找到本地 active boundary 指针"],
            failures=[],
        )

    links = parse_active_links(pointer)
    if pointer == SHARED_POINTER and not links:
        return PointerState(
            source=source,
            href=None,
            resolved_boundary=None,
            canonical=False,
            warnings=["未找到本地 active boundary 指针"],
            failures=[],
        )
    if len(links) != 1:
        return PointerState(
            source=source,
            href=None,
            resolved_boundary=None,
            canonical=False,
            warnings=[],
            failures=[f"{source} 必须且只能声明一个 active boundary 链接"],
        )

    href = links[0]
    boundary, failures = resolve_boundary_reference(href, pointer)
    if failures or boundary is None:
        return PointerState(
            source=source,
            href=href,
            resolved_boundary=None,
            canonical=False,
            warnings=[],
            failures=failures,
        )

    warnings: list[str] = []
    if pointer == SHARED_POINTER:
        warnings.append("正在使用共享 CURRENT.md；建议使用本地 CURRENT.local.md")
    canonical = href == boundary.name and pointer == LOCAL_POINTER
    if not canonical:
        warnings.append("active boundary 指针可规范化为本地 basename 链接")

    return PointerState(
        source=source,
        href=href,
        resolved_boundary=repo_relative(boundary),
        canonical=canonical,
        warnings=warnings,
        failures=[],
    )


def check_active_boundary() -> CheckResult:
    state = inspect_pointer()
    details: list[str] = []
    if state.source:
        details.append(f"来源: {state.source}")
    if state.href:
        details.append(f"链接: {state.href}")
    if state.resolved_boundary:
        details.append(f"解析结果: {state.resolved_boundary}")
    details.extend(state.warnings)
    details.extend(state.failures)

    if state.failures:
        return CheckResult(
            "active-boundary",
            "fail",
            "当前任务入口无效。",
            details,
            fixable=True,
        )
    if not state.resolved_boundary:
        return CheckResult(
            "active-boundary",
            "warn",
            "尚未设置当前任务入口。",
            details,
            fixable=bool(concrete_boundary_files()),
        )
    if state.warnings:
        return CheckResult(
            "active-boundary",
            "warn",
            "当前任务入口可用，但建议规范化。",
            details,
            fixable=True,
        )
    return CheckResult(
        "active-boundary",
        "ok",
        "当前任务入口已设置。",
        details,
        fixable=False,
    )


def check_codex_mode() -> CheckResult:
    command = [sys.executable, ".gstack/scripts/codex_mode.py", "show", "--format", "json"]
    result = run(command)
    details = [f"command: {' '.join(command)}"]
    if result.returncode != 0:
        details.append(result.stderr.strip() or result.stdout.strip())
        return CheckResult("codex-mode", "fail", "协作模式 helper 运行失败。", details)
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        details.append(result.stdout.strip())
        return CheckResult("codex-mode", "fail", "协作模式 helper 返回了无效 JSON。", details)
    details.append(f"模式: {payload.get('mode')} ({payload.get('internal_enum')})")
    details.append(f"来源: {payload.get('source')}")
    details.append(f"本机模式文件存在: {CODEX_MODE_FILE.exists()}")
    return CheckResult("codex-mode", "ok", "协作模式已解析。", details)


def check_git_hooks() -> CheckResult:
    repo_check = run(["git", "rev-parse", "--is-inside-work-tree"])
    if repo_check.returncode != 0:
        return CheckResult(
            "git-hooks",
            "warn",
            "当前目录还不是 git worktree，暂不检查 git hooks。",
            ["初始化或克隆为 git 仓库后，再运行本检查"],
        )
    result = run(["git", "config", "core.hooksPath"])
    hooks_path = result.stdout.strip()
    details = [f"core.hooksPath: {hooks_path or '<unset>'}"]
    failures: list[str] = []
    warnings: list[str] = []
    if hooks_path != ".githooks":
        failures.append("core.hooksPath 不是 `.githooks`")
    for hook in REQUIRED_HOOKS:
        hook_path = GIT_HOOKS_DIR / hook
        if not hook_path.exists():
            failures.append(f"缺少 hook: .githooks/{hook}")
        elif not os.access(hook_path, os.X_OK):
            warnings.append(f"hook 不可执行: .githooks/{hook}")
    details.extend(warnings)
    details.extend(failures)
    if failures:
        return CheckResult("git-hooks", "warn", "仓库管理的 git hooks 尚未安装。", details)
    if warnings:
        return CheckResult("git-hooks", "warn", "仓库管理的 git hooks 已存在，但有提醒。", details)
    return CheckResult("git-hooks", "ok", "仓库管理的 git hooks 已安装。", details)


def check_skills() -> CheckResult:
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    skills_home = codex_home / "skills"
    details = [f"skills 目录: {skills_home}"]
    missing: list[str] = []
    stale: list[str] = []
    for skill in REQUIRED_SKILLS:
        source = (REPO_ROOT / ".gstack" / "skills" / skill).resolve()
        target = skills_home / skill
        if not target.exists():
            missing.append(skill)
            continue
        if target.is_symlink():
            try:
                actual = target.resolve()
            except OSError:
                stale.append(skill)
                continue
            if actual != source:
                stale.append(f"{skill} -> {actual}")
        else:
            stale.append(f"{skill} 已存在但不是 symlink")
    if missing:
        details.append("缺失: " + ", ".join(missing))
    if stale:
        details.append("过期: " + ", ".join(stale))
    if missing or stale:
        details.append("修复命令: bash .gstack/scripts/sync_repo_skills.sh")
        return CheckResult("skills", "warn", "repo-native skills 尚未完全同步。", details)
    return CheckResult("skills", "ok", "repo-native skills 已同步。", details)


def check_context_isolation() -> CheckResult:
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    skills_home = codex_home / "skills"
    details: list[str] = []
    warnings: list[str] = []

    parent_parts = [part.lower() for part in REPO_ROOT.parts[:-1]]
    risky_parts = sorted(
        {
            part
            for part in parent_parts
            for pattern in CONTEXT_RISK_PARENT_PATTERNS
            if pattern in part
        }
    )
    if risky_parts:
        details.append(
            "父目录命名提示: "
            + ", ".join(risky_parts)
            + "；仅作提醒，不作为项目身份来源。"
        )

    external_skills: list[str] = []
    kept_nonlinks: list[str] = []
    for prefix in EXTERNAL_SKILL_PREFIXES:
        for target in sorted(skills_home.glob(f"{prefix}*")):
            if target.is_symlink():
                try:
                    resolved = target.resolve()
                except OSError:
                    resolved = Path("<broken>")
                external_skills.append(f"{target.name} -> {resolved}")
            elif target.exists():
                kept_nonlinks.append(target.name)

    if external_skills:
        warnings.append("检测到外部项目 skill symlink；它们不属于当前 kk-* 骨架。")
        details.append("外部 skill symlink:")
        details.extend(f"  - {item}" for item in external_skills[:12])
        if len(external_skills) > 12:
            details.append(f"  - ... 另有 {len(external_skills) - 12} 个")
        details.append("如已不再需要，可运行: bash .gstack/scripts/sync_repo_skills.sh --remove-tg-links")

    if kept_nonlinks:
        warnings.append("检测到外部项目 skill 普通目录；doctor 不会自动处理。")
        details.append("外部 skill 普通目录: " + ", ".join(kept_nonlinks[:12]))

    if warnings:
        details = [*warnings, *details]
        return CheckResult(
            "context-isolation",
            "warn",
            "检测到可能导致串味的外部上下文线索。",
            details,
        )

    return CheckResult(
        "context-isolation",
        "ok",
        "未发现会改变当前项目身份的外部 skill 污染线索。",
        [
            *details,
            "项目身份应继续以当前仓库、adapter、boundary 和用户输入为准。",
        ],
    )


def check_scripts() -> CheckResult:
    details: list[str] = []
    failures: list[str] = []
    for script in REQUIRED_SCRIPTS:
        path = REPO_ROOT / ".gstack" / "scripts" / script
        if not path.exists():
            failures.append(f"缺失: .gstack/scripts/{script}")
            continue
        mode = path.stat().st_mode
        if path.suffix == ".py" and not (mode & stat.S_IXUSR):
            details.append(f"不可直接执行，但可用 python3 运行: .gstack/scripts/{script}")
    if failures:
        details.extend(failures)
        return CheckResult("scripts", "fail", "缺少必要协作脚本。", details)
    return CheckResult("scripts", "ok", "必要协作脚本已存在。", details)


def check_core_docs() -> CheckResult:
    missing: list[str] = []
    for doc in REQUIRED_CORE_DOCS:
        if not (REPO_ROOT / doc).exists():
            missing.append(doc)
    if missing:
        return CheckResult(
            "core-docs",
            "fail",
            "核心协作文档存在断链。",
            [f"缺失: {doc}" for doc in missing],
        )
    return CheckResult(
        "core-docs",
        "ok",
        "核心协作文档已存在。",
        [f"已检查 {len(REQUIRED_CORE_DOCS)} 个入口文档"],
    )


def check_adapter_runtime() -> CheckResult:
    try:
        runtime = load_adapter_runtime(REPO_ROOT, strict=False)
    except RuntimeError as exc:
        return CheckResult(
            "adapter-runtime",
            "fail",
            "adapter runtime 无法加载。",
            [str(exc)],
        )

    details = [
        f"adapter: {runtime.adapter_name}",
        f"{ADAPTER_ENV}: {os.environ.get(ADAPTER_ENV, '<unset>')}",
        f"{ADAPTER_RUNTIME_ENV}: {os.environ.get(ADAPTER_RUNTIME_ENV, '<unset>')}",
        f"runtime: {display_path(runtime.runtime_file)}",
        f"implementation prefixes: {len(runtime.path_tuple('implementation_prefixes'))}",
        f"spec prefixes: {len(runtime.path_tuple('spec_prefixes'))}",
        f"data-access trigger prefixes: {len(runtime.path_tuple('data_access_trigger_prefixes'))}",
    ]
    if runtime.warnings:
        details.extend(runtime.warnings)
        return CheckResult(
            "adapter-runtime",
            "fail" if not runtime.exists else "warn",
            "adapter runtime 存在问题。",
            details,
        )
    return CheckResult(
        "adapter-runtime",
        "ok",
        "adapter runtime 已加载。",
        details,
    )


def check_dev_stack_entry() -> CheckResult:
    runtime = load_adapter_runtime(REPO_ROOT, strict=False)
    entry = str(runtime.command_value("dev_stack_entry", "") or "").strip()
    if not entry:
        return CheckResult(
            "dev-stack-entry",
            "ok",
            "当前 adapter 未声明本地开发环境启动入口。",
            ["adapter commands.dev_stack_entry 为空"],
        )
    path = REPO_ROOT / entry
    if not path.exists():
        return CheckResult(
            "dev-stack-entry",
            "warn",
            "缺少本地开发环境启动入口。",
            [f"期望路径: {entry}", *runtime.warnings],
        )
    executable = os.access(path, os.X_OK)
    details = [f"脚本: {repo_relative(path)}", f"可执行: {executable}"]
    return CheckResult(
        "dev-stack-entry",
        "ok" if executable else "warn",
        "本地开发环境启动入口已存在。",
        details,
    )


def run_checks() -> list[CheckResult]:
    return [
        check_active_boundary(),
        check_codex_mode(),
        check_git_hooks(),
        check_skills(),
        check_context_isolation(),
        check_scripts(),
        check_core_docs(),
        check_adapter_runtime(),
        check_dev_stack_entry(),
    ]


def status_rank(status: str) -> int:
    return {"ok": 0, "warn": 1, "fail": 2}.get(status, 2)


def overall_status(results: list[CheckResult]) -> str:
    worst = max((status_rank(result.status) for result in results), default=0)
    return ["ok", "warn", "fail"][worst]


def human_check_label(check_id: str) -> str:
    labels = {
        "active-boundary": "当前任务入口",
        "codex-mode": "协作模式",
        "git-hooks": "提交前本地检查",
        "skills": "Codex 技能同步",
        "context-isolation": "上下文隔离",
        "scripts": "协作脚本",
        "core-docs": "核心协作文档",
        "adapter-runtime": "项目适配器运行配置",
        "dev-stack-entry": "开发环境启动入口",
    }
    return labels.get(check_id, check_id)


def human_result_text(result: CheckResult) -> str:
    status = result.status
    check_id = result.check_id
    if check_id == "active-boundary":
        if status == "ok":
            return "正常，Codex 知道当前应该按哪份任务记录继续。"
        if status == "warn":
            return "可用但需要整理，Codex 可以先在本地修正任务入口。"
        return "无效，Codex 需要先恢复当前任务入口；如果本地有多个候选任务，才需要你确认要继续哪一个。"
    if check_id == "codex-mode":
        if status == "ok":
            return "正常，Codex 可以按当前协作模式推进。"
        return "读取失败，Codex 需要先修复本地协作模式 helper。"
    if check_id == "git-hooks":
        if status == "ok":
            return "正常，本地提交前检查已经接上。"
        if status == "warn":
            return "基本存在但有可执行权限等小问题，Codex 可以先整理本机配置。"
        return "未接好，Codex 可以修复本机提交前检查；这不会自动提交代码。"
    if check_id == "skills":
        if status == "ok":
            return "正常，repo-native skills 已同步到本机 Codex。"
        return "没有完全同步，Codex 可以运行同步脚本补齐本机 skill 链接。"
    if check_id == "context-isolation":
        if status == "ok":
            return "正常，当前没有会改变项目身份的外部 skill 污染线索。"
        return "有串味风险；Codex 必须只按当前仓库、adapter、boundary 和用户输入判断项目身份。"
    if check_id == "scripts":
        if status == "ok":
            return "正常，必须的协作脚本都在。"
        return "缺少必要脚本，需要先修复仓库里的协作脚本文件。"
    if check_id == "core-docs":
        if status == "ok":
            return "正常，skill 和工作流依赖的核心文档都在。"
        return "核心文档有断链，需要先补齐或修正引用。"
    if check_id == "adapter-runtime":
        if status == "ok":
            return "正常，guard 和 doctor 可以从当前 adapter 读取路径、命令和 gate 规则。"
        if status == "warn":
            return "adapter runtime 可用但有提醒，需要确认路径或配置是否符合当前项目。"
        return "adapter runtime 缺失或不可解析，需要先补齐。"
    if check_id == "dev-stack-entry":
        if status == "ok":
            return "正常，完整开发环境有统一启动入口。"
        return "启动入口缺失或不可执行；如果要启动完整业务环境，需要先补齐。"
    if status == "ok":
        return "正常。"
    if status == "warn":
        return "有提醒，需要 Codex 先确认是否影响当前任务。"
    return "有问题，需要 Codex 先处理。"


def human_next_step(result: CheckResult) -> str:
    if result.check_id == "active-boundary" and result.fixable:
        return "Codex 可修正本地任务入口。"
    if result.check_id == "git-hooks":
        return "Codex 可整理本机提交前检查配置；不会执行代码提交流程或切分支。"
    if result.check_id == "skills":
        return "Codex 可同步本机工作流技能链接。"
    if result.check_id == "context-isolation":
        detail_text = "\n".join(result.details)
        has_symlink = "外部 skill symlink" in detail_text
        has_nonlink = "普通目录" in detail_text
        if has_symlink and has_nonlink:
            return "Codex 可清理外部 skill symlink；普通目录需要用户确认后人工处理。父目录名只作为提醒。"
        if has_symlink:
            return "Codex 可清理外部 skill symlink；父目录名只作为提醒，不应影响项目身份判断。"
        if has_nonlink:
            return "检测到外部 skill 普通目录；doctor 不会自动删除，需用户确认后人工处理。父目录名只作为提醒。"
        return "父目录名只作为提醒，不应影响项目身份判断。"
    if result.check_id == "scripts":
        return "Codex 需要检查缺失的协作脚本，并在仓库内补齐。"
    if result.check_id == "core-docs":
        return "Codex 需要补齐缺失文档，或把引用改到 adapter / example 提供的路径。"
    if result.check_id == "adapter-runtime":
        return "Codex 需要补齐 `adapters/<name>/runtime.json`，或修正 `KK_ADAPTER` / `KK_ADAPTER_RUNTIME`。"
    if result.check_id == "dev-stack-entry":
        return "如果当前任务要启动完整环境，Codex 需要检查项目适配器里的启动入口。"
    if result.check_id == "codex-mode":
        return "Codex 需要检查协作模式 helper 和本机模式文件。"
    return "Codex 需要先阅读该项检查结果，再决定本地修复步骤。"


def render_explanation(results: list[CheckResult]) -> str:
    status = overall_status(results)
    problem_results = [result for result in results if result.status != "ok"]
    lines = ["# 出错后怎么继续", ""]

    if status == "ok":
        lines.append("当前本地协作状态正常，可以继续开发。")
    elif status == "warn":
        lines.append("当前本地协作状态基本可用，但有几项需要 Codex 先整理。")
    else:
        lines.append("当前本地协作状态有阻塞项，Codex 需要先处理这些问题，再继续正式开发。")

    lines.extend(
        [
            "",
            "## 你现在需要做什么",
            "",
        ]
    )
    if status == "ok":
        lines.append("- 暂时不需要你做技术操作。Codex 可以继续按当前任务推进。")
    else:
        lines.append("- 先不用你读日志或运行命令，Codex 会优先处理本地可证明的问题。")
    lines.append("- 只有涉及业务判断、真实数据、生产环境、数据库变更、破坏性命令或代码提交流程时，Codex 才会停下来问你。")

    lines.extend(["", "## 当前状态摘要", ""])
    for result in results:
        lines.append(f"- {human_check_label(result.check_id)}：{human_result_text(result)}")

    lines.extend(["", "## Codex 的下一步", ""])
    if problem_results:
        for result in problem_results:
            lines.append(f"- {human_check_label(result.check_id)}：{human_next_step(result)}")
    else:
        lines.append("- 继续当前任务；如果后续检查失败，先定位问题，再补齐本地证据或低风险配置。")

    lines.extend(
        [
            "",
            "## 什么时候需要你确认",
            "",
            "- 当前没有必须由你确认的业务问题。",
            "- 如果需要选择产品口径、使用真实数据、操作生产环境、改数据库、执行破坏性命令或代码提交流程，Codex 会单独问你。",
        ]
    )
    return "\n".join(lines)


def render_markdown(results: list[CheckResult]) -> str:
    lines = ["# gstack doctor", ""]
    for result in results:
        badge = {"ok": "通过", "warn": "提醒", "fail": "失败"}.get(result.status, result.status)
        lines.append(f"- [{badge}] `{result.check_id}`: {result.message}")
        for detail in result.details:
            lines.append(f"  - {detail}")
        if result.fixable:
            lines.append("  - 可自动修复: yes")
    lines.append("")
    lines.append(f"总体状态: `{overall_status(results)}`")
    return "\n".join(lines)


def render_json(results: list[CheckResult]) -> str:
    payload = {
        "overall": overall_status(results),
        "results": [asdict(result) for result in results],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def print_results(results: list[CheckResult], *, output_format: str) -> None:
    if output_format == "json":
        print(render_json(results))
    else:
        print(render_markdown(results))


def resolve_requested_boundary(raw: str | None) -> Path | None:
    if not raw:
        state = inspect_pointer()
        if state.resolved_boundary:
            return REPO_ROOT / state.resolved_boundary
        return None
    boundary, failures = resolve_boundary_reference(raw, None)
    if failures:
        raise SystemExit("; ".join(failures))
    return boundary


def fix_active_boundary(raw_boundary: str | None) -> CheckResult:
    target = resolve_requested_boundary(raw_boundary)
    if target is None:
        choices = [repo_relative(path) for path in concrete_boundary_files()[-5:]]
        details = ["没有解析出可用 boundary 目标"]
        if choices:
            details.append("最近候选: " + ", ".join(choices))
        return CheckResult(
            "fix-active-boundary",
            "fail",
            "没有可解析目标，无法修复 active boundary。",
            details,
        )
    LOCAL_POINTER.write_text(pointer_text(target), encoding="utf-8")
    return CheckResult(
        "fix-active-boundary",
        "ok",
        "已规范化本地 active boundary 指针。",
        [f"目标: {repo_relative(target)}", f"指针: {repo_relative(LOCAL_POINTER)}"],
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="检查本地 gstack 状态。")
    check.add_argument("--format", choices=("markdown", "json"), default="markdown")

    subparsers.add_parser("explain", help="用中文解释本地 gstack 状态。")

    fix = subparsers.add_parser("fix", help="修复低风险本地 gstack 状态。")
    fix.add_argument("--format", choices=("markdown", "json"), default="markdown")
    fix.add_argument(
        "--active-boundary",
        action="store_true",
        help="规范化 .gstack/task-boundaries/CURRENT.local.md。",
    )
    fix.add_argument(
        "--boundary",
        help="当 --active-boundary 无法推断时，指定要启用的 boundary 文件。",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "check":
        results = run_checks()
        print_results(results, output_format=args.format)
        return 1 if any(result.status == "fail" for result in results) else 0

    if args.command == "explain":
        results = run_checks()
        print(render_explanation(results))
        return 1 if any(result.status == "fail" for result in results) else 0

    if args.command == "fix":
        results: list[CheckResult] = []
        if args.active_boundary:
            results.append(fix_active_boundary(args.boundary))
        else:
            parser.error("fix 至少需要一个目标，例如 --active-boundary")
        results.extend(run_checks())
        print_results(results, output_format=args.format)
        return 1 if any(result.status == "fail" for result in results) else 0

    parser.error("未处理的命令")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
