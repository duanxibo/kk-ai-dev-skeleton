# public-workspace-layers Task Boundary

- Task: public-workspace-layers
- 负责人: Codex
- 日期: 2026-06-12
- 相关 issue / doc: `.gstack/requirements/2026-06-12_public-workspace-layers-fast-lane-requirement.md`

## Goal

- 补齐公共骨架中缺失的空 workspace layers：`archive/`、`blueprint/`、`shared/`、`.gstack/designs/`、`.gstack/migrations/`，并让初始化 helper 自动创建这些层。

## Allowed Files

- `.gstack/requirements/2026-06-12_public-workspace-layers-fast-lane-requirement.md`
- `.gstack/reviews/2026-06-12_public-workspace-layers-fast-lane-review.md`
- `.gstack/task-boundaries/2026-06-12_public-workspace-layers.md`
- `.gstack/qa-reports/2026-06-12_public-workspace-layers-qa.md`
- `.gstack/designs/README.md`
- `.gstack/migrations/README.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `archive/**`
- `blueprint/**`
- `shared/**`
- `README.md`
- `adapters/default/adapter.md`
- `scripts/init_project.py`
- `tests/test_init_project.py`

## Forbidden Files

- 源项目 私有历史内容：`<private-source-project>/archive/**`
- 源项目 私有 blueprint 内容：`<private-source-project>/blueprint/**`
- 源项目 真实 shared 输入：`<private-source-project>/shared/**`
- 真实试点项目：`<pilot-project>/**`
- `.agents/plugins/marketplace.json`
- 当前机器 Codex plugin cache / personal marketplace
- `.env*`、真实凭证、生产配置、真实客户数据
- git workflow action，除非用户另行明确批准

## Functional Non-goals

- 不复制 源项目 业务文档、旧页面、旧脚本、Excel、CSV 或 SQL evidence。
- 不把 archive 当当前实现真源。
- 不移动已有业务代码。
- 不发布 / commit / push。

## User-visible Acceptance

- 公共骨架目录结构包含 `archive/`、`blueprint/`、`shared/`、`.gstack/designs/`、`.gstack/migrations/`。
- 每个新增层都有说明该放什么、不该放什么。
- 初始化 helper 会创建这些空层。

## Generated Artifact Policy

- User-visible Change: `no`
- Artifact Type: `markdown docs, directory placeholders, python helper, unit tests`
- Acceptance Surface:
  - `README.md`
  - `scripts/init_project.py`
  - `tests/test_init_project.py`
- Browser QA: `not-required`
- Reason:
  本次不改变 Web UI、HTML、dashboard 或可视化交互。

## Decision Mode

- Mode: `自主执行`
- Source: `repo-default`
- Internal Enum: `codex-led`
- Reason:
  用户已同意补齐公共骨架层，方案明确。

## Flow Lane

- Lane: `fast-lane`
- Reason:
  小范围骨架结构和文档增强，无业务口径多解、生产操作、DB schema 或真实数据。

## Autonomy Plan

- Codex May Do Without Asking:
  - 在 Allowed Files 内实现。
  - 运行本地测试和 guards。
- Codex Must Ask Before:
  - 复制私有历史内容或真实数据。
  - 触碰 Forbidden Files。
  - git workflow action、发布、生产操作、DB schema 变更或真实数据写入。
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户`
- Goal Mode:
  `not-used`
- Local Restart:
  `not-required`

## Subagent Plan

- Mode: `not-used`
- Reason:
  fast-lane 小任务由 main agent 直接完成。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-12_public-workspace-layers-fast-lane-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-12_public-workspace-layers-fast-lane-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-12_public-workspace-layers-fast-lane-requirement.md`
  note: fast-lane requirement 同时作为 requirement freeze。
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-12_public-workspace-layers-fast-lane-review.md`
- domain-spec-readiness:
  status: not-required
  evidence: `.gstack/task-boundaries/2026-06-12_public-workspace-layers.md`
  note: 本次不改变 stack domain 产品或工程真源。
- implement:
  status: done
  evidence: `.gstack/task-boundaries/2026-06-12_public-workspace-layers.md`
- qa:
  status: done
  command: qa-only
  evidence: `.gstack/qa-reports/2026-06-12_public-workspace-layers-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "本任务不涉及真实数据、接口、查数或数据源选择"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_public-workspace-layers.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据源 / 接口 / 查数"
  - gate_id: data-query
    trigger_reason: "本任务不涉及复杂查数或高风险指标"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_public-workspace-layers.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不需要 Query Brief、SQL 或查询 review"
  - gate_id: prototype-logic-extraction
    trigger_reason: "本任务补齐 archive / baseline 空层，但不迁移原型业务逻辑到正式实现"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_public-workspace-layers.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-12_public-workspace-layers.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；本轮不使用 subagent"
  - gate_id: doc-backfill
    trigger_reason: "本任务新增目录说明，不是从已有代码反推文档"
    owner: kk-doc-backfill
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_public-workspace-layers.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "新增文档同步创建，不需要从代码反推"
  - gate_id: data-knowledge-sync
    trigger_reason: "本任务不新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_public-workspace-layers.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据知识同步"
```

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `adapters/default/adapter.md`
- `adapters/default/runtime.json`

## Spec Sync Plan

- Spec Impact: `not-required`
- Expected Spec Targets:
  - 不适用
- Allowed No-Spec-Change Reason:
  本次为公共骨架目录、文档和 helper 初始化能力增强，不改变具体应用 stack domain 产品或工程真源。

## Verification

- `python3 -m unittest tests/test_init_project.py`
- `python3 -m unittest tests/test_git_marketplace_publish_docs.py tests/test_marketplace_rollout_docs.py tests/test_plugin_marketplace.py tests/test_plugin_update_check.py tests/test_init_project.py`
- `python3 -m py_compile scripts/init_project.py tests/test_init_project.py`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`
- `python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-12_public-workspace-layers.md`

## Lessons To Write Back

- 如发现新坑，写入 `.gstack/knowledge/` 或 `.gstack/rules/`。
