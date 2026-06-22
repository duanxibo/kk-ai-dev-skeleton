#!/usr/bin/env python3
"""KK Dev Skeleton adapter installer helper.

This is a deterministic helper for Codex. Business users should keep using
natural-language requests; Codex calls this script internally to detect, plan,
dry-run, apply safe metadata scaffolding, verify, and report adapter readiness.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SCRIPT_PATH = Path(__file__).resolve()
SOURCE_REPO_ROOT = SCRIPT_PATH.parents[1]
REPO_ROOT = SOURCE_REPO_ROOT
DEFAULT_ADAPTER = REPO_ROOT / "adapters" / "default"
ACTIVE_BOUNDARY = REPO_ROOT / ".gstack" / "task-boundaries" / "CURRENT.local.md"
SKELETON_MARKER = ".gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md"

CORE_REQUIRED_PATHS = (
    "AGENTS.md",
    "README.md",
    "QUICK_START_FOR_PARTNERS.md",
    "COMPANY_ADOPTION_GUIDE.md",
    "CODEX_ADOPTION_CONNECTOR.md",
    ".gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md",
    ".gstack/README.md",
    ".gstack/knowledge/CODEMAP.md",
    ".gstack/knowledge/doc-placement.md",
    ".gstack/knowledge/ai-programming-framework.md",
    ".gstack/scripts/gstack_doctor.py",
    ".gstack/scripts/gstack_dashboard.py",
    ".gstack/scripts/gstack_loop.py",
    ".gstack/scripts/gstack_loop_contract_smoke.py",
    ".gstack/scripts/spec_sync_guard.py",
    ".gstack/scripts/natural_language_dev_smoke.py",
    "scripts/init_project.py",
    "adapters/default/adapter.md",
    "adapters/default/runtime.json",
)

ROOT_CODE_CANDIDATES = (
    "src",
    "app",
    "apps",
    "packages",
    "services",
    "backend",
    "frontend",
    "prisma",
    "e2e",
    "package.json",
    "pnpm-lock.yaml",
    "package-lock.json",
    "yarn.lock",
    "next.config.js",
    "next.config.mjs",
    "vite.config.js",
    "vite.config.ts",
    "docker-compose.yml",
    "docker-compose.yaml",
)

PROJECT_IMPLEMENTATION_CANDIDATES = (
    "src",
    "app",
    "apps",
    "packages",
    "services",
    "backend",
    "frontend",
    "prisma",
    "e2e",
    "tests",
    "scripts",
)

PROJECT_FORMAL_STACK_CANDIDATES = (
    "src",
    "app",
    "apps",
    "packages",
    "services",
    "backend",
    "frontend",
)

PROJECT_DOC_CANDIDATES = (
    "docs",
    "specs",
    ".gstack/knowledge",
    ".gstack/requirements",
)

PROJECT_DEMO_CANDIDATES = (
    "demo",
    "demos",
    "examples",
    "playground",
    "samples",
)

PROJECT_ARCHIVE_CANDIDATES = (
    "archive",
)

GENERIC_FORBIDDEN_PREFIXES = (
    ".env",
    ".env.",
    "node_modules/",
    "dist/",
    "build/",
    "target/",
    ".venv/",
    "__pycache__/",
)


DEFAULT_ADAPTER_MD = """# 默认项目 Adapter

这个 adapter 是模板。复制到 `adapters/<project-name>/adapter.md` 后，填入项目专属规则。
同目录下的 `runtime.json` 是机器可读配置，供 guard、doctor、dashboard 和 Loop runtime helper 判断路径、命令和 gate 触发规则。真实项目复制 adapter 后，必须同时改 `adapter.md` 和 `runtime.json`。

## 项目目标

- 说明这个项目要构建什么。
- 说明主要用户是谁。
- 说明第一个可见成功标准是什么。

## 真源文档

- 产品 spec：`stack/<project>/specs/`
- API 契约：`stack/<project>/specs/api/`
- 数据模型：`stack/<project>/specs/data/`
- UI 行为：`stack/<project>/specs/ui/`
- 测试口径：`stack/<project>/specs/testing/`
- 前置蓝图：`blueprint/`
- 历史归档：`archive/`
- 共享输入：`shared/`

根据你的项目调整这些路径。机器可读路径在 `adapters/default/runtime.json`。

## 实现路径

默认初始化会创建 `stack/<project>/`。如果真实项目已有 `src/`、`prisma/`、`e2e/`、`packages/`、`services/` 或其它根目录代码，不要让 Codex 静默接受散落一级目录的最终形态；先生成迁移计划，再分步迁入项目自己的正式实现路径。

推荐默认：

- 前端：`stack/<project>/src/frontend/`
- 后端：`stack/<project>/src/backend/`
- 脚本：`stack/<project>/scripts/`
- 测试：`stack/<project>/tests/`
- Fixtures：`stack/<project>/fixtures/`

## 命令

```bash
python3 scripts/init_project.py --adapter default --detect
python3 scripts/init_project.py --adapter default --plan
python3 scripts/init_project.py --adapter default --verify --report
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --apply --dry-run
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --apply
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --apply-core --dry-run
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --apply-core
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --apply-runtime --dry-run --report
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --apply-runtime --report
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --rewrite-adapter --dry-run
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --rewrite-adapter
python3 scripts/init_project.py --adapter default --validate-adapter --report
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --validate-adapter --report
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --verify --verify-core --report
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --verify-runtime --report
python3 scripts/init_project.py --adapter default --pilot --report
python3 scripts/init_project.py --adapter default --pilot --pilot-output /tmp/adapter-pilot --report
python3 .gstack/scripts/gstack_loop.py plan --format user
python3 .gstack/scripts/gstack_loop.py eng-review --format user
python3 .gstack/scripts/gstack_loop.py subagents --format user
python3 .gstack/scripts/gstack_loop.py repair-loop --dry-run --format user
python3 .gstack/scripts/gstack_loop.py write-back --dry-run --format user --evidence .gstack/scripts/gstack_loop.py
python3 .gstack/scripts/gstack_loop.py authorize --raw "继续做" --format user
python3 .gstack/scripts/gstack_loop.py chat-smoke --format user
python3 .gstack/scripts/gstack_loop.py nl-smoke --format user
python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user
python3 .gstack/scripts/gstack_doctor.py check
python3 .gstack/scripts/natural_language_dev_smoke.py --format user
python3 .gstack/scripts/spec_sync_guard.py
```

## Loop Runtime Capabilities

- Chat-first execution protocol for natural-language goals.
- Stage skill routing, stage state machine, controlled local verification, and explicit stage write-back.
- ENG review decisioner: Codex owns technical choices, users own business choices and high-risk authorization.
- Subagent orchestration protocol with checkpoint, deadline, retry, result schema, and evidence collection.
- Test-repair loop protocol: failure classification, local repair guidance, rerun order, and QA evidence policy.
- Chat authorization classifier for continue / confirmation / git / production / database / destructive scopes.
- `chat-smoke`, `nl-smoke`, and `gstack_loop_contract_smoke.py` for deterministic regression evidence.

## Forbidden Paths（禁止路径）

- `.env`
- `.env.*`
- `secrets/`
- 生产部署配置
- 生成的构建产物
- 真实客户数据
- 未经迁移计划批准的根目录业务代码移动
- 未经明确授权写入 `archive/` 的历史材料
- 未经脱敏或授权的 `shared/` 输入文件

## Runtime Bundle 策略

- `apply-core` 只创建缺失的 portable core 文件，保留目标项目已有文件。
- `apply-runtime` 是显式 opt-in：先确保 adapter metadata 和 portable core，再从 skeleton source checkout 复制 allowlisted runtime scripts。
- `verify-runtime` 检查 runtime script 文件、Python compile、Loop contract smoke、chat-smoke 和 nl-smoke。
- runtime bundle 不包含 data-access、SQL、ClickHouse、Metabase、生产、DB、凭证工具或具体项目业务 `stack/`。

## 数据和 API 规则

- 除非用户明确授权数据 scope，否则不要连接真实数据。
- 不要暴露密钥或原始敏感字段。
- 不要让前端代码依赖临时数据库查询。
- 实现前先定义 API 输入、输出、错误、空态和授权行为。

## 发布规则

- Git workflow actions 必须获得用户明确批准。
- 生产部署必须获得用户明确批准。
- 回滚必须获得用户明确批准，并且要有具体目标。

## Required Gates（必要门禁）

只在相关时使用 gates：

- `data-access`
- `data-query`
- `prototype-logic-extraction`
- `subagent-plan`
- `doc-backfill`
- `data-knowledge-sync`
- `ui-interaction-qa`

