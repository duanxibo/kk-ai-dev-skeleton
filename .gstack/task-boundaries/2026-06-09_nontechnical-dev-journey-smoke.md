# Task Boundary：nontechnical-dev-journey-smoke

- Task: nontechnical-dev-journey-smoke
- 负责人: Codex
- 日期: 2026-06-09
- 相关 issue / doc:
  - `.gstack/requirements/2026-06-09_nontechnical-dev-journey-smoke.md`
  - `.gstack/reviews/2026-06-09_nontechnical-dev-journey-smoke-review.md`

## Goal

- Provide a stable example task for natural-language development smoke checks.

## Allowed Files

- `.gstack/task-boundaries/2026-06-09_nontechnical-dev-journey-smoke.md`
- `.gstack/requirements/2026-06-09_nontechnical-dev-journey-smoke.md`
- `.gstack/reviews/2026-06-09_nontechnical-dev-journey-smoke-review.md`
- `.gstack/qa-reports/2026-06-09_nontechnical-dev-journey-smoke-qa.md`
- `examples/simple-web-app/**`

## Forbidden Files

- `.env`
- `.env.*`
- `secrets/**`
- production configs
- real data

## Functional Non-goals

- 不连接真实数据。
- 不写数据库。
- 不发布。
- 不执行代码提交流程。

## User-visible Acceptance

- User-visible Change:
  `yes`
- Expected Visible Behavior:
  - 用户能看到一个示例任务已经完成。
  - 用户能看到怎么验收自然语言开发关键路径。
  - 用户能拿到一段团队可读的交付总结。
- User Actions To Verify:
  - 运行 dashboard explain 查看当前任务。
  - 运行 dashboard verify 查看验收步骤。
  - 运行 delivery summary 生成团队说明。
- Required Evidence:
  `CLI 输出 / QA 报告`
- If No User-visible Change:
  不适用。

## Generated Artifact Policy

- Surface Type:
  `CLI-output / docs-only`
- Acceptance URL:
  `不适用`
- Refresh / Regeneration:
  重新运行相关 `.gstack/scripts/*.py` helper。
- If No Visible Change:
  确认当前任务 query 是 `nontechnical-dev-journey-smoke`。
- Required Interaction Evidence:
  不涉及 HTML 交互。

## Decision Mode

- Mode: `autonomous`
- Source:
  `repo-default`
- Internal Enum:
  `codex-led`
- Reason:
  示例任务只用于 smoke，风险低。

## Flow Lane

- Lane: `fast-lane`
- Reason:
  示例任务明确、低风险、可本地验证。
- Evidence Strategy:
  - fast-lane requirement, review, boundary, QA.

## Autonomy Plan

- Codex May Do Without Asking:
  - 读取示例任务记录。
  - 生成 dashboard、readiness、verify、delivery summary。
- Codex Must Ask Before:
  - git workflow action
  - production action
  - real data access
  - database changes
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户`
- Goal Mode:
  `not-used`
- Local Restart:
  `not-required`

## Subagent Plan

- Mode: `not-used`
- Reason:
  示例任务无需 subagent。
- Main Agent Owns:
  - smoke evidence.
- Candidate Subagents:
  - name: `not-used`
    role: `reviewer`
    trigger stage: `qa`
    write scope: `read-only`
    forbidden paths:
      - `**`
    output evidence: `.gstack/qa-reports/2026-06-09_nontechnical-dev-journey-smoke-qa.md`
    status: `not-used`
- Result Integration:
  - 不适用。

## GStack Required Flow

- requirement-brief:
  status: `done`
  evidence: `.gstack/requirements/2026-06-09_nontechnical-dev-journey-smoke.md`
- plan-ceo-review:
  status: `done`
  evidence: `.gstack/reviews/2026-06-09_nontechnical-dev-journey-smoke-review.md`
- requirement-freeze:
  status: `done`
  evidence: `.gstack/requirements/2026-06-09_nontechnical-dev-journey-smoke.md`
- plan-eng-review:
  status: `done`
  evidence: `.gstack/reviews/2026-06-09_nontechnical-dev-journey-smoke-review.md`
- domain-spec-readiness:
  status: `not-required`
  evidence: `examples/simple-web-app/stack/specs/requirements.md examples/simple-web-app/stack/specs/frontend.md examples/simple-web-app/stack/specs/testing.md`
- implement:
  status: `done`
  evidence: `examples/simple-web-app/stack/frontend/index.html`
- qa:
  status: `done`
  command: `qa-only`
  evidence: `.gstack/qa-reports/2026-06-09_nontechnical-dev-journey-smoke-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "示例不涉及真实数据源、接口、查数或外部系统。"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: "不适用"
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "不涉及数据专项"
  - gate_id: prototype-logic-extraction
    trigger_reason: "示例没有把前端或原型业务逻辑迁移到后端。"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: "不适用"
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "不涉及原型逻辑承接"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent。"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-09_nontechnical-dev-journey-smoke.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "已声明不使用 subagent"
```

## Required Knowledge

- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/natural-language-dev-regression-cases.md`

## Spec Sync Plan

- Spec Impact:
  `not-required`
- Expected Spec Targets:
  - `examples/simple-web-app/stack/specs/requirements.md`
  - `examples/simple-web-app/stack/specs/frontend.md`
  - `examples/simple-web-app/stack/specs/testing.md`
- If Not Required, Why:
  示例 spec 已覆盖 smoke 所需行为。

## Verification

- `python3 .gstack/scripts/gstack_dashboard.py explain --query nontechnical-dev-journey-smoke --limit 1`
- `python3 .gstack/scripts/gstack_dashboard.py verify --query nontechnical-dev-journey-smoke --limit 1`
- `python3 .gstack/scripts/nontechnical_delivery_summary.py --query nontechnical-dev-journey-smoke --format user`

## Lessons To Write Back

- 公开骨架需要保留一个最小 example task evidence，才能验证 dashboard、readiness、verify 和 delivery summary 的端到端行为。
