#!/usr/bin/env python3
"""Plan or advance one safe Loop Engineering iteration from repo-native task evidence.

The planner is read-only: it chooses the next task candidate from the generated
dashboard evidence and explains what Codex can do next. The controlled runner
can execute only allowlisted local verification commands when explicitly passed
`--execute`; it does not activate a boundary, edit files, connect to services,
touch databases, or execute code workflow actions.

The advance executor adds a small deterministic state machine on top of the
planner. It explains which stage action is allowed next and can run only local
guard / verification commands for stages that are safe to automate. V7 adds an
explicit, evidence-backed write-back option; it remains off by default and
never treats ambiguous chat confirmation as production, database, destructive,
or git workflow authorization. V8 adds subagent timeout resilience: every
recommended subagent gets deadline, checkpoint, scope budget, retry, and
timeout evidence rules so main agent never has to wait indefinitely or pretend
an unreturned review passed. V9 adds a dedicated eng-review decisioner and
evidence checker: Codex records engineering choices it owns, keeps user
questions limited to business choices or high-risk authorization, and flags
eng-review evidence that asks the user to choose test commands, code structure,
subagent roles, gate recovery order, or implementation strategy. V10 adds a
stage write-back closure command: main agent can explicitly write the current
active stage back to the boundary after repo-native evidence exists, while
dry-run, non-active tasks, missing evidence, and cross-stage jumps remain
refused. V11 adds a deterministic subagent orchestration report: Codex can
plan explorer / reviewer / worker / QA delegation, timeout contracts, and
repo-native evidence collection without turning the helper into a background
agent scheduler. V12 adds a deterministic test-repair loop report: Codex can
run or preview allowlisted verification, classify failures, explain whether the
main agent can repair locally, prescribe reruns, and enforce QA evidence rules
without letting the helper edit code or pretend failed verification passed.
V13 hardens chat authorization recognition: continuation, ambiguous
confirmation, git workflow, production, database / real-data, destructive, and
forbidden scopes are classified with explicit scope, confidence and matched
marker evidence so Codex can keep doing local work without treating vague chat
as high-risk authorization.
V14 adds an end-to-end chat-first loop smoke report: a deterministic scenario
walks natural-language goal intake through requirement, review, freeze,
engineering review, spec readiness, implementation, QA evidence and final idle
without writing task evidence, launching subagents, running git workflow, or
touching production / DB / real data.
V15 connects the real nontechnical natural-language entry helpers into Loop
runtime smoke: the report runs fixed read-only dry-runs of nontechnical
next-step routing and formal kickoff preview, checks that the kickoff is
ready-to-write but not written or activated, and keeps production / DB / git
workflow actions blocked.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from gstack_dashboard import dashboard_payload


REPO_ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = "11"
PLANNER_VERSION = "loop-v15-natural-language-runtime"
RUNNER_VERSION = "controlled-local-runner-v3"
ADVANCE_EXECUTOR_VERSION = "stage-advance-v2"
ENG_REVIEW_DECISIONER_VERSION = "eng-review-decisioner-v1"
STAGE_WRITE_BACK_CLOSURE_VERSION = "stage-write-back-closure-v1"
SUBAGENT_ORCHESTRATION_VERSION = "subagent-orchestration-v1"
TEST_REPAIR_LOOP_RUNTIME_VERSION = "test-repair-loop-v1"
CHAT_AUTHORIZATION_RUNTIME_VERSION = "chat-authorization-v2"
CHAT_FIRST_LOOP_SMOKE_VERSION = "chat-first-loop-smoke-v1"
NATURAL_LANGUAGE_LOOP_SMOKE_VERSION = "natural-language-loop-smoke-v1"
SAFE_COMMANDS: dict[str, tuple[str, ...]] = {
    "python3 -m py_compile .gstack/scripts/gstack_loop.py": (
        "python3",
        "-m",
        "py_compile",
        ".gstack/scripts/gstack_loop.py",
    ),
    "python3 -m py_compile .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py": (
        "python3",
        "-m",
        "py_compile",
        ".gstack/scripts/gstack_loop.py",
        ".gstack/scripts/gstack_loop_contract_smoke.py",
    ),
    "git diff --check": (
        "git",
        "diff",
        "--check",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format user": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "user",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query loop-engineering-v5": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
        "--query",
        "loop-engineering-v5",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query loop-engineering-v5": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "user",
        "--query",
        "loop-engineering-v5",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query loop-engineering-v6": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
        "--query",
        "loop-engineering-v6",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query loop-engineering-v7": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
        "--query",
        "loop-engineering-v7",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query loop-engineering-v7": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "user",
        "--query",
        "loop-engineering-v7",
    ),
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 我确认 --format json": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "authorize",
        "--raw",
        "我确认",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 提交并推送 --format json": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "authorize",
        "--raw",
        "提交并推送",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop.py --format markdown": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "--format",
        "markdown",
    ),
    "python3 .gstack/scripts/gstack_loop.py run --dry-run --format json": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "run",
        "--dry-run",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop.py advance --dry-run --format json --query loop-engineering-v5": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "advance",
        "--dry-run",
        "--format",
        "json",
        "--query",
        "loop-engineering-v5",
    ),
    "python3 .gstack/scripts/gstack_loop.py advance --dry-run --format json --query loop-engineering-v6": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "advance",
        "--dry-run",
        "--format",
        "json",
        "--query",
        "loop-engineering-v6",
    ),
    "python3 .gstack/scripts/gstack_loop.py advance --dry-run --format json --query loop-engineering-v7": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "advance",
        "--dry-run",
        "--format",
        "json",
        "--query",
        "loop-engineering-v7",
    ),
    "python3 .gstack/scripts/gstack_loop.py run --dry-run --format json --query loop-engineering-v5": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "run",
        "--dry-run",
        "--format",
        "json",
        "--query",
        "loop-engineering-v5",
    ),
    "python3 .gstack/scripts/gstack_loop.py run --dry-run --format json --query loop-engineering-v6": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "run",
        "--dry-run",
        "--format",
        "json",
        "--query",
        "loop-engineering-v6",
    ),
    "python3 .gstack/scripts/gstack_loop.py run --dry-run --format json --query loop-engineering-v7": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "run",
        "--dry-run",
        "--format",
        "json",
        "--query",
        "loop-engineering-v7",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query subagent-timeout-resilience": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
        "--query",
        "subagent-timeout-resilience",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query subagent-timeout-resilience": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "user",
        "--query",
        "subagent-timeout-resilience",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query eng-review-auto-decisioner": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
        "--query",
        "eng-review-auto-decisioner",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query eng-review-auto-decisioner": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "user",
        "--query",
        "eng-review-auto-decisioner",
    ),
    "python3 .gstack/scripts/gstack_loop.py eng-review --format json --query eng-review-auto-decisioner": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "eng-review",
        "--format",
        "json",
        "--query",
        "eng-review-auto-decisioner",
    ),
    "python3 .gstack/scripts/gstack_loop.py eng-review --format user --query eng-review-auto-decisioner": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "eng-review",
        "--format",
        "user",
        "--query",
        "eng-review-auto-decisioner",
    ),
    "python3 .gstack/scripts/gstack_loop.py eng-review --format json --evidence .gstack/reviews/2026-06-15_eng-review-auto-decisioner-eng-review.md": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "eng-review",
        "--format",
        "json",
        "--evidence",
        ".gstack/reviews/2026-06-15_eng-review-auto-decisioner-eng-review.md",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query stage-write-back-closure": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
        "--query",
        "stage-write-back-closure",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query stage-write-back-closure": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "user",
        "--query",
        "stage-write-back-closure",
    ),
    "python3 .gstack/scripts/gstack_loop.py write-back --dry-run --format json --query stage-write-back-closure --evidence .gstack/scripts/gstack_loop.py": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "write-back",
        "--dry-run",
        "--format",
        "json",
        "--query",
        "stage-write-back-closure",
        "--evidence",
        ".gstack/scripts/gstack_loop.py",
    ),
    "python3 .gstack/scripts/gstack_loop.py write-back --dry-run --format user --query stage-write-back-closure --evidence .gstack/scripts/gstack_loop.py": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "write-back",
        "--dry-run",
        "--format",
        "user",
        "--query",
        "stage-write-back-closure",
        "--evidence",
        ".gstack/scripts/gstack_loop.py",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query subagent-auto-orchestration": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
        "--query",
        "subagent-auto-orchestration",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query subagent-auto-orchestration": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "user",
        "--query",
        "subagent-auto-orchestration",
    ),
    "python3 .gstack/scripts/gstack_loop.py subagents --format json --query subagent-auto-orchestration": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "subagents",
        "--format",
        "json",
        "--query",
        "subagent-auto-orchestration",
    ),
    "python3 .gstack/scripts/gstack_loop.py subagents --format user --query subagent-auto-orchestration": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "subagents",
        "--format",
        "user",
        "--query",
        "subagent-auto-orchestration",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query test-repair-loop-runtime": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
        "--query",
        "test-repair-loop-runtime",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query test-repair-loop-runtime": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "user",
        "--query",
        "test-repair-loop-runtime",
    ),
    "python3 .gstack/scripts/gstack_loop.py repair-loop --dry-run --format json --query test-repair-loop-runtime": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "repair-loop",
        "--dry-run",
        "--format",
        "json",
        "--query",
        "test-repair-loop-runtime",
    ),
    "python3 .gstack/scripts/gstack_loop.py repair-loop --dry-run --format user --query test-repair-loop-runtime": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "repair-loop",
        "--dry-run",
        "--format",
        "user",
        "--query",
        "test-repair-loop-runtime",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query chat-authorization-runtime": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
        "--query",
        "chat-authorization-runtime",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query chat-authorization-runtime": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "user",
        "--query",
        "chat-authorization-runtime",
    ),
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 继续做 --format json": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "authorize",
        "--raw",
        "继续做",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 不要提交也不要推送 --format json": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "authorize",
        "--raw",
        "不要提交也不要推送",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 发布到生产 --format json": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "authorize",
        "--raw",
        "发布到生产",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 不改数据库 --format json": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "authorize",
        "--raw",
        "不改数据库",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop.py authorize --raw 撤销刚才的改动 --format json": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "authorize",
        "--raw",
        "撤销刚才的改动",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop.py chat-smoke --format json": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "chat-smoke",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop.py chat-smoke --format user": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "chat-smoke",
        "--format",
        "user",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query chat-first-loop-smoke": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
        "--query",
        "chat-first-loop-smoke",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query chat-first-loop-smoke": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "user",
        "--query",
        "chat-first-loop-smoke",
    ),
    "python3 .gstack/scripts/gstack_loop.py nl-smoke --format json": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "nl-smoke",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop.py nl-smoke --format user": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "nl-smoke",
        "--format",
        "user",
    ),
    "python3 .gstack/scripts/natural_language_dev_smoke.py --format json": (
        "python3",
        ".gstack/scripts/natural_language_dev_smoke.py",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/natural_language_dev_smoke.py --format user": (
        "python3",
        ".gstack/scripts/natural_language_dev_smoke.py",
        "--format",
        "user",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format json --query natural-language-loop-runtime": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "json",
        "--query",
        "natural-language-loop-runtime",
    ),
    "python3 .gstack/scripts/gstack_loop.py plan --format user --query natural-language-loop-runtime": (
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "plan",
        "--format",
        "user",
        "--query",
        "natural-language-loop-runtime",
    ),
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json": (
        "python3",
        ".gstack/scripts/gstack_loop_contract_smoke.py",
        "--format",
        "json",
    ),
    "python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user": (
        "python3",
        ".gstack/scripts/gstack_loop_contract_smoke.py",
        "--format",
        "user",
    ),
    "python3 .gstack/scripts/natural_language_dev_smoke.py --format user": (
        "python3",
        ".gstack/scripts/natural_language_dev_smoke.py",
        "--format",
        "user",
    ),
    "python3 .gstack/scripts/spec_sync_guard.py": (
        "python3",
        ".gstack/scripts/spec_sync_guard.py",
    ),
    "python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD": (
        "python3",
        ".gstack/scripts/team_flow_guard.py",
        "--mode",
        "audit",
        "--base",
        "HEAD",
    ),
}


STAGE_ACTIONS = {
    "requirement-brief": "补齐任务目标、范围和最小验收标准。",
    "plan-ceo-review": "确认这件事值得做、范围不跑偏，再进入工程判断。",
    "requirement-freeze": "冻结本轮需求和不做范围，避免循环推进时扩大范围。",
    "plan-eng-review": "确认实现路径、风险和验证计划。",
    "domain-spec-readiness": "确认需要同步的真源文档，或写明本轮不需要改业务规格。",
    "implement": "在已声明的任务边界内完成实现和文档同步。",
    "qa": "运行验证并沉淀 QA evidence。",
    "complete": "任务已经完成，循环应选择下一条未完成任务。",
}


@dataclass(frozen=True)
class LoopCandidate:
    task: str
    boundary: str
    active: bool
    blocked: bool
    progress: str
    current_stage_key: str
    current_stage: str
    next_step: str
    selection_reason: str
    blocked_reasons: list[str]
    evidence_missing: list[str]


@dataclass(frozen=True)
class DecisionPolicy:
    user_decides: list[str]
    codex_decides: list[str]
    ask_user_style: str
    requirement_design_discussion: list[str]


@dataclass(frozen=True)
class SubagentRecommendation:
    mode: str
    recommended_now: bool
    reason: str
    candidate_subagents: list[dict[str, str]]
    skip_conditions: list[str]
    result_integration: list[str]


@dataclass(frozen=True)
class SubagentTimeoutPolicy:
    default_checkpoint_seconds: int
    default_deadline_seconds: int
    max_files_per_readonly_agent: int
    max_retry_attempts: int
    required_checkpoint_fields: list[str]
    result_schema_required_fields: list[str]
    timeout_classifications: list[str]
    timeout_recovery_steps: list[str]
    retry_scope_rules: list[str]
    evidence_rules: list[str]


@dataclass(frozen=True)
class TestingPolicy:
    auto_run: bool
    required_checks: list[str]
    repair_policy: list[str]
    qa_evidence: str
    ui_policy: str


@dataclass(frozen=True)
class ContinuationPolicy:
    can_auto_continue_until: str
    auto_recovery_actions: list[str]
    risk_authorizations_required: list[str]
    evidence_targets: list[str]


@dataclass(frozen=True)
class ReleasePolicy:
    commit_policy: str
    push_policy: str
    deploy_policy: str
    explicit_authorization_examples: list[str]


@dataclass(frozen=True)
class StageSkillRoute:
    stage_key: str
    stage_label: str
    intent: str
    default_skills: list[str]
    skill_ids: list[str]
    helper_scripts: list[str]
    tool_capabilities: list[str]
    codex_auto_decisions: list[str]
    ask_user_when: list[str]
    subagent_default: str
    evidence_targets: list[str]


@dataclass(frozen=True)
class ChatFirstProtocol:
    current_stage: str
    stage_status: str
    user_facing_status: str
    codex_will_do: list[str]
    user_must_choose: list[str]
    user_does_not_need_to_handle: list[str]
    validation_result_policy: list[str]
    write_back_policy: list[str]


@dataclass(frozen=True)
class EngineeringDecisionEvidence:
    status: str
    codex_owned_decisions: list[str]
    user_owned_decisions: list[str]
    anti_user_delegation_checks: list[str]
    evidence_targets: list[str]


@dataclass(frozen=True)
class EngReviewEvidenceCheck:
    evidence_path: str
    exists: bool
    status: str
    required_markers: list[str]
    found_required_markers: list[str]
    missing_required_markers: list[str]
    forbidden_user_delegations: list[str]
    forbidden_user_delegations_found: list[str]
    summary: str


@dataclass(frozen=True)
class EngReviewDecisioner:
    status: str
    decisioner_version: str
    trigger_stages: list[str]
    codex_owned_decisions: list[str]
    user_owned_decisions: list[str]
    forbidden_user_delegations: list[str]
    required_evidence_markers: list[str]
    evidence_targets: list[str]
    generation_policy: list[str]
    check_policy: list[str]
    evidence_check: EngReviewEvidenceCheck


@dataclass(frozen=True)
class TestRepairLoopPolicy:
    enabled: bool
    max_local_repair_attempts: int
    loop_steps: list[str]
    stop_and_ask_when: list[str]
    qa_evidence_rule: str


@dataclass(frozen=True)
class StageWriteBackPolicy:
    default_enabled: bool
    allowed_when: list[str]
    refused_when: list[str]
    evidence_required: str
    boundary_update_scope: list[str]


@dataclass(frozen=True)
class StageWriteBackClosurePolicy:
    status: str
    writer_version: str
    current_stage_key: str
    current_stage_label: str
    suggested_evidence: str
    suggested_command: str
    stage_evidence_rules: list[dict[str, str]]
    allowed_when: list[str]
    refused_when: list[str]
    non_actions: list[str]


@dataclass(frozen=True)
class SubagentOrchestrationPolicy:
    status: str
    orchestrator_version: str
    current_stage_key: str
    current_stage_label: str
    mode: str
    recommended_now: bool
    decision_reason: str
    planned_subagents: list[dict[str, str]]
    launch_order: list[str]
    result_collection: list[str]
    boundary_update_policy: list[str]
    skip_conditions: list[str]
    timeout_contract: dict[str, str]
    allowed_when: list[str]
    refused_when: list[str]
    non_actions: list[str]


@dataclass(frozen=True)
class ChatAuthorizationDecision:
    classifier_version: str
    raw: str
    category: str
    risk_level: str
    authorization_scope: str
    confirmation_strength: str
    authorization_granted: bool
    requires_explicit_authorization: bool
    can_continue_locally: bool
    matched_markers: list[str]
    required_explicit_phrase: str
    reason: str
    allowed_actions: list[str]
    blocked_actions: list[str]


@dataclass(frozen=True)
class ChatFirstLoopSmokeStep:
    stage_key: str
    stage_label: str
    status: str
    progress: str
    evidence_target: str
    protocol_status: str
    codex_will_do: list[str]
    user_must_choose: list[str]
    user_does_not_need_to_handle: list[str]
    validation_result_policy: list[str]
    write_back_policy: list[str]
    eng_review_status: str
    subagent_mode: str
    subagent_recommended_now: bool
    test_repair_enabled: bool
    stage_write_back_status: str
    checks: list[str]


@dataclass(frozen=True)
class ChatFirstLoopSmokeReport:
    generated_at: str
    schema_version: str
    smoke_version: str
    planner_version: str
    status: str
    mode: str
    raw_goal: str
    stage_count: int
    covered_stage_keys: list[str]
    missing_stage_keys: list[str]
    boundary_evidence: str
    requirement_evidence: str
    review_evidence: str
    qa_evidence: str
    doc_sync_evidence: list[str]
    local_continuation: ChatAuthorizationDecision
    ambiguous_confirmation: ChatAuthorizationDecision
    explicit_git_authorization: ChatAuthorizationDecision
    forbidden_git_scope: ChatAuthorizationDecision
    final_protocol: ChatFirstProtocol
    final_state: str
    steps: list[ChatFirstLoopSmokeStep]
    stop_conditions: list[str]
    non_actions: list[str]
    source_note: str


@dataclass(frozen=True)
class NaturalLanguageHelperRun:
    name: str
    command: list[str]
    returncode: int
    status: str
    stdout_tail: str
    stderr_tail: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class NaturalLanguageLoopSmokeReport:
    generated_at: str
    schema_version: str
    smoke_version: str
    planner_version: str
    status: str
    mode: str
    raw_request: str
    audience: str
    success: str
    non_goal: str
    topic: str
    next_step: NaturalLanguageHelperRun
    formal_kickoff: NaturalLanguageHelperRun
    next_step_intent: str
    next_step_helper_entry: str
    next_step_needs_user_confirmation: bool
    formal_status: str
    formal_can_write: bool
    formal_written: bool
    formal_activated: bool
    formal_ai_reviewed: bool
    recommended_lane: str
    risk_confirmation_status: str
    acceptance_checks: list[str]
    formal_paths: dict[str, str]
    readiness_checks: list[str]
    failure_reasons: list[str]
    final_state: str
    stop_conditions: list[str]
    non_actions: list[str]
    source_note: str


@dataclass(frozen=True)
class LoopPlan:
    generated_at: str
    schema_version: str
    planner_version: str
    status: str
    mode: str
    candidate_count: int
    open_tasks: int
    total_tasks: int
    selected: LoopCandidate | None
    can_auto_continue: bool
    codex_next_actions: list[str]
    chat_first_protocol: ChatFirstProtocol
    decision_policy: DecisionPolicy
    engineering_decision_evidence: EngineeringDecisionEvidence
    eng_review_decisioner: EngReviewDecisioner
    continuation_policy: ContinuationPolicy
    current_stage_skill_route: StageSkillRoute | None
    stage_skill_routes: list[StageSkillRoute]
    subagent_recommendation: SubagentRecommendation
    subagent_timeout_policy: SubagentTimeoutPolicy
    subagent_orchestration: SubagentOrchestrationPolicy
    testing_policy: TestingPolicy
    test_repair_loop: TestRepairLoopPolicy
    stage_write_back_policy: StageWriteBackPolicy
    stage_write_back_closure: StageWriteBackClosurePolicy
    release_policy: ReleasePolicy
    stop_conditions: list[str]
    needs_user_confirmation: list[str]
    non_actions: list[str]
    source_note: str


@dataclass(frozen=True)
class LoopRunCommand:
    command: str
    status: str
    allowed: bool
    skipped_reason: str
    returncode: int | None
    duration_seconds: float | None
    stdout_tail: str
    stderr_tail: str


@dataclass(frozen=True)
class StageWriteBackResult:
    requested: bool
    performed: bool
    status: str
    stage_key: str
    evidence: str
    boundary: str
    reason: str
    updated_fields: list[str]


@dataclass(frozen=True)
class LoopRunReport:
    generated_at: str
    schema_version: str
    executor_version: str
    mode: str
    executor_level: str
    dry_run: bool
    execute_requested: bool
    status: str
    selected: LoopCandidate | None
    candidate_status: str
    stop_reason: str
    requires_user_confirmation: list[str]
    command_source: str
    command_count: int
    passed_count: int
    failed_count: int
    skipped_count: int
    commands: list[LoopRunCommand]
    write_back_result: StageWriteBackResult
    stop_conditions: list[str]
    non_actions: list[str]
    source_note: str


@dataclass(frozen=True)
class TestRepairFailureAnalysis:
    status: str
    failed_command: str
    returncode: int | None
    failure_kind: str
    repairability: str
    summary: str
    stdout_tail: str
    stderr_tail: str
    suggested_next_action: str
    requires_user_confirmation: list[str]
    evidence_policy: list[str]


@dataclass(frozen=True)
class TestRepairLoopReport:
    generated_at: str
    schema_version: str
    loop_version: str
    mode: str
    dry_run: bool
    execute_requested: bool
    max_local_repair_attempts: int
    status: str
    selected: LoopCandidate | None
    candidate_status: str
    command_source: str
    command_count: int
    passed_count: int
    failed_count: int
    skipped_count: int
    commands: list[LoopRunCommand]
    failure_analysis: TestRepairFailureAnalysis
    repair_plan: list[str]
    rerun_policy: list[str]
    qa_evidence_policy: list[str]
    stop_conditions: list[str]
    non_actions: list[str]
    source_note: str


@dataclass(frozen=True)
class StageExecutionDecision:
    stage_key: str
    stage_label: str
    action: str
    can_execute: bool
    execution_strategy: str
    next_stage_on_success: str
    requires_main_agent: bool
    requires_user_confirmation: bool
    stop_reason: str
    write_back_required: bool
    evidence_targets: list[str]
    instructions: list[str]


@dataclass(frozen=True)
class LoopAdvanceReport:
    generated_at: str
    schema_version: str
    executor_version: str
    mode: str
    dry_run: bool
    execute_requested: bool
    status: str
    selected: LoopCandidate | None
    candidate_status: str
    stage_decision: StageExecutionDecision | None
    command_source: str
    command_count: int
    passed_count: int
    failed_count: int
    skipped_count: int
    commands: list[LoopRunCommand]
    write_back_result: StageWriteBackResult
    stop_conditions: list[str]
    non_actions: list[str]
    source_note: str


@dataclass(frozen=True)
class EngReviewDecisionReport:
    generated_at: str
    schema_version: str
    decisioner_version: str
    mode: str
    status: str
    selected: LoopCandidate | None
    candidate_status: str
    eng_review_decisioner: EngReviewDecisioner
    stop_conditions: list[str]
    non_actions: list[str]
    source_note: str


@dataclass(frozen=True)
class StageWriteBackReport:
    generated_at: str
    schema_version: str
    writer_version: str
    mode: str
    dry_run: bool
    execute_requested: bool
    status: str
    selected: LoopCandidate | None
    candidate_status: str
    requested_stage_key: str
    current_stage_key: str
    next_stage_on_success: str
    write_back_result: StageWriteBackResult
    closure_policy: StageWriteBackClosurePolicy
    stop_conditions: list[str]
    non_actions: list[str]
    source_note: str


@dataclass(frozen=True)
class SubagentOrchestrationReport:
    generated_at: str
    schema_version: str
    orchestrator_version: str
    mode: str
    status: str
    selected: LoopCandidate | None
    candidate_status: str
    subagent_orchestration: SubagentOrchestrationPolicy
    stop_conditions: list[str]
    non_actions: list[str]
    source_note: str


STAGE_SKILL_ROUTES: tuple[StageSkillRoute, ...] = (
    StageSkillRoute(
        stage_key="requirement-brief",
        stage_label="需求说明",
        intent="把自然语言目标转成 requirement、范围、不做事项、验收方式和风险边界。",
        default_skills=["kk-natural-language-dev", "kk-task-kickoff"],
        skill_ids=["kk-natural-language-dev", "kk-task-kickoff"],
        helper_scripts=["nontechnical_intake.py", "nontechnical_next_step.py", "autopilot_bootstrap.py"],
        tool_capabilities=[],
        codex_auto_decisions=[
            "选择 fast-lane / standard / discovery 的内部路线。",
            "选择 requirement 模板和 repo-native evidence 落点。",
            "把用户语言转成 boundary、Required Gates 和 Spec Sync Plan 草案。",
        ],
        ask_user_when=[
            "目标用户、成功样子或不做范围不清楚。",
            "多个产品方向都合理。",
            "涉及真实数据、生产、数据库结构、破坏性动作或代码提交流程授权。",
        ],
        subagent_default="信息源多或范围大时使用 read-only requirement reviewer；小而明确的 fast-lane 可不使用。",
        evidence_targets=[".gstack/requirements/", ".gstack/task-boundaries/"],
    ),
    StageSkillRoute(
        stage_key="plan-ceo-review",
        stage_label="产品评审",
        intent="确认需求值得做、范围不跑偏、用户可见变化和验收方式清楚。",
        default_skills=["plan-ceo-review", "plan-design-review", "kk-task-kickoff"],
        skill_ids=["plan-ceo-review", "plan-design-review", "kk-task-kickoff"],
        helper_scripts=[],
        tool_capabilities=[],
        codex_auto_decisions=[
            "判断是否需要设计视角复核。",
            "收敛不做范围和阶段验收方式。",
            "把可本地证明的 review 结论写入 repo evidence。",
        ],
        ask_user_when=[
            "业务优先级、用户可见结果或体验方向存在多解。",
            "需要确认是否放弃某个用户可见能力。",
        ],
        subagent_default="有产品/设计多视角风险时使用 read-only reviewer。",
        evidence_targets=[".gstack/reviews/", ".gstack/requirements/"],
    ),
    StageSkillRoute(
        stage_key="requirement-freeze",
        stage_label="需求 / 原型冻结",
        intent="冻结本轮要做和明确不做，避免进入施工后扩大范围。",
        default_skills=["kk-task-kickoff", "plan-ceo-review"],
        skill_ids=["kk-task-kickoff", "plan-ceo-review"],
        helper_scripts=["autopilot_bootstrap.py"],
        tool_capabilities=[],
        codex_auto_decisions=[
            "选择 freeze evidence 的具体模板和落点。",
            "把无争议的边界、验收和风险控制写入 requirement freeze。",
        ],
        ask_user_when=[
            "冻结范围会改变业务目标或用户可见结果。",
            "需要批准延期、删减或新增需求切片。",
        ],
        subagent_default="通常不需要；范围大时使用 read-only reviewer 复核冻结边界。",
        evidence_targets=[".gstack/requirements/"],
    ),
    StageSkillRoute(
        stage_key="plan-eng-review",
        stage_label="工程评审",
        intent="确认实现路线、数据/接口风险、测试策略、subagent 分工和门禁恢复方式。",
        default_skills=["plan-eng-review", "kk-subagent-orchestrator", "kk-data-kickoff（仅数据/接口触发）", "kk-doc-sync"],
        skill_ids=["plan-eng-review", "kk-subagent-orchestrator", "kk-data-kickoff", "kk-doc-sync"],
        helper_scripts=["gstack_doctor.py"],
        tool_capabilities=[],
        codex_auto_decisions=[
            "选择代码结构、实现顺序、测试组合和门禁恢复路径。",
            "选择是否启动 explorer / reviewer / worker subagent。",
            "判断 data-access、prototype-logic-extraction、doc-sync 是否需要进入 planned。",
        ],
        ask_user_when=[
            "工程路线会改变业务口径或用户可见行为。",
            "需要真实数据、生产权限、数据库结构变更或代码提交流程授权。",
        ],
        subagent_default="默认考虑 read-only explorer / reviewer；worker 仅在写范围可清楚切开时使用。",
        evidence_targets=[".gstack/reviews/", ".gstack/task-boundaries/"],
    ),
    StageSkillRoute(
        stage_key="domain-spec-readiness",
        stage_label="规格就绪",
        intent="确认产品语义、接口、数据、测试或框架真源已经同步，或写明不需要变更的原因。",
        default_skills=["kk-task-kickoff", "kk-doc-sync", "kk-doc-backfill（仅文档滞后触发）", "kk-data-kickoff（仅数据/接口触发）"],
        skill_ids=["kk-task-kickoff", "kk-doc-sync", "kk-doc-backfill", "kk-data-kickoff"],
        helper_scripts=["spec_sync_guard.py"],
        tool_capabilities=[],
        codex_auto_decisions=[
            "选择需要同步的 spec / knowledge / workflow 文档。",
            "判断 no-spec-change 是否可由本地证据证明。",
            "补齐可证明的 domain readiness evidence。",
        ],
        ask_user_when=[
            "spec 语义需要业务负责人确认。",
            "数据口径、字段归属或接口契约无法从 repo 真源证明。",
        ],
        subagent_default="有多个 spec 或历史 evidence 需要并行读取时使用 read-only explorer。",
        evidence_targets=["stack/<project>/specs/", ".gstack/knowledge/", ".gstack/workflows/"],
    ),
    StageSkillRoute(
        stage_key="implement",
        stage_label="实现",
        intent="在已冻结 requirement 和 active boundary 内完成代码、脚本或文档施工。",
        default_skills=["kk-subagent-orchestrator", "kk-doc-sync"],
        skill_ids=["kk-subagent-orchestrator", "kk-doc-sync"],
        helper_scripts=[],
        tool_capabilities=["apply_patch", "local verification commands"],
        codex_auto_decisions=[
            "选择具体实现顺序、重构粒度、局部 helper 和代码 pattern。",
            "选择最小可验证实现切片。",
            "验证失败时先修复本地可证明的问题并重跑。",
        ],
        ask_user_when=[
            "实现需要扩大 allowed files 或改变业务语义。",
            "需要破坏性动作、真实数据、生产、数据库结构或代码提交流程授权。",
        ],
        subagent_default="默认至少考虑 read-only implementation reviewer；worker 只在前端/后端/测试/文档写范围互不重叠时使用。",
        evidence_targets=["changed files", ".gstack/reviews/", ".gstack/task-boundaries/"],
    ),
    StageSkillRoute(
        stage_key="qa",
        stage_label="验收",
        intent="运行本地验证、页面交互验收和 guard，并把结果写入 QA evidence。",
        default_skills=["qa", "qa-only", "browse", "design-review", "kk-doc-sync"],
        skill_ids=["qa", "qa-only", "design-review", "kk-doc-sync"],
        helper_scripts=["spec_sync_guard.py", "team_flow_guard.py", "natural_language_dev_smoke.py"],
        tool_capabilities=["Browser / Chrome / Playwright for UI-visible tasks"],
        codex_auto_decisions=[
            "选择单测、构建、smoke、Browser / Chrome / Playwright 和 guard 组合。",
            "失败时先定位并修复本地可证明缺口。",
            "把验证结果写入 `.gstack/qa-reports/`。",
        ],
        ask_user_when=[
            "需要用户验收真实业务结果或外部账号权限。",
            "需要生产、真实数据、发布、回滚或代码提交流程授权。",
        ],
        subagent_default="默认考虑 read-only QA reviewer 复核覆盖面和残余风险。",
        evidence_targets=[".gstack/qa-reports/", ".gstack/task-boundaries/"],
    ),
    StageSkillRoute(
        stage_key="complete",
        stage_label="全部完成",
        intent="任务已完成；loop 应选择下一条未完成任务或进入 idle。",
        default_skills=["gstack_dashboard", "gstack_loop"],
        skill_ids=[],
        helper_scripts=["gstack_dashboard.py", "gstack_loop.py"],
        tool_capabilities=[],
        codex_auto_decisions=[
            "生成完成摘要和下一条候选任务计划。",
            "不自动进入提交、推送、合并请求或上线。",
        ],
        ask_user_when=[
            "用户要求代码提交流程或发布动作。",
            "用户要改变后续任务优先级。",
        ],
        subagent_default="通常不需要；大 diff 可使用 read-only release/doc reviewer。",
        evidence_targets=[".gstack/qa-reports/", ".gstack/reviews/"],
    ),
)

STAGE_SKILL_ROUTE_BY_KEY = {route.stage_key: route for route in STAGE_SKILL_ROUTES}
STAGE_ORDER = (
    "requirement-brief",
    "plan-ceo-review",
    "requirement-freeze",
    "plan-eng-review",
    "domain-spec-readiness",
    "implement",
    "qa",
    "complete",
)


def stage_skill_route_for(candidate: LoopCandidate | None) -> StageSkillRoute | None:
    if candidate is None:
        return None
    return STAGE_SKILL_ROUTE_BY_KEY.get(candidate.current_stage_key)


def next_stage_after(stage_key: str) -> str:
    try:
        index = STAGE_ORDER.index(stage_key)
    except ValueError:
        return "unknown"
    if index + 1 >= len(STAGE_ORDER):
        return "complete"
    return STAGE_ORDER[index + 1]


def stage_execution_decision_for(
    candidate: LoopCandidate | None,
    route: StageSkillRoute | None,
) -> StageExecutionDecision | None:
    if candidate is None:
        return StageExecutionDecision(
            stage_key="idle",
            stage_label="空队列",
            action="idle",
            can_execute=False,
            execution_strategy="none",
            next_stage_on_success="idle",
            requires_main_agent=False,
            requires_user_confirmation=False,
            stop_reason="no-candidate",
            write_back_required=False,
            evidence_targets=[],
            instructions=["当前没有可推进任务；如需继续，需要先创建新的 requirement / boundary。"],
        )

    stage_key = candidate.current_stage_key or "unknown"
    stage_label = route.stage_label if route else candidate.current_stage
    evidence_targets = route.evidence_targets if route else []
    if candidate.blocked:
        return StageExecutionDecision(
            stage_key=stage_key,
            stage_label=stage_label,
            action="blocked-stop",
            can_execute=False,
            execution_strategy="stop",
            next_stage_on_success=stage_key,
            requires_main_agent=True,
            requires_user_confirmation=True,
            stop_reason="blocked",
            write_back_required=False,
            evidence_targets=evidence_targets,
            instructions=["先读取 blocked reason；只有本地证据可修复时才由 Codex 自行恢复，否则必须问用户。"],
        )
    if candidate.evidence_missing:
        return StageExecutionDecision(
            stage_key=stage_key,
            stage_label=stage_label,
            action="repair-evidence",
            can_execute=False,
            execution_strategy="main-agent",
            next_stage_on_success=stage_key,
            requires_main_agent=True,
            requires_user_confirmation=False,
            stop_reason="evidence-missing",
            write_back_required=True,
            evidence_targets=evidence_targets,
            instructions=["修正缺失或过期的 evidence 链接，再重新生成 loop plan。"],
        )
    if not candidate.active:
        return StageExecutionDecision(
            stage_key=stage_key,
            stage_label=stage_label,
            action="activate-local-boundary",
            can_execute=False,
            execution_strategy="main-agent-local-state",
            next_stage_on_success=stage_key,
            requires_main_agent=True,
            requires_user_confirmation=False,
            stop_reason="not-active",
            write_back_required=False,
            evidence_targets=[candidate.boundary],
            instructions=[
                "由 Codex 设置本机 active boundary；这是 gitignored 本地状态，不写入共享 CURRENT.md。",
                f"维护兜底命令：bash .gstack/scripts/use_boundary.sh {candidate.boundary}",
            ],
        )
    if stage_key in {"requirement-brief", "plan-ceo-review", "requirement-freeze"}:
        return StageExecutionDecision(
            stage_key=stage_key,
            stage_label=stage_label,
            action="requirement-design-main-agent",
            can_execute=False,
            execution_strategy="main-agent-dialogue",
            next_stage_on_success=next_stage_after(stage_key),
            requires_main_agent=True,
            requires_user_confirmation=False,
            stop_reason="main-agent-required",
            write_back_required=True,
            evidence_targets=evidence_targets,
            instructions=[
                "按 gstack 范式磨清需求、设计、验收和不做范围。",
                "只有业务或设计多解时才给用户 2-3 个选择；不要把工程施工题交给用户。",
            ],
        )
    if stage_key == "plan-eng-review":
        return StageExecutionDecision(
            stage_key=stage_key,
            stage_label=stage_label,
            action="engineering-review-main-agent",
            can_execute=False,
            execution_strategy="main-agent-review",
            next_stage_on_success="domain-spec-readiness",
            requires_main_agent=True,
            requires_user_confirmation=False,
            stop_reason="main-agent-required",
            write_back_required=True,
            evidence_targets=evidence_targets,
            instructions=[
                "由 Codex 选择工程方案、代码结构、测试组合和 subagent 策略。",
                "如果路线改变业务语义、真实数据、生产、数据库或代码提交流程，必须停下来问用户。",
            ],
        )
    if stage_key == "domain-spec-readiness":
        return StageExecutionDecision(
            stage_key=stage_key,
            stage_label=stage_label,
            action="run-spec-readiness-guard",
            can_execute=True,
            execution_strategy="allowlist-guard",
            next_stage_on_success="implement",
            requires_main_agent=True,
            requires_user_confirmation=False,
            stop_reason="",
            write_back_required=True,
            evidence_targets=evidence_targets,
            instructions=[
                "同步 Expected Spec Targets 或写明 no-spec-change reason。",
                "可运行 spec_sync_guard.py 验证当前 spec readiness；通过后仍由 main agent 更新 boundary 状态。",
            ],
        )
    if stage_key == "implement":
        return StageExecutionDecision(
            stage_key=stage_key,
            stage_label=stage_label,
            action="implementation-main-agent",
            can_execute=False,
            execution_strategy="main-agent-code-edit",
            next_stage_on_success="qa",
            requires_main_agent=True,
            requires_user_confirmation=False,
            stop_reason="main-agent-required",
            write_back_required=True,
            evidence_targets=evidence_targets,
            instructions=[
                "由 Codex 在 Allowed Files 内完成实现；执行器不会自己改代码。",
                "实现完成后自动进入验证，失败先本地修复并重跑。",
            ],
        )
    if stage_key == "qa":
        return StageExecutionDecision(
            stage_key=stage_key,
            stage_label=stage_label,
            action="run-boundary-verification",
            can_execute=True,
            execution_strategy="allowlist-boundary-verification",
            next_stage_on_success="complete",
            requires_main_agent=True,
            requires_user_confirmation=False,
            stop_reason="",
            write_back_required=True,
            evidence_targets=evidence_targets,
            instructions=[
                "复用受控 verification runner，只执行 active boundary Verification 中的 allowlist 命令。",
                "通过后由 main agent 写入 QA evidence 并更新 boundary；执行器不自动改任务状态。",
            ],
        )
    if stage_key == "complete":
        return StageExecutionDecision(
            stage_key=stage_key,
            stage_label=stage_label,
            action="complete",
            can_execute=False,
            execution_strategy="none",
            next_stage_on_success="complete",
            requires_main_agent=False,
            requires_user_confirmation=False,
            stop_reason="complete",
            write_back_required=False,
            evidence_targets=evidence_targets,
            instructions=["当前任务已完成；重新 plan 后再选择下一条未完成任务。"],
        )
    return StageExecutionDecision(
        stage_key=stage_key,
        stage_label=stage_label,
        action="unknown-stage-stop",
        can_execute=False,
        execution_strategy="stop",
        next_stage_on_success=stage_key,
        requires_main_agent=True,
        requires_user_confirmation=False,
        stop_reason="unknown-stage",
        write_back_required=False,
        evidence_targets=evidence_targets,
        instructions=["无法识别当前阶段；先修正 boundary 的 GStack Required Flow。"],
    )


def clean_task_name(raw: Any) -> str:
    name = str(raw or "未命名任务").strip()
    for prefix in ("Task Boundary:", "Task Boundary：", "task boundary:", "task boundary："):
        if name.startswith(prefix):
            name = name[len(prefix) :].strip()
    if name.lower().endswith(" boundary"):
        name = name[:-9].strip()
    return name or "未命名任务"


def build_candidate(item: dict[str, Any], reason: str) -> LoopCandidate:
    stage_key = str(item.get("current_step_key") or "")
    return LoopCandidate(
        task=clean_task_name(item.get("task")),
        boundary=str(item.get("boundary") or ""),
        active=bool(item.get("active")),
        blocked=bool(item.get("blocked")),
        progress=str(item.get("progress") or "0/7"),
        current_stage_key=stage_key,
        current_stage=str(item.get("current_step") or "未知阶段"),
        next_step=str(item.get("next_step_label") or item.get("current_step") or "下一步"),
        selection_reason=reason,
        blocked_reasons=[str(value) for value in item.get("blocked_reasons") or []],
        evidence_missing=[str(value) for value in item.get("evidence_missing") or []],
    )


def choose_candidate(tasks: list[dict[str, Any]]) -> LoopCandidate | None:
    for item in tasks:
        if item.get("active"):
            return build_candidate(item, "当前 active task 还未完成；Loop runtime 优先继续当前任务，避免频繁切换上下文。")
    for item in tasks:
        if not item.get("blocked"):
            return build_candidate(item, "当前没有未完成的 active task；Loop runtime 选择排序后的第一条未卡住任务。")
    if tasks:
        return build_candidate(tasks[0], "当前匹配任务都显示卡住；Loop runtime 只能选择最高优先级卡住项并进入停止条件。")
    return None


def non_actions() -> list[str]:
    return [
        "gstack_loop.py 本身不会修改业务代码或任务文档；它只输出下一轮执行策略。",
        "gstack_loop.py 不会运行实现、发布、回滚或提交流程；run / advance 只会在显式执行时运行 allowlist 本地 guard / verification。",
        "不会连接真实数据、生产环境、数据库或外部服务。",
        "不会创建共享 dashboard/status 聚合文件。",
        "不会把模糊确认当成生产、数据库、删除、回滚或代码提交流程授权。",
    ]


def high_risk_stop_conditions() -> list[str]:
    return [
        "遇到业务口径多解、真实数据权限、生产环境、数据库结构、破坏性命令、提交 / 推送代码 / 合并请求 / 上线等代码提交流程或发布动作时停止并请求明确授权。",
        "遇到 active boundary 缺失、必要 evidence 缺失或 guard 失败时，Codex 先修复本地可证明的问题；无法证明时停止。",
        "遇到任务卡住且原因需要外部系统、账号权限或业务负责人确认时停止。",
    ]


def decision_policy() -> DecisionPolicy:
    return DecisionPolicy(
        user_decides=[
            "需求目标、使用者、成功样子、业务口径、不做范围和验收标准。",
            "存在多个合理产品 / 设计方向时，从 Codex 给出的 2-3 个业务选项中选择。",
            "真实数据、生产环境、数据库结构、破坏性命令、提交、推送代码、合并请求、上线或回滚授权。",
        ],
        codex_decides=[
            "在已冻结 requirement 和 active boundary 内选择工程方案、代码结构、实现顺序和重构粒度。",
            "选择测试组合、验证命令、门禁恢复顺序和本地可证明的修复方式。",
            "决定是否启动 explorer / reviewer / QA subagent；worker 只在写范围能切开时使用。",
        ],
        ask_user_style="只把需求、设计、风险和授权做成用户选择；不把框架、库、代码结构、测试命令等工程施工题甩给用户。",
        requirement_design_discussion=[
            "需求和设计讨论必须遵循 gstack 范式：先磨清用户目标、业务边界、可见变化和验收方式，再进入施工。",
            "如果用户给的是宽泛目标，先拆成可交付切片和阶段验收；信息不足时最多问关键业务选择。",
            "需求冻结后，工程施工相关取舍默认由 Codex 在 boundary 内自主完成，并在 review / QA evidence 中解释结果。",
        ],
    )


def testing_policy_for(candidate: LoopCandidate | None) -> TestingPolicy:
    checks = [
        "实现后自动运行 active boundary 的 Verification 列表。",
        "收口前必须运行 `python3 .gstack/scripts/spec_sync_guard.py`。",
        "实现类 diff 运行 `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD` 或更严格门禁。",
        "脚本改动至少运行语法检查和关键格式 smoke；用户可见页面或可视化改动必须用浏览器自动化做交互验证。",
    ]
    if candidate and candidate.current_stage_key in {"implement", "qa"}:
        checks.insert(0, f"当前阶段是 {candidate.current_stage}，施工完成后立即进入自动验证，不等待用户选择测试方案。")
    return TestingPolicy(
        auto_run=True,
        required_checks=checks,
        repair_policy=[
            "验证失败时，Codex 先定位并修复本地可证明的问题，然后重跑相关检查。",
            "如果失败依赖外部账号、真实数据、生产权限或业务口径，停止并说明已尝试内容和缺口。",
            "不能为了过门禁编造 QA、业务确认或线上验证证据。",
        ],
        qa_evidence="验证结果必须沉淀到 `.gstack/qa-reports/` 或 active boundary 指向的 QA evidence。",
        ui_policy="页面或可视化任务不能只看字符串或静态文件，必须记录实际打开、操作、截图或 blocked / partial reason。",
    )


def engineering_decision_evidence_for(candidate: LoopCandidate | None) -> EngineeringDecisionEvidence:
    stage = candidate.current_stage_key if candidate else "idle"
    return EngineeringDecisionEvidence(
        status="active" if stage in {"plan-eng-review", "domain-spec-readiness", "implement", "qa"} else "available",
        codex_owned_decisions=[
            "工程路线、代码结构、实现顺序、重构粒度和 helper 边界。",
            "测试组合、验证命令、门禁恢复顺序和本地可证明修复。",
            "是否启动 read-only explorer / reviewer / QA subagent；worker 只在写范围可切开时使用。",
            "no-spec-change 是否可由 repo 证据证明，或应同步哪些 `.gstack` / stack 真源。",
        ],
        user_owned_decisions=[
            "业务目标、用户可见成功样子、业务口径、不做范围和验收标准。",
            "多个合理产品 / 设计方向的取舍。",
            "真实数据、生产、数据库、破坏性命令、git workflow、上线或回滚授权。",
        ],
        anti_user_delegation_checks=[
            "不得要求用户选择测试命令、代码结构、subagent 角色或门禁恢复顺序。",
            "ENG review evidence 必须记录 Codex 自行做出的工程取舍。",
            "如果用户被要求做技术选择，review 必须标记为风险并改为 Codex 推荐方案。",
        ],
        evidence_targets=[
            ".gstack/reviews/",
            ".gstack/task-boundaries/",
            ".gstack/qa-reports/",
            "active boundary 的 Spec Sync Plan",
        ],
    )


ENG_REVIEW_REQUIRED_MARKERS: tuple[str, ...] = (
    "AI 语义复核: yes",
    "## Codex 自主工程决策",
    "## 用户决策边界",
    "## 防技术甩锅检查",
    "## 验证计划",
)


ENG_REVIEW_FORBIDDEN_USER_DELEGATIONS: tuple[str, ...] = (
    "需要用户选择测试命令",
    "需要用户决定测试命令",
    "需要用户选择代码结构",
    "需要用户决定代码结构",
    "请用户选择技术方案",
    "请用户决定技术方案",
    "用户决定 subagent 角色",
    "用户选择 subagent 角色",
    "用户决定门禁恢复顺序",
    "用户选择门禁恢复顺序",
    "让用户选择测试命令",
    "让用户选择代码结构",
    "ask user to choose test commands",
    "ask user to choose code structure",
    "ask user to choose subagent roles",
    "ask user to choose gate recovery order",
)


def safe_repo_path(raw_path: str) -> tuple[Path | None, str]:
    raw_path = raw_path.strip()
    if not raw_path:
        return None, ""
    path = Path(raw_path)
    resolved = path.resolve() if path.is_absolute() else (REPO_ROOT / path).resolve()
    try:
        relative = resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return None, raw_path
    return resolved, relative


def boundary_stage_evidence_for(candidate: LoopCandidate | None, stage_key: str) -> str:
    path = boundary_path(candidate)
    if path is None or not path.is_file():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    in_stage = False
    for line in lines:
        stripped = line.strip()
        if stripped == f"- {stage_key}:":
            in_stage = True
            continue
        if in_stage and stripped.startswith("- ") and stripped.endswith(":"):
            return ""
        if in_stage and stripped.startswith("evidence:"):
            value = stripped.removeprefix("evidence:").strip()
            return value.strip("`").strip()
    return ""


def eng_review_evidence_target_for(candidate: LoopCandidate | None) -> str:
    boundary_evidence = boundary_stage_evidence_for(candidate, "plan-eng-review")
    if boundary_evidence:
        return boundary_evidence
    date_prefix = datetime.now(timezone.utc).date().isoformat()
    if candidate is None:
        return f".gstack/reviews/{date_prefix}_eng-review.md"
    slug = re.sub(r"[^a-z0-9]+", "-", candidate.task.lower()).strip("-")
    if not slug:
        slug = "task"
    return f".gstack/reviews/{date_prefix}_{slug}-eng-review.md"


def eng_review_evidence_check_for(evidence_path: str) -> EngReviewEvidenceCheck:
    required_markers = list(ENG_REVIEW_REQUIRED_MARKERS)
    forbidden_markers = list(ENG_REVIEW_FORBIDDEN_USER_DELEGATIONS)
    if not evidence_path:
        return EngReviewEvidenceCheck(
            evidence_path="",
            exists=False,
            status="not-checked",
            required_markers=required_markers,
            found_required_markers=[],
            missing_required_markers=required_markers,
            forbidden_user_delegations=forbidden_markers,
            forbidden_user_delegations_found=[],
            summary="未指定 eng-review evidence；只能生成决策器要求，不能检查已写 evidence。",
        )
    path, relative = safe_repo_path(evidence_path)
    if path is None:
        return EngReviewEvidenceCheck(
            evidence_path=evidence_path,
            exists=False,
            status="invalid-path",
            required_markers=required_markers,
            found_required_markers=[],
            missing_required_markers=required_markers,
            forbidden_user_delegations=forbidden_markers,
            forbidden_user_delegations_found=[],
            summary="evidence path 必须位于当前 repo 内。",
        )
    if not path.is_file():
        return EngReviewEvidenceCheck(
            evidence_path=relative,
            exists=False,
            status="missing",
            required_markers=required_markers,
            found_required_markers=[],
            missing_required_markers=required_markers,
            forbidden_user_delegations=forbidden_markers,
            forbidden_user_delegations_found=[],
            summary="eng-review evidence 文件不存在；需要先写入 repo-native review evidence。",
        )
    text = path.read_text(encoding="utf-8")
    lowered = text.lower()
    found_required = [marker for marker in required_markers if marker in text]
    missing_required = [marker for marker in required_markers if marker not in text]
    found_forbidden = [
        marker
        for marker in forbidden_markers
        if (marker in text or marker.lower() in lowered)
    ]
    if found_forbidden:
        status = "needs-rewrite"
        summary = "evidence 出现把工程选择交给用户的表述，需要改写为 Codex 推荐方案。"
    elif missing_required:
        status = "needs-evidence"
        summary = "evidence 缺少 eng-review 自动决策器要求的最低标记。"
    else:
        status = "pass"
        summary = "evidence 满足 Codex 工程自决、用户决策边界和防技术甩锅最低检查。"
    return EngReviewEvidenceCheck(
        evidence_path=relative,
        exists=True,
        status=status,
        required_markers=required_markers,
        found_required_markers=found_required,
        missing_required_markers=missing_required,
        forbidden_user_delegations=forbidden_markers,
        forbidden_user_delegations_found=found_forbidden,
        summary=summary,
    )


def eng_review_status_for(candidate: LoopCandidate | None, check: EngReviewEvidenceCheck) -> str:
    if candidate is None:
        return "idle"
    if candidate.blocked:
        return "blocked"
    if candidate.evidence_missing:
        return "evidence-repair"
    if not candidate.active:
        return "needs-activation"
    if check.status in {"needs-rewrite", "invalid-path"}:
        return "needs-rewrite"
    if candidate.current_stage_key == "plan-eng-review":
        return "ready-to-generate"
    if candidate.current_stage_key in {"domain-spec-readiness", "implement", "qa"}:
        return "active"
    return "available"


def eng_review_decisioner_for(
    candidate: LoopCandidate | None,
    *,
    evidence_path: str = "",
) -> EngReviewDecisioner:
    target = evidence_path
    if candidate is not None and not target:
        target = eng_review_evidence_target_for(candidate)
    check = eng_review_evidence_check_for(target)
    return EngReviewDecisioner(
        status=eng_review_status_for(candidate, check),
        decisioner_version=ENG_REVIEW_DECISIONER_VERSION,
        trigger_stages=[
            "plan-eng-review",
            "domain-spec-readiness",
            "implement",
            "qa",
        ],
        codex_owned_decisions=[
            "选择工程方案、代码结构、实现顺序、重构粒度和 helper 边界。",
            "选择测试组合、验证命令、门禁恢复顺序和本地可证明修复方式。",
            "判断 no-spec-change 是否可证明，或应同步哪些 `.gstack` / stack 真源文档。",
            "决定是否启动 explorer / reviewer / QA subagent，并声明 timeout / checkpoint / evidence 规则。",
            "把 ENG review 结论写成 Codex 推荐方案、备选方案、风险和验证计划。",
        ],
        user_owned_decisions=[
            "业务目标、业务口径、用户可见成功样子、不做范围和验收标准。",
            "多个合理产品 / 设计方向的取舍。",
            "真实数据、生产、数据库结构、破坏性命令、git workflow、上线或回滚授权。",
        ],
        forbidden_user_delegations=list(ENG_REVIEW_FORBIDDEN_USER_DELEGATIONS),
        required_evidence_markers=list(ENG_REVIEW_REQUIRED_MARKERS),
        evidence_targets=[
            ".gstack/reviews/<date>_<task>-eng-review.md",
            "active boundary 的 plan-eng-review evidence",
            "active boundary 的 Autonomy Plan / Subagent Plan / Spec Sync Plan",
            ".gstack/qa-reports/<date>_<task>-qa.md",
        ],
        generation_policy=[
            "plan-eng-review 阶段由 Codex 生成 ENG review evidence，不把工程路线、代码结构、测试命令或 subagent 角色做成用户选择题。",
            "如果工程路线影响业务语义、真实数据、生产、DB、破坏性动作或 git workflow，必须停下来请求明确业务选择或授权。",
            "review 必须写明 Codex 自主工程决策、用户决策边界、防技术甩锅检查和验证计划。",
        ],
        check_policy=[
            "缺少必需 marker 时标记为 `needs-evidence`。",
            "发现把测试命令、代码结构、subagent 角色、门禁恢复顺序或技术方案交给用户的短语时标记为 `needs-rewrite`。",
            "checker 只做最低确定性门槛；main agent 仍需对高风险授权和业务语义负责。",
        ],
        evidence_check=check,
    )


def test_repair_loop_policy_for(candidate: LoopCandidate | None) -> TestRepairLoopPolicy:
    return TestRepairLoopPolicy(
        enabled=candidate is not None and candidate.current_stage_key in {"implement", "qa"},
        max_local_repair_attempts=2,
        loop_steps=[
            "运行 active boundary Verification 或当前阶段 allowlist guard。",
            "若失败，读取失败命令、退出码和 stdout / stderr tail。",
            "判断失败是否可由本地代码、脚本、文档或测试 evidence 修复。",
            "在 Allowed Files 内修复后重跑相关检查。",
            "通过后写 QA evidence；仍失败或需要外部权限时停止并说明缺口。",
        ],
        stop_and_ask_when=[
            "失败依赖业务口径、真实数据、生产账号、DB 权限、外部服务或用户验收。",
            "修复需要扩大 active boundary allowed files。",
            "修复需要破坏性命令、git workflow、上线或回滚授权。",
        ],
        qa_evidence_rule="每次最终结论必须落 `.gstack/qa-reports/` 或 active boundary 指向的 QA evidence；不能只留在聊天里。",
    )


def stage_write_back_policy() -> StageWriteBackPolicy:
    return StageWriteBackPolicy(
        default_enabled=False,
        allowed_when=[
            "用户或 Codex 显式传入 --write-back。",
            "或显式运行 `gstack_loop.py write-back --execute`。",
            "当前任务是本机 active boundary。",
            "对应 stage 的命令已实际执行且报告状态为 passed。",
            "传入的 --write-back-evidence 指向 repo 内已存在文件或目录。",
        ],
        refused_when=[
            "dry-run 模式。",
            "没有 selected task、任务不是 active、任务 blocked 或 evidence missing。",
            "命令失败、被跳过、没有命令或未实际执行。",
            "`write-back` 请求的 stage 与 selected current stage 不一致。",
            "evidence path 缺失、不存在、越出 repo 或仍是占位符。",
        ],
        evidence_required="--write-back-evidence 或 write-back --evidence 必须是 repo-relative 且已存在的 evidence 文件或目录。",
        boundary_update_scope=[
            "只更新 active boundary 的 GStack Required Flow 当前 stage。",
            "只写 status: done、evidence 和可选 note。",
            "不更新共享 CURRENT.md、不提交、不推送、不发布。",
        ],
    )


def stage_evidence_rules() -> list[dict[str, str]]:
    return [
        {
            "stage_key": "requirement-brief",
            "evidence_target": ".gstack/requirements/",
            "done_when": "requirement brief 已写入 repo-native evidence。",
        },
        {
            "stage_key": "plan-ceo-review",
            "evidence_target": ".gstack/reviews/",
            "done_when": "CEO / product review 已写入 repo-native evidence。",
        },
        {
            "stage_key": "requirement-freeze",
            "evidence_target": ".gstack/requirements/",
            "done_when": "requirement freeze 或 prototype freeze 已写入 repo-native evidence。",
        },
        {
            "stage_key": "plan-eng-review",
            "evidence_target": ".gstack/reviews/",
            "done_when": "ENG review 已写明 Codex 自主工程决策、风险和验证计划。",
        },
        {
            "stage_key": "domain-spec-readiness",
            "evidence_target": "active boundary 的 Expected Spec Targets 或 no-spec-change reason",
            "done_when": "真源文档已同步，或已写明本轮不需要 stack domain spec 的可证明原因。",
        },
        {
            "stage_key": "implement",
            "evidence_target": "changed files / docs / scripts",
            "done_when": "实现或文档施工已完成，且仍在 Allowed Files 内。",
        },
        {
            "stage_key": "qa",
            "evidence_target": ".gstack/qa-reports/",
            "done_when": "QA report 已记录实际验证命令、结果和残余风险。",
        },
    ]


def suggested_evidence_for_stage(candidate: LoopCandidate | None) -> str:
    if candidate is None:
        return ""
    current = boundary_stage_evidence_for(candidate, candidate.current_stage_key)
    if current:
        return current
    for rule in stage_evidence_rules():
        if rule["stage_key"] == candidate.current_stage_key:
            return rule["evidence_target"]
    return ""


def write_back_evidence_argument(value: str) -> str:
    evidence = value.strip()
    if not evidence or "<" in evidence or ">" in evidence or " " in evidence:
        return "<repo-evidence-path>"
    if evidence.startswith((".gstack/", "stack/", "shared/")) or evidence.endswith(".md"):
        return evidence
    return "<repo-evidence-path>"


def stage_write_back_closure_for(candidate: LoopCandidate | None) -> StageWriteBackClosurePolicy:
    if candidate is None:
        status = "idle"
        current_stage_key = "none"
        current_stage_label = "空队列"
        suggested_evidence = ""
        suggested_command = "none"
    else:
        candidate_status, can_continue = status_for(candidate)
        status = candidate_status if not can_continue else "ready"
        current_stage_key = candidate.current_stage_key
        current_stage_label = candidate.current_stage
        suggested_evidence = suggested_evidence_for_stage(candidate)
        if current_stage_key in STAGE_ORDER and current_stage_key != "complete":
            evidence_arg = write_back_evidence_argument(suggested_evidence)
            suggested_command = (
                "python3 .gstack/scripts/gstack_loop.py write-back --execute "
                f"--evidence {evidence_arg}"
            )
        else:
            suggested_command = "none"
    return StageWriteBackClosurePolicy(
        status=status,
        writer_version=STAGE_WRITE_BACK_CLOSURE_VERSION,
        current_stage_key=current_stage_key,
        current_stage_label=current_stage_label,
        suggested_evidence=suggested_evidence,
        suggested_command=suggested_command,
        stage_evidence_rules=stage_evidence_rules(),
        allowed_when=[
            "显式运行 `gstack_loop.py write-back --execute`。",
            "selected task 是当前本机 active boundary。",
            "写回 stage 等于 selected task 的 current stage，不允许跳阶段。",
            "evidence path 位于 repo 内且已经存在。",
            "任务未 blocked、无 evidence_missing，且当前 stage 不是 complete。",
        ],
        refused_when=[
            "默认 dry-run。",
            "没有 selected task、任务不是 active、任务 blocked 或 evidence missing。",
            "缺少 evidence、evidence 不存在、越出 repo 或仍是占位符。",
            "传入的 --stage-key 与 selected current stage 不一致。",
            "当前 stage 是 complete、未知 stage 或 boundary 缺少 GStack Required Flow。",
        ],
        non_actions=[
            "write-back 不生成 requirement / review / QA 正文，只引用已存在 evidence。",
            "write-back 不运行测试、不执行实现、不提交、不推送、不上线、不操作生产或 DB。",
            "write-back 不修改共享 CURRENT.md，只修改 selected active boundary 当前阶段字段。",
        ],
    )


def continuation_policy_for(candidate: LoopCandidate | None) -> ContinuationPolicy:
    risk_authorizations = [
        "业务口径多解或用户可见设计目标不明确",
        "真实数据源、字段口径、权限或 owner 无法由 repo 证据证明",
        "生产部署、生产重启、线上数据修复、远端服务操作",
        "DB schema、migration、生产写入、破坏性 SQL 或真实数据变更",
        "删除、reset、revert、rollback、清理文件等破坏性动作",
        "创建 / 切换分支、提交、修改提交、变基、推送代码、拉取、合并、挑选提交、重置、创建合并请求",
        "上线、发布、回滚",
    ]
    auto_recovery = [
        "补齐 active boundary 中可由本地证据证明的 flow、Subagent Plan、Autonomy Plan 或 Required Gates。",
        "修正缺失或过期的 requirement / review / QA evidence 链接。",
        "运行本地 guard，按失败输出补文档、测试记录或 no-spec-change 原因。",
        "验证失败时先定位并修复本地代码、脚本、文档或测试缺口，再重跑相关检查。",
    ]
    if candidate is None:
        until = "idle"
        evidence = []
    else:
        evidence = [
            candidate.boundary,
            ".gstack/requirements/",
            ".gstack/reviews/",
            ".gstack/qa-reports/",
            "active boundary 的 Expected Spec Targets",
        ]
        if candidate.blocked:
            until = "blocked-hard-stop"
        elif candidate.evidence_missing:
            until = "evidence-repair"
        elif not candidate.active:
            until = "activation"
        elif candidate.current_stage_key in {"requirement-brief", "plan-ceo-review", "requirement-freeze"}:
            until = "requirement-freeze-or-next-business-choice"
        elif candidate.current_stage_key in {"plan-eng-review", "domain-spec-readiness"}:
            until = "implement-ready"
        elif candidate.current_stage_key == "implement":
            until = "qa"
        elif candidate.current_stage_key == "qa":
            until = "complete"
        else:
            until = "next-stage"
    return ContinuationPolicy(
        can_auto_continue_until=until,
        auto_recovery_actions=auto_recovery,
        risk_authorizations_required=risk_authorizations,
        evidence_targets=evidence,
    )


def release_policy() -> ReleasePolicy:
    return ReleasePolicy(
        commit_policy="提交、修改提交、压缩提交、挑选提交、变基、创建 / 切换分支，只在用户明确说出对应代码提交流程动作后执行。",
        push_policy="推送代码、拉取、合并、创建合并请求或变更远端跟踪关系，只在用户明确授权后执行。",
        deploy_policy="上线、发布、生产重启、生产回滚或线上数据修复，只在用户明确授权且边界写清后执行。",
        explicit_authorization_examples=[
            "提交",
            "提交并推送",
            "创建合并请求",
            "上线",
            "发布到生产",
            "回滚这次发布",
        ],
    )


def has_any(raw: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword.lower() in raw for keyword in keywords)


def has_negation(raw: str) -> bool:
    return has_any(
        raw,
        (
            "不要",
            "别",
            "不许",
            "禁止",
            "先不",
            "不用",
            "不执行",
            "不要执行",
            "别执行",
            "不要提交",
            "不要推送",
            "不提交",
            "不推送",
            "不改",
            "不要改",
            "别改",
            "不上线",
            "不发布",
        ),
    )


def matched_keywords(raw: str, keywords: tuple[str, ...]) -> list[str]:
    return [keyword for keyword in keywords if keyword.lower() in raw]


def chat_authorization_for(raw_text: str) -> ChatAuthorizationDecision:
    raw = raw_text.strip()
    normalized = raw.lower()
    negated = has_negation(normalized)
    high_risk_blocked = [
        "提交、推送、创建 PR、分支切换、merge、rebase、pull 等 git workflow。",
        "上线、发布、生产重启、生产回滚或线上数据修复。",
        "数据库结构、migration、生产写入、真实数据写入或破坏性 SQL。",
        "删除、reset、回滚、清理文件等破坏性动作。",
    ]

    def decision(
        *,
        category: str,
        risk_level: str,
        authorization_scope: str,
        confirmation_strength: str,
        authorization_granted: bool,
        requires_explicit_authorization: bool,
        can_continue_locally: bool,
        matched_markers: list[str],
        required_explicit_phrase: str,
        reason: str,
        allowed_actions: list[str],
        blocked_actions: list[str] | None = None,
    ) -> ChatAuthorizationDecision:
        return ChatAuthorizationDecision(
            classifier_version=CHAT_AUTHORIZATION_RUNTIME_VERSION,
            raw=raw_text,
            category=category,
            risk_level=risk_level,
            authorization_scope=authorization_scope,
            confirmation_strength=confirmation_strength,
            authorization_granted=authorization_granted,
            requires_explicit_authorization=requires_explicit_authorization,
            can_continue_locally=can_continue_locally,
            matched_markers=matched_markers,
            required_explicit_phrase=required_explicit_phrase,
            reason=reason,
            allowed_actions=allowed_actions,
            blocked_actions=blocked_actions or high_risk_blocked,
        )

    if not raw:
        return decision(
            category="empty",
            risk_level="none",
            authorization_scope="none",
            confirmation_strength="none",
            authorization_granted=False,
            requires_explicit_authorization=False,
            can_continue_locally=False,
            matched_markers=[],
            required_explicit_phrase="",
            reason="没有可识别的聊天输入。",
            allowed_actions=[],
        )

    destructive = ("删除", "删掉", "清空", "reset", "回滚", "rollback", "revert", "撤销", "rm -rf", "drop ")
    database = ("数据库", "db", "migration", "改表", "删表", "写库", "线上数据", "真实数据写入", "生产写入", "truncate", "drop table")
    deploy = ("上线", "发布", "deploy", "生产", "重启生产", "生产重启", "回滚发布", "生产回滚")
    git = ("提交", "commit", "推送", "push", "合并请求", "pull request", "pr", "创建分支", "切换分支", "merge", "rebase", "pull", "cherry-pick", "amend")
    local_verify = ("跑测试", "运行测试", "验证", "检查", "smoke", "guard", "本地验证")
    continue_words = ("继续", "下一步", "按计划", "接着", "全自动", "做完", "推进", "继续做", "同意继续")
    confirm_words = ("我确认", "可以", "同意", "好的", "ok", "按这个做", "确认")

    database_matches = matched_keywords(normalized, database)
    deploy_matches = matched_keywords(normalized, deploy)
    git_matches = matched_keywords(normalized, git)
    destructive_matches = matched_keywords(normalized, destructive)
    local_verify_matches = matched_keywords(normalized, local_verify)
    continue_matches = matched_keywords(normalized, continue_words)
    confirm_matches = matched_keywords(normalized, confirm_words)

    if database_matches:
        if negated:
            return decision(
                category="forbidden-database-scope",
                risk_level="high",
                authorization_scope="forbidden-database-or-real-data",
                confirmation_strength="explicit-forbidden",
                authorization_granted=False,
                requires_explicit_authorization=False,
                can_continue_locally=True,
                matched_markers=database_matches,
                required_explicit_phrase="如果后续需要数据库、migration 或真实数据写入，必须重新明确授权。",
                reason="识别到数据库 / 真实数据动作，同时存在否定表达；本轮应把 DB / real-data 操作记录为 forbidden scope。",
                allowed_actions=["继续不触碰数据库、migration、真实数据写入或生产写入的本地工作。"],
            )
        return decision(
            category="database-or-real-data" if not negated else "forbidden-database-scope",
            risk_level="high",
            authorization_scope="database-or-real-data",
            confirmation_strength="explicit-high-risk",
            authorization_granted=True,
            requires_explicit_authorization=True,
            can_continue_locally=False,
            matched_markers=database_matches,
            required_explicit_phrase="已明确命中数据库、migration、真实数据或生产写入动作；执行前仍需 boundary 写清范围。",
            reason="识别到数据库、migration、真实数据或生产写入；只能在 boundary 写清并获得明确授权后执行。",
            allowed_actions=["整理需求、风险、执行范围和只读验证计划。"],
        )

    if deploy_matches:
        if negated:
            return decision(
                category="forbidden-production-scope",
                risk_level="high",
                authorization_scope="forbidden-production-or-deploy",
                confirmation_strength="explicit-forbidden",
                authorization_granted=False,
                requires_explicit_authorization=False,
                can_continue_locally=True,
                matched_markers=deploy_matches,
                required_explicit_phrase="如果后续需要上线、发布、生产重启或生产回滚，必须重新明确授权。",
                reason="识别到上线 / 发布 / 生产动作，同时存在否定表达；本轮应把生产动作记录为 forbidden scope。",
                allowed_actions=["继续不触碰生产、发布、deploy、生产重启或生产回滚的本地工作。"],
            )
        return decision(
            category="deploy-or-production",
            risk_level="high",
            authorization_scope="production-or-deploy",
            confirmation_strength="explicit-high-risk",
            authorization_granted=True,
            requires_explicit_authorization=True,
            can_continue_locally=False,
            matched_markers=deploy_matches,
            required_explicit_phrase="已明确命中上线、发布、生产或回滚发布动作；执行前仍需单独核对范围。",
            reason="识别到上线、发布、生产或回滚；这类动作必须明确授权且单独写清范围。",
            allowed_actions=["整理发布前检查清单并等待执行前核对。"],
        )

    if git_matches:
        if negated:
            return decision(
                category="forbidden-git-scope",
                risk_level="high",
                authorization_scope="forbidden-git-workflow",
                confirmation_strength="explicit-forbidden",
                authorization_granted=False,
                requires_explicit_authorization=False,
                can_continue_locally=True,
                matched_markers=git_matches,
                required_explicit_phrase="如果后续需要提交、推送、创建 PR、分支、merge 或 rebase，必须重新明确授权。",
                reason="识别到 git workflow 动作，同时存在否定表达；本轮应把 git workflow 记录为 forbidden scope。",
                allowed_actions=["继续不触碰 commit、push、PR、branch、merge、rebase、pull 的本地工作。"],
            )
        return decision(
            category="git-workflow",
            risk_level="high",
            authorization_scope="git-workflow",
            confirmation_strength="explicit-high-risk",
            authorization_granted=True,
            requires_explicit_authorization=True,
            can_continue_locally=False,
            matched_markers=git_matches,
            required_explicit_phrase="已明确命中提交、推送、PR、分支、merge、rebase、pull 或 amend 动作。",
            reason="识别到 git workflow 动作；只有用户明确说出提交、推送、创建 PR 等动作时才可执行。",
            allowed_actions=["执行对应 git workflow 前再次核对当前 diff 和验证结果。"],
        )

    if destructive_matches:
        if negated:
            return decision(
                category="forbidden-destructive-scope",
                risk_level="high",
                authorization_scope="forbidden-destructive-action",
                confirmation_strength="explicit-forbidden",
                authorization_granted=False,
                requires_explicit_authorization=False,
                can_continue_locally=True,
                matched_markers=destructive_matches,
                required_explicit_phrase="如果后续需要删除、清空、reset、撤销或回滚，必须重新明确授权并写清范围。",
                reason="识别到破坏性动作，同时存在否定表达；本轮应把 destructive action 记录为 forbidden scope。",
                allowed_actions=["继续只读检查或本地非破坏性收尾。"],
            )
        return decision(
            category="destructive-action",
            risk_level="high",
            authorization_scope="destructive-scope-required",
            confirmation_strength="scope-required",
            authorization_granted=False,
            requires_explicit_authorization=True,
            can_continue_locally=True,
            matched_markers=destructive_matches,
            required_explicit_phrase="必须明确说明删除 / 清空 / reset / 撤销 / 回滚的对象、范围和恢复方式。",
            reason="识别到删除、reset、回滚或清理类高风险动作；必须有精确范围，模糊表达不能执行。",
            allowed_actions=["只读检查当前 diff、任务记录和可恢复路径。"],
        )

    if local_verify_matches:
        return decision(
            category="local-verification",
            risk_level="low",
            authorization_scope="local-verification",
            confirmation_strength="low-risk-direct",
            authorization_granted=True,
            requires_explicit_authorization=False,
            can_continue_locally=True,
            matched_markers=local_verify_matches,
            required_explicit_phrase="如需提交、推送、上线、改 DB 或破坏性动作，必须另行明确说出对应动作。",
            reason="识别到本地验证 / 测试请求；可在 allowlist 和 active boundary 内执行。",
            allowed_actions=["运行本地测试、smoke、guard，并写入 QA evidence。"],
        )

    if continue_matches:
        return decision(
            category="continue-local-work",
            risk_level="low",
            authorization_scope="local-work-only",
            confirmation_strength="low-risk-direct",
            authorization_granted=True,
            requires_explicit_authorization=False,
            can_continue_locally=True,
            matched_markers=continue_matches,
            required_explicit_phrase="如需提交、推送、上线、改 DB 或破坏性动作，必须另行明确说出对应动作。",
            reason="识别到继续推进；只授权 Codex 继续本地可证明的需求、实现、验证和文档动作。",
            allowed_actions=["继续 active boundary 内的本地开发、验证和文档同步。"],
        )

    if confirm_matches:
        return decision(
            category="ambiguous-confirmation",
            risk_level="medium",
            authorization_scope="ambiguous-local-only",
            confirmation_strength="ambiguous",
            authorization_granted=False,
            requires_explicit_authorization=True,
            can_continue_locally=True,
            matched_markers=confirm_matches,
            required_explicit_phrase="如需高风险动作，必须明确说出提交 / 推送 / 上线 / 改 DB / 删除 / 回滚等具体动作。",
            reason="模糊确认只能确认当前低风险方案理解，不能代表生产、数据库、删除、回滚或 git workflow 授权。",
            allowed_actions=["继续不触碰高风险动作的本地工程准备或询问缺失范围。"],
        )
    return decision(
        category="unclear",
        risk_level="medium",
        authorization_scope="unclear",
        confirmation_strength="unclear",
        authorization_granted=False,
        requires_explicit_authorization=True,
        can_continue_locally=False,
        matched_markers=[],
        required_explicit_phrase="请明确这是业务选择、继续本地工作，还是提交 / 推送 / 上线 / DB / destructive 授权。",
        reason="无法稳定识别授权强度；需要 Codex 用一句话澄清业务选择或授权范围。",
        allowed_actions=["只读查看当前任务状态。"],
    )


def subagent_timeout_policy() -> SubagentTimeoutPolicy:
    return SubagentTimeoutPolicy(
        default_checkpoint_seconds=60,
        default_deadline_seconds=240,
        max_files_per_readonly_agent=3,
        max_retry_attempts=1,
        required_checkpoint_fields=[
            "files_read",
            "early_findings",
            "remaining_scope",
            "needs_more_time",
        ],
        result_schema_required_fields=[
            "status",
            "findings",
            "blocked_reason",
            "files_reviewed",
            "confidence",
            "timeout_classification",
        ],
        timeout_classifications=[
            "timeout-without-checkpoint",
            "timeout-after-checkpoint",
            "scope-too-wide",
            "tool-or-scheduler-timeout",
        ],
        timeout_recovery_steps=[
            "如果 checkpoint 前超时，记录 timeout-without-checkpoint，不把结果当成 review 通过。",
            "如果 checkpoint 后超时，保留 checkpoint 内容作为 partial evidence，并由 main agent 判断是否足够继续。",
            "如果范围过宽，缩小到最多 1-2 个输入文件并只重试一次。",
            "重试仍无 checkpoint 时，写 blocked evidence，main agent 用 deterministic smoke / guard 继续可证明验证。",
        ],
        retry_scope_rules=[
            "重试必须缩小 required inputs 或只问一个明确问题，不能原样重跑。",
            "read-only reviewer 默认最多 3 个主要输入文件；大 diff 拆成 schema / safety / docs 等独立 reviewer。",
            "worker 不用于超时恢复；只有 read-only explorer / reviewer 可自动缩小范围重试。",
        ],
        evidence_rules=[
            "subagent pass / findings / blocked / timeout 都必须回收到 repo-native evidence 或 boundary Result Integration。",
            "timeout 不能写成 QA 通过、review 通过或业务确认。",
            "没有 checkpoint 的 timeout 必须标注 `blocked` 或 `timeout-without-checkpoint`。",
        ],
    )


def subagent_with_timeout(
    *,
    name: str,
    role: str,
    trigger_stage: str,
    write_scope: str,
    output_evidence: str,
    max_files: int | None = None,
    checkpoint_seconds: int | None = None,
    deadline_seconds: int | None = None,
) -> dict[str, str]:
    policy = subagent_timeout_policy()
    return {
        "name": name,
        "role": role,
        "trigger_stage": trigger_stage,
        "write_scope": write_scope,
        "output_evidence": output_evidence,
        "checkpoint_seconds": str(checkpoint_seconds or policy.default_checkpoint_seconds),
        "deadline_seconds": str(deadline_seconds or policy.default_deadline_seconds),
        "max_files": str(max_files or policy.max_files_per_readonly_agent),
        "result_schema": "status|findings|blocked_reason|files_reviewed|confidence|timeout_classification",
        "timeout_recovery": "checkpoint required; narrow-scope-once; record timeout evidence; do not pretend pass",
    }


def subagent_recommendation_for(candidate: LoopCandidate | None) -> SubagentRecommendation:
    skip_conditions = [
        "单文件小修且没有独立探索、review 或 QA 面。",
        "下一个动作被用户业务选择、真实数据权限或生产授权强阻塞。",
        "写范围高度耦合，worker 拆分会增加冲突；此时仍可用 read-only reviewer。",
    ]
    integration = [
        "active boundary 的 Subagent Plan 必须记录 mode、角色、触发阶段、写范围和输出 evidence。",
        "explorer / reviewer 默认 read-only，结论回收到 review、QA、decision、learning 或相关 spec。",
        "worker 必须有互不重叠的 repo-relative write scope，并由 main agent 最终集成和验证。",
        "所有 subagent 都必须声明 checkpoint、deadline、结果 schema 和 timeout evidence；超时不能冒充通过。",
    ]
    if candidate is None:
        return SubagentRecommendation(
            mode="not-used",
            recommended_now=False,
            reason="当前没有可继续任务，暂不启动 subagent。",
            candidate_subagents=[],
            skip_conditions=skip_conditions,
            result_integration=integration,
        )
    if not candidate.active:
        return SubagentRecommendation(
            mode="planned-after-activation",
            recommended_now=False,
            reason="候选任务尚未激活；先激活 boundary，再根据阶段启动 read-only explorer / reviewer。",
            candidate_subagents=[
                subagent_with_timeout(
                    name="boundary-readiness-reviewer",
                    role="reviewer",
                    trigger_stage="after-activation",
                    write_scope="read-only",
                    output_evidence=".gstack/reviews/<date>_<task>-subagent-review.md",
                )
            ],
            skip_conditions=skip_conditions,
            result_integration=integration,
        )
    if candidate.blocked:
        return SubagentRecommendation(
            mode="review-if-local",
            recommended_now=False,
            reason="任务已卡住；只有卡点属于本地证据、代码或文档复核时才启动 read-only reviewer。",
            candidate_subagents=[
                subagent_with_timeout(
                    name="blocker-reviewer",
                    role="reviewer",
                    trigger_stage="blocked-local-review",
                    write_scope="read-only",
                    output_evidence=".gstack/reviews/<date>_<task>-blocker-review.md",
                    max_files=2,
                )
            ],
            skip_conditions=skip_conditions,
            result_integration=integration,
        )

    stage = candidate.current_stage_key
    if stage in {"requirement-brief", "plan-ceo-review", "requirement-freeze"}:
        return SubagentRecommendation(
            mode="review",
            recommended_now=True,
            reason="需求和设计需要磨清时，默认用 read-only reviewer 独立检查目标、范围、验收和多解风险。",
            candidate_subagents=[
                subagent_with_timeout(
                    name="requirement-design-reviewer",
                    role="reviewer",
                    trigger_stage=stage,
                    write_scope="read-only",
                    output_evidence=".gstack/reviews/<date>_<task>-requirement-design-review.md",
                )
            ],
            skip_conditions=skip_conditions,
            result_integration=integration,
        )
    if stage in {"plan-eng-review", "domain-spec-readiness"}:
        return SubagentRecommendation(
            mode="mixed-read-only",
            recommended_now=True,
            reason="工程设计和 spec readiness 有独立复核面，默认拆出 explorer / reviewer 做只读检查。",
            candidate_subagents=[
                subagent_with_timeout(
                    name="spec-contract-explorer",
                    role="explorer",
                    trigger_stage=stage,
                    write_scope="read-only",
                    output_evidence=".gstack/reviews/<date>_<task>-spec-contract-review.md",
                ),
                subagent_with_timeout(
                    name="engineering-plan-reviewer",
                    role="reviewer",
                    trigger_stage=stage,
                    write_scope="read-only",
                    output_evidence=".gstack/reviews/<date>_<task>-eng-review.md",
                ),
            ],
            skip_conditions=skip_conditions,
            result_integration=integration,
        )
    if stage == "implement":
        return SubagentRecommendation(
            mode="mixed",
            recommended_now=True,
            reason="进入施工后，默认至少用 read-only reviewer；若前端、后端、测试或文档写范围可切开，再分配 worker。",
            candidate_subagents=[
                subagent_with_timeout(
                    name="implementation-reviewer",
                    role="reviewer",
                    trigger_stage="implement",
                    write_scope="read-only",
                    output_evidence=".gstack/reviews/<date>_<task>-implementation-review.md",
                    max_files=3,
                ),
                subagent_with_timeout(
                    name="scoped-worker",
                    role="worker",
                    trigger_stage="implement",
                    write_scope="only-if-disjoint",
                    output_evidence="changed files + verification output",
                    max_files=1,
                    checkpoint_seconds=90,
                    deadline_seconds=300,
                ),
            ],
            skip_conditions=skip_conditions,
            result_integration=integration,
        )
    if stage == "qa":
        return SubagentRecommendation(
            mode="review",
            recommended_now=True,
            reason="QA 阶段默认用独立 reviewer 复核测试覆盖、用户可见验收和残余风险。",
            candidate_subagents=[
                subagent_with_timeout(
                    name="qa-evidence-reviewer",
                    role="reviewer",
                    trigger_stage="qa",
                    write_scope="read-only",
                    output_evidence=".gstack/qa-reports/<date>_<task>-qa-review.md",
                )
            ],
            skip_conditions=skip_conditions,
            result_integration=integration,
        )
    return SubagentRecommendation(
        mode="not-used",
        recommended_now=False,
        reason="当前阶段不需要 subagent；继续由 main agent 完成并在下一阶段重新评估。",
        candidate_subagents=[],
        skip_conditions=skip_conditions,
        result_integration=integration,
    )


def subagent_required_inputs(candidate: LoopCandidate | None) -> list[str]:
    if candidate is None:
        return []
    inputs = [candidate.boundary]
    route = stage_skill_route_for(candidate)
    if route is not None:
        inputs.extend(route.evidence_targets[:2])
    return [item for item in inputs if item]


def subagent_forbidden_paths() -> list[str]:
    return [
        "stack/** unless active boundary explicitly allows it",
        "archive/**",
        "blueprint/**",
        ".gstack/data-access/*.local.*",
        "production / DB / real-data targets",
        "git workflow actions",
    ]


def enrich_subagent_plan(
    subagent: dict[str, str],
    *,
    candidate: LoopCandidate | None,
    index: int,
) -> dict[str, str]:
    role = subagent.get("role", "")
    write_scope = subagent.get("write_scope", "")
    auto_start = "main-agent-may-start"
    if role == "worker":
        auto_start = "only-when-write-scope-is-disjoint"
    if candidate is None or not candidate.active or candidate.blocked or candidate.evidence_missing:
        auto_start = "refused-until-task-ready"
    return {
        "name": subagent.get("name", f"subagent-{index + 1}"),
        "role": role or "reviewer",
        "trigger_stage": subagent.get("trigger_stage", ""),
        "task": subagent.get(
            "task",
            "执行当前阶段的窄范围探索、复核或验证，并按 result_schema 返回 findings。",
        ),
        "write_scope": write_scope or "read-only",
        "forbidden_paths": " | ".join(subagent_forbidden_paths()),
        "required_inputs": " | ".join(subagent_required_inputs(candidate)),
        "output_evidence": subagent.get("output_evidence", ""),
        "checkpoint_seconds": subagent.get("checkpoint_seconds", str(subagent_timeout_policy().default_checkpoint_seconds)),
        "deadline_seconds": subagent.get("deadline_seconds", str(subagent_timeout_policy().default_deadline_seconds)),
        "max_files": subagent.get("max_files", str(subagent_timeout_policy().max_files_per_readonly_agent)),
        "result_schema": subagent.get("result_schema", "status|findings|blocked_reason|files_reviewed|confidence|timeout_classification"),
        "timeout_recovery": subagent.get("timeout_recovery", "checkpoint required; narrow-scope-once; record timeout evidence; do not pretend pass"),
        "auto_start": auto_start,
        "status": "planned" if auto_start != "refused-until-task-ready" else "blocked",
        "result_integration_target": subagent.get("output_evidence", ""),
    }


def subagent_orchestration_for(candidate: LoopCandidate | None) -> SubagentOrchestrationPolicy:
    recommendation = subagent_recommendation_for(candidate)
    timeout = subagent_timeout_policy()
    if candidate is None:
        candidate_status = "idle"
        can_continue = False
        current_stage_key = "none"
        current_stage_label = "空队列"
    else:
        candidate_status, can_continue = status_for(candidate)
        current_stage_key = candidate.current_stage_key
        current_stage_label = candidate.current_stage

    planned = [
        enrich_subagent_plan(subagent, candidate=candidate, index=index)
        for index, subagent in enumerate(recommendation.candidate_subagents)
    ]
    if recommendation.recommended_now and can_continue:
        status = "ready"
    elif candidate_status in {"blocked", "evidence-repair", "needs-activation", "idle"}:
        status = candidate_status
    elif planned:
        status = "planned"
    else:
        status = "not-recommended"

    launch_order = [
        "main agent 先确认 active boundary、current stage 和 Allowed Files。",
        "优先启动 read-only explorer / reviewer；worker 只在 write scope 互不重叠时启动。",
        "每个 subagent 必须在 checkpoint 前返回 partial evidence，否则按 timeout-without-checkpoint 处理。",
        "main agent 整合 findings 后再决定是否实现、修复、写 QA 或停止询问用户。",
    ]
    result_collection = [
        "pass / findings / blocked / timeout 都必须回收到 repo-native evidence 或 boundary Result Integration。",
        "reviewer 结果回收到 `.gstack/reviews/`；QA reviewer 结果回收到 `.gstack/qa-reports/`。",
        "治理类结果回收到 `.gstack/decisions/`、`.gstack/learnings/` 或相关 knowledge / workflow。",
        "timeout 只能作为 partial / blocked evidence，不能写成 review 通过或 QA 通过。",
    ]
    boundary_update_policy = [
        "active boundary 的 Subagent Plan 必须记录 mode、role、trigger stage、write scope、output evidence 和 status。",
        "启动前把 status 置为 planned / running；完成后由 main agent 更新为 done / blocked / timeout。",
        "worker changed files 必须由 main agent 审查、集成和验证。",
        "不修改共享 CURRENT.md；本机 active pointer 仍是 local state。",
    ]
    refused_when = [
        "没有 selected task、任务不是 active、任务 blocked 或 evidence missing。",
        "subagent 输入超过范围预算且无法缩小到 1-3 个主要文件。",
        "worker 写范围不能 repo-relative 明确切开。",
        "任务被业务选择、真实数据、生产、DB、破坏性命令、git workflow 或上线授权阻塞。",
        "subagent 结果缺少 required schema 或没有 checkpoint。",
    ]
    allowed_when = [
        "selected task 是当前本机 active boundary。",
        "当前阶段存在独立探索、复核、QA、文档治理或可切开的写范围。",
        "每个 subagent 有 role、trigger stage、write scope、required inputs、output evidence 和 timeout contract。",
        "main agent 保持最终集成、验证和用户答复责任。",
    ]
    non_actions = [
        "subagents 报告不实际启动 subagent；它只生成可执行编排协议。",
        "不生成 review / QA 通过结论，只声明 evidence 回收路径。",
        "不修改代码、不提交、不推送、不上线、不连接生产或 DB。",
        "不把 subagent 选择题交给用户；工程分工由 Codex 决定。",
    ]
    return SubagentOrchestrationPolicy(
        status=status,
        orchestrator_version=SUBAGENT_ORCHESTRATION_VERSION,
        current_stage_key=current_stage_key,
        current_stage_label=current_stage_label,
        mode=recommendation.mode,
        recommended_now=bool(recommendation.recommended_now and can_continue),
        decision_reason=recommendation.reason,
        planned_subagents=planned,
        launch_order=launch_order,
        result_collection=result_collection,
        boundary_update_policy=boundary_update_policy,
        skip_conditions=recommendation.skip_conditions,
        timeout_contract={
            "checkpoint_seconds": str(timeout.default_checkpoint_seconds),
            "deadline_seconds": str(timeout.default_deadline_seconds),
            "max_files_per_readonly_agent": str(timeout.max_files_per_readonly_agent),
            "max_retry_attempts": str(timeout.max_retry_attempts),
            "required_checkpoint_fields": "|".join(timeout.required_checkpoint_fields),
            "result_schema_required_fields": "|".join(timeout.result_schema_required_fields),
        },
        allowed_when=allowed_when,
        refused_when=refused_when,
        non_actions=non_actions,
    )


def actions_for(candidate: LoopCandidate | None) -> list[str]:
    if candidate is None:
        return [
            "当前没有未完成任务可选；Loop 进入 idle 状态。",
            "如果要继续演进骨架，应先由 Codex 创建下一段明确任务记录。",
        ]

    actions: list[str] = []
    if not candidate.active:
        actions.append("先由 Codex 在本机激活这条任务边界，再继续推进；激活本身不提交共享状态。")
    if candidate.blocked:
        actions.append("先读取卡住原因，区分本地可修复问题和需要用户确认的问题。")
    elif candidate.evidence_missing:
        actions.append("先修正缺失的 evidence 链接或任务记录，避免在错误状态上继续循环。")
    else:
        if candidate.current_stage_key in {"requirement-brief", "plan-ceo-review", "requirement-freeze"}:
            actions.append("先按 gstack 范式磨清需求 / 设计；只有业务或设计多解才给用户 2-3 个选择。")
        if candidate.current_stage_key == "implement":
            actions.append("需求冻结后由 Codex 自主选择工程施工方案，不把技术选型题转交给用户。")
        actions.append(STAGE_ACTIONS.get(candidate.current_stage_key, "继续完成当前任务的下一步。"))
        actions.append("按 subagent recommendation 启动合适的 explorer / reviewer；worker 仅在写范围可切开时使用。")
        actions.append("施工或文档同步完成后自动运行 Testing Policy 中的验证，并写入 QA evidence。")
        actions.append("完成该阶段后重新生成 loop plan，而不是无条件进入下一步。")
    actions.append("每轮只推进一个清晰阶段，并在验证后更新 QA 或任务证据。")
    return actions


def confirmations_for(candidate: LoopCandidate | None) -> list[str]:
    if candidate is None:
        return ["暂时不需要；当前只是空队列说明。"]
    if candidate.blocked:
        return ["如果卡住原因涉及业务口径、真实数据、生产、数据库、账号权限、提交、推送代码、合并请求或上线，需要你明确确认。"]
    return ["只有业务 / 设计多解、真实数据 / 生产 / 数据库、破坏性命令、提交 / 推送代码 / 合并请求 / 上线需要你确认；工程施工和测试方案由 Codex 自主选择。"]


def chat_first_protocol_for(candidate: LoopCandidate | None) -> ChatFirstProtocol:
    status, can_continue = status_for(candidate)
    if candidate is None:
        stage = "空队列"
        stage_status = "idle"
        user_status = "当前没有未完成 Loop 任务；如果要继续，需要先创建下一段任务 evidence。"
    else:
        stage = candidate.current_stage
        stage_status = status
        user_status = f"当前任务是「{candidate.task}」，阶段是「{candidate.current_stage}」，进度 {candidate.progress}。"
        if can_continue:
            user_status += " Codex 可以继续推进本地可证明的工程动作。"
        else:
            user_status += " 需要先处理 active、blocked 或 evidence 前置状态。"
    return ChatFirstProtocol(
        current_stage=stage,
        stage_status=stage_status,
        user_facing_status=user_status,
        codex_will_do=actions_for(candidate),
        user_must_choose=confirmations_for(candidate),
        user_does_not_need_to_handle=[
            "不需要选择 gstack skill、模板、代码结构、测试命令或 subagent 角色。",
            "不需要手动维护 lane、boundary、gate 或 dashboard 聚合状态。",
            "工程施工、门禁恢复和本地验证组合由 Codex 在 active boundary 内自主处理。",
        ],
        validation_result_policy=[
            "验证会报告 passed / failed / skipped / dry-run / no-commands，不把空 Verification 误判为通过。",
            "失败时 Codex 先做本地可证明的分析、修复和重跑；外部权限或业务口径才问用户。",
            "最终验证结果必须写入 QA evidence 或 boundary 指向的 evidence。",
        ],
        write_back_policy=[
            "阶段写回默认关闭。",
            "只有显式传入 --write-back、实际执行通过、evidence path 存在且当前任务为 active 时才更新 boundary。",
            "写回只更新当前阶段的 status / evidence / note，不自动执行提交、推送、上线或生产动作。",
        ],
    )


def status_for(candidate: LoopCandidate | None) -> tuple[str, bool]:
    if candidate is None:
        return "idle", False
    if candidate.blocked:
        return "blocked", False
    if candidate.evidence_missing:
        return "evidence-repair", False
    if not candidate.active:
        return "needs-activation", False
    return "ready", True


def smoke_stage_evidence_target(stage_key: str) -> str:
    targets = {
        "requirement-brief": ".gstack/requirements/<date>_<task>-requirement.md",
        "plan-ceo-review": ".gstack/reviews/<date>_<task>-ceo-review.md",
        "requirement-freeze": ".gstack/requirements/<date>_<task>-freeze.md",
        "plan-eng-review": ".gstack/reviews/<date>_<task>-eng-review.md",
        "domain-spec-readiness": ".gstack/knowledge/ai-programming-framework.md 或 stack domain spec no-change evidence",
        "implement": "changed files within active boundary",
        "qa": ".gstack/qa-reports/<date>_<task>-qa.md",
        "complete": "gstack_loop.py plan --query <task> shows open_tasks=0 / idle",
    }
    return targets.get(stage_key, "repo-native evidence")


def smoke_candidate_for_stage(stage_key: str, index: int) -> LoopCandidate:
    route = STAGE_SKILL_ROUTE_BY_KEY.get(stage_key)
    stage_label = route.stage_label if route else stage_key
    progress = "7/7" if stage_key == "complete" else f"{min(index, 6)}/7"
    return LoopCandidate(
        task="chat-first-loop-smoke scenario",
        boundary=".gstack/task-boundaries/<date>_chat-first-loop-smoke.md",
        active=True,
        blocked=False,
        progress=progress,
        current_stage_key=stage_key,
        current_stage=stage_label,
        next_step=stage_label,
        selection_reason="deterministic chat-smoke scenario",
        blocked_reasons=[],
        evidence_missing=[],
    )


def chat_first_loop_smoke_step(stage_key: str, index: int) -> ChatFirstLoopSmokeStep:
    candidate = smoke_candidate_for_stage(stage_key, index)
    route = stage_skill_route_for(candidate)
    protocol = chat_first_protocol_for(candidate)
    eng_review = eng_review_decisioner_for(candidate)
    subagents = subagent_orchestration_for(candidate)
    repair_loop = test_repair_loop_policy_for(candidate)
    write_back = stage_write_back_closure_for(candidate)
    checks = [
        "chat-first protocol present",
        "repo-native evidence target declared",
        "user choices limited to business decisions or high-risk authorization",
        "technical choices remain Codex-owned",
    ]
    if stage_key in {"implement", "qa"}:
        checks.append("test-repair policy available for local verification failure handling")
    if stage_key in {"plan-eng-review", "domain-spec-readiness", "implement", "qa"}:
        checks.append("eng-review decisioner active for engineering self-decisions")
    if stage_key == "complete":
        checks.append("completion does not imply commit, push, PR, deploy, DB, or destructive action")
    return ChatFirstLoopSmokeStep(
        stage_key=stage_key,
        stage_label=route.stage_label if route else candidate.current_stage,
        status="covered",
        progress=candidate.progress,
        evidence_target=smoke_stage_evidence_target(stage_key),
        protocol_status=protocol.stage_status,
        codex_will_do=protocol.codex_will_do,
        user_must_choose=protocol.user_must_choose,
        user_does_not_need_to_handle=protocol.user_does_not_need_to_handle,
        validation_result_policy=protocol.validation_result_policy,
        write_back_policy=protocol.write_back_policy,
        eng_review_status=eng_review.status,
        subagent_mode=subagents.mode,
        subagent_recommended_now=subagents.recommended_now,
        test_repair_enabled=repair_loop.enabled,
        stage_write_back_status=write_back.status,
        checks=checks,
    )


def build_chat_first_loop_smoke_report(raw_goal: str) -> ChatFirstLoopSmokeReport:
    expected_stages = list(STAGE_ORDER)
    steps = [
        chat_first_loop_smoke_step(stage_key, index)
        for index, stage_key in enumerate(expected_stages)
    ]
    covered = [step.stage_key for step in steps if step.status == "covered"]
    missing = [stage for stage in expected_stages if stage not in covered]
    final_protocol = chat_first_protocol_for(None)
    local_continuation = chat_authorization_for("同意，继续做")
    ambiguous_confirmation = chat_authorization_for("我确认")
    explicit_git_authorization = chat_authorization_for("提交并推送")
    forbidden_git_scope = chat_authorization_for("不要提交也不要推送")
    status = "ok"
    if missing:
        status = "missing-stage-coverage"
    if local_continuation.category != "continue-local-work":
        status = "authorization-regressed"
    if ambiguous_confirmation.authorization_granted:
        status = "authorization-regressed"
    if not explicit_git_authorization.authorization_granted:
        status = "authorization-regressed"
    if forbidden_git_scope.authorization_granted:
        status = "authorization-regressed"
    return ChatFirstLoopSmokeReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        schema_version=SCHEMA_VERSION,
        smoke_version=CHAT_FIRST_LOOP_SMOKE_VERSION,
        planner_version=PLANNER_VERSION,
        status=status,
        mode="deterministic-chat-first-loop-smoke",
        raw_goal=raw_goal,
        stage_count=len(steps),
        covered_stage_keys=covered,
        missing_stage_keys=missing,
        boundary_evidence=".gstack/task-boundaries/<date>_<task>.md",
        requirement_evidence=".gstack/requirements/<date>_<task>-requirement.md",
        review_evidence=".gstack/reviews/<date>_<task>-eng-review.md",
        qa_evidence=".gstack/qa-reports/<date>_<task>-qa.md",
        doc_sync_evidence=[
            ".gstack/scripts/README.md",
            ".gstack/workflows/codex-autopilot.md",
            ".gstack/knowledge/ai-programming-framework.md",
            "stack domain spec or no-spec-change evidence when product behavior changes",
        ],
        local_continuation=local_continuation,
        ambiguous_confirmation=ambiguous_confirmation,
        explicit_git_authorization=explicit_git_authorization,
        forbidden_git_scope=forbidden_git_scope,
        final_protocol=final_protocol,
        final_state="idle-after-complete-evidence",
        steps=steps,
        stop_conditions=high_risk_stop_conditions(),
        non_actions=non_actions(),
        source_note=(
            "chat-smoke 是端到端协议 smoke：它模拟自然语言目标进入 requirement、review、freeze、"
            "eng-review、spec readiness、implement、QA 和 complete / idle，但不写文件、不运行测试、"
            "不启动 subagent、不执行 git workflow、不连接生产 / DB / 真实数据。"
        ),
    )


def natural_language_non_actions() -> list[str]:
    return [
        "nl-smoke 只运行只读 dry-run helper，不传 --write、不传 --activate。",
        "不会创建真实业务 requirement / review / boundary / QA 文件。",
        "不会执行实现、测试修复、subagent 启动、提交、推送、PR、上线、生产或 DB 动作。",
        "不会把 formal kickoff 的 ready-to-write 误判成已经写入或已经完成业务实现。",
        "不会连接真实数据、生产环境、数据库或外部服务。",
    ]


def natural_language_next_step_command(args: argparse.Namespace) -> list[str]:
    return [
        "python3",
        ".gstack/scripts/nontechnical_next_step.py",
        "--raw",
        args.raw_request,
        "--audience",
        args.audience,
        "--success",
        args.success,
        "--non-goal",
        args.non_goal,
        "--ai-reviewed",
        "--format",
        "json",
    ]


def natural_language_formal_kickoff_command(args: argparse.Namespace) -> list[str]:
    return [
        "python3",
        ".gstack/scripts/nontechnical_formal_kickoff.py",
        "--raw",
        args.raw_request,
        "--audience",
        args.audience,
        "--success",
        args.success,
        "--non-goal",
        args.non_goal,
        "--topic",
        args.topic,
        "--dry-run",
        "--ai-reviewed",
        "--format",
        "json",
    ]


def run_json_helper(name: str, command: list[str]) -> NaturalLanguageHelperRun:
    completed = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    payload: dict[str, Any] = {}
    status = "ok" if completed.returncode == 0 else "failed"
    if completed.returncode == 0:
        try:
            loaded = json.loads(completed.stdout)
            if isinstance(loaded, dict):
                payload = loaded
            else:
                status = "invalid-json"
        except json.JSONDecodeError:
            status = "invalid-json"
    return NaturalLanguageHelperRun(
        name=name,
        command=command,
        returncode=completed.returncode,
        status=status,
        stdout_tail=output_tail(completed.stdout, 1200),
        stderr_tail=output_tail(completed.stderr, 1200),
        payload=payload,
    )


def build_natural_language_loop_smoke_report(args: argparse.Namespace) -> NaturalLanguageLoopSmokeReport:
    next_step = run_json_helper("nontechnical_next_step", natural_language_next_step_command(args))
    formal = run_json_helper("nontechnical_formal_kickoff", natural_language_formal_kickoff_command(args))
    next_payload = next_step.payload
    formal_payload = formal.payload
    summary = formal_payload.get("summary") if isinstance(formal_payload.get("summary"), dict) else {}
    paths = formal_payload.get("paths") if isinstance(formal_payload.get("paths"), dict) else {}
    acceptance = formal_payload.get("acceptance_checks") if isinstance(formal_payload.get("acceptance_checks"), list) else []
    next_response = str(next_payload.get("user_response") or "")
    failures: list[str] = []
    if next_step.status != "ok":
        failures.append(f"nontechnical_next_step failed: {next_step.status}")
    if formal.status != "ok":
        failures.append(f"nontechnical_formal_kickoff failed: {formal.status}")
    if next_payload.get("intent") != "formal_kickoff_preview":
        failures.append(f"next_step intent changed: {next_payload.get('intent')}")
    if next_payload.get("helper_entry") != "nontechnical_formal_kickoff.user":
        failures.append(f"next_step helper_entry changed: {next_payload.get('helper_entry')}")
    if next_payload.get("needs_user_confirmation") is not False:
        failures.append("next_step should not need user confirmation for the fixed safe request")
    if "正式开工包" not in next_response:
        failures.append("next_step user_response should mention formal kickoff package")
    if "不会直接操作真实数据" not in next_response:
        failures.append("next_step user_response should preserve high-risk non-actions")
    if formal_payload.get("status") != "ready-to-write":
        failures.append(f"formal status changed: {formal_payload.get('status')}")
    if formal_payload.get("can_write") is not True:
        failures.append("formal can_write should be true for fixed reviewed request")
    if formal_payload.get("written") is not False:
        failures.append("formal dry-run must not write evidence")
    if formal_payload.get("activated") is not False:
        failures.append("formal dry-run must not activate boundary")
    if formal_payload.get("ai_reviewed") is not True:
        failures.append("formal dry-run should record ai_reviewed true")
    for key in ["requirement", "review", "boundary", "qa"]:
        value = paths.get(key)
        if not isinstance(value, str) or not value.startswith(".gstack/"):
            failures.append(f"formal paths missing repo-native {key}: {value}")
    if len(acceptance) < 4:
        failures.append("formal acceptance checks should include multiple user-visible checks")
    if not any("第一眼" in str(item) for item in acceptance):
        failures.append("acceptance checks should include first-visible-success")
    if not any("不改生产数据库" in str(item) for item in acceptance):
        failures.append("acceptance checks should preserve non-goal")
    readiness_checks = [
        "next-step routes to formal kickoff preview",
        "formal kickoff dry-run is ready-to-write",
        "formal kickoff dry-run did not write evidence",
        "formal kickoff dry-run did not activate boundary",
        "repo-native requirement/review/boundary/QA paths are present",
        "acceptance checks are present and preserve non-goals",
        "high-risk non-actions remain visible",
    ]
    status = "ok" if not failures else "failed"
    final_state = "ready-to-write-dry-run-not-written" if status == "ok" else "natural-language-entry-regressed"
    return NaturalLanguageLoopSmokeReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        schema_version=SCHEMA_VERSION,
        smoke_version=NATURAL_LANGUAGE_LOOP_SMOKE_VERSION,
        planner_version=PLANNER_VERSION,
        status=status,
        mode="real-helper-dry-run-natural-language-loop-smoke",
        raw_request=args.raw_request,
        audience=args.audience,
        success=args.success,
        non_goal=args.non_goal,
        topic=args.topic,
        next_step=next_step,
        formal_kickoff=formal,
        next_step_intent=str(next_payload.get("intent") or ""),
        next_step_helper_entry=str(next_payload.get("helper_entry") or ""),
        next_step_needs_user_confirmation=bool(next_payload.get("needs_user_confirmation")),
        formal_status=str(formal_payload.get("status") or ""),
        formal_can_write=bool(formal_payload.get("can_write")),
        formal_written=bool(formal_payload.get("written")),
        formal_activated=bool(formal_payload.get("activated")),
        formal_ai_reviewed=bool(formal_payload.get("ai_reviewed")),
        recommended_lane=str(formal_payload.get("recommended_lane") or summary.get("recommended_path") or ""),
        risk_confirmation_status=str(summary.get("risk_confirmation_status") or formal_payload.get("risk_confirmation_status") or ""),
        acceptance_checks=[str(item) for item in acceptance],
        formal_paths={str(key): str(value) for key, value in paths.items()},
        readiness_checks=readiness_checks,
        failure_reasons=failures,
        final_state=final_state,
        stop_conditions=high_risk_stop_conditions(),
        non_actions=natural_language_non_actions(),
        source_note=(
            "nl-smoke 运行真实自然语言入口的只读 dry-run：nontechnical_next_step 负责正式开工预览路由，"
            "nontechnical_formal_kickoff 负责 ready-to-write 开工包预览。它不写 evidence、不激活 boundary、"
            "不执行实现、不提交、不推送、不上线、不操作生产 / DB / 真实数据。"
        ),
    )


def build_plan(args: argparse.Namespace) -> LoopPlan:
    payload = dashboard_payload(
        limit=args.limit,
        active_only=False,
        open_only=True,
        blocked_only=False,
        stage=args.stage,
        query=args.query,
        sort="attention",
    )
    all_payload = dashboard_payload(
        limit=None,
        active_only=False,
        open_only=False,
        blocked_only=False,
        stage="",
        query=args.query,
        sort="attention",
    )
    tasks = [item for item in payload.get("tasks", []) if isinstance(item, dict)]
    candidate = choose_candidate(tasks)
    status, can_auto_continue = status_for(candidate)
    return LoopPlan(
        generated_at=datetime.now(timezone.utc).isoformat(),
        schema_version=SCHEMA_VERSION,
        planner_version=PLANNER_VERSION,
        status=status,
        mode="read-only-autonomy-plan",
        candidate_count=len(tasks),
        open_tasks=int(payload.get("matched_tasks") or 0),
        total_tasks=int(all_payload.get("total_tasks") or 0),
        selected=candidate,
        can_auto_continue=can_auto_continue,
        codex_next_actions=actions_for(candidate),
        chat_first_protocol=chat_first_protocol_for(candidate),
        decision_policy=decision_policy(),
        engineering_decision_evidence=engineering_decision_evidence_for(candidate),
        eng_review_decisioner=eng_review_decisioner_for(candidate),
        continuation_policy=continuation_policy_for(candidate),
        current_stage_skill_route=stage_skill_route_for(candidate),
        stage_skill_routes=list(STAGE_SKILL_ROUTES),
        subagent_recommendation=subagent_recommendation_for(candidate),
        subagent_timeout_policy=subagent_timeout_policy(),
        subagent_orchestration=subagent_orchestration_for(candidate),
        testing_policy=testing_policy_for(candidate),
        test_repair_loop=test_repair_loop_policy_for(candidate),
        stage_write_back_policy=stage_write_back_policy(),
        stage_write_back_closure=stage_write_back_closure_for(candidate),
        release_policy=release_policy(),
        stop_conditions=high_risk_stop_conditions(),
        needs_user_confirmation=confirmations_for(candidate),
        non_actions=non_actions(),
        source_note="Loop V15 plan 只读取当前 checkout / 当前分支的 repo-native task evidence；它会输出 chat-first 协议、端到端 chat-smoke 能力、真实自然语言入口 nl-smoke 能力、阶段 skill 路由、工程自决证据、eng-review 自动决策器、subagent 自动编排、subagent timeout policy、测试-修复循环 runtime、聊天授权识别 runtime、阶段写回闭环、受控写回策略和用户确认边界。advance / run / repair-loop 只在显式执行时运行 allowlist 本地命令；write-back 必须显式 --execute 且提供已存在 evidence；subagents 只生成编排协议，不实际启动后台 agent。",
    )


def boundary_path(candidate: LoopCandidate | None) -> Path | None:
    if candidate is None or not candidate.boundary:
        return None
    path = (REPO_ROOT / candidate.boundary).resolve()
    try:
        path.relative_to(REPO_ROOT)
    except ValueError:
        return None
    if path.is_file() and path.match("*/.gstack/task-boundaries/*.md"):
        return path
    return None


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


def normalize_verification_command(line: str) -> str:
    value = line.strip()
    if value.startswith("```"):
        return ""
    if value.startswith("- "):
        value = value[2:].strip()
    return value.strip().strip("`").strip()


def verification_commands(candidate: LoopCandidate | None) -> tuple[str, list[str]]:
    path = boundary_path(candidate)
    if path is None:
        return "none", []
    text = path.read_text(encoding="utf-8")
    commands: list[str] = []
    for line in section_lines(text, "Verification"):
        command = normalize_verification_command(line)
        if command:
            commands.append(command)
    return path.relative_to(REPO_ROOT).as_posix(), commands


def repo_relative_existing_path(raw: str) -> str:
    value = raw.strip().strip("`").strip()
    if not value or "<" in value or ">" in value:
        return ""
    path = (REPO_ROOT / value).resolve()
    try:
        relative = path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return ""
    if not path.exists():
        return ""
    return relative


def empty_write_back_result(
    *,
    requested: bool,
    stage_key: str,
    evidence: str,
    boundary: str,
    status: str,
    reason: str,
) -> StageWriteBackResult:
    return StageWriteBackResult(
        requested=requested,
        performed=False,
        status=status,
        stage_key=stage_key,
        evidence=evidence,
        boundary=boundary,
        reason=reason,
        updated_fields=[],
    )


def update_required_flow_stage(
    path: Path,
    *,
    stage_key: str,
    evidence: str,
    note: str,
) -> list[str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    flow_start = next((index for index, line in enumerate(lines) if line.strip() == "## GStack Required Flow"), -1)
    if flow_start < 0:
        raise ValueError("GStack Required Flow section not found")
    flow_end = len(lines)
    for index in range(flow_start + 1, len(lines)):
        if lines[index].startswith("## "):
            flow_end = index
            break

    stage_pattern = re.compile(rf"^\s*-\s*{re.escape(stage_key)}\s*:\s*(.*?)\s*$", re.I)
    next_stage_pattern = re.compile(r"^\s*-\s*[a-z0-9/-]+\s*:\s*(.*?)\s*$", re.I)
    stage_start = -1
    stage_end = flow_end
    for index in range(flow_start + 1, flow_end):
        if stage_pattern.match(lines[index]):
            stage_start = index
            for next_index in range(index + 1, flow_end):
                if next_stage_pattern.match(lines[next_index]):
                    stage_end = next_index
                    break
            break
    if stage_start < 0:
        raise ValueError(f"stage not found: {stage_key}")

    def field_index(field: str) -> int:
        pattern = re.compile(rf"^\s*{re.escape(field)}\s*:\s*(.*?)\s*$", re.I)
        for index in range(stage_start + 1, stage_end):
            if pattern.match(lines[index]):
                return index
        return -1

    updated: list[str] = []
    status_index = field_index("status")
    if status_index >= 0:
        lines[status_index] = "  status: done"
    else:
        lines.insert(stage_start + 1, "  status: done")
        stage_end += 1
    updated.append("status")

    evidence_index = field_index("evidence")
    if evidence_index >= 0:
        lines[evidence_index] = f"  evidence: `{evidence}`"
    else:
        insert_at = status_index + 1 if status_index >= 0 else stage_start + 2
        lines.insert(insert_at, f"  evidence: `{evidence}`")
        stage_end += 1
    updated.append("evidence")

    if note:
        note_index = field_index("note")
        if note_index >= 0:
            lines[note_index] = f"  note: {note}"
        else:
            lines.insert(stage_end, f"  note: {note}")
        updated.append("note")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return updated


def maybe_write_back_stage(
    args: argparse.Namespace,
    *,
    candidate: LoopCandidate | None,
    stage_key: str,
    report_status: str,
) -> StageWriteBackResult:
    requested = bool(getattr(args, "write_back", False))
    raw_evidence = str(getattr(args, "write_back_evidence", "") or "")
    evidence = repo_relative_existing_path(raw_evidence)
    boundary = candidate.boundary if candidate else ""
    if not requested:
        return empty_write_back_result(
            requested=False,
            stage_key=stage_key,
            evidence=raw_evidence,
            boundary=boundary,
            status="not-requested",
            reason="未传入 --write-back，按默认策略不修改 boundary。",
        )
    if getattr(args, "dry_run", True):
        return empty_write_back_result(
            requested=True,
            stage_key=stage_key,
            evidence=raw_evidence,
            boundary=boundary,
            status="refused",
            reason="dry-run 模式不会写回任务状态。",
        )
    if candidate is None:
        return empty_write_back_result(
            requested=True,
            stage_key=stage_key,
            evidence=raw_evidence,
            boundary=boundary,
            status="refused",
            reason="没有 selected task。",
        )
    if not candidate.active or candidate.blocked or candidate.evidence_missing:
        return empty_write_back_result(
            requested=True,
            stage_key=stage_key,
            evidence=raw_evidence,
            boundary=boundary,
            status="refused",
            reason="只有 active、未 blocked、无 evidence 缺失的任务才允许写回。",
        )
    if report_status != "passed":
        return empty_write_back_result(
            requested=True,
            stage_key=stage_key,
            evidence=raw_evidence,
            boundary=boundary,
            status="refused",
            reason=f"验证状态是 {report_status}，不是 passed。",
        )
    if stage_key not in STAGE_ORDER or stage_key == "complete":
        return empty_write_back_result(
            requested=True,
            stage_key=stage_key,
            evidence=raw_evidence,
            boundary=boundary,
            status="refused",
            reason="当前 stage 不允许写回。",
        )
    if not evidence:
        return empty_write_back_result(
            requested=True,
            stage_key=stage_key,
            evidence=raw_evidence,
            boundary=boundary,
            status="refused",
            reason="--write-back-evidence 必须指向 repo 内已存在文件或目录。",
        )
    path = boundary_path(candidate)
    if path is None:
        return empty_write_back_result(
            requested=True,
            stage_key=stage_key,
            evidence=evidence,
            boundary=boundary,
            status="refused",
            reason="无法解析 active boundary path。",
        )
    note = str(getattr(args, "write_back_note", "") or "").strip()
    updated_fields = update_required_flow_stage(path, stage_key=stage_key, evidence=evidence, note=note)
    return StageWriteBackResult(
        requested=True,
        performed=True,
        status="updated",
        stage_key=stage_key,
        evidence=evidence,
        boundary=path.relative_to(REPO_ROOT).as_posix(),
        reason="验证通过且 evidence 存在，已受控写回当前阶段状态。",
        updated_fields=updated_fields,
    )


def output_tail(value: str, limit: int) -> str:
    if limit <= 0:
        return ""
    if len(value) <= limit:
        return value.strip()
    return value[-limit:].strip()


def skip_reason_for(command: str, candidate: LoopCandidate | None) -> str:
    if candidate is None:
        return "当前没有可执行任务。"
    if not candidate.active:
        return "候选任务不是本机当前 active task，受控执行器不会自动激活或切换任务。"
    if candidate.blocked:
        return "当前任务已卡住；受控执行器不会在 blocked 状态执行命令。"
    if candidate.evidence_missing:
        return "当前任务存在缺失证据；受控执行器不会在 evidence 缺失时执行命令。"
    tokens = command.split()
    if (
        any(token.endswith("gstack_loop.py") for token in tokens)
        and any(token in {"run", "advance", "repair-loop"} for token in tokens)
        and "--execute" in tokens
    ):
        return "跳过自我递归执行命令，避免 run / advance / repair-loop --execute 调用自身。"
    if command not in SAFE_COMMANDS:
        return "命令不在 allowlist 中；受控执行器不会运行任意 shell 命令。"
    return ""


def command_result_for_skip(command: str, reason: str) -> LoopRunCommand:
    return LoopRunCommand(
        command=command,
        status="skipped",
        allowed=False,
        skipped_reason=reason,
        returncode=None,
        duration_seconds=None,
        stdout_tail="",
        stderr_tail="",
    )


def command_result_for_dry_run(command: str) -> LoopRunCommand:
    return LoopRunCommand(
        command=command,
        status="dry-run",
        allowed=True,
        skipped_reason="dry-run only；传入 --execute 才会运行。",
        returncode=None,
        duration_seconds=None,
        stdout_tail="",
        stderr_tail="",
    )


def execute_safe_command(command: str, timeout_seconds: int, max_output_chars: int) -> LoopRunCommand:
    started = time.monotonic()
    try:
        completed = subprocess.run(
            SAFE_COMMANDS[command],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
        )
        duration = round(time.monotonic() - started, 3)
        return LoopRunCommand(
            command=command,
            status="passed" if completed.returncode == 0 else "failed",
            allowed=True,
            skipped_reason="",
            returncode=completed.returncode,
            duration_seconds=duration,
            stdout_tail=output_tail(completed.stdout, max_output_chars),
            stderr_tail=output_tail(completed.stderr, max_output_chars),
        )
    except subprocess.TimeoutExpired as exc:
        duration = round(time.monotonic() - started, 3)
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return LoopRunCommand(
            command=command,
            status="failed",
            allowed=True,
            skipped_reason="",
            returncode=None,
            duration_seconds=duration,
            stdout_tail=output_tail(stdout, max_output_chars),
            stderr_tail=output_tail(f"timeout after {timeout_seconds}s\n{stderr}", max_output_chars),
        )


def build_run_report(args: argparse.Namespace) -> LoopRunReport:
    plan = build_plan(args)
    selected = plan.selected
    candidate_status, _ = status_for(selected)
    source, commands = verification_commands(selected)
    results: list[LoopRunCommand] = []
    for command in commands:
        skip_reason = skip_reason_for(command, selected)
        if skip_reason:
            results.append(command_result_for_skip(command, skip_reason))
        elif args.dry_run:
            results.append(command_result_for_dry_run(command))
        else:
            results.append(execute_safe_command(command, args.timeout_seconds, args.max_output_chars))

    passed_count = sum(1 for item in results if item.status == "passed")
    failed_count = sum(1 for item in results if item.status == "failed")
    skipped_count = sum(1 for item in results if item.status in {"skipped", "dry-run"})
    if not commands:
        status = "no-commands"
    elif args.dry_run:
        status = "dry-run"
    elif failed_count:
        status = "failed"
    else:
        status = "passed"
    if selected is None:
        stop_reason = "no-candidate"
    elif selected.blocked:
        stop_reason = "blocked"
    elif selected.evidence_missing:
        stop_reason = "evidence-missing"
    elif not selected.active:
        stop_reason = "not-active"
    elif args.dry_run:
        stop_reason = "dry-run-only"
    elif failed_count:
        stop_reason = "command-failed"
    else:
        stop_reason = ""
    write_back_stage = selected.current_stage_key if selected else "none"
    if selected and selected.current_stage_key != "qa" and getattr(args, "write_back", False):
        write_back_result = empty_write_back_result(
            requested=True,
            stage_key=write_back_stage,
            evidence=str(getattr(args, "write_back_evidence", "") or ""),
            boundary=selected.boundary,
            status="refused",
            reason="run --write-back 只用于 QA 阶段；其他阶段使用 advance --write-back 或 main agent 写回。",
        )
    else:
        write_back_result = maybe_write_back_stage(
            args,
            candidate=selected,
            stage_key=write_back_stage,
            report_status=status,
        )
    return LoopRunReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        schema_version=SCHEMA_VERSION,
        executor_version=RUNNER_VERSION,
        mode=RUNNER_VERSION,
        executor_level="verification-only",
        dry_run=args.dry_run,
        execute_requested=not args.dry_run,
        status=status,
        selected=selected,
        candidate_status=candidate_status,
        stop_reason=stop_reason,
        requires_user_confirmation=confirmations_for(selected),
        command_source=source,
        command_count=len(commands),
        passed_count=passed_count,
        failed_count=failed_count,
        skipped_count=skipped_count,
        commands=results,
        write_back_result=write_back_result,
        stop_conditions=high_risk_stop_conditions(),
        non_actions=[
            "不会自动激活或切换 task boundary。",
            "不会修改 task boundary，除非显式传入 --write-back、实际验证通过且 evidence path 存在。",
            "不会运行不在 allowlist 中的命令。",
            "不会使用 shell=True、管道、重定向或命令拼接。",
            "不会执行提交、推送代码、创建合并请求、上线、生产、数据库或真实数据动作。",
        ],
        source_note="Loop run 只执行当前 active boundary Verification 中的 allowlist 本地验证命令；阶段写回默认关闭，必须显式 --write-back 且 evidence 存在。",
    )


def simulated_failure_command(args: argparse.Namespace) -> LoopRunCommand | None:
    command = str(getattr(args, "failure_command", "") or "").strip()
    if not command:
        return None
    stdout = str(getattr(args, "failure_stdout", "") or "")
    stderr = str(getattr(args, "failure_stderr", "") or "")
    returncode = int(getattr(args, "failure_returncode", 1) or 1)
    allowed = command in SAFE_COMMANDS
    return LoopRunCommand(
        command=command,
        status="failed" if allowed else "skipped",
        allowed=allowed,
        skipped_reason="" if allowed else "simulated failure command is outside allowlist",
        returncode=returncode if allowed else None,
        duration_seconds=0.0,
        stdout_tail=output_tail(stdout, int(getattr(args, "max_output_chars", 1200) or 1200)),
        stderr_tail=output_tail(stderr, int(getattr(args, "max_output_chars", 1200) or 1200)),
    )


def repair_failure_text(command: LoopRunCommand) -> str:
    return " ".join(
        [
            command.command,
            command.skipped_reason,
            command.stdout_tail,
            command.stderr_tail,
        ]
    ).lower()


def analyze_test_repair_failure(
    commands: list[LoopRunCommand],
    *,
    selected: LoopCandidate | None,
    dry_run: bool,
    simulated: bool,
) -> TestRepairFailureAnalysis:
    evidence_policy = [
        "失败分析、修复动作、重跑结果和残余风险必须写入 `.gstack/qa-reports/` 或 active boundary 指向的 QA evidence。",
        "dry-run、skipped、blocked 或 failed 不能写成 QA pass。",
        "如果只完成 partial verification，QA evidence 必须标注 partial / blocked reason。",
    ]
    if selected is None:
        return TestRepairFailureAnalysis(
            status="idle",
            failed_command="none",
            returncode=None,
            failure_kind="no-candidate",
            repairability="not-applicable",
            summary="当前没有 selected task；测试-修复循环不启动。",
            stdout_tail="",
            stderr_tail="",
            suggested_next_action="先创建或激活下一段明确任务 evidence。",
            requires_user_confirmation=[],
            evidence_policy=evidence_policy,
        )
    if selected.blocked or selected.evidence_missing or not selected.active:
        if selected.blocked:
            failure_kind = "task-blocked"
            summary = "当前任务 blocked；先处理 blocked reason。"
        elif selected.evidence_missing:
            failure_kind = "evidence-missing"
            summary = "当前任务 evidence 缺失；先修复 evidence 链路。"
        else:
            failure_kind = "not-active"
            summary = "候选任务不是本机 active boundary；不运行测试-修复循环。"
        return TestRepairFailureAnalysis(
            status="blocked",
            failed_command="none",
            returncode=None,
            failure_kind=failure_kind,
            repairability="blocked",
            summary=summary,
            stdout_tail="",
            stderr_tail="",
            suggested_next_action="先恢复 active boundary / evidence 状态，再重新运行 repair-loop。",
            requires_user_confirmation=[],
            evidence_policy=evidence_policy,
        )
    if not commands:
        return TestRepairFailureAnalysis(
            status="no-failure",
            failed_command="none",
            returncode=None,
            failure_kind="no-commands",
            repairability="not-applicable",
            summary="Verification 为空；不能把空验证误判为通过。",
            stdout_tail="",
            stderr_tail="",
            suggested_next_action="先补充可执行 Verification 或 QA evidence。",
            requires_user_confirmation=[],
            evidence_policy=evidence_policy,
        )
    failed = next((item for item in commands if item.status == "failed"), None)
    skipped = next((item for item in commands if item.status == "skipped"), None)
    if failed is None and skipped is None:
        if dry_run and not simulated:
            return TestRepairFailureAnalysis(
                status="not-run",
                failed_command="none",
                returncode=None,
                failure_kind="dry-run",
                repairability="not-applicable",
                summary="当前是 dry-run，只预览命令，不产生失败分析。",
                stdout_tail="",
                stderr_tail="",
                suggested_next_action="确认命令和边界后，显式传入 --execute 才运行本地验证。",
                requires_user_confirmation=[],
                evidence_policy=evidence_policy,
            )
        return TestRepairFailureAnalysis(
            status="no-failure",
            failed_command="none",
            returncode=0,
            failure_kind="passed",
            repairability="not-needed",
            summary="未发现失败命令；可以写 QA evidence 并按阶段写回策略收口。",
            stdout_tail="",
            stderr_tail="",
            suggested_next_action="写入 QA evidence；如当前阶段是 qa，可用 write-back 完成阶段状态。",
            requires_user_confirmation=[],
            evidence_policy=evidence_policy,
        )
    target = failed or skipped
    assert target is not None
    text = repair_failure_text(target)
    if target.status == "skipped" or "allowlist" in text or "outside allowlist" in text or "自我递归" in text:
        return TestRepairFailureAnalysis(
            status="blocked",
            failed_command=target.command,
            returncode=target.returncode,
            failure_kind="runtime-refused",
            repairability="blocked",
            summary="命令被受控 runtime 拒绝；不能通过 repair-loop 执行任意或自递归命令。",
            stdout_tail=target.stdout_tail,
            stderr_tail=target.stderr_tail,
            suggested_next_action="改用 allowlist 内的本地验证，或由 main agent 更新 boundary / SAFE_COMMANDS 后再重跑。",
            requires_user_confirmation=[],
            evidence_policy=evidence_policy,
        )
    external_markers = [
        "permission denied",
        "unauthorized",
        "forbidden",
        "401",
        "403",
        "credential",
        "login",
        "生产",
        "真实数据",
        "database",
        "db schema",
        "connection refused",
        "network is unreachable",
    ]
    if any(marker in text for marker in external_markers):
        return TestRepairFailureAnalysis(
            status="blocked",
            failed_command=target.command,
            returncode=target.returncode,
            failure_kind="external-or-permission",
            repairability="requires-user-or-external",
            summary="失败疑似依赖权限、网络、真实数据、生产或外部服务，不能靠本地修复闭环证明。",
            stdout_tail=target.stdout_tail,
            stderr_tail=target.stderr_tail,
            suggested_next_action="停止并说明已尝试内容、缺少的外部证据或授权。",
            requires_user_confirmation=[
                "真实数据、生产、DB、外部账号、网络权限或业务负责人确认。",
            ],
            evidence_policy=evidence_policy,
        )
    return TestRepairFailureAnalysis(
        status="needs-repair",
        failed_command=target.command,
        returncode=target.returncode,
        failure_kind="local-verification-failure",
        repairability="local-repairable",
        summary="失败来自 allowlist 本地验证；Codex 应先在 Allowed Files 内分析、修复并重跑。",
        stdout_tail=target.stdout_tail,
        stderr_tail=target.stderr_tail,
        suggested_next_action="读取失败输出，定位本地代码、脚本、文档或测试 evidence 缺口，修复后先重跑失败命令，再跑完整 Verification。",
        requires_user_confirmation=[],
        evidence_policy=evidence_policy,
    )


def repair_plan_for_analysis(analysis: TestRepairFailureAnalysis, max_attempts: int) -> list[str]:
    if analysis.repairability == "local-repairable":
        return [
            f"最多执行 {max_attempts} 轮本地修复尝试；每轮必须有明确失败命令和输出摘要。",
            "先读取 failed command、returncode、stdout_tail、stderr_tail。",
            "只在 active boundary Allowed Files 内修复本地代码、脚本、文档或测试 evidence。",
            "修复后先重跑 failed command；通过后再跑 active boundary 的完整 Verification。",
            "最终把失败、修复、重跑结果和残余风险写入 QA evidence。",
        ]
    if analysis.repairability in {"requires-user-or-external", "blocked"}:
        return [
            "停止自动修复，不扩大边界。",
            "说明失败命令、失败摘要、已尝试内容和缺少的授权或外部证据。",
            "只有用户明确授权真实数据、生产、DB、破坏性命令、git workflow 或上线动作后，才可进入对应高风险流程。",
        ]
    if analysis.status == "not-run":
        return [
            "dry-run 只预览命令和协议，不执行验证也不写 QA pass。",
            "需要真实运行时，显式传入 --execute。",
        ]
    if analysis.status == "no-failure":
        return [
            "无需修复；把实际验证结果写入 QA evidence。",
            "如当前阶段允许写回，再使用阶段写回闭环标记 QA done。",
        ]
    return [
        "当前没有可修复失败；先补齐任务、Verification 或 evidence 状态。",
    ]


def rerun_policy() -> list[str]:
    return [
        "本地修复后先重跑失败命令，避免用不相关 smoke 掩盖原失败。",
        "失败命令通过后，必须重跑 active boundary 的完整 Verification。",
        "重跑仍失败且仍属本地问题时，可在最大尝试次数内继续修复。",
        "超过最大尝试次数、需要外部权限或需要扩大边界时停止并写 blocked / partial QA。",
    ]


def qa_evidence_policy() -> list[str]:
    return [
        "QA evidence 必须记录原失败命令、returncode、输出摘要、修复动作、重跑命令和最终结果。",
        "如果 repair-loop 只是 dry-run，QA 不得写 pass。",
        "如果失败依赖外部权限或高风险授权，QA 必须标注 blocked / partial reason。",
        "QA evidence 写入后才能通过 write-back 将 qa 阶段标为 done。",
    ]


def build_test_repair_loop_report(args: argparse.Namespace) -> TestRepairLoopReport:
    plan = build_plan(args)
    selected = plan.selected
    candidate_status, _ = status_for(selected)
    source, commands = verification_commands(selected)
    simulated = simulated_failure_command(args)
    results: list[LoopRunCommand] = []
    if simulated is not None:
        source = "simulated-failure"
        results = [simulated]
    else:
        for command in commands:
            skip_reason = skip_reason_for(command, selected)
            if skip_reason:
                results.append(command_result_for_skip(command, skip_reason))
            elif args.dry_run:
                results.append(command_result_for_dry_run(command))
            else:
                results.append(execute_safe_command(command, args.timeout_seconds, args.max_output_chars))
    passed_count = sum(1 for item in results if item.status == "passed")
    failed_count = sum(1 for item in results if item.status == "failed")
    skipped_count = sum(1 for item in results if item.status in {"skipped", "dry-run"})
    analysis = analyze_test_repair_failure(
        results,
        selected=selected,
        dry_run=args.dry_run,
        simulated=simulated is not None,
    )
    if analysis.status == "needs-repair":
        status = "needs-repair"
    elif analysis.repairability in {"requires-user-or-external", "blocked"}:
        status = "blocked"
    elif analysis.status == "not-run":
        status = "dry-run"
    elif analysis.failure_kind == "no-commands":
        status = "no-commands"
    elif analysis.status == "no-failure":
        status = "passed" if not args.dry_run or simulated is not None else "dry-run"
    else:
        status = analysis.status
    max_attempts = int(getattr(args, "max_local_repair_attempts", 2) or 2)
    return TestRepairLoopReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        schema_version=SCHEMA_VERSION,
        loop_version=TEST_REPAIR_LOOP_RUNTIME_VERSION,
        mode="test-repair-loop",
        dry_run=args.dry_run,
        execute_requested=not args.dry_run,
        max_local_repair_attempts=max_attempts,
        status=status,
        selected=selected,
        candidate_status=candidate_status,
        command_source=source,
        command_count=len(results),
        passed_count=passed_count,
        failed_count=failed_count,
        skipped_count=skipped_count,
        commands=results,
        failure_analysis=analysis,
        repair_plan=repair_plan_for_analysis(analysis, max_attempts),
        rerun_policy=rerun_policy(),
        qa_evidence_policy=qa_evidence_policy(),
        stop_conditions=high_risk_stop_conditions(),
        non_actions=[
            "repair-loop 不自动编辑代码、文档、测试或 QA evidence。",
            "repair-loop 不把 failed / skipped / dry-run / blocked 写成 QA pass。",
            "repair-loop 不运行不在 allowlist 中的命令。",
            "repair-loop 不执行提交、推送代码、创建合并请求、上线、生产、数据库或真实数据动作。",
        ],
        source_note=(
            "repair-loop 是测试-修复循环报告：它运行或预览 allowlist 验证，"
            "分类失败并给 main agent 修复 / 重跑 / QA evidence 协议；实际修复由 Codex 在 boundary 内完成。"
        ),
    )


def advance_commands(
    decision: StageExecutionDecision | None,
    candidate: LoopCandidate | None,
) -> tuple[str, list[str]]:
    if decision is None or candidate is None or not decision.can_execute:
        return "none", []
    if decision.execution_strategy == "allowlist-guard":
        return "stage-execution-rule", ["python3 .gstack/scripts/spec_sync_guard.py"]
    if decision.execution_strategy == "allowlist-boundary-verification":
        return verification_commands(candidate)
    return "none", []


def execute_stage_commands(
    commands: list[str],
    candidate: LoopCandidate | None,
    *,
    dry_run: bool,
    timeout_seconds: int,
    max_output_chars: int,
) -> list[LoopRunCommand]:
    results: list[LoopRunCommand] = []
    for command in commands:
        skip_reason = skip_reason_for(command, candidate)
        if skip_reason:
            results.append(command_result_for_skip(command, skip_reason))
        elif dry_run:
            results.append(command_result_for_dry_run(command))
        else:
            results.append(execute_safe_command(command, timeout_seconds, max_output_chars))
    return results


def advance_status(
    decision: StageExecutionDecision | None,
    commands: list[LoopRunCommand],
    *,
    dry_run: bool,
    command_count: int,
) -> str:
    if decision is None:
        return "no-candidate"
    if decision.stop_reason == "complete":
        return "complete"
    if decision.stop_reason and not decision.can_execute:
        return "stopped"
    if not decision.can_execute:
        return "needs-main-agent"
    if command_count == 0:
        return "no-commands"
    if dry_run:
        return "dry-run"
    if any(item.status == "failed" for item in commands):
        return "failed"
    if any(item.status == "skipped" for item in commands):
        return "skipped"
    return "passed"


def build_advance_report(args: argparse.Namespace) -> LoopAdvanceReport:
    plan = build_plan(args)
    selected = plan.selected
    candidate_status, _ = status_for(selected)
    decision = stage_execution_decision_for(selected, plan.current_stage_skill_route)
    command_source, commands = advance_commands(decision, selected)
    command_results = execute_stage_commands(
        commands,
        selected,
        dry_run=args.dry_run,
        timeout_seconds=args.timeout_seconds,
        max_output_chars=args.max_output_chars,
    )
    passed_count = sum(1 for item in command_results if item.status == "passed")
    failed_count = sum(1 for item in command_results if item.status == "failed")
    skipped_count = sum(1 for item in command_results if item.status in {"skipped", "dry-run"})
    report_status = advance_status(decision, command_results, dry_run=args.dry_run, command_count=len(commands))
    write_back_result = maybe_write_back_stage(
        args,
        candidate=selected,
        stage_key=decision.stage_key if decision else "none",
        report_status=report_status,
    )
    return LoopAdvanceReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        schema_version=SCHEMA_VERSION,
        executor_version=ADVANCE_EXECUTOR_VERSION,
        mode="stage-advance",
        dry_run=args.dry_run,
        execute_requested=not args.dry_run,
        status=report_status,
        selected=selected,
        candidate_status=candidate_status,
        stage_decision=decision,
        command_source=command_source,
        command_count=len(commands),
        passed_count=passed_count,
        failed_count=failed_count,
        skipped_count=skipped_count,
        commands=command_results,
        write_back_result=write_back_result,
        stop_conditions=high_risk_stop_conditions(),
        non_actions=[
            "不会自动激活或切换 task boundary。",
            "不会写入 requirement、review、QA 或 spec evidence，除非显式 --write-back 且 evidence path 存在。",
            "不会运行不在 allowlist 中的命令。",
            "不会使用 shell=True、管道、重定向或命令拼接。",
            "不会执行提交、推送代码、创建合并请求、上线、生产、数据库或真实数据动作。",
        ],
        source_note="Loop advance 是受控阶段状态机：它只解释当前阶段可执行动作，并在安全阶段运行 allowlist 本地 guard / verification；阶段写回默认关闭，必须显式 --write-back 且 evidence 存在。",
    )


def build_eng_review_report(args: argparse.Namespace) -> EngReviewDecisionReport:
    plan = build_plan(args)
    selected = plan.selected
    candidate_status, _ = status_for(selected)
    explicit_evidence = str(getattr(args, "evidence", "") or "")
    decisioner = eng_review_decisioner_for(selected, evidence_path=explicit_evidence)
    status = decisioner.evidence_check.status if explicit_evidence else decisioner.status
    return EngReviewDecisionReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        schema_version=SCHEMA_VERSION,
        decisioner_version=ENG_REVIEW_DECISIONER_VERSION,
        mode="eng-review-decisioner",
        status=status,
        selected=selected,
        candidate_status=candidate_status,
        eng_review_decisioner=decisioner,
        stop_conditions=high_risk_stop_conditions(),
        non_actions=[
            "不会修改 requirement、review、boundary、QA 或业务代码。",
            "不会替用户做业务口径、多产品方向或高风险授权选择。",
            "不会执行提交、推送代码、创建合并请求、上线、生产、数据库或真实数据动作。",
            "不会把缺失或需要改写的 evidence 冒充为 ENG review 通过。",
        ],
        source_note="eng-review decisioner 只生成 / 检查 Codex 工程自决 evidence：工程方案、代码结构、测试组合、subagent 策略和门禁恢复由 Codex 自主决策；用户只处理业务选择和高风险授权。",
    )


def build_subagent_orchestration_report(args: argparse.Namespace) -> SubagentOrchestrationReport:
    plan = build_plan(args)
    selected = plan.selected
    candidate_status, _ = status_for(selected)
    orchestration = subagent_orchestration_for(selected)
    return SubagentOrchestrationReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        schema_version=SCHEMA_VERSION,
        orchestrator_version=SUBAGENT_ORCHESTRATION_VERSION,
        mode="subagent-orchestration",
        status=orchestration.status,
        selected=selected,
        candidate_status=candidate_status,
        subagent_orchestration=orchestration,
        stop_conditions=high_risk_stop_conditions(),
        non_actions=[
            "不会实际启动 subagent；只输出 main agent 可执行的编排协议。",
            "不会修改代码、review、QA、boundary 或 spec。",
            "不会把 subagent timeout 写成 QA 通过或 review 通过。",
            "不会执行提交、推送代码、创建合并请求、上线、生产、数据库或真实数据动作。",
        ],
        source_note="subagents 是 subagent 自动编排只读入口：它根据 selected task、当前阶段、timeout policy 和 boundary 约束生成 explorer / reviewer / worker / QA 分工协议，由 main agent 决定是否实际启动并负责回收 evidence。",
    )


def build_write_back_report(args: argparse.Namespace) -> StageWriteBackReport:
    plan = build_plan(args)
    selected = plan.selected
    candidate_status, _ = status_for(selected)
    current_stage_key = selected.current_stage_key if selected else "none"
    requested_stage = str(getattr(args, "stage_key", "") or current_stage_key)
    evidence = str(getattr(args, "evidence", "") or "")
    note = str(getattr(args, "note", "") or "")

    setattr(args, "write_back", True)
    setattr(args, "write_back_evidence", evidence)
    setattr(args, "write_back_note", note)

    if selected is not None and requested_stage != current_stage_key:
        write_back_result = empty_write_back_result(
            requested=True,
            stage_key=requested_stage,
            evidence=evidence,
            boundary=selected.boundary,
            status="refused",
            reason="write-back 只允许写回 selected task 的当前阶段，不能用 --stage-key 跳阶段。",
        )
    else:
        write_back_result = maybe_write_back_stage(
            args,
            candidate=selected,
            stage_key=requested_stage,
            report_status="passed",
        )
    if args.dry_run:
        status = "dry-run"
    elif write_back_result.performed:
        status = "updated"
    else:
        status = write_back_result.status
    return StageWriteBackReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        schema_version=SCHEMA_VERSION,
        writer_version=STAGE_WRITE_BACK_CLOSURE_VERSION,
        mode="stage-write-back",
        dry_run=args.dry_run,
        execute_requested=not args.dry_run,
        status=status,
        selected=selected,
        candidate_status=candidate_status,
        requested_stage_key=requested_stage,
        current_stage_key=current_stage_key,
        next_stage_on_success=next_stage_after(requested_stage),
        write_back_result=write_back_result,
        closure_policy=stage_write_back_closure_for(selected),
        stop_conditions=high_risk_stop_conditions(),
        non_actions=[
            "不会生成 requirement、review、QA 或 spec 正文。",
            "不会运行测试或实现命令。",
            "不会自动激活或切换 task boundary。",
            "不会执行提交、推送代码、创建合并请求、上线、生产、数据库或真实数据动作。",
        ],
        source_note="write-back 是阶段写回闭环入口：它只在显式 --execute、当前 active stage、已有 repo evidence 同时满足时更新 boundary 当前阶段 status / evidence / note。",
    )


def render_json(plan: LoopPlan) -> str:
    return json.dumps(asdict(plan), ensure_ascii=False, indent=2)


def render_run_json(report: LoopRunReport) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2)


def render_test_repair_loop_json(report: TestRepairLoopReport) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2)


def render_advance_json(report: LoopAdvanceReport) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2)


def render_eng_review_json(report: EngReviewDecisionReport) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2)


def render_subagent_orchestration_json(report: SubagentOrchestrationReport) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2)


def render_write_back_json(report: StageWriteBackReport) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2)


def render_test_repair_loop_markdown(report: TestRepairLoopReport) -> str:
    analysis = report.failure_analysis
    lines = [
        "# Test Repair Loop Report",
        "",
        f"- Schema：`{report.schema_version}`",
        f"- Runtime：`{report.loop_version}`",
        f"- 状态：`{report.status}`",
        f"- Dry run：`{'yes' if report.dry_run else 'no'}`",
        f"- 最大本地修复尝试：`{report.max_local_repair_attempts}`",
        f"- 命令来源：`{report.command_source}`",
        f"- 命令数量：`{report.command_count}`",
        f"- 通过：`{report.passed_count}`",
        f"- 失败：`{report.failed_count}`",
        f"- 跳过：`{report.skipped_count}`",
        f"- 来源说明：{report.source_note}",
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "## Selected Task",
                "",
                f"- 任务：{report.selected.task}",
                f"- 边界：`{report.selected.boundary}`",
                f"- 当前任务：`{'yes' if report.selected.active else 'no'}`",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：`{report.selected.progress}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Failure Analysis",
            "",
            f"- Status：`{analysis.status}`",
            f"- Failed command：`{analysis.failed_command}`",
            f"- Returncode：`{analysis.returncode if analysis.returncode is not None else 'n/a'}`",
            f"- Failure kind：`{analysis.failure_kind}`",
            f"- Repairability：`{analysis.repairability}`",
            f"- Summary：{analysis.summary}",
            f"- Suggested next action：{analysis.suggested_next_action}",
        ]
    )
    if analysis.stdout_tail:
        lines.extend(["- stdout tail:", "```text", analysis.stdout_tail, "```"])
    if analysis.stderr_tail:
        lines.extend(["- stderr tail:", "```text", analysis.stderr_tail, "```"])
    lines.extend(
        [
            "- Requires user confirmation：",
            *[f"  - {item}" for item in analysis.requires_user_confirmation],
            "",
            "## Repair Plan",
            *[f"- {item}" for item in report.repair_plan],
            "",
            "## Rerun Policy",
            *[f"- {item}" for item in report.rerun_policy],
            "",
            "## QA Evidence Policy",
            *[f"- {item}" for item in report.qa_evidence_policy],
            "",
            "## Commands",
        ]
    )
    if report.commands:
        for item in report.commands:
            lines.extend(
                [
                    "",
                    f"### `{item.command}`",
                    "",
                    f"- 状态：`{item.status}`",
                    f"- allowlist：`{'yes' if item.allowed else 'no'}`",
                    f"- 跳过原因：{item.skipped_reason or '无'}",
                    f"- 退出码：`{item.returncode if item.returncode is not None else 'n/a'}`",
                    f"- 耗时：`{item.duration_seconds if item.duration_seconds is not None else 'n/a'}`",
                ]
            )
            if item.stdout_tail:
                lines.extend(["- stdout tail:", "```text", item.stdout_tail, "```"])
            if item.stderr_tail:
                lines.extend(["- stderr tail:", "```text", item.stderr_tail, "```"])
    else:
        lines.append("- 没有可执行命令。")
    lines.extend(
        [
            "",
            "## Stop Conditions",
            *[f"- {item}" for item in report.stop_conditions],
            "",
            "## Non Actions",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_test_repair_loop_user(report: TestRepairLoopReport) -> str:
    analysis = report.failure_analysis
    lines = [
        "自动测试-修复循环：",
        f"- Schema：{report.schema_version}",
        f"- Runtime：{report.loop_version}",
        f"- 状态：{report.status}",
        f"- 这次是否真实运行：{'否，只预览' if report.dry_run else '是，显式 execute'}",
        f"- 命令：{report.command_count} 条，失败 {report.failed_count} 条，跳过 {report.skipped_count} 条",
        "",
        report.source_note,
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "当前任务：",
                f"- {report.selected.task}",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：{report.selected.progress}",
            ]
        )
    lines.extend(
        [
            "",
            "失败判断：",
            f"- 类型：{analysis.failure_kind}",
            f"- 可修复性：{analysis.repairability}",
            f"- 摘要：{analysis.summary}",
            f"- 下一步：{analysis.suggested_next_action}",
            "",
            "修复循环：",
            *[f"- {item}" for item in report.repair_plan],
            "",
            "重跑规则：",
            *[f"- {item}" for item in report.rerun_policy],
            "",
            "QA evidence 规则：",
            *[f"- {item}" for item in report.qa_evidence_policy],
        ]
    )
    if analysis.requires_user_confirmation:
        lines.extend(
            [
                "",
                "需要你确认：",
                *[f"- {item}" for item in analysis.requires_user_confirmation],
            ]
        )
    lines.extend(
        [
            "",
            "这次不会做什么：",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_markdown(plan: LoopPlan) -> str:
    subagent_lines = [
        (
            f"  - {item.get('name', 'subagent')} / {item.get('role', 'role')} / "
            f"{item.get('trigger_stage', 'stage')} / {item.get('write_scope', 'scope')} / "
            f"checkpoint {item.get('checkpoint_seconds', 'n/a')}s / deadline {item.get('deadline_seconds', 'n/a')}s"
        )
        for item in plan.subagent_recommendation.candidate_subagents
    ]
    if not subagent_lines:
        subagent_lines = ["  - none"]

    lines = [
        "# Loop Engineering V15 Plan",
        "",
        f"- Schema：`{plan.schema_version}`",
        f"- Planner：`{plan.planner_version}`",
        f"- 状态：`{plan.status}`",
        f"- 模式：`{plan.mode}`",
        f"- 未完成任务：`{plan.open_tasks}`",
        f"- 候选任务：`{plan.candidate_count}`",
        f"- 任务总数：`{plan.total_tasks}`",
        f"- 可自动继续：`{'yes' if plan.can_auto_continue else 'no'}`",
        f"- 来源说明：{plan.source_note}",
    ]
    if plan.selected:
        selected = plan.selected
        lines.extend(
            [
                "",
                "## Selected Task",
                "",
                f"- 任务：{selected.task}",
                f"- 边界：`{selected.boundary}`",
                f"- 当前任务：`{'yes' if selected.active else 'no'}`",
                f"- 是否卡住：`{'yes' if selected.blocked else 'no'}`",
                f"- 当前阶段：{selected.current_stage}",
                f"- 进度：`{selected.progress}`",
                f"- 选择理由：{selected.selection_reason}",
            ]
        )
        if selected.blocked_reasons:
            lines.append("- 卡住原因：")
            lines.extend(f"  - {item}" for item in selected.blocked_reasons)
        if selected.evidence_missing:
            lines.append("- 缺失证据：")
            lines.extend(f"  - {item}" for item in selected.evidence_missing)
    else:
        lines.extend(["", "## Selected Task", "", "- 当前没有可选择的未完成任务。"])

    if plan.current_stage_skill_route:
        route = plan.current_stage_skill_route
        lines.extend(
            [
                "",
                "## Current Stage Skill Route",
                "",
                f"- 阶段：{route.stage_label} (`{route.stage_key}`)",
                f"- 目的：{route.intent}",
                "- 默认 skills：",
                *[f"  - {item}" for item in route.default_skills],
                "- Skill IDs：",
                *[f"  - {item}" for item in route.skill_ids],
                "- Helper scripts：",
                *[f"  - {item}" for item in route.helper_scripts],
                "- Tool capabilities：",
                *[f"  - {item}" for item in route.tool_capabilities],
                "- Codex 自动决策：",
                *[f"  - {item}" for item in route.codex_auto_decisions],
                "- 必须问用户：",
                *[f"  - {item}" for item in route.ask_user_when],
                f"- subagent 默认：{route.subagent_default}",
                "- Evidence targets：",
                *[f"  - {item}" for item in route.evidence_targets],
            ]
        )

    lines.extend(
        [
            "",
            "## Chat-first Protocol",
            "",
            f"- 当前阶段：{plan.chat_first_protocol.current_stage}",
            f"- 阶段状态：`{plan.chat_first_protocol.stage_status}`",
            f"- 用户可读状态：{plan.chat_first_protocol.user_facing_status}",
            "- Codex 会自动做：",
            *[f"  - {item}" for item in plan.chat_first_protocol.codex_will_do],
            "- 需要用户选择 / 授权：",
            *[f"  - {item}" for item in plan.chat_first_protocol.user_must_choose],
            "- 用户不需要处理：",
            *[f"  - {item}" for item in plan.chat_first_protocol.user_does_not_need_to_handle],
            "- 验证结果策略：",
            *[f"  - {item}" for item in plan.chat_first_protocol.validation_result_policy],
            "- 写回策略：",
            *[f"  - {item}" for item in plan.chat_first_protocol.write_back_policy],
            "",
            "## Codex Next Actions",
            *[f"- {item}" for item in plan.codex_next_actions],
            "",
            "## Stage Skill Routes",
            "",
            *[
                f"- {route.stage_label} (`{route.stage_key}`): {', '.join(route.default_skills)}"
                for route in plan.stage_skill_routes
            ],
            "",
            "## Decision Policy",
            "",
            "### User Decides",
            *[f"- {item}" for item in plan.decision_policy.user_decides],
            "",
            "### Codex Decides",
            *[f"- {item}" for item in plan.decision_policy.codex_decides],
            "",
            f"- Ask User Style: {plan.decision_policy.ask_user_style}",
            "",
            "### Requirement / Design Discussion",
            *[f"- {item}" for item in plan.decision_policy.requirement_design_discussion],
            "",
            "## Engineering Decision Evidence",
            "",
            f"- 状态：`{plan.engineering_decision_evidence.status}`",
            "- Codex 自决：",
            *[f"  - {item}" for item in plan.engineering_decision_evidence.codex_owned_decisions],
            "- 用户决策：",
            *[f"  - {item}" for item in plan.engineering_decision_evidence.user_owned_decisions],
            "- 防止把技术选择甩给用户：",
            *[f"  - {item}" for item in plan.engineering_decision_evidence.anti_user_delegation_checks],
            "- Evidence targets：",
            *[f"  - {item}" for item in plan.engineering_decision_evidence.evidence_targets],
            "",
            "## ENG Review Auto Decisioner",
            "",
            f"- 状态：`{plan.eng_review_decisioner.status}`",
            f"- 版本：`{plan.eng_review_decisioner.decisioner_version}`",
            "- 触发阶段：",
            *[f"  - {item}" for item in plan.eng_review_decisioner.trigger_stages],
            "- Codex 自主工程决策：",
            *[f"  - {item}" for item in plan.eng_review_decisioner.codex_owned_decisions],
            "- 用户决策边界：",
            *[f"  - {item}" for item in plan.eng_review_decisioner.user_owned_decisions],
            "- 禁止交给用户的技术选择：",
            *[f"  - {item}" for item in plan.eng_review_decisioner.forbidden_user_delegations],
            "- 必需 evidence markers：",
            *[f"  - {item}" for item in plan.eng_review_decisioner.required_evidence_markers],
            "- 生成策略：",
            *[f"  - {item}" for item in plan.eng_review_decisioner.generation_policy],
            "- 检查策略：",
            *[f"  - {item}" for item in plan.eng_review_decisioner.check_policy],
            "- Evidence check：",
            f"  - path: `{plan.eng_review_decisioner.evidence_check.evidence_path or 'none'}`",
            f"  - status: `{plan.eng_review_decisioner.evidence_check.status}`",
            f"  - summary: {plan.eng_review_decisioner.evidence_check.summary}",
            "",
            "## Continuation Policy",
            "",
            f"- 可自动推进到：`{plan.continuation_policy.can_auto_continue_until}`",
            "- 可自动恢复：",
            *[f"  - {item}" for item in plan.continuation_policy.auto_recovery_actions],
            "- 必须授权的风险动作：",
            *[f"  - {item}" for item in plan.continuation_policy.risk_authorizations_required],
            "- Evidence targets：",
            *[f"  - {item}" for item in plan.continuation_policy.evidence_targets],
            "",
            "## Subagent Recommendation",
            "",
            f"- 模式：`{plan.subagent_recommendation.mode}`",
            f"- 现在建议启动：`{'yes' if plan.subagent_recommendation.recommended_now else 'no'}`",
            f"- 原因：{plan.subagent_recommendation.reason}",
            "- 候选 subagents：",
            *subagent_lines,
            "- 跳过条件：",
            *[f"  - {item}" for item in plan.subagent_recommendation.skip_conditions],
            "- 结果回收：",
            *[f"  - {item}" for item in plan.subagent_recommendation.result_integration],
            "",
            "## Subagent Orchestration",
            "",
            f"- 状态：`{plan.subagent_orchestration.status}`",
            f"- 版本：`{plan.subagent_orchestration.orchestrator_version}`",
            f"- 当前阶段：{plan.subagent_orchestration.current_stage_label} (`{plan.subagent_orchestration.current_stage_key}`)",
            f"- 模式：`{plan.subagent_orchestration.mode}`",
            f"- 现在建议启动：`{'yes' if plan.subagent_orchestration.recommended_now else 'no'}`",
            f"- 判断原因：{plan.subagent_orchestration.decision_reason}",
            "- 编排 subagents：",
            *[
                (
                    f"  - {item.get('name', 'subagent')} / {item.get('role', 'role')} / "
                    f"{item.get('trigger_stage', 'stage')} / {item.get('write_scope', 'scope')} / "
                    f"checkpoint {item.get('checkpoint_seconds', '?')}s / deadline {item.get('deadline_seconds', '?')}s / "
                    f"evidence {item.get('output_evidence', 'none')}"
                )
                for item in plan.subagent_orchestration.planned_subagents
            ],
            "- 启动顺序：",
            *[f"  - {item}" for item in plan.subagent_orchestration.launch_order],
            "- Evidence 回收：",
            *[f"  - {item}" for item in plan.subagent_orchestration.result_collection],
            "- Boundary 更新策略：",
            *[f"  - {item}" for item in plan.subagent_orchestration.boundary_update_policy],
            "- Refused when：",
            *[f"  - {item}" for item in plan.subagent_orchestration.refused_when],
            "",
            "## Subagent Timeout Policy",
            "",
            f"- 默认 checkpoint 秒数：`{plan.subagent_timeout_policy.default_checkpoint_seconds}`",
            f"- 默认 deadline 秒数：`{plan.subagent_timeout_policy.default_deadline_seconds}`",
            f"- read-only agent 最大主要输入文件数：`{plan.subagent_timeout_policy.max_files_per_readonly_agent}`",
            f"- 最大缩小范围重试次数：`{plan.subagent_timeout_policy.max_retry_attempts}`",
            "- Checkpoint 必填字段：",
            *[f"  - {item}" for item in plan.subagent_timeout_policy.required_checkpoint_fields],
            "- Result schema 必填字段：",
            *[f"  - {item}" for item in plan.subagent_timeout_policy.result_schema_required_fields],
            "- Timeout 分类：",
            *[f"  - {item}" for item in plan.subagent_timeout_policy.timeout_classifications],
            "- Timeout recovery：",
            *[f"  - {item}" for item in plan.subagent_timeout_policy.timeout_recovery_steps],
            "- Retry scope rules：",
            *[f"  - {item}" for item in plan.subagent_timeout_policy.retry_scope_rules],
            "- Evidence rules：",
            *[f"  - {item}" for item in plan.subagent_timeout_policy.evidence_rules],
            "",
            "## Testing Policy",
            "",
            f"- 自动运行：`{'yes' if plan.testing_policy.auto_run else 'no'}`",
            *[f"- {item}" for item in plan.testing_policy.required_checks],
            "- 修复策略：",
            *[f"  - {item}" for item in plan.testing_policy.repair_policy],
            f"- QA evidence：{plan.testing_policy.qa_evidence}",
            f"- UI policy：{plan.testing_policy.ui_policy}",
            "",
            "## Test Repair Loop",
            "",
            f"- 启用：`{'yes' if plan.test_repair_loop.enabled else 'no'}`",
            f"- 最大本地修复尝试：`{plan.test_repair_loop.max_local_repair_attempts}`",
            "- Loop steps：",
            *[f"  - {item}" for item in plan.test_repair_loop.loop_steps],
            "- Stop and ask when：",
            *[f"  - {item}" for item in plan.test_repair_loop.stop_and_ask_when],
            f"- QA evidence rule：{plan.test_repair_loop.qa_evidence_rule}",
            "",
            "## Stage Write-back Policy",
            "",
            f"- 默认启用：`{'yes' if plan.stage_write_back_policy.default_enabled else 'no'}`",
            "- Allowed when：",
            *[f"  - {item}" for item in plan.stage_write_back_policy.allowed_when],
            "- Refused when：",
            *[f"  - {item}" for item in plan.stage_write_back_policy.refused_when],
            f"- Evidence required：{plan.stage_write_back_policy.evidence_required}",
            "- Boundary update scope：",
            *[f"  - {item}" for item in plan.stage_write_back_policy.boundary_update_scope],
            "",
            "## Stage Write-back Closure",
            "",
            f"- 状态：`{plan.stage_write_back_closure.status}`",
            f"- 版本：`{plan.stage_write_back_closure.writer_version}`",
            f"- 当前阶段：{plan.stage_write_back_closure.current_stage_label} (`{plan.stage_write_back_closure.current_stage_key}`)",
            f"- 建议 evidence：`{plan.stage_write_back_closure.suggested_evidence or 'none'}`",
            f"- 建议命令：`{plan.stage_write_back_closure.suggested_command}`",
            "- Stage evidence rules：",
            *[
                f"  - {item['stage_key']}: {item['evidence_target']} / {item['done_when']}"
                for item in plan.stage_write_back_closure.stage_evidence_rules
            ],
            "- Allowed when：",
            *[f"  - {item}" for item in plan.stage_write_back_closure.allowed_when],
            "- Refused when：",
            *[f"  - {item}" for item in plan.stage_write_back_closure.refused_when],
            "- Non actions：",
            *[f"  - {item}" for item in plan.stage_write_back_closure.non_actions],
            "",
            "## Commit / Release Boundary",
            "",
            f"- Commit: {plan.release_policy.commit_policy}",
            f"- 推送 / 合并请求: {plan.release_policy.push_policy}",
            f"- Deploy: {plan.release_policy.deploy_policy}",
            "- 明确授权示例：",
            *[f"  - {item}" for item in plan.release_policy.explicit_authorization_examples],
            "",
            "## Stop Conditions",
            *[f"- {item}" for item in plan.stop_conditions],
            "",
            "## Needs User Confirmation",
            *[f"- {item}" for item in plan.needs_user_confirmation],
            "",
            "## Non Actions",
            *[f"- {item}" for item in plan.non_actions],
        ]
    )
    return "\n".join(lines)


def render_run_markdown(report: LoopRunReport) -> str:
    lines = [
        "# Loop Engineering Run Report",
        "",
        f"- Schema：`{report.schema_version}`",
        f"- Executor：`{report.executor_version}`",
        f"- 状态：`{report.status}`",
        f"- 模式：`{report.mode}`",
        f"- Dry run：`{'yes' if report.dry_run else 'no'}`",
        f"- 命令来源：`{report.command_source}`",
        f"- 命令数量：`{report.command_count}`",
        f"- 通过：`{report.passed_count}`",
        f"- 失败：`{report.failed_count}`",
        f"- 跳过：`{report.skipped_count}`",
        f"- 来源说明：{report.source_note}",
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "## Selected Task",
                "",
                f"- 任务：{report.selected.task}",
                f"- 边界：`{report.selected.boundary}`",
                f"- 当前任务：`{'yes' if report.selected.active else 'no'}`",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：`{report.selected.progress}`",
            ]
        )
    lines.extend(["", "## Commands"])
    if report.commands:
        for item in report.commands:
            lines.extend(
                [
                    "",
                    f"### `{item.command}`",
                    "",
                    f"- 状态：`{item.status}`",
                    f"- allowlist：`{'yes' if item.allowed else 'no'}`",
                    f"- 跳过原因：{item.skipped_reason or '无'}",
                    f"- 退出码：`{item.returncode if item.returncode is not None else 'n/a'}`",
                    f"- 耗时：`{item.duration_seconds if item.duration_seconds is not None else 'n/a'}`",
                ]
            )
            if item.stdout_tail:
                lines.extend(["- stdout tail:", "```text", item.stdout_tail, "```"])
            if item.stderr_tail:
                lines.extend(["- stderr tail:", "```text", item.stderr_tail, "```"])
    else:
        lines.append("- 没有可执行命令。")
    lines.extend(
        [
            "",
            "## Stage Write-back",
            "",
            f"- Requested：`{'yes' if report.write_back_result.requested else 'no'}`",
            f"- Performed：`{'yes' if report.write_back_result.performed else 'no'}`",
            f"- Status：`{report.write_back_result.status}`",
            f"- Stage：`{report.write_back_result.stage_key}`",
            f"- Evidence：`{report.write_back_result.evidence or 'none'}`",
            f"- Boundary：`{report.write_back_result.boundary or 'none'}`",
            f"- Reason：{report.write_back_result.reason}",
            "- Updated fields：",
            *[f"  - {item}" for item in report.write_back_result.updated_fields],
            "",
            "## Stop Conditions",
            *[f"- {item}" for item in report.stop_conditions],
            "",
            "## Non Actions",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_advance_markdown(report: LoopAdvanceReport) -> str:
    lines = [
        "# Loop Engineering Advance Report",
        "",
        f"- Schema：`{report.schema_version}`",
        f"- Executor：`{report.executor_version}`",
        f"- 状态：`{report.status}`",
        f"- Dry run：`{'yes' if report.dry_run else 'no'}`",
        f"- 命令来源：`{report.command_source}`",
        f"- 命令数量：`{report.command_count}`",
        f"- 通过：`{report.passed_count}`",
        f"- 失败：`{report.failed_count}`",
        f"- 跳过：`{report.skipped_count}`",
        f"- 来源说明：{report.source_note}",
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "## Selected Task",
                "",
                f"- 任务：{report.selected.task}",
                f"- 边界：`{report.selected.boundary}`",
                f"- 当前任务：`{'yes' if report.selected.active else 'no'}`",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：`{report.selected.progress}`",
            ]
        )
    if report.stage_decision:
        decision = report.stage_decision
        lines.extend(
            [
                "",
                "## Stage Decision",
                "",
                f"- 阶段：{decision.stage_label} (`{decision.stage_key}`)",
                f"- 动作：`{decision.action}`",
                f"- 执行策略：`{decision.execution_strategy}`",
                f"- 可由脚本执行：`{'yes' if decision.can_execute else 'no'}`",
                f"- 成功后阶段：`{decision.next_stage_on_success}`",
                f"- 需要 main agent：`{'yes' if decision.requires_main_agent else 'no'}`",
                f"- 需要用户确认：`{'yes' if decision.requires_user_confirmation else 'no'}`",
                f"- 停止原因：`{decision.stop_reason or 'none'}`",
                f"- 需要写回 evidence：`{'yes' if decision.write_back_required else 'no'}`",
                "- Evidence targets：",
                *[f"  - {item}" for item in decision.evidence_targets],
                "- 指令：",
                *[f"  - {item}" for item in decision.instructions],
            ]
        )
    lines.extend(["", "## Commands"])
    if report.commands:
        for item in report.commands:
            lines.extend(
                [
                    "",
                    f"### `{item.command}`",
                    "",
                    f"- 状态：`{item.status}`",
                    f"- allowlist：`{'yes' if item.allowed else 'no'}`",
                    f"- 跳过原因：{item.skipped_reason or '无'}",
                    f"- 退出码：`{item.returncode if item.returncode is not None else 'n/a'}`",
                    f"- 耗时：`{item.duration_seconds if item.duration_seconds is not None else 'n/a'}`",
                ]
            )
            if item.stdout_tail:
                lines.extend(["- stdout tail:", "```text", item.stdout_tail, "```"])
            if item.stderr_tail:
                lines.extend(["- stderr tail:", "```text", item.stderr_tail, "```"])
    else:
        lines.append("- 当前阶段没有可由脚本直接执行的命令。")
    lines.extend(
        [
            "",
            "## Stage Write-back",
            "",
            f"- Requested：`{'yes' if report.write_back_result.requested else 'no'}`",
            f"- Performed：`{'yes' if report.write_back_result.performed else 'no'}`",
            f"- Status：`{report.write_back_result.status}`",
            f"- Stage：`{report.write_back_result.stage_key}`",
            f"- Evidence：`{report.write_back_result.evidence or 'none'}`",
            f"- Boundary：`{report.write_back_result.boundary or 'none'}`",
            f"- Reason：{report.write_back_result.reason}",
            "- Updated fields：",
            *[f"  - {item}" for item in report.write_back_result.updated_fields],
            "",
            "## Stop Conditions",
            *[f"- {item}" for item in report.stop_conditions],
            "",
            "## Non Actions",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_user(plan: LoopPlan) -> str:
    lines = [
        "Loop V15 决策：",
        f"- Schema：{plan.schema_version}",
        f"- Planner：{plan.planner_version}",
        f"- 状态：{plan.status}",
        f"- 当前未完成任务：{plan.open_tasks}",
        f"- 这次是否能自动继续：{'能' if plan.can_auto_continue else '不能，先处理前置条件'}",
        "",
        plan.source_note,
    ]
    if plan.selected:
        selected = plan.selected
        lines.extend(
            [
                "",
                "本轮选中的任务：",
                f"- {selected.task}",
                f"- 当前阶段：{selected.current_stage}",
                f"- 进度：{selected.progress}",
                f"- 选择理由：{selected.selection_reason}",
            ]
        )
    else:
        lines.extend(["", "本轮选中的任务：", "- 当前没有可继续的未完成任务。"])

    if plan.current_stage_skill_route:
        route = plan.current_stage_skill_route
        lines.extend(
            [
                "",
                "当前阶段会自动使用的 gstack 能力：",
                f"- 阶段：{route.stage_label}",
                f"- 默认使用：{', '.join(route.default_skills)}",
                f"- 目的：{route.intent}",
                "- Codex 自己决定：",
                *[f"  - {item}" for item in route.codex_auto_decisions],
                "- 只有这些情况才问你：",
                *[f"  - {item}" for item in route.ask_user_when],
                f"- subagent 默认策略：{route.subagent_default}",
            ]
        )

    lines.extend(
        [
            "",
            "Chat-first 执行协议：",
            f"- 当前阶段：{plan.chat_first_protocol.current_stage}",
            f"- 阶段状态：{plan.chat_first_protocol.stage_status}",
            f"- 现在状态：{plan.chat_first_protocol.user_facing_status}",
            "- 我会自动做：",
            *[f"  - {item}" for item in plan.chat_first_protocol.codex_will_do],
            "- 需要你选 / 授权：",
            *[f"  - {item}" for item in plan.chat_first_protocol.user_must_choose],
            "- 不需要你管：",
            *[f"  - {item}" for item in plan.chat_first_protocol.user_does_not_need_to_handle],
            "- 验证结果会这样处理：",
            *[f"  - {item}" for item in plan.chat_first_protocol.validation_result_policy],
            "- 阶段写回会这样处理：",
            *[f"  - {item}" for item in plan.chat_first_protocol.write_back_policy],
            "",
            "Codex 的下一步：",
            *[f"- {item}" for item in plan.codex_next_actions],
            "",
            "需要你做选择的事：",
            *[f"- {item}" for item in plan.decision_policy.user_decides],
            "",
            "Codex 会自行处理的事：",
            *[f"- {item}" for item in plan.decision_policy.codex_decides],
            "",
            "提问方式：",
            f"- {plan.decision_policy.ask_user_style}",
            "",
            "工程自决证据：",
            "- Codex 自己决定：",
            *[f"  - {item}" for item in plan.engineering_decision_evidence.codex_owned_decisions],
            "- 仍然需要你决定：",
            *[f"  - {item}" for item in plan.engineering_decision_evidence.user_owned_decisions],
            "- 不会把这些技术选择甩给你：",
            *[f"  - {item}" for item in plan.engineering_decision_evidence.anti_user_delegation_checks],
            "",
            "ENG review 自动工程决策器：",
            f"- 状态：{plan.eng_review_decisioner.status}",
            f"- 版本：{plan.eng_review_decisioner.decisioner_version}",
            "- Codex 会自动做的工程决策：",
            *[f"  - {item}" for item in plan.eng_review_decisioner.codex_owned_decisions],
            "- 只有这些仍然归你决定：",
            *[f"  - {item}" for item in plan.eng_review_decisioner.user_owned_decisions],
            "- 不会问你的技术题：",
            *[f"  - {item}" for item in plan.eng_review_decisioner.forbidden_user_delegations],
            f"- Evidence check: {plan.eng_review_decisioner.evidence_check.status}，{plan.eng_review_decisioner.evidence_check.summary}",
            "",
            "自动推进边界：",
            f"- 最多自动推进到：{plan.continuation_policy.can_auto_continue_until}",
            "- 本地可证明的门禁和验证失败会先由 Codex 自动修复；涉及真实数据、生产、数据库、破坏性命令、提交、合并请求、上线或回滚会停下来问你。",
            "",
            "subagent 策略：",
            f"- 模式：{plan.subagent_recommendation.mode}",
            f"- 现在建议启动：{'是' if plan.subagent_recommendation.recommended_now else '否'}",
            f"- 原因：{plan.subagent_recommendation.reason}",
            f"- 默认 checkpoint：{plan.subagent_timeout_policy.default_checkpoint_seconds} 秒内必须先回一次部分结论",
            f"- 默认 deadline：{plan.subagent_timeout_policy.default_deadline_seconds} 秒没有完成就按 timeout 处理",
            f"- 默认范围：read-only subagent 一次最多看 {plan.subagent_timeout_policy.max_files_per_readonly_agent} 个主要输入文件",
            f"- 默认重试：超时后只能缩小范围重试 {plan.subagent_timeout_policy.max_retry_attempts} 次，不能原样重跑",
            "- 超时后处理：",
            *[f"  - {item}" for item in plan.subagent_timeout_policy.timeout_recovery_steps],
            "- 结果证据规则：",
            *[f"  - {item}" for item in plan.subagent_timeout_policy.evidence_rules],
            "",
            "subagent 自动编排：",
            f"- 状态：{plan.subagent_orchestration.status}",
            f"- 模式：{plan.subagent_orchestration.mode}",
            f"- 当前阶段：{plan.subagent_orchestration.current_stage_label}",
            f"- 现在建议启动：{'是' if plan.subagent_orchestration.recommended_now else '否'}",
            f"- 判断原因：{plan.subagent_orchestration.decision_reason}",
            "- 自动分工：",
            *[
                (
                    f"  - {item.get('name', 'subagent')} / {item.get('role', 'role')} / "
                    f"{item.get('trigger_stage', 'stage')} / {item.get('write_scope', 'scope')} / "
                    f"evidence {item.get('output_evidence', 'none')}"
                )
                for item in plan.subagent_orchestration.planned_subagents
            ],
            "- Evidence 回收：",
            *[f"  - {item}" for item in plan.subagent_orchestration.result_collection],
            "",
            "自动测试策略：",
            *[f"- {item}" for item in plan.testing_policy.required_checks],
            "- 失败后修复循环：",
            *[f"  - {item}" for item in plan.test_repair_loop.loop_steps],
            "",
            "阶段写回边界：",
            f"- 默认启用：{'是' if plan.stage_write_back_policy.default_enabled else '否'}",
            f"- 证据要求：{plan.stage_write_back_policy.evidence_required}",
            "- 拒绝写回：",
            *[f"  - {item}" for item in plan.stage_write_back_policy.refused_when],
            "",
            "阶段写回闭环：",
            f"- 状态：{plan.stage_write_back_closure.status}",
            f"- 当前阶段：{plan.stage_write_back_closure.current_stage_label}",
            f"- 建议 evidence：{plan.stage_write_back_closure.suggested_evidence or 'none'}",
            f"- 建议命令：{plan.stage_write_back_closure.suggested_command}",
            "- 允许写回：",
            *[f"  - {item}" for item in plan.stage_write_back_closure.allowed_when],
            "- 会拒绝：",
            *[f"  - {item}" for item in plan.stage_write_back_closure.refused_when],
            "",
            "提交和上线边界：",
            f"- {plan.release_policy.commit_policy}",
            f"- {plan.release_policy.push_policy}",
            f"- {plan.release_policy.deploy_policy}",
            "",
            "什么时候必须停下来：",
            *[f"- {item}" for item in plan.stop_conditions],
            "",
            "需要你确认：",
            *[f"- {item}" for item in plan.needs_user_confirmation],
            "",
            "这次不会做什么：",
            *[f"- {item}" for item in plan.non_actions],
        ]
    )
    return "\n".join(lines)


def render_run_user(report: LoopRunReport) -> str:
    lines = [
        "Loop 执行报告：",
        f"- Schema：{report.schema_version}",
        f"- Executor：{report.executor_version}",
        f"- 状态：{report.status}",
        f"- 这次是否实际运行：{'否，只预览' if report.dry_run else '是，只运行 allowlist 本地验证'}",
        f"- 命令数量：{report.command_count}",
        f"- 通过：{report.passed_count}",
        f"- 失败：{report.failed_count}",
        f"- 跳过：{report.skipped_count}",
        "",
        report.source_note,
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "当前任务：",
                f"- {report.selected.task}",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：{report.selected.progress}",
            ]
        )
    lines.extend(["", "命令结果："])
    if report.commands:
        for item in report.commands:
            detail = f"{item.status}"
            if item.returncode is not None:
                detail += f"，退出码 {item.returncode}"
            if item.skipped_reason:
                detail += f"，{item.skipped_reason}"
            lines.append(f"- {item.command}：{detail}")
    else:
        lines.append("- 没有找到可执行的本地验证命令。")
    lines.extend(
        [
            "",
            "阶段写回：",
            f"- 是否请求：{'是' if report.write_back_result.requested else '否'}",
            f"- 是否执行：{'是' if report.write_back_result.performed else '否'}",
            f"- 状态：{report.write_back_result.status}",
            f"- 原因：{report.write_back_result.reason}",
            "",
            "这次不会做什么：",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_advance_user(report: LoopAdvanceReport) -> str:
    lines = [
        "Loop 阶段推进报告：",
        f"- Schema：{report.schema_version}",
        f"- Executor：{report.executor_version}",
        f"- 状态：{report.status}",
        f"- 这次是否实际运行：{'否，只预览' if report.dry_run else '是，只运行 allowlist 本地阶段命令'}",
        "",
        report.source_note,
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "当前任务：",
                f"- {report.selected.task}",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：{report.selected.progress}",
            ]
        )
    if report.stage_decision:
        decision = report.stage_decision
        lines.extend(
            [
                "",
                "阶段决策：",
                f"- 动作：{decision.action}",
                f"- 执行策略：{decision.execution_strategy}",
                f"- 脚本能否直接执行：{'能' if decision.can_execute else '不能，需要 Codex main agent 施工'}",
                f"- 成功后进入：{decision.next_stage_on_success}",
                f"- 是否需要写回 evidence：{'是' if decision.write_back_required else '否'}",
                f"- 是否需要问你：{'是' if decision.requires_user_confirmation else '否'}",
                "- 现在应该做：",
                *[f"  - {item}" for item in decision.instructions],
            ]
        )
    lines.extend(["", "命令结果："])
    if report.commands:
        for item in report.commands:
            detail = f"{item.status}"
            if item.returncode is not None:
                detail += f"，退出码 {item.returncode}"
            if item.skipped_reason:
                detail += f"，{item.skipped_reason}"
            lines.append(f"- {item.command}：{detail}")
    else:
        lines.append("- 当前阶段没有由脚本直接执行的命令。")
    lines.extend(
        [
            "",
            "阶段写回：",
            f"- 是否请求：{'是' if report.write_back_result.requested else '否'}",
            f"- 是否执行：{'是' if report.write_back_result.performed else '否'}",
            f"- 状态：{report.write_back_result.status}",
            f"- 原因：{report.write_back_result.reason}",
            "",
            "这次不会做什么：",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_eng_review_markdown(report: EngReviewDecisionReport) -> str:
    decisioner = report.eng_review_decisioner
    check = decisioner.evidence_check
    lines = [
        "# ENG Review Auto Decisioner",
        "",
        f"- Schema：`{report.schema_version}`",
        f"- Decisioner：`{report.decisioner_version}`",
        f"- 状态：`{report.status}`",
        f"- 候选状态：`{report.candidate_status}`",
        f"- 来源说明：{report.source_note}",
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "## Selected Task",
                "",
                f"- 任务：{report.selected.task}",
                f"- 边界：`{report.selected.boundary}`",
                f"- 当前任务：`{'yes' if report.selected.active else 'no'}`",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：`{report.selected.progress}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Decision Contract",
            "",
            f"- 状态：`{decisioner.status}`",
            "- Codex 自主工程决策：",
            *[f"  - {item}" for item in decisioner.codex_owned_decisions],
            "- 用户决策边界：",
            *[f"  - {item}" for item in decisioner.user_owned_decisions],
            "- 禁止交给用户的技术选择：",
            *[f"  - {item}" for item in decisioner.forbidden_user_delegations],
            "- 必需 evidence markers：",
            *[f"  - {item}" for item in decisioner.required_evidence_markers],
            "- 生成策略：",
            *[f"  - {item}" for item in decisioner.generation_policy],
            "- 检查策略：",
            *[f"  - {item}" for item in decisioner.check_policy],
            "",
            "## Evidence Check",
            "",
            f"- Path：`{check.evidence_path or 'none'}`",
            f"- Exists：`{'yes' if check.exists else 'no'}`",
            f"- Status：`{check.status}`",
            f"- Summary：{check.summary}",
            "- Found required markers：",
            *[f"  - {item}" for item in check.found_required_markers],
            "- Missing required markers：",
            *[f"  - {item}" for item in check.missing_required_markers],
            "- Forbidden delegations found：",
            *[f"  - {item}" for item in check.forbidden_user_delegations_found],
            "",
            "## Stop Conditions",
            *[f"- {item}" for item in report.stop_conditions],
            "",
            "## Non Actions",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_eng_review_user(report: EngReviewDecisionReport) -> str:
    decisioner = report.eng_review_decisioner
    check = decisioner.evidence_check
    lines = [
        "ENG review 自动工程决策器：",
        f"- Schema：{report.schema_version}",
        f"- Decisioner：{report.decisioner_version}",
        f"- 状态：{report.status}",
        "",
        report.source_note,
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "当前任务：",
                f"- {report.selected.task}",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：{report.selected.progress}",
            ]
        )
    lines.extend(
        [
            "",
            "Codex 自动做：",
            *[f"- {item}" for item in decisioner.codex_owned_decisions],
            "",
            "只在这些情况问你：",
            *[f"- {item}" for item in decisioner.user_owned_decisions],
            "",
            "不会问你的技术题：",
            *[f"- {item}" for item in decisioner.forbidden_user_delegations],
            "",
            "Evidence 检查：",
            f"- path: {check.evidence_path or 'none'}",
            f"- status: {check.status}",
            f"- {check.summary}",
        ]
    )
    if check.missing_required_markers:
        lines.extend(["- 缺少 marker：", *[f"  - {item}" for item in check.missing_required_markers]])
    if check.forbidden_user_delegations_found:
        lines.extend(["- 发现技术甩锅短语：", *[f"  - {item}" for item in check.forbidden_user_delegations_found]])
    lines.extend(
        [
            "",
            "这次不会做什么：",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_subagent_orchestration_markdown(report: SubagentOrchestrationReport) -> str:
    policy = report.subagent_orchestration
    lines = [
        "# Subagent Orchestration Report",
        "",
        f"- Schema：`{report.schema_version}`",
        f"- Orchestrator：`{report.orchestrator_version}`",
        f"- 状态：`{report.status}`",
        f"- 来源说明：{report.source_note}",
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "## Selected Task",
                "",
                f"- 任务：{report.selected.task}",
                f"- 边界：`{report.selected.boundary}`",
                f"- 当前任务：`{'yes' if report.selected.active else 'no'}`",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：`{report.selected.progress}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Orchestration",
            "",
            f"- 版本：`{policy.orchestrator_version}`",
            f"- 当前阶段：{policy.current_stage_label} (`{policy.current_stage_key}`)",
            f"- 模式：`{policy.mode}`",
            f"- 现在建议启动：`{'yes' if policy.recommended_now else 'no'}`",
            f"- 判断原因：{policy.decision_reason}",
            "- Planned subagents：",
        ]
    )
    if policy.planned_subagents:
        for item in policy.planned_subagents:
            lines.extend(
                [
                    f"  - `{item.get('name', 'subagent')}` / `{item.get('role', 'role')}` / `{item.get('trigger_stage', 'stage')}`",
                    f"    - write scope: `{item.get('write_scope', 'none')}`",
                    f"    - required inputs: `{item.get('required_inputs', 'none')}`",
                    f"    - output evidence: `{item.get('output_evidence', 'none')}`",
                    f"    - checkpoint/deadline: `{item.get('checkpoint_seconds', '?')}s / {item.get('deadline_seconds', '?')}s`",
                    f"    - status: `{item.get('status', 'planned')}`",
                ]
            )
    else:
        lines.append("  - none")
    lines.extend(
        [
            "- Launch order：",
            *[f"  - {item}" for item in policy.launch_order],
            "- Result collection：",
            *[f"  - {item}" for item in policy.result_collection],
            "- Boundary update policy：",
            *[f"  - {item}" for item in policy.boundary_update_policy],
            "- Timeout contract：",
            *[f"  - {key}: `{value}`" for key, value in policy.timeout_contract.items()],
            "- Skip conditions：",
            *[f"  - {item}" for item in policy.skip_conditions],
            "- Refused when：",
            *[f"  - {item}" for item in policy.refused_when],
            "",
            "## Non Actions",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_subagent_orchestration_user(report: SubagentOrchestrationReport) -> str:
    policy = report.subagent_orchestration
    lines = [
        "Subagent 自动编排：",
        f"- Schema：{report.schema_version}",
        f"- Orchestrator：{report.orchestrator_version}",
        f"- 状态：{report.status}",
        "",
        report.source_note,
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "当前任务：",
                f"- {report.selected.task}",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：{report.selected.progress}",
            ]
        )
    lines.extend(
        [
            "",
            "Codex 会自动判断：",
            f"- 模式：{policy.mode}",
            f"- 现在建议启动：{'是' if policy.recommended_now else '否'}",
            f"- 原因：{policy.decision_reason}",
        ]
    )
    if policy.planned_subagents:
        lines.extend(["", "计划的 subagent："])
        for item in policy.planned_subagents:
            lines.extend(
                [
                    f"- {item.get('name', 'subagent')} / {item.get('role', 'role')} / {item.get('trigger_stage', 'stage')}",
                    f"  - 写范围：{item.get('write_scope', 'none')}",
                    f"  - 输入：{item.get('required_inputs', 'none')}",
                    f"  - evidence：{item.get('output_evidence', 'none')}",
                    f"  - checkpoint/deadline：{item.get('checkpoint_seconds', '?')}s / {item.get('deadline_seconds', '?')}s",
                ]
            )
    else:
        lines.extend(["", "计划的 subagent：", "- none"])
    lines.extend(
        [
            "",
            "结果怎么回收：",
            *[f"- {item}" for item in policy.result_collection],
            "",
            "什么时候会跳过或停止：",
            *[f"- {item}" for item in policy.refused_when],
            "",
            "不需要你管：",
            "- 不需要选择 subagent 角色、checkpoint、deadline、测试组合或门禁恢复顺序。",
            "- Codex 负责启动、整合、验证和把结论写入 repo-native evidence。",
            "",
            "这次不会做什么：",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_write_back_markdown(report: StageWriteBackReport) -> str:
    result = report.write_back_result
    lines = [
        "# Stage Write-back Report",
        "",
        f"- Schema：`{report.schema_version}`",
        f"- Writer：`{report.writer_version}`",
        f"- 状态：`{report.status}`",
        f"- Dry run：`{'yes' if report.dry_run else 'no'}`",
        f"- Requested stage：`{report.requested_stage_key}`",
        f"- Current stage：`{report.current_stage_key}`",
        f"- 成功后阶段：`{report.next_stage_on_success}`",
        f"- 来源说明：{report.source_note}",
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "## Selected Task",
                "",
                f"- 任务：{report.selected.task}",
                f"- 边界：`{report.selected.boundary}`",
                f"- 当前任务：`{'yes' if report.selected.active else 'no'}`",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：`{report.selected.progress}`",
            ]
        )
    lines.extend(
        [
            "",
            "## Write-back Result",
            "",
            f"- Requested：`{'yes' if result.requested else 'no'}`",
            f"- Performed：`{'yes' if result.performed else 'no'}`",
            f"- Status：`{result.status}`",
            f"- Stage：`{result.stage_key}`",
            f"- Evidence：`{result.evidence or 'none'}`",
            f"- Boundary：`{result.boundary or 'none'}`",
            f"- Reason：{result.reason}",
            "- Updated fields：",
            *[f"  - {item}" for item in result.updated_fields],
            "",
            "## Closure Policy",
            "",
            f"- 状态：`{report.closure_policy.status}`",
            f"- Suggested evidence：`{report.closure_policy.suggested_evidence or 'none'}`",
            f"- Suggested command：`{report.closure_policy.suggested_command}`",
            "- Allowed when：",
            *[f"  - {item}" for item in report.closure_policy.allowed_when],
            "- Refused when：",
            *[f"  - {item}" for item in report.closure_policy.refused_when],
            "",
            "## Stop Conditions",
            *[f"- {item}" for item in report.stop_conditions],
            "",
            "## Non Actions",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_write_back_user(report: StageWriteBackReport) -> str:
    result = report.write_back_result
    lines = [
        "阶段写回报告：",
        f"- Schema：{report.schema_version}",
        f"- Writer：{report.writer_version}",
        f"- 状态：{report.status}",
        f"- 这次是否实际写回：{'否，只预览' if report.dry_run else '是，显式 execute'}",
        "",
        report.source_note,
    ]
    if report.selected:
        lines.extend(
            [
                "",
                "当前任务：",
                f"- {report.selected.task}",
                f"- 当前阶段：{report.selected.current_stage}",
                f"- 进度：{report.selected.progress}",
            ]
        )
    lines.extend(
        [
            "",
            "写回结果：",
            f"- 是否执行：{'是' if result.performed else '否'}",
            f"- 阶段：{result.stage_key}",
            f"- evidence：{result.evidence or 'none'}",
            f"- 原因：{result.reason}",
            f"- 成功后阶段：{report.next_stage_on_success}",
            "",
            "允许条件：",
            *[f"- {item}" for item in report.closure_policy.allowed_when],
            "",
            "拒绝条件：",
            *[f"- {item}" for item in report.closure_policy.refused_when],
            "",
            "这次不会做什么：",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_chat_first_loop_smoke_json(report: ChatFirstLoopSmokeReport) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2)


def render_chat_first_loop_smoke_markdown(report: ChatFirstLoopSmokeReport) -> str:
    lines = [
        "# Chat-first Loop Smoke",
        "",
        f"- Schema：`{report.schema_version}`",
        f"- Smoke：`{report.smoke_version}`",
        f"- Planner：`{report.planner_version}`",
        f"- Status：`{report.status}`",
        f"- Goal：{report.raw_goal}",
        f"- Stage count：`{report.stage_count}`",
        f"- Missing stages：`{', '.join(report.missing_stage_keys) if report.missing_stage_keys else 'none'}`",
        f"- Final state：`{report.final_state}`",
        "",
        "## Source Note",
        "",
        report.source_note,
        "",
        "## Stages",
    ]
    for step in report.steps:
        lines.extend(
            [
                "",
                f"### {step.stage_key}",
                "",
                f"- Label：{step.stage_label}",
                f"- Status：`{step.status}`",
                f"- Evidence：`{step.evidence_target}`",
                f"- Eng review：`{step.eng_review_status}`",
                f"- Subagent mode：`{step.subagent_mode}`",
                f"- Test repair：`{'enabled' if step.test_repair_enabled else 'disabled'}`",
                "- Checks：",
                *[f"  - {item}" for item in step.checks],
            ]
        )
    lines.extend(
        [
            "",
            "## Authorization Samples",
            "",
            f"- Continue：`{report.local_continuation.category}` / `{report.local_continuation.authorization_scope}`",
            f"- Ambiguous：`{report.ambiguous_confirmation.category}` / granted `{report.ambiguous_confirmation.authorization_granted}`",
            f"- Git explicit：`{report.explicit_git_authorization.category}` / granted `{report.explicit_git_authorization.authorization_granted}`",
            f"- Git forbidden：`{report.forbidden_git_scope.category}` / granted `{report.forbidden_git_scope.authorization_granted}`",
            "",
            "## Non Actions",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_chat_first_loop_smoke_user(report: ChatFirstLoopSmokeReport) -> str:
    lines = [
        "Chat-first Loop 端到端 smoke：",
        f"- Schema：{report.schema_version}",
        f"- Smoke：{report.smoke_version}",
        f"- 状态：{report.status}",
        f"- 自然语言目标：{report.raw_goal}",
        f"- 覆盖阶段数：{report.stage_count}",
        f"- 缺失阶段：{', '.join(report.missing_stage_keys) if report.missing_stage_keys else '无'}",
        f"- 最终状态：{report.final_state}",
        "",
        report.source_note,
        "",
        "阶段链路：",
    ]
    for step in report.steps:
        lines.extend(
            [
                f"- {step.stage_label}：{step.status}",
                f"  - evidence：{step.evidence_target}",
                f"  - Codex 自动处理：{step.codex_will_do[0] if step.codex_will_do else 'none'}",
                f"  - 需要用户决定：{step.user_must_choose[0] if step.user_must_choose else '无'}",
            ]
        )
    lines.extend(
        [
            "",
            "授权样例：",
            f"- “同意，继续做”：{report.local_continuation.category}，只授权 {report.local_continuation.authorization_scope}",
            f"- “我确认”：{report.ambiguous_confirmation.category}，不授权高风险动作",
            f"- “提交并推送”：{report.explicit_git_authorization.category}，显式高风险授权",
            f"- “不要提交也不要推送”：{report.forbidden_git_scope.category}，记录 forbidden scope",
            "",
            "不需要你管：",
            "- 不需要选择 skill、模板、代码结构、测试命令、subagent 角色或门禁恢复顺序。",
            "- Codex 负责需求、评审、实现、验证、QA evidence 和文档同步的工程闭环。",
            "",
            "必须停下来问你的情况：",
            *[f"- {item}" for item in report.stop_conditions],
            "",
            "这次不会做什么：",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_natural_language_loop_smoke_json(report: NaturalLanguageLoopSmokeReport) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2)


def render_natural_language_loop_smoke_markdown(report: NaturalLanguageLoopSmokeReport) -> str:
    lines = [
        "# Natural-language Loop Smoke",
        "",
        f"- Schema：`{report.schema_version}`",
        f"- Smoke：`{report.smoke_version}`",
        f"- Planner：`{report.planner_version}`",
        f"- Status：`{report.status}`",
        f"- Mode：`{report.mode}`",
        f"- Request：{report.raw_request}",
        f"- Audience：{report.audience}",
        f"- Success：{report.success}",
        f"- Non-goal：{report.non_goal}",
        f"- Final state：`{report.final_state}`",
        "",
        "## Source Note",
        "",
        report.source_note,
        "",
        "## Helper Results",
        "",
        f"- Next step：`{report.next_step.status}` / `{report.next_step_intent}` / `{report.next_step_helper_entry}`",
        f"- Formal kickoff：`{report.formal_kickoff.status}` / `{report.formal_status}`",
        f"- Can write：`{'yes' if report.formal_can_write else 'no'}`",
        f"- Written：`{'yes' if report.formal_written else 'no'}`",
        f"- Activated：`{'yes' if report.formal_activated else 'no'}`",
        f"- AI reviewed：`{'yes' if report.formal_ai_reviewed else 'no'}`",
        f"- Risk confirmation：`{report.risk_confirmation_status}`",
        "",
        "## Formal Paths",
        *[f"- {key}: `{value}`" for key, value in report.formal_paths.items()],
        "",
        "## Acceptance Checks",
        *[f"- {item}" for item in report.acceptance_checks],
        "",
        "## Readiness Checks",
        *[f"- {item}" for item in report.readiness_checks],
    ]
    if report.failure_reasons:
        lines.extend(["", "## Failures", *[f"- {item}" for item in report.failure_reasons]])
    lines.extend(
        [
            "",
            "## Stop Conditions",
            *[f"- {item}" for item in report.stop_conditions],
            "",
            "## Non Actions",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_natural_language_loop_smoke_user(report: NaturalLanguageLoopSmokeReport) -> str:
    lines = [
        "自然语言入口 Loop smoke：",
        f"- Schema：{report.schema_version}",
        f"- Smoke：{report.smoke_version}",
        f"- 状态：{report.status}",
        f"- 自然语言目标：{report.raw_request}",
        f"- 用户：{report.audience}",
        f"- 成功样子：{report.success}",
        f"- 不做范围：{report.non_goal}",
        f"- 最终状态：{report.final_state}",
        "",
        report.source_note,
        "",
        "真实入口检查：",
        f"- 下一步路由：{report.next_step_intent} / {report.next_step_helper_entry}",
        f"- 正式开工预览：{report.formal_status}",
        f"- 可写入正式开工包：{'是，但本次 dry-run 没写入' if report.formal_can_write else '否'}",
        f"- 已写入：{'是' if report.formal_written else '否'}",
        f"- 已激活 boundary：{'是' if report.formal_activated else '否'}",
        "",
        "生成路径预览：",
        *[f"- {key}: {value}" for key, value in report.formal_paths.items()],
        "",
        "验收清单：",
        *[f"- {item}" for item in report.acceptance_checks],
        "",
        "能力检查：",
        *[f"- {item}" for item in report.readiness_checks],
    ]
    if report.failure_reasons:
        lines.extend(["", "需要修复：", *[f"- {item}" for item in report.failure_reasons]])
    lines.extend(
        [
            "",
            "必须停下来问你的情况：",
            *[f"- {item}" for item in report.stop_conditions],
            "",
            "这次不会做什么：",
            *[f"- {item}" for item in report.non_actions],
        ]
    )
    return "\n".join(lines)


def render_authorization_json(decision: ChatAuthorizationDecision) -> str:
    return json.dumps(asdict(decision), ensure_ascii=False, indent=2)


def render_authorization_user(decision: ChatAuthorizationDecision) -> str:
    lines = [
        "聊天授权识别：",
        f"- 分类器版本：{decision.classifier_version}",
        f"- 输入：{decision.raw or '空'}",
        f"- 分类：{decision.category}",
        f"- 风险等级：{decision.risk_level}",
        f"- 授权范围：{decision.authorization_scope}",
        f"- 确认强度：{decision.confirmation_strength}",
        f"- 是否已授权：{'是' if decision.authorization_granted else '否'}",
        f"- 是否需要明确授权：{'是' if decision.requires_explicit_authorization else '否'}",
        f"- 是否可继续本地低风险动作：{'是' if decision.can_continue_locally else '否'}",
        f"- 命中标记：{', '.join(decision.matched_markers) if decision.matched_markers else '无'}",
        f"- 需要明确说出：{decision.required_explicit_phrase or '无'}",
        f"- 判断原因：{decision.reason}",
        "",
        "可以做：",
        *[f"- {item}" for item in decision.allowed_actions],
        "",
        "不能据此执行：",
        *[f"- {item}" for item in decision.blocked_actions],
    ]
    return "\n".join(lines)


def add_plan_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    parser.add_argument("--query", default="", help="Optional task keyword filter.")
    parser.add_argument("--stage", default="", help="Optional current-stage filter.")
    parser.add_argument("--limit", type=int, default=None, help="Maximum candidate tasks to inspect.")


def add_run_arguments(parser: argparse.ArgumentParser) -> None:
    add_plan_arguments(parser)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--dry-run", action="store_true", default=True, help="Preview allowed commands without running them.")
    mode_group.add_argument("--execute", action="store_false", dest="dry_run", help="Run allowlisted local verification commands.")
    parser.add_argument("--timeout-seconds", type=int, default=180, help="Per-command timeout.")
    parser.add_argument("--max-output-chars", type=int, default=1200, help="Tail length captured per stream.")
    parser.add_argument("--write-back", action="store_true", help="After a passed execute run, update the current stage in the active boundary.")
    parser.add_argument("--write-back-evidence", default="", help="Repo-relative evidence path required for --write-back.")
    parser.add_argument("--write-back-note", default="", help="Optional note written beside the stage evidence.")


def add_test_repair_loop_arguments(parser: argparse.ArgumentParser) -> None:
    add_plan_arguments(parser)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--dry-run", action="store_true", default=True, help="Preview the test-repair loop without running commands.")
    mode_group.add_argument("--execute", action="store_false", dest="dry_run", help="Run allowlisted local verification commands before analysis.")
    parser.add_argument("--timeout-seconds", type=int, default=180, help="Per-command timeout.")
    parser.add_argument("--max-output-chars", type=int, default=1200, help="Tail length captured per stream.")
    parser.add_argument("--max-local-repair-attempts", type=int, default=2, help="Maximum local repair attempts prescribed by the loop.")
    parser.add_argument("--failure-command", default="", help="Testing hook: simulate a failed command instead of running Verification.")
    parser.add_argument("--failure-returncode", type=int, default=1, help="Testing hook: simulated failure return code.")
    parser.add_argument("--failure-stdout", default="", help="Testing hook: simulated stdout tail.")
    parser.add_argument("--failure-stderr", default="", help="Testing hook: simulated stderr tail.")


def add_eng_review_arguments(parser: argparse.ArgumentParser) -> None:
    add_plan_arguments(parser)
    parser.add_argument("--evidence", default="", help="Optional repo-relative eng-review evidence path to check.")


def add_write_back_arguments(parser: argparse.ArgumentParser) -> None:
    add_plan_arguments(parser)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument("--dry-run", action="store_true", default=True, help="Preview stage write-back without editing the boundary.")
    mode_group.add_argument("--execute", action="store_false", dest="dry_run", help="Write the current stage back to the active boundary.")
    parser.add_argument("--evidence", required=True, help="Repo-relative evidence path required for stage write-back.")
    parser.add_argument("--note", default="", help="Optional note written beside the stage evidence.")
    parser.add_argument("--stage-key", default="", help="Optional guard; when passed it must match the selected current stage.")


def add_chat_smoke_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="user")
    parser.add_argument(
        "--raw-goal",
        default="用户用自然语言提出一个本地可验证的工程目标，Codex 完成需求、评审、实现、验证、QA evidence 和文档同步。",
        help="Natural-language goal used in the deterministic smoke scenario.",
    )


def add_natural_language_smoke_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="user")
    parser.add_argument(
        "--raw-request",
        default="我已经说清楚了，正式开工做一个项目看板，支持筛选、导出和多人验收",
        help="Natural-language request routed through the real nontechnical helper dry-run.",
    )
    parser.add_argument("--audience", default="运营同事", help="User audience passed to the nontechnical helper.")
    parser.add_argument("--success", default="能按时间范围和条目 筛选并导出", help="Success criterion passed to the nontechnical helper.")
    parser.add_argument("--non-goal", default="不改生产数据库", help="Non-goal passed to the nontechnical helper.")
    parser.add_argument("--topic", default="natural-language-loop-smoke", help="Topic used by formal kickoff dry-run.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command")
    plan_parser = subparsers.add_parser("plan", help="Render a read-only loop plan.")
    add_plan_arguments(plan_parser)
    run_parser = subparsers.add_parser("run", help="Run allowlisted local verification commands for the selected task.")
    add_run_arguments(run_parser)
    advance_parser = subparsers.add_parser("advance", help="Evaluate and optionally execute one safe stage transition.")
    add_run_arguments(advance_parser)
    eng_review_parser = subparsers.add_parser("eng-review", help="Generate or check eng-review decision evidence.")
    add_eng_review_arguments(eng_review_parser)
    subagents_parser = subparsers.add_parser("subagents", help="Render the subagent orchestration plan for the selected task.")
    add_plan_arguments(subagents_parser)
    repair_loop_parser = subparsers.add_parser("repair-loop", help="Render or run the test-repair loop protocol for the selected task.")
    add_test_repair_loop_arguments(repair_loop_parser)
    write_back_parser = subparsers.add_parser("write-back", help="Write the selected current stage back to the active boundary.")
    add_write_back_arguments(write_back_parser)
    authorize_parser = subparsers.add_parser("authorize", help="Classify chat authorization strength.")
    authorize_parser.add_argument("--raw", required=True, help="Raw chat text to classify.")
    authorize_parser.add_argument("--format", choices=("json", "user"), default="user")
    chat_smoke_parser = subparsers.add_parser("chat-smoke", help="Render an end-to-end chat-first loop smoke report.")
    add_chat_smoke_arguments(chat_smoke_parser)
    nl_smoke_parser = subparsers.add_parser("nl-smoke", help="Render a real-helper dry-run natural-language loop smoke report.")
    add_natural_language_smoke_arguments(nl_smoke_parser)
    add_plan_arguments(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command not in {None, "plan", "run", "advance", "eng-review", "subagents", "repair-loop", "write-back", "authorize", "chat-smoke", "nl-smoke"}:
        parser.error(f"Unsupported command: {args.command}")
    if args.command == "authorize":
        decision = chat_authorization_for(args.raw)
        if args.format == "json":
            print(render_authorization_json(decision))
        else:
            print(render_authorization_user(decision))
        return 0
    if args.command == "run":
        report = build_run_report(args)
        if args.format == "json":
            print(render_run_json(report))
        elif args.format == "user":
            print(render_run_user(report))
        else:
            print(render_run_markdown(report))
        return 1 if report.status == "failed" else 0
    if args.command == "advance":
        report = build_advance_report(args)
        if args.format == "json":
            print(render_advance_json(report))
        elif args.format == "user":
            print(render_advance_user(report))
        else:
            print(render_advance_markdown(report))
        return 1 if report.status == "failed" else 0
    if args.command == "eng-review":
        report = build_eng_review_report(args)
        if args.format == "json":
            print(render_eng_review_json(report))
        elif args.format == "user":
            print(render_eng_review_user(report))
        else:
            print(render_eng_review_markdown(report))
        return 0
    if args.command == "subagents":
        report = build_subagent_orchestration_report(args)
        if args.format == "json":
            print(render_subagent_orchestration_json(report))
        elif args.format == "user":
            print(render_subagent_orchestration_user(report))
        else:
            print(render_subagent_orchestration_markdown(report))
        return 0
    if args.command == "repair-loop":
        report = build_test_repair_loop_report(args)
        if args.format == "json":
            print(render_test_repair_loop_json(report))
        elif args.format == "user":
            print(render_test_repair_loop_user(report))
        else:
            print(render_test_repair_loop_markdown(report))
        return 1 if report.status == "blocked" else 0
    if args.command == "write-back":
        report = build_write_back_report(args)
        if args.format == "json":
            print(render_write_back_json(report))
        elif args.format == "user":
            print(render_write_back_user(report))
        else:
            print(render_write_back_markdown(report))
        return 1 if report.status == "refused" else 0
    if args.command == "chat-smoke":
        report = build_chat_first_loop_smoke_report(args.raw_goal)
        if args.format == "json":
            print(render_chat_first_loop_smoke_json(report))
        elif args.format == "user":
            print(render_chat_first_loop_smoke_user(report))
        else:
            print(render_chat_first_loop_smoke_markdown(report))
        return 0 if report.status == "ok" else 1
    if args.command == "nl-smoke":
        report = build_natural_language_loop_smoke_report(args)
        if args.format == "json":
            print(render_natural_language_loop_smoke_json(report))
        elif args.format == "user":
            print(render_natural_language_loop_smoke_user(report))
        else:
            print(render_natural_language_loop_smoke_markdown(report))
        return 0 if report.status == "ok" else 1
    plan = build_plan(args)
    if args.format == "json":
        print(render_json(plan))
    elif args.format == "user":
        print(render_user(plan))
    else:
        print(render_markdown(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
