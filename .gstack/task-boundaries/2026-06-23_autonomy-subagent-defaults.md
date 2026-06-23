# Task Boundary: 自主推进与 subagent 默认策略增强

- Task: 自主推进与 subagent 默认策略增强
- 负责人: Codex
- 日期: 2026-06-23
- 相关 issue / doc:
  - `.gstack/requirements/2026-06-23_autonomy-subagent-defaults-requirement.md`
  - `.gstack/reviews/2026-06-23_autonomy-subagent-defaults-review.md`

## Goal

把“少让用户反复说继续”和“主动评估 / 使用 subagent”固化到公开骨架自然语言开发 runtime，并同步到当前线上平台项目。

## Allowed Files

- `AGENTS.md`
- `.gstack/requirements/2026-06-23_autonomy-subagent-defaults-requirement.md`
- `.gstack/reviews/2026-06-23_autonomy-subagent-defaults-review.md`
- `.gstack/reviews/2026-06-23_autonomy-subagent-defaults-subagent-review.md`
- `.gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md`
- `.gstack/qa-reports/2026-06-23_autonomy-subagent-defaults-qa.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/natural-language-dev-regression-cases.md`
- `.gstack/scripts/nontechnical_confirmation_response.py`
- `.gstack/scripts/nontechnical_continue.py`
- `.gstack/scripts/nontechnical_execution_plan.py`
- `.gstack/scripts/nontechnical_intent_router.py`
- `.gstack/scripts/natural_language_dev_smoke.py`
- `.gstack/skills/kk-task-kickoff/SKILL.md`
- `.gstack/skills/kk-natural-language-dev/SKILL.md`
- `.gstack/skills/kk-subagent-orchestrator/SKILL.md`
- `.gstack/workflows/subagent-collaboration.md`

## Forbidden Files

- `adapters/*/app/**`
- `archive/`
- `.env`
- `.env.*`
- `secrets/`
- 真实数据、生产配置、DB schema、业务页面实现、部署脚本或外部服务接入。

## Functional Non-goals

- 不实现真实后台 agent 服务。
- 不改目标业务项目功能、API、数据合同、runner 逻辑或真实服务接入。
- 不执行 commit、push、PR、生产、数据库、真实数据或破坏性动作。

## User-visible Acceptance

- User-visible Change: yes
- Expected Visible Behavior:
  - 用户只说“我确认 / 可以”时，低风险任务说明应允许 Codex 继续本地推进，不要求用户重复说“继续”。
  - 继续推进说明应明确 Codex 会连续处理本地可证明步骤，不把工程实现顺序、测试组合、门禁恢复和 subagent 调度甩给用户。
  - 复杂任务执行计划应说明 Codex 会主动安排并行复核 / subagent 策略。
  - natural-language smoke 覆盖自主推进和 subagent 调度默认策略。
- User Actions To Verify:
  - Codex 运行本地 helper 和 smoke 命令。
- Required Evidence:
  `.gstack/qa-reports/2026-06-23_autonomy-subagent-defaults-qa.md`
- If No User-visible Change:
  不适用；本轮改变的是 Codex 对用户短确认和继续请求的可见回复与后续行为。

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
  用户指出骨架体验缺口，本轮不涉及业务多解或高风险动作。

## Flow Lane

- Lane: fast-lane
- Reason:
  是 `.gstack` framework runtime 和文档同步的小范围增强，可本地验证。
- Evidence Strategy:
  使用 fast-lane requirement、review、boundary 和 QA evidence。

## Autonomy Plan

- Codex May Do Without Asking:
  - 更新允许范围内的 `.gstack` runtime、skill、knowledge、workflow 和 evidence。
  - 同步当前新项目的 portable runtime。
  - 运行本地验证、smoke 和 guard。
- Codex Must Ask Before:
  - 生产、数据库、真实数据、部署、破坏性命令、git workflow action 或超出本 boundary 的业务实现。
- Gate Recovery:
  Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户。
- Goal Mode: not-used
  本轮可在当前会话内完成。
- Local Restart:
  `not-required`，本轮不启动业务应用。

## Subagent Plan

- Mode: review
- Reason:
  用户明确指出新项目看不到 subagent 使用；本轮需要把 read-only review 默认策略固化到公开骨架。
- Main Agent Owns:
  - 流程控制、active boundary、最终集成、验证和最终答复
- Candidate Subagents:
  - name: `autonomy-subagent-policy-reviewer`
    role: `reviewer`
    trigger stage: `review`
    write scope: `read-only`
    forbidden paths:
      - `adapters/*/app/**`
      - `archive/`
      - `.env`
      - `.env.*`
      - `secrets/`
    output evidence: `.gstack/reviews/2026-06-23_autonomy-subagent-defaults-subagent-review.md`
    status: done
