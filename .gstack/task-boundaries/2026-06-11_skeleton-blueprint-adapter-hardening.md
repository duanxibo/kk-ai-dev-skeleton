# Task Boundary：skeleton-blueprint-adapter-hardening

- Task: skeleton-blueprint-adapter-hardening
- 负责人: Codex
- 日期: 2026-06-11
- 相关 issue / doc:
  - `.gstack/requirements/2026-06-11_skeleton-blueprint-adapter-hardening.md`
  - `.gstack/reviews/2026-06-11_skeleton-blueprint-adapter-hardening-review.md`

## Goal

- 补齐公开 AI 开发骨架缺失的协作蓝图、角色入口和 data-access 知识入口。
- 修复已发现的 skill Required Reading 断链。
- 降低框架核心里的项目专属残留，明确哪些能力应由 adapter 提供。

## Allowed Files

- `README.md`
- `AGENTS.md`
- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
- `.gstack/README.md`
- `.gstack/entrypoints/**`
- `.gstack/knowledge/**`
- `.gstack/skills/kk-*/SKILL.md`
- `.gstack/skills/kk-*/references/**`
- `.gstack/templates/**`
- `.gstack/workflows/**`
- `.gstack/scripts/gstack_doctor.py`
- `.gstack/scripts/nontechnical_task_starter.py`
- `.gstack/scripts/nontechnical_ci_failure.py`
- `.gstack/scripts/nontechnical_first_use.py`
- `.gstack/scripts/nontechnical_scope_change.py`
- `.gstack/scripts/nontechnical_team_sync.py`
- `.gstack/scripts/natural_language_dev_smoke.py`
- `.gstack/scripts/spec_sync_guard.py`
- `.gstack/scripts/required_gates_audit.py`
- `.gstack/scripts/team_flow_guard.py`
- `adapters/default/**`
- `.gstack/requirements/2026-06-11_skeleton-blueprint-adapter-hardening.md`
- `.gstack/reviews/2026-06-11_skeleton-blueprint-adapter-hardening-review.md`
- `.gstack/task-boundaries/2026-06-11_skeleton-blueprint-adapter-hardening.md`
- `.gstack/qa-reports/2026-06-11_skeleton-blueprint-adapter-hardening-qa.md`

## Forbidden Files

- `.env`
- `.env.*`
- `secrets/**`
- production configs
- real customer data
- 源项目 business specs, archived business evidence, or private data assets
- git workflow actions

## Functional Non-goals

- 不发布公司级 CLI。
- 不做完整 package manager 安装流程。
- 不把所有脚本彻底重构为多 adapter runtime。
- 不删除现有 `kk-*` skills。
- 不清理用户机器上的 `tg-*` symlink。

## User-visible Acceptance

- User-visible Change:
  `yes`
- Expected Visible Behavior:
  - 新用户能从 `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md` 理解骨架的协作架构。
  - `kk-task-kickoff` 和 `kk-data-*` 要求读取的核心文件存在。
  - 框架文档明确 core / adapter / runtime 边界。
  - 项目专属业务词不再作为默认公开骨架能力出现在关键用户入口中。
- User Actions To Verify:
  - 阅读 README、AGENTS、协作蓝图和 adapter。
  - 运行 doctor、spec guard 和自然语言 smoke。
- Required Evidence:
  `CLI 输出 / 文档扫描 / QA 报告`
- If No User-visible Change:
  不适用。

## Generated Artifact Policy

- Surface Type:
  `docs-only`
- Acceptance URL:
  `不适用`
- Refresh / Regeneration:
  重新打开或搜索仓库文档即可看到最新内容。
- If No Visible Change:
  如果用户在页面中看不到变化，原因是本轮是骨架文档和协作脚本硬化，不改变示例 app UI。
- Required Interaction Evidence:
  不涉及 UI 交互；以 CLI 检查和文档扫描为证据。

## Decision Mode

- Mode: `自主执行`
- Source:
  `user-this-task`
- Internal Enum:
  `codex-led`
- Reason:
  用户已同意继续，且本轮是低风险骨架硬化。

## Flow Lane

- Lane: `fast-lane`
- Reason:
  范围明确、低风险、可本地验证，不涉及真实数据、生产、数据库或 git workflow action。
- Evidence Strategy:
  - `fast-lane`：使用 fast-lane requirement、review、boundary 和 QA。

