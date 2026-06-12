# existing-project-upgrade-lane Task Boundary

- Task: existing-project-upgrade-lane
- 负责人: Codex
- 日期: 2026-06-12
- 相关 issue / doc: `.gstack/requirements/2026-06-12_existing-project-upgrade-lane-fast-lane-requirement.md`

## Goal

- 支持插件更新后对已有项目做增量骨架改造：先生成升级计划，再执行安全、幂等的项目布局修复，不要求新建项目或重新接入。

## Allowed Files

- `.gstack/requirements/2026-06-12_existing-project-upgrade-lane-fast-lane-requirement.md`
- `.gstack/reviews/2026-06-12_existing-project-upgrade-lane-fast-lane-review.md`
- `.gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md`
- `.gstack/qa-reports/2026-06-12_existing-project-upgrade-lane-qa.md`
- `scripts/init_project.py`
- `tests/test_init_project.py`
- `plugins/kk-dev-skeleton-adoption/.codex-plugin/plugin.json`
- `plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption/SKILL.md`
- `plugins/PARTNER_INSTALL.md`
- `plugins/MARKETPLACE_ROLLOUT.md`
- `README.md`
- `CODEX_ADOPTION_CONNECTOR.md`

## Forbidden Files

- 伙伴或试点项目真实代码：`/Users/edy/work/codespace/ai/task-manager-cp/**`
- marketplace manifest：`.agents/plugins/marketplace.json`
- 当前机器 Codex plugin cache / personal marketplace
- 数据库配置、真实凭证、`.env*`、`.gstack/data-access/*.local.*`
- git workflow action，除非用户另行明确批准

## Functional Non-goals

- 不自动覆盖 adapter。
- 不自动移动根目录业务代码。
- 不全量同步 framework core 文件。
- 不修改真实试点项目。
- 不执行 commit、push 或发布动作，除非用户另行明确批准。

## User-visible Acceptance

- 已有项目可以通过自然语言请求“升级当前项目到新版 KK Dev Skeleton”。
- Codex 先输出增量升级计划，不要求重新接入新项目。
- 安全应用只创建缺失的 `stack/<adapter>/` layout。
- 根目录业务代码只列为迁移候选。

## Generated Artifact Policy

- User-visible Change: `no`
- Artifact Type: `python helper, plugin skill text, markdown docs, unit tests`
- Acceptance Surface:
  - `scripts/init_project.py`
  - `plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption/SKILL.md`
  - `tests/test_init_project.py`
- Browser QA: `not-required`
- Reason:
  本次可验证面是 CLI helper 输出和插件 workflow 文本，不改变 Web UI、HTML、dashboard 或可视化交互。

## Decision Mode

- Mode: `自主执行`
- Source: `repo-default`
- Internal Enum: `codex-led`
- Reason:
  用户目标明确，方案为低风险 helper / plugin workflow 增强。

## Flow Lane

- Lane: `fast-lane`
- Reason:
  小范围工具增强，无业务口径多解、生产操作、DB schema 或真实数据。
- Evidence Strategy:
  - 使用 fast-lane requirement、fast-lane review、boundary 和 QA evidence。

## Autonomy Plan

- Codex May Do Without Asking:
  - 在 Allowed Files 内实现升级计划和安全 apply。
  - 运行本地测试、插件校验和 gstack guards。
- Codex Must Ask Before:
  - 自动覆盖 adapter。
  - 自动移动业务代码。
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
  fast-lane 小任务由 main agent 直接完成即可。
- Main Agent Owns:
  - 流程控制、实现、验证、最终答复
- Candidate Subagents:
  - name: `not-used`
    role: `reviewer`
    trigger stage: `review`
    write scope: `read-only`
    forbidden paths:
      - `scripts/init_project.py`
    output evidence: `.gstack/qa-reports/2026-06-12_existing-project-upgrade-lane-qa.md`
    status: `not-used`
- Result Integration:
  - 验证结果写入 QA 报告和 final summary。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-12_existing-project-upgrade-lane-fast-lane-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-12_existing-project-upgrade-lane-fast-lane-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-12_existing-project-upgrade-lane-fast-lane-requirement.md`
  note: fast-lane requirement 同时作为 requirement freeze。
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-12_existing-project-upgrade-lane-fast-lane-review.md`
- domain-spec-readiness:
  status: not-required
  evidence: `.gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md`
  note: 本次不改变 stack domain 产品或工程真源。
- implement:
  status: done
  evidence: `.gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md`
- qa:
  status: done
  command: qa-only
  evidence: `.gstack/qa-reports/2026-06-12_existing-project-upgrade-lane-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "本任务不涉及真实数据、接口、查数或数据源选择"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据源 / 接口 / 查数"
  - gate_id: data-query
    trigger_reason: "本任务不涉及复杂查数或高风险指标"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不需要 Query Brief、SQL 或查询 review"
  - gate_id: prototype-logic-extraction
    trigger_reason: "本任务不涉及前端 / 原型业务逻辑迁后端"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确没有前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；本轮不使用 subagent"
  - gate_id: doc-backfill
    trigger_reason: "本任务不是代码已有但文档缺失的 backfill 场景"
    owner: kk-doc-backfill
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "新增文档同步创建，不需要从代码反推"
  - gate_id: data-knowledge-sync
    trigger_reason: "本任务不新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md"
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
- `/Users/edy/.codex/skills/.system/plugin-creator/SKILL.md`

## Spec Sync Plan

- Spec Impact: `not-required`
- Expected Spec Targets:
  - 不适用
- Prototype Logic Evidence Sync:
  不适用。
- Allowed No-Spec-Change Reason:
  本次为骨架 helper 和插件 workflow 增强，不改变具体应用 stack domain 产品或工程真源。

## Verification

- `python3 -m unittest tests/test_init_project.py`
- `python3 -m unittest tests/test_git_marketplace_publish_docs.py tests/test_marketplace_rollout_docs.py tests/test_plugin_marketplace.py tests/test_plugin_update_check.py tests/test_init_project.py`
- `python3 -m py_compile scripts/init_project.py tests/test_init_project.py`
- `python3 scripts/init_project.py --adapter default --upgrade-plan --format json`
- `python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py plugins/kk-dev-skeleton-adoption`
- `python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/kk-dev-skeleton-adoption`
- `python3 /Users/edy/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`
- `python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md`

## Lessons To Write Back

- 如发现新坑，写入 `.gstack/knowledge/` 或 `.gstack/rules/`。
