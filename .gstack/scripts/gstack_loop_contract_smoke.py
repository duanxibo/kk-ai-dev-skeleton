#!/usr/bin/env python3
"""Smoke test the Loop Engineering plan / advance / run contract.

This script checks deterministic local behavior only. It does not edit task
state, connect to services, run git workflow actions, or execute production
operations.
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

import gstack_loop


REPO_ROOT = Path(__file__).resolve().parents[2]
V6_BOUNDARY = ".gstack/task-boundaries/2026-06-14_loop-engineering-v6-contract-tests.md"
V7_BOUNDARY = ".gstack/task-boundaries/2026-06-15_loop-engineering-v7-chat-first-runtime.md"
V8_BOUNDARY = ".gstack/task-boundaries/2026-06-15_subagent-timeout-resilience.md"
V9_BOUNDARY = ".gstack/task-boundaries/2026-06-15_eng-review-auto-decisioner.md"
V10_BOUNDARY = ".gstack/task-boundaries/2026-06-17_stage-write-back-closure.md"
V11_BOUNDARY = ".gstack/task-boundaries/2026-06-17_subagent-auto-orchestration.md"
V12_BOUNDARY = ".gstack/task-boundaries/2026-06-17_test-repair-loop-runtime.md"
V13_BOUNDARY = ".gstack/task-boundaries/2026-06-17_chat-authorization-runtime.md"
V14_BOUNDARY = ".gstack/task-boundaries/2026-06-17_chat-first-loop-smoke.md"
V15_BOUNDARY = ".gstack/task-boundaries/2026-06-17_natural-language-loop-runtime.md"
V6_VERIFICATION_COMMANDS = [
    "python3 -m py_compile .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user",
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query loop-engineering-v6",
    "python3 .gstack/scripts/gstack_loop.py advance --dry-run --format json --query loop-engineering-v6",
    "python3 .gstack/scripts/spec_sync_guard.py",
    "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD",
]
V7_VERIFICATION_COMMANDS = [
    "python3 -m py_compile .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user",
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query loop-engineering-v7",
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query loop-engineering-v7",
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 我确认 --format json",
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 提交并推送 --format json",
    "python3 .gstack/scripts/gstack_loop.py advance --dry-run --format json --query loop-engineering-v7",
    "python3 .gstack/scripts/gstack_loop.py run --dry-run --format json --query loop-engineering-v7",
    "python3 .gstack/scripts/spec_sync_guard.py",
    "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD",
]
V8_VERIFICATION_COMMANDS = [
    "python3 -m py_compile .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user",
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query subagent-timeout-resilience",
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query subagent-timeout-resilience",
    "python3 .gstack/scripts/spec_sync_guard.py",
    "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD",
]
V9_VERIFICATION_COMMANDS = [
    "python3 -m py_compile .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user",
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query eng-review-auto-decisioner",
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query eng-review-auto-decisioner",
    "python3 .gstack/scripts/gstack_loop.py eng-review --format json --query eng-review-auto-decisioner",
    "python3 .gstack/scripts/gstack_loop.py eng-review --format user --query eng-review-auto-decisioner",
    "python3 .gstack/scripts/gstack_loop.py eng-review --format json --evidence .gstack/reviews/2026-06-15_eng-review-auto-decisioner-eng-review.md",
    "python3 .gstack/scripts/spec_sync_guard.py",
    "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD",
]
V10_VERIFICATION_COMMANDS = [
    "python3 -m py_compile .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user",
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query stage-write-back-closure",
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query stage-write-back-closure",
    "python3 .gstack/scripts/gstack_loop.py write-back --dry-run --format json --query stage-write-back-closure --evidence .gstack/scripts/gstack_loop.py",
    "python3 .gstack/scripts/gstack_loop.py write-back --dry-run --format user --query stage-write-back-closure --evidence .gstack/scripts/gstack_loop.py",
    "python3 .gstack/scripts/spec_sync_guard.py",
    "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD",
]
V11_VERIFICATION_COMMANDS = [
    "python3 -m py_compile .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user",
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query subagent-auto-orchestration",
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query subagent-auto-orchestration",
    "python3 .gstack/scripts/gstack_loop.py subagents --format json --query subagent-auto-orchestration",
    "python3 .gstack/scripts/gstack_loop.py subagents --format user --query subagent-auto-orchestration",
    "python3 .gstack/scripts/spec_sync_guard.py",
    "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD",
]
V12_VERIFICATION_COMMANDS = [
    "python3 -m py_compile .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user",
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query test-repair-loop-runtime",
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query test-repair-loop-runtime",
    "python3 .gstack/scripts/gstack_loop.py repair-loop --dry-run --format json --query test-repair-loop-runtime",
    "python3 .gstack/scripts/gstack_loop.py repair-loop --dry-run --format user --query test-repair-loop-runtime",
    "python3 .gstack/scripts/spec_sync_guard.py",
    "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD",
]
V13_VERIFICATION_COMMANDS = [
    "python3 -m py_compile .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user",
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query chat-authorization-runtime",
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query chat-authorization-runtime",
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 继续做 --format json",
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 我确认 --format json",
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 提交并推送 --format json",
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 不要提交也不要推送 --format json",
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 发布到生产 --format json",
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 不改数据库 --format json",
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 撤销刚才的改动 --format json",
    "python3 .gstack/scripts/spec_sync_guard.py",
    "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD",
]
V14_VERIFICATION_COMMANDS = [
    "python3 -m py_compile .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user",
    "python3 .gstack/scripts/gstack_loop.py chat-smoke --format json",
    "python3 .gstack/scripts/gstack_loop.py chat-smoke --format user",
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query chat-first-loop-smoke",
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query chat-first-loop-smoke",
    "python3 .gstack/scripts/spec_sync_guard.py",
    "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD",
    "git diff --check",
]
V15_VERIFICATION_COMMANDS = [
    "python3 -m py_compile .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json",
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user",
    "python3 .gstack/scripts/gstack_loop.py nl-smoke --format json",
    "python3 .gstack/scripts/gstack_loop.py nl-smoke --format user",
    "python3 .gstack/scripts/natural_language_dev_smoke.py --format json",
    "python3 .gstack/scripts/natural_language_dev_smoke.py --format user",
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query natural-language-loop-runtime",
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query natural-language-loop-runtime",
    "python3 .gstack/scripts/spec_sync_guard.py",
    "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD",
    "git diff --check",
]


@dataclass(frozen=True)
class ContractResult:
    check_id: str
    status: str
    message: str
    details: list[str]


USER_COVERAGE_LINES = [
    "plan 输出稳定的 schema 和 planner 版本。",
    "advance 输出阶段决策、成功后阶段、证据目标和停止原因。",
    "run 输出受控本地验证报告和命令摘要。",
    "每个 gstack 阶段都有明确的执行策略，不会把需求、设计或实现交给脚本自动施工。",
    "非 active、blocked、evidence 缺失和未知阶段不会执行命令。",
    "自递归 run / advance --execute 会被跳过。",
    "空 Verification 不会被误判为通过。",
    "默认 dry-run，不会默认真实执行本地验证。",
    "V6 boundary 的 Verification 命令全部在受控 allowlist 中。",
    "V7 boundary 的 chat-first、授权识别和 dry-run 命令全部在受控 allowlist 中。",
    "V8 boundary 的 subagent timeout 修复命令全部在受控 allowlist 中。",
    "V9 boundary 的 eng-review 自动工程决策器命令全部在受控 allowlist 中。",
    "eng-review decisioner schema、策略和 evidence checker 已被契约测试覆盖。",
    "V10 boundary 的阶段写回闭环命令全部在受控 allowlist 中。",
    "write-back schema、当前阶段约束、dry-run 和 evidence 拒绝条件已被契约测试覆盖。",
    "V11 boundary 的 subagent 自动编排命令全部在受控 allowlist 中。",
    "subagents schema、自动分工、timeout contract 和 evidence 回收规则已被契约测试覆盖。",
    "V12 boundary 的自动测试-修复循环命令全部在受控 allowlist 中。",
    "repair-loop schema、失败分类、dry-run、stop states 和 QA evidence policy 已被契约测试覆盖。",
    "V13 boundary 的聊天授权识别命令全部在受控 allowlist 中。",
    "authorize schema 覆盖分类器版本、授权范围、确认强度、命中标记和 required explicit phrase。",
    "V14 boundary 的端到端 chat-smoke 命令全部在受控 allowlist 中。",
    "chat-smoke schema 覆盖完整阶段链、授权样例、最终 idle 和 non-actions。",
    "V15 boundary 的真实自然语言入口 smoke 命令全部在受控 allowlist 中。",
    "nl-smoke schema 覆盖正式开工预览、ready-to-write dry-run、acceptance checks、paths 和 non-actions。",
    "run / advance report 层覆盖 dry-run、skip 和空命令状态。",
    "聊天授权识别不会把“继续做 / 我确认”当成 git / 生产 / DB / destructive 授权。",
    "阶段写回必须显式 --write-back、验证通过且 evidence 存在。",
    "subagent timeout policy 覆盖 checkpoint、deadline、范围收缩重试和 timeout evidence。",
]


def ok(check_id: str, message: str, details: list[str] | None = None) -> ContractResult:
    return ContractResult(check_id, "ok", message, details or [])


def fail(check_id: str, message: str, details: list[str] | None = None) -> ContractResult:
    return ContractResult(check_id, "fail", message, details or [])


def missing_historical_boundary_result(check_id: str, label: str, boundary: str) -> ContractResult:
    return ok(
        check_id,
        f"{label} historical boundary fixture is absent; portable runtime skips source-only allowlist fixture check.",
        [boundary, "target-portable-runtime-skip"],
    )


def python_command(*args: str) -> list[str]:
    return [sys.executable, *args]


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def load_json_command(check_id: str, command: list[str]) -> tuple[dict[str, Any] | None, list[str]]:
    result = run(command)
    details = [f"command: {' '.join(command)}"]
    if result.returncode != 0:
        details.append(result.stderr.strip() or result.stdout.strip())
        return None, details
    try:
        return json.loads(result.stdout), details
    except json.JSONDecodeError:
        details.append(result.stdout.strip())
        return None, details


def require_keys(payload: dict[str, Any], keys: list[str]) -> list[str]:
    return [f"missing key: {key}" for key in keys if key not in payload]


def candidate(stage_key: str, *, active: bool = True, blocked: bool = False, evidence_missing: bool = False) -> gstack_loop.LoopCandidate:
    return gstack_loop.LoopCandidate(
        task=f"contract {stage_key}",
        boundary=V6_BOUNDARY,
        active=active,
        blocked=blocked,
        progress="0/7",
        current_stage_key=stage_key,
        current_stage=stage_key,
        next_step=stage_key,
        selection_reason="contract smoke",
        blocked_reasons=["blocked for contract"] if blocked else [],
        evidence_missing=["missing for contract"] if evidence_missing else [],
    )


def plan_for(item: gstack_loop.LoopCandidate | None) -> gstack_loop.LoopPlan:
    return gstack_loop.LoopPlan(
        generated_at="contract-smoke",
        schema_version=gstack_loop.SCHEMA_VERSION,
        planner_version=gstack_loop.PLANNER_VERSION,
        status="ready" if item is not None else "idle",
        mode="contract-smoke",
        candidate_count=1 if item is not None else 0,
        open_tasks=1 if item is not None else 0,
        total_tasks=1 if item is not None else 0,
        selected=item,
        can_auto_continue=item is not None and item.active and not item.blocked and not item.evidence_missing,
        codex_next_actions=[],
        chat_first_protocol=gstack_loop.chat_first_protocol_for(item),
        decision_policy=gstack_loop.decision_policy(),
        engineering_decision_evidence=gstack_loop.engineering_decision_evidence_for(item),
        eng_review_decisioner=gstack_loop.eng_review_decisioner_for(item),
        continuation_policy=gstack_loop.continuation_policy_for(item),
        current_stage_skill_route=gstack_loop.stage_skill_route_for(item),
        stage_skill_routes=list(gstack_loop.STAGE_SKILL_ROUTES),
        subagent_recommendation=gstack_loop.subagent_recommendation_for(item),
        subagent_timeout_policy=gstack_loop.subagent_timeout_policy(),
        subagent_orchestration=gstack_loop.subagent_orchestration_for(item),
        testing_policy=gstack_loop.testing_policy_for(item),
        test_repair_loop=gstack_loop.test_repair_loop_policy_for(item),
        stage_write_back_policy=gstack_loop.stage_write_back_policy(),
        stage_write_back_closure=gstack_loop.stage_write_back_closure_for(item),
        release_policy=gstack_loop.release_policy(),
        stop_conditions=gstack_loop.high_risk_stop_conditions(),
        needs_user_confirmation=gstack_loop.confirmations_for(item),
        non_actions=gstack_loop.non_actions(),
        source_note="contract smoke fixture",
    )


def run_args(*args: str) -> argparse.Namespace:
    return gstack_loop.build_parser().parse_args(["run", *args])


def advance_args(*args: str) -> argparse.Namespace:
    return gstack_loop.build_parser().parse_args(["advance", *args])


def write_back_args(*args: str) -> argparse.Namespace:
    return gstack_loop.build_parser().parse_args(["write-back", *args])


def repair_loop_args(*args: str) -> argparse.Namespace:
    return gstack_loop.build_parser().parse_args(["repair-loop", *args])


def check_plan_json_schema() -> ContractResult:
    payload, details = load_json_command(
        "plan-json-schema",
        python_command(".gstack/scripts/gstack_loop.py", "plan", "--format", "json", "--limit", "1"),
    )
    if payload is None:
        return fail("plan-json-schema", "plan did not return JSON.", details)
    failures = require_keys(
        payload,
        [
            "generated_at",
            "schema_version",
            "planner_version",
            "status",
            "selected",
            "chat_first_protocol",
            "current_stage_skill_route",
            "stage_skill_routes",
            "decision_policy",
            "engineering_decision_evidence",
            "eng_review_decisioner",
            "testing_policy",
            "subagent_timeout_policy",
            "subagent_orchestration",
            "test_repair_loop",
            "stage_write_back_policy",
            "stage_write_back_closure",
            "release_policy",
            "stop_conditions",
            "non_actions",
        ],
    )
    if payload.get("schema_version") != gstack_loop.SCHEMA_VERSION:
        failures.append("schema_version does not match gstack_loop.SCHEMA_VERSION")
    if payload.get("planner_version") != gstack_loop.PLANNER_VERSION:
        failures.append("planner_version does not match gstack_loop.PLANNER_VERSION")
    chat = payload.get("chat_first_protocol") or {}
    if not isinstance(chat, dict):
        failures.append("chat_first_protocol is not an object")
    else:
        for key in ["current_stage", "codex_will_do", "user_must_choose", "user_does_not_need_to_handle", "validation_result_policy", "write_back_policy"]:
            if key not in chat:
                failures.append(f"chat_first_protocol missing key: {key}")
    eng = payload.get("engineering_decision_evidence") or {}
    if not isinstance(eng, dict):
        failures.append("engineering_decision_evidence is not an object")
    else:
        for key in ["codex_owned_decisions", "user_owned_decisions", "anti_user_delegation_checks", "evidence_targets"]:
            if key not in eng:
                failures.append(f"engineering_decision_evidence missing key: {key}")
    decisioner = payload.get("eng_review_decisioner") or {}
    if not isinstance(decisioner, dict):
        failures.append("eng_review_decisioner is not an object")
    else:
        for key in [
            "status",
            "decisioner_version",
            "codex_owned_decisions",
            "user_owned_decisions",
            "forbidden_user_delegations",
            "required_evidence_markers",
            "generation_policy",
            "check_policy",
            "evidence_check",
        ]:
            if key not in decisioner:
                failures.append(f"eng_review_decisioner missing key: {key}")
        check = decisioner.get("evidence_check") or {}
        if not isinstance(check, dict):
            failures.append("eng_review_decisioner.evidence_check is not an object")
        else:
            for key in [
                "evidence_path",
                "exists",
                "status",
                "required_markers",
                "missing_required_markers",
                "forbidden_user_delegations",
                "forbidden_user_delegations_found",
                "summary",
            ]:
                if key not in check:
                    failures.append(f"eng_review_decisioner.evidence_check missing key: {key}")
    repair = payload.get("test_repair_loop") or {}
    if not isinstance(repair, dict):
        failures.append("test_repair_loop is not an object")
    elif "loop_steps" not in repair or "stop_and_ask_when" not in repair:
        failures.append("test_repair_loop missing loop steps or stop conditions")
    timeout_policy = payload.get("subagent_timeout_policy") or {}
    if not isinstance(timeout_policy, dict):
        failures.append("subagent_timeout_policy is not an object")
    else:
        for key in [
            "default_checkpoint_seconds",
            "default_deadline_seconds",
            "max_files_per_readonly_agent",
            "max_retry_attempts",
            "required_checkpoint_fields",
            "result_schema_required_fields",
            "timeout_classifications",
            "timeout_recovery_steps",
            "retry_scope_rules",
            "evidence_rules",
        ]:
            if key not in timeout_policy:
                failures.append(f"subagent_timeout_policy missing key: {key}")
    orchestration = payload.get("subagent_orchestration") or {}
    if not isinstance(orchestration, dict):
        failures.append("subagent_orchestration is not an object")
    else:
        for key in [
            "status",
            "orchestrator_version",
            "current_stage_key",
            "current_stage_label",
            "mode",
            "recommended_now",
            "decision_reason",
            "planned_subagents",
            "launch_order",
            "result_collection",
            "boundary_update_policy",
            "skip_conditions",
            "timeout_contract",
            "allowed_when",
            "refused_when",
            "non_actions",
        ]:
            if key not in orchestration:
                failures.append(f"subagent_orchestration missing key: {key}")
        if orchestration.get("orchestrator_version") != gstack_loop.SUBAGENT_ORCHESTRATION_VERSION:
            failures.append("subagent_orchestration orchestrator_version changed")
    write_back = payload.get("stage_write_back_policy") or {}
    if not isinstance(write_back, dict):
        failures.append("stage_write_back_policy is not an object")
    elif write_back.get("default_enabled") is not False:
        failures.append("stage_write_back_policy must default to disabled")
    closure = payload.get("stage_write_back_closure") or {}
    if not isinstance(closure, dict):
        failures.append("stage_write_back_closure is not an object")
    else:
        for key in [
            "status",
            "writer_version",
            "current_stage_key",
            "current_stage_label",
            "suggested_evidence",
            "suggested_command",
            "stage_evidence_rules",
            "allowed_when",
            "refused_when",
            "non_actions",
        ]:
            if key not in closure:
                failures.append(f"stage_write_back_closure missing key: {key}")
        if closure.get("writer_version") != gstack_loop.STAGE_WRITE_BACK_CLOSURE_VERSION:
            failures.append("stage_write_back_closure writer_version changed")
    if failures:
        return fail("plan-json-schema", "plan JSON schema changed unexpectedly.", [*details, *failures])
    return ok("plan-json-schema", "plan JSON has the stable contract fields.", details)


def check_advance_json_schema() -> ContractResult:
    payload, details = load_json_command(
        "advance-json-schema",
        python_command(".gstack/scripts/gstack_loop.py", "advance", "--dry-run", "--format", "json", "--limit", "1"),
    )
    if payload is None:
        return fail("advance-json-schema", "advance did not return JSON.", details)
    failures = require_keys(
        payload,
        [
            "generated_at",
            "schema_version",
            "executor_version",
            "mode",
            "dry_run",
            "execute_requested",
            "status",
            "selected",
            "candidate_status",
            "stage_decision",
            "command_source",
            "command_count",
            "passed_count",
            "failed_count",
            "skipped_count",
            "commands",
            "write_back_result",
            "stop_conditions",
            "non_actions",
        ],
    )
    decision = payload.get("stage_decision") or {}
    if not isinstance(decision, dict):
        failures.append("stage_decision is not an object")
    else:
        failures.extend(
            f"stage_decision missing key: {key}"
            for key in [
                "stage_key",
                "action",
                "can_execute",
                "execution_strategy",
                "next_stage_on_success",
                "requires_main_agent",
                "requires_user_confirmation",
                "stop_reason",
                "write_back_required",
                "evidence_targets",
                "instructions",
            ]
            if key not in decision
        )
    if payload.get("schema_version") != gstack_loop.SCHEMA_VERSION:
        failures.append("schema_version does not match gstack_loop.SCHEMA_VERSION")
    if payload.get("executor_version") != gstack_loop.ADVANCE_EXECUTOR_VERSION:
        failures.append("executor_version does not match advance executor version")
    if payload.get("dry_run") is not True:
        failures.append("advance must default to dry-run for this check")
    if payload.get("execute_requested") is not False:
        failures.append("advance dry-run must not mark execute_requested")
    write_back = payload.get("write_back_result") or {}
    if not isinstance(write_back, dict):
        failures.append("advance write_back_result is not an object")
    elif write_back.get("performed") is not False:
        failures.append("advance dry-run must not perform write-back")
    if failures:
        return fail("advance-json-schema", "advance JSON schema changed unexpectedly.", [*details, *failures])
    return ok("advance-json-schema", "advance JSON has the stable contract fields.", details)


def check_run_json_schema() -> ContractResult:
    payload, details = load_json_command(
        "run-json-schema",
        python_command(".gstack/scripts/gstack_loop.py", "run", "--dry-run", "--format", "json", "--limit", "1"),
    )
    if payload is None:
        return fail("run-json-schema", "run did not return JSON.", details)
    failures = require_keys(
        payload,
        [
            "generated_at",
            "schema_version",
            "executor_version",
            "mode",
            "executor_level",
            "dry_run",
            "execute_requested",
            "status",
            "selected",
            "candidate_status",
            "command_source",
            "command_count",
            "passed_count",
            "failed_count",
            "skipped_count",
            "commands",
            "write_back_result",
            "stop_conditions",
            "non_actions",
        ],
    )
    if payload.get("schema_version") != gstack_loop.SCHEMA_VERSION:
        failures.append("schema_version does not match gstack_loop.SCHEMA_VERSION")
    if payload.get("executor_version") != gstack_loop.RUNNER_VERSION:
        failures.append("executor_version does not match runner version")
    if payload.get("dry_run") is not True:
        failures.append("run must default to dry-run for this check")
    write_back = payload.get("write_back_result") or {}
    if not isinstance(write_back, dict):
        failures.append("run write_back_result is not an object")
    elif write_back.get("performed") is not False:
        failures.append("run dry-run must not perform write-back")
    if failures:
        return fail("run-json-schema", "run JSON schema changed unexpectedly.", [*details, *failures])
    return ok("run-json-schema", "run JSON has the stable contract fields.", details)


def check_repair_loop_json_schema() -> ContractResult:
    payload, details = load_json_command(
        "repair-loop-json-schema",
        python_command(
            ".gstack/scripts/gstack_loop.py",
            "repair-loop",
            "--dry-run",
            "--format",
            "json",
            "--query",
            "test-repair-loop-runtime",
            "--limit",
            "1",
        ),
    )
    if payload is None:
        return fail("repair-loop-json-schema", "repair-loop did not return JSON.", details)
    failures = require_keys(
        payload,
        [
            "generated_at",
            "schema_version",
            "loop_version",
            "mode",
            "dry_run",
            "execute_requested",
            "max_local_repair_attempts",
            "status",
            "selected",
            "candidate_status",
            "command_source",
            "command_count",
            "passed_count",
            "failed_count",
            "skipped_count",
            "commands",
            "failure_analysis",
            "repair_plan",
            "rerun_policy",
            "qa_evidence_policy",
            "stop_conditions",
            "non_actions",
            "source_note",
        ],
    )
    if payload.get("schema_version") != gstack_loop.SCHEMA_VERSION:
        failures.append("schema_version does not match gstack_loop.SCHEMA_VERSION")
    if payload.get("loop_version") != gstack_loop.TEST_REPAIR_LOOP_RUNTIME_VERSION:
        failures.append("loop_version does not match TEST_REPAIR_LOOP_RUNTIME_VERSION")
    if payload.get("dry_run") is not True:
        failures.append("repair-loop must default to dry-run for this check")
    if payload.get("execute_requested") is not False:
        failures.append("repair-loop dry-run must not mark execute_requested")
    analysis = payload.get("failure_analysis") or {}
    if not isinstance(analysis, dict):
        failures.append("failure_analysis is not an object")
    else:
        for key in [
            "status",
            "failed_command",
            "returncode",
            "failure_kind",
            "repairability",
            "summary",
            "stdout_tail",
            "stderr_tail",
            "suggested_next_action",
            "requires_user_confirmation",
            "evidence_policy",
        ]:
            if key not in analysis:
                failures.append(f"failure_analysis missing key: {key}")
    if not isinstance(payload.get("repair_plan"), list) or not payload.get("repair_plan"):
        failures.append("repair_plan must be a non-empty list")
    if not isinstance(payload.get("rerun_policy"), list) or not payload.get("rerun_policy"):
        failures.append("rerun_policy must be a non-empty list")
    if not isinstance(payload.get("qa_evidence_policy"), list) or not payload.get("qa_evidence_policy"):
        failures.append("qa_evidence_policy must be a non-empty list")
    if failures:
        return fail("repair-loop-json-schema", "repair-loop JSON schema changed unexpectedly.", [*details, *failures])
    return ok("repair-loop-json-schema", "repair-loop JSON has the stable test-repair contract fields.", details)


def check_stage_matrix() -> ContractResult:
    expected = {
        "requirement-brief": ("requirement-design-main-agent", False, "main-agent-dialogue", "plan-ceo-review", True),
        "plan-ceo-review": ("requirement-design-main-agent", False, "main-agent-dialogue", "requirement-freeze", True),
        "requirement-freeze": ("requirement-design-main-agent", False, "main-agent-dialogue", "plan-eng-review", True),
        "plan-eng-review": ("engineering-review-main-agent", False, "main-agent-review", "domain-spec-readiness", True),
        "domain-spec-readiness": ("run-spec-readiness-guard", True, "allowlist-guard", "implement", True),
        "implement": ("implementation-main-agent", False, "main-agent-code-edit", "qa", True),
        "qa": ("run-boundary-verification", True, "allowlist-boundary-verification", "complete", True),
        "complete": ("complete", False, "none", "complete", False),
    }
    failures: list[str] = []
    for stage, (action, can_execute, strategy, next_stage, write_back) in expected.items():
        item = candidate(stage)
        decision = gstack_loop.stage_execution_decision_for(item, gstack_loop.stage_skill_route_for(item))
        if decision is None:
            failures.append(f"{stage}: decision is None")
            continue
        actual = (
            decision.action,
            decision.can_execute,
            decision.execution_strategy,
            decision.next_stage_on_success,
            decision.write_back_required,
        )
        expected_tuple = (action, can_execute, strategy, next_stage, write_back)
        if actual != expected_tuple:
            failures.append(f"{stage}: expected {expected_tuple}, got {actual}")
    if failures:
        return fail("stage-matrix", "Stage execution matrix regressed.", failures)
    return ok("stage-matrix", "All stages keep their expected execution strategy.")


def check_stop_states() -> ContractResult:
    cases = [
        ("not-active", candidate("qa", active=False), "activate-local-boundary", False, "not-active"),
        ("blocked", candidate("qa", blocked=True), "blocked-stop", False, "blocked"),
        ("evidence-missing", candidate("qa", evidence_missing=True), "repair-evidence", False, "evidence-missing"),
        ("unknown-stage", candidate("surprise-stage"), "unknown-stage-stop", False, "unknown-stage"),
    ]
    failures: list[str] = []
    for name, item, action, can_execute, stop_reason in cases:
        decision = gstack_loop.stage_execution_decision_for(item, gstack_loop.stage_skill_route_for(item))
        if decision is None:
            failures.append(f"{name}: decision is None")
            continue
        actual = (decision.action, decision.can_execute, decision.stop_reason)
        expected = (action, can_execute, stop_reason)
        if actual != expected:
            failures.append(f"{name}: expected {expected}, got {actual}")
        source, commands = gstack_loop.advance_commands(decision, item)
        if commands:
            failures.append(f"{name}: expected no commands, got {source}: {commands}")
    if failures:
        return fail("stop-states", "Stop states must not execute commands.", failures)
    return ok("stop-states", "Inactive, blocked, evidence-missing and unknown stages do not execute.")


def check_execution_safety() -> ContractResult:
    item = candidate("qa")
    commands = [
        "python3 .gstack/scripts/gstack_loop.py run --execute --format json",
        "python3 .gstack/scripts/gstack_loop.py advance --execute --format json",
        "python3 .gstack/scripts/gstack_loop.py repair-loop --execute --format json",
        "python3 .gstack/scripts/gstack_loop.py --format markdown",
        "python3 .gstack/scripts/spec_sync_guard.py",
        "echo unsafe",
    ]
    reasons = {command: gstack_loop.skip_reason_for(command, item) for command in commands}
    failures: list[str] = []
    if "自我递归" not in reasons[commands[0]]:
        failures.append("run --execute recursion was not blocked")
    if "自我递归" not in reasons[commands[1]]:
        failures.append("advance --execute recursion was not blocked")
    if "自我递归" not in reasons[commands[2]]:
        failures.append("repair-loop --execute recursion was not blocked")
    if reasons[commands[3]]:
        failures.append("diagnostic gstack_loop markdown command should remain allowed")
    if reasons[commands[4]]:
        failures.append("spec_sync_guard allowlist command should remain allowed")
    if "allowlist" not in reasons[commands[5]]:
        failures.append("non-allowlist shell-like command was not blocked")
    no_command_status = gstack_loop.advance_status(
        gstack_loop.stage_execution_decision_for(item, gstack_loop.stage_skill_route_for(item)),
        [],
        dry_run=False,
        command_count=0,
    )
    if no_command_status != "no-commands":
        failures.append(f"empty executable stage returned {no_command_status}, expected no-commands")
    if failures:
        return fail("execution-safety", "Loop execution safety regressed.", failures)
    return ok("execution-safety", "Recursion, allowlist and empty-command safety checks passed.")


def check_v6_boundary_allowlist() -> ContractResult:
    item = candidate("qa")
    boundary = REPO_ROOT / V6_BOUNDARY
    failures: list[str] = []
    if not boundary.is_file():
        return missing_historical_boundary_result("v6-boundary-allowlist", "V6", V6_BOUNDARY)
    source, commands = gstack_loop.verification_commands(item)
    if source != V6_BOUNDARY:
        failures.append(f"expected source {V6_BOUNDARY}, got {source}")
    if commands != V6_VERIFICATION_COMMANDS:
        failures.append(f"Verification commands changed: expected {V6_VERIFICATION_COMMANDS}, got {commands}")
    for command in commands:
        reason = gstack_loop.skip_reason_for(command, item)
        if reason:
            failures.append(f"{command}: {reason}")
    if failures:
        return fail("v6-boundary-allowlist", "V6 boundary Verification is not fully runnable by the controlled runner.", failures)
    return ok("v6-boundary-allowlist", "V6 boundary Verification commands all match the controlled allowlist.")


def check_v7_boundary_allowlist() -> ContractResult:
    item = gstack_loop.LoopCandidate(
        task="contract loop-engineering-v7",
        boundary=V7_BOUNDARY,
        active=True,
        blocked=False,
        progress="5/7",
        current_stage_key="qa",
        current_stage="qa",
        next_step="qa",
        selection_reason="contract smoke",
        blocked_reasons=[],
        evidence_missing=[],
    )
    boundary = REPO_ROOT / V7_BOUNDARY
    failures: list[str] = []
    if not boundary.is_file():
        return missing_historical_boundary_result("v7-boundary-allowlist", "V7", V7_BOUNDARY)
    source, commands = gstack_loop.verification_commands(item)
    if source != V7_BOUNDARY:
        failures.append(f"expected source {V7_BOUNDARY}, got {source}")
    if commands != V7_VERIFICATION_COMMANDS:
        failures.append(f"Verification commands changed: expected {V7_VERIFICATION_COMMANDS}, got {commands}")
    for command in commands:
        reason = gstack_loop.skip_reason_for(command, item)
        if reason:
            failures.append(f"{command}: {reason}")
    if failures:
        return fail("v7-boundary-allowlist", "V7 boundary Verification is not fully covered by the controlled allowlist.", failures)
    return ok("v7-boundary-allowlist", "V7 boundary Verification commands all match the controlled allowlist.")


def check_v8_boundary_allowlist() -> ContractResult:
    item = gstack_loop.LoopCandidate(
        task="contract subagent-timeout-resilience",
        boundary=V8_BOUNDARY,
        active=True,
        blocked=False,
        progress="5/7",
        current_stage_key="qa",
        current_stage="qa",
        next_step="qa",
        selection_reason="contract smoke",
        blocked_reasons=[],
        evidence_missing=[],
    )
    boundary = REPO_ROOT / V8_BOUNDARY
    failures: list[str] = []
    if not boundary.is_file():
        return missing_historical_boundary_result("v8-boundary-allowlist", "V8", V8_BOUNDARY)
    source, commands = gstack_loop.verification_commands(item)
    if source != V8_BOUNDARY:
        failures.append(f"expected source {V8_BOUNDARY}, got {source}")
    if commands != V8_VERIFICATION_COMMANDS:
        failures.append(f"Verification commands changed: expected {V8_VERIFICATION_COMMANDS}, got {commands}")
    for command in commands:
        reason = gstack_loop.skip_reason_for(command, item)
        if reason:
            failures.append(f"{command}: {reason}")
    if failures:
        return fail("v8-boundary-allowlist", "V8 boundary Verification is not fully covered by the controlled allowlist.", failures)
    return ok("v8-boundary-allowlist", "V8 boundary Verification commands all match the controlled allowlist.")


def check_v9_boundary_allowlist() -> ContractResult:
    item = gstack_loop.LoopCandidate(
        task="contract eng-review-auto-decisioner",
        boundary=V9_BOUNDARY,
        active=True,
        blocked=False,
        progress="5/7",
        current_stage_key="qa",
        current_stage="qa",
        next_step="qa",
        selection_reason="contract smoke",
        blocked_reasons=[],
        evidence_missing=[],
    )
    boundary = REPO_ROOT / V9_BOUNDARY
    failures: list[str] = []
    if not boundary.is_file():
        return missing_historical_boundary_result("v9-boundary-allowlist", "V9", V9_BOUNDARY)
    source, commands = gstack_loop.verification_commands(item)
    if source != V9_BOUNDARY:
        failures.append(f"expected source {V9_BOUNDARY}, got {source}")
    if commands != V9_VERIFICATION_COMMANDS:
        failures.append(f"Verification commands changed: expected {V9_VERIFICATION_COMMANDS}, got {commands}")
    for command in commands:
        reason = gstack_loop.skip_reason_for(command, item)
        if reason:
            failures.append(f"{command}: {reason}")
    if failures:
        return fail("v9-boundary-allowlist", "V9 boundary Verification is not fully covered by the controlled allowlist.", failures)
    return ok("v9-boundary-allowlist", "V9 boundary Verification commands all match the controlled allowlist.")


def check_v10_boundary_allowlist() -> ContractResult:
    item = gstack_loop.LoopCandidate(
        task="contract stage-write-back-closure",
        boundary=V10_BOUNDARY,
        active=True,
        blocked=False,
        progress="5/7",
        current_stage_key="qa",
        current_stage="qa",
        next_step="qa",
        selection_reason="contract smoke",
        blocked_reasons=[],
        evidence_missing=[],
    )
    boundary = REPO_ROOT / V10_BOUNDARY
    failures: list[str] = []
    if not boundary.is_file():
        return missing_historical_boundary_result("v10-boundary-allowlist", "V10", V10_BOUNDARY)
    source, commands = gstack_loop.verification_commands(item)
    if source != V10_BOUNDARY:
        failures.append(f"expected source {V10_BOUNDARY}, got {source}")
    if commands != V10_VERIFICATION_COMMANDS:
        failures.append(f"Verification commands changed: expected {V10_VERIFICATION_COMMANDS}, got {commands}")
    for command in commands:
        reason = gstack_loop.skip_reason_for(command, item)
        if reason:
            failures.append(f"{command}: {reason}")
    if failures:
        return fail("v10-boundary-allowlist", "V10 boundary Verification is not fully covered by the controlled allowlist.", failures)
    return ok("v10-boundary-allowlist", "V10 boundary Verification commands all match the controlled allowlist.")


def check_v11_boundary_allowlist() -> ContractResult:
    item = gstack_loop.LoopCandidate(
        task="contract subagent-auto-orchestration",
        boundary=V11_BOUNDARY,
        active=True,
        blocked=False,
        progress="6/7",
        current_stage_key="qa",
        current_stage="qa",
        next_step="qa",
        selection_reason="contract smoke",
        blocked_reasons=[],
        evidence_missing=[],
    )
    boundary = REPO_ROOT / V11_BOUNDARY
    failures: list[str] = []
    if not boundary.is_file():
        return missing_historical_boundary_result("v11-boundary-allowlist", "V11", V11_BOUNDARY)
    source, commands = gstack_loop.verification_commands(item)
    if source != V11_BOUNDARY:
        failures.append(f"expected source {V11_BOUNDARY}, got {source}")
    if commands != V11_VERIFICATION_COMMANDS:
        failures.append(f"Verification commands changed: expected {V11_VERIFICATION_COMMANDS}, got {commands}")
    for command in commands:
        reason = gstack_loop.skip_reason_for(command, item)
        if reason:
            failures.append(f"{command}: {reason}")
    if failures:
        return fail("v11-boundary-allowlist", "V11 boundary Verification is not fully covered by the controlled allowlist.", failures)
    return ok("v11-boundary-allowlist", "V11 boundary Verification commands all match the controlled allowlist.")


def check_v12_boundary_allowlist() -> ContractResult:
    item = gstack_loop.LoopCandidate(
        task="contract test-repair-loop-runtime",
        boundary=V12_BOUNDARY,
        active=True,
        blocked=False,
        progress="6/7",
        current_stage_key="qa",
        current_stage="qa",
        next_step="qa",
        selection_reason="contract smoke",
        blocked_reasons=[],
        evidence_missing=[],
    )
    boundary = REPO_ROOT / V12_BOUNDARY
    failures: list[str] = []
    if not boundary.is_file():
        return missing_historical_boundary_result("v12-boundary-allowlist", "V12", V12_BOUNDARY)
    source, commands = gstack_loop.verification_commands(item)
    if source != V12_BOUNDARY:
        failures.append(f"expected source {V12_BOUNDARY}, got {source}")
    if commands != V12_VERIFICATION_COMMANDS:
        failures.append(f"Verification commands changed: expected {V12_VERIFICATION_COMMANDS}, got {commands}")
    for command in commands:
        reason = gstack_loop.skip_reason_for(command, item)
        if reason:
            failures.append(f"{command}: {reason}")
    if failures:
        return fail("v12-boundary-allowlist", "V12 boundary Verification is not fully covered by the controlled allowlist.", failures)
    return ok("v12-boundary-allowlist", "V12 boundary Verification commands all match the controlled allowlist.")


def check_v13_boundary_allowlist() -> ContractResult:
    item = gstack_loop.LoopCandidate(
        task="contract chat-authorization-runtime",
        boundary=V13_BOUNDARY,
        active=True,
        blocked=False,
        progress="6/7",
        current_stage_key="qa",
        current_stage="qa",
        next_step="qa",
        selection_reason="contract smoke",
        blocked_reasons=[],
        evidence_missing=[],
    )
    boundary = REPO_ROOT / V13_BOUNDARY
    failures: list[str] = []
    if not boundary.is_file():
        return missing_historical_boundary_result("v13-boundary-allowlist", "V13", V13_BOUNDARY)
    source, commands = gstack_loop.verification_commands(item)
    if source != V13_BOUNDARY:
        failures.append(f"expected source {V13_BOUNDARY}, got {source}")
    if commands != V13_VERIFICATION_COMMANDS:
        failures.append(f"Verification commands changed: expected {V13_VERIFICATION_COMMANDS}, got {commands}")
    for command in commands:
        reason = gstack_loop.skip_reason_for(command, item)
        if reason:
            failures.append(f"{command}: {reason}")
    if failures:
        return fail("v13-boundary-allowlist", "V13 boundary Verification is not fully covered by the controlled allowlist.", failures)
    return ok("v13-boundary-allowlist", "V13 boundary Verification commands all match the controlled allowlist.")


def check_v14_boundary_allowlist() -> ContractResult:
    item = gstack_loop.LoopCandidate(
        task="contract chat-first-loop-smoke",
        boundary=V14_BOUNDARY,
        active=True,
        blocked=False,
        progress="6/7",
        current_stage_key="qa",
        current_stage="qa",
        next_step="qa",
        selection_reason="contract smoke",
        blocked_reasons=[],
        evidence_missing=[],
    )
    boundary = REPO_ROOT / V14_BOUNDARY
    failures: list[str] = []
    if not boundary.is_file():
        return missing_historical_boundary_result("v14-boundary-allowlist", "V14", V14_BOUNDARY)
    source, commands = gstack_loop.verification_commands(item)
    if source != V14_BOUNDARY:
        failures.append(f"expected source {V14_BOUNDARY}, got {source}")
    if commands != V14_VERIFICATION_COMMANDS:
        failures.append(f"Verification commands changed: expected {V14_VERIFICATION_COMMANDS}, got {commands}")
    for command in commands:
        reason = gstack_loop.skip_reason_for(command, item)
        if reason:
            failures.append(f"{command}: {reason}")
    if failures:
        return fail("v14-boundary-allowlist", "V14 boundary Verification is not fully covered by the controlled allowlist.", failures)
    return ok("v14-boundary-allowlist", "V14 boundary Verification commands all match the controlled allowlist.")


def check_v15_boundary_allowlist() -> ContractResult:
    item = gstack_loop.LoopCandidate(
        task="contract natural-language-loop-runtime",
        boundary=V15_BOUNDARY,
        active=True,
        blocked=False,
        progress="6/7",
        current_stage_key="qa",
        current_stage="qa",
        next_step="qa",
        selection_reason="contract smoke",
        blocked_reasons=[],
        evidence_missing=[],
    )
    boundary = REPO_ROOT / V15_BOUNDARY
    failures: list[str] = []
    if not boundary.is_file():
        return missing_historical_boundary_result("v15-boundary-allowlist", "V15", V15_BOUNDARY)
    source, commands = gstack_loop.verification_commands(item)
    if source != V15_BOUNDARY:
        failures.append(f"expected source {V15_BOUNDARY}, got {source}")
    if commands != V15_VERIFICATION_COMMANDS:
        failures.append(f"Verification commands changed: expected {V15_VERIFICATION_COMMANDS}, got {commands}")
    for command in commands:
        reason = gstack_loop.skip_reason_for(command, item)
        if reason:
            failures.append(f"{command}: {reason}")
    if failures:
        return fail("v15-boundary-allowlist", "V15 boundary Verification is not fully covered by the controlled allowlist.", failures)
    return ok("v15-boundary-allowlist", "V15 boundary Verification commands all match the controlled allowlist.")


def check_subagents_json_schema() -> ContractResult:
    payload, details = load_json_command(
        "subagents-json-schema",
        python_command(".gstack/scripts/gstack_loop.py", "subagents", "--format", "json", "--limit", "1"),
    )
    if payload is None:
        return fail("subagents-json-schema", "subagents did not return JSON.", details)
    failures = require_keys(
        payload,
        [
            "generated_at",
            "schema_version",
            "orchestrator_version",
            "mode",
            "status",
            "selected",
            "candidate_status",
            "subagent_orchestration",
            "stop_conditions",
            "non_actions",
            "source_note",
        ],
    )
    if payload.get("schema_version") != gstack_loop.SCHEMA_VERSION:
        failures.append("schema_version does not match gstack_loop.SCHEMA_VERSION")
    if payload.get("orchestrator_version") != gstack_loop.SUBAGENT_ORCHESTRATION_VERSION:
        failures.append("orchestrator_version does not match gstack_loop.SUBAGENT_ORCHESTRATION_VERSION")
    orchestration = payload.get("subagent_orchestration") or {}
    if not isinstance(orchestration, dict):
        failures.append("subagent_orchestration is not an object")
    else:
        for key in [
            "status",
            "orchestrator_version",
            "current_stage_key",
            "current_stage_label",
            "mode",
            "recommended_now",
            "decision_reason",
            "planned_subagents",
            "launch_order",
            "result_collection",
            "boundary_update_policy",
            "skip_conditions",
            "timeout_contract",
            "allowed_when",
            "refused_when",
            "non_actions",
        ]:
            if key not in orchestration:
                failures.append(f"subagent_orchestration missing key: {key}")
        timeout = orchestration.get("timeout_contract") or {}
        if not isinstance(timeout, dict):
            failures.append("subagent_orchestration.timeout_contract is not an object")
        else:
            for key in [
                "checkpoint_seconds",
                "deadline_seconds",
                "max_files_per_readonly_agent",
                "max_retry_attempts",
                "required_checkpoint_fields",
                "result_schema_required_fields",
            ]:
                if key not in timeout:
                    failures.append(f"timeout_contract missing key: {key}")
        planned = orchestration.get("planned_subagents") or []
        if planned and isinstance(planned, list):
            first = planned[0]
            if not isinstance(first, dict):
                failures.append("planned_subagents item is not an object")
            else:
                for key in [
                    "name",
                    "role",
                    "trigger_stage",
                    "task",
                    "write_scope",
                    "forbidden_paths",
                    "required_inputs",
                    "output_evidence",
                    "checkpoint_seconds",
                    "deadline_seconds",
                    "max_files",
                    "result_schema",
                    "timeout_recovery",
                    "auto_start",
                    "status",
                    "result_integration_target",
                ]:
                    if key not in first:
                        failures.append(f"planned_subagents item missing key: {key}")
    if failures:
        return fail("subagents-json-schema", "subagents JSON schema changed unexpectedly.", [*details, *failures])
    return ok("subagents-json-schema", "subagents JSON has the stable orchestration fields.", details)


def check_subagent_orchestration_policy() -> ContractResult:
    policy = gstack_loop.subagent_orchestration_for(candidate("domain-spec-readiness"))
    qa_policy = gstack_loop.subagent_orchestration_for(candidate("qa"))
    failures: list[str] = []
    if policy.status != "ready":
        failures.append(f"domain-spec-readiness status changed: {policy.status}")
    if policy.mode != "mixed-read-only":
        failures.append(f"domain-spec-readiness mode changed: {policy.mode}")
    if policy.recommended_now is not True:
        failures.append("domain-spec-readiness should recommend starting read-only subagents")
    names = {item.get("name") for item in policy.planned_subagents}
    for expected in ["spec-contract-explorer", "engineering-plan-reviewer"]:
        if expected not in names:
            failures.append(f"domain-spec-readiness planned_subagents missing {expected}")
    for subagent in policy.planned_subagents:
        for key in [
            "name",
            "role",
            "trigger_stage",
            "task",
            "write_scope",
            "forbidden_paths",
            "checkpoint_seconds",
            "deadline_seconds",
            "max_files",
            "result_schema",
            "timeout_recovery",
            "required_inputs",
            "output_evidence",
            "auto_start",
            "status",
            "result_integration_target",
        ]:
            if key not in subagent:
                failures.append(f"{subagent.get('name', 'subagent')} missing {key}")
        if int(subagent.get("max_files", "99")) > gstack_loop.subagent_timeout_policy().max_files_per_readonly_agent:
            failures.append(f"{subagent.get('name', 'subagent')} exceeds read-only max files")
        if "do not pretend pass" not in subagent.get("timeout_recovery", ""):
            failures.append(f"{subagent.get('name', 'subagent')} timeout recovery must forbid pretending pass")
    if not any(".gstack" in item for item in policy.result_collection):
        failures.append("result_collection must route findings back to repo-native evidence")
    if int(policy.timeout_contract.get("max_files_per_readonly_agent", "99")) > 3:
        failures.append("timeout_contract read-only file budget is too broad")
    if not any("active boundary" in item for item in policy.launch_order):
        failures.append("launch_order must keep main agent boundary responsibility")
    if not any(item.get("name") == "qa-evidence-reviewer" for item in qa_policy.planned_subagents):
        failures.append("qa stage must plan qa-evidence-reviewer")
    if failures:
        return fail("subagent-orchestration-policy", "Subagent orchestration policy regressed.", failures)
    return ok("subagent-orchestration-policy", "Subagent orchestration plans explorer / reviewer / QA roles with timeout and evidence recovery.")


def check_subagent_orchestration_stop_states() -> ContractResult:
    cases = [
        ("not-active", candidate("qa", active=False), "needs-activation"),
        ("blocked", candidate("qa", blocked=True), "blocked"),
        ("evidence-missing", candidate("qa", evidence_missing=True), "evidence-repair"),
        ("idle", None, "idle"),
    ]
    failures: list[str] = []
    for name, item, expected_status in cases:
        policy = gstack_loop.subagent_orchestration_for(item)
        if policy.status != expected_status:
            failures.append(f"{name}: expected status {expected_status}, got {policy.status}")
        if policy.recommended_now:
            failures.append(f"{name}: should not recommend starting subagents")
        if item is None and policy.planned_subagents:
            failures.append("idle: expected no planned subagents")
        for subagent in policy.planned_subagents:
            if subagent.get("status") != "blocked":
                failures.append(f"{name}: {subagent.get('name', 'subagent')} should be blocked until task is ready")
        if not any("没有 selected task" in reason or "blocked" in reason or "evidence missing" in reason for reason in policy.refused_when):
            failures.append(f"{name}: refused_when must mention selected task / blocked / evidence guards")
    if failures:
        return fail("subagent-orchestration-stop-states", "Subagent orchestration stop states regressed.", failures)
    return ok("subagent-orchestration-stop-states", "Subagent orchestration refuses idle, inactive, blocked and evidence-missing tasks.")


def check_repair_loop_failure_analysis() -> ContractResult:
    item = candidate("qa")
    original_build_plan = gstack_loop.build_plan
    failures: list[str] = []
    try:
        gstack_loop.build_plan = lambda args: plan_for(item)  # type: ignore[assignment]

        local_report = gstack_loop.build_test_repair_loop_report(
            repair_loop_args(
                "--dry-run",
                "--failure-command",
                "python3 .gstack/scripts/spec_sync_guard.py",
                "--failure-returncode",
                "1",
                "--failure-stderr",
                "AssertionError: local contract failed",
            )
        )
        if local_report.status != "needs-repair":
            failures.append(f"local failure status changed: {local_report.status}")
        if local_report.failure_analysis.failure_kind != "local-verification-failure":
            failures.append(f"local failure kind changed: {local_report.failure_analysis.failure_kind}")
        if local_report.failure_analysis.repairability != "local-repairable":
            failures.append(f"local repairability changed: {local_report.failure_analysis.repairability}")
        if not any("重跑 failed command" in step for step in local_report.repair_plan):
            failures.append("local repair plan must require rerunning the failed command")
        if not any("QA evidence" in step for step in local_report.qa_evidence_policy):
            failures.append("QA evidence policy must be present for local failures")

        external_report = gstack_loop.build_test_repair_loop_report(
            repair_loop_args(
                "--dry-run",
                "--failure-command",
                "python3 .gstack/scripts/spec_sync_guard.py",
                "--failure-returncode",
                "1",
                "--failure-stderr",
                "401 unauthorized credential required",
            )
        )
        if external_report.status != "blocked":
            failures.append(f"external failure status changed: {external_report.status}")
        if external_report.failure_analysis.failure_kind != "external-or-permission":
            failures.append(f"external failure kind changed: {external_report.failure_analysis.failure_kind}")
        if external_report.failure_analysis.repairability != "requires-user-or-external":
            failures.append(f"external repairability changed: {external_report.failure_analysis.repairability}")
        if not external_report.failure_analysis.requires_user_confirmation:
            failures.append("external failure must require user / external confirmation")

        refused_report = gstack_loop.build_test_repair_loop_report(
            repair_loop_args("--dry-run", "--failure-command", "echo unsafe", "--failure-stderr", "unsafe")
        )
        if refused_report.status != "blocked":
            failures.append(f"refused command status changed: {refused_report.status}")
        if refused_report.failure_analysis.failure_kind != "runtime-refused":
            failures.append(f"refused command kind changed: {refused_report.failure_analysis.failure_kind}")
    finally:
        gstack_loop.build_plan = original_build_plan  # type: ignore[assignment]
    if failures:
        return fail("repair-loop-failure-analysis", "repair-loop failure classification regressed.", failures)
    return ok("repair-loop-failure-analysis", "repair-loop classifies local, external and runtime-refused failures.")


def check_repair_loop_stop_states() -> ContractResult:
    cases = [
        ("not-active", candidate("qa", active=False), "blocked", "not-active"),
        ("blocked", candidate("qa", blocked=True), "blocked", "task-blocked"),
        ("evidence-missing", candidate("qa", evidence_missing=True), "blocked", "evidence-missing"),
        ("idle", None, "idle", "no-candidate"),
    ]
    original_build_plan = gstack_loop.build_plan
    failures: list[str] = []
    try:
        for name, item, expected_status, expected_kind in cases:
            gstack_loop.build_plan = lambda args, selected=item: plan_for(selected)  # type: ignore[assignment]
            report = gstack_loop.build_test_repair_loop_report(repair_loop_args("--dry-run"))
            if report.status != expected_status:
                failures.append(f"{name}: expected status {expected_status}, got {report.status}")
            if report.failure_analysis.failure_kind != expected_kind:
                failures.append(f"{name}: expected kind {expected_kind}, got {report.failure_analysis.failure_kind}")
            if item is not None and report.commands and any(command.status == "passed" for command in report.commands):
                failures.append(f"{name}: stop state must not pass commands")
    finally:
        gstack_loop.build_plan = original_build_plan  # type: ignore[assignment]
    if failures:
        return fail("repair-loop-stop-states", "repair-loop stop states regressed.", failures)
    return ok("repair-loop-stop-states", "repair-loop refuses idle, inactive, blocked and evidence-missing tasks.")


def check_repair_loop_report_layer() -> ContractResult:
    item = candidate("qa")
    original_build_plan = gstack_loop.build_plan
    original_verification_commands = gstack_loop.verification_commands
    failures: list[str] = []
    mixed_commands = [
        "python3 .gstack/scripts/spec_sync_guard.py",
        "echo unsafe",
        "python3 .gstack/scripts/gstack_loop.py repair-loop --execute --format json",
    ]
    try:
        gstack_loop.build_plan = lambda args: plan_for(item)  # type: ignore[assignment]
        gstack_loop.verification_commands = lambda selected: ("contract-fixture", [])  # type: ignore[assignment]
        empty_report = gstack_loop.build_test_repair_loop_report(repair_loop_args("--execute"))
        if empty_report.status != "no-commands":
            failures.append(f"empty repair-loop status: expected no-commands, got {empty_report.status}")
        if empty_report.passed_count != 0 or empty_report.command_count != 0:
            failures.append("empty repair-loop should not count passed commands")

        gstack_loop.verification_commands = lambda selected: ("contract-fixture", mixed_commands)  # type: ignore[assignment]
        dry_run_report = gstack_loop.build_test_repair_loop_report(repair_loop_args("--dry-run"))
        statuses = [command.status for command in dry_run_report.commands]
        allowed = [command.allowed for command in dry_run_report.commands]
        reasons = [command.skipped_reason for command in dry_run_report.commands]
        if dry_run_report.status != "blocked":
            failures.append(f"mixed repair-loop status should be blocked because skipped commands are refused, got {dry_run_report.status}")
        if dry_run_report.command_count != 3 or dry_run_report.skipped_count != 3:
            failures.append(
                f"mixed repair-loop counters changed: command={dry_run_report.command_count}, skipped={dry_run_report.skipped_count}"
            )
        if statuses != ["dry-run", "skipped", "skipped"]:
            failures.append(f"mixed repair-loop command statuses changed: {statuses}")
        if allowed != [True, False, False]:
            failures.append(f"mixed repair-loop command allow flags changed: {allowed}")
        if "allowlist" not in reasons[1]:
            failures.append("repair-loop non-allowlist command did not report allowlist skip")
        if "自我递归" not in reasons[2]:
            failures.append("repair-loop recursive command did not report recursion skip")
    finally:
        gstack_loop.build_plan = original_build_plan  # type: ignore[assignment]
        gstack_loop.verification_commands = original_verification_commands  # type: ignore[assignment]
    if failures:
        return fail("repair-loop-report-layer", "repair-loop report layer regressed.", failures)
    return ok("repair-loop-report-layer", "repair-loop keeps dry-run, skip, recursion and empty-command semantics.")


def check_eng_review_json_schema() -> ContractResult:
    payload, details = load_json_command(
        "eng-review-json-schema",
        python_command(".gstack/scripts/gstack_loop.py", "eng-review", "--format", "json", "--limit", "1"),
    )
    if payload is None:
        return fail("eng-review-json-schema", "eng-review did not return JSON.", details)
    failures = require_keys(
        payload,
        [
            "generated_at",
            "schema_version",
            "decisioner_version",
            "mode",
            "status",
            "selected",
            "candidate_status",
            "eng_review_decisioner",
            "stop_conditions",
            "non_actions",
        ],
    )
    if payload.get("schema_version") != gstack_loop.SCHEMA_VERSION:
        failures.append("schema_version does not match gstack_loop.SCHEMA_VERSION")
    if payload.get("decisioner_version") != gstack_loop.ENG_REVIEW_DECISIONER_VERSION:
        failures.append("decisioner_version does not match gstack_loop.ENG_REVIEW_DECISIONER_VERSION")
    decisioner = payload.get("eng_review_decisioner") or {}
    if not isinstance(decisioner, dict):
        failures.append("eng_review_decisioner is not an object")
    else:
        for key in [
            "status",
            "decisioner_version",
            "trigger_stages",
            "codex_owned_decisions",
            "user_owned_decisions",
            "forbidden_user_delegations",
            "required_evidence_markers",
            "generation_policy",
            "check_policy",
            "evidence_check",
        ]:
            if key not in decisioner:
                failures.append(f"eng_review_decisioner missing key: {key}")
        check = decisioner.get("evidence_check") or {}
        if not isinstance(check, dict):
            failures.append("eng_review_decisioner.evidence_check is not an object")
        else:
            for key in [
                "evidence_path",
                "exists",
                "status",
                "required_markers",
                "found_required_markers",
                "missing_required_markers",
                "forbidden_user_delegations",
                "forbidden_user_delegations_found",
                "summary",
            ]:
                if key not in check:
                    failures.append(f"eng_review_decisioner.evidence_check missing key: {key}")
    if failures:
        return fail("eng-review-json-schema", "eng-review JSON schema changed unexpectedly.", [*details, *failures])
    return ok("eng-review-json-schema", "eng-review JSON has the stable decisioner fields.", details)


def check_eng_review_decisioner_policy() -> ContractResult:
    decisioner = gstack_loop.eng_review_decisioner_for(candidate("plan-eng-review"))
    idle_decisioner = gstack_loop.eng_review_decisioner_for(None)
    failures: list[str] = []
    if decisioner.decisioner_version != gstack_loop.ENG_REVIEW_DECISIONER_VERSION:
        failures.append("decisioner version changed")
    for expected in ["代码结构", "测试组合", "subagent"]:
        if not any(expected in item for item in decisioner.codex_owned_decisions):
            failures.append(f"codex_owned_decisions missing {expected}")
    for forbidden in ["需要用户选择测试命令", "用户决定门禁恢复顺序"]:
        if forbidden not in decisioner.forbidden_user_delegations:
            failures.append(f"forbidden delegation missing: {forbidden}")
    for marker in ["AI 语义复核: yes", "## Codex 自主工程决策", "## 用户决策边界", "## 防技术甩锅检查", "## 验证计划"]:
        if marker not in decisioner.required_evidence_markers:
            failures.append(f"required marker missing: {marker}")
    if not any("业务" in item for item in decisioner.user_owned_decisions):
        failures.append("user_owned_decisions must stay limited to business / authorization choices")
    if idle_decisioner.status != "idle":
        failures.append(f"idle decisioner status changed: {idle_decisioner.status}")
    if idle_decisioner.evidence_check.status != "not-checked":
        failures.append(f"idle decisioner evidence check changed: {idle_decisioner.evidence_check.status}")
    if failures:
        return fail("eng-review-decisioner-policy", "ENG review decisioner policy regressed.", failures)
    return ok("eng-review-decisioner-policy", "ENG review decisioner keeps technical choices owned by Codex.")


def check_eng_review_evidence_checker() -> ContractResult:
    temp_review = REPO_ROOT / ".gstack" / "reviews" / f"contract-smoke-eng-review-{os.getpid()}.tmp.md"
    failures: list[str] = []
    pass_text = "\n".join(
        [
            "# Contract Smoke ENG Review",
            "",
            "- AI 语义复核: yes",
            "",
            "## Codex 自主工程决策",
            "",
            "- Codex 选择工程方案、代码结构和测试组合。",
            "",
            "## 用户决策边界",
            "",
            "- 用户只决定业务目标和高风险授权。",
            "",
            "## 防技术甩锅检查",
            "",
            "- 不把测试命令、代码结构、subagent 角色或门禁恢复顺序交给用户。",
            "",
            "## 验证计划",
            "",
            "- 运行 contract smoke。",
        ]
    )
    forbidden_text = pass_text + "\n\n- 需要用户选择测试命令。\n"
    missing_text = "# Contract Smoke ENG Review\n\n- AI 语义复核: yes\n"
    try:
        temp_review.write_text(pass_text, encoding="utf-8")
        passed = gstack_loop.eng_review_evidence_check_for(temp_review.relative_to(REPO_ROOT).as_posix())
        if passed.status != "pass":
            failures.append(f"expected pass, got {passed.status}: {passed.summary}")
        temp_review.write_text(forbidden_text, encoding="utf-8")
        forbidden = gstack_loop.eng_review_evidence_check_for(temp_review.relative_to(REPO_ROOT).as_posix())
        if forbidden.status != "needs-rewrite":
            failures.append(f"expected needs-rewrite, got {forbidden.status}")
        if "需要用户选择测试命令" not in forbidden.forbidden_user_delegations_found:
            failures.append("forbidden user delegation marker was not detected")
        temp_review.write_text(missing_text, encoding="utf-8")
        missing = gstack_loop.eng_review_evidence_check_for(temp_review.relative_to(REPO_ROOT).as_posix())
        if missing.status != "needs-evidence":
            failures.append(f"expected needs-evidence, got {missing.status}")
    finally:
        temp_review.unlink(missing_ok=True)
    if failures:
        return fail("eng-review-evidence-checker", "ENG review evidence checker regressed.", failures)
    return ok("eng-review-evidence-checker", "ENG review evidence checker detects pass, missing markers and user-delegated technical choices.")


def check_authorization_classifier() -> ContractResult:
    local_continue = gstack_loop.chat_authorization_for("同意，继续做")
    auto_continue = gstack_loop.chat_authorization_for("全自动做完")
    ambiguous = gstack_loop.chat_authorization_for("我确认")
    git = gstack_loop.chat_authorization_for("提交并推送")
    forbidden_git = gstack_loop.chat_authorization_for("不要提交也不要推送")
    production = gstack_loop.chat_authorization_for("发布到生产")
    database = gstack_loop.chat_authorization_for("执行 migration")
    forbidden_database = gstack_loop.chat_authorization_for("不改数据库")
    destructive = gstack_loop.chat_authorization_for("撤销刚才的改动")
    failures: list[str] = []
    required_fields = (
        "classifier_version",
        "authorization_scope",
        "confirmation_strength",
        "matched_markers",
        "required_explicit_phrase",
    )
    for label, decision in {
        "同意，继续做": local_continue,
        "全自动做完": auto_continue,
        "我确认": ambiguous,
        "提交并推送": git,
        "不要提交也不要推送": forbidden_git,
        "发布到生产": production,
        "执行 migration": database,
        "不改数据库": forbidden_database,
        "撤销刚才的改动": destructive,
    }.items():
        for field in required_fields:
            if not hasattr(decision, field):
                failures.append(f"{label} missing field: {field}")
        if decision.classifier_version != gstack_loop.CHAT_AUTHORIZATION_RUNTIME_VERSION:
            failures.append(f"{label} classifier_version: {decision.classifier_version}")
    for decision in (local_continue, auto_continue):
        if decision.category != "continue-local-work":
            failures.append(f"{decision.raw} category: {decision.category}")
        if not decision.authorization_granted or not decision.can_continue_locally:
            failures.append(f"{decision.raw} should grant only low-risk local continuation")
        if decision.authorization_scope != "local-work-only":
            failures.append(f"{decision.raw} scope: {decision.authorization_scope}")
    if ambiguous.category != "ambiguous-confirmation":
        failures.append(f"我确认 category: {ambiguous.category}")
    if ambiguous.authorization_granted:
        failures.append("我确认 must not grant high-risk authorization")
    if not ambiguous.can_continue_locally:
        failures.append("我确认 should still allow low-risk local continuation")
    if ambiguous.authorization_scope != "ambiguous-local-only":
        failures.append(f"我确认 scope: {ambiguous.authorization_scope}")
    if git.category != "git-workflow" or not git.authorization_granted:
        failures.append(f"提交并推送 should be explicit git workflow authorization, got {git.category}/{git.authorization_granted}")
    if git.authorization_scope != "git-workflow" or git.confirmation_strength != "explicit-high-risk":
        failures.append(f"提交并推送 scope/strength: {git.authorization_scope}/{git.confirmation_strength}")
    if forbidden_git.category != "forbidden-git-scope" or forbidden_git.authorization_granted:
        failures.append(f"negated git phrase should be forbidden scope, got {forbidden_git.category}/{forbidden_git.authorization_granted}")
    if not forbidden_git.can_continue_locally:
        failures.append("negated git phrase should still allow local non-git continuation")
    if production.category != "deploy-or-production" or not production.authorization_granted:
        failures.append(f"发布到生产 should be explicit production authorization, got {production.category}/{production.authorization_granted}")
    if database.category != "database-or-real-data" or not database.authorization_granted:
        failures.append(f"执行 migration should be explicit DB authorization, got {database.category}/{database.authorization_granted}")
    if forbidden_database.category != "forbidden-database-scope" or forbidden_database.authorization_granted:
        failures.append(f"不改数据库 should forbid DB scope, got {forbidden_database.category}/{forbidden_database.authorization_granted}")
    if not forbidden_database.can_continue_locally:
        failures.append("forbidden DB scope should still allow local non-DB continuation")
    if destructive.category != "destructive-action":
        failures.append(f"撤销刚才的改动 category: {destructive.category}")
    if destructive.authorization_granted:
        failures.append("destructive vague rollback must not be executable authorization")
    if destructive.confirmation_strength != "scope-required":
        failures.append(f"destructive strength: {destructive.confirmation_strength}")
    if failures:
        return fail("authorization-classifier", "Chat authorization classifier regressed.", failures)
    return ok("authorization-classifier", "Chat authorization classifier covers local continuation, ambiguity, high-risk grants and forbidden scopes.")


def check_chat_smoke_json_schema() -> ContractResult:
    payload, details = load_json_command(
        "chat-smoke-json-schema",
        python_command(".gstack/scripts/gstack_loop.py", "chat-smoke", "--format", "json"),
    )
    if payload is None:
        return fail("chat-smoke-json-schema", "chat-smoke did not return JSON.", details)
    failures = require_keys(
        payload,
        [
            "schema_version",
            "smoke_version",
            "planner_version",
            "status",
            "stage_count",
            "covered_stage_keys",
            "missing_stage_keys",
            "local_continuation",
            "ambiguous_confirmation",
            "explicit_git_authorization",
            "forbidden_git_scope",
            "final_protocol",
            "final_state",
            "steps",
            "non_actions",
        ],
    )
    if payload.get("schema_version") != gstack_loop.SCHEMA_VERSION:
        failures.append("schema_version does not match gstack_loop.SCHEMA_VERSION")
    if payload.get("smoke_version") != gstack_loop.CHAT_FIRST_LOOP_SMOKE_VERSION:
        failures.append("smoke_version does not match CHAT_FIRST_LOOP_SMOKE_VERSION")
    if payload.get("planner_version") != gstack_loop.PLANNER_VERSION:
        failures.append("planner_version does not match gstack_loop.PLANNER_VERSION")
    if payload.get("status") != "ok":
        failures.append(f"status should be ok, got {payload.get('status')}")
    expected_stages = list(gstack_loop.STAGE_ORDER)
    if payload.get("covered_stage_keys") != expected_stages:
        failures.append(f"covered stages changed: {payload.get('covered_stage_keys')}")
    if payload.get("stage_count") != len(expected_stages):
        failures.append(f"stage_count changed: {payload.get('stage_count')}")
    if payload.get("missing_stage_keys") != []:
        failures.append(f"missing_stage_keys should be empty: {payload.get('missing_stage_keys')}")
    if payload.get("final_protocol", {}).get("stage_status") != "idle":
        failures.append("final_protocol should be idle")
    if payload.get("final_state") != "idle-after-complete-evidence":
        failures.append(f"final_state changed: {payload.get('final_state')}")
    local = payload.get("local_continuation") or {}
    ambiguous = payload.get("ambiguous_confirmation") or {}
    git = payload.get("explicit_git_authorization") or {}
    forbidden_git = payload.get("forbidden_git_scope") or {}
    if local.get("category") != "continue-local-work" or local.get("authorization_scope") != "local-work-only":
        failures.append(f"local continuation changed: {local}")
    if ambiguous.get("authorization_granted") is not False:
        failures.append("ambiguous confirmation must not grant high-risk authorization")
    if git.get("category") != "git-workflow" or git.get("authorization_granted") is not True:
        failures.append(f"explicit git authorization changed: {git}")
    if forbidden_git.get("category") != "forbidden-git-scope" or forbidden_git.get("authorization_granted") is not False:
        failures.append(f"forbidden git scope changed: {forbidden_git}")
    steps = payload.get("steps") or []
    if len(steps) != len(expected_stages):
        failures.append(f"steps length changed: {len(steps)}")
    else:
        for step in steps:
            for key in ["stage_key", "evidence_target", "codex_will_do", "user_must_choose", "checks"]:
                if key not in step:
                    failures.append(f"step missing {key}: {step}")
    non_actions = "\n".join(payload.get("non_actions") or [])
    for forbidden in ["不会连接真实数据", "不会创建共享 dashboard", "不会把模糊确认当成生产"]:
        if forbidden not in non_actions:
            failures.append(f"missing non-action phrase: {forbidden}")
    if failures:
        return fail("chat-smoke-json-schema", "chat-smoke end-to-end schema regressed.", failures + details)
    return ok("chat-smoke-json-schema", "chat-smoke covers the full chat-first loop, authorization samples and final idle state.", details)


def check_nl_smoke_json_schema() -> ContractResult:
    payload, details = load_json_command(
        "nl-smoke-json-schema",
        python_command(".gstack/scripts/gstack_loop.py", "nl-smoke", "--format", "json"),
    )
    if payload is None:
        return fail("nl-smoke-json-schema", "nl-smoke did not return JSON.", details)
    failures = require_keys(
        payload,
        [
            "schema_version",
            "smoke_version",
            "planner_version",
            "status",
            "mode",
            "raw_request",
            "next_step",
            "formal_kickoff",
            "next_step_intent",
            "next_step_helper_entry",
            "formal_status",
            "formal_can_write",
            "formal_written",
            "formal_activated",
            "formal_paths",
            "acceptance_checks",
            "readiness_checks",
            "failure_reasons",
            "final_state",
            "non_actions",
        ],
    )
    if payload.get("schema_version") != gstack_loop.SCHEMA_VERSION:
        failures.append("schema_version does not match gstack_loop.SCHEMA_VERSION")
    if payload.get("smoke_version") != gstack_loop.NATURAL_LANGUAGE_LOOP_SMOKE_VERSION:
        failures.append("smoke_version does not match NATURAL_LANGUAGE_LOOP_SMOKE_VERSION")
    if payload.get("planner_version") != gstack_loop.PLANNER_VERSION:
        failures.append("planner_version does not match gstack_loop.PLANNER_VERSION")
    if payload.get("status") != "ok":
        failures.append(f"status should be ok, got {payload.get('status')}")
    if payload.get("next_step_intent") != "formal_kickoff_preview":
        failures.append(f"next_step_intent changed: {payload.get('next_step_intent')}")
    if payload.get("next_step_helper_entry") != "nontechnical_formal_kickoff.user":
        failures.append(f"next_step_helper_entry changed: {payload.get('next_step_helper_entry')}")
    if payload.get("next_step_needs_user_confirmation") is not False:
        failures.append("next_step should not require user confirmation for fixed safe request")
    if payload.get("formal_status") != "ready-to-write":
        failures.append(f"formal_status changed: {payload.get('formal_status')}")
    if payload.get("formal_can_write") is not True:
        failures.append("formal_can_write should be true")
    if payload.get("formal_written") is not False:
        failures.append("formal dry-run must not write evidence")
    if payload.get("formal_activated") is not False:
        failures.append("formal dry-run must not activate boundary")
    if payload.get("formal_ai_reviewed") is not True:
        failures.append("formal_ai_reviewed should be true")
    if payload.get("final_state") != "ready-to-write-dry-run-not-written":
        failures.append(f"final_state changed: {payload.get('final_state')}")
    paths = payload.get("formal_paths") or {}
    if not isinstance(paths, dict):
        failures.append("formal_paths is not an object")
    else:
        for key in ["requirement", "review", "boundary", "qa"]:
            if not str(paths.get(key) or "").startswith(".gstack/"):
                failures.append(f"formal_paths missing {key}: {paths.get(key)}")
    checks = payload.get("acceptance_checks") or []
    if not isinstance(checks, list) or len(checks) < 4:
        failures.append("acceptance_checks should be a list with user-visible checks")
    else:
        joined = "\n".join(str(item) for item in checks)
        for expected in ["第一眼", "导出", "不改生产数据库"]:
            if expected not in joined:
                failures.append(f"acceptance_checks missing phrase: {expected}")
    readiness = "\n".join(payload.get("readiness_checks") or [])
    for expected in ["formal kickoff dry-run is ready-to-write", "did not write evidence", "did not activate boundary"]:
        if expected not in readiness:
            failures.append(f"readiness_checks missing phrase: {expected}")
    if payload.get("failure_reasons") != []:
        failures.append(f"failure_reasons should be empty: {payload.get('failure_reasons')}")
    non_actions = "\n".join(payload.get("non_actions") or [])
    for forbidden in ["不传 --write", "不会创建真实业务", "不会连接真实数据"]:
        if forbidden not in non_actions:
            failures.append(f"missing non-action phrase: {forbidden}")
    if failures:
        return fail("nl-smoke-json-schema", "nl-smoke real-helper dry-run schema regressed.", failures + details)
    return ok("nl-smoke-json-schema", "nl-smoke covers real natural-language kickoff preview, dry-run non-write semantics and acceptance checks.", details)


def check_subagent_timeout_policy() -> ContractResult:
    policy = gstack_loop.subagent_timeout_policy()
    item = candidate("implement")
    recommendation = gstack_loop.subagent_recommendation_for(item)
    failures: list[str] = []
    if policy.default_checkpoint_seconds != 60:
        failures.append(f"checkpoint default changed: {policy.default_checkpoint_seconds}")
    if policy.default_deadline_seconds != 240:
        failures.append(f"deadline default changed: {policy.default_deadline_seconds}")
    if policy.max_files_per_readonly_agent > 3:
        failures.append(f"readonly max_files too broad: {policy.max_files_per_readonly_agent}")
    if policy.max_retry_attempts != 1:
        failures.append(f"retry attempts changed: {policy.max_retry_attempts}")
    for expected in ["timeout-without-checkpoint", "scope-too-wide"]:
        if expected not in policy.timeout_classifications:
            failures.append(f"missing timeout classification: {expected}")
    if not any("不能写成 QA 通过" in rule or "不能写成 QA" in rule for rule in policy.evidence_rules):
        failures.append("evidence rules must forbid pretending timeout is QA pass")
    if not recommendation.candidate_subagents:
        failures.append("implement stage should recommend timeout-governed subagents")
    for subagent in recommendation.candidate_subagents:
        for key in ["checkpoint_seconds", "deadline_seconds", "max_files", "result_schema", "timeout_recovery"]:
            if key not in subagent:
                failures.append(f"{subagent.get('name', 'subagent')} missing {key}")
        if subagent.get("role") in {"reviewer", "explorer"} and int(subagent.get("max_files", "99")) > 3:
            failures.append(f"{subagent.get('name')} readonly max_files exceeds policy")
        if "do not pretend pass" not in subagent.get("timeout_recovery", ""):
            failures.append(f"{subagent.get('name')} timeout recovery must forbid pretending pass")
    if failures:
        return fail("subagent-timeout-policy", "Subagent timeout policy regressed.", failures)
    return ok("subagent-timeout-policy", "Subagent timeout policy covers checkpoint, deadline, retry and timeout evidence.")


def check_stage_write_back_contract() -> ContractResult:
    temp_boundary = REPO_ROOT / ".gstack" / "task-boundaries" / f"contract-smoke-writeback-{os.getpid()}.tmp.md"
    temp_boundary.write_text(
        "\n".join(
            [
                "# Contract Smoke Writeback",
                "",
                "## GStack Required Flow",
                "",
                "- qa:",
                "  status: pending",
                "  evidence:",
                "",
            ]
        ),
        encoding="utf-8",
    )
    item = gstack_loop.LoopCandidate(
        task="contract writeback",
        boundary=temp_boundary.relative_to(REPO_ROOT).as_posix(),
        active=True,
        blocked=False,
        progress="6/7",
        current_stage_key="qa",
        current_stage="qa",
        next_step="qa",
        selection_reason="contract smoke",
        blocked_reasons=[],
        evidence_missing=[],
    )
    failures: list[str] = []
    try:
        dry_run_result = gstack_loop.maybe_write_back_stage(
            run_args("--dry-run", "--write-back", "--write-back-evidence", ".gstack/scripts/gstack_loop.py"),
            candidate=item,
            stage_key="qa",
            report_status="passed",
        )
        if dry_run_result.performed:
            failures.append("dry-run write-back should not perform")
        missing_evidence_result = gstack_loop.maybe_write_back_stage(
            run_args("--execute", "--write-back", "--write-back-evidence", ".gstack/missing-evidence.md"),
            candidate=item,
            stage_key="qa",
            report_status="passed",
        )
        if missing_evidence_result.performed:
            failures.append("missing evidence write-back should not perform")
        failed_result = gstack_loop.maybe_write_back_stage(
            run_args("--execute", "--write-back", "--write-back-evidence", ".gstack/scripts/gstack_loop.py"),
            candidate=item,
            stage_key="qa",
            report_status="failed",
        )
        if failed_result.performed:
            failures.append("failed report write-back should not perform")
        passed_result = gstack_loop.maybe_write_back_stage(
            run_args("--execute", "--write-back", "--write-back-evidence", ".gstack/scripts/gstack_loop.py", "--write-back-note", "contract smoke"),
            candidate=item,
            stage_key="qa",
            report_status="passed",
        )
        if not passed_result.performed:
            failures.append(f"passed write-back should perform: {passed_result.reason}")
        updated = temp_boundary.read_text(encoding="utf-8")
        if "status: done" not in updated:
            failures.append("write-back did not set status: done")
        if "evidence: `.gstack/scripts/gstack_loop.py`" not in updated:
            failures.append("write-back did not write evidence path")
        if "note: contract smoke" not in updated:
            failures.append("write-back did not write note")
    finally:
        temp_boundary.unlink(missing_ok=True)
    if failures:
        return fail("stage-write-back", "Stage write-back safety contract regressed.", failures)
    return ok("stage-write-back", "Stage write-back requires execute, passed status and existing evidence before updating boundary.")


def check_write_back_json_schema() -> ContractResult:
    payload, details = load_json_command(
        "write-back-json-schema",
        python_command(
            ".gstack/scripts/gstack_loop.py",
            "write-back",
            "--dry-run",
            "--format",
            "json",
            "--limit",
            "1",
            "--evidence",
            ".gstack/scripts/gstack_loop.py",
        ),
    )
    if payload is None:
        return fail("write-back-json-schema", "write-back did not return JSON.", details)
    failures = require_keys(
        payload,
        [
            "generated_at",
            "schema_version",
            "writer_version",
            "mode",
            "dry_run",
            "execute_requested",
            "status",
            "selected",
            "candidate_status",
            "requested_stage_key",
            "current_stage_key",
            "next_stage_on_success",
            "write_back_result",
            "closure_policy",
            "stop_conditions",
            "non_actions",
        ],
    )
    if payload.get("schema_version") != gstack_loop.SCHEMA_VERSION:
        failures.append("schema_version does not match gstack_loop.SCHEMA_VERSION")
    if payload.get("writer_version") != gstack_loop.STAGE_WRITE_BACK_CLOSURE_VERSION:
        failures.append("writer_version does not match stage write-back closure version")
    if payload.get("dry_run") is not True:
        failures.append("write-back must default to dry-run for this check")
    if payload.get("execute_requested") is not False:
        failures.append("write-back dry-run must not mark execute_requested")
    result = payload.get("write_back_result") or {}
    if not isinstance(result, dict):
        failures.append("write_back_result is not an object")
    elif result.get("performed") is not False:
        failures.append("write-back dry-run must not perform")
    closure = payload.get("closure_policy") or {}
    if not isinstance(closure, dict):
        failures.append("closure_policy is not an object")
    else:
        for key in [
            "writer_version",
            "current_stage_key",
            "suggested_evidence",
            "suggested_command",
            "stage_evidence_rules",
            "allowed_when",
            "refused_when",
            "non_actions",
        ]:
            if key not in closure:
                failures.append(f"closure_policy missing key: {key}")
    if failures:
        return fail("write-back-json-schema", "write-back JSON schema changed unexpectedly.", [*details, *failures])
    return ok("write-back-json-schema", "write-back JSON has the stable closure fields.", details)


def check_stage_write_back_closure_policy() -> ContractResult:
    item = candidate("implement")
    policy = gstack_loop.stage_write_back_closure_for(item)
    failures: list[str] = []
    if policy.writer_version != gstack_loop.STAGE_WRITE_BACK_CLOSURE_VERSION:
        failures.append("writer_version changed")
    if policy.current_stage_key != "implement":
        failures.append(f"current_stage_key changed: {policy.current_stage_key}")
    if "write-back --execute" not in policy.suggested_command:
        failures.append("suggested_command must use explicit write-back --execute")
    if "<repo-evidence-path>" not in policy.suggested_command:
        failures.append("non-path evidence targets must render as a repo evidence placeholder")
    for stage in ["requirement-brief", "implement", "qa"]:
        if not any(rule.get("stage_key") == stage for rule in policy.stage_evidence_rules):
            failures.append(f"stage_evidence_rules missing {stage}")
    if not any("--stage-key" in item or "current stage" in item for item in policy.refused_when):
        failures.append("refused_when must mention stage-key/current-stage guard")
    if not any("不生成 requirement" in item for item in policy.non_actions):
        failures.append("non_actions must say write-back does not generate evidence body")
    if failures:
        return fail("stage-write-back-closure-policy", "Stage write-back closure policy regressed.", failures)
    return ok("stage-write-back-closure-policy", "Stage write-back closure policy keeps explicit execute, evidence and current-stage guards.")


def check_write_back_command_contract() -> ContractResult:
    temp_boundary = REPO_ROOT / ".gstack" / "task-boundaries" / f"contract-smoke-writeback-command-{os.getpid()}.tmp.md"
    temp_boundary.write_text(
        "\n".join(
            [
                "# Contract Smoke Writeback Command",
                "",
                "## GStack Required Flow",
                "",
                "- implement:",
                "  status: pending",
                "  evidence:",
                "- qa:",
                "  status: pending",
                "  evidence:",
                "",
            ]
        ),
        encoding="utf-8",
    )
    item = gstack_loop.LoopCandidate(
        task="contract writeback command",
        boundary=temp_boundary.relative_to(REPO_ROOT).as_posix(),
        active=True,
        blocked=False,
        progress="5/7",
        current_stage_key="implement",
        current_stage="implement",
        next_step="implement",
        selection_reason="contract smoke",
        blocked_reasons=[],
        evidence_missing=[],
    )
    original_build_plan = gstack_loop.build_plan
    failures: list[str] = []
    try:
        gstack_loop.build_plan = lambda args: plan_for(item)  # type: ignore[assignment]

        dry_run_report = gstack_loop.build_write_back_report(
            write_back_args("--dry-run", "--evidence", ".gstack/scripts/gstack_loop.py")
        )
        if dry_run_report.status != "dry-run":
            failures.append(f"dry-run status changed: {dry_run_report.status}")
        if dry_run_report.write_back_result.performed:
            failures.append("dry-run write-back command should not perform")
        if "status: done" in temp_boundary.read_text(encoding="utf-8"):
            failures.append("dry-run write-back command edited boundary")

        missing_evidence_report = gstack_loop.build_write_back_report(
            write_back_args("--execute", "--evidence", ".gstack/missing-evidence.md")
        )
        if missing_evidence_report.write_back_result.performed:
            failures.append("missing evidence write-back command should not perform")

        mismatch_report = gstack_loop.build_write_back_report(
            write_back_args("--execute", "--stage-key", "qa", "--evidence", ".gstack/scripts/gstack_loop.py")
        )
        if mismatch_report.status != "refused":
            failures.append(f"stage mismatch status changed: {mismatch_report.status}")
        if mismatch_report.write_back_result.performed:
            failures.append("stage mismatch write-back command should not perform")

        passed_report = gstack_loop.build_write_back_report(
            write_back_args("--execute", "--evidence", ".gstack/scripts/gstack_loop.py", "--note", "contract closure")
        )
        if passed_report.status != "updated":
            failures.append(f"passed write-back status changed: {passed_report.status}")
        if not passed_report.write_back_result.performed:
            failures.append(f"passed write-back command should perform: {passed_report.write_back_result.reason}")
        updated = temp_boundary.read_text(encoding="utf-8")
        if "- implement:" not in updated or "status: done" not in updated:
            failures.append("write-back command did not update implement stage")
        if "evidence: `.gstack/scripts/gstack_loop.py`" not in updated:
            failures.append("write-back command did not write evidence path")
        if "note: contract closure" not in updated:
            failures.append("write-back command did not write note")
        if "- qa:\n  status: pending" not in updated:
            failures.append("write-back command should not update the next stage")
    finally:
        gstack_loop.build_plan = original_build_plan  # type: ignore[assignment]
        temp_boundary.unlink(missing_ok=True)
    if failures:
        return fail("write-back-command-contract", "write-back command safety contract regressed.", failures)
    return ok("write-back-command-contract", "write-back command handles dry-run, missing evidence, stage mismatch and current-stage update.")


def check_report_layer_contract() -> ContractResult:
    item = candidate("qa")
    original_build_plan = gstack_loop.build_plan
    original_verification_commands = gstack_loop.verification_commands
    failures: list[str] = []
    mixed_commands = [
        "python3 .gstack/scripts/spec_sync_guard.py",
        "echo unsafe",
        "python3 .gstack/scripts/gstack_loop.py run --execute --format json",
    ]
    try:
        gstack_loop.build_plan = lambda args: plan_for(item)  # type: ignore[assignment]
        gstack_loop.verification_commands = lambda selected: ("contract-fixture", [])  # type: ignore[assignment]
        empty_run_report = gstack_loop.build_run_report(run_args("--execute"))
        if empty_run_report.status != "no-commands":
            failures.append(f"run empty Verification status: expected no-commands, got {empty_run_report.status}")
        if empty_run_report.passed_count != 0 or empty_run_report.command_count != 0:
            failures.append("run empty Verification should not count passed commands")
        empty_advance_report = gstack_loop.build_advance_report(advance_args("--execute"))
        if empty_advance_report.status != "no-commands":
            failures.append(f"advance empty Verification status: expected no-commands, got {empty_advance_report.status}")
        if empty_advance_report.passed_count != 0 or empty_advance_report.command_count != 0:
            failures.append("advance empty Verification should not count passed commands")

        gstack_loop.verification_commands = lambda selected: ("contract-fixture", mixed_commands)  # type: ignore[assignment]
        run_report = gstack_loop.build_run_report(run_args("--dry-run"))
        advance_report = gstack_loop.build_advance_report(advance_args("--dry-run"))
        for label, report in [("run", run_report), ("advance", advance_report)]:
            statuses = [command.status for command in report.commands]
            allowed = [command.allowed for command in report.commands]
            reasons = [command.skipped_reason for command in report.commands]
            if report.status != "dry-run":
                failures.append(f"{label} report status: expected dry-run, got {report.status}")
            if report.command_count != 3 or report.skipped_count != 3 or report.passed_count != 0 or report.failed_count != 0:
                failures.append(
                    f"{label} counters changed: command={report.command_count}, skipped={report.skipped_count}, "
                    f"passed={report.passed_count}, failed={report.failed_count}"
                )
            if statuses != ["dry-run", "skipped", "skipped"]:
                failures.append(f"{label} command statuses changed: {statuses}")
            if allowed != [True, False, False]:
                failures.append(f"{label} command allow flags changed: {allowed}")
            if "allowlist" not in reasons[1]:
                failures.append(f"{label} non-allowlist command did not report allowlist skip")
            if "自我递归" not in reasons[2]:
                failures.append(f"{label} recursive command did not report recursion skip")
    finally:
        gstack_loop.build_plan = original_build_plan  # type: ignore[assignment]
        gstack_loop.verification_commands = original_verification_commands  # type: ignore[assignment]
    if failures:
        return fail("report-layer-contract", "run / advance report layer regressed.", failures)
    return ok("report-layer-contract", "run and advance reports keep dry-run, skip and empty-command semantics.")


def check_dry_run_defaults() -> ContractResult:
    parser = gstack_loop.build_parser()
    run_args = parser.parse_args(["run"])
    advance_args = parser.parse_args(["advance"])
    repair_args = parser.parse_args(["repair-loop"])
    failures: list[str] = []
    if run_args.dry_run is not True:
        failures.append("run default dry_run is not true")
    if advance_args.dry_run is not True:
        failures.append("advance default dry_run is not true")
    if repair_args.dry_run is not True:
        failures.append("repair-loop default dry_run is not true")
    if failures:
        return fail("dry-run-defaults", "run / advance / repair-loop default execution mode changed.", failures)
    return ok("dry-run-defaults", "run, advance and repair-loop default to dry-run.")


def all_checks() -> list[ContractResult]:
    return [
        check_plan_json_schema(),
        check_advance_json_schema(),
        check_run_json_schema(),
        check_repair_loop_json_schema(),
        check_stage_matrix(),
        check_stop_states(),
        check_execution_safety(),
        check_v6_boundary_allowlist(),
        check_v7_boundary_allowlist(),
        check_v8_boundary_allowlist(),
        check_v9_boundary_allowlist(),
        check_v10_boundary_allowlist(),
        check_v11_boundary_allowlist(),
        check_v12_boundary_allowlist(),
        check_v13_boundary_allowlist(),
        check_v14_boundary_allowlist(),
        check_v15_boundary_allowlist(),
        check_subagents_json_schema(),
        check_repair_loop_failure_analysis(),
        check_repair_loop_stop_states(),
        check_repair_loop_report_layer(),
        check_eng_review_json_schema(),
        check_eng_review_decisioner_policy(),
        check_eng_review_evidence_checker(),
        check_authorization_classifier(),
        check_chat_smoke_json_schema(),
        check_nl_smoke_json_schema(),
        check_subagent_timeout_policy(),
        check_subagent_orchestration_policy(),
        check_subagent_orchestration_stop_states(),
        check_stage_write_back_contract(),
        check_write_back_json_schema(),
        check_stage_write_back_closure_policy(),
        check_write_back_command_contract(),
        check_report_layer_contract(),
        check_dry_run_defaults(),
    ]


def render_json(results: list[ContractResult]) -> str:
    failed = [item for item in results if item.status != "ok"]
    payload = {
        "status": "fail" if failed else "ok",
        "check_count": len(results),
        "failed_count": len(failed),
        "results": [asdict(item) for item in results],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def render_user(results: list[ContractResult]) -> str:
    failed = [item for item in results if item.status != "ok"]
    lines = [
        "Loop Engineering 契约检查" + ("未通过。" if failed else "通过。"),
        "",
        "已覆盖：",
        *[f"- {line}" for line in USER_COVERAGE_LINES],
    ]
    if failed:
        lines.extend(["", "需要修复："])
        for item in failed:
            lines.append(f"- {item.check_id}: {item.message}")
            lines.extend(f"  - {detail}" for detail in item.details)
    else:
        lines.extend(["", "需要你确认：", "- 没有发现需要你确认的阻塞。"])
    return "\n".join(lines)


def render_markdown(results: list[ContractResult]) -> str:
    failed = [item for item in results if item.status != "ok"]
    lines = [
        "# Loop Engineering Contract Smoke",
        "",
        f"- Status: `{'fail' if failed else 'ok'}`",
        f"- Checks: `{len(results)}`",
        f"- Failed: `{len(failed)}`",
        "",
        "## Results",
    ]
    for item in results:
        lines.extend(
            [
                "",
                f"### {item.check_id}",
                "",
                f"- Status: `{item.status}`",
                f"- Message: {item.message}",
            ]
        )
        if item.details:
            lines.append("- Details:")
            lines.extend(f"  - {detail}" for detail in item.details)
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    args = parser.parse_args(argv)

    results = all_checks()
    if args.format == "json":
        print(render_json(results))
    elif args.format == "user":
        print(render_user(results))
    else:
        print(render_markdown(results))
    return 1 if any(item.status != "ok" for item in results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
