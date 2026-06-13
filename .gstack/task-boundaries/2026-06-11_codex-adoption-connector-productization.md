# codex-adoption-connector-productization Task Boundary

- Task: codex-adoption-connector-productization
- 负责人: Codex
- 日期: 2026-06-11
- 相关 issue / doc: `.gstack/requirements/2026-06-11_codex-adoption-connector-productization-fast-lane-requirement.md`

## Goal

- 沉淀内部安装器 / Codex 接入器的产品化路线，明确用户通过 Codex 自然语言接入，命令只作为 Codex 内部工具

## Allowed Files

- .gstack/requirements/2026-06-11_codex-adoption-connector-productization-fast-lane-requirement.md
- .gstack/reviews/2026-06-11_codex-adoption-connector-productization-fast-lane-review.md
- .gstack/task-boundaries/2026-06-11_codex-adoption-connector-productization.md
- .gstack/qa-reports/2026-06-11_codex-adoption-connector-productization-qa.md
- README.md
- COMPANY_ADOPTION_GUIDE.md
- CODEX_ADOPTION_CONNECTOR.md

## Forbidden Files

- adapter runtime、guard、doctor、smoke 和安装器脚本实现
- 应用代码、示例应用和测试夹具
- 数据库配置、真实凭证、`.env*`、`.gstack/data-access/*.local.*`
- git workflow action，除非用户另行明确批准

## Functional Non-goals

- 不实现新的内部安装器或 Codex plugin。
- 不调整 helper 脚本行为。
- 不引入真实项目业务规则。
- 不把接入流程改成业务用户手动执行命令。

## User-visible Acceptance

- 用户能从 README 或公司接入指南进入 Codex 接入器产品化方案。
- 文档清楚说明：当前给用户的是完整骨架包或内部模板仓库 + Codex 自然语言接入。
- 文档清楚说明：内部安装器和脚本由 Codex 调用，业务用户不需要手动执行。
- 文档清楚说明后续产品化阶段：内部安装器 -> Codex 接入器 / 内部 plugin -> 组织级产品化。

## Generated Artifact Policy

- User-visible Change: `no`
- Artifact Type: `repo documentation`
- Acceptance Surface: `markdown files`
- Browser QA: `not-required`
- Reason:
  本次仅更新 repo 文档和 evidence，不生成 HTML、页面、dashboard、截图或可交互 UI。

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
    output evidence: `.gstack/qa-reports/2026-06-11_codex-adoption-connector-productization-qa.md`
    status: `not-used`
- Result Integration:
  - 本轮验证结果写入 QA 报告和 final summary。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-11_codex-adoption-connector-productization-fast-lane-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-11_codex-adoption-connector-productization-fast-lane-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-11_codex-adoption-connector-productization-fast-lane-requirement.md`
  note: fast-lane requirement 同时作为 requirement freeze。
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-11_codex-adoption-connector-productization-fast-lane-review.md`
- domain-spec-readiness:
  status: not-required
  evidence: `.gstack/task-boundaries/2026-06-11_codex-adoption-connector-productization.md`
  note: 本次 fast-lane 小需求不改变 stack domain 产品或工程真源。
- implement:
  status: done
  evidence: `CODEX_ADOPTION_CONNECTOR.md`
- qa:
  status: done
  command: qa-only
  evidence: `.gstack/qa-reports/2026-06-11_codex-adoption-connector-productization-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "AI 已确认 fast-lane 不涉及真实数据、接口、查数或数据源选择；如实现中发现涉及，必须退出 fast-lane 或改为 planned"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-adoption-connector-productization.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确本任务不涉及数据源 / 接口 / 查数"
  - gate_id: data-query
    trigger_reason: "AI 已确认 fast-lane 不涉及复杂查数或高风险指标"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-adoption-connector-productization.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不需要 Query Brief、SQL 或查询 review"
  - gate_id: prototype-logic-extraction
    trigger_reason: "AI 已确认 fast-lane 不涉及前端 / 原型业务逻辑迁后端"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-adoption-connector-productization.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确没有前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-adoption-connector-productization.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；本轮不使用 subagent"
  - gate_id: doc-backfill
    trigger_reason: "AI 已确认 fast-lane 不是代码已有但文档缺失的 backfill 场景"
    owner: kk-doc-backfill
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-adoption-connector-productization.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "新增文档同步创建，不需要从代码反推"
  - gate_id: data-knowledge-sync
    trigger_reason: "AI 已确认 fast-lane 不新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-adoption-connector-productization.md"
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

- `python3 .gstack/scripts/spec_sync_guard.py`
- `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`
- `python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_codex-adoption-connector-productization.md`
- `rg --hidden -n "用户.*执行.*python3|业务用户.*运行.*python3|在目标项目根目录内执行|复制到新项目后的最小步骤" CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md -S`
- `rg --hidden -n "对 Codex 说|自然语言|Codex 接入器|内部安装器" CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md -S`
- `rg --hidden -n "lunhui|cohort|审批模块|review-service|源项目|source-project" CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md -S`

## Lessons To Write Back

- 如发现新坑，写入 `.gstack/knowledge/` 或 `.gstack/rules/`。

## 本地激活

- 自动激活时由 `python3 .gstack/scripts/autopilot_bootstrap.py ... --activate` 写入本机 `CURRENT.local.md`。