如果某个 gate 不需要，在 task boundary 中记录原因。
"""


LOOP_RUNTIME_CAPABILITIES = (
    "chat-first-protocol",
    "stage-skill-routing",
    "eng-review-decisioner",
    "stage-write-back-closure",
    "subagent-timeout-policy",
    "subagent-orchestration",
    "controlled-local-runner",
    "test-repair-loop",
    "chat-authorization-classifier",
    "chat-first-smoke",
    "natural-language-kickoff-smoke",
    "loop-contract-smoke",
)

LOOP_REQUIRED_COMMAND_KEYS = (
    "loop_plan",
    "loop_eng_review",
    "loop_subagents",
    "loop_repair_dry_run",
    "loop_write_back_dry_run",
    "loop_authorize_continue",
    "loop_authorize_git",
    "loop_chat_smoke",
    "loop_nl_smoke",
    "loop_contract_smoke",
)

RUNTIME_BUNDLE_FILES = (
    ".gstack/scripts/autopilot_bootstrap.py",
    ".gstack/scripts/codex_mode.py",
    ".gstack/scripts/gstack_dashboard.py",
    ".gstack/scripts/gstack_doctor.py",
    ".gstack/scripts/gstack_loop.py",
    ".gstack/scripts/gstack_loop_contract_smoke.py",
    ".gstack/scripts/natural_language_dev_smoke.py",
    ".gstack/scripts/nontechnical_acceptance_plan.py",
    ".gstack/scripts/nontechnical_ci_failure.py",
    ".gstack/scripts/nontechnical_confirmation_brief.py",
    ".gstack/scripts/nontechnical_confirmation_response.py",
    ".gstack/scripts/nontechnical_continue.py",
    ".gstack/scripts/nontechnical_delivery_summary.py",
    ".gstack/scripts/nontechnical_execution_plan.py",
    ".gstack/scripts/nontechnical_first_use.py",
    ".gstack/scripts/nontechnical_formal_kickoff.py",
    ".gstack/scripts/nontechnical_guided_kickoff.py",
    ".gstack/scripts/nontechnical_home.py",
    ".gstack/scripts/nontechnical_implementation_readiness.py",
    ".gstack/scripts/nontechnical_intake.py",
    ".gstack/scripts/nontechnical_intent_router.py",
    ".gstack/scripts/nontechnical_mode_control.py",
    ".gstack/scripts/nontechnical_next_step.py",
    ".gstack/scripts/nontechnical_page_change_brief.py",
    ".gstack/scripts/nontechnical_pause.py",
    ".gstack/scripts/nontechnical_recommendation.py",
    ".gstack/scripts/nontechnical_requirement_brief.py",
    ".gstack/scripts/nontechnical_requirement_readiness.py",
    ".gstack/scripts/nontechnical_scope_change.py",
    ".gstack/scripts/nontechnical_task_list.py",
    ".gstack/scripts/nontechnical_task_starter.py",
    ".gstack/scripts/nontechnical_team_sync.py",
    ".gstack/scripts/nontechnical_undo_request.py",
    ".gstack/scripts/nontechnical_visible_change.py",
    ".gstack/scripts/required_gates_audit.py",
    ".gstack/scripts/rule_manager.py",
    ".gstack/scripts/spec_sync_guard.py",
    ".gstack/scripts/team_flow_guard.py",
    ".gstack/scripts/use_boundary.sh",
)

RUNTIME_BUNDLE_PYTHON_FILES = tuple(
    path for path in RUNTIME_BUNDLE_FILES if path.endswith(".py")
)


def loop_runtime_commands() -> dict[str, list[str]]:
    return {
        "loop_plan": ["python3", ".gstack/scripts/gstack_loop.py", "plan", "--format", "user"],
        "loop_plan_json": ["python3", ".gstack/scripts/gstack_loop.py", "plan", "--format", "json"],
        "loop_run_dry_run": ["python3", ".gstack/scripts/gstack_loop.py", "run", "--dry-run", "--format", "user"],
        "loop_advance_dry_run": ["python3", ".gstack/scripts/gstack_loop.py", "advance", "--dry-run", "--format", "user"],
        "loop_eng_review": ["python3", ".gstack/scripts/gstack_loop.py", "eng-review", "--format", "user"],
        "loop_subagents": ["python3", ".gstack/scripts/gstack_loop.py", "subagents", "--format", "user"],
        "loop_repair_dry_run": ["python3", ".gstack/scripts/gstack_loop.py", "repair-loop", "--dry-run", "--format", "user"],
        "loop_write_back_dry_run": [
            "python3",
            ".gstack/scripts/gstack_loop.py",
            "write-back",
            "--dry-run",
            "--format",
            "user",
            "--evidence",
            ".gstack/scripts/gstack_loop.py",
        ],
        "loop_authorize_continue": ["python3", ".gstack/scripts/gstack_loop.py", "authorize", "--raw", "继续做", "--format", "user"],
        "loop_authorize_git": ["python3", ".gstack/scripts/gstack_loop.py", "authorize", "--raw", "提交并推送", "--format", "json"],
        "loop_chat_smoke": ["python3", ".gstack/scripts/gstack_loop.py", "chat-smoke", "--format", "user"],
        "loop_nl_smoke": ["python3", ".gstack/scripts/gstack_loop.py", "nl-smoke", "--format", "user"],
        "loop_contract_smoke": ["python3", ".gstack/scripts/gstack_loop_contract_smoke.py", "--format", "user"],
    }


def loop_runtime_section() -> dict[str, Any]:
    return {
        "runtime_version": "loop-v15-natural-language-runtime",
        "schema_version": "11",
        "capabilities": list(LOOP_RUNTIME_CAPABILITIES),
        "default_flow": [
            "requirement-brief",
            "plan-ceo-review",
            "requirement-freeze",
            "plan-eng-review",
            "domain-spec-readiness",
            "implement",
            "qa",
        ],
        "codex_autonomous_actions": [
            "requirement drafting after semantic review",
            "engineering design and implementation choices inside active boundary",
            "test command selection",
            "subagent strategy selection",
            "gate recovery for locally provable evidence",
            "QA evidence drafting after real verification",
            "documentation sync for changed behavior or contracts",
        ],
        "user_decision_boundary": {
            "ask_user_for": [
                "business scope",
                "product or design multi-choice decisions",
                "real data access",
                "production operations",
                "database schema or real-data writes",
                "destructive commands",
                "git workflow authorization",
            ],
            "do_not_ask_user_for": [
                "code structure",
                "test command selection",
                "subagent role selection",
                "gate recovery order",
                "implementation strategy",
            ],
        },
    }


def online_flow_protocol_section() -> dict[str, Any]:
    return {
        "protocol_version": "online-flow-v1",
        "status": "supported",
        "design_doc": ".gstack/designs/2026-06-22_online-software-factory-platform-protocol.md",
        "platform_role": [
            "collect demand, attachments, acceptance method, non-goals, and risk flags",
            "manage PRD, architecture, acceptance, status display, and authorization events",
            "generate revisioned ClaimPackage objects for a controlled Codex runner",
            "display StatusEvent summaries without replacing repo-native evidence",
        ],
        "runner_role": [
            "validate claim revision, checksum, adapter, and authorization boundary",
            "create or update requirement, review, task boundary, Required Gates, and QA evidence",
            "implement and verify only inside the active boundary",
            "write StatusEvent updates for progress, blockers, QA, and delivery summaries",
        ],
        "repo_role": [
            "preserve requirement, review, boundary, QA, decision, and learning evidence",
            "provide adapter paths, verification commands, forbidden scopes, and Required Gates",
            "provide explicit runtime bundle smoke and guard checks",
        ],
        "objects": [
            "OnlineDemand",
            "MvpConfirmation",
            "ClaimPackage",
            "StatusEvent",
            "QaResult",
            "DeliverySummary",
            "PostLaunchFeedback",
        ],
        "status_machine": [
            "draft",
            "needs-triage",
            "mvp-confirming",
            "ready-for-codex",
            "claimed",
            "kickoff-prepared",
            "in-development",
            "qa",
            "ready-for-acceptance",
            "accepted",
            "done",
        ],
        "side_states": [
            "needs-user-confirmation",
            "blocked",
            "deferred",
            "cancelled",
            "reopened",
        ],
        "evidence_mapping": {
            "OnlineDemand": ".gstack/requirements/",
            "MvpConfirmation": ".gstack/requirements/ and .gstack/reviews/",
            "ClaimPackage": ".gstack/task-boundaries/",
            "StatusEvent": "boundary stage, review, or QA summary",
            "QaResult": ".gstack/qa-reports/",
            "DeliverySummary": ".gstack/qa-reports/ plus platform delivery note",
            "PostLaunchFeedback": "new OnlineDemand or reopened demand",
        },
        "default_authorization": [
            "repo evidence preparation",
            "active-boundary local implementation",
            "local verification",
            "QA and delivery summary generation",
        ],
        "requires_separate_authorization": [
            "git workflow action",
            "branch create or switch",
            "commit, amend, squash, rebase, merge, pull, push, or pull request",
            "staging or production deployment",
            "production operation or rollback",
            "database schema change or real-data write",
            "destructive command",
            "external paid service call",
        ],
        "non_actions": [
            "does not implement the web platform",
            "does not run a cloud runner by itself",
            "does not store secrets or production credentials",
            "does not replace repo-native evidence with platform state",
            "does not grant high-risk authorization from ambiguous confirmation",
        ],
    }


def authorization_section() -> dict[str, Any]:
    return {
        "classifier_version": "chat-authorization-v2",
        "ambiguous_confirmation_does_not_authorize": [
            "git workflow",
            "production",
            "database",
            "real-data write",
            "destructive command",
        ],
        "requires_explicit_authorization": [
            "commit",
            "amend",
            "branch switch or creation",
            "pull",
            "push",
            "merge",
            "pull request",
            "deploy",
            "production restart or rollback",
            "database schema change",
            "real-data write",
            "destructive command",
        ],
        "forbidden_scope_markers": [
            "不要提交",
            "不推送",
            "不改数据库",
            "别上线",
        ],
    }


def smoke_tests_section() -> dict[str, Any]:
    return {
        "loop_contract_smoke": ["python3", ".gstack/scripts/gstack_loop_contract_smoke.py", "--format", "user"],
        "chat_smoke": ["python3", ".gstack/scripts/gstack_loop.py", "chat-smoke", "--format", "user"],
        "natural_language_loop_smoke": ["python3", ".gstack/scripts/gstack_loop.py", "nl-smoke", "--format", "user"],
        "natural_language_dev_smoke": ["python3", ".gstack/scripts/natural_language_dev_smoke.py", "--format", "user"],
    }


def runtime_bundle_section() -> dict[str, Any]:
    return {
        "bundle_version": 1,
        "mode": "explicit-copy",
        "source": "skeleton-source-repo",
        "write_policy": "create-missing-preserve-existing",
        "apply_command": ["python3", "scripts/init_project.py", "--adapter", "default", "--apply-runtime"],
        "verify_command": ["python3", "scripts/init_project.py", "--adapter", "default", "--verify-runtime", "--report"],
        "files": list(RUNTIME_BUNDLE_FILES),
        "excluded_by_default": [
            "stack/**",
            "archive/**",
            "blueprint/**",
            "shared/**",
            ".gstack/data-access/**",
            "data source, SQL, production, database, and credential helpers",
        ],
        "required_smoke_commands": [
            ["python3", ".gstack/scripts/gstack_loop_contract_smoke.py", "--format", "user"],
            ["python3", ".gstack/scripts/gstack_loop.py", "chat-smoke", "--format", "user"],
            ["python3", ".gstack/scripts/gstack_loop.py", "nl-smoke", "--format", "user"],
        ],
        "source_extended_smoke_commands": [
            ["python3", ".gstack/scripts/natural_language_dev_smoke.py", "--format", "user"],
        ],
        "non_goals": [
            "Does not install a background service, dashboard daemon, production connector, database tool, or git automation.",
            "Does not overwrite existing target runtime scripts by default.",
            "Does not copy project business stack, archive, blueprint, shared data, credentials, or data-access helpers.",
        ],
    }


def evidence_policy_section() -> dict[str, Any]:
    return {
        "repo_native_dirs": [
            ".gstack/requirements/",
            ".gstack/reviews/",
            ".gstack/task-boundaries/",
            ".gstack/qa-reports/",
            ".gstack/decisions/",
            ".gstack/learnings/",
        ],
        "qa_requires_real_verification": True,
        "eng_review_required_markers": [
            "AI 语义复核: yes",
            "## Codex 自主工程决策",
            "## 用户决策边界",
            "## 防技术甩锅检查",
            "## 验证计划",
        ],
        "stage_write_back_requires_existing_evidence": True,
    }


def loop_non_actions() -> list[str]:
    return [
        "does not run as a background service",
        "does not overwrite target project files by default",
        "does not connect to production systems",
        "does not connect to real databases",
        "does not write real data",
        "does not execute destructive commands",
        "does not perform git workflow actions without explicit user authorization",
        "does not mark QA passed without real verification",
    ]


DEFAULT_RUNTIME: dict[str, Any] = json.loads(
    r'''
{
  "version": 7,
  "name": "default",
  "description": "默认项目 adapter 的机器可读运行配置，包含 portable core、Loop runtime V15 contract 和 explicit runtime bundle install。真实项目应复制 adapters/default 后改写本文件。",
  "paths": {
    "collaboration_root": ".gstack/",
    "boundary_prefix": ".gstack/task-boundaries/",
    "requirement_prefix": ".gstack/requirements/",
    "review_prefix": ".gstack/reviews/",
    "ceo_review_prefix": ".gstack/reviews/",
    "eng_review_prefix": ".gstack/reviews/",
    "qa_prefix": ".gstack/qa-reports/",
    "design_prefix": ".gstack/designs/",
    "decision_prefix": ".gstack/decisions/",
    "learning_prefix": ".gstack/learnings/",
    "formal_stack_prefixes": [
      "stack/default/"
    ],
    "domain_spec_prefixes": [
      "stack/default/specs/"
    ],
    "implementation_prefixes": [
      "stack/default/src/",
      "stack/default/scripts/",
      "stack/default/tests/",
      "stack/default/fixtures/"
    ],
    "spec_prefixes": [
      "stack/default/specs/"
    ],
    "prototype_prefixes": [
      "archive/baseline/example-baseline/app/",
      "archive/baseline/example-baseline/scripts/",
      "archive/baseline/example-baseline/templates/",
      "archive/baseline/example-baseline/seeds/"
    ],
    "backend_implementation_prefixes": [
      "stack/default/src/backend/",
      "stack/default/src/server/"
    ],
    "backend_test_prefixes": [
      "stack/default/tests/backend/",
      "stack/default/tests/"
    ],
    "backend_domain_spec_prefix": "stack/default/specs/",
    "deprecated_backend_spec_prefixes": [
      "docs/specs/archive/backend-legacy/"
    ],
    "domain_spec_prefix": "stack/default/specs/",
    "data_access_trigger_prefixes": [
      "stack/default/src/",
      "stack/default/specs/",
      ".gstack/templates/data-interface-design.template.md",
      ".gstack/knowledge/data-access/source-registry.md",
      ".gstack/knowledge/data-access/sources/",
      ".gstack/knowledge/data-access/sql-drafts/",
      ".gstack/knowledge/data-access/requirement-gaps/"
    ],
    "frontend_hint_prefixes": [
      "stack/default/src/frontend/",
      "stack/default/src/app/",
      "archive/baseline/example-baseline/app/"
    ],
    "prototype_logic_evidence_prefixes": [
      ".gstack/designs/",
      ".gstack/reviews/",
      ".gstack/knowledge/",
      ".gstack/knowledge/data-access/",
      "stack/default/",
      "archive/baseline/",
      "baseline/"
    ],
    "demo_prefixes": [
      "examples/"
    ],
    "archive_prefixes": [
      "archive/",
      "archive/baseline/"
    ],
    "forbidden_default_prefixes": [
      ".env",
      ".env.",
      "secrets/",
      "node_modules/",
      "dist/",
      "build/",
      "target/",
      ".venv/",
      "__pycache__/"
    ],
    "migration_candidate_prefixes": [
      "src/",
      "app/",
      "prisma/",
      "e2e/",
      "apps/",
      "packages/",
      "services/",
      "backend/",
      "frontend/"
    ]
  },
  "commands": {
    "detect": [
      "python3",
      "scripts/init_project.py",
      "--adapter",
      "default",
      "--detect"
    ],
    "plan": [
      "python3",
      "scripts/init_project.py",
      "--adapter",
      "default",
      "--plan"
    ],
    "verify": [
      "python3",
      "scripts/init_project.py",
      "--adapter",
      "default",
      "--verify",
      "--report"
    ],
    "target_apply_dry_run": [
      "python3",
      "scripts/init_project.py",
      "--repo-root",
      "<repo-root>",
      "--adapter",
      "default",
      "--apply",
      "--dry-run"
    ],
    "target_apply": [
      "python3",
      "scripts/init_project.py",
      "--repo-root",
      "<repo-root>",
      "--adapter",
      "default",
      "--apply"
    ],
    "target_apply_core_dry_run": [
      "python3",
      "scripts/init_project.py",
      "--repo-root",
      "<repo-root>",
      "--project-name",
      "<project-name>",
      "--adapter",
      "default",
      "--apply-core",
      "--dry-run"
    ],
    "target_apply_core": [
      "python3",
      "scripts/init_project.py",
      "--repo-root",
      "<repo-root>",
      "--project-name",
      "<project-name>",
      "--adapter",
      "default",
      "--apply-core"
    ],
    "target_apply_runtime_dry_run": [
      "python3",
      "scripts/init_project.py",
      "--repo-root",
      "<repo-root>",
      "--adapter",
      "default",
      "--apply-runtime",
      "--dry-run",
      "--report"
    ],
    "target_apply_runtime": [
      "python3",
      "scripts/init_project.py",
      "--repo-root",
      "<repo-root>",
      "--adapter",
      "default",
      "--apply-runtime",
      "--report"
    ],
    "target_verify_runtime": [
      "python3",
      "scripts/init_project.py",
      "--repo-root",
      "<repo-root>",
      "--adapter",
      "default",
      "--verify-runtime",
      "--report"
    ],
    "target_rewrite_adapter_dry_run": [
      "python3",
      "scripts/init_project.py",
      "--repo-root",
      "<repo-root>",
      "--project-name",
      "<project-name>",
      "--adapter",
      "default",
      "--rewrite-adapter",
      "--dry-run"
    ],
    "target_rewrite_adapter": [
      "python3",
      "scripts/init_project.py",
      "--repo-root",
      "<repo-root>",
      "--project-name",
      "<project-name>",
      "--adapter",
      "default",
      "--rewrite-adapter"
    ],
    "validate": [
      "python3",
      "scripts/init_project.py",
      "--adapter",
      "default",
      "--validate-adapter",
      "--report"
    ],
    "target_validate_adapter": [
      "python3",
      "scripts/init_project.py",
      "--repo-root",
      "<repo-root>",
      "--adapter",
      "default",
      "--validate-adapter",
      "--report"
    ],
    "target_verify_core": [
      "python3",
      "scripts/init_project.py",
      "--repo-root",
      "<repo-root>",
      "--adapter",
      "default",
      "--verify",
      "--verify-core",
      "--report"
    ],
    "pilot": [
      "python3",
      "scripts/init_project.py",
      "--adapter",
      "default",
      "--pilot",
      "--report"
    ],
    "pilot_output": [
      "python3",
      "scripts/init_project.py",
      "--adapter",
      "default",
      "--pilot",
      "--pilot-output",
      "<empty-dir>",
      "--report"
    ],
    "loop_plan": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "plan",
      "--format",
      "user"
    ],
    "loop_plan_json": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "plan",
      "--format",
      "json"
    ],
    "loop_run_dry_run": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "run",
      "--dry-run",
      "--format",
      "user"
    ],
    "loop_advance_dry_run": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "advance",
      "--dry-run",
      "--format",
      "user"
    ],
    "loop_eng_review": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "eng-review",
      "--format",
      "user"
    ],
    "loop_subagents": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "subagents",
      "--format",
      "user"
    ],
    "loop_repair_dry_run": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "repair-loop",
      "--dry-run",
      "--format",
      "user"
    ],
    "loop_write_back_dry_run": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "write-back",
      "--dry-run",
      "--format",
      "user",
      "--evidence",
      ".gstack/scripts/gstack_loop.py"
    ],
    "loop_authorize_continue": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "authorize",
      "--raw",
      "继续做",
      "--format",
      "user"
    ],
    "loop_authorize_git": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "authorize",
      "--raw",
      "提交并推送",
      "--format",
      "json"
    ],
    "loop_chat_smoke": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "chat-smoke",
      "--format",
      "user"
    ],
    "loop_nl_smoke": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "nl-smoke",
      "--format",
      "user"
    ],
    "loop_contract_smoke": [
      "python3",
      ".gstack/scripts/gstack_loop_contract_smoke.py",
      "--format",
      "user"
    ],
    "doctor": [
      "python3",
      ".gstack/scripts/gstack_doctor.py",
      "check"
    ],
    "dashboard": [
      "python3",
      ".gstack/scripts/gstack_dashboard.py",
      "show"
    ],
    "natural_language_smoke": [
      "python3",
      ".gstack/scripts/natural_language_dev_smoke.py",
      "--format",
      "user"
    ],
    "spec_sync": [
      "python3",
      ".gstack/scripts/spec_sync_guard.py"
    ]
  },
  "gates": {
    "data_access_status_requirements": [
      {
        "prefixes": [
          "stack/default/src/backend/",
          "stack/default/src/server/"
        ],
        "statuses": [
          "done",
          "blocked",
          "deferred"
        ],
        "reason": "business data implementation paths require `data-access` done / blocked / deferred"
      },
      {
        "prefixes": [
          "stack/default/specs/"
        ],
        "statuses": [
          "done",
          "not-required"
        ],
        "reason": "interface/spec/data docs require `data-access` done or reasoned not-required"
      },
      {
        "prefixes": [
          "stack/default/src/frontend/",
          "stack/default/src/app/"
        ],
        "statuses": [
          "done",
          "not-required",
          "blocked",
          "deferred"
        ],
        "reason": "frontend data wiring requires `data-access` evidence or reasoned not-required"
      },
      {
        "prefixes": [
          ".gstack/templates/data-interface-design.template.md"
        ],
        "statuses": [
          "done",
          "planned"
        ],
        "reason": "data-interface design changes require `data-access` done or planned"
      }
    ],
    "data-access": "Use when a task touches real data, source systems, API contracts, metrics, SQL, or data scope.",
    "prototype-logic-extraction": "Use when backend/service code takes over existing frontend, fixture, mock, or prototype logic.",
    "ui-interaction-qa": "Use when UI, HTML, dashboard, or visualization behavior changes."
  },
  "loop_runtime": {
    "runtime_version": "loop-v15-natural-language-runtime",
    "schema_version": "11",
    "capabilities": [
      "chat-first-protocol",
      "stage-skill-routing",
      "eng-review-decisioner",
      "stage-write-back-closure",
      "subagent-timeout-policy",
      "subagent-orchestration",
      "controlled-local-runner",
      "test-repair-loop",
      "chat-authorization-classifier",
      "chat-first-smoke",
      "natural-language-kickoff-smoke",
      "loop-contract-smoke"
    ],
    "default_flow": [
      "requirement-brief",
      "plan-review",
      "requirement-freeze",
      "engineering-review",
      "source-of-truth-readiness",
      "implementation",
      "qa"
    ],
    "codex_autonomous_actions": [
      "requirement drafting after semantic review",
      "engineering design and implementation choices inside active boundary",
      "test command selection",
      "subagent strategy selection",
      "gate recovery for locally provable evidence",
      "QA evidence drafting after real verification",
      "documentation sync for changed behavior or contracts"
    ],
    "user_decision_boundary": {
      "ask_user_for": [
        "business scope",
        "product or design multi-choice decisions",
        "real data access",
        "production operations",
        "database schema or real-data writes",
        "destructive commands",
        "git workflow authorization"
      ],
      "do_not_ask_user_for": [
        "code structure",
        "test command selection",
        "subagent role selection",
        "gate recovery order",
        "implementation strategy"
      ]
    }
  },
  "online_flow_protocol": {
    "protocol_version": "online-flow-v1",
    "status": "supported",
    "design_doc": ".gstack/designs/2026-06-22_online-software-factory-platform-protocol.md",
    "platform_role": [
      "collect demand, attachments, acceptance method, non-goals, and risk flags",
      "manage PRD, architecture, acceptance, status display, and authorization events",
      "generate revisioned ClaimPackage objects for a controlled Codex runner",
      "display StatusEvent summaries without replacing repo-native evidence"
    ],
    "runner_role": [
      "validate claim revision, checksum, adapter, and authorization boundary",
      "create or update requirement, review, task boundary, Required Gates, and QA evidence",
      "implement and verify only inside the active boundary",
      "write StatusEvent updates for progress, blockers, QA, and delivery summaries"
    ],
    "repo_role": [
      "preserve requirement, review, boundary, QA, decision, and learning evidence",
      "provide adapter paths, verification commands, forbidden scopes, and Required Gates",
      "provide explicit runtime bundle smoke and guard checks"
    ],
    "objects": [
      "OnlineDemand",
      "MvpConfirmation",
      "ClaimPackage",
      "StatusEvent",
      "QaResult",
      "DeliverySummary",
      "PostLaunchFeedback"
    ],
    "status_machine": [
      "draft",
      "needs-triage",
      "mvp-confirming",
      "ready-for-codex",
      "claimed",
      "kickoff-prepared",
      "in-development",
      "qa",
      "ready-for-acceptance",
      "accepted",
      "done"
    ],
    "side_states": [
      "needs-user-confirmation",
      "blocked",
      "deferred",
      "cancelled",
      "reopened"
    ],
    "evidence_mapping": {
      "OnlineDemand": ".gstack/requirements/",
      "MvpConfirmation": ".gstack/requirements/ and .gstack/reviews/",
      "ClaimPackage": ".gstack/task-boundaries/",
      "StatusEvent": "boundary stage, review, or QA summary",
      "QaResult": ".gstack/qa-reports/",
      "DeliverySummary": ".gstack/qa-reports/ plus platform delivery note",
      "PostLaunchFeedback": "new OnlineDemand or reopened demand"
    },
    "default_authorization": [
      "repo evidence preparation",
      "active-boundary local implementation",
      "local verification",
      "QA and delivery summary generation"
    ],
    "requires_separate_authorization": [
      "git workflow action",
      "branch create or switch",
      "commit, amend, squash, rebase, merge, pull, push, or pull request",
      "staging or production deployment",
      "production operation or rollback",
      "database schema change or real-data write",
      "destructive command",
      "external paid service call"
    ],
    "non_actions": [
      "does not implement the web platform",
      "does not run a cloud runner by itself",
      "does not store secrets or production credentials",
      "does not replace repo-native evidence with platform state",
      "does not grant high-risk authorization from ambiguous confirmation"
    ]
  },
  "runtime_bundle": {
    "bundle_version": 1,
    "mode": "explicit-copy",
    "source": "skeleton-source-repo",
    "write_policy": "create-missing-preserve-existing",
    "apply_command": [
      "python3",
      "scripts/init_project.py",
      "--adapter",
      "default",
      "--apply-runtime"
    ],
    "verify_command": [
      "python3",
      "scripts/init_project.py",
      "--adapter",
      "default",
      "--verify-runtime",
      "--report"
    ],
    "files": [
      ".gstack/scripts/autopilot_bootstrap.py",
      ".gstack/scripts/codex_mode.py",
      ".gstack/scripts/gstack_dashboard.py",
      ".gstack/scripts/gstack_doctor.py",
      ".gstack/scripts/gstack_loop.py",
      ".gstack/scripts/gstack_loop_contract_smoke.py",
      ".gstack/scripts/natural_language_dev_smoke.py",
      ".gstack/scripts/nontechnical_acceptance_plan.py",
      ".gstack/scripts/nontechnical_ci_failure.py",
      ".gstack/scripts/nontechnical_confirmation_brief.py",
      ".gstack/scripts/nontechnical_confirmation_response.py",
      ".gstack/scripts/nontechnical_continue.py",
      ".gstack/scripts/nontechnical_delivery_summary.py",
      ".gstack/scripts/nontechnical_execution_plan.py",
      ".gstack/scripts/nontechnical_first_use.py",
      ".gstack/scripts/nontechnical_formal_kickoff.py",
      ".gstack/scripts/nontechnical_guided_kickoff.py",
      ".gstack/scripts/nontechnical_home.py",
      ".gstack/scripts/nontechnical_implementation_readiness.py",
      ".gstack/scripts/nontechnical_intake.py",
      ".gstack/scripts/nontechnical_intent_router.py",
      ".gstack/scripts/nontechnical_mode_control.py",
      ".gstack/scripts/nontechnical_next_step.py",
      ".gstack/scripts/nontechnical_page_change_brief.py",
      ".gstack/scripts/nontechnical_pause.py",
      ".gstack/scripts/nontechnical_recommendation.py",
      ".gstack/scripts/nontechnical_requirement_brief.py",
      ".gstack/scripts/nontechnical_requirement_readiness.py",
      ".gstack/scripts/nontechnical_scope_change.py",
      ".gstack/scripts/nontechnical_task_list.py",
      ".gstack/scripts/nontechnical_task_starter.py",
      ".gstack/scripts/nontechnical_team_sync.py",
      ".gstack/scripts/nontechnical_undo_request.py",
      ".gstack/scripts/nontechnical_visible_change.py",
      ".gstack/scripts/required_gates_audit.py",
      ".gstack/scripts/rule_manager.py",
      ".gstack/scripts/spec_sync_guard.py",
      ".gstack/scripts/team_flow_guard.py",
      ".gstack/scripts/use_boundary.sh"
    ],
    "excluded_by_default": [
      "stack/**",
      "archive/**",
      "blueprint/**",
      "shared/**",
      ".gstack/data-access/**",
      "data source, SQL, production, database, and credential helpers"
    ],
    "required_smoke_commands": [
      [
        "python3",
        ".gstack/scripts/gstack_loop_contract_smoke.py",
        "--format",
        "user"
      ],
      [
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "chat-smoke",
        "--format",
        "user"
      ],
      [
        "python3",
        ".gstack/scripts/gstack_loop.py",
        "nl-smoke",
        "--format",
        "user"
      ]
    ],
    "source_extended_smoke_commands": [
      [
        "python3",
        ".gstack/scripts/natural_language_dev_smoke.py",
        "--format",
        "user"
      ]
    ],
    "non_goals": [
      "Does not install a background service, dashboard daemon, production connector, database tool, or git automation.",
      "Does not overwrite existing target runtime scripts by default.",
      "Does not copy project business stack, archive, blueprint, shared data, credentials, or data-access helpers."
    ]
  },
  "authorization": {
    "classifier_version": "chat-authorization-v2",
    "ambiguous_confirmation_does_not_authorize": [
      "git workflow",
      "production",
      "database",
      "real-data write",
      "destructive command"
    ],
    "requires_explicit_authorization": [
      "commit",
      "amend",
      "branch switch or creation",
      "pull",
      "push",
      "merge",
      "pull request",
      "deploy",
      "production restart or rollback",
      "database schema change",
      "real-data write",
      "destructive command"
    ],
    "forbidden_scope_markers": [
      "不要提交",
      "不推送",
      "不改数据库",
      "别上线"
    ]
  },
  "smoke_tests": {
    "loop_contract_smoke": [
      "python3",
      ".gstack/scripts/gstack_loop_contract_smoke.py",
      "--format",
      "user"
    ],
    "chat_smoke": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "chat-smoke",
      "--format",
      "user"
    ],
    "natural_language_loop_smoke": [
      "python3",
      ".gstack/scripts/gstack_loop.py",
      "nl-smoke",
      "--format",
      "user"
    ],
    "natural_language_dev_smoke": [
      "python3",
      ".gstack/scripts/natural_language_dev_smoke.py",
      "--format",
      "user"
    ]
  },
  "evidence_policy": {
    "repo_native_dirs": [
      ".gstack/requirements/",
      ".gstack/reviews/",
      ".gstack/task-boundaries/",
      ".gstack/qa-reports/",
      ".gstack/decisions/",
      ".gstack/learnings/"
    ],
    "qa_requires_real_verification": true,
    "eng_review_required_markers": [
      "AI 语义复核: yes",
      "## Codex 自主工程决策",
      "## 用户决策边界",
      "## 防技术甩锅检查",
      "## 验证计划"
    ],
    "stage_write_back_requires_existing_evidence": true
  },
  "non_actions": [
    "does not run as a background service",
    "does not overwrite target project files by default",
    "does not connect to production systems",
    "does not connect to real databases",
    "does not write real data",
    "does not execute destructive commands",
    "does not perform git workflow actions without explicit user authorization",
    "does not mark QA passed without real verification"
  ]
}
'''
)

PORTABLE_CORE_FILES = (
    "AGENTS.md",
    "README.md",
    ".gstack/README.md",
    ".gstack/knowledge/CODEMAP.md",
    ".gstack/knowledge/doc-placement.md",
    ".gstack/knowledge/ai-programming-framework.md",
    ".gstack/scripts/README.md",
    ".gstack/task-boundaries/CURRENT.md",
    ".gstack/requirements/README.md",
    ".gstack/reviews/README.md",
    ".gstack/qa-reports/README.md",
    "scripts/init_project.py",
    "adapters/default/core_manifest.json",
    "adapters/default/runtime_schema.json",
)

PORTABLE_CORE_REQUIRED_PATHS = (
    *PORTABLE_CORE_FILES,
    "adapters/default/adapter.md",
    "adapters/default/runtime.json",
)


def core_manifest_payload() -> dict[str, Any]:
    return {
        "version": 3,
        "name": "portable-core",
        "description": "Minimal portable collaboration core for target repositories with Loop runtime contract metadata.",
        "write_policy": "create-missing-preserve-existing",
        "files": [
            {
                "path": path,
                "mode": "create-if-missing",
            }
            for path in PORTABLE_CORE_FILES
        ],
        "loop_runtime_contract": {
            "version": "loop-v15-natural-language-runtime",
            "capabilities": list(LOOP_RUNTIME_CAPABILITIES),
            "required_command_keys": list(LOOP_REQUIRED_COMMAND_KEYS),
            "metadata_sections": [
                "loop_runtime",
                "online_flow_protocol",
                "runtime_bundle",
                "authorization",
                "smoke_tests",
                "evidence_policy",
                "non_actions",
            ],
        },
        "runtime_bundle_policy": {
            "mode": "metadata-first-plus-explicit-runtime-copy",
            "apply_command": "python3 scripts/init_project.py --adapter default --apply-runtime",
            "verify_command": "python3 scripts/init_project.py --adapter default --verify-runtime --report",
            "files": list(RUNTIME_BUNDLE_FILES),
            "note": "The portable core records the contract and safety boundary. Projects should explicitly copy the runtime bundle from a skeleton source checkout before treating loop commands as executable.",
        },
        "non_goals": [
            "Does not copy project business stack, archive, blueprint, real data configuration, or local secrets.",
            "Does not perform production, database, external service, or git workflow actions.",
        ],
    }


def runtime_schema_payload() -> dict[str, Any]:
    return {
        "version": 3,
        "name": "adapter-runtime-schema",
        "description": "Deterministic schema guard for adapter runtime metadata and Loop runtime contract sections.",
        "required_runtime_keys": [
            "version",
            "name",
            "description",
            "paths",
            "commands",
            "gates",
            "loop_runtime",
            "online_flow_protocol",
            "runtime_bundle",
            "authorization",
            "smoke_tests",
            "evidence_policy",
            "non_actions",
        ],
        "required_runtime_object_keys": [
            "paths",
            "commands",
            "gates",
            "loop_runtime",
            "online_flow_protocol",
            "authorization",
            "smoke_tests",
            "evidence_policy",
        ],
        "required_runtime_list_keys": [
            "non_actions",
        ],
        "required_command_keys": list(LOOP_REQUIRED_COMMAND_KEYS),
        "required_loop_capabilities": list(LOOP_RUNTIME_CAPABILITIES),
        "required_path_string_keys": [
            "collaboration_root",
            "boundary_prefix",
            "requirement_prefix",
            "review_prefix",
            "qa_prefix",
            "decision_prefix",
            "learning_prefix",
        ],
        "required_path_list_keys": [
            "formal_stack_prefixes",
            "domain_spec_prefixes",
            "implementation_prefixes",
            "demo_prefixes",
            "archive_prefixes",
            "forbidden_default_prefixes",
        ],
        "structured_gate_keys": [
            "data_access_status_requirements",
        ],
        "path_rules": {
            "must_be_repo_relative": True,
            "must_not_escape_repo": True,
            "must_not_be_url": True,
        },
        "non_goals": [
            "Does not validate project business truth.",
            "Does not connect to production, databases, external services, or git remotes.",
            "Does not prove loop commands are executable unless --verify-runtime passes in the target repo.",
        ],
    }


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


def configure_repo_root(repo_root: Path) -> None:
    global REPO_ROOT, DEFAULT_ADAPTER, ACTIVE_BOUNDARY

    REPO_ROOT = repo_root.resolve()
    DEFAULT_ADAPTER = REPO_ROOT / "adapters" / "default"
    ACTIVE_BOUNDARY = REPO_ROOT / ".gstack" / "task-boundaries" / "CURRENT.local.md"


def slugify(raw: str) -> str:
    value = raw.strip().lower()
    value = re.sub(r"[^a-z0-9._\-\s]+", "-", value)
    value = re.sub(r"[\s_]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-.")
    return value or "default"


def repo_relative(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return resolved.as_posix()


def adapter_dir(adapter: str) -> Path:
    return REPO_ROOT / "adapters" / adapter


def is_skeleton_repo() -> bool:
    return (REPO_ROOT / SKELETON_MARKER).exists()


def normalize_dir_prefix(raw: str) -> str:
    value = raw.strip()
    if not value:
        return ""
    value = value[2:] if value.startswith("./") else value
    return value if value.endswith("/") else f"{value}/"


def existing_dir_prefixes(candidates: tuple[str, ...]) -> list[str]:
    prefixes: list[str] = []
    for candidate in candidates:
        path = REPO_ROOT / candidate
        if path.is_dir():
            prefixes.append(normalize_dir_prefix(candidate))
    return prefixes


def stack_child_prefixes() -> list[str]:
    stack_dir = REPO_ROOT / "stack"
    if not stack_dir.is_dir():
        return []
    return [
        normalize_dir_prefix(f"stack/{path.name}")
        for path in sorted(stack_dir.iterdir())
        if path.is_dir()
    ]


def merge_dir_prefixes(detected: list[str], explicit: list[str] | None) -> list[str]:
    values = [normalize_dir_prefix(item) for item in (explicit or [])]
    values = [item for item in values if item]
    if values:
        return list(dict.fromkeys(values))
    return list(dict.fromkeys(detected))


def merge_forbidden_prefixes(explicit: list[str] | None) -> list[str]:
    values = [item.strip() for item in (explicit or []) if item.strip()]
    return list(dict.fromkeys([*GENERIC_FORBIDDEN_PREFIXES, *values]))


def detect_project_shape() -> dict[str, list[str]]:
    implementation_prefixes = existing_dir_prefixes(PROJECT_IMPLEMENTATION_CANDIDATES)
    formal_stack_prefixes = stack_child_prefixes() or existing_dir_prefixes(PROJECT_FORMAL_STACK_CANDIDATES)
    archive_prefixes = existing_dir_prefixes(PROJECT_ARCHIVE_CANDIDATES)
    return {
        "formal_stack_prefixes": formal_stack_prefixes,
        "domain_spec_prefixes": existing_dir_prefixes(PROJECT_DOC_CANDIDATES),
        "implementation_prefixes": implementation_prefixes,
        "demo_prefixes": existing_dir_prefixes(PROJECT_DEMO_CANDIDATES),
        "archive_prefixes": archive_prefixes or ["archive/"],
        "forbidden_default_prefixes": list(GENERIC_FORBIDDEN_PREFIXES),
    }


def project_shape_from_args(args: argparse.Namespace) -> dict[str, list[str]]:
    detected = detect_project_shape()
    return {
        "formal_stack_prefixes": merge_dir_prefixes(
            detected["formal_stack_prefixes"],
            args.formal_stack_prefix,
        ),
        "domain_spec_prefixes": merge_dir_prefixes(
            detected["domain_spec_prefixes"],
            args.domain_spec_prefix,
        ),
        "implementation_prefixes": merge_dir_prefixes(
            detected["implementation_prefixes"],
            args.implementation_prefix,
        ),
        "demo_prefixes": merge_dir_prefixes(
            detected["demo_prefixes"],
            args.demo_prefix,
        ),
        "archive_prefixes": merge_dir_prefixes(
            detected["archive_prefixes"],
            args.archive_prefix,
        ),
        "forbidden_default_prefixes": merge_forbidden_prefixes(args.forbidden_prefix),
    }


def project_display_name(project_name: str | None, adapter: str) -> str:
    cleaned = (project_name or "").strip()
    if cleaned:
        return cleaned
    if is_skeleton_repo() and adapter == "default":
        return "KK Dev Skeleton"
    if REPO_ROOT.name:
        return REPO_ROOT.name.replace("-", " ").replace("_", " ").title()
    return adapter.replace("-", " ").title()


def render_project_shape_markdown(project_shape: dict[str, list[str]] | None) -> str:
    if not project_shape:
        return ""
    sections = [
        ("Formal stack prefixes", project_shape.get("formal_stack_prefixes", [])),
        ("Domain / spec prefixes", project_shape.get("domain_spec_prefixes", [])),
        ("Implementation prefixes", project_shape.get("implementation_prefixes", [])),
        ("Demo prefixes", project_shape.get("demo_prefixes", [])),
        ("Archive prefixes", project_shape.get("archive_prefixes", [])),
    ]
    lines = ["## Project Shape", ""]
    for title, values in sections:
        lines.append(f"### {title}")
        if values:
            lines.extend(f"- `{value}`" for value in values)
        else:
            lines.append("- `not-declared`")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n\n"


def adapter_markdown(
    adapter: str,
    *,
    project_name: str | None = None,
    project_shape: dict[str, list[str]] | None = None,
) -> str:
    if adapter == "default" and not project_name and is_skeleton_repo():
        return DEFAULT_ADAPTER_MD
    display_name = project_display_name(project_name, adapter)
    project_shape_section = render_project_shape_markdown(project_shape)
    return f"""# {display_name} Adapter

