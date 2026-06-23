# Delivery Summary Next-Step Task Boundary

- Task: 交付总结下一步建议强制输出
- Date: 2026-06-23
- Flow Lane: `fast-lane`

## Goal

让交付总结和最终完成收口默认包含 `下一步建议`。

## Allowed Files

- `AGENTS.md`
- `.gstack/requirements/2026-06-23_delivery-summary-next-step-requirement.md`
- `.gstack/reviews/2026-06-23_delivery-summary-next-step-review.md`
- `.gstack/task-boundaries/2026-06-23_delivery-summary-next-step.md`
- `.gstack/qa-reports/2026-06-23_delivery-summary-next-step-qa.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/natural-language-dev-regression-cases.md`
- `.gstack/scripts/nontechnical_delivery_summary.py`
- `.gstack/scripts/nontechnical_intent_router.py`
- `.gstack/scripts/natural_language_dev_smoke.py`
- `.gstack/skills/kk-natural-language-dev/SKILL.md`

## Forbidden Files

- `stack/`
- `archive/`
- `blueprint/`
- `shared/`
- `plugins/`
- `.agents/plugins/`
- `.env`
- `.env.*`
- `secrets/`
- real data, production configuration, app implementation, database schema, external service integration, and git workflow actions

## Functional Non-goals

- 不构建具体产品功能或 UI。
- 不改变 adapter 业务语义。
- 不执行 commit、push、PR、生产、数据库、真实数据、破坏性命令或外部服务动作。

## User-visible Acceptance

- User-visible Change: `yes`
- Expected Visible Behavior:
  - 交付总结结构化输出包含 `next_step_suggestions`。
  - 交付总结用户输出包含 `下一步建议`。
  - 下一步路由到交付总结时保留 `下一步建议`。
  - intent router 的交付总结说明也提到下一步建议。
- User Actions To Verify:
  - Run the delivery summary helper and natural-language smoke.
- Required Evidence:
  `.gstack/qa-reports/2026-06-23_delivery-summary-next-step-qa.md`

## Generated Artifact Policy

- Surface Type: `CLI-output`
- Acceptance URL: `not-applicable`
- Refresh / Regeneration:
  Re-run the helper and smoke commands from the repository root.
- Required Interaction Evidence:
  Browser QA is not required because no app page, HTML artifact, local HTTP server, or browser-rendered UI is changed.

## Decision Mode

- Mode: `自主执行`
- Reason:
  The user identified a deterministic skeleton gap. No high-risk action is needed.

## Flow Lane

- Lane: `fast-lane`
- Reason:
  Scoped helper and documentation enhancement with deterministic local verification.

## Autonomy Plan

- Codex May Do Without Asking:
  - Update allowed framework core files.
  - Run local validation and smoke commands.
  - Sync safe runtime files to the already-created target project.
- Codex Must Ask Before:
  - Commit, push, PR, production, database, real data, destructive command, or actual app implementation.
- Goal Mode: `not-used`

## Subagent Plan

- Mode: `not-used`
- Reason:
  The scope is deterministic helper routing and tests.

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-23_delivery-summary-next-step-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-23_delivery-summary-next-step-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-23_delivery-summary-next-step-requirement.md`
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-23_delivery-summary-next-step-review.md`
- domain-spec-readiness:
  status: done
  evidence: `.gstack/knowledge/ai-programming-framework.md`
- implement:
  status: done
  evidence: `.gstack/scripts/nontechnical_delivery_summary.py`
- qa:
  status: done
  evidence: `.gstack/qa-reports/2026-06-23_delivery-summary-next-step-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "Framework helper routing only; no real data, source system, SQL, API, or data scope change."
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-23_delivery-summary-next-step.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "No data source or API semantics are touched."
  - gate_id: ui-design-quality
    trigger_reason: "No UI, HTML, dashboard, visualization, or user interaction implementation is changed."
    owner: kk-ui-design-kickoff
    required_before: implement
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-23_delivery-summary-next-step.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "No UI quality gate is needed for helper-only text output."
  - gate_id: subagent-plan
    trigger_reason: "Subagent usage considered and not needed."
    owner: kk-subagent-orchestrator
    required_before: implement
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-23_delivery-summary-next-step.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "Subagent Plan records Mode: not-used."
```

## Spec Sync Plan

- Spec Impact: `updated`
- Expected Spec Targets:
  - `.gstack/knowledge/ai-programming-framework.md`
  - `.gstack/skills/kk-natural-language-dev/SKILL.md`
  - `AGENTS.md`

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/natural-language-dev-regression-cases.md`
- `.gstack/skills/kk-natural-language-dev/SKILL.md`

## Lessons To Write Back

- 已回写到 `.gstack/knowledge/ai-programming-framework.md`：
  交付总结和最终完成收口必须包含 `下一步建议`。
- 已回写到 `.gstack/knowledge/natural-language-dev-regression-cases.md`：
  natural-language smoke 必须覆盖交付总结输出中的 `下一步建议`。
- 已回写到 `AGENTS.md`：
  完成检查要求最终交付回复包含下一步建议修改。

## Verification

```bash
python3 -m py_compile .gstack/scripts/nontechnical_delivery_summary.py .gstack/scripts/nontechnical_intent_router.py .gstack/scripts/natural_language_dev_smoke.py
python3 .gstack/scripts/nontechnical_delivery_summary.py --raw "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险" --format json
python3 .gstack/scripts/nontechnical_delivery_summary.py --raw "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险" --format user
python3 .gstack/scripts/nontechnical_next_step.py --raw "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险" --format user
python3 .gstack/scripts/natural_language_dev_smoke.py --format user
python3 -m unittest discover -s tests
python3 scripts/init_project.py --adapter default --validate-adapter --report
python3 scripts/init_project.py --adapter default --verify-runtime --report
python3 .gstack/scripts/gstack_doctor.py check
python3 .gstack/scripts/spec_sync_guard.py
git diff --check
```
