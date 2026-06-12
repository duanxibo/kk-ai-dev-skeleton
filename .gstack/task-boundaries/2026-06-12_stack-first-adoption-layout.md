# stack-first-adoption-layout Task Boundary

- Task: stack-first-adoption-layout
- 负责人: Codex
- 日期: 2026-06-12
- 相关 issue / doc: `.gstack/requirements/2026-06-12_stack-first-adoption-layout-fast-lane-requirement.md`

## Goal

- 修正 KK Dev Skeleton 初始化策略：默认创建 stack/<project>/ 目录，adapter/runtime 采用 stack-first 路由，并对已有根目录代码输出迁移计划，避免初始化后代码散落在一级目录

## Allowed Files

- .gstack/requirements/2026-06-12_stack-first-adoption-layout-fast-lane-requirement.md
- .gstack/reviews/2026-06-12_stack-first-adoption-layout-fast-lane-review.md
- .gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md
- .gstack/qa-reports/2026-06-12_stack-first-adoption-layout-qa.md
- scripts/init_project.py
- tests/test_init_project.py
- adapters/default/adapter.md
- adapters/default/runtime.json
- plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption/SKILL.md
- plugins/kk-dev-skeleton-adoption/.codex-plugin/plugin.json
- README.md
- COMPANY_ADOPTION_GUIDE.md
- CODEX_ADOPTION_CONNECTOR.md
- .gstack/knowledge/CODEMAP.md
- .gstack/knowledge/code-patterns.md

## Forbidden Files

- 目标试点项目真实代码：`/Users/edy/work/codespace/ai/task-manager-cp/**`
- marketplace manifest：`.agents/plugins/marketplace.json`
- 当前机器 Codex plugin cache / personal marketplace
- 数据库配置、真实凭证、`.env*`、`.gstack/data-access/*.local.*`
- git workflow action，除非用户另行明确批准

## Functional Non-goals

- 不自动移动已有项目的 `src/`、`prisma/`、`e2e/`、`tests/` 或配置文件。
- 不修改真实试点项目 `task-manager-cp`。
- 不改 marketplace 发布配置。
- 不发布 / commit / push，除非用户另行明确批准。
- 不做生产、数据库、真实数据或部署操作。

## User-visible Acceptance

- 新初始化默认创建 `stack/<project>/` 目录结构。
- 默认 adapter 和 runtime 文档明确 stack-first。
- 对已有根目录代码，接入报告输出迁移建议，而不是静默认为散落一级目录是最终形态。
- 测试覆盖 apply 后生成 stack layout。

## Generated Artifact Policy

- User-visible Change: `no`
- Artifact Type: `python helper, adapter docs, plugin skill text, markdown docs, unit tests`
- Acceptance Surface:
  - `scripts/init_project.py`
  - `tests/test_init_project.py`
  - `adapters/default/adapter.md`
  - `adapters/default/runtime.json`
- Browser QA: `not-required`
- Reason:
  本次不改变页面、HTML、可视化或交互 UI；验收面是初始化 helper 行为、文档和测试。

## Decision Mode

- Mode: `自主执行`
- Source:
  `repo-default`
- Internal Enum:
  `codex-led`
- Reason:
  Codex 语义复核后确认 fast-lane 任务范围明确，按当前协作模式自动生成最小 evidence。

## Flow Lane

- Lane: `fast-lane`
- Reason:
  小需求 / 明确改动，无业务口径多解、生产操作、DB schema 或 git workflow action。
- Evidence Strategy:
  - 使用 fast-lane requirement、fast-lane review、boundary 和 QA evidence。

## Autonomy Plan

- Codex May Do Without Asking:
  - 补齐 fast-lane evidence。
  - 在 Allowed Files 内实现。
  - 运行本地验证和门禁。