This adapter describes the target repository layout for repo-native AI development helpers.
It is project-owned metadata and does not replace the repository source of truth.

## Project Goal

- Keep product semantics, implementation, fixtures, tests, and delivery evidence inside this repository.
- Keep collaboration evidence, task boundaries, reviews, QA, decisions, and reusable learnings inside `.gstack/`.
- Keep project-specific stack, data, permission, deployment, and rollback rules in the adapter runtime.

## Source Of Truth

- Repository entry: `README.md`
- Collaboration entry: `.gstack/README.md`
- Code map: `.gstack/knowledge/CODEMAP.md`
- Document placement: `.gstack/knowledge/doc-placement.md`
- Active task entry: `.gstack/task-boundaries/CURRENT.md`

## Commands

```bash
python3 scripts/init_project.py --adapter {adapter} --detect
python3 scripts/init_project.py --adapter {adapter} --plan
python3 scripts/init_project.py --adapter {adapter} --verify --verify-core --report
python3 scripts/init_project.py --adapter {adapter} --apply-runtime --dry-run --report
python3 scripts/init_project.py --adapter {adapter} --verify-runtime --report
python3 scripts/init_project.py --adapter {adapter} --rewrite-adapter --dry-run
```

When the Loop runtime script bundle is present:

```bash
python3 .gstack/scripts/gstack_loop.py plan --format user
python3 .gstack/scripts/gstack_loop.py eng-review --format user
python3 .gstack/scripts/gstack_loop.py subagents --format user
python3 .gstack/scripts/gstack_loop.py repair-loop --dry-run --format user
python3 .gstack/scripts/gstack_loop.py authorize --raw "继续做" --format user
python3 .gstack/scripts/gstack_loop.py chat-smoke --format user
python3 .gstack/scripts/gstack_loop.py nl-smoke --format user
python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user
```

