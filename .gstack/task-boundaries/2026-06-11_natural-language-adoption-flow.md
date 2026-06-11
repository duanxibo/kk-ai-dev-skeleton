# 自然语言接入方式修正 Task Boundary

- Task: 自然语言接入方式修正
- 负责人: Codex
- 日期: 2026-06-11
- 相关 issue / doc: `.gstack/requirements/2026-06-11_natural-language-adoption-flow-fast-lane-requirement.md`

## Goal

- 将公司内接入指南从用户手动执行命令改为通过 Codex 自然语言完成接入。

## Allowed Files

- .gstack/requirements/2026-06-11_natural-language-adoption-flow-fast-lane-requirement.md
- .gstack/reviews/2026-06-11_natural-language-adoption-flow-fast-lane-review.md
- .gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md
- .gstack/qa-reports/<pending-qa-report>.md
- COMPANY_ADOPTION_GUIDE.md
- README.md
- .gstack/requirements/
- .gstack/reviews/
- .gstack/task-boundaries/
- .gstack/qa-reports/

## Forbidden Files

- adapters/
- .gstack/scripts/
- examples/
- app/
- src/
- .git/
- .idea/

## Functional Non-goals

- 不改运行脚本、guard 或 adapter runtime 行为。
- 不执行 git workflow action，不创建分支、commit、push 或 PR。
- 不修改示例应用或真实业务代码。

## User-visible Acceptance

- User-visible Change:
  `no`
- Expected Visible Behavior:
  - `README.md` 的接入说明不再要求业务用户手动执行初始化命令。
  - `COMPANY_ADOPTION_GUIDE.md` 明确写清：用户通过 Codex 自然语言完成接入，Codex 负责初始化、自检和证据沉淀。
- User Actions To Verify:
  - 打开 `README.md`，确认推荐接入方式是自然语言提示。
  - 打开 `COMPANY_ADOPTION_GUIDE.md`，确认新项目接入步骤以“对 Codex 说”开头。
- Required Evidence:
  `CLI 输出 / 文档内容检查 / rg 检查`
- If No User-visible Change:
  本轮是 docs-only 改动，没有页面、HTML、前端交互或应用行为变化；验收方式是打开 Markdown 文件并运行文档内容检查。

## Generated Artifact Policy

- Surface Type:
  `docs-only`
- Acceptance URL:
  不适用；本轮是仓库 Markdown 文档。
- Refresh / Regeneration:
  不需要生成；直接打开最新 `README.md` 和 `COMPANY_ADOPTION_GUIDE.md`。
- If No Visible Change:
  确认打开的是当前仓库最新文件，而不是旧分支、旧压缩包或旧文档副本。
- Required Interaction Evidence:
  不适用；本轮不是 HTML / 前端 / 可视化任务。

## Decision Mode

- Mode: `自主执行`
- Source:
  `user-this-task`
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
    output evidence: `.gstack/qa-reports/<pending-qa-report>.md`
    status: `not-used`
- Result Integration:
  - 本轮验证结果写入 QA 报告和 final summary。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-11_natural-language-adoption-flow-fast-lane-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-11_natural-language-adoption-flow-fast-lane-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-11_natural-language-adoption-flow-fast-lane-requirement.md`
  note: fast-lane requirement 同时作为 requirement freeze。
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-11_natural-language-adoption-flow-fast-lane-review.md`
- domain-spec-readiness:
  status: not-required
  evidence: `.gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md`
  note: 本次 fast-lane 小需求不改变 stack domain 产品或工程真源。
- implement:
  status: done
  evidence: `.gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md`
- qa:
  status: done
  command: qa-only
  evidence: `.gstack/qa-reports/2026-06-11_natural-language-adoption-flow-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "AI 已确认 fast-lane 不涉及真实数据、接口、查数或数据源选择；如实现中发现涉及，必须退出 fast-lane 或改为 planned"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确本任务不涉及数据源 / 接口 / 查数"
  - gate_id: data-query
    trigger_reason: "AI 已确认 fast-lane 不涉及复杂查数或高风险指标"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不需要 Query Brief、SQL 或查询 review"
  - gate_id: prototype-logic-extraction
    trigger_reason: "AI 已确认 fast-lane 不涉及前端 / 原型业务逻辑迁后端"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确没有前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；本轮不使用 subagent"
  - gate_id: doc-backfill
    trigger_reason: "AI 已确认 fast-lane 不是代码已有但文档缺失的 backfill 场景"
    owner: kk-doc-backfill
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "新增文档同步创建，不需要从代码反推"
  - gate_id: data-knowledge-sync
    trigger_reason: "AI 已确认 fast-lane 不新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md"
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
- `README.md`
- `COMPANY_ADOPTION_GUIDE.md`

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

- python3 .gstack/scripts/spec_sync_guard.py
- python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD
- python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md
- rg --hidden -n "在目标项目根目录内执行|复制到新项目后的最小步骤|用户.*执行.*python3|业务用户.*运行.*python3" COMPANY_ADOPTION_GUIDE.md README.md -S
- rg --hidden -n "通过 Codex|自然语言|对 Codex 说" COMPANY_ADOPTION_GUIDE.md README.md -S

## Lessons To Write Back

- 如发现新坑，写入 `.gstack/knowledge/` 或 `.gstack/rules/`。

## 本地激活

- 自动激活时由 `python3 .gstack/scripts/autopilot_bootstrap.py ... --activate` 写入本机 `CURRENT.local.md`。
