# Task Boundary: 低风险阶段自动串联

- Task: 低风险阶段自动串联
- 负责人: Codex
- 日期: 2026-06-24
- 相关 issue / doc:
  - `.gstack/requirements/2026-06-24_low-risk-phase-autochain-requirement.md`
  - `.gstack/reviews/2026-06-24_low-risk-phase-autochain-review.md`

## Goal

把“低风险任务完成后自动串联下一段低风险任务”固化到公开骨架 runtime、kk-* skills、知识层和自然语言 smoke。

## Allowed Files

- `AGENTS.md`
- `.gstack/requirements/2026-06-24_low-risk-phase-autochain-requirement.md`
- `.gstack/reviews/2026-06-24_low-risk-phase-autochain-review.md`
- `.gstack/task-boundaries/2026-06-24_low-risk-phase-autochain.md`
- `.gstack/qa-reports/2026-06-24_low-risk-phase-autochain-qa.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/natural-language-dev-regression-cases.md`
- `.gstack/scripts/nontechnical_continue.py`
- `.gstack/scripts/nontechnical_delivery_summary.py`
- `.gstack/scripts/natural_language_dev_smoke.py`
- `.gstack/skills/kk-task-kickoff/SKILL.md`
- `.gstack/skills/kk-natural-language-dev/SKILL.md`

## Forbidden Files

- `adapters/*/app/**`
- `examples/**`
- `archive/**`
- `stack/**`
- `.env`
- `.env.*`
- `secrets/`
- 真实数据、生产配置、DB schema、业务页面实现、部署脚本或外部服务接入

## Functional Non-goals

- 不实现真实后台 agent 服务。
- 不改目标业务项目功能、API、数据合同、runner 逻辑或真实服务接入。
- 不执行 commit、push、PR、生产、数据库、真实数据或破坏性动作。
- 不移除交付总结的下一步建议；只让它表达下一步是否由 Codex 自动继续。

## User-visible Acceptance

- User-visible Change: yes
- Expected Visible Behavior:
  - 用户只说“继续做”时，如果当前任务未完成，Codex 继续当前本地可证明步骤。
  - 如果当前低风险任务已完成，且下一项仍是本地可验证低风险任务，Codex 会说明可自动开启下一段任务记录继续推进。
  - 交付总结仍包含下一步建议，但会说明低风险建议不是暂停点。
  - 下一项涉及业务方向、多种设计选择、真实数据、生产、数据库、破坏性命令或代码提交流程时，Codex 仍暂停确认。
- User Actions To Verify:
  - Codex 运行本地 helper 和 smoke 命令。
- Required Evidence:
  `.gstack/qa-reports/2026-06-24_low-risk-phase-autochain-qa.md`

## Generated Artifact Policy

- Surface Type: CLI-output
- Acceptance URL: 不适用；使用 helper / smoke CLI 输出验收。
- Refresh / Regeneration:
  从仓库根目录重新运行 helper / smoke 命令。
- If No Visible Change:
  如果用户看不到行为变化，优先检查目标项目是否已同步 runtime bundle、active boundary 是否可解析、以及自然语言 helper 是否来自当前骨架版本。
- Required Interaction Evidence:
  本轮不改 app page、HTML artifact、本地 HTTP server 或浏览器渲染 UI；Browser / Chrome / Playwright 不适用。

## Decision Mode

- Mode: 自主执行
- Source: user-this-task
- Internal Enum: codex-led
- Reason:
  用户已授权继续同步公开骨架，任务不涉及业务多解或高风险动作。

## Flow Lane

- Lane: fast-lane
- Reason:
  是 `.gstack` framework runtime 和文档同步的小范围增强，可本地验证。
- Evidence Strategy:
  使用 fast-lane requirement、review、boundary 和 QA evidence。

## Autonomy Plan

- Codex May Do Without Asking:
  - 更新允许范围内的 `.gstack` runtime、skill、knowledge 和 evidence。
  - 运行本地验证、smoke、adapter validate 和 runtime verify。
- Codex Must Ask Before:
  - 生产、数据库、真实数据、部署、破坏性命令、git workflow action 或超出本 boundary 的业务实现。