## Loop Runtime Capabilities

- Chat-first execution from natural-language goal to requirement, review, boundary, implementation, verification, QA evidence, and doc sync.
- Codex-owned engineering decisions for code structure, test selection, subagent strategy, local gate recovery, and documentation sync inside the active boundary.
- User-owned decisions for business scope, product / design multi-choice tradeoffs, real data, production, database, destructive commands, and git workflow authorization.
- Stage write-back, subagent orchestration, test-repair loop, chat authorization classification, `chat-smoke`, `nl-smoke`, and contract smoke are declared in `runtime.json`.

{project_shape_section}## Safety Boundary

- Do not connect to real data by default.
- Do not perform production operations.
- Do not modify database schema.
- Do not run git workflow actions without explicit user approval.
- Do not overwrite existing project files unless a later task explicitly authorizes that scope.
- `apply-runtime` is explicit opt-in; it copies only the portable Loop runtime script allowlist and preserves existing target files.
- `rewrite-adapter` only rewrites adapter metadata; it does not move business code or rewrite portable core files.
"""


def runtime_payload(
    adapter: str,
    *,
    project_name: str | None = None,
    project_shape: dict[str, list[str]] | None = None,
) -> dict[str, Any]:
    if is_skeleton_repo() and not project_name:
        payload = json.loads(json.dumps(DEFAULT_RUNTIME, ensure_ascii=False))
    else:
        display_name = project_display_name(project_name, adapter)
        shape = project_shape or {
            "formal_stack_prefixes": [],
            "domain_spec_prefixes": [],
            "implementation_prefixes": [],
            "demo_prefixes": [],
            "archive_prefixes": ["archive/"],
            "forbidden_default_prefixes": list(GENERIC_FORBIDDEN_PREFIXES),
        }
        payload = {
            "version": 7,
            "name": adapter,
            "description": f"{display_name} adapter metadata for repo-native AI development helpers with Loop runtime contract metadata and explicit runtime bundle install.",
            "project": {
                "name": display_name,
                "source": "generated-by-adapter-installer",
                "rewrite_status": "project-specific" if project_shape else "generic",
            },
            "paths": {
                "collaboration_root": ".gstack/",
                "boundary_prefix": ".gstack/task-boundaries/",
                "requirement_prefix": ".gstack/requirements/",
                "review_prefix": ".gstack/reviews/",
                "qa_prefix": ".gstack/qa-reports/",
                "decision_prefix": ".gstack/decisions/",
                "learning_prefix": ".gstack/learnings/",
                "formal_stack_prefixes": shape["formal_stack_prefixes"],
                "domain_spec_prefixes": shape["domain_spec_prefixes"],
                "implementation_prefixes": shape["implementation_prefixes"],
                "demo_prefixes": shape["demo_prefixes"],
                "archive_prefixes": shape["archive_prefixes"],
                "forbidden_default_prefixes": shape["forbidden_default_prefixes"],
            },
            "commands": {
                "detect": ["python3", "scripts/init_project.py", "--adapter", adapter, "--detect"],
                "plan": ["python3", "scripts/init_project.py", "--adapter", adapter, "--plan"],
                "rewrite_adapter_dry_run": ["python3", "scripts/init_project.py", "--adapter", adapter, "--rewrite-adapter", "--dry-run"],
                "rewrite_adapter": ["python3", "scripts/init_project.py", "--adapter", adapter, "--rewrite-adapter"],
                "validate": ["python3", "scripts/init_project.py", "--adapter", adapter, "--validate-adapter", "--report"],
                "verify_core": ["python3", "scripts/init_project.py", "--adapter", adapter, "--verify", "--verify-core", "--report"],
                "pilot": ["python3", "scripts/init_project.py", "--adapter", adapter, "--pilot", "--report"],
                "pilot_output": ["python3", "scripts/init_project.py", "--adapter", adapter, "--pilot", "--pilot-output", "<empty-dir>", "--report"],
                **loop_runtime_commands(),
            },
            "gates": {
                "data-access": "Use when a task touches real data, source systems, API contracts, metrics, SQL, or data scope.",
                "prototype-logic-extraction": "Use when backend/service code takes over existing frontend, fixture, mock, or prototype logic.",
                "ui-interaction-qa": "Use when UI, HTML, dashboard, or visualization behavior changes.",
            },
            "loop_runtime": loop_runtime_section(),
            "online_flow_protocol": online_flow_protocol_section(),
            "runtime_bundle": runtime_bundle_section(),
            "authorization": authorization_section(),
            "smoke_tests": smoke_tests_section(),
            "evidence_policy": evidence_policy_section(),
            "non_actions": loop_non_actions(),
        }
    payload["name"] = adapter
    if adapter != "default" and is_skeleton_repo() and not project_name:
        payload["description"] = f"{adapter} adapter metadata copied from KK Dev Skeleton default."
    return payload


def portable_core_templates(*, project_name: str | None, adapter: str) -> dict[str, str]:
    display_name = project_display_name(project_name, adapter)
    manifest_text = json.dumps(core_manifest_payload(), ensure_ascii=False, indent=2) + "\n"
    runtime_schema_text = json.dumps(runtime_schema_payload(), ensure_ascii=False, indent=2) + "\n"
    script_text = SCRIPT_PATH.read_text(encoding="utf-8")
    return {
        "AGENTS.md": f"""# {display_name}

## Collaboration Rules

- Start implementation work by reading `README.md`, `.gstack/README.md`, `.gstack/knowledge/CODEMAP.md`, `.gstack/knowledge/doc-placement.md`, and `.gstack/task-boundaries/CURRENT.md`.
- Keep task requirements, reviews, boundaries, QA reports, decisions, and learnings in `.gstack/`.
- Codex should make technical choices inside the active task boundary: code structure, implementation order, tests, subagent strategy, local gate recovery, and doc sync.
- Ask the user only for business choices, product or design multi-choice decisions, real data access, production operations, database changes, destructive commands, and git workflow authorization.
- Ambiguous replies such as "ok", "confirmed", "continue", or "do it" do not authorize git, production, database, real-data write, destructive, or rollback actions.
- Do not operate on production, databases, real data, destructive commands, external services, or git workflow actions without explicit user authorization.
- Preserve existing project files by default; generated installer actions should create missing files and report what they changed.
""",
        "README.md": f"""# {display_name}