- Codex Must Ask Before:
  - 业务口径多解。
  - 触碰 Forbidden Files。
  - 生产操作、DB schema 变更、真实数据写入、破坏性命令或 git workflow action。
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户`
- Goal Mode:
  `not-used`
  fast-lane 小任务默认不启用持续 goal。
- Local Restart:
  `not-required`

## Subagent Plan

- Mode: `not-used`
- Reason:
  fast-lane 小任务默认由 main agent 直接完成；如实现中范围扩大，再退出 fast-lane 并重新规划。
- Main Agent Owns:
  - 流程控制、active boundary、最终集成、最终答复
- Candidate Subagents:
  - name: `not-used`
    role: `reviewer`
    trigger stage: `review`
    write scope: `read-only`
    forbidden paths:
      - `stack/**`
    output evidence: `.gstack/qa-reports/2026-06-12_stack-first-adoption-layout-qa.md`
    status: `not-used`
- Result Integration:
  - 本轮验证结果写入 QA 报告和 final summary。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-12_stack-first-adoption-layout-fast-lane-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-12_stack-first-adoption-layout-fast-lane-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-12_stack-first-adoption-layout-fast-lane-requirement.md`
  note: fast-lane requirement 同时作为 requirement freeze。
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-12_stack-first-adoption-layout-fast-lane-review.md`
- domain-spec-readiness:
  status: not-required
  evidence: `.gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md`
  note: 本次 fast-lane 小需求不改变 stack domain 产品或工程真源。
- implement:
  status: done
  evidence: `.gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md`
- qa:
  status: done
  command: qa-only
  evidence: `.gstack/qa-reports/2026-06-12_stack-first-adoption-layout-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "AI 已确认 fast-lane 不涉及真实数据、接口、查数或数据源选择；如实现中发现涉及，必须退出 fast-lane 或改为 planned"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确本任务不涉及数据源 / 接口 / 查数"
  - gate_id: data-query
    trigger_reason: "AI 已确认 fast-lane 不涉及复杂查数或高风险指标"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不需要 Query Brief、SQL 或查询 review"
  - gate_id: prototype-logic-extraction
    trigger_reason: "AI 已确认 fast-lane 不涉及前端 / 原型业务逻辑迁后端"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确没有前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；本轮不使用 subagent"
  - gate_id: doc-backfill
    trigger_reason: "AI 已确认 fast-lane 不是代码已有但文档缺失的 backfill 场景"
    owner: kk-doc-backfill
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "新增文档同步创建，不需要从代码反推"
  - gate_id: data-knowledge-sync
    trigger_reason: "AI 已确认 fast-lane 不新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据知识同步"
```

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/workflows/codex-autopilot.md`
- `.gstack/templates/fast-lane-requirement.template.md`
- `.gstack/templates/fast-lane-review.template.md`

## Spec Sync Plan

- Spec Impact:
  `not-required`
- Expected Spec Targets:
  - 不适用
- Prototype Logic Evidence Sync:
  不适用。
- Allowed No-Spec-Change Reason:
  本次 fast-lane 小需求不改变 stack domain 产品或工程真源。

## Verification

- `python3 -m unittest tests/test_init_project.py`
- `python3 -m unittest tests/test_git_marketplace_publish_docs.py tests/test_marketplace_rollout_docs.py tests/test_plugin_marketplace.py tests/test_init_project.py`
- `python3 -m py_compile scripts/init_project.py tests/test_init_project.py`
- `python3 scripts/init_project.py --adapter default --detect --format json`
- `python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py plugins/kk-dev-skeleton-adoption`
- `python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/kk-dev-skeleton-adoption`
- `python3 /Users/edy/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption`
- `python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py --marketplace-path .agents/plugins/marketplace.json`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`
- `python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md`

## Lessons To Write Back

- 如发现新坑，写入 `.gstack/knowledge/` 或 `.gstack/rules/`。

## 本地激活

- 自动激活时由 `python3 .gstack/scripts/autopilot_bootstrap.py ... --activate` 写入本机 `CURRENT.local.md`。