- Result Integration:
  subagent / read-only review 结论回收到 review、skill、knowledge、smoke 和本 boundary；main agent 负责最终验证。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-23_autonomy-subagent-defaults-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-23_autonomy-subagent-defaults-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-23_autonomy-subagent-defaults-requirement.md`
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-23_autonomy-subagent-defaults-review.md`
- domain-spec-readiness:
  status: not-required
  evidence: `.gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md`
- implement:
  status: done
  evidence: `.gstack/scripts/nontechnical_confirmation_response.py`
- qa:
  status: done
  command: local smoke
  evidence: `.gstack/qa-reports/2026-06-23_autonomy-subagent-defaults-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "不涉及真实数据、数据库、BI、接口接入或查数。"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "不涉及数据专项。"
  - gate_id: data-query
    trigger_reason: "不涉及复杂查数或高风险指标。"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "不涉及数据查询专项。"
  - gate_id: prototype-logic-extraction
    trigger_reason: "不涉及前端 / 原型业务逻辑迁后端。"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "不涉及原型逻辑迁移。"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent；本轮使用 read-only review 策略。"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan 并说明结果回收。"
  - gate_id: doc-backfill
    trigger_reason: "不属于代码已有但文档缺失的 backfill 场景。"
    owner: kk-doc-backfill
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "不涉及 backfill。"
  - gate_id: data-knowledge-sync
    trigger_reason: "不新增或调整后端 API、DTO、migration、表、读模型、快照或 projection。"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "不涉及数据知识同步。"
  - gate_id: ui-design-quality
    trigger_reason: "本轮不涉及页面、HTML、dashboard、可视化或 UI 质量改动。"
    owner: kk-ui-design-kickoff
    required_before: implement
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md"
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
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/natural-language-dev-regression-cases.md`
- `.gstack/skills/kk-task-kickoff/SKILL.md`
- `.gstack/skills/kk-natural-language-dev/SKILL.md`
- `.gstack/skills/kk-subagent-orchestrator/SKILL.md`
- `.gstack/workflows/subagent-collaboration.md`

## Spec Sync Plan

- Spec Impact: updated
- Expected Spec Targets:
  - `.gstack/knowledge/ai-programming-framework.md`
  - `.gstack/knowledge/natural-language-dev-regression-cases.md`
  - `.gstack/skills/kk-task-kickoff/SKILL.md`
  - `.gstack/skills/kk-natural-language-dev/SKILL.md`
  - `.gstack/skills/kk-subagent-orchestrator/SKILL.md`
  - `.gstack/workflows/subagent-collaboration.md`
  - `AGENTS.md`
- Prototype Logic Evidence Sync:
  不适用。
- Allowed No-Spec-Change Reason:
  不适用；本轮已同步 framework knowledge / skill 真源。

## Verification

- `python3 -m py_compile .gstack/scripts/nontechnical_confirmation_response.py .gstack/scripts/nontechnical_continue.py .gstack/scripts/nontechnical_execution_plan.py .gstack/scripts/nontechnical_intent_router.py .gstack/scripts/natural_language_dev_smoke.py`
- `python3 .gstack/scripts/nontechnical_confirmation_response.py --raw "我确认" --format json`
- `python3 .gstack/scripts/nontechnical_continue.py --raw "继续做" --format user`
- `python3 .gstack/scripts/nontechnical_execution_plan.py --raw "我想做一个完整的经营看板，支持搜索筛选、数据同步、导出和多人验收" --audience "运营同事" --success "能按月份和 SKU 筛选并导出" --non-goal "不改生产数据库" --format json`
- `python3 .gstack/scripts/nontechnical_intent_router.py --raw "继续同步线上数据" --format json`
- `python3 .gstack/scripts/natural_language_dev_smoke.py --format user`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `git diff --check`

## Lessons To Write Back

- 已回写到 `.gstack/knowledge/ai-programming-framework.md`：
  低风险确认后应连续推进，subagent 策略由 Codex 自主评估。
- 已回写到 `.gstack/knowledge/natural-language-dev-regression-cases.md`：
  smoke 必须覆盖 active-task 低风险确认、continue、不把高风险继续误判为普通继续，以及执行计划中的 subagent 策略。

## 本地激活

- 正常情况下由 `$kk-task-kickoff` 自动完成。
- 本轮使用：
  `bash .gstack/scripts/use_boundary.sh .gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md`