This repository has been initialized with a portable AI development collaboration core.

Start with natural language:

- Describe the goal.
- Say who will use it.
- Say what success should look like.
- Say what must not be touched.
- Say whether real data, production, database, publishing, or git workflow actions are involved.

The collaboration system keeps task evidence under `.gstack/` and adapter metadata under `adapters/default/`.

Codex should work chat-first: clarify the goal, write or update requirement / review / boundary evidence when needed, implement inside the declared boundary, run local verification, write QA evidence only after real checks, and sync relevant docs. You should only need to confirm business choices or high-risk authorization.

High-risk actions still require explicit authorization: commit, amend, branch changes, pull, push, merge, pull request, deployment, production restart or rollback, database schema changes, real-data writes, destructive commands, and broad revert / rollback.

Useful local checks after the runtime bundle is installed:

```bash
python3 scripts/init_project.py --adapter default --validate-adapter --report
python3 scripts/init_project.py --adapter default --verify --verify-core --report
python3 scripts/init_project.py --adapter default --verify-runtime --report
python3 .gstack/scripts/gstack_loop.py chat-smoke --format user
python3 .gstack/scripts/gstack_loop.py nl-smoke --format user
python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user
```

To install the runtime bundle from a skeleton source checkout into this target repo:

```bash
python3 scripts/init_project.py --repo-root /path/to/this/project --adapter default --apply-runtime --dry-run --report
python3 scripts/init_project.py --repo-root /path/to/this/project --adapter default --apply-runtime --report
```
""",
        ".gstack/README.md": """# Collaboration System

This directory stores repo-native collaboration evidence. It is not a replacement for the product or engineering source of truth.

Recommended evidence folders:

- `requirements/`
- `reviews/`
- `task-boundaries/`
- `qa-reports/`
- `decisions/`
- `learnings/`

Loop runtime contract:

- Chat-first execution: natural language goal -> requirement / review / boundary -> implementation -> verification -> QA evidence -> doc sync.
- ENG review decisioner: Codex owns engineering choices inside the boundary; users own business choices and high-risk authorization.
- Stage write-back: only after existing repo-native evidence; helpers do not generate evidence bodies.
- Subagent orchestration: planned by protocol with checkpoint, deadline, result schema, forbidden paths, and evidence collection.
- Test-repair loop: classify local failures, repair locally when safe, rerun failed commands first, then full verification, then write QA.
- Chat authorization: vague confirmations do not authorize git, production, database, real-data write, destructive, or rollback actions.

Use `scripts/init_project.py --verify --verify-core --report` to check the portable core files.
""",
        ".gstack/knowledge/CODEMAP.md": f"""# Code Map

This file should explain where {display_name} keeps product truth, implementation code, tests, fixtures, and delivery scripts.

Fill this in before broad implementation work. At minimum record:

- primary app or service directories
- test directories
- documentation / spec directories
- generated or local-only directories
- forbidden paths and sensitive configuration rules
""",
        ".gstack/knowledge/doc-placement.md": """# Document Placement

Use this file to decide where long-lived documents belong.

- Product and engineering truth should live with the project source of truth.
- Collaboration process evidence should live under `.gstack/`.
- Historical or abandoned material should be clearly marked as archive.
- Do not put machine-specific absolute paths in long-lived repository documents.
""",
        ".gstack/knowledge/ai-programming-framework.md": """# AI Programming Framework

This file records the portable collaboration contract for this project.

## Framework Core

- `chat-first execution`: users describe goals in natural language; Codex turns them into requirement, review, boundary, implementation, verification, QA evidence, and doc sync.
- `engineering autonomy`: Codex chooses code structure, implementation order, test commands, subagent strategy, local gate recovery, and doc sync paths inside the active boundary.
- `user decision boundary`: users decide business scope, product / design multi-choice tradeoffs, real data access, production, database changes, destructive commands, and git workflow authorization.
- `eng-review decisioner`: ENG review evidence should prove Codex did not ask the user to choose technical implementation details.
- `stage write-back`: stage status is written only after existing repo-native evidence is present; helpers do not generate requirement, review, QA, implementation, or test bodies.
- `subagent orchestration`: complex tasks may use explorer, reviewer, worker, or QA subagents with checkpoint, deadline, result schema, forbidden paths, and evidence collection.
- `test-repair loop`: failed local verification should be analyzed, fixed locally when safe, rerun from the failed command, then rerun full verification and write QA evidence.
- `chat authorization`: ambiguous confirmation never authorizes git, production, database, real-data write, destructive, or rollback actions.

## Required Evidence

- Requirements: `.gstack/requirements/`
- Reviews: `.gstack/reviews/`
- Boundaries: `.gstack/task-boundaries/`
- QA reports: `.gstack/qa-reports/`
- Decisions: `.gstack/decisions/`
- Learnings: `.gstack/learnings/`

## Smoke Checks

After the runtime scripts are installed, use:

```bash
python3 .gstack/scripts/gstack_loop.py chat-smoke --format user
python3 .gstack/scripts/gstack_loop.py nl-smoke --format user
python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user
```

These checks must not write evidence, activate tasks, run git workflow actions, connect to production, modify databases, or write real data.
""",
        ".gstack/scripts/README.md": """# Collaboration Scripts

This portable core always includes the adapter installer:

```bash
python3 scripts/init_project.py --adapter default --detect
python3 scripts/init_project.py --adapter default --plan
python3 scripts/init_project.py --adapter default --validate-adapter --report
python3 scripts/init_project.py --adapter default --verify --verify-core --report
```

The executable Loop runtime script bundle is explicit opt-in. Install it from a skeleton source checkout:

```bash
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --apply-runtime --dry-run --report
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --apply-runtime --report
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --verify-runtime --report
```

When the Loop runtime script bundle is installed, these checks should also be available:

```bash
python3 .gstack/scripts/gstack_loop.py plan --format user
python3 .gstack/scripts/gstack_loop.py eng-review --format user
python3 .gstack/scripts/gstack_loop.py subagents --format user
python3 .gstack/scripts/gstack_loop.py repair-loop --dry-run --format user
python3 .gstack/scripts/gstack_loop.py write-back --dry-run --format user --evidence .gstack/scripts/gstack_loop.py
python3 .gstack/scripts/gstack_loop.py authorize --raw "继续做" --format user
python3 .gstack/scripts/gstack_loop.py chat-smoke --format user
python3 .gstack/scripts/gstack_loop.py nl-smoke --format user
python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user
```

Loop runtime helpers are safe-by-default: dry-run first, allowlisted local verification only, no production, no database writes, no real data writes, no destructive commands, and no git workflow action without explicit user authorization.
""",
        ".gstack/task-boundaries/CURRENT.md": """# Current Task Boundary Entry

This stable entry does not store a shared active-task pointer.