- Low-risk Phase Auto-chain:
  当前低风险任务完成后，如果 phase plan、交付总结或下一步建议里的下一项仍是本地可验证低风险任务，Codex 应自动创建或激活下一段最小 boundary 并继续推进；每段仍必须有范围、验收口径和 QA evidence。
- Gate Recovery:
  Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户。
- Goal Mode: not-used
  本轮可在当前会话内完成。
- Local Restart:
  `not-required`，本轮不启动业务应用。

## Subagent Plan

- Mode: not-used
- Reason:
  当前任务是 fast-lane、单一协作层语义同步；写入范围集中在 `.gstack` runtime / skill / knowledge，无互不重叠 worker 写集。本轮用户授权继续同步，但没有显式要求启动 subagent；按当前工具约束不额外 spawn，用 smoke、adapter verify、runtime verify 和 guard 覆盖复核。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-24_low-risk-phase-autochain-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-24_low-risk-phase-autochain-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-24_low-risk-phase-autochain-requirement.md`
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-24_low-risk-phase-autochain-review.md`
- domain-spec-readiness:
  status: not-required
  evidence: `.gstack/task-boundaries/2026-06-24_low-risk-phase-autochain.md`
- implement:
  status: done
  evidence: `.gstack/scripts/nontechnical_continue.py`, `.gstack/scripts/nontechnical_delivery_summary.py`, `.gstack/scripts/natural_language_dev_smoke.py`, `AGENTS.md`, `.gstack/skills/`, `.gstack/knowledge/`
- qa:
  status: done
  evidence: `.gstack/qa-reports/2026-06-24_low-risk-phase-autochain-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "不涉及真实数据、数据库、BI、接口接入或查数。"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-24_low-risk-phase-autochain.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "不涉及数据专项。"
  - gate_id: prototype-logic-extraction
    trigger_reason: "不涉及前端 / 原型业务逻辑迁后端。"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-24_low-risk-phase-autochain.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "不涉及原型逻辑迁移。"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent；本轮不使用并说明原因。"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-24_low-risk-phase-autochain.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan。"
  - gate_id: data-knowledge-sync
    trigger_reason: "不新增或调整后端 API、DTO、migration、表、读模型、快照或 projection。"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-24_low-risk-phase-autochain.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "不涉及数据知识同步。"
  - gate_id: ui-design-quality
    trigger_reason: "本轮不涉及页面、HTML、dashboard、可视化或 UI 质量改动。"
    owner: kk-ui-design-kickoff
    required_before: implement
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-24_low-risk-phase-autochain.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "不涉及 UI 质量专项。"
```

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/context-isolation.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/natural-language-dev-regression-cases.md`
- `.gstack/skills/kk-task-kickoff/SKILL.md`
- `.gstack/skills/kk-natural-language-dev/SKILL.md`

## Spec Sync Plan

- Spec Impact: updated
- Expected Spec Targets:
  - `AGENTS.md`
  - `.gstack/knowledge/ai-programming-framework.md`
  - `.gstack/knowledge/natural-language-dev-regression-cases.md`
  - `.gstack/skills/kk-task-kickoff/SKILL.md`
  - `.gstack/skills/kk-natural-language-dev/SKILL.md`
- Prototype Logic Evidence Sync:
  不适用。
- Allowed No-Spec-Change Reason:
  不适用；本轮已同步 framework knowledge / skill 真源。

## Verification

- `python3 -m py_compile .gstack/scripts/nontechnical_continue.py .gstack/scripts/nontechnical_delivery_summary.py .gstack/scripts/natural_language_dev_smoke.py`
- `python3 .gstack/scripts/nontechnical_continue.py --raw "继续做" --format user`
- `python3 .gstack/scripts/nontechnical_delivery_summary.py --raw "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险" --format user`
- `python3 .gstack/scripts/natural_language_dev_smoke.py --format user`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `python3 -m unittest discover -s tests`
- `python3 scripts/init_project.py --adapter default --validate-adapter --report`
- `python3 scripts/init_project.py --adapter default --verify-runtime --report`
- `git diff --check`

## Lessons To Write Back

- 低风险任务完成后，若下一段仍是本地可验证低风险任务，下一步建议不是暂停点；Codex 应自动创建或激活下一段 boundary 并继续推进。
- 交付总结需要区分低风险自动继续、业务决策等待用户、高风险动作等待明确授权。
