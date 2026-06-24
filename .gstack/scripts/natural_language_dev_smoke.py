#!/usr/bin/env python3
"""Smoke test the nontechnical natural-language development journey.

This script checks deterministic repo-native helpers only. It does not create
formal evidence, connect to data sources, open browsers, or run git actions.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
ACTIVE_BOUNDARY_ENV = "KK_ACTIVE_BOUNDARY"

ACTIVE_TASK_FIXTURE = """# Task Boundary: Natural Language Smoke Active Task

- Task: natural-language-smoke-active-task
- Owner: smoke

## Decision Mode

- Mode: autonomous

## Flow Lane

- Lane: fast-lane

## Subagent Plan

- Mode: review
- Reason:
  Smoke fixture includes an independent review surface.

## GStack Required Flow

- requirement-brief:
  status: done
- plan-ceo-review:
  status: done
- requirement-freeze:
  status: done
- plan-eng-review:
  status: done
- domain-spec-readiness:
  status: not-required
- implement:
  status: planned
- qa:
  status: planned
"""

COMPLETED_TASK_FIXTURE = """# Task Boundary: Natural Language Smoke Completed Task

- Task: natural-language-smoke-completed-task
- Owner: smoke

## Decision Mode

- Mode: autonomous

## Flow Lane

- Lane: fast-lane

## Subagent Plan

- Mode: review
- Reason:
  Smoke fixture includes an independent review surface.

## User-visible Acceptance

### Expected Visible Behavior

- 已完成当前低风险体验修复。
- 下一项低风险体验修复可以继续推进，不需要用户再次回复继续。

### User Actions To Verify

- 查看交付总结，确认下一步建议不会变成暂停点。

## Functional Non-goals

- 不触碰真实数据、生产、数据库或代码提交流程。

## GStack Required Flow

- requirement-brief:
  status: done
- plan-ceo-review:
  status: done
- requirement-freeze:
  status: done
- plan-eng-review:
  status: done
- domain-spec-readiness:
  status: not-required
- implement:
  status: done
- qa:
  status: done