Use concrete files in `.gstack/task-boundaries/` for task scope, allowed files, forbidden files, non-goals, acceptance evidence, and verification.
Local tools may keep a machine-local active pointer outside shared source control.
""",
        ".gstack/requirements/README.md": "# Requirements\n\nStore task requirement briefs and freeze evidence here.\n",
        ".gstack/reviews/README.md": "# Reviews\n\nStore plan, engineering, code, and delivery reviews here.\n",
        ".gstack/qa-reports/README.md": "# QA Reports\n\nStore reproducible acceptance and verification evidence here.\n",
        "scripts/init_project.py": script_text,
        "adapters/default/core_manifest.json": manifest_text,
        "adapters/default/runtime_schema.json": runtime_schema_text,
    }


def read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.exists():
        return None, "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, f"invalid json: {exc}"
    if not isinstance(payload, dict):
        return None, "json root must be an object"
    return payload, None


def write_default_adapter_files(*, dry_run: bool = False) -> list[str]:
    created: list[str] = []
    if not dry_run:
        DEFAULT_ADAPTER.mkdir(parents=True, exist_ok=True)

    adapter_md = DEFAULT_ADAPTER / "adapter.md"
    if not adapter_md.exists():
        if not dry_run:
            adapter_md.write_text(DEFAULT_ADAPTER_MD.rstrip() + "\n", encoding="utf-8")
        created.append(repo_relative(adapter_md))

    runtime_json = DEFAULT_ADAPTER / "runtime.json"
    if not runtime_json.exists():
        if not dry_run:
            runtime_json.write_text(
                json.dumps(DEFAULT_RUNTIME, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        created.append(repo_relative(runtime_json))

    core_manifest_json = DEFAULT_ADAPTER / "core_manifest.json"
    if not core_manifest_json.exists():
        if not dry_run:
            core_manifest_json.write_text(
                json.dumps(core_manifest_payload(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        created.append(repo_relative(core_manifest_json))

    runtime_schema_json = DEFAULT_ADAPTER / "runtime_schema.json"
    if not runtime_schema_json.exists():
        if not dry_run:
            runtime_schema_json.write_text(
                json.dumps(runtime_schema_payload(), ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        created.append(repo_relative(runtime_schema_json))

    return created


def copy_default_adapter(
    adapter: str,
    *,
    force: bool,
    dry_run: bool,
    project_name: str | None = None,
) -> dict[str, Any]:
    target = adapter_dir(adapter)
    adapter_md = target / "adapter.md"
    runtime_json = target / "runtime.json"
    created_paths: list[str] = []
    would_create: list[str] = []
    preserved_paths: list[str] = []
    replaced_paths: list[str] = []
    would_replace: list[str] = []

    def ensure_text(path: Path, text: str, *, replace_allowed: bool) -> None:
        if path.exists():
            if replace_allowed:
                if dry_run:
                    would_replace.append(repo_relative(path))
                else:
                    path.write_text(text.rstrip() + "\n", encoding="utf-8")
                    replaced_paths.append(repo_relative(path))
            else:
                preserved_paths.append(repo_relative(path))
            return
        if dry_run:
            would_create.append(repo_relative(path))
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        created_paths.append(repo_relative(path))

    replace_existing = force and adapter != "default"
    ensure_text(adapter_md, adapter_markdown(adapter, project_name=project_name), replace_allowed=replace_existing)
    ensure_text(
        runtime_json,
        json.dumps(runtime_payload(adapter, project_name=project_name), ensure_ascii=False, indent=2),
        replace_allowed=replace_existing,
    )

    if dry_run:
        if would_replace:
            message = f"dry-run: would replace adapter metadata: {', '.join(would_replace)}"
        elif would_create:
            message = f"dry-run: would create adapter metadata: {', '.join(would_create)}"
        else:
            message = "dry-run: adapter metadata already present"
    elif replaced_paths:
        message = f"adapter metadata replaced: {', '.join(replaced_paths)}"
    elif created_paths:
        message = f"adapter metadata created: {', '.join(created_paths)}"
    else:
        message = "adapter metadata already present"

    return {
        "created": bool(created_paths),
        "replaced": bool(replaced_paths),
        "dry_run": dry_run,
        "created_paths": created_paths,
        "would_create": would_create,
        "preserved_paths": preserved_paths,
        "replaced_paths": replaced_paths,
        "would_replace": would_replace,
        "message": message,
    }


def rewrite_adapter_metadata(
    adapter: str,
    *,
    project_name: str | None,
    project_shape: dict[str, list[str]],
    dry_run: bool,
) -> dict[str, Any]:
    target = adapter_dir(adapter)
    adapter_md = target / "adapter.md"
    runtime_json = target / "runtime.json"
    created_paths: list[str] = []
    would_create: list[str] = []
    replaced_paths: list[str] = []
    would_replace: list[str] = []
    unchanged_paths: list[str] = []

    def ensure_text(path: Path, text: str) -> None:
        rendered = text.rstrip() + "\n"
        if path.exists():
            if path.read_text(encoding="utf-8") == rendered:
                unchanged_paths.append(repo_relative(path))
                return
            if dry_run:
                would_replace.append(repo_relative(path))
            else:
                path.write_text(rendered, encoding="utf-8")
                replaced_paths.append(repo_relative(path))
            return
        if dry_run:
            would_create.append(repo_relative(path))
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8")
        created_paths.append(repo_relative(path))

    ensure_text(
        adapter_md,
        adapter_markdown(adapter, project_name=project_name, project_shape=project_shape),
    )
    ensure_text(
        runtime_json,
        json.dumps(
            runtime_payload(adapter, project_name=project_name, project_shape=project_shape),
            ensure_ascii=False,
            indent=2,
        ),
    )

    if dry_run:
        if would_create or would_replace:
            pieces = []
            if would_create:
                pieces.append(f"would create: {', '.join(would_create)}")
            if would_replace:
                pieces.append(f"would replace: {', '.join(would_replace)}")
            message = f"dry-run: adapter metadata rewrite {'; '.join(pieces)}"
        else:
            message = "dry-run: adapter metadata already matches project rewrite"
    elif created_paths or replaced_paths:
        pieces = []
        if created_paths:
            pieces.append(f"created: {', '.join(created_paths)}")
        if replaced_paths:
            pieces.append(f"replaced: {', '.join(replaced_paths)}")
        message = f"adapter metadata rewritten ({'; '.join(pieces)})"
    else:
        message = "adapter metadata already matches project rewrite"

    return {
        "changed": bool(created_paths or replaced_paths),
        "created": bool(created_paths),
        "replaced": bool(replaced_paths),
        "dry_run": dry_run,
        "created_paths": created_paths,
        "would_create": would_create,
        "replaced_paths": replaced_paths,
        "would_replace": would_replace,
        "unchanged_paths": unchanged_paths,
        "project_shape": project_shape,
        "message": message,
    }


def copy_core_bundle(adapter: str, *, project_name: str | None, dry_run: bool) -> dict[str, Any]:
    created_paths: list[str] = []
    would_create: list[str] = []
    preserved_paths: list[str] = []
    templates = portable_core_templates(project_name=project_name, adapter=adapter)

    for relative_path, text in templates.items():
        path = REPO_ROOT / relative_path
        if path.exists():
            preserved_paths.append(relative_path)
            continue
        if dry_run:
            would_create.append(relative_path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.rstrip() + "\n", encoding="utf-8")
        created_paths.append(relative_path)

    if dry_run:
        if would_create:
            message = f"dry-run: would create portable core files: {', '.join(would_create)}"
        else:
            message = "dry-run: portable core files already present"
    elif created_paths:
        message = f"portable core files created: {', '.join(created_paths)}"
    else:
        message = "portable core files already present"

    return {
        "created": bool(created_paths),
        "dry_run": dry_run,
        "created_paths": created_paths,
        "would_create": would_create,
        "preserved_paths": preserved_paths,
        "message": message,
    }


def copy_runtime_bundle(*, dry_run: bool) -> dict[str, Any]:
    created_paths: list[str] = []
    would_create: list[str] = []
    preserved_paths: list[str] = []
    source_missing: list[str] = []

    for relative_path in RUNTIME_BUNDLE_FILES:
        source = SOURCE_REPO_ROOT / relative_path
        target = REPO_ROOT / relative_path
        if not source.exists():
            source_missing.append(relative_path)
            continue
        if target.exists():
            preserved_paths.append(relative_path)
            continue
        if dry_run:
            would_create.append(relative_path)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        created_paths.append(relative_path)

    if source_missing:
        message = f"runtime bundle source files missing: {', '.join(source_missing)}"
    elif dry_run:
        if would_create:
            message = f"dry-run: would create runtime bundle files: {', '.join(would_create)}"
        else:
            message = "dry-run: runtime bundle files already present"
    elif created_paths:
        message = f"runtime bundle files created: {', '.join(created_paths)}"
    else:
        message = "runtime bundle files already present"

    return {
        "created": bool(created_paths),
        "ok": not source_missing,
        "dry_run": dry_run,
        "created_paths": created_paths,
        "would_create": would_create,
        "preserved_paths": preserved_paths,
        "source_missing": source_missing,
        "message": message,
    }


def read_active_boundary() -> str | None:
    if not ACTIVE_BOUNDARY.exists():
        return None
    text = ACTIVE_BOUNDARY.read_text(encoding="utf-8")
    match = re.search(r"\]\(([^)]+)\)", text)
    if match:
        return f".gstack/task-boundaries/{match.group(1)}"
    return None


def is_git_worktree() -> bool:
    if not REPO_ROOT.exists():
        return False
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def root_code_paths() -> list[str]:
    return [path for path in ROOT_CODE_CANDIDATES if (REPO_ROOT / path).exists()]


def detect_project(adapter: str) -> dict[str, Any]:
    target = adapter_dir(adapter)
    runtime_path = target / "runtime.json"
    runtime, runtime_error = read_json(runtime_path)
    required_core_paths = (
        CORE_REQUIRED_PATHS
        if is_skeleton_repo()
        else PORTABLE_CORE_REQUIRED_PATHS
    )
    core_missing = [path for path in required_core_paths if not (REPO_ROOT / path).exists()]
    core_present = [path for path in required_core_paths if (REPO_ROOT / path).exists()]
    portable_core_missing = [path for path in PORTABLE_CORE_REQUIRED_PATHS if not (REPO_ROOT / path).exists()]
    portable_core_present = [path for path in PORTABLE_CORE_REQUIRED_PATHS if (REPO_ROOT / path).exists()]
    runtime_bundle_missing = [path for path in RUNTIME_BUNDLE_FILES if not (REPO_ROOT / path).exists()]
    runtime_bundle_present = [path for path in RUNTIME_BUNDLE_FILES if (REPO_ROOT / path).exists()]
    paths = runtime.get("paths", {}) if runtime else {}
    formal_stack_prefixes = paths.get("formal_stack_prefixes", []) if isinstance(paths, dict) else []
    project_shape = detect_project_shape()

    return {
        "repo_root": REPO_ROOT.as_posix(),
        "adapter": adapter,
        "adapter_dir": repo_relative(target),
        "adapter_exists": target.exists(),
        "adapter_md_exists": (target / "adapter.md").exists(),
        "runtime_json_exists": runtime_path.exists(),
        "runtime_json_valid": runtime is not None,
        "runtime_json_error": runtime_error,
        "default_adapter_exists": DEFAULT_ADAPTER.exists(),
        "active_boundary": read_active_boundary(),
        "git_worktree": is_git_worktree(),
        "core_present": core_present,
        "core_missing": core_missing,
        "portable_core_present": portable_core_present,
        "portable_core_missing": portable_core_missing,
        "runtime_bundle_present": runtime_bundle_present,
        "runtime_bundle_missing": runtime_bundle_missing,
        "root_code_paths": root_code_paths(),
        "project_shape": project_shape,
        "formal_stack_prefixes": formal_stack_prefixes,
        "formal_stack_prefixes_exist": [
            prefix for prefix in formal_stack_prefixes if (REPO_ROOT / prefix).exists()
        ],
        "adapter_rewrite_suggested": bool(project_shape["formal_stack_prefixes"]) and not bool(formal_stack_prefixes),
    }


def plan_adoption(state: dict[str, Any]) -> list[str]:
    steps: list[str] = []
    if state["core_missing"]:
        steps.append("补齐缺失的 adapter installer core 文件。")
    else:
        steps.append("adapter installer core 文件已具备。")

    if not state["adapter_exists"]:
        steps.append(f"创建 adapters/{state['adapter']}，默认从 adapters/default 复制。")
    elif not state["adapter_md_exists"] or not state["runtime_json_exists"]:
        steps.append("补齐 adapter.md 和 runtime.json，保留已有内容，不默认覆盖。")
    elif not state["runtime_json_valid"]:
        steps.append("修复 runtime.json 格式错误。")
    else:
        steps.append(f"保留现有 adapters/{state['adapter']}。")

    if state["root_code_paths"]:
        joined = "、".join(f"`{path}`" for path in state["root_code_paths"])
        steps.append(f"检测到根目录代码或配置：{joined}。不自动移动，先生成迁移计划。")

    if state["formal_stack_prefixes"]:
        steps.append("后续实现继续以 adapter runtime 中的 formal stack prefixes 为默认工程入口。")
    elif state["project_shape"]["formal_stack_prefixes"]:
        steps.append("检测到可作为项目真源起点的目录；运行 --rewrite-adapter 写入项目专属 adapter metadata。")
    else:
        steps.append("补充 formal stack prefixes，避免 Codex 无法判断默认实现路径。")

    if state["portable_core_missing"]:
        steps.append("如需最小完整协作系统，运行 --apply-core 受控补齐 portable core bundle。")
    else:
        steps.append("portable core bundle 已具备。")

    if state["runtime_bundle_missing"]:
        steps.append("如需可执行 Loop runtime，运行 --apply-runtime 显式复制 runtime script bundle，再运行 --verify-runtime。")
    else:
        steps.append("runtime script bundle 已具备，可运行 --verify-runtime。")

    steps.extend(
        [
            "运行 detect / plan / verify，并输出 report 作为接入证据。",
            "如果要复制到新项目，由 Codex 根据新项目 adapter 改写 runtime paths、commands 和 gates。",
            "独立 runtime、Web UI、跨机器后台同步和 git 操作另起任务处理。",
        ]
    )
    return steps


def verify_commands(adapter: str) -> list[tuple[str, list[str]]]:
    doctor = REPO_ROOT / ".gstack" / "scripts" / "gstack_doctor.py"
    smoke = REPO_ROOT / ".gstack" / "scripts" / "natural_language_dev_smoke.py"
    spec_sync = REPO_ROOT / ".gstack" / "scripts" / "spec_sync_guard.py"
    loop = REPO_ROOT / ".gstack" / "scripts" / "gstack_loop.py"
    contract = REPO_ROOT / ".gstack" / "scripts" / "gstack_loop_contract_smoke.py"
    if not is_skeleton_repo():
        return []
    if not (doctor.exists() and smoke.exists() and spec_sync.exists()):
        return []
    commands = [
        ("doctor", [sys.executable, ".gstack/scripts/gstack_doctor.py", "check"]),
        ("natural-language-smoke", [sys.executable, ".gstack/scripts/natural_language_dev_smoke.py", "--format", "user"]),
        ("spec-sync", [sys.executable, ".gstack/scripts/spec_sync_guard.py"]),
    ]
    if loop.exists() and contract.exists():
        commands.extend(
            [
                ("loop-contract-smoke", [sys.executable, ".gstack/scripts/gstack_loop_contract_smoke.py", "--format", "user"]),
                ("loop-chat-smoke", [sys.executable, ".gstack/scripts/gstack_loop.py", "chat-smoke", "--format", "user"]),
                ("loop-nl-smoke", [sys.executable, ".gstack/scripts/gstack_loop.py", "nl-smoke", "--format", "user"]),
            ]
        )
    return commands


def run_command(name: str, command: list[str]) -> CommandRun:
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
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


def path_is_unsafe(value: str) -> bool:
    return (
        value.startswith("/")
        or value.startswith("~")
        or value.startswith("../")
        or "/../" in value
        or "://" in value
    )


def runtime_schema_errors(adapter: str, runtime: dict[str, Any]) -> tuple[list[str], list[str]]:
    schema = runtime_schema_payload()
    errors: list[str] = []
    warnings: list[str] = []

    for key in schema["required_runtime_keys"]:
        if key not in runtime:
            errors.append(f"runtime.{key} is missing")

    for key in schema["required_runtime_object_keys"]:
        value = runtime.get(key)
        if not isinstance(value, dict):
            errors.append(f"runtime.{key} must be an object")

    for key in schema["required_runtime_list_keys"]:
        value = runtime.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f"runtime.{key} must be a non-empty list")

    version = runtime.get("version")
    if not isinstance(version, int) or version < 1:
        errors.append("runtime.version must be a positive integer")

    name = runtime.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("runtime.name must be a non-empty string")
    elif slugify(name) != adapter:
        errors.append(f"runtime.name must match adapter `{adapter}`")

    description = runtime.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append("runtime.description must be a non-empty string")

    paths = runtime.get("paths")
    if not isinstance(paths, dict):
        errors.append("runtime.paths must be an object")
        paths = {}

    for key in schema["required_path_string_keys"]:
        value = paths.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"runtime.paths.{key} must be a non-empty string")
        elif path_is_unsafe(value):
            errors.append(f"runtime.paths.{key} must be repo-relative and safe: {value}")

    for key in schema["required_path_list_keys"]:
        value = paths.get(key)
        if not isinstance(value, list):
            errors.append(f"runtime.paths.{key} must be a list")
            continue
        for index, item in enumerate(value):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"runtime.paths.{key}[{index}] must be a non-empty string")
            elif path_is_unsafe(item):
                errors.append(f"runtime.paths.{key}[{index}] must be repo-relative and safe: {item}")

    commands = runtime.get("commands")
    if not isinstance(commands, dict) or not commands:
        errors.append("runtime.commands must be a non-empty object")
    elif isinstance(commands, dict):
        for key, value in commands.items():
            if not isinstance(key, str) or not key.strip():
                errors.append("runtime.commands keys must be non-empty strings")
            if not isinstance(value, list) or not value or not all(isinstance(part, str) and part for part in value):
                errors.append(f"runtime.commands.{key} must be a non-empty string list")
        for key in schema["required_command_keys"]:
            if key not in commands:
                errors.append(f"runtime.commands.{key} is missing")

    gates = runtime.get("gates")
    if not isinstance(gates, dict) or not gates:
        errors.append("runtime.gates must be a non-empty object")
    elif isinstance(gates, dict):
        for key, value in gates.items():
            if not isinstance(key, str) or not key.strip():
                errors.append("runtime.gates keys must be non-empty strings")
                continue
            if key in schema["structured_gate_keys"]:
                if not isinstance(value, list) or not value:
                    errors.append(f"runtime.gates.{key} must be a non-empty rule list")
                    continue
                for index, rule in enumerate(value):
                    if not isinstance(rule, dict):
                        errors.append(f"runtime.gates.{key}[{index}] must be an object")
                        continue
                    prefixes = rule.get("prefixes")
                    statuses = rule.get("statuses")
                    reason = rule.get("reason")
                    if not isinstance(prefixes, list) or not prefixes or not all(isinstance(item, str) and item for item in prefixes):
                        errors.append(f"runtime.gates.{key}[{index}].prefixes must be a non-empty string list")
                    if not isinstance(statuses, list) or not statuses or not all(isinstance(item, str) and item for item in statuses):
                        errors.append(f"runtime.gates.{key}[{index}].statuses must be a non-empty string list")
                    if not isinstance(reason, str) or not reason.strip():
                        errors.append(f"runtime.gates.{key}[{index}].reason must be a non-empty string")
                continue
            if not isinstance(value, str) or not value.strip():
                errors.append(f"runtime.gates.{key} must be a non-empty string")

    loop_runtime = runtime.get("loop_runtime")
    if isinstance(loop_runtime, dict):
        runtime_version = loop_runtime.get("runtime_version")
        if not isinstance(runtime_version, str) or not runtime_version.strip():
            errors.append("runtime.loop_runtime.runtime_version must be a non-empty string")
        schema_version = loop_runtime.get("schema_version")
        if not isinstance(schema_version, str) or not schema_version.strip():
            errors.append("runtime.loop_runtime.schema_version must be a non-empty string")
        capabilities = loop_runtime.get("capabilities")
        if not isinstance(capabilities, list) or not all(isinstance(item, str) and item for item in capabilities):
            errors.append("runtime.loop_runtime.capabilities must be a non-empty string list")
            capabilities = []
        missing_capabilities = [
            item for item in schema["required_loop_capabilities"]
            if item not in capabilities
        ]
        if missing_capabilities:
            errors.append(f"runtime.loop_runtime.capabilities missing: {', '.join(missing_capabilities)}")
        default_flow = loop_runtime.get("default_flow")
        if not isinstance(default_flow, list) or len(default_flow) < 7:
            errors.append("runtime.loop_runtime.default_flow must include the main gstack stages")
        codex_actions = loop_runtime.get("codex_autonomous_actions")
        if not isinstance(codex_actions, list) or not codex_actions:
            errors.append("runtime.loop_runtime.codex_autonomous_actions must be a non-empty list")
        boundary = loop_runtime.get("user_decision_boundary")
        if not isinstance(boundary, dict):
            errors.append("runtime.loop_runtime.user_decision_boundary must be an object")
        else:
            for key in ("ask_user_for", "do_not_ask_user_for"):
                value = boundary.get(key)
                if not isinstance(value, list) or not value:
                    errors.append(f"runtime.loop_runtime.user_decision_boundary.{key} must be a non-empty list")

    online_flow = runtime.get("online_flow_protocol")
    if isinstance(online_flow, dict):
        protocol_version = online_flow.get("protocol_version")
        if not isinstance(protocol_version, str) or not protocol_version.strip():
            errors.append("runtime.online_flow_protocol.protocol_version must be a non-empty string")
        if online_flow.get("status") != "supported":
            errors.append("runtime.online_flow_protocol.status must be supported")
        design_doc = online_flow.get("design_doc")
        if not isinstance(design_doc, str) or not design_doc.strip() or path_is_unsafe(design_doc):
            errors.append("runtime.online_flow_protocol.design_doc must be a safe repo-relative path")
        for key in (
            "objects",
            "status_machine",
            "side_states",
            "default_authorization",
            "requires_separate_authorization",
            "non_actions",
        ):
            value = online_flow.get(key)
            if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
                errors.append(f"runtime.online_flow_protocol.{key} must be a non-empty string list")
        for key in ("platform_role", "runner_role", "repo_role"):
            value = online_flow.get(key)
            if not isinstance(value, list) or not value:
                errors.append(f"runtime.online_flow_protocol.{key} must be a non-empty list")
        mapping = online_flow.get("evidence_mapping")
        if not isinstance(mapping, dict) or not mapping:
            errors.append("runtime.online_flow_protocol.evidence_mapping must be a non-empty object")
        else:
            for required_object in ("OnlineDemand", "ClaimPackage", "StatusEvent", "QaResult"):
                if required_object not in mapping:
                    errors.append(f"runtime.online_flow_protocol.evidence_mapping missing {required_object}")

    runtime_bundle = runtime.get("runtime_bundle")
    if isinstance(runtime_bundle, dict):
        if runtime_bundle.get("mode") != "explicit-copy":
            errors.append("runtime.runtime_bundle.mode must be explicit-copy")
        if runtime_bundle.get("write_policy") != "create-missing-preserve-existing":
            errors.append("runtime.runtime_bundle.write_policy must be create-missing-preserve-existing")
        files = runtime_bundle.get("files")
        if not isinstance(files, list) or not files:
            errors.append("runtime.runtime_bundle.files must be a non-empty list")
            files = []
        for index, item in enumerate(files):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"runtime.runtime_bundle.files[{index}] must be a non-empty string")
            elif path_is_unsafe(item):
                errors.append(f"runtime.runtime_bundle.files[{index}] must be repo-relative and safe: {item}")
        missing_runtime_files = [
            item for item in RUNTIME_BUNDLE_FILES
            if item not in files
        ]
        if missing_runtime_files:
            errors.append(f"runtime.runtime_bundle.files missing: {', '.join(missing_runtime_files)}")
        for key in ("apply_command", "verify_command"):
            value = runtime_bundle.get(key)
            if not isinstance(value, list) or not value or not all(isinstance(part, str) and part for part in value):
                errors.append(f"runtime.runtime_bundle.{key} must be a non-empty string list")
        smoke_commands = runtime_bundle.get("required_smoke_commands")
        if not isinstance(smoke_commands, list) or not smoke_commands:
            errors.append("runtime.runtime_bundle.required_smoke_commands must be a non-empty list")
        else:
            for index, command in enumerate(smoke_commands):
                if not isinstance(command, list) or not command or not all(isinstance(part, str) and part for part in command):
                    errors.append(f"runtime.runtime_bundle.required_smoke_commands[{index}] must be a non-empty string list")

    authorization = runtime.get("authorization")
    if isinstance(authorization, dict):
        classifier_version = authorization.get("classifier_version")
        if not isinstance(classifier_version, str) or not classifier_version.strip():
            errors.append("runtime.authorization.classifier_version must be a non-empty string")
        for key in ("ambiguous_confirmation_does_not_authorize", "requires_explicit_authorization"):
            value = authorization.get(key)
            if not isinstance(value, list) or not value:
                errors.append(f"runtime.authorization.{key} must be a non-empty list")

    smoke_tests = runtime.get("smoke_tests")
    if isinstance(smoke_tests, dict):
        for key in ("loop_contract_smoke", "chat_smoke", "natural_language_loop_smoke", "natural_language_dev_smoke"):
            value = smoke_tests.get(key)
            if not isinstance(value, list) or not value or not all(isinstance(part, str) and part for part in value):
                errors.append(f"runtime.smoke_tests.{key} must be a non-empty string list")

    evidence = runtime.get("evidence_policy")
    if isinstance(evidence, dict):
        repo_native_dirs = evidence.get("repo_native_dirs")
        if not isinstance(repo_native_dirs, list) or not repo_native_dirs:
            errors.append("runtime.evidence_policy.repo_native_dirs must be a non-empty list")
        if evidence.get("qa_requires_real_verification") is not True:
            errors.append("runtime.evidence_policy.qa_requires_real_verification must be true")
        markers = evidence.get("eng_review_required_markers")
        if not isinstance(markers, list) or not markers:
            errors.append("runtime.evidence_policy.eng_review_required_markers must be a non-empty list")

    non_actions = runtime.get("non_actions")
    if isinstance(non_actions, list):
        for index, item in enumerate(non_actions):
            if not isinstance(item, str) or not item.strip():
                errors.append(f"runtime.non_actions[{index}] must be a non-empty string")

    if not is_skeleton_repo():
        project = runtime.get("project")
        if not isinstance(project, dict):
            warnings.append("runtime.project is missing; run --rewrite-adapter for target-specific metadata")
        shape = detect_project_shape()
        formal_stack_prefixes = paths.get("formal_stack_prefixes") if isinstance(paths, dict) else []
        if shape["formal_stack_prefixes"] and not formal_stack_prefixes:
            warnings.append("runtime.paths.formal_stack_prefixes is empty although project shape suggests formal roots; run --rewrite-adapter")

    return errors, warnings


def adapter_markdown_errors(adapter: str) -> tuple[list[str], list[str]]:
    path = adapter_dir(adapter) / "adapter.md"
    errors: list[str] = []
    warnings: list[str] = []
    if not path.exists():
        return errors, warnings
    text = path.read_text(encoding="utf-8")
    if not text.lstrip().startswith("# "):
        warnings.append("adapter.md should start with a markdown H1 heading")
    if not is_skeleton_repo() and "KK Dev Skeleton Default Adapter" in text:
        errors.append("target adapter.md still contains KK Dev Skeleton Default Adapter; run --rewrite-adapter")
    return errors, warnings


def adapter_metadata_errors(adapter: str) -> tuple[dict[str, Any], list[str], list[str]]:
    state = detect_project(adapter)
    errors: list[str] = []
    warnings: list[str] = []
    if not state["adapter_exists"]:
        errors.append("adapter directory is missing")
    if not state["adapter_md_exists"]:
        errors.append("adapter.md is missing")
    if not state["runtime_json_exists"]:
        errors.append("runtime.json is missing")
    if not state["runtime_json_valid"]:
        errors.append(f"runtime.json is invalid: {state['runtime_json_error']}")
    runtime, runtime_error = read_json(adapter_dir(adapter) / "runtime.json")
    if runtime_error is None and runtime is not None:
        schema_errors, schema_warnings = runtime_schema_errors(adapter, runtime)
        errors.extend(schema_errors)
        warnings.extend(schema_warnings)
    adapter_errors, adapter_warnings = adapter_markdown_errors(adapter)
    errors.extend(adapter_errors)
    warnings.extend(adapter_warnings)
    return state, errors, warnings


def run_static_adapter_check(adapter: str) -> CommandRun:
    state, errors, warnings = adapter_metadata_errors(adapter)
    payload = {
        "repo_root": state["repo_root"],
        "adapter": adapter,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "adapter_md_exists": state["adapter_md_exists"],
        "runtime_json_valid": state["runtime_json_valid"],
        "core_missing_count": len(state["core_missing"]),
        "portable_core_missing_count": len(state["portable_core_missing"]),
    }
    return CommandRun(
        name="target-adapter-metadata",
        command=[
            sys.executable,
            SCRIPT_PATH.as_posix(),
            "--repo-root",
            REPO_ROOT.as_posix(),
            "--adapter",
            adapter,
            "--validate-adapter",
            "--format",
            "json",
        ],
        returncode=0 if not errors else 1,
        stdout=json.dumps(payload, ensure_ascii=False),
        stderr="",
    )


def run_static_core_check(adapter: str) -> CommandRun:
    state, errors, warnings = adapter_metadata_errors(adapter)
    for path in state["portable_core_missing"]:
        errors.append(f"portable core file is missing: {path}")
    payload = {
        "repo_root": state["repo_root"],
        "adapter": adapter,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "portable_core_missing": state["portable_core_missing"],
        "portable_core_present_count": len(state["portable_core_present"]),
    }
    return CommandRun(
        name="target-portable-core",
        command=[
            sys.executable,
            SCRIPT_PATH.as_posix(),
            "--repo-root",
            REPO_ROOT.as_posix(),
            "--adapter",
            adapter,
            "--verify",
            "--verify-core",
            "--report",
        ],
        returncode=0 if not errors else 1,
        stdout=json.dumps(payload, ensure_ascii=False),
        stderr="",
    )


def run_static_runtime_check(adapter: str) -> CommandRun:
    state, errors, warnings = adapter_metadata_errors(adapter)
    for path in state["runtime_bundle_missing"]:
        errors.append(f"runtime bundle file is missing: {path}")
    payload = {
        "repo_root": state["repo_root"],
        "adapter": adapter,
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "runtime_bundle_missing": state["runtime_bundle_missing"],
        "runtime_bundle_present_count": len(state["runtime_bundle_present"]),
    }
    return CommandRun(
        name="target-runtime-bundle",
        command=[
            sys.executable,
            SCRIPT_PATH.as_posix(),
            "--repo-root",
            REPO_ROOT.as_posix(),
            "--adapter",
            adapter,
            "--verify-runtime",
            "--format",
            "json",
        ],
        returncode=0 if not errors else 1,
        stdout=json.dumps(payload, ensure_ascii=False),
        stderr="",
    )


def runtime_smoke_commands() -> list[tuple[str, list[str]]]:
    commands = [
        ("runtime-python-compile", [sys.executable, "-m", "py_compile", *RUNTIME_BUNDLE_PYTHON_FILES]),
        ("loop-contract-smoke", [sys.executable, ".gstack/scripts/gstack_loop_contract_smoke.py", "--format", "user"]),
        ("loop-chat-smoke", [sys.executable, ".gstack/scripts/gstack_loop.py", "chat-smoke", "--format", "user"]),
        ("loop-nl-smoke", [sys.executable, ".gstack/scripts/gstack_loop.py", "nl-smoke", "--format", "user"]),
    ]
    if is_skeleton_repo():
        commands.append(("natural-language-smoke", [sys.executable, ".gstack/scripts/natural_language_dev_smoke.py", "--format", "user"]))
    return commands


def run_runtime_verification(adapter: str) -> list[CommandRun]:
    static_result = run_static_runtime_check(adapter)
    if not static_result.ok:
        return [static_result]
    return [static_result, *[run_command(name, command) for name, command in runtime_smoke_commands()]]


def run_verification(adapter: str, *, verify_core: bool = False, verify_runtime: bool = False) -> list[CommandRun]:
    results: list[CommandRun] = []
    if verify_core:
        results.append(run_static_core_check(adapter))
        results.extend(run_command(name, command) for name, command in verify_commands(adapter))
    if verify_runtime:
        results.extend(run_runtime_verification(adapter))
    if results:
        return results
    commands = verify_commands(adapter)
    if commands:
        return [run_static_adapter_check(adapter), *[run_command(name, command) for name, command in commands]]
    return [run_static_adapter_check(adapter)]


def render_detection(state: dict[str, Any]) -> str:
    lines = [
        "Adapter installer detect",
        "",
        f"- repo root: `{state['repo_root']}`",
        f"- adapter: `{state['adapter']}`",
        f"- adapter dir: `{state['adapter_dir']}`",
        f"- adapter exists: `{str(state['adapter_exists']).lower()}`",
        f"- adapter.md exists: `{str(state['adapter_md_exists']).lower()}`",
        f"- runtime.json exists: `{str(state['runtime_json_exists']).lower()}`",
        f"- runtime.json valid: `{str(state['runtime_json_valid']).lower()}`",
        f"- active boundary: `{state['active_boundary'] or 'not-found'}`",
        f"- git worktree: `{str(state['git_worktree']).lower()}`",
        f"- core missing count: `{len(state['core_missing'])}`",
        f"- portable core missing count: `{len(state['portable_core_missing'])}`",
        f"- runtime bundle missing count: `{len(state['runtime_bundle_missing'])}`",
    ]
    if state["runtime_json_error"]:
        lines.append(f"- runtime error: `{state['runtime_json_error']}`")
    if state["core_missing"]:
        lines.append("- core missing:")
        lines.extend(f"  - `{path}`" for path in state["core_missing"])
    if state["root_code_paths"]:
        lines.append("- root code paths needing migration review:")
        lines.extend(f"  - `{path}`" for path in state["root_code_paths"])
    if state["formal_stack_prefixes"]:
        lines.append("- formal stack prefixes:")
        lines.extend(f"  - `{path}`" for path in state["formal_stack_prefixes"])
    shape = state["project_shape"]
    if shape["formal_stack_prefixes"]:
        lines.append("- detected project shape formal prefixes:")
        lines.extend(f"  - `{path}`" for path in shape["formal_stack_prefixes"])
    if shape["implementation_prefixes"]:
        lines.append("- detected implementation prefixes:")
        lines.extend(f"  - `{path}`" for path in shape["implementation_prefixes"])
    if state["portable_core_missing"]:
        lines.append("- portable core missing:")
        lines.extend(f"  - `{path}`" for path in state["portable_core_missing"])
    if state["runtime_bundle_missing"]:
        lines.append("- runtime bundle missing:")
        lines.extend(f"  - `{path}`" for path in state["runtime_bundle_missing"])
    return "\n".join(lines)


def render_plan(adapter: str, state: dict[str, Any]) -> str:
    lines = ["Adapter installer plan", "", f"- adapter: `{adapter}`", "", "Steps:"]
    lines.extend(f"{index}. {step}" for index, step in enumerate(plan_adoption(state), 1))
    return "\n".join(lines)


def render_verification(results: list[CommandRun]) -> str:
    lines = ["Adapter installer verification", ""]
    for item in results:
        status = "pass" if item.ok else "fail"
        lines.extend(
            [
                f"- {item.name}: `{status}`",
                f"  command: `{' '.join(item.command)}`",
                f"  exit: `{item.returncode}`",
            ]
        )
        if item.stdout.strip():
            lines.append(f"  stdout: {item.stdout.strip().splitlines()[0]}")
        if item.stderr.strip():
            lines.append(f"  stderr: {item.stderr.strip().splitlines()[0]}")
    return "\n".join(lines)


def command_run_payload(item: CommandRun) -> dict[str, Any]:
    return {
        "name": item.name,
        "command": item.command,
        "returncode": item.returncode,
        "ok": item.ok,
        "stdout": item.stdout,
        "stderr": item.stderr,
    }


def create_pilot_project(target: Path) -> list[str]:
    paths = ["src/", "docs/", "tests/"]
    for relative_path in paths:
        (target / relative_path).mkdir(parents=True, exist_ok=True)
    (target / "src" / "README.md").write_text(
        "# Pilot Source\n\nTemporary implementation root for adapter installer pilot.\n",
        encoding="utf-8",
    )
    (target / "docs" / "README.md").write_text(
        "# Pilot Docs\n\nTemporary spec root for adapter installer pilot.\n",
        encoding="utf-8",
    )
    (target / "tests" / "README.md").write_text(
        "# Pilot Tests\n\nTemporary test root for adapter installer pilot.\n",
        encoding="utf-8",
    )
    return paths


def run_adoption_pilot(
    adapter: str,
    *,
    project_name: str | None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    original_root = REPO_ROOT
    display_name = (project_name or "Adapter Pilot").strip() or "Adapter Pilot"
    payload: dict[str, Any]

    def blocked_payload(target: Path, message: str) -> dict[str, Any]:
        return {
            "ok": False,
            "temporary_target": False,
            "target_root": target.as_posix(),
            "project_name": display_name,
            "project_paths": [],
            "errors": [message],
            "verification": [],
            "cleanup": "pilot did not start; no files were written",
        }

    def execute_pilot(target: Path, *, temporary_target: bool, cleanup: str) -> dict[str, Any]:
        project_paths = create_pilot_project(target)
        try:
            configure_repo_root(target)
            apply_result = copy_default_adapter(
                adapter,
                force=False,
                dry_run=False,
                project_name=display_name,
            )
            core_apply_result = copy_core_bundle(
                adapter,
                project_name=display_name,
                dry_run=False,
            )
            runtime_apply_result = copy_runtime_bundle(dry_run=False)
            project_shape = detect_project_shape()
            rewrite_dry_run = rewrite_adapter_metadata(
                adapter,
                project_name=display_name,
                project_shape=project_shape,
                dry_run=True,
            )
            rewrite_result = rewrite_adapter_metadata(
                adapter,
                project_name=display_name,
                project_shape=project_shape,
                dry_run=False,
            )
            validate_result = run_static_adapter_check(adapter)
            verify_core_result = run_static_core_check(adapter)
            runtime_verification = run_runtime_verification(adapter)
            state = detect_project(adapter)
            verification = [validate_result, verify_core_result, *runtime_verification]
            payload = {
                "ok": all(item.ok for item in verification),
                "temporary_target": temporary_target,
                "target_root": target.as_posix(),
                "project_name": display_name,
                "project_paths": project_paths,
                "state": state,
                "apply": apply_result,
                "core_apply": core_apply_result,
                "runtime_apply": runtime_apply_result,
                "rewrite_dry_run": rewrite_dry_run,
                "rewrite": rewrite_result,
                "verification": [command_run_payload(item) for item in verification],
                "cleanup": cleanup,
            }
        finally:
            configure_repo_root(original_root)
        return payload

    if output_dir is not None:
        target = output_dir.expanduser().resolve()
        if target.exists() and not target.is_dir():
            return blocked_payload(target, "pilot-output path exists and is not a directory")
        if target.exists() and any(target.iterdir()):
            return blocked_payload(target, "pilot-output directory is not empty; refusing to overwrite")
        target.mkdir(parents=True, exist_ok=True)
        return execute_pilot(
            target,
            temporary_target=False,
            cleanup="sandbox directory is preserved after pilot completes",
        )

    with tempfile.TemporaryDirectory(prefix="kk-dev-skeleton-adapter-pilot-") as temporary_root:
        target = Path(temporary_root).resolve()
        return execute_pilot(
            target,
            temporary_target=True,
            cleanup="temporary directory is removed after pilot completes",
        )


def render_pilot(pilot: dict[str, Any]) -> str:
    lines = [
        "Adapter installer pilot",
        "",
        f"- ok: `{str(pilot['ok']).lower()}`",
        f"- target: `{'temporary' if pilot['temporary_target'] else 'sandbox-output'}`",
        f"- project name: `{pilot['project_name']}`",
        f"- target root: `{pilot['target_root']}`",
        f"- cleanup: {pilot['cleanup']}",
    ]
    if pilot.get("errors"):
        lines.append("- errors:")
        lines.extend(f"  - {error}" for error in pilot["errors"])
    if not pilot["ok"] and "apply" not in pilot:
        return "\n".join(lines)
    lines.append("- project paths:")
    lines.extend(f"  - `{path}`" for path in pilot["project_paths"])
    lines.extend(
        [
            "- apply:",
            f"  - created paths: `{len(pilot['apply']['created_paths'])}`",
            f"  - message: {pilot['apply']['message']}",
            "- core apply:",
            f"  - created paths: `{len(pilot['core_apply']['created_paths'])}`",
            f"  - message: {pilot['core_apply']['message']}",
            "- runtime apply:",
            f"  - ok: `{str(pilot['runtime_apply']['ok']).lower()}`",
            f"  - created paths: `{len(pilot['runtime_apply']['created_paths'])}`",
            f"  - message: {pilot['runtime_apply']['message']}",
            "- rewrite dry-run:",
            f"  - would create: `{len(pilot['rewrite_dry_run']['would_create'])}`",
            f"  - would replace: `{len(pilot['rewrite_dry_run']['would_replace'])}`",
            "- rewrite:",
            f"  - changed: `{str(pilot['rewrite']['changed']).lower()}`",
            f"  - message: {pilot['rewrite']['message']}",
            "- verification:",
        ]
    )
    for item in pilot["verification"]:
        status = "pass" if item["ok"] else "fail"
        lines.extend(
            [
                f"  - {item['name']}: `{status}`",
                f"    command: `{' '.join(item['command'])}`",
                f"    exit: `{item['returncode']}`",
            ]
        )
        if item["stdout"].strip():
            lines.append(f"    stdout: {item['stdout'].strip().splitlines()[0]}")
        if item["stderr"].strip():
            lines.append(f"    stderr: {item['stderr'].strip().splitlines()[0]}")
    return "\n".join(lines)


def render_report(
    adapter: str,
    state: dict[str, Any],
    *,
    apply_result: dict[str, Any] | None = None,
    core_apply_result: dict[str, Any] | None = None,
    runtime_apply_result: dict[str, Any] | None = None,
    rewrite_result: dict[str, Any] | None = None,
    verification: list[CommandRun] | None = None,
) -> str:
    blocks = [render_detection(state), render_plan(adapter, state)]
    if apply_result is not None:
        blocks.append(
            "\n".join(
                [
                    "Adapter installer apply",
                    "",
                    f"- dry-run: `{str(apply_result.get('dry_run', False)).lower()}`",
                    f"- created: `{str(apply_result['created']).lower()}`",
                    f"- replaced: `{str(apply_result['replaced']).lower()}`",
                    f"- message: {apply_result['message']}",
                ]
            )
        )
    if core_apply_result is not None:
        blocks.append(
            "\n".join(
                [
                    "Adapter installer core apply",
                    "",
                    f"- dry-run: `{str(core_apply_result.get('dry_run', False)).lower()}`",
                    f"- created: `{str(core_apply_result['created']).lower()}`",
                    f"- message: {core_apply_result['message']}",
                ]
            )
        )
    if runtime_apply_result is not None:
        blocks.append(
            "\n".join(
                [
                    "Adapter installer runtime apply",
                    "",
                    f"- dry-run: `{str(runtime_apply_result.get('dry_run', False)).lower()}`",
                    f"- ok: `{str(runtime_apply_result.get('ok', False)).lower()}`",
                    f"- created: `{str(runtime_apply_result['created']).lower()}`",
                    f"- message: {runtime_apply_result['message']}",
                ]
            )
        )
    if rewrite_result is not None:
        blocks.append(
            "\n".join(
                [
                    "Adapter installer rewrite",
                    "",
                    f"- dry-run: `{str(rewrite_result.get('dry_run', False)).lower()}`",
                    f"- changed: `{str(rewrite_result['changed']).lower()}`",
                    f"- created: `{str(rewrite_result['created']).lower()}`",
                    f"- replaced: `{str(rewrite_result['replaced']).lower()}`",
                    f"- message: {rewrite_result['message']}",
                ]
            )
        )
    if verification is not None:
        blocks.append(render_verification(verification))
    blocks.append(
        "\n".join(
            [
                "Next safe pilot",
                "",
                "- Use --apply-core for a portable collaboration core, --apply-runtime for explicit executable Loop scripts, then --rewrite-adapter to bind adapter metadata to the target project shape before treating the target repository as adopted.",
            ]
        )
    )
    return "\n\n".join(blocks)


def print_json(payload: Any) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", help="Target repository root. Defaults to this skeleton source checkout.")
    parser.add_argument("--adapter", default="default", help="Adapter name under adapters/.")
    parser.add_argument("--project-name", help="Human-readable project name for generated target adapter metadata.")
    parser.add_argument("--detect", action="store_true", help="Detect adapter readiness without writing.")
    parser.add_argument("--plan", action="store_true", help="Print an adapter adoption plan without writing.")
    parser.add_argument("--apply", action="store_true", help="Apply safe adapter metadata scaffolding.")
    parser.add_argument("--apply-core", action="store_true", help="Apply portable core collaboration files plus adapter metadata.")
    parser.add_argument("--apply-runtime", action="store_true", help="Apply portable core plus explicit Loop runtime script bundle from the skeleton source checkout.")
    parser.add_argument("--rewrite-adapter", action="store_true", help="Rewrite adapter metadata for the target project's detected or declared shape.")
    parser.add_argument("--formal-stack-prefix", action="append", help="Override detected formal stack prefix for --rewrite-adapter. Repeatable.")
    parser.add_argument("--domain-spec-prefix", action="append", help="Override detected domain/spec prefix for --rewrite-adapter. Repeatable.")
    parser.add_argument("--implementation-prefix", action="append", help="Override detected implementation prefix for --rewrite-adapter. Repeatable.")
    parser.add_argument("--demo-prefix", action="append", help="Override detected demo prefix for --rewrite-adapter. Repeatable.")
    parser.add_argument("--archive-prefix", action="append", help="Override detected archive prefix for --rewrite-adapter. Repeatable.")
    parser.add_argument("--forbidden-prefix", action="append", help="Add forbidden prefix for generated runtime metadata. Repeatable.")
    parser.add_argument("--dry-run", action="store_true", help="Preview --apply changes without writing.")
    parser.add_argument("--validate-adapter", action="store_true", help="Run deterministic adapter metadata schema checks.")
    parser.add_argument("--pilot", action="store_true", help="Run an isolated temporary adoption pilot without touching a real target repo.")
    parser.add_argument("--pilot-output", help="Preserve pilot output in a missing or empty sandbox directory.")
    parser.add_argument("--verify", action="store_true", help="Run adapter readiness checks.")
    parser.add_argument("--verify-core", action="store_true", help="Verify portable core files in addition to adapter metadata.")
    parser.add_argument("--verify-runtime", action="store_true", help="Verify explicit Loop runtime script bundle files, compile, and target-safe smoke.")
    parser.add_argument("--report", action="store_true", help="Print a combined report.")
    parser.add_argument("--force", action="store_true", help="Allow replacing a non-default copied adapter.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.repo_root:
        configure_repo_root(Path(args.repo_root).expanduser().resolve())
    adapter = slugify(args.adapter)

    if args.pilot_output and not args.pilot:
        print("--pilot-output requires --pilot", file=sys.stderr)
        return 2

    pilot_result: dict[str, Any] | None = None
    if args.pilot:
        pilot_result = run_adoption_pilot(
            adapter,
            project_name=args.project_name,
            output_dir=Path(args.pilot_output) if args.pilot_output else None,
        )

    apply_result: dict[str, Any] | None = None
    if args.apply or args.apply_core or args.apply_runtime:
        apply_result = copy_default_adapter(
            adapter,
            force=args.force,
            dry_run=args.dry_run,
            project_name=args.project_name,
        )

    core_apply_result: dict[str, Any] | None = None
    if args.apply_core or args.apply_runtime:
        core_apply_result = copy_core_bundle(adapter, project_name=args.project_name, dry_run=args.dry_run)

    runtime_apply_result: dict[str, Any] | None = None
    if args.apply_runtime:
        runtime_apply_result = copy_runtime_bundle(dry_run=args.dry_run)

    rewrite_result: dict[str, Any] | None = None
    if args.rewrite_adapter:
        rewrite_result = rewrite_adapter_metadata(
            adapter,
            project_name=args.project_name,
            project_shape=project_shape_from_args(args),
            dry_run=args.dry_run,
        )

    verification: list[CommandRun] | None = None
    if args.validate_adapter and not args.verify and not args.verify_runtime:
        verification = [run_static_adapter_check(adapter)]
    elif args.verify or args.verify_runtime:
        verification = run_verification(adapter, verify_core=args.verify_core, verify_runtime=args.verify_runtime)

    state = detect_project(adapter)
    if args.format == "json":
        payload: dict[str, Any] = {"adapter": adapter, "state": state}
        if args.plan or args.report:
            payload["plan"] = plan_adoption(state)
        if apply_result is not None:
            payload["apply"] = apply_result
        if core_apply_result is not None:
            payload["core_apply"] = core_apply_result
        if runtime_apply_result is not None:
            payload["runtime_apply"] = runtime_apply_result
        if rewrite_result is not None:
            payload["rewrite"] = rewrite_result
        if verification is not None:
            payload["verification"] = [
                command_run_payload(item)
                for item in verification
            ]
        if pilot_result is not None:
            payload["pilot"] = pilot_result
        print_json(payload)
    elif args.report:
        blocks: list[str] = []
        if pilot_result is not None:
            blocks.append(render_pilot(pilot_result))
        if pilot_result is None or any(
            item is not None
            for item in (apply_result, core_apply_result, runtime_apply_result, rewrite_result, verification)
        ):
            blocks.append(
                render_report(
                    adapter,
                    state,
                    apply_result=apply_result,
                    core_apply_result=core_apply_result,
                    runtime_apply_result=runtime_apply_result,
                    rewrite_result=rewrite_result,
                    verification=verification,
                )
            )
        print("\n\n".join(blocks))
    else:
        blocks: list[str] = []
        if pilot_result is not None:
            blocks.append(render_pilot(pilot_result))
        if args.detect:
            blocks.append(render_detection(state))
        if args.plan:
            blocks.append(render_plan(adapter, state))
        if apply_result is not None:
            blocks.append(
                render_report(
                    adapter,
                    state,
                    apply_result=apply_result,
                    core_apply_result=core_apply_result,
                    runtime_apply_result=runtime_apply_result,
                    rewrite_result=rewrite_result,
                )
            )
        elif core_apply_result is not None:
            blocks.append(
                render_report(
                    adapter,
                    state,
                    core_apply_result=core_apply_result,
                    runtime_apply_result=runtime_apply_result,
                    rewrite_result=rewrite_result,
                )
            )
        elif runtime_apply_result is not None:
            blocks.append(
                render_report(
                    adapter,
                    state,
                    runtime_apply_result=runtime_apply_result,
                    rewrite_result=rewrite_result,
                )
            )
        elif rewrite_result is not None:
            blocks.append(render_report(adapter, state, rewrite_result=rewrite_result))
        if verification is not None:
            blocks.append(render_verification(verification))
        if blocks:
            print("\n\n".join(blocks))
        else:
            print(render_report(adapter, state))

    if pilot_result is not None and not pilot_result["ok"]:
        return 1
    if runtime_apply_result is not None and not runtime_apply_result.get("ok", False):
        return 1
    if verification is not None and any(not item.ok for item in verification):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