## Autonomy Plan

- Codex May Do Without Asking:
  - 新增和修正骨架文档。
  - 小范围修正文档断链和明显脚本文案残留。
  - 运行本地检查和 smoke。
- Codex Must Ask Before:
  - git workflow action
  - 发布包或创建远程仓库
  - 生产操作
  - 真实数据访问
  - DB schema 变更
  - 大规模脚本架构重构
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户`
- Goal Mode:
  `not-used`
- Local Restart:
  `not-required`

## Subagent Plan

- Mode: `not-used`
- Reason:
  本次是单一骨架硬化任务，范围清晰，无需 subagent。
- Main Agent Owns:
  - 文档补齐
  - 小范围脚本文案修正
  - QA evidence
- Candidate Subagents:
  - name: `not-used`
    role: `reviewer`
    trigger stage: `qa`
    write scope: `read-only`
    forbidden paths:
      - `**`
    output evidence: `.gstack/qa-reports/2026-06-11_skeleton-blueprint-adapter-hardening-qa.md`
    status: `not-used`
- Result Integration:
  - 不适用。

## GStack Required Flow

- requirement-brief:
  status: `done`
  evidence: `.gstack/requirements/2026-06-11_skeleton-blueprint-adapter-hardening.md`
- plan-ceo-review:
  status: `done`
  evidence: `.gstack/reviews/2026-06-11_skeleton-blueprint-adapter-hardening-review.md`
- requirement-freeze:
  status: `done`
  evidence: `.gstack/requirements/2026-06-11_skeleton-blueprint-adapter-hardening.md`
- plan-eng-review:
  status: `done`
  evidence: `.gstack/reviews/2026-06-11_skeleton-blueprint-adapter-hardening-review.md`
- domain-spec-readiness:
  status: `done`
  evidence: `.gstack/knowledge/ai-programming-framework.md adapters/default/adapter.md`
- implement:
  status: `done`
  evidence: `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md .gstack/entrypoints/ .gstack/knowledge/data-access/ adapters/default/forbidden-scopes.json`
- qa:
  status: `done`
  command: `qa-only`
  evidence: `.gstack/qa-reports/2026-06-11_skeleton-blueprint-adapter-hardening-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "本次不接真实数据，但需要补公开骨架 data-access 知识入口以满足 skill 断链。"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: done
    evidence_path: ".gstack/knowledge/data-access/README.md"
    evidence_section: "通用 data-access contract"
    blocking_reason: ""
    done_criteria: "已有通用 data-access 入口、source registry、query access 和 interface guide 占位，不包含真实连接或私有数据。"
  - gate_id: data-query
    trigger_reason: "本次不执行查数，只补通用数据查询说明入口。"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/knowledge/data-access/query-access-guide.md"
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "不执行 SQL、不连接真实数据库。"
  - gate_id: prototype-logic-extraction
    trigger_reason: "本次不迁移原型业务逻辑到后端。"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: "不适用"
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "不涉及原型逻辑承接。"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent。"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-11_skeleton-blueprint-adapter-hardening.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "已声明不使用 subagent。"
  - gate_id: doc-backfill
    trigger_reason: "本次属于骨架文档断链回填。"
    owner: kk-doc-backfill
    required_before: review
    status: done
    evidence_path: ".gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md"
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "断链文档已补齐或引用已修正。"
```

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/context-isolation.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/qa-dimensions.md`
- `adapters/default/adapter.md`

## Spec Sync Plan

- Spec Impact:
  `updated`
- Expected Spec Targets:
  - `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
  - `.gstack/entrypoints/`
  - `.gstack/knowledge/data-access/`
  - `.gstack/knowledge/ai-programming-framework.md`
  - `adapters/default/adapter.md`
- Prototype Logic Evidence Sync:
  不适用。
- Allowed No-Spec-Change Reason:
  不适用。

## Verification

- `python3 .gstack/scripts/gstack_doctor.py check`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `python3 .gstack/scripts/natural_language_dev_smoke.py`
- `rg --hidden` 检查 `源项目 / lunhui / cohort / product-review` 等私有业务残留。
- `rg --hidden` 检查新增断链引用。

## Lessons To Write Back

- 公开骨架必须有“断链检查”意识：skill Required Reading、templates 和 workflows 引用的文件必须随骨架一起发布，或明确标记为 adapter-provided。