"""


@dataclass(frozen=True)
class SmokeResult:
    check_id: str
    status: str
    message: str
    details: list[str]


USER_CHECK_LABELS: dict[str, str] = {
    "broad-intake": "需求还很模糊时，会先问一个最关键的问题",
    "complex-intake": "复杂需求会先拆成可交付步骤",
    "small-intake": "明确的小需求可以快速进入实现准备",
    "high-risk-intake": "真实数据、线上环境或数据库相关需求会暂停确认",
    "risk-confirmed-intake": "带安全约束的风险确认可以进入受控起点整理",
    "dashboard-explain": "当前进度说明对非技术用户可读",
    "dashboard-verify": "完成后的验收方式对非技术用户可读",
    "doctor-explain": "出错后的恢复说明对非技术用户可读",
    "complex-task-starter": "复杂需求可以生成开发起点预览",
    "risky-task-starter": "高风险任务不会直接生成可执行起点",
    "complex-task-starter-user-format": "复杂需求的起始说明会隐藏工程术语",
    "complex-task-starter-acceptance-json": "复杂需求会沉淀可验收清单",
    "risky-task-starter-user-format": "高风险暂停说明对用户可读",
    "risk-confirmed-task-starter": "风险受控确认能生成开发起点预览",
    "risk-confirmed-task-starter-user-format": "风险受控确认会说明不会触碰的高风险动作",
    "risk-insufficient-task-starter": "含糊确认不会被当成授权",
    "forbidden-scope-mapping": "明确禁止的业务范围会被识别",
    "forbidden-scope-user-format": "禁止范围会用人话说明并隐藏路径",
    "smoke-user-format": "关键路径检查结果能用人话输出",
    "intent-router-json": "非技术用户原话能被路由到正确入口",
    "intent-router-user-format": "路由结果能用人话输出",
    "next-step-json": "非技术用户原话能生成正确下一步",
    "next-step-user-format": "下一步说明能直接给用户看",
    "execution-plan-json": "复杂需求能生成用户可读执行计划并包含 subagent 策略",
    "execution-plan-user-format": "执行计划说明能直接给用户看，并说明 Codex 分工策略",
    "task-breakdown-json": "拆任务 / 里程碑请求会生成阶段计划",
    "task-breakdown-user-format": "任务拆解说明能直接给用户看",
    "first-use-json": "第一次使用项目骨架会得到新手路径",
    "first-use-user-format": "新手路径说明能直接给用户看",
    "requirement-brief-json": "需求模板请求会生成通用信息卡",
    "requirement-brief-user-format": "通用需求信息卡能直接给用户看",
    "requirement-readiness-json": "需求完整度请求会生成缺失信息检查",
    "requirement-readiness-user-format": "需求完整度检查能直接给用户看",
    "page-change-brief-json": "改已有页面前会得到信息收集卡",
    "page-change-brief-user-format": "页面改动信息卡能直接给用户看",
    "ui-optimization-autoguard": "UI 优化短句会自动进入 UI 质量链路",
    "acceptance-plan-json": "复杂需求能生成需求级验收计划",
    "acceptance-plan-user-format": "需求级验收计划能直接给用户看",
    "visible-change-json": "刷新后看不到变化会进入可见变化排查",
    "visible-change-user-format": "可见变化排查说明能直接给用户看",
    "ci-failure-json": "CI / GitHub 检查失败会进入 CI 失败解释",
    "ci-failure-user-format": "CI 失败解释能直接给用户看",
    "continue-runner-json": "继续推进会读取当前任务并连续推进低风险本地步骤",
    "continue-runner-completed-autochain-json": "已完成低风险任务会自动串联下一段低风险任务",
    "continue-runner-user-format": "继续推进说明能直接给用户看，且不要求用户每步说继续",
    "mode-control-json": "协作模式表达会进入模式控制",
    "mode-control-user-format": "协作模式说明能直接给用户看",
    "recommendation-json": "用户不懂技术时会得到推荐方案",
    "recommendation-user-format": "推荐方案说明能直接给用户看",
    "scope-change-json": "需求范围调整会进入范围说明",
    "scope-change-user-format": "需求范围调整说明能直接给用户看",
    "team-sync-json": "无数据库团队同步会先说明能力边界",
    "team-sync-user-format": "团队同步说明能直接给用户看",
    "delivery-summary-json": "完成说明会生成团队可读交付总结",
    "delivery-summary-autonomy-json": "完成说明的下一步建议不会强制用户再说继续",
    "delivery-summary-user-format": "交付总结说明能直接给用户看",
    "task-list-json": "未完成任务请求会生成任务概览",
    "task-list-user-format": "任务概览说明能直接给用户看",
    "home-json": "打开项目后可以看到非技术开发首页",
    "home-user-format": "开发首页能直接给用户看",
    "implementation-readiness-json": "正式开工后能看到是否可开始实现",
    "implementation-readiness-user-format": "实现就绪说明能直接给用户看",
    "confirmation-brief-json": "当前确认事项能生成可读说明",
    "confirmation-brief-user-format": "确认事项说明能直接给用户看",
    "confirmation-response-json": "模糊确认会允许低风险继续，同时不授权高风险动作",
    "confirmation-response-user-format": "确认回复说明能直接给用户看",
    "pause-control-json": "暂停当前推进能生成可读说明",
    "pause-control-user-format": "暂停说明能直接给用户看",
    "undo-request-json": "撤销请求会先要求确认范围",
    "undo-request-user-format": "撤销请求说明能直接给用户看",
    "formal-kickoff-json": "复杂需求能预览正式开工包",
    "formal-kickoff-user-format": "正式开工包说明能直接给用户看",
    "guided-kickoff-template": "复杂需求向导能给出照填模板",
    "guided-kickoff-plan": "复杂需求向导能给出执行计划",
    "guided-kickoff-formal-json": "复杂需求向导能给出正式开工预览",
}

USER_COVERAGE_LINES = [
    "提需求太模糊时，会先问一个关键问题。",
    "复杂需求会先拆步骤，并先固定验收口径。",
    "明确的小需求可以快速进入实现准备。",
    "涉及真实数据、线上环境、数据库或代码提交流程时会暂停确认。",
    "只允许整理范围和验收口径的风险确认，可以受控进入开发起点。",
    "当前进度、完成后怎么验收、出错后怎么继续，都有可读说明。",
    "用户明确禁止的业务范围会被识别并避开。",
    "常见用户原话会先路由到正确入口。",
    "常见用户原话能直接生成下一步说明。",
    "用户询问怎么推进时，会看到阶段、确认点和验收方式。",
    "用户询问某个具体需求怎么验收时，会看到验收清单、实际操作和预期结果。",
    "用户刷新页面但看不到变化时，会得到查看位置、刷新方式和排查步骤。",
    "用户说 CI 或 GitHub 检查失败时，会得到失败检查类型和下一步排查说明。",
    "用户只说继续做、按计划推进或先做第一步时，会继续当前任务而不是重新追问，并且不会每一步都等用户再说继续。",
    "低风险任务完成后，如果下一项仍是本地可验证低风险任务，会自动进入下一段任务记录并继续推进。",
    "用户说先别改代码、关键地方问我或全自动做完时，会先解释协作模式。",
    "用户不懂技术或不想选技术方案时，会看到推荐方案和第一安全步。",
    "用户要求拆任务、排优先级、里程碑或每阶段验收时，会看到阶段计划和阶段验收方式。",
    "用户第一次使用项目骨架或不会写代码时，会看到从想法到开工的新手路径。",
    "用户不知道怎么描述复杂需求或询问开工前需要哪些信息时，会看到可照填的通用需求信息卡。",
    "用户填完需求后问还缺什么或够不够开工时，会看到需求完整度检查和优先补充项。",
    "用户问改已有页面该给什么信息时，会看到页面位置、当前问题、期望变化、验收方式和不碰范围的照填清单。",
    "用户只说进行 UI 优化时，会自动进入 UI 设计梳理、实现、视觉复核和浏览器验收链路。",
    "用户调整需求范围时，会看到保留、排除和后续范围，而不是重新追问。",
    "用户要求先做原型、能点的 demo、静态页面或不接接口版本时，会按原型优先范围处理。",
    "用户提出团队状态同步但不要数据库时，会看到无数据库路线的能力边界和确认问题。",
    "用户要给团队看的完成说明时，会看到交付总结、验收方式、风险、未做事项和下一步建议。",
    "用户要求查看未完成任务、历史需求或任务清单时，会看到只读任务概览。",
    "用户通过 Codex 打开项目后，可以看到当前任务、可选动作、复杂需求模板、验收方式和恢复方式。",
    "用户问能否开始实现时，会看到已完成准备、缺失准备、Codex 下一步和是否需要确认。",
    "用户问现在需要确认什么时，会看到确认事项、可直接回复的话和 Codex 下一步。",
    "用户只回复我确认、可以或同意时，会看到确认范围说明，不会被当成高风险授权；低风险方向确认后 Codex 会在任务范围内继续本地推进。",
    "工程顺序、测试组合、门禁恢复和 subagent 调度由 Codex 决策，不要求用户选择内部角色或反复说继续。",
    "用户说先停一下或暂停当前任务时，会看到暂停说明、保留内容和恢复方式。",
    "用户说撤销刚才改动时，会看到需要确认的撤销范围、安全查看方式和不会直接回滚的说明。",
    "用户明确说正式开工时，会进入正式开工包预览。",
    "信息足够的复杂需求可以生成正式开工包预览，高风险需求仍会暂停确认。",
    "用户不知道该从哪个入口开始时，可以用复杂需求向导串联模板、完整度检查、执行计划和开工预览。",
]


def run(command: list[str], *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, **(env or {})},
    )


def python_command(*args: str) -> list[str]:
    return [sys.executable, *args]


def fail(check_id: str, message: str, details: list[str]) -> SmokeResult:
    return SmokeResult(check_id, "fail", message, details)


def ok(check_id: str, message: str, details: list[str]) -> SmokeResult:
    return SmokeResult(check_id, "ok", message, details)


def load_json_command(
    check_id: str,
    command: list[str],
    *,
    env: dict[str, str] | None = None,
) -> tuple[dict[str, Any] | None, list[str]]:
    result = run(command, env=env)
    details = [f"command: {' '.join(command)}"]
    if result.returncode != 0:
        details.append(result.stderr.strip() or result.stdout.strip())
        return None, details
    try:
        return json.loads(result.stdout), details
    except json.JSONDecodeError:
        details.append(result.stdout.strip())
        return None, details


def load_json_command_with_fixture(
    check_id: str,
    command: list[str],
    fixture_text: str,
) -> tuple[dict[str, Any] | None, list[str]]:
    fixture_path = REPO_ROOT / ".gstack" / "task-boundaries" / f".natural-language-smoke-active-{os.getpid()}.md"
    fixture_path.write_text(fixture_text, encoding="utf-8")
    try:
        relative = fixture_path.relative_to(REPO_ROOT).as_posix()
        return load_json_command(check_id, command, env={ACTIVE_BOUNDARY_ENV: relative})
    finally:
        try:
            fixture_path.unlink()
        except FileNotFoundError:
            pass


def load_json_command_with_active_fixture(
    check_id: str,
    command: list[str],
) -> tuple[dict[str, Any] | None, list[str]]:
    return load_json_command_with_fixture(check_id, command, ACTIVE_TASK_FIXTURE)


def load_json_command_with_completed_fixture(
    check_id: str,
    command: list[str],
) -> tuple[dict[str, Any] | None, list[str]]:
    return load_json_command_with_fixture(check_id, command, COMPLETED_TASK_FIXTURE)


def check_conditions(
    check_id: str,
    message: str,
    payload: dict[str, Any] | None,
    details: list[str],
    conditions: list[tuple[bool, str]],
) -> SmokeResult:
    if payload is None:
        return fail(check_id, "Command did not return valid JSON.", details)
    failed = [reason for passed, reason in conditions if not passed]
    if failed:
        return fail(check_id, message, [*details, *failed])
    return ok(check_id, message, details)


def intake_json(*args: str) -> tuple[dict[str, Any] | None, list[str]]:
    return load_json_command(
        "intake",
        python_command(".gstack/scripts/nontechnical_intake.py", *args, "--format", "json"),
    )


def check_broad_intake() -> SmokeResult:
    payload, details = intake_json("--raw", "我想让这个 AI 开发流程更适合不懂技术的人")
    question = (payload or {}).get("suggested_question", "")
    return check_conditions(
        "broad-intake",
        "Broad nontechnical goal asks one experience question.",
        payload,
        details,
        [
            ((payload or {}).get("can_continue") is False, "expected can_continue=false"),
            ("提需求" in question and "出错后" in question, "expected experience-area question"),
            ("先问用户" in (payload or {}).get("first_safe_step", ""), "expected first safe step to ask user"),
        ],
    )


def check_complex_intake() -> SmokeResult:
    payload, details = intake_json(
        "--raw",
        "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
        "--audience",
        "运营同事",
        "--success",
        "能看到按月份和 SKU 过滤后的结果",
        "--non-goal",
        "不改生产数据库",
    )
    slices = (payload or {}).get("delivery_slices", [])
    return check_conditions(
        "complex-intake",
        "Complex request is split into a phased delivery path.",
        payload,
        details,
        [
            ((payload or {}).get("can_continue") is True, "expected can_continue=true"),
            ((payload or {}).get("complexity") == "复杂需求", "expected complexity=复杂需求"),
            ("标准推进" in (payload or {}).get("recommended_path", ""), "expected standard recommended path"),
            (any("冻结" in item for item in slices), "expected requirement/acceptance freeze slice"),
            ("第一安全步" not in (payload or {}).get("first_safe_step", ""), "first_safe_step should contain the step itself"),
        ],
    )


def check_small_intake() -> SmokeResult:
    payload, details = intake_json(
        "--raw",
        "帮我把页面搜索和筛选做得更好用",
        "--audience",
        "运营",
        "--success",
        "可以输入关键词过滤表格",
        "--non-goal",
        "不接真实数据",
    )
    return check_conditions(
        "small-intake",
        "Small page request remains eligible for focused implementation.",
        payload,
        details,
        [
            ((payload or {}).get("can_continue") is True, "expected can_continue=true"),
            ((payload or {}).get("complexity") == "小需求", "expected complexity=小需求"),
            ((payload or {}).get("likely_surface") == "用户可见页面能力", "expected page-visible surface"),
            ("快速推进" in (payload or {}).get("recommended_path", ""), "expected quick recommended path"),
        ],
    )


def check_high_risk_intake() -> SmokeResult:
    payload, details = intake_json("--raw", "帮我把线上数据同步一下")
    risks = (payload or {}).get("risks", [])
    return check_conditions(
        "high-risk-intake",
        "High-risk data request pauses for scope and authorization.",
        payload,
        details,
        [
            ((payload or {}).get("can_continue") is False, "expected can_continue=false"),
            (any("真实数据" in item for item in risks), "expected real-data risk"),
            (any("生产" in item for item in risks), "expected production risk"),
            ("暂停确认" in (payload or {}).get("recommended_path", ""), "expected pause recommendation"),
        ],
    )


def check_risk_confirmed_intake() -> SmokeResult:
    payload, details = intake_json(
        "--raw",
        "帮我整理一个线上数据同步任务",
        "--audience",
        "运营负责人",
        "--success",
        "能看到同步范围、风险和验收方式",
        "--non-goal",
        "不操作线上数据、不写数据库、不发布、不提交",
        "--risk-confirmation",
        "只允许先整理需求和验收口径，不操作线上数据，不写数据库，不发布，不提交",
    )
    controls = (payload or {}).get("risk_controls", [])
    return check_conditions(
        "risk-confirmed-intake",
        "Risk-confirmed request can continue only as a controlled draft.",
        payload,
        details,
        [
            ((payload or {}).get("can_continue") is True, "expected can_continue=true"),
            ((payload or {}).get("risk_confirmation_status") == "safe-to-draft", "expected safe-to-draft confirmation"),
            (any("不写入" in item for item in controls), "expected no-write risk control"),
            (any("不操作线上" in item for item in controls), "expected no-production risk control"),
            ("风险受控推进" in (payload or {}).get("recommended_path", ""), "expected controlled-risk recommendation"),
        ],
    )


def check_text_command(
    check_id: str,
    command: list[str],
    expected_fragments: list[str],
    message: str,
    *,
    allow_nonzero: bool = False,
    forbidden_fragments: list[str] | None = None,
) -> SmokeResult:
    result = run(command)
    details = [f"command: {' '.join(command)}"]
    if result.returncode != 0 and not allow_nonzero:
        details.append(result.stderr.strip() or result.stdout.strip())
        return fail(check_id, "Command failed.", details)
    if result.returncode != 0:
        details.append(f"command exited {result.returncode}; validating output text only")
    missing = [fragment for fragment in expected_fragments if fragment not in result.stdout]
    if missing:
        return fail(check_id, message, [*details, "missing: " + ", ".join(missing)])
    forbidden = [fragment for fragment in (forbidden_fragments or []) if fragment in result.stdout]
    if forbidden:
        return fail(check_id, message, [*details, "forbidden: " + ", ".join(forbidden)])
    return ok(check_id, message, details)


def check_dashboard_explain() -> SmokeResult:
    return check_text_command(
        "dashboard-explain",
        python_command(
            ".gstack/scripts/gstack_dashboard.py",
            "explain",
            "--all",
            "--query",
            "nontechnical-dev-journey-smoke",
            "--limit",
            "1",
        ),
        ["当前任务", "下一步", "需要你确认"],
        "Dashboard explain gives current task, next step, and confirmation need.",
    )


def check_dashboard_verify() -> SmokeResult:
    return check_text_command(
        "dashboard-verify",
        python_command(
            ".gstack/scripts/gstack_dashboard.py",
            "verify",
            "--query",
            "nontechnical-dev-journey-smoke",
            "--limit",
            "1",
        ),
        ["你可以这样验收", "预期应该看到", "验收证据"],
        "Dashboard verify gives plain-language acceptance guidance.",
    )


def check_doctor_explain() -> SmokeResult:
    return check_text_command(
        "doctor-explain",
        python_command(".gstack/scripts/gstack_doctor.py", "explain"),
        ["出错后怎么继续", "Codex 的下一步", "什么时候需要你确认"],
        "Doctor explain gives plain-language recovery guidance.",
        allow_nonzero=True,
    )


def check_home_json() -> SmokeResult:
    payload, details = load_json_command(
        "home-json",
        python_command(".gstack/scripts/nontechnical_home.py", "--format", "json"),
    )
    options = (payload or {}).get("options", [])
    template = (payload or {}).get("complex_request_template", [])
    acceptance = (payload or {}).get("acceptance_summary", [])
    recovery = (payload or {}).get("recovery_summary", [])
    helper_status = (payload or {}).get("helper_status", [])
    return check_conditions(
        "home-json",
        "Home helper exposes current status, options, template, acceptance, and recovery.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "home-ready", "expected home-ready status"),
            (bool((payload or {}).get("current_task")), "expected current_task"),
            (bool((payload or {}).get("current_state")), "expected current_state"),
            (bool((payload or {}).get("next_step")), "expected next_step"),
            (any("继续当前任务" in item for item in options), "expected continue option"),
            (any("开始复杂需求" in item for item in options), "expected complex-request option"),
            (any("验收当前结果" in item for item in options), "expected acceptance option"),
            (any("出错后恢复" in item for item in options), "expected recovery option"),
            (any("谁会用" in item for item in template), "expected audience template"),
            (any("怎么验收" in item for item in template), "expected acceptance template"),
            (isinstance(acceptance, list) and len(acceptance) >= 1, "expected acceptance summary"),
            (isinstance(recovery, list) and len(recovery) >= 1, "expected recovery summary"),
            (isinstance(helper_status, list) and len(helper_status) == 3, "expected helper status list"),
        ],
    )


def check_home_user_format() -> SmokeResult:
    return check_text_command(
        "home-user-format",
        python_command(".gstack/scripts/nontechnical_home.py", "--format", "user"),
        [
            "非技术开发首页",
            "当前任务",
            "现在状态",
            "你现在可以",
            "开始复杂需求",
            "验收当前结果",
            "出错后怎么继续",
            "这次不会做什么",
        ],
        "Home user format is suitable for nontechnical Codex users.",
        forbidden_fragments=[
            "python3",
            ".gstack",
            "boundary",
            "gate",
            "spec",
            "JSON",
            "建议 lane",
            "git",
            "CLI",
            "commit",
            "push",
            "merge",
            " PR",
        ],
    )


def check_implementation_readiness_json() -> SmokeResult:
    payload, details = load_json_command(
        "implementation-readiness-json",
        python_command(".gstack/scripts/nontechnical_implementation_readiness.py", "--format", "json"),
    )
    completed = (payload or {}).get("completed_preparation", [])
    missing = (payload or {}).get("missing_preparation", [])
    next_actions = (payload or {}).get("codex_next_actions", [])
    confirmations = (payload or {}).get("needs_user_confirmation", [])
    return check_conditions(
        "implementation-readiness-json",
        "Implementation readiness exposes current task, preparation state, next actions, and confirmations.",
        payload,
        details,
        [
            ((payload or {}).get("status") in {"ready-to-implement", "not-ready-to-implement", "implementation-done-needs-acceptance", "already-complete", "no-active-task"}, "expected known readiness status"),
            (bool((payload or {}).get("current_task")), "expected current_task"),
            (isinstance((payload or {}).get("can_start_implementation"), bool), "expected boolean can_start_implementation"),
            (bool((payload or {}).get("overall_judgment")), "expected overall_judgment"),
            (isinstance(completed, list) and len(completed) >= 1, "expected completed preparation list"),
            (isinstance(missing, list) and len(missing) >= 1, "expected missing preparation list"),
            (isinstance(next_actions, list) and len(next_actions) >= 1, "expected next actions"),
            (isinstance(confirmations, list) and len(confirmations) >= 1, "expected confirmations"),
        ],
    )


def check_implementation_readiness_user_format() -> SmokeResult:
    return check_text_command(
        "implementation-readiness-user-format",
        python_command(".gstack/scripts/nontechnical_implementation_readiness.py", "--format", "user"),
        [
            "实现就绪检查",
            "当前任务",
            "整体判断",
            "已经准备好",
            "还差什么",
            "Codex 的下一步",
            "需要你确认",
            "这次不会做什么",
        ],
        "Implementation readiness user format explains readiness without internal terms.",
        forbidden_fragments=[
            "python3",
            ".gstack",
            "boundary",
            "gate",
            "spec",
            "JSON",
            "建议 lane",
            "git",
            "CLI",
            "commit",
            "push",
            "merge",
            " PR",
        ],
    )


def check_confirmation_brief_json() -> SmokeResult:
    payload, details = load_json_command(
        "confirmation-brief-json",
        python_command(".gstack/scripts/nontechnical_confirmation_brief.py", "--format", "json"),
    )
    return check_conditions(
        "confirmation-brief-json",
        "Confirmation brief exposes current task, confirmation state, suggested replies, and next actions.",
        payload,
        details,
        [
            ((payload or {}).get("status") in {"needs-user-confirmation", "no-user-confirmation-needed", "no-active-task"}, "expected known confirmation status"),
            (bool((payload or {}).get("current_task")), "expected current_task"),
            (isinstance((payload or {}).get("waiting_for_user"), bool), "expected boolean waiting_for_user"),
            (isinstance((payload or {}).get("confirmation_items"), list) and len((payload or {}).get("confirmation_items", [])) >= 1, "expected confirmation_items"),
            (isinstance((payload or {}).get("suggested_replies"), list) and len((payload or {}).get("suggested_replies", [])) >= 1, "expected suggested_replies"),
            (isinstance((payload or {}).get("codex_next_actions"), list) and len((payload or {}).get("codex_next_actions", [])) >= 1, "expected codex_next_actions"),
            (isinstance((payload or {}).get("non_actions"), list) and len((payload or {}).get("non_actions", [])) >= 1, "expected non_actions"),
        ],
    )


def check_confirmation_brief_user_format() -> SmokeResult:
    return check_text_command(
        "confirmation-brief-user-format",
        python_command(".gstack/scripts/nontechnical_confirmation_brief.py", "--format", "user"),
        [
            "确认事项说明",
            "当前任务",
            "现在是否等你确认",
            "需要你确认",
            "你可以这样回复",
            "Codex 的下一步",
            "这次不会做什么",
        ],
        "Confirmation brief user format explains current confirmation needs without internal terms.",
        forbidden_fragments=[
            "python3",
            ".gstack",
            "boundary",
            "gate",
            "spec",
            "JSON",
            "建议 lane",
            "git",
            "CLI",
            "commit",
            "push",
            "merge",
            " PR",
        ],
    )


def check_confirmation_response_json() -> SmokeResult:
    payload, details = load_json_command_with_active_fixture(
        "confirmation-response-json",
        python_command(".gstack/scripts/nontechnical_confirmation_response.py", "--raw", "我确认", "--format", "json"),
    )
    conditions = [
        ((payload or {}).get("status") in {"safe-to-continue", "needs-confirmation-scope", "no-active-task"}, "expected known confirmation response status"),
        (bool((payload or {}).get("current_task")), "expected current_task"),
        (bool((payload or {}).get("response_understanding")), "expected response_understanding"),
        (isinstance((payload or {}).get("can_confirm"), list) and len((payload or {}).get("can_confirm", [])) >= 1, "expected can_confirm"),
        (isinstance((payload or {}).get("still_needs_clarity"), list) and len((payload or {}).get("still_needs_clarity", [])) >= 1, "expected still_needs_clarity"),
        (isinstance((payload or {}).get("safe_next_actions"), list) and len((payload or {}).get("safe_next_actions", [])) >= 1, "expected safe_next_actions"),
        (isinstance((payload or {}).get("suggested_replies"), list) and len((payload or {}).get("suggested_replies", [])) >= 1, "expected suggested_replies"),
        (isinstance((payload or {}).get("non_actions"), list) and len((payload or {}).get("non_actions", [])) >= 1, "expected non_actions"),
    ]
    safe_actions = (payload or {}).get("safe_next_actions", [])
    conditions.append(((payload or {}).get("status") == "safe-to-continue", "expected active fixture to be safe-to-continue"))
    conditions.append((any("不需要你再说" in item for item in safe_actions), "expected safe continuation without another continue prompt"))
    conditions.append((any("subagent" in item for item in safe_actions), "expected Codex-owned subagent decision"))
    return check_conditions(
        "confirmation-response-json",
        "Confirmation response exposes current task, confirmation scope, safe actions, and non-actions.",
        payload,
        details,
        conditions,
    )


def check_confirmation_response_user_format() -> SmokeResult:
    return check_text_command(
        "confirmation-response-user-format",
        python_command(".gstack/scripts/nontechnical_confirmation_response.py", "--raw", "我确认", "--format", "user"),
        [
            "确认回复说明",
            "当前任务",
            "我对这句话的理解",
            "这句话可以确认什么",
            "还需要说清楚什么",
            "Codex 可以先安全做什么",
            "你可以这样回复",
            "这次不会做什么",
        ],
        "Confirmation response user format explains confirmation scope without internal terms.",
        forbidden_fragments=[
            "python3",
            ".gstack",
            "boundary",
            "gate",
            "spec",
            "JSON",
            "建议 lane",
            "git",
            "CLI",
            "commit",
            "push",
            "merge",
            " PR",
        ],
    )


def check_pause_control_json() -> SmokeResult:
    payload, details = load_json_command(
        "pause-control-json",
        python_command(".gstack/scripts/nontechnical_pause.py", "--raw", "先停一下，暂停这个任务", "--format", "json"),
    )
    return check_conditions(
        "pause-control-json",
        "Pause helper exposes current task, pause behavior, preserved context, and resume options.",
        payload,
        details,
        [
            ((payload or {}).get("status") in {"paused", "no-active-task"}, "expected known pause status"),
            (bool((payload or {}).get("current_task")), "expected current_task"),
            (bool((payload or {}).get("pause_understanding")), "expected pause_understanding"),
            (isinstance((payload or {}).get("preserved_context"), list) and len((payload or {}).get("preserved_context", [])) >= 1, "expected preserved_context"),
            (isinstance((payload or {}).get("stopped_actions"), list) and len((payload or {}).get("stopped_actions", [])) >= 1, "expected stopped_actions"),
            (isinstance((payload or {}).get("resume_options"), list) and len((payload or {}).get("resume_options", [])) >= 1, "expected resume_options"),
            (isinstance((payload or {}).get("needs_user_confirmation"), list) and len((payload or {}).get("needs_user_confirmation", [])) >= 1, "expected needs_user_confirmation"),
            (isinstance((payload or {}).get("non_actions"), list) and len((payload or {}).get("non_actions", [])) >= 1, "expected non_actions"),
        ],
    )


def check_pause_control_user_format() -> SmokeResult:
    return check_text_command(
        "pause-control-user-format",
        python_command(".gstack/scripts/nontechnical_pause.py", "--raw", "先停一下，暂停这个任务", "--format", "user"),
        [
            "暂停说明",
            "我会先暂停",
            "当前任务",
            "暂停后不会继续做什么",
            "已经保留的内容",
            "之后怎么恢复",
            "这次不会做什么",
        ],
        "Pause helper user format explains pause behavior without internal terms.",
        forbidden_fragments=[
            "python3",
            ".gstack",
            "boundary",
            "gate",
            "spec",
            "JSON",
            "建议 lane",
            "git",
            "CLI",
            "commit",
            "push",
            "merge",
            " PR",
        ],
    )


def check_undo_request_json() -> SmokeResult:
    payload, details = load_json_command(
        "undo-request-json",
        python_command(".gstack/scripts/nontechnical_undo_request.py", "--raw", "撤销刚才的改动，回到之前", "--format", "json"),
    )
    return check_conditions(
        "undo-request-json",
        "Undo helper exposes current task, required scope, safe actions, suggested replies, and non-actions.",
        payload,
        details,
        [
            ((payload or {}).get("status") in {"needs-undo-scope", "no-active-task"}, "expected known undo status"),
            (bool((payload or {}).get("current_task")), "expected current_task"),
            (bool((payload or {}).get("request_understanding")), "expected request_understanding"),
            (isinstance((payload or {}).get("required_scope"), list) and len((payload or {}).get("required_scope", [])) >= 1, "expected required_scope"),
            (isinstance((payload or {}).get("safe_next_actions"), list) and len((payload or {}).get("safe_next_actions", [])) >= 1, "expected safe_next_actions"),
            (isinstance((payload or {}).get("suggested_replies"), list) and len((payload or {}).get("suggested_replies", [])) >= 1, "expected suggested_replies"),
            (isinstance((payload or {}).get("needs_user_confirmation"), list) and len((payload or {}).get("needs_user_confirmation", [])) >= 1, "expected needs_user_confirmation"),
            (isinstance((payload or {}).get("non_actions"), list) and len((payload or {}).get("non_actions", [])) >= 1, "expected non_actions"),
        ],
    )


def check_undo_request_user_format() -> SmokeResult:
    return check_text_command(
        "undo-request-user-format",
        python_command(".gstack/scripts/nontechnical_undo_request.py", "--raw", "撤销刚才的改动，回到之前", "--format", "user"),
        [
            "撤销请求说明",
            "当前任务",
            "我对这句话的理解",
            "需要先确认的范围",
            "Codex 可以先安全做什么",
            "你可以这样回复",
            "这次不会做什么",
        ],
        "Undo helper user format explains undo scope without internal terms.",
        forbidden_fragments=[
            "python3",
            ".gstack",
            "boundary",
            "gate",
            "spec",
            "JSON",
            "建议 lane",
            "git",
            "CLI",
            "commit",
            "push",
            "merge",
            " PR",
        ],
    )


def check_complex_task_starter() -> SmokeResult:
    return check_text_command(
        "complex-task-starter",
        python_command(
            ".gstack/scripts/nontechnical_task_starter.py",
            "--raw",
            "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
            "--audience",
            "运营同事",
            "--success",
            "能看到按月份和 SKU 过滤后的结果",
            "--non-goal",
            "不改生产数据库",
            "--topic",
            "complex-dashboard",
            "--dry-run",
        ),
        ["状态：ready-to-draft", "建议 lane：standard", "草稿文件", "验收清单", "按月份和 SKU"],
        "Complex task starter previews a standard draft package with acceptance checks.",
    )


def check_risky_task_starter() -> SmokeResult:
    return check_text_command(
        "risky-task-starter",
        python_command(
            ".gstack/scripts/nontechnical_task_starter.py",
            "--raw",
            "帮我把线上数据同步一下",
            "--dry-run",
        ),
        ["状态：pause-for-risk", "建议 lane：blocked-until-confirmed", "先不要执行"],
        "Risky task starter pauses instead of generating implementable status.",
    )


def check_complex_task_starter_user_format() -> SmokeResult:
    return check_text_command(
        "complex-task-starter-user-format",
        python_command(
            ".gstack/scripts/nontechnical_task_starter.py",
            "--raw",
            "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
            "--audience",
            "运营同事",
            "--success",
            "能看到按月份和 SKU 过滤后的结果",
            "--non-goal",
            "不改生产数据库",
            "--topic",
            "complex-dashboard",
            "--dry-run",
            "--format",
            "user",
        ),
        ["我理解你想做的是", "我会先把它拆成几步来推进", "第一步我会先做", "完成后可以这样验收", "第一眼能看到"],
        "Complex starter user format hides internal terms and explains acceptance.",
        forbidden_fragments=["建议 lane", "草稿文件", "boundary", "gate", "spec", "JSON"],
    )


def check_complex_task_starter_acceptance_json() -> SmokeResult:
    payload, details = load_json_command(
        "complex-task-starter-acceptance-json",
        python_command(
            ".gstack/scripts/nontechnical_task_starter.py",
            "--raw",
            "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
            "--audience",
            "运营同事",
            "--success",
            "能看到按月份和 SKU 过滤后的结果",
            "--non-goal",
            "不改生产数据库",
            "--topic",
            "complex-dashboard",
            "--dry-run",
            "--format",
            "json",
        ),
    )
    checks = (payload or {}).get("acceptance_checks", [])
    return check_conditions(
        "complex-task-starter-acceptance-json",
        "Complex starter exposes structured acceptance checks.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "ready-to-draft", "expected ready-to-draft status"),
            (isinstance(checks, list) and len(checks) >= 4, "expected at least four acceptance checks"),
            (any("按月份和 SKU" in item for item in checks), "expected success criteria in acceptance checks"),
            (any("搜索" in item or "筛选" in item for item in checks), "expected search/filter acceptance check"),
            (any("导出" in item for item in checks), "expected export acceptance check"),
            (any("多人" in item for item in checks), "expected multi-person acceptance check"),
        ],
    )


def check_risky_task_starter_user_format() -> SmokeResult:
    return check_text_command(
        "risky-task-starter-user-format",
        python_command(
            ".gstack/scripts/nontechnical_task_starter.py",
            "--raw",
            "帮我把线上数据同步一下",
            "--dry-run",
            "--format",
            "user",
        ),
        ["我先不执行这件事", "我需要你确认一个问题", "在确认前"],
        "Risky starter user format pauses in plain language.",
        forbidden_fragments=["建议 lane", "草稿文件", "boundary", "gate", "spec", "JSON"],
    )


def check_risk_confirmed_task_starter() -> SmokeResult:
    return check_text_command(
        "risk-confirmed-task-starter",
        python_command(
            ".gstack/scripts/nontechnical_task_starter.py",
            "--raw",
            "帮我整理一个线上数据同步任务",
            "--audience",
            "运营负责人",
            "--success",
            "能看到同步范围、风险和验收方式",
            "--non-goal",
            "不操作线上数据、不写数据库、不发布、不提交",
            "--risk-confirmation",
            "只允许先整理需求和验收口径，不操作线上数据，不写数据库，不发布，不提交",
            "--topic",
            "risk-confirmed",
            "--dry-run",
        ),
        ["状态：ready-to-draft-with-risk-controls", "风险确认状态：safe-to-draft", "风险控制项", "不操作线上"],
        "Risk-confirmed starter previews a controlled draft package.",
    )


def check_risk_confirmed_task_starter_user_format() -> SmokeResult:
    return check_text_command(
        "risk-confirmed-task-starter-user-format",
        python_command(
            ".gstack/scripts/nontechnical_task_starter.py",
            "--raw",
            "帮我整理一个线上数据同步任务",
            "--audience",
            "运营负责人",
            "--success",
            "能看到同步范围、风险和验收方式",
            "--non-goal",
            "不操作线上数据、不写数据库、不发布、不提交",
            "--risk-confirmation",
            "只允许先整理需求和验收口径，不操作线上数据，不写数据库，不发布，不提交",
            "--topic",
            "risk-confirmed",
            "--dry-run",
            "--format",
            "user",
        ),
        ["我可以先整理开发起点", "不会执行高风险动作", "完成后可以这样验收", "不会操作线上数据"],
        "Risk-confirmed starter user format explains controlled continuation.",
        forbidden_fragments=["建议 lane", "草稿文件", "boundary", "gate", "spec", "JSON", "git workflow action"],
    )


def check_risk_insufficient_task_starter() -> SmokeResult:
    return check_text_command(
        "risk-insufficient-task-starter",
        python_command(
            ".gstack/scripts/nontechnical_task_starter.py",
            "--raw",
            "帮我把线上数据同步一下",
            "--risk-confirmation",
            "我确认",
            "--topic",
            "risk-insufficient",
            "--dry-run",
        ),
        ["状态：pause-for-risk", "风险确认状态：insufficient", "风险控制项"],
        "Insufficient risk confirmation still pauses.",
    )


def check_forbidden_scope_mapping() -> SmokeResult:
    return check_text_command(
        "forbidden-scope-mapping",
        python_command(
            ".gstack/scripts/nontechnical_task_starter.py",
            "--raw",
            "帮我做一个经营看板",
            "--audience",
            "运营同事",
            "--success",
            "能看到经营指标",
            "--non-goal",
            "不要动受限业务模块，也不要引入数据库",
            "--topic",
            "forbidden-restricted-module",
            "--dry-run",
        ),
        ["推断的禁止业务范围", "受限业务模块", "app/restricted-module/**"],
        "Starter maps explicit forbidden business scope to forbidden paths.",
    )


def check_forbidden_scope_user_format() -> SmokeResult:
    return check_text_command(
        "forbidden-scope-user-format",
        python_command(
            ".gstack/scripts/nontechnical_task_starter.py",
            "--raw",
            "帮我做一个经营看板",
            "--audience",
            "运营同事",
            "--success",
            "能看到经营指标",
            "--non-goal",
            "不要动受限业务模块，也不要引入数据库",
            "--topic",
            "forbidden-restricted-module",
            "--dry-run",
            "--format",
            "user",
        ),
        ["我也会避开这些范围", "受限业务模块"],
        "Starter user format explains forbidden scope without exposing paths.",
        forbidden_fragments=["app/restricted-module", "boundary", "gate", "spec", "JSON"],
    )


def check_smoke_user_format() -> SmokeResult:
    passing_output = render_user(
        [
            ok("broad-intake", "internal message", ["command: internal"]),
            ok("complex-intake", "internal message", [".gstack/internal"]),
        ]
    )
    failing_output = render_user(
        [
            ok("broad-intake", "internal message", ["command: internal"]),
            fail("complex-intake", "internal message", ["command: internal"]),
        ]
    )
    combined_output = passing_output + "\n" + failing_output
    expected_fragments = [
        "非技术开发关键路径检查通过。",
        "没有发现需要你确认的阻塞。",
        "非技术开发关键路径检查未通过。",
        "复杂需求会先拆成可交付步骤",
        "Codex 应先修复这些体验项",
    ]
    forbidden_fragments = [
        "broad-intake",
        "complex-intake",
        "command:",
        ".gstack",
        "boundary",
        "gate",
        "spec",
        "JSON",
        "建议 lane",
    ]
    missing = [fragment for fragment in expected_fragments if fragment not in combined_output]
    forbidden = [fragment for fragment in forbidden_fragments if fragment in combined_output]
    details = ["renderer sample validated without invoking subprocess recursion"]
    if missing or forbidden:
        if missing:
            details.append("missing: " + ", ".join(missing))
        if forbidden:
            details.append("forbidden: " + ", ".join(forbidden))
        return fail("smoke-user-format", "Smoke user format exposes internal details.", details)
    return ok("smoke-user-format", "Smoke user format gives plain-language results.", details)


def check_intent_router_json() -> SmokeResult:
    cases = [
        (
            "home",
            ["--raw", "打开开发首页，告诉我现在能做什么"],
            "nontechnical_home",
            True,
        ),
        (
            "implementation-readiness",
            ["--raw", "现在能开始实现了吗，还差什么才能开始开发"],
            "implementation_readiness",
            True,
        ),
        (
            "confirmation-brief",
            ["--raw", "现在需要我确认什么，我该回复什么"],
            "confirmation_brief",
            True,
        ),
        (
            "confirmation-response",
            ["--raw", "我确认"],
            "confirmation_response",
            True,
        ),
        (
            "pause-control",
            ["--raw", "先停一下，暂停这个任务"],
            "pause_current_task",
            True,
        ),
        (
            "undo-request",
            ["--raw", "撤销刚才的改动，回到之前"],
            "undo_request",
            True,
        ),
        (
            "progress",
            ["--raw", "我不知道现在做到哪一步了，帮我看一下"],
            "progress_status",
            True,
        ),
        (
            "verify",
            ["--raw", "做完以后我怎么知道它真的好了"],
            "completion_verify",
            True,
        ),
        (
            "acceptance-plan",
            [
                "--raw",
                "我想做一个完整的经营看板，支持筛选、导出和多人验收，怎么验收",
                "--audience",
                "运营同事",
                "--success",
                "能按月份和 SKU 筛选并导出",
                "--non-goal",
                "不改生产数据库",
            ],
            "acceptance_plan",
            True,
        ),
        (
            "visible-change",
            ["--raw", "我刷新了页面但没看到变化"],
            "visible_change_troubleshoot",
            True,
        ),
        (
            "page-change-brief",
            ["--raw", "我想改一个已有页面，但是不知道该先给你什么信息"],
            "page_change_brief",
            True,
        ),
        (
            "requirement-brief",
            ["--raw", "给我一个需求模板，我照着填"],
            "requirement_brief",
            True,
        ),
        (
            "requirement-readiness",
            ["--raw", "我按模板填了一版，你帮我看看还缺什么"],
            "requirement_readiness",
            True,
        ),
        (
            "first-use",
            ["--raw", "我第一次用这个项目，不懂技术，应该怎么开始"],
            "first_use_guide",
            True,
        ),
        (
            "ui-optimization",
            ["--raw", "进行 UI 优化"],
            "ui_optimization_kickoff",
            True,
        ),
        (
            "ci-failure",
            ["--raw", "GitHub 检查失败了，帮我看下一步怎么办"],
            "ci_failure_explain",
            True,
        ),
        (
            "continue",
            ["--raw", "按你刚才的计划继续推进"],
            "continue_current_task",
            True,
        ),
        (
            "mode-manual",
            ["--raw", "这次先别改代码，只给我方案"],
            "mode_control",
            True,
        ),
        (
            "mode-checkpoint",
            ["--raw", "这次关键地方问我，其他你继续推进"],
            "mode_control",
            True,
        ),
        (
            "recommendation",
            ["--raw", "我不懂技术，你帮我选一个最合适的方案"],
            "recommendation",
            True,
        ),
        (
            "recommendation-options",
            ["--raw", "这个需求有几种做法你直接推荐一个，不要让我选技术方案"],
            "recommendation",
            True,
        ),
        (
            "scope-change",
            ["--raw", "这个需求先不要做导出，只保留搜索和筛选"],
            "scope_change",
            True,
        ),
        (
            "prototype-first",
            ["--raw", "我想把刚才的需求改一下，不接真实数据，先做可点击页面"],
            "scope_change",
            True,
        ),
        (
            "prototype-demo",
            ["--raw", "先给我一个能点的 demo，数据用假的"],
            "scope_change",
            True,
        ),
        (
            "prototype-static",
            ["--raw", "先做静态页面看看效果，不接接口"],
            "scope_change",
            True,
        ),
        (
            "task-list",
            ["--raw", "帮我列一下现在还没做完的任务"],
            "task_list_explain",
            True,
        ),
        (
            "team-sync",
            ["--raw", "帮我把团队所有人的任务状态同步起来，但不要引入数据库，也不要动受限业务模块"],
            "team_sync_explain",
            False,
        ),
        (
            "delivery-summary",
            ["--raw", "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险"],
            "delivery_summary",
            True,
        ),
        (
            "recovery",
            ["--raw", "出错了，帮我看下一步怎么办"],
            "error_recovery",
            True,
        ),
        (
            "smoke",
            ["--raw", "帮我检查非技术开发关键路径"],
            "natural_language_smoke",
            True,
        ),
        (
            "complex",
            [
                "--raw",
                "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
                "--audience",
                "运营同事",
                "--success",
                "能看到按月份和 SKU 过滤后的结果",
                "--non-goal",
                "不改生产数据库",
            ],
            "complex_task_starter",
            True,
        ),
        (
            "formal-kickoff",
            [
                "--raw",
                "我已经说清楚了，正式开工做一个经营看板，支持筛选、导出和多人验收",
                "--audience",
                "运营同事",
                "--success",
                "能按月份和 SKU 筛选并导出",
                "--non-goal",
                "不改生产数据库",
            ],
            "formal_kickoff_preview",
            True,
        ),
        (
            "execution-plan",
            [
                "--raw",
                "我想做一个完整的经营看板，支持筛选、导出和多人验收，你会怎么推进",
                "--audience",
                "运营同事",
                "--success",
                "能按月份和 SKU 筛选并导出",
                "--non-goal",
                "不改生产数据库",
            ],
            "execution_plan",
            True,
        ),
        (
            "task-breakdown",
            ["--raw", "帮我把这个复杂需求拆成几个小任务，排一下优先级"],
            "execution_plan",
            False,
        ),
        (
            "risk",
            ["--raw", "帮我把线上数据同步一下"],
            "risk_confirmation",
            False,
        ),
        (
            "high-risk-continue",
            ["--raw", "继续同步线上数据"],
            "risk_confirmation",
            False,
        ),
        (
            "risk-confirmed",
            [
                "--raw",
                "帮我整理一个线上数据同步任务",
                "--audience",
                "运营负责人",
                "--success",
                "能看到同步范围、风险和验收方式",
                "--non-goal",
                "不操作线上数据、不写数据库、不发布、不提交",
                "--risk-confirmation",
                "只允许先整理需求和验收口径，不操作线上数据，不写数据库，不发布，不提交",
            ],
            "controlled_starter",
            True,
        ),
    ]
    details: list[str] = []
    failures: list[str] = []
    for label, args, expected_intent, expected_continue in cases:
        payload, command_details = load_json_command(
            "intent-router-json",
            python_command(".gstack/scripts/nontechnical_intent_router.py", *args, "--format", "json"),
        )
        details.extend(f"{label}: {detail}" for detail in command_details)
        if payload is None:
            failures.append(f"{label}: invalid json")
            continue
        if payload.get("intent") != expected_intent:
            failures.append(f"{label}: expected {expected_intent}, got {payload.get('intent')}")
        if payload.get("can_continue") is not expected_continue:
            failures.append(f"{label}: expected can_continue={expected_continue}, got {payload.get('can_continue')}")
    if failures:
        return fail("intent-router-json", "Intent router misclassified a user utterance.", [*details, *failures])
    return ok("intent-router-json", "Intent router classifies common user utterances.", details)


def check_intent_router_user_format() -> SmokeResult:
    cases = [
        (
            "home",
            ["--raw", "打开开发首页，告诉我现在能做什么", "--format", "user"],
            ["我会这样处理", "开发首页", "需要你确认：暂时不需要"],
        ),
        (
            "implementation-readiness",
            ["--raw", "现在能开始实现了吗，还差什么才能开始开发", "--format", "user"],
            ["我会这样处理", "开始实现", "需要你确认：暂时不需要"],
        ),
        (
            "confirmation-brief",
            ["--raw", "现在需要我确认什么，我该回复什么", "--format", "user"],
            ["我会这样处理", "确认", "需要你确认：暂时不需要"],
        ),
        (
            "confirmation-response",
            ["--raw", "我确认", "--format", "user"],
            ["我会这样处理", "确认回复", "需要你确认"],
        ),
        (
            "pause-control",
            ["--raw", "先停一下，暂停这个任务", "--format", "user"],
            ["我会这样处理", "暂停", "需要你确认：暂时不需要"],
        ),
        (
            "undo-request",
            ["--raw", "撤销刚才的改动，回到之前", "--format", "user"],
            ["我会这样处理", "撤销", "需要你确认"],
        ),
        (
            "verify",
            ["--raw", "做完以后我怎么知道它真的好了", "--format", "user"],
            ["我会这样处理", "需要你确认：暂时不需要", "不会直接操作真实数据"],
        ),
        (
            "acceptance-plan",
            [
                "--raw",
                "我想做一个完整的经营看板，支持筛选、导出和多人验收，怎么验收",
                "--audience",
                "运营同事",
                "--success",
                "能按月份和 SKU 筛选并导出",
                "--non-goal",
                "不改生产数据库",
                "--format",
                "user",
            ],
            ["我会这样处理", "验收清单", "需要你确认：暂时不需要"],
        ),
        (
            "visible-change",
            ["--raw", "我刷新了页面但没看到变化", "--format", "user"],
            ["我会这样处理", "查看位置", "需要你确认：暂时不需要"],
        ),
        (
            "page-change-brief",
            ["--raw", "我想改一个已有页面，但是不知道该先给你什么信息", "--format", "user"],
            ["我会这样处理", "信息清单", "照填模板", "需要你确认"],
        ),
        (
            "requirement-brief",
            ["--raw", "给我一个需求模板，我照着填", "--format", "user"],
            ["我会这样处理", "需求信息", "照填模板", "需要你确认"],
        ),
        (
            "requirement-readiness",
            ["--raw", "我按模板填了一版，你帮我看看还缺什么", "--format", "user"],
            ["我会这样处理", "完整度", "优先缺失项", "需要你确认"],
        ),
        (
            "first-use",
            ["--raw", "这个骨架怎么用来开发一个复杂需求", "--format", "user"],
            ["我会这样处理", "新手", "从想法到开工", "需要你确认"],
        ),
        (
            "ui-optimization",
            ["--raw", "进行 UI 优化", "--format", "user"],
            ["我会这样处理", "用户可见界面优化", "UI 设计梳理", "视觉复核", "浏览器验收", "需要你确认：暂时不需要"],
        ),
        (
            "ci-failure",
            ["--raw", "GitHub 检查失败了，帮我看下一步怎么办", "--format", "user"],
            ["我会这样处理", "失败检查", "需要你确认：暂时不需要"],
        ),
        (
            "continue",
            ["--raw", "继续做", "--format", "user"],
            ["我会这样处理", "继续推进", "需要你确认：暂时不需要"],
        ),
        (
            "mode-manual",
            ["--raw", "这次先别改代码，只给我方案", "--format", "user"],
            ["我会这样处理", "协作模式", "需要你确认：暂时不需要"],
        ),
        (
            "recommendation",
            ["--raw", "我不懂技术，你帮我选一个最合适的方案", "--format", "user"],
            ["我会这样处理", "推荐方案", "需要你确认：暂时不需要"],
        ),
        (
            "scope-change",
            ["--raw", "这个需求先不要做导出，只保留搜索和筛选", "--format", "user"],
            ["我会这样处理", "需求范围调整", "需要你确认：暂时不需要"],
        ),
        (
            "team-sync",
            ["--raw", "帮我把团队所有人的任务状态同步起来，但不要引入数据库，也不要动受限业务模块", "--format", "user"],
            ["我会这样处理", "无数据库", "只读生成视图", "需要你确认"],
        ),
        (
            "delivery-summary",
            ["--raw", "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险", "--format", "user"],
            ["我会这样处理", "交付总结", "下一步建议", "需要你确认：暂时不需要"],
        ),
        (
            "risk",
            ["--raw", "帮我把线上数据同步一下", "--format", "user"],
            ["我会这样处理", "需要你确认", "代码提交流程"],
        ),
        (
            "formal-kickoff",
            [
                "--raw",
                "我已经说清楚了，正式开工做一个经营看板，支持筛选、导出和多人验收",
                "--audience",
                "运营同事",
                "--success",
                "能按月份和 SKU 筛选并导出",
                "--non-goal",
                "不改生产数据库",
                "--format",
                "user",
            ],
            ["我会这样处理", "正式开工包", "需要你确认：暂时不需要"],
        ),
    ]
    details: list[str] = []
    failures: list[str] = []
    forbidden_fragments = ["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git"]
    for label, args, expected_fragments in cases:
        result = run(python_command(".gstack/scripts/nontechnical_intent_router.py", *args))
        details.append(f"{label}: command: {sys.executable} .gstack/scripts/nontechnical_intent_router.py {' '.join(args)}")
        if result.returncode != 0:
            failures.append(f"{label}: command failed")
            failures.append(result.stderr.strip() or result.stdout.strip())
            continue
        missing = [fragment for fragment in expected_fragments if fragment not in result.stdout]
        if missing:
            failures.append(f"{label}: missing " + ", ".join(missing))
        forbidden = [fragment for fragment in forbidden_fragments if fragment in result.stdout]
        if forbidden:
            failures.append(f"{label}: forbidden " + ", ".join(forbidden))
    if failures:
        return fail("intent-router-user-format", "Intent router user format exposes internal routing details.", [*details, *failures])
    return ok("intent-router-user-format", "Intent router user format hides internal routing details.", details)


def check_next_step_json() -> SmokeResult:
    cases = [
        (
            "home",
            ["--raw", "打开开发首页，告诉我现在能做什么"],
            "nontechnical_home",
            "nontechnical_home.user",
        ),
        (
            "implementation-readiness",
            ["--raw", "现在能开始实现了吗，还差什么才能开始开发"],
            "implementation_readiness",
            "nontechnical_implementation_readiness.user",
        ),
        (
            "confirmation-brief",
            ["--raw", "现在需要我确认什么，我该回复什么"],
            "confirmation_brief",
            "nontechnical_confirmation_brief.user",
        ),
        (
            "confirmation-response",
            ["--raw", "我确认"],
            "confirmation_response",
            "nontechnical_confirmation_response.user",
        ),
        (
            "pause-control",
            ["--raw", "先停一下，暂停这个任务"],
            "pause_current_task",
            "nontechnical_pause.user",
        ),
        (
            "undo-request",
            ["--raw", "撤销刚才的改动，回到之前"],
            "undo_request",
            "nontechnical_undo_request.user",
        ),
        (
            "progress",
            ["--raw", "我不知道现在做到哪一步了，帮我看一下"],
            "progress_status",
            "gstack_dashboard.explain",
        ),
        (
            "verify",
            ["--raw", "做完以后我怎么知道它真的好了"],
            "completion_verify",
            "gstack_dashboard.verify",
        ),
        (
            "acceptance-plan",
            [
                "--raw",
                "我想做一个完整的经营看板，支持筛选、导出和多人验收，怎么验收",
                "--audience",
                "运营同事",
                "--success",
                "能按月份和 SKU 筛选并导出",
                "--non-goal",
                "不改生产数据库",
            ],
            "acceptance_plan",
            "nontechnical_acceptance_plan.user",
        ),
        (
            "visible-change",
            ["--raw", "我刷新了页面但没看到变化"],
            "visible_change_troubleshoot",
            "nontechnical_visible_change.user",
        ),
        (
            "page-change-brief",
            ["--raw", "我想改一个已有页面，但是不知道该先给你什么信息"],
            "page_change_brief",
            "nontechnical_page_change_brief.user",
        ),
        (
            "requirement-brief",
            ["--raw", "开工前我需要给你哪些信息"],
            "requirement_brief",
            "nontechnical_requirement_brief.user",
        ),
        (
            "requirement-readiness",
            ["--raw", "这些信息够不够开工"],
            "requirement_readiness",
            "nontechnical_requirement_readiness.user",
        ),
        (
            "first-use",
            ["--raw", "这个骨架怎么用来开发一个复杂需求"],
            "first_use_guide",
            "nontechnical_first_use.user",
        ),
        (
            "ui-optimization",
            ["--raw", "进行 UI 优化"],
            "ui_optimization_kickoff",
            "nontechnical_ui_optimization.user",
        ),
        (
            "ci-failure",
            ["--raw", "GitHub 检查失败了，帮我看下一步怎么办"],
            "ci_failure_explain",
            "nontechnical_ci_failure.user",
        ),
        (
            "continue",
            ["--raw", "那就先做第一步"],
            "continue_current_task",
            "nontechnical_continue.user",
        ),
        (
            "mode-manual",
            ["--raw", "这次先别改代码，只给我方案"],
            "mode_control",
            "nontechnical_mode_control.user",
        ),
        (
            "mode-checkpoint",
            ["--raw", "这次关键地方问我，其他你继续推进"],
            "mode_control",
            "nontechnical_mode_control.user",
        ),
        (
            "recommendation",
            ["--raw", "这个需求有几种做法你直接推荐一个，不要让我选技术方案"],
            "recommendation",
            "nontechnical_recommendation.user",
        ),
        (
            "scope-change",
            ["--raw", "这个需求先不要做导出，只保留搜索和筛选"],
            "scope_change",
            "nontechnical_scope_change.user",
        ),
        (
            "prototype-first",
            ["--raw", "我想把刚才的需求改一下，不接真实数据，先做可点击页面"],
            "scope_change",
            "nontechnical_scope_change.user",
        ),
        (
            "prototype-demo",
            ["--raw", "先给我一个能点的 demo，数据用假的"],
            "scope_change",
            "nontechnical_scope_change.user",
        ),
        (
            "prototype-static",
            ["--raw", "先做静态页面看看效果，不接接口"],
            "scope_change",
            "nontechnical_scope_change.user",
        ),
        (
            "task-list",
            ["--raw", "我想先看看有哪些历史需求和未完成任务"],
            "task_list_explain",
            "nontechnical_task_list.user",
        ),
        (
            "team-sync",
            ["--raw", "帮我把团队所有人的任务状态同步起来，但不要引入数据库，也不要动受限业务模块"],
            "team_sync_explain",
            "nontechnical_team_sync.user",
        ),
        (
            "delivery-summary",
            ["--raw", "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险"],
            "delivery_summary",
            "nontechnical_delivery_summary.user",
        ),
        (
            "recovery",
            ["--raw", "出错了，帮我看下一步怎么办"],
            "error_recovery",
            "gstack_doctor.explain",
        ),
        (
            "smoke",
            ["--raw", "帮我检查非技术开发关键路径"],
            "natural_language_smoke",
            "natural_language_dev_smoke.user",
        ),
        (
            "complex",
            [
                "--raw",
                "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
                "--audience",
                "运营同事",
                "--success",
                "能看到按月份和 SKU 过滤后的结果",
                "--non-goal",
                "不改生产数据库",
            ],
            "complex_task_starter",
            "nontechnical_task_starter.user",
        ),
        (
            "formal-kickoff",
            [
                "--raw",
                "我已经说清楚了，正式开工做一个经营看板，支持筛选、导出和多人验收",
                "--audience",
                "运营同事",
                "--success",
                "能按月份和 SKU 筛选并导出",
                "--non-goal",
                "不改生产数据库",
                "--ai-reviewed",
            ],
            "formal_kickoff_preview",
            "nontechnical_formal_kickoff.user",
        ),
        (
            "execution-plan",
            [
                "--raw",
                "我想做一个完整的经营看板，支持筛选、导出和多人验收，你会怎么推进",
                "--audience",
                "运营同事",
                "--success",
                "能按月份和 SKU 筛选并导出",
                "--non-goal",
                "不改生产数据库",
            ],
            "execution_plan",
            "nontechnical_execution_plan.user",
        ),
        (
            "task-breakdown",
            ["--raw", "这个功能先做哪几个里程碑，每个阶段怎么验收"],
            "execution_plan",
            "nontechnical_execution_plan.user",
        ),
    ]
    details: list[str] = []
    failures: list[str] = []
    for label, args, expected_intent, expected_helper in cases:
        payload, command_details = load_json_command(
            "next-step-json",
            python_command(".gstack/scripts/nontechnical_next_step.py", *args, "--format", "json"),
        )
        details.extend(f"{label}: {detail}" for detail in command_details)
        if payload is None:
            failures.append(f"{label}: invalid json")
            continue
        if payload.get("intent") != expected_intent:
            failures.append(f"{label}: expected {expected_intent}, got {payload.get('intent')}")
        if payload.get("helper_entry") != expected_helper:
            failures.append(f"{label}: expected helper {expected_helper}, got {payload.get('helper_entry')}")
        if not payload.get("user_response"):
            failures.append(f"{label}: empty user_response")
    if failures:
        return fail("next-step-json", "Next-step runner selected the wrong helper.", [*details, *failures])
    return ok("next-step-json", "Next-step runner selects the right helper.", details)


def check_next_step_user_format() -> SmokeResult:
    cases = [
        (
            "home",
            ["--raw", "打开开发首页，告诉我现在能做什么", "--format", "user"],
            ["非技术开发首页", "当前任务", "你现在可以", "开始复杂需求", "验收当前结果", "出错后怎么继续"],
        ),
        (
            "implementation-readiness",
            ["--raw", "现在能开始实现了吗，还差什么才能开始开发", "--format", "user"],
            ["实现就绪检查", "当前任务", "整体判断", "已经准备好", "还差什么", "Codex 的下一步", "需要你确认"],
        ),
        (
            "confirmation-brief",
            ["--raw", "现在需要我确认什么，我该回复什么", "--format", "user"],
            ["确认事项说明", "当前任务", "现在是否等你确认", "需要你确认", "你可以这样回复", "Codex 的下一步"],
        ),
        (
            "confirmation-response",
            ["--raw", "我确认", "--format", "user"],
            ["确认回复说明", "当前任务", "这句话可以确认什么", "还需要说清楚什么", "Codex 可以先安全做什么", "你可以这样回复"],
        ),
        (
            "pause-control",
            ["--raw", "先停一下，暂停这个任务", "--format", "user"],
            ["暂停说明", "我会先暂停", "当前任务", "暂停后不会继续做什么", "已经保留的内容", "之后怎么恢复"],
        ),
        (
            "undo-request",
            ["--raw", "撤销刚才的改动，回到之前", "--format", "user"],
            ["撤销请求说明", "当前任务", "需要先确认的范围", "Codex 可以先安全做什么", "你可以这样回复"],
        ),
        (
            "verify",
            ["--raw", "做完以后我怎么知道它真的好了", "--format", "user"],
            ["你可以这样验收", "预期应该看到"],
        ),
        (
            "acceptance-plan",
            [
                "--raw",
                "我想做一个完整的经营看板，支持筛选、导出和多人验收，怎么验收",
                "--audience",
                "运营同事",
                "--success",
                "能按月份和 SKU 筛选并导出",
                "--non-goal",
                "不改生产数据库",
                "--format",
                "user",
            ],
            ["可以这样验收", "你要实际看到 / 操作", "预期应该看到", "需要你确认"],
        ),
        (
            "visible-change",
            ["--raw", "我刷新了页面但没看到变化", "--format", "user"],
            ["Codex 的下一步", "需要你确认"],
        ),
        (
            "page-change-brief",
            ["--raw", "改页面要怎么描述，才能让你直接开工", "--format", "user"],
            ["你不用懂技术", "页面位置", "现在看到的问题", "我希望改成", "我会这样验收", "本次不要碰", "Codex 的下一步", "需要你确认"],
        ),
        (
            "requirement-brief",
            ["--raw", "我有个复杂需求，但不知道该怎么描述给你", "--format", "user"],
            ["你可以这样描述需求", "照填模板", "谁会用", "成功后第一眼", "这次不做", "Codex 的下一步", "需要你确认"],
        ),
        (
            "requirement-readiness",
            ["--raw", "我这样描述可以开始做了吗", "--format", "user"],
            ["需求完整度检查", "整体判断", "已经说清楚", "还需要补充", "Codex 的下一步", "这次不会做什么"],
        ),
        (
            "first-use",
            ["--raw", "我完全不会写代码，能不能带我从想法开始", "--format", "user"],
            ["新手开始路径", "你可以这样开始", "现在只要这样发", "Codex 的下一步", "这次不会做什么"],
        ),
        (
            "ui-optimization",
            ["--raw", "进行 UI 优化", "--format", "user"],
            ["UI 优化开工说明", "用户可见界面", "UI 设计梳理", "视觉复核", "浏览器验收", "不改 API 合同", "不改数据合同", "不改 runner 逻辑", "需要你确认"],
        ),
        (
            "ci-failure",
            ["--raw", "GitHub 检查失败了，帮我看下一步怎么办", "--format", "user"],
            ["CI / GitHub 检查失败", "先确认失败的是哪类检查", "Codex 的下一步", "需要你确认"],
        ),
        (
            "continue",
            ["--raw", "按你刚才的计划继续推进", "--format", "user"],
            ["我会按继续推进处理", "当前任务", "Codex 的下一步", "需要你确认"],
        ),
        (
            "mode-manual",
            ["--raw", "这次先别改代码，只给我方案", "--format", "user"],
            ["当前协作模式", "手动控制", "不改代码", "需要你确认", "这次不会做什么"],
        ),
        (
            "mode-checkpoint",
            ["--raw", "这次关键地方问我，其他你继续推进", "--format", "user"],
            ["当前协作模式", "关键确认", "关键产品口径", "需要你确认", "这次不会做什么"],
        ),
        (
            "recommendation",
            ["--raw", "我不知道该先做页面、接数据还是做导出，你替我决定第一步", "--format", "user"],
            ["我会先给推荐方案", "推荐方案", "为什么推荐", "暂不选择", "第一安全步", "需要你确认"],
        ),
        (
            "scope-change",
            ["--raw", "这个需求先不要做导出，只保留搜索和筛选", "--format", "user"],
            ["我会按需求范围调整处理", "这次先做 / 保留", "搜索", "筛选", "这次先不做 / 排除", "导出", "需要你确认"],
        ),
        (
            "prototype-first",
            ["--raw", "我想把刚才的需求改一下，不接真实数据，先做可点击页面", "--format", "user"],
            ["我会按需求范围调整处理", "可点击页面", "真实数据接入", "按可点击 / mock 数据版本理解", "需要你确认"],
        ),
        (
            "team-sync",
            ["--raw", "帮我把团队所有人的任务状态同步起来，但不要引入数据库，也不要动受限业务模块", "--format", "user"],
            ["团队状态同步需求", "不引入数据库", "只读生成视图", "需要你确认", "受限业务模块"],
        ),
        (
            "task-list",
            ["--raw", "我想先看看有哪些历史需求和未完成任务", "--format", "user"],
            ["任务概览", "未完成任务", "卡住任务", "Codex 的下一步", "需要你确认"],
        ),
        (
            "delivery-summary",
            ["--raw", "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险", "--format", "user"],
            ["可以直接这样发给团队", "本次交付", "这次改了什么", "怎么验收", "风险和未做", "下一步建议", "需要你确认"],
        ),
        (
            "recovery",
            ["--raw", "出错了，帮我看下一步怎么办", "--format", "user"],
            ["出错后怎么继续", "Codex 的下一步"],
        ),
        (
            "complex",
            [
                "--raw",
                "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
                "--audience",
                "运营同事",
                "--success",
                "能看到按月份和 SKU 过滤后的结果",
                "--non-goal",
                "不改生产数据库",
                "--format",
                "user",
            ],
            ["我理解你想做的是", "完成后可以这样验收"],
        ),
        (
            "formal-kickoff",
            [
                "--raw",
                "我已经说清楚了，正式开工做一个经营看板，支持筛选、导出和多人验收",
                "--audience",
                "运营同事",
                "--success",
                "能按月份和 SKU 筛选并导出",
                "--non-goal",
                "不改生产数据库",
                "--ai-reviewed",
                "--format",
                "user",
            ],
            ["正式开工包", "完成后可以这样验收", "不会直接操作"],
        ),
        (
            "execution-plan",
            [
                "--raw",
                "我想做一个完整的经营看板，支持筛选、导出和多人验收，你会怎么推进",
                "--audience",
                "运营同事",
                "--success",
                "能按月份和 SKU 筛选并导出",
                "--non-goal",
                "不改生产数据库",
                "--format",
                "user",
            ],
            ["执行计划", "推进顺序", "需要你确认", "完成后可以这样验收"],
        ),
        (
            "task-breakdown",
            ["--raw", "这个功能先做哪几个里程碑，每个阶段怎么验收", "--format", "user"],
            ["执行计划", "推进顺序", "先补齐关键信息", "确认交付表面", "每个阶段", "需要你确认"],
        ),
        (
            "risk",
            ["--raw", "帮我把线上数据同步一下", "--format", "user"],
            ["需要你确认", "代码提交流程"],
        ),
    ]
    details: list[str] = []
    failures: list[str] = []
    forbidden_fragments = [
        "python3",
        ".gstack",
        "boundary",
        "gate",
        "spec",
        "JSON",
        "建议 lane",
        "git",
        "CLI",
        "commit",
        "push",
        "merge",
        " PR",
    ]
    for label, args, expected_fragments in cases:
        result = run(python_command(".gstack/scripts/nontechnical_next_step.py", *args))
        details.append(f"{label}: command: {sys.executable} .gstack/scripts/nontechnical_next_step.py {' '.join(args)}")
        if result.returncode != 0:
            failures.append(f"{label}: command failed")
            failures.append(result.stderr.strip() or result.stdout.strip())
            continue
        missing = [fragment for fragment in expected_fragments if fragment not in result.stdout]
        if missing:
            failures.append(f"{label}: missing " + ", ".join(missing))
        forbidden = [fragment for fragment in forbidden_fragments if fragment in result.stdout]
        if forbidden:
            failures.append(f"{label}: forbidden " + ", ".join(forbidden))
    if failures:
        return fail("next-step-user-format", "Next-step user format exposes internal details.", [*details, *failures])
    return ok("next-step-user-format", "Next-step user format is suitable for users.", details)


def check_execution_plan_json() -> SmokeResult:
    payload, details = load_json_command(
        "execution-plan-json",
        python_command(
            ".gstack/scripts/nontechnical_execution_plan.py",
            "--raw",
            "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
            "--audience",
            "运营同事",
            "--success",
            "能按月份和 SKU 筛选并导出",
            "--non-goal",
            "不改生产数据库",
            "--format",
            "json",
        ),
    )
    phases = (payload or {}).get("phases", [])
    confirmations = (payload or {}).get("needs_user_confirmation", [])
    checks = (payload or {}).get("acceptance_checks", [])
    subagents = (payload or {}).get("subagent_strategy", [])
    return check_conditions(
        "execution-plan-json",
        "Execution plan exposes phases, confirmation points, and acceptance checks.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "ready-to-plan", "expected ready-to-plan status"),
            (isinstance(phases, list) and len(phases) >= 3, "expected at least three phases"),
            (any("最小可见" in str(phase) for phase in phases), "expected visible-slice phase"),
            (isinstance(subagents, list) and any("subagent" in item for item in subagents), "expected subagent strategy"),
            (any("数据" in item for item in confirmations), "expected data confirmation point"),
            (any("筛选" in item or "导出" in item for item in checks), "expected acceptance checks"),
        ],
    )


def check_execution_plan_user_format() -> SmokeResult:
    return check_text_command(
        "execution-plan-user-format",
        python_command(
            ".gstack/scripts/nontechnical_execution_plan.py",
            "--raw",
            "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
            "--audience",
            "运营同事",
            "--success",
            "能按月份和 SKU 筛选并导出",
            "--non-goal",
            "不改生产数据库",
            "--format",
            "user",
        ),
        ["执行计划", "推进顺序", "Codex 可以自动处理", "Codex 的分工策略", "subagent", "需要你确认", "完成后可以这样验收"],
        "Execution plan user format explains plan without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI"],
    )


def check_task_breakdown_json() -> SmokeResult:
    payload, details = load_json_command(
        "task-breakdown-json",
        python_command(
            ".gstack/scripts/nontechnical_execution_plan.py",
            "--raw",
            "这个功能先做哪几个里程碑，每个阶段怎么验收",
            "--format",
            "json",
        ),
    )
    phases = (payload or {}).get("phases", [])
    confirmations = (payload or {}).get("needs_user_confirmation", [])
    checks = (payload or {}).get("acceptance_checks", [])
    return check_conditions(
        "task-breakdown-json",
        "Task breakdown request exposes partial plan, confirmation, and phase acceptance.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "ready-to-plan", "expected ready-to-plan status"),
            ((payload or {}).get("can_continue") is True, "expected can_continue=true for plan-only output"),
            (any("先补齐关键信息" in str(phase) for phase in phases), "expected key-info phase"),
            (any("确认交付表面" in str(phase) for phase in phases), "expected delivery-surface phase"),
            (isinstance(confirmations, list) and len(confirmations) == 1, "expected exactly one confirmation question"),
            (any("每个阶段" in item for item in checks), "expected per-phase acceptance check"),
        ],
    )


def check_task_breakdown_user_format() -> SmokeResult:
    return check_text_command(
        "task-breakdown-user-format",
        python_command(
            ".gstack/scripts/nontechnical_next_step.py",
            "--raw",
            "这个功能先做哪几个里程碑，每个阶段怎么验收",
            "--format",
            "user",
        ),
        ["执行计划", "推进顺序", "先补齐关键信息", "确认交付表面", "每个阶段", "需要你确认"],
        "Task breakdown user format explains milestones without current-task verification.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI"],
    )


def check_first_use_json() -> SmokeResult:
    payload, details = load_json_command(
        "first-use-json",
        python_command(
            ".gstack/scripts/nontechnical_first_use.py",
            "--raw",
            "我第一次用这个项目，不懂技术，应该怎么开始",
            "--format",
            "json",
        ),
    )
    start_path = (payload or {}).get("start_path", [])
    template = (payload or {}).get("send_now_template", [])
    next_actions = (payload or {}).get("codex_next_actions", [])
    non_actions = (payload or {}).get("non_actions", [])
    return check_conditions(
        "first-use-json",
        "First-use guide exposes start path, template, and safe non-actions.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "first-use-guide-ready", "expected first-use-guide-ready status"),
            (any("一句话" in item for item in start_path), "expected one-sentence goal step"),
            (any("成功后第一眼" in item for item in start_path), "expected visible success step"),
            (any("这次不要碰" in item for item in template), "expected do-not-touch template field"),
            (any("真实数据" in item for item in template), "expected risk template field"),
            (any("正式开工" in item for item in next_actions), "expected formal kickoff next action"),
            (any("敏感配置" in item for item in non_actions), "expected sensitive-config non-action"),
        ],
    )


def check_first_use_user_format() -> SmokeResult:
    return check_text_command(
        "first-use-user-format",
        python_command(
            ".gstack/scripts/nontechnical_first_use.py",
            "--raw",
            "我完全不会写代码，能不能带我从想法开始",
            "--format",
            "user",
        ),
        ["新手开始路径", "你可以这样开始", "现在只要这样发", "从想法", "Codex 的下一步", "需要你确认", "这次不会做什么"],
        "First-use guide user format explains the start path without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", " PR", "commit", "push", "merge"],
    )


def check_requirement_brief_json() -> SmokeResult:
    payload, details = load_json_command(
        "requirement-brief-json",
        python_command(
            ".gstack/scripts/nontechnical_requirement_brief.py",
            "--raw",
            "我有个复杂需求，但不知道该怎么描述给你",
            "--format",
            "json",
        ),
    )
    fields = (payload or {}).get("brief_fields", [])
    template = (payload or {}).get("fill_in_template", [])
    non_actions = (payload or {}).get("non_actions", [])
    return check_conditions(
        "requirement-brief-json",
        "Requirement brief exposes fill-in fields and non-actions.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "ready-to-collect-requirement", "expected ready-to-collect-requirement status"),
            (any("谁会用" in item for item in fields), "expected audience field"),
            (any("想完成什么" in item for item in fields), "expected goal field"),
            (any("成功后第一眼" in item for item in fields), "expected visible-success field"),
            (any("数据从哪里来" in item for item in fields), "expected data-source field"),
            (any("这次不做" in item for item in fields), "expected non-goal field"),
            (any("怎么验收" in item for item in fields), "expected acceptance field"),
            (any("是否涉及线上" in item for item in template), "expected risk template field"),
            (any("敏感配置" in item for item in non_actions), "expected sensitive-config non-action"),
        ],
    )


def check_requirement_brief_user_format() -> SmokeResult:
    return check_text_command(
        "requirement-brief-user-format",
        python_command(
            ".gstack/scripts/nontechnical_requirement_brief.py",
            "--raw",
            "开工前我需要给你哪些信息",
            "--format",
            "user",
        ),
        ["你可以这样描述需求", "照填模板", "谁会用", "成功后第一眼", "数据", "这次不做", "怎么验收", "Codex 的下一步", "这次不会做什么"],
        "Requirement brief user format explains fill-in fields without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", " PR", "commit", "push", "merge"],
    )


def check_requirement_readiness_json() -> SmokeResult:
    payload, details = load_json_command(
        "requirement-readiness-json",
        python_command(
            ".gstack/scripts/nontechnical_requirement_readiness.py",
            "--raw",
            "谁会用：运营同事；他们想完成：按月份和 SKU 筛选经营看板；现在的问题是：人工查找太慢；成功后第一眼看到：有月份和 SKU 筛选结果；用户会这样操作：选择月份、输入 SKU、查看表格；数据来源：先用假数据；这次不做：真实数据、数据库、发布和代码提交流程；是否涉及线上、数据库、真实数据、发布或代码提交流程：暂时都不涉及；我会这样验收：输入 SKU 后只看到匹配结果",
            "--format",
            "json",
        ),
    )
    present = (payload or {}).get("present_fields", [])
    priority_missing = (payload or {}).get("priority_missing", [])
    controls = (payload or {}).get("risk_controls", [])
    non_actions = (payload or {}).get("non_actions", [])
    return check_conditions(
        "requirement-readiness-json",
        "Requirement readiness exposes readiness, fields, and risk controls.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "ready-for-kickoff-preview", "expected ready-for-kickoff-preview status"),
            ((payload or {}).get("can_preview_kickoff") is True, "expected can_preview_kickoff=true"),
            (any("谁会用" in item for item in present), "expected audience present"),
            (any("想完成什么" in item for item in present), "expected goal present"),
            (any("成功后第一眼" in item for item in present), "expected visible success present"),
            (any("数据来源" in item for item in present), "expected data source present"),
            (any("这次不做" in item for item in present), "expected non-goal present"),
            (any("怎么验收" in item for item in present), "expected acceptance present"),
            (priority_missing == [], "expected no priority missing items"),
            (any("暂时都不涉及" in item for item in controls), "expected safe risk-control phrase"),
            (any("敏感配置" in item for item in non_actions), "expected sensitive-config non-action"),
        ],
    )


def check_requirement_readiness_user_format() -> SmokeResult:
    return check_text_command(
        "requirement-readiness-user-format",
        python_command(
            ".gstack/scripts/nontechnical_requirement_readiness.py",
            "--raw",
            "我按模板填了一版，你帮我看看还缺什么",
            "--format",
            "user",
        ),
        ["需求完整度检查", "整体判断", "已经说清楚", "还需要补充", "风险确认", "Codex 的下一步", "需要你确认", "这次不会做什么"],
        "Requirement readiness user format explains missing fields without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", " PR", "commit", "push", "merge"],
    )


def check_page_change_brief_json() -> SmokeResult:
    payload, details = load_json_command(
        "page-change-brief-json",
        python_command(
            ".gstack/scripts/nontechnical_page_change_brief.py",
            "--raw",
            "我想改一个已有页面，但是不知道该先给你什么信息",
            "--format",
            "json",
        ),
    )
    what_to_send = (payload or {}).get("what_to_send", [])
    template = (payload or {}).get("fill_in_template", [])
    non_actions = (payload or {}).get("non_actions", [])
    return check_conditions(
        "page-change-brief-json",
        "Page-change brief exposes fill-in fields and non-actions.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "page-change-brief-ready", "expected page-change-brief-ready status"),
            (any("页面位置" in item for item in what_to_send), "expected page location field"),
            (any("现在看到的问题" in item for item in what_to_send), "expected current problem field"),
            (any("你希望变成什么" in item for item in what_to_send), "expected desired change field"),
            (any("完成后怎么验收" in item for item in what_to_send), "expected acceptance field"),
            (any("这次不要碰" in item for item in template), "expected do-not-touch template field"),
            (any("敏感配置" in item for item in non_actions), "expected sensitive-config non-action"),
        ],
    )


def check_page_change_brief_user_format() -> SmokeResult:
    return check_text_command(
        "page-change-brief-user-format",
        python_command(
            ".gstack/scripts/nontechnical_page_change_brief.py",
            "--raw",
            "改页面要怎么描述，才能让你直接开工",
            "--format",
            "user",
        ),
        ["你不用懂技术", "页面位置", "现在看到的问题", "你希望变成什么", "我会这样验收", "这次不要碰", "Codex 的下一步", "需要你确认", "敏感配置"],
        "Page-change brief user format explains fill-in fields without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", " PR", "commit", "push", "merge"],
    )


def check_acceptance_plan_json() -> SmokeResult:
    payload, details = load_json_command(
        "acceptance-plan-json",
        python_command(
            ".gstack/scripts/nontechnical_acceptance_plan.py",
            "--raw",
            "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收，怎么验收",
            "--audience",
            "运营同事",
            "--success",
            "能按月份和 SKU 筛选并导出",
            "--non-goal",
            "不改生产数据库",
            "--format",
            "json",
        ),
    )
    checks = (payload or {}).get("acceptance_checks", [])
    actions = (payload or {}).get("user_actions_to_verify", [])
    expected = (payload or {}).get("expected_results", [])
    return check_conditions(
        "acceptance-plan-json",
        "Acceptance plan exposes checks, user actions, and expected results.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "ready-to-acceptance-plan", "expected ready-to-acceptance-plan status"),
            (isinstance(checks, list) and len(checks) >= 4, "expected at least four acceptance checks"),
            (any("筛选" in item or "导出" in item for item in checks), "expected filter/export acceptance checks"),
            (isinstance(actions, list) and len(actions) >= 3, "expected user actions to verify"),
            (isinstance(expected, list) and len(expected) >= 3, "expected expected results"),
        ],
    )


def check_acceptance_plan_user_format() -> SmokeResult:
    return check_text_command(
        "acceptance-plan-user-format",
        python_command(
            ".gstack/scripts/nontechnical_acceptance_plan.py",
            "--raw",
            "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收，怎么验收",
            "--audience",
            "运营同事",
            "--success",
            "能按月份和 SKU 筛选并导出",
            "--non-goal",
            "不改生产数据库",
            "--format",
            "user",
        ),
        ["可以这样验收", "你要实际看到 / 操作", "预期应该看到", "需要你确认", "风险说明"],
        "Acceptance plan user format explains acceptance without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI"],
    )


def check_visible_change_json() -> SmokeResult:
    payload, details = load_json_command(
        "visible-change-json",
        python_command(
            ".gstack/scripts/nontechnical_visible_change.py",
            "--raw",
            "我刷新了页面但没看到变化",
            "--format",
            "json",
        ),
    )
    status = (payload or {}).get("status")
    view_locations = (payload or {}).get("view_locations", [])
    next_actions = (payload or {}).get("codex_next_actions", [])
    confirmations = (payload or {}).get("needs_user_confirmation", [])
    return check_conditions(
        "visible-change-json",
        "Visible-change helper exposes location, refresh, and next actions.",
        payload,
        details,
        [
            (status in {"page-troubleshoot-ready", "not-page-change", "no-active-task"}, f"unexpected status={status}"),
            (isinstance(view_locations, list) and len(view_locations) >= 1, "expected view location guidance"),
            (isinstance(next_actions, list) and len(next_actions) >= 1, "expected Codex next actions"),
            (isinstance(confirmations, list) and len(confirmations) >= 1, "expected confirmation guidance"),
        ],
    )


def check_visible_change_user_format() -> SmokeResult:
    return check_text_command(
        "visible-change-user-format",
        python_command(
            ".gstack/scripts/nontechnical_visible_change.py",
            "--raw",
            "我刷新了页面但没看到变化",
            "--format",
            "user",
        ),
        ["Codex 的下一步", "需要你确认"],
        "Visible-change user format explains troubleshooting without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", "这个能力主要给谁用"],
    )


def check_ci_failure_json() -> SmokeResult:
    payload, details = load_json_command(
        "ci-failure-json",
        python_command(
            ".gstack/scripts/nontechnical_ci_failure.py",
            "--raw",
            "GitHub 检查失败了，帮我看下一步怎么办",
            "--format",
            "json",
        ),
    )
    actions = (payload or {}).get("what_codex_will_check", [])
    needs = (payload or {}).get("what_user_may_need_to_provide", [])
    non_actions = (payload or {}).get("non_actions", [])
    return check_conditions(
        "ci-failure-json",
        "CI failure helper exposes check type, next actions, and needed user detail.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "needs-ci-detail", "expected needs-ci-detail status"),
            ((payload or {}).get("detected_check") == "unknown", "expected unknown check before job/log is provided"),
            (isinstance(actions, list) and len(actions) >= 2, "expected Codex next actions"),
            (isinstance(needs, list) and any("失败检查名" in item for item in needs), "expected failed check name request"),
            (isinstance(non_actions, list) and any("敏感配置" in item for item in non_actions), "expected sensitive-config allowance note"),
        ],
    )


def check_ci_failure_user_format() -> SmokeResult:
    return check_text_command(
        "ci-failure-user-format",
        python_command(
            ".gstack/scripts/nontechnical_ci_failure.py",
            "--raw",
            "restricted-module 检查失败了",
            "--format",
            "user",
        ),
        ["先确认失败的是哪类检查", "受限业务模块检查", "Codex 的下一步", "需要你确认", "敏感配置"],
        "CI failure user format explains troubleshooting without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", " PR", "commit", "push", "merge"],
    )


def check_continue_runner_json() -> SmokeResult:
    payload, details = load_json_command_with_active_fixture(
        "continue-runner-json",
        python_command(
            ".gstack/scripts/nontechnical_continue.py",
            "--raw",
            "继续做",
            "--format",
            "json",
        ),
    )
    actions = (payload or {}).get("codex_next_actions", [])
    confirmations = (payload or {}).get("needs_user_confirmation", [])
    non_actions = (payload or {}).get("non_actions", [])
    auto_chain_status = (payload or {}).get("auto_chain_status", "")
    autonomy_condition = (any("不会每一步" in item for item in confirmations), "expected no repeated continue prompt guidance")
    subagent_condition = (any("subagent" in item for item in actions), "expected Codex-owned subagent decision")
    return check_conditions(
        "continue-runner-json",
        "Continue helper exposes current state, next actions, and non-actions.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "continue-current-task", "expected active fixture to continue current task"),
            (auto_chain_status == "continue-current-boundary", "expected continue-current-boundary auto chain status"),
            (isinstance(actions, list) and len(actions) >= 1, "expected Codex next actions"),
            subagent_condition,
            (isinstance(confirmations, list) and len(confirmations) >= 1, "expected confirmation guidance"),
            autonomy_condition,
            (isinstance(non_actions, list) and any("敏感配置" in item for item in non_actions), "expected sensitive-config non-action"),
        ],
    )


def check_continue_runner_completed_autochain_json() -> SmokeResult:
    payload, details = load_json_command_with_completed_fixture(
        "continue-runner-completed-autochain-json",
        python_command(
            ".gstack/scripts/nontechnical_continue.py",
            "--raw",
            "继续做",
            "--format",
            "json",
        ),
    )
    actions = (payload or {}).get("codex_next_actions", [])
    confirmations = (payload or {}).get("needs_user_confirmation", [])
    return check_conditions(
        "continue-runner-completed-autochain-json",
        "Completed low-risk task can auto-chain the next low-risk slice.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "current-task-complete", "expected completed fixture status"),
            ((payload or {}).get("auto_chain_status") == "auto-start-next-low-risk-boundary", "expected low-risk auto-chain status"),
            (any("自动选择" in item or "下一段" in item for item in actions), "expected next low-risk slice action"),
            (any("暂时不需要" in item for item in confirmations), "expected no user confirmation for low-risk auto-chain"),
        ],
    )


def check_continue_runner_user_format() -> SmokeResult:
    return check_text_command(
        "continue-runner-user-format",
        python_command(
            ".gstack/scripts/nontechnical_continue.py",
            "--raw",
            "那就先做第一步",
            "--format",
            "user",
        ),
        ["我会按继续推进处理", "Codex 的下一步", "需要你确认", "这次不会做什么", "敏感配置"],
        "Continue helper user format explains continuation without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", " PR", "commit", "push", "merge"],
    )


def check_mode_control_json() -> SmokeResult:
    cases = [
        (
            "manual",
            "这次先别改代码，只给我方案",
            "手动控制",
            "manual",
            "current-task",
        ),
        (
            "checkpoint",
            "这次关键地方问我，其他你继续推进",
            "关键确认",
            "checkpoint",
            "current-task",
        ),
        (
            "codex-led",
            "这次全自动做完",
            "自主执行",
            "codex-led",
            "current-task",
        ),
    ]
    details: list[str] = []
    failures: list[str] = []
    for label, raw, expected_mode, expected_enum, expected_scope in cases:
        payload, command_details = load_json_command(
            "mode-control-json",
            python_command(".gstack/scripts/nontechnical_mode_control.py", "--raw", raw, "--format", "json"),
        )
        details.extend(f"{label}: {detail}" for detail in command_details)
        if payload is None:
            failures.append(f"{label}: invalid json")
            continue
        non_actions = payload.get("non_actions", [])
        if payload.get("mode") != expected_mode:
            failures.append(f"{label}: expected mode {expected_mode}, got {payload.get('mode')}")
        if payload.get("internal_enum") != expected_enum:
            failures.append(f"{label}: expected enum {expected_enum}, got {payload.get('internal_enum')}")
        if payload.get("scope") != expected_scope:
            failures.append(f"{label}: expected scope {expected_scope}, got {payload.get('scope')}")
        if payload.get("writes_local_mode") is not False:
            failures.append(f"{label}: expected writes_local_mode=false")
        if not any("敏感配置" in item for item in non_actions):
            failures.append(f"{label}: expected sensitive-config non-action")
    if failures:
        return fail("mode-control-json", "Mode-control helper returned the wrong mode.", [*details, *failures])
    return ok("mode-control-json", "Mode-control helper detects modes without writing local state.", details)


def check_mode_control_user_format() -> SmokeResult:
    return check_text_command(
        "mode-control-user-format",
        python_command(
            ".gstack/scripts/nontechnical_mode_control.py",
            "--raw",
            "这次先别改代码，只给我方案",
            "--format",
            "user",
        ),
        ["当前协作模式", "手动控制", "不改代码", "需要你确认", "这次不会做什么", "敏感配置"],
        "Mode-control user format explains collaboration mode without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", " PR", "commit", "push", "merge"],
    )


def check_recommendation_json() -> SmokeResult:
    cases = [
        (
            "choose-solution",
            "我不懂技术，你帮我选一个最合适的方案",
            "先固定目标和验收方式，再做最小可见路径",
            [],
        ),
        (
            "options",
            "这个需求有几种做法你直接推荐一个，不要让我选技术方案",
            "先固定目标和验收方式，再做最小可见路径",
            [],
        ),
        (
            "first-step",
            "我不知道该先做页面、接数据还是做导出，你替我决定第一步",
            "先做最小可见页面 / 可点击路径",
            ["接真实数据 / 补接口", "导出能力"],
        ),
    ]
    details: list[str] = []
    failures: list[str] = []
    for label, raw, expected_recommendation, expected_not_chosen in cases:
        payload, command_details = load_json_command(
            "recommendation-json",
            python_command(".gstack/scripts/nontechnical_recommendation.py", "--raw", raw, "--format", "json"),
        )
        details.extend(f"{label}: {detail}" for detail in command_details)
        if payload is None:
            failures.append(f"{label}: invalid json")
            continue
        not_chosen = payload.get("options_not_chosen_now", [])
        non_actions = payload.get("non_actions", [])
        if payload.get("recommended_option") != expected_recommendation:
            failures.append(f"{label}: expected recommendation {expected_recommendation}, got {payload.get('recommended_option')}")
        if not payload.get("first_safe_step"):
            failures.append(f"{label}: expected first_safe_step")
        for item in expected_not_chosen:
            if item not in not_chosen:
                failures.append(f"{label}: expected not chosen {item}")
        if not any("敏感配置" in item for item in non_actions):
            failures.append(f"{label}: expected sensitive-config non-action")
    if failures:
        return fail("recommendation-json", "Recommendation helper returned the wrong recommendation.", [*details, *failures])
    return ok("recommendation-json", "Recommendation helper exposes recommended option and first safe step.", details)


def check_recommendation_user_format() -> SmokeResult:
    cases = [
        (
            "choose-solution",
            ["--raw", "我不懂技术，你帮我选一个最合适的方案", "--format", "user"],
            ["我会先给推荐方案", "推荐方案", "为什么推荐", "第一安全步", "不让你选技术实现", "需要你确认"],
        ),
        (
            "first-step",
            ["--raw", "我不知道该先做页面、接数据还是做导出，你替我决定第一步", "--format", "user"],
            ["先做最小可见页面 / 可点击路径", "暂不选择", "接真实数据 / 补接口", "导出能力", "第一安全步", "这次不会做什么"],
        ),
    ]
    details: list[str] = []
    failures: list[str] = []
    forbidden_fragments = ["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", " PR", "commit", "push", "merge"]
    for label, args, expected_fragments in cases:
        result = run(python_command(".gstack/scripts/nontechnical_recommendation.py", *args))
        details.append(f"{label}: command: {sys.executable} .gstack/scripts/nontechnical_recommendation.py {' '.join(args)}")
        if result.returncode != 0:
            failures.append(f"{label}: command failed")
            failures.append(result.stderr.strip() or result.stdout.strip())
            continue
        missing = [fragment for fragment in expected_fragments if fragment not in result.stdout]
        if missing:
            failures.append(f"{label}: missing " + ", ".join(missing))
        forbidden = [fragment for fragment in forbidden_fragments if fragment in result.stdout]
        if forbidden:
            failures.append(f"{label}: forbidden " + ", ".join(forbidden))
    if failures:
        return fail("recommendation-user-format", "Recommendation user format exposes internal details.", [*details, *failures])
    return ok("recommendation-user-format", "Recommendation user format explains solution choice without internal terms.", details)


def check_scope_change_json() -> SmokeResult:
    cases = [
        (
            "scope-reduction",
            "这个需求先不要做导出，只保留搜索和筛选",
            "scope-adjustment",
            ["搜索", "筛选"],
            ["导出"],
            [],
        ),
        (
            "prototype-first",
            "我想把刚才的需求改一下，不接真实数据，先做可点击页面",
            "prototype-first",
            ["可点击页面"],
            ["真实数据接入"],
            [],
        ),
        (
            "defer-real-data",
            "这次先做一个能点的版本，数据先用假的，后面再接真实数据",
            "prototype-first",
            ["可点击页面", "假数据 / mock 数据"],
            ["真实数据接入"],
            ["真实数据接入"],
        ),
        (
            "demo-fake-data",
            "先给我一个能点的 demo，数据用假的",
            "prototype-first",
            ["demo", "可点击页面", "假数据 / mock 数据"],
            ["真实数据接入"],
            [],
        ),
        (
            "static-no-interface",
            "先做静态页面看看效果，不接接口",
            "prototype-first",
            ["静态页面"],
            ["接口接入"],
            [],
        ),
        (
            "scope-expansion",
            "刚才说的不对，受限业务模块可以动，但不要动数据库",
            "scope-expansion",
            ["受限业务模块"],
            ["数据库"],
            [],
        ),
    ]
    details: list[str] = []
    failures: list[str] = []
    for label, raw, expected_type, expected_included, expected_excluded, expected_deferred in cases:
        payload, command_details = load_json_command(
            "scope-change-json",
            python_command(".gstack/scripts/nontechnical_scope_change.py", "--raw", raw, "--format", "json"),
        )
        details.extend(f"{label}: {detail}" for detail in command_details)
        if payload is None:
            failures.append(f"{label}: invalid json")
            continue
        included = payload.get("included_now", [])
        excluded = payload.get("excluded_now", [])
        deferred = payload.get("deferred_later", [])
        non_actions = payload.get("non_actions", [])
        if payload.get("change_type") != expected_type:
            failures.append(f"{label}: expected type {expected_type}, got {payload.get('change_type')}")
        for item in expected_included:
            if item not in included:
                failures.append(f"{label}: expected included {item}")
        for item in expected_excluded:
            if item not in excluded:
                failures.append(f"{label}: expected excluded {item}")
        for item in expected_deferred:
            if item not in deferred:
                failures.append(f"{label}: expected deferred {item}")
        if not any("敏感配置" in item for item in non_actions):
            failures.append(f"{label}: expected sensitive-config non-action")
    if failures:
        return fail("scope-change-json", "Scope-change helper returned the wrong scope.", [*details, *failures])
    return ok("scope-change-json", "Scope-change helper exposes included, excluded, and deferred scope.", details)


def check_scope_change_user_format() -> SmokeResult:
    cases = [
        (
            "scope-reduction",
            ["--raw", "这个需求先不要做导出，只保留搜索和筛选", "--format", "user"],
            ["我会按需求范围调整处理", "这次先做 / 保留", "搜索", "筛选", "这次先不做 / 排除", "导出", "需要你确认", "这次不会做什么"],
        ),
        (
            "prototype-first",
            ["--raw", "这次先做一个能点的版本，数据先用假的，后面再接真实数据", "--format", "user"],
            ["可点击页面", "假数据 / mock 数据", "后续再做", "真实数据接入", "按可点击 / mock 数据版本理解", "需要你确认"],
        ),
        (
            "static-no-interface",
            ["--raw", "先做静态页面看看效果，不接接口", "--format", "user"],
            ["静态页面", "接口接入", "把原型 / demo / 静态页面当作先看效果的版本", "需要你确认"],
        ),
    ]
    details: list[str] = []
    failures: list[str] = []
    forbidden_fragments = ["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", " PR", "commit", "push", "merge"]
    for label, args, expected_fragments in cases:
        result = run(python_command(".gstack/scripts/nontechnical_scope_change.py", *args))
        details.append(f"{label}: command: {sys.executable} .gstack/scripts/nontechnical_scope_change.py {' '.join(args)}")
        if result.returncode != 0:
            failures.append(f"{label}: command failed")
            failures.append(result.stderr.strip() or result.stdout.strip())
            continue
        missing = [fragment for fragment in expected_fragments if fragment not in result.stdout]
        if missing:
            failures.append(f"{label}: missing " + ", ".join(missing))
        forbidden = [fragment for fragment in forbidden_fragments if fragment in result.stdout]
        if forbidden:
            failures.append(f"{label}: forbidden " + ", ".join(forbidden))
    if failures:
        return fail("scope-change-user-format", "Scope-change user format exposes internal details.", [*details, *failures])
    return ok("scope-change-user-format", "Scope-change user format explains scope changes without internal terms.", details)


def check_task_list_json() -> SmokeResult:
    payload, details = load_json_command(
        "task-list-json",
        python_command(
            ".gstack/scripts/nontechnical_task_list.py",
            "--raw",
            "帮我列一下现在还没做完的任务",
            "--format",
            "json",
        ),
    )
    tasks = (payload or {}).get("tasks", [])
    non_actions = (payload or {}).get("non_actions", [])
    return check_conditions(
        "task-list-json",
        "Task-list helper exposes a read-only task overview.",
        payload,
        details,
        [
            ((payload or {}).get("status") in {"has-open-tasks", "no-open-tasks", "no-matching-open-tasks"}, "unexpected task-list status"),
            (isinstance((payload or {}).get("total_tasks"), int), "expected integer total_tasks"),
            (isinstance((payload or {}).get("open_tasks"), int), "expected integer open_tasks"),
            (isinstance((payload or {}).get("blocked_tasks"), int), "expected integer blocked_tasks"),
            (isinstance(tasks, list), "expected tasks list"),
            (any("共享任务状态文件" in item for item in non_actions), "expected no shared-status non-action"),
            (any("敏感配置" in item for item in non_actions), "expected sensitive-config non-action"),
        ],
    )


def check_task_list_user_format() -> SmokeResult:
    return check_text_command(
        "task-list-user-format",
        python_command(
            ".gstack/scripts/nontechnical_task_list.py",
            "--raw",
            "我想先看看有哪些历史需求和未完成任务",
            "--format",
            "user",
        ),
        ["任务概览", "未完成任务", "卡住任务", "优先看的任务", "Codex 的下一步", "这次不会做什么"],
        "Task-list user format explains task inventory without internal terms.",
        forbidden_fragments=[
            "python3",
            ".gstack",
            "boundary",
            "Boundary",
            "gate",
            "spec",
            "JSON",
            "建议 lane",
            "git",
            "CLI",
            " PR",
            "commit",
            "push",
            "merge",
        ],
    )


def check_team_sync_json() -> SmokeResult:
    payload, details = load_json_command(
        "team-sync-json",
        python_command(
            ".gstack/scripts/nontechnical_team_sync.py",
            "--raw",
            "帮我把团队所有人的任务状态同步起来，但不要引入数据库，也不要动受限业务模块",
            "--format",
            "json",
        ),
    )
    notes = (payload or {}).get("feasibility_notes", [])
    confirmations = (payload or {}).get("needs_user_confirmation", [])
    non_actions = (payload or {}).get("non_actions", [])
    scopes = (payload or {}).get("forbidden_business_scopes", [])
    return check_conditions(
        "team-sync-json",
        "Team-sync helper exposes no-database limits, confirmation, and forbidden scope.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "needs-sync-model-confirmation", "expected needs-sync-model-confirmation status"),
            ((payload or {}).get("no_database_requested") is True, "expected no_database_requested=true"),
            (any("实时多人同步" in item for item in notes), "expected no realtime sync note"),
            (any("只读状态视图" in item for item in notes), "expected repo evidence readonly view note"),
            (any("repo evidence" in item for item in confirmations), "expected repo evidence confirmation"),
            (any("受限业务模块" in item for item in scopes), "expected restricted-module forbidden business scope"),
            (any("敏感配置" in item for item in non_actions), "expected sensitive-config non-action"),
        ],
    )


def check_team_sync_user_format() -> SmokeResult:
    return check_text_command(
        "team-sync-user-format",
        python_command(
            ".gstack/scripts/nontechnical_team_sync.py",
            "--raw",
            "帮我把团队所有人的任务状态同步起来，但不要引入数据库，也不要动受限业务模块",
            "--format",
            "user",
        ),
        ["团队状态同步需求", "不引入数据库", "不能承诺实时多人同步", "只读状态视图", "需要你确认", "受限业务模块"],
        "Team-sync user format explains no-database limits without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", " PR", "commit", "push", "merge", "app/restricted-module"],
    )


def check_delivery_summary_json() -> SmokeResult:
    payload, details = load_json_command(
        "delivery-summary-json",
        python_command(
            ".gstack/scripts/nontechnical_delivery_summary.py",
            "--raw",
            "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险",
            "--format",
            "json",
        ),
    )
    changed = (payload or {}).get("changed_items", [])
    actions = (payload or {}).get("acceptance_actions", [])
    risks = (payload or {}).get("risks_and_non_actions", [])
    confirmations = (payload or {}).get("needs_user_confirmation", [])
    suggestions = (payload or {}).get("next_step_suggestions", [])
    autonomy = (payload or {}).get("next_step_autonomy", "")
    return check_conditions(
        "delivery-summary-json",
        "Delivery summary helper exposes shareable summary fields.",
        payload,
        details,
        [
            ((payload or {}).get("status") in {"ready-to-share", "progress-summary", "no-task"}, "unexpected delivery summary status"),
            (isinstance(changed, list) and len(changed) >= 1, "expected changed items"),
            (isinstance(actions, list) and len(actions) >= 1, "expected acceptance actions"),
            (isinstance(risks, list) and len(risks) >= 1, "expected risks and non-actions"),
            (isinstance(suggestions, list) and len(suggestions) >= 1, "expected next-step suggestions"),
            (autonomy in {"auto-continue-low-risk", "continue-current-task", "needs-current-task"}, "expected next-step autonomy field"),
            (isinstance(confirmations, list) and len(confirmations) >= 1, "expected confirmation guidance"),
        ],
    )


def check_delivery_summary_autonomy_json() -> SmokeResult:
    payload, details = load_json_command_with_completed_fixture(
        "delivery-summary-autonomy-json",
        python_command(
            ".gstack/scripts/nontechnical_delivery_summary.py",
            "--raw",
            "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险",
            "--format",
            "json",
        ),
    )
    suggestions = (payload or {}).get("next_step_suggestions", [])
    confirmations = (payload or {}).get("needs_user_confirmation", [])
    return check_conditions(
        "delivery-summary-autonomy-json",
        "Delivery summary next-step advice distinguishes auto-continuation from user confirmation.",
        payload,
        details,
        [
            ((payload or {}).get("status") == "ready-to-share", "expected completed task summary"),
            ((payload or {}).get("next_step_autonomy") == "auto-continue-low-risk", "expected low-risk auto continuation"),
            (any("不需要你再说" in item for item in suggestions), "expected no repeated continue advice"),
            (any("停下来让你确认" in item for item in suggestions), "expected high-risk stop condition advice"),
            (any("暂时不需要" in item for item in confirmations), "expected no immediate confirmation"),
        ],
    )


def check_delivery_summary_user_format() -> SmokeResult:
    return check_text_command(
        "delivery-summary-user-format",
        python_command(
            ".gstack/scripts/nontechnical_delivery_summary.py",
            "--raw",
            "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险",
            "--format",
            "user",
        ),
        ["可以直接这样发给团队", "本次交付", "这次改了什么", "怎么验收", "风险和未做", "下一步建议", "需要你确认"],
        "Delivery summary user format explains completion summary without internal terms.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI", " PR", "commit", "push", "merge"],
    )


def check_formal_kickoff_json() -> SmokeResult:
    cases = [
        (
            "complex",
            [
                "--raw",
                "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
                "--audience",
                "运营同事",
                "--success",
                "能看到按月份和 SKU 过滤后的结果",
                "--non-goal",
                "不改生产数据库",
                "--topic",
                "formal-kickoff-smoke",
                "--dry-run",
                "--ai-reviewed",
            ],
            "ready-to-write",
            "standard",
            True,
        ),
        (
            "risk",
            ["--raw", "帮我把线上数据同步一下", "--dry-run"],
            "pause-for-risk",
            "discovery",
            False,
        ),
        (
            "not-reviewed",
            [
                "--raw",
                "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
                "--audience",
                "运营同事",
                "--success",
                "能看到按月份和 SKU 过滤后的结果",
                "--non-goal",
                "不改生产数据库",
                "--topic",
                "formal-kickoff-not-reviewed-smoke",
                "--dry-run",
            ],
            "preview-needs-codex-review",
            "standard",
            False,
        ),
    ]
    details: list[str] = []
    failures: list[str] = []
    for label, args, expected_status, expected_lane, expected_can_write in cases:
        payload, command_details = load_json_command(
            "formal-kickoff-json",
            python_command(".gstack/scripts/nontechnical_formal_kickoff.py", *args, "--format", "json"),
        )
        details.extend(f"{label}: {detail}" for detail in command_details)
        if payload is None:
            failures.append(f"{label}: invalid json")
            continue
        if payload.get("status") != expected_status:
            failures.append(f"{label}: expected status {expected_status}, got {payload.get('status')}")
        if payload.get("recommended_lane") != expected_lane:
            failures.append(f"{label}: expected lane {expected_lane}, got {payload.get('recommended_lane')}")
        if payload.get("can_write") is not expected_can_write:
            failures.append(f"{label}: expected can_write={expected_can_write}, got {payload.get('can_write')}")
        paths = payload.get("paths") or {}
        if label == "complex" and not paths.get("boundary", "").endswith(".md"):
            failures.append(f"{label}: expected boundary path in payload")
    if failures:
        return fail("formal-kickoff-json", "Formal kickoff helper returned the wrong state.", [*details, *failures])
    return ok("formal-kickoff-json", "Formal kickoff helper classifies write readiness correctly.", details)


def check_formal_kickoff_user_format() -> SmokeResult:
    cases = [
        (
            "complex",
            [
                "--raw",
                "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收",
                "--audience",
                "运营同事",
                "--success",
                "能看到按月份和 SKU 过滤后的结果",
                "--non-goal",
                "不改生产数据库",
                "--topic",
                "formal-kickoff-user-smoke",
                "--dry-run",
                "--ai-reviewed",
                "--format",
                "user",
            ],
            ["正式开工包", "完成后可以这样验收"],
        ),
        (
            "risk",
            ["--raw", "帮我把线上数据同步一下", "--dry-run", "--format", "user"],
            ["先不生成正式开工包", "还需要你确认"],
        ),
    ]
    details: list[str] = []
    failures: list[str] = []
    forbidden_fragments = ["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI"]
    for label, args, expected_fragments in cases:
        result = run(python_command(".gstack/scripts/nontechnical_formal_kickoff.py", *args))
        details.append(f"{label}: command: {sys.executable} .gstack/scripts/nontechnical_formal_kickoff.py {' '.join(args)}")
        if result.returncode != 0:
            failures.append(f"{label}: command failed")
            failures.append(result.stderr.strip() or result.stdout.strip())
            continue
        missing = [fragment for fragment in expected_fragments if fragment not in result.stdout]
        if missing:
            failures.append(f"{label}: missing " + ", ".join(missing))
        forbidden = [fragment for fragment in forbidden_fragments if fragment in result.stdout]
        if forbidden:
            failures.append(f"{label}: forbidden " + ", ".join(forbidden))
    if failures:
        return fail("formal-kickoff-user-format", "Formal kickoff user format exposes internal details.", [*details, *failures])
    return ok("formal-kickoff-user-format", "Formal kickoff user format is suitable for users.", details)


def check_guided_kickoff_template() -> SmokeResult:
    return check_text_command(
        "guided-kickoff-template",
        python_command(".gstack/scripts/nontechnical_guided_kickoff.py", "--format", "user"),
        ["复杂需求向导", "谁会用", "想完成什么", "成功后第一眼看到", "怎么验收", "这次不会做什么"],
        "Guided kickoff prints a fill-in template for nontechnical users.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI"],
    )


def check_guided_kickoff_plan() -> SmokeResult:
    return check_text_command(
        "guided-kickoff-plan",
        python_command(
            ".gstack/scripts/nontechnical_guided_kickoff.py",
            "--raw",
            "我想做一个完整的经营看板，支持筛选、导出和多人验收",
            "--audience",
            "运营同事",
            "--success",
            "能按月份和 SKU 筛选并导出",
            "--non-goal",
            "不改生产数据库",
            "--format",
            "user",
        ),
        ["执行计划", "推进顺序", "Codex 可以自动处理", "完成后可以这样验收", "不改生产数据库"],
        "Guided kickoff turns a complete complex request into an execution plan.",
        forbidden_fragments=["python3", ".gstack", "boundary", "gate", "spec", "JSON", "建议 lane", "git", "CLI"],
    )


def check_guided_kickoff_formal_json() -> SmokeResult:
    payload, details = load_json_command(
        "guided-kickoff-formal-json",
        python_command(
            ".gstack/scripts/nontechnical_guided_kickoff.py",
            "--raw",
            "我已经说清楚了，正式开工做一个经营看板，支持筛选、导出和多人验收",
            "--audience",
            "运营同事",
            "--success",
            "能按月份和 SKU 筛选并导出",
            "--non-goal",
            "不改生产数据库",
            "--formal",
            "--ai-reviewed",
            "--format",
            "json",
        ),
    )
    return check_conditions(
        "guided-kickoff-formal-json",
        "Guided kickoff can return a formal kickoff preview after AI review.",
        payload,
        details,
        [
            ((payload or {}).get("stage") == "formal-kickoff-preview", "expected formal-kickoff-preview stage"),
            ((payload or {}).get("helper_entry") == "nontechnical_formal_kickoff.user", "expected formal kickoff helper"),
            ((payload or {}).get("helper_status") == "ok", "expected ok helper status"),
            ((payload or {}).get("needs_user_confirmation") is False, "expected no immediate confirmation"),
            ("正式开工包" in (payload or {}).get("user_response", ""), "expected formal kickoff copy"),
        ],
    )


def run_smoke() -> list[SmokeResult]:
    return [
        check_broad_intake(),
        check_complex_intake(),
        check_small_intake(),
        check_high_risk_intake(),
        check_risk_confirmed_intake(),
        check_dashboard_explain(),
        check_dashboard_verify(),
        check_doctor_explain(),
        check_home_json(),
        check_home_user_format(),
        check_implementation_readiness_json(),
        check_implementation_readiness_user_format(),
        check_confirmation_brief_json(),
        check_confirmation_brief_user_format(),
        check_confirmation_response_json(),
        check_confirmation_response_user_format(),
        check_pause_control_json(),
        check_pause_control_user_format(),
        check_undo_request_json(),
        check_undo_request_user_format(),
        check_complex_task_starter(),
        check_risky_task_starter(),
        check_complex_task_starter_user_format(),
        check_complex_task_starter_acceptance_json(),
        check_risky_task_starter_user_format(),
        check_risk_confirmed_task_starter(),
        check_risk_confirmed_task_starter_user_format(),
        check_risk_insufficient_task_starter(),
        check_forbidden_scope_mapping(),
        check_forbidden_scope_user_format(),
        check_smoke_user_format(),
        check_intent_router_json(),
        check_intent_router_user_format(),
        check_next_step_json(),
        check_next_step_user_format(),
        check_execution_plan_json(),
        check_execution_plan_user_format(),
        check_task_breakdown_json(),
        check_task_breakdown_user_format(),
        check_first_use_json(),
        check_first_use_user_format(),
        check_requirement_brief_json(),
        check_requirement_brief_user_format(),
        check_requirement_readiness_json(),
        check_requirement_readiness_user_format(),
        check_page_change_brief_json(),
        check_page_change_brief_user_format(),
        check_acceptance_plan_json(),
        check_acceptance_plan_user_format(),
        check_visible_change_json(),
        check_visible_change_user_format(),
        check_ci_failure_json(),
        check_ci_failure_user_format(),
        check_continue_runner_json(),
        check_continue_runner_completed_autochain_json(),
        check_continue_runner_user_format(),
        check_mode_control_json(),
        check_mode_control_user_format(),
        check_recommendation_json(),
        check_recommendation_user_format(),
        check_scope_change_json(),
        check_scope_change_user_format(),
        check_task_list_json(),
        check_task_list_user_format(),
        check_team_sync_json(),
        check_team_sync_user_format(),
        check_delivery_summary_json(),
        check_delivery_summary_autonomy_json(),
        check_delivery_summary_user_format(),
        check_formal_kickoff_json(),
        check_formal_kickoff_user_format(),
        check_guided_kickoff_template(),
        check_guided_kickoff_plan(),
        check_guided_kickoff_formal_json(),
    ]


def overall_status(results: list[SmokeResult]) -> str:
    return "fail" if any(result.status == "fail" for result in results) else "ok"


def render_markdown(results: list[SmokeResult]) -> str:
    lines = ["# natural language development smoke", ""]
    for result in results:
        badge = "OK" if result.status == "ok" else "FAIL"
        lines.append(f"- [{badge}] `{result.check_id}`: {result.message}")
        for detail in result.details:
            lines.append(f"  - {detail}")
    lines.append("")
    lines.append(f"Overall: `{overall_status(results)}`")
    return "\n".join(lines)


def render_json(results: list[SmokeResult]) -> str:
    payload = {
        "overall": overall_status(results),
        "results": [asdict(result) for result in results],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_user(results: list[SmokeResult]) -> str:
    failed = [result for result in results if result.status == "fail"]
    if not failed:
        lines = [
            "非技术开发关键路径检查通过。",
            "",
            "已覆盖：",
        ]
        lines.extend(f"- {line}" for line in USER_COVERAGE_LINES)
        lines.extend(
            [
                "",
                "需要你确认：",
                "- 没有发现需要你确认的阻塞。",
            ]
        )
        return "\n".join(lines)

    failed_labels: list[str] = []
    seen_labels: set[str] = set()
    for result in failed:
        label = USER_CHECK_LABELS.get(result.check_id, "有一项用户体验检查没有通过")
        if label not in seen_labels:
            failed_labels.append(label)
            seen_labels.add(label)

    lines = [
        "非技术开发关键路径检查未通过。",
        "",
        "需要 Codex 修复的体验项：",
    ]
    lines.extend(f"- {label}" for label in failed_labels)
    lines.extend(
        [
            "",
            "下一步：",
            "- Codex 应先修复这些体验项，再重新检查。",
            "- 只有涉及真实数据、线上环境、数据库、外部服务或代码提交流程时，才需要你确认。",
        ]
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    results = run_smoke()
    if args.format == "json":
        print(render_json(results))
    elif args.format == "user":
        print(render_user(results))
    else:
        print(render_markdown(results))
    return 1 if overall_status(results) == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
