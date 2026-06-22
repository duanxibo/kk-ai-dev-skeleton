# UI Optimization Autoguard Task Boundary

- Task: strengthen automatic UI optimization routing and safeguards
- Date: 2026-06-22
- Flow Lane: `fast-lane`

## Goal

Make short requests such as “进行 UI 优化” automatically route to the UI quality workflow without requiring the user to name `kk-ui-design-kickoff`, `kk-ui-polish-review`, browser QA, or internal gates.

## Allowed Files

- `.gstack/requirements/2026-06-22_ui-optimization-autoguard-requirement.md`
- `.gstack/reviews/2026-06-22_ui-optimization-autoguard-review.md`
- `.gstack/task-boundaries/2026-06-22_ui-optimization-autoguard.md`
- `.gstack/qa-reports/2026-06-22_ui-optimization-autoguard-qa.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/scripts/nontechnical_ui_optimization.py`
- `.gstack/scripts/nontechnical_intent_router.py`
- `.gstack/scripts/nontechnical_next_step.py`
- `.gstack/scripts/natural_language_dev_smoke.py`
- `.gstack/skills/kk-natural-language-dev/SKILL.md`
- `.gstack/skills/kk-task-kickoff/SKILL.md`
- `.gstack/skills/kk-ui-design-kickoff/SKILL.md`
- `.gstack/skills/kk-ui-polish-review/SKILL.md`
- `scripts/init_project.py`
- `adapters/default/runtime.json`
- `adapters/default/core_manifest.json`

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
- real data, production configuration, app UI implementation, database schema, external service integration, and git workflow actions

## Functional Non-goals

- Do not redesign any actual page in this task.
- Do not introduce a Figma or external design service dependency.
- Do not change data, API, runner, adapter business semantics, production, database, or git workflow behavior.

## User-visible Acceptance

- User-visible Change: `no`
- Expected Visible Behavior:
  - A user can say “进行 UI 优化”.
  - The natural-language helper explains that Codex will automatically do UI design preparation, implementation, visual review, and browser acceptance.
  - The user is not asked to name internal skills or gates.
- User Actions To Verify:
  - Run `python3 .gstack/scripts/nontechnical_next_step.py --raw "进行 UI 优化" --format user`.
- Required Evidence:
  CLI output and smoke tests.
- If No User-visible Change:
  Not applicable.

## Generated Artifact Policy

- Surface Type: `CLI-output`
- Acceptance URL: `not-applicable`
- Refresh / Regeneration:
  Re-run the helper and smoke commands from the repository root.
- Required Interaction Evidence:
  Browser QA is not required for this helper-only task because no app page, HTML artifact, local HTTP server, or browser-rendered UI is changed; actual UI implementation tasks still require browser QA.

## Decision Mode

- Mode: `自主执行`
- Reason:
  The user explicitly asked to continue strengthening the skeleton capability. No high-risk action is needed.

## Flow Lane

- Lane: `fast-lane`
- Reason:
  Scoped deterministic helper and smoke enhancement.

## Autonomy Plan

- Codex May Do Without Asking:
  - Update allowed framework core files.
  - Run local validation and smoke commands.
  - Sync safe runtime files to the already-created target project.
- Codex Must Ask Before:
  - Commit, push, PR, production, database, real data, destructive command, or actual app UI redesign.
- Goal Mode: `not-used`

## Subagent Plan

- Mode: `not-used`
- Reason:
  The scope is deterministic helper routing and tests.

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-22_ui-optimization-autoguard-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-22_ui-optimization-autoguard-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-22_ui-optimization-autoguard-requirement.md`
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-22_ui-optimization-autoguard-review.md`
- domain-spec-readiness:
  status: done
  evidence: `.gstack/knowledge/ai-programming-framework.md`
- implement:
  status: done
  evidence: `.gstack/scripts/nontechnical_ui_optimization.py`
- qa:
  status: done
  evidence: `.gstack/qa-reports/2026-06-22_ui-optimization-autoguard-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "Framework helper routing only; no real data, source system, SQL, API, or data scope change."
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-22_ui-optimization-autoguard.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "No data source or API semantics are touched."
  - gate_id: data-query
    trigger_reason: "No SQL or analytics query is needed."
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-22_ui-optimization-autoguard.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "No query brief or SQL draft is needed."
  - gate_id: prototype-logic-extraction
    trigger_reason: "No frontend/prototype/mock business logic is being migrated to backend/service code."
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-22_ui-optimization-autoguard.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "No prototype parity or backend-owned logic transfer."
  - gate_id: ui-design-quality
    trigger_reason: "This task strengthens automatic UI optimization routing and must prove the UI quality workflow is selected for terse user wording."
    owner: kk-ui-design-kickoff
    required_before: implement
    status: done
    evidence_path: ".gstack/scripts/natural_language_dev_smoke.py"
    evidence_section: "ui optimization smoke"
    blocking_reason: ""
    done_criteria: "The route and next-step smoke verify that '进行 UI 优化' selects UI design preparation, implementation, polish review, and browser QA safeguards."
  - gate_id: data-knowledge-sync
    trigger_reason: "No API, DTO, read model, table, persistence, or data contract change."
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-22_ui-optimization-autoguard.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "No data knowledge sync needed."
  - gate_id: subagent-plan
    trigger_reason: "Subagent usage considered and not needed."
    owner: kk-subagent-orchestrator
    required_before: implement
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-22_ui-optimization-autoguard.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "Subagent Plan records Mode: not-used."
  - gate_id: doc-backfill
    trigger_reason: "No undocumented implemented behavior is being backfilled."
    owner: kk-doc-backfill
    required_before: qa
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-22_ui-optimization-autoguard.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "No doc backfill needed."
```

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/task-boundaries/CURRENT.md`
- `adapters/default/adapter.md`
- `adapters/default/runtime.json`
- `.gstack/skills/kk-task-kickoff/SKILL.md`
- `.gstack/skills/kk-task-kickoff/references/workflow.md`
- `.gstack/skills/kk-task-kickoff/references/boundary-checklist.md`

## Spec Sync Plan

- Spec Impact: `updated`
- Expected Spec Targets:
  - `.gstack/knowledge/ai-programming-framework.md`
  - `.gstack/skills/kk-natural-language-dev/SKILL.md`
  - `.gstack/skills/kk-task-kickoff/SKILL.md`
  - `adapters/default/runtime.json`
  - `adapters/default/core_manifest.json`
- Allowed No-Spec-Change Reason: not applicable.

## Verification

```bash
python3 -m py_compile .gstack/scripts/nontechnical_ui_optimization.py .gstack/scripts/nontechnical_intent_router.py .gstack/scripts/nontechnical_next_step.py .gstack/scripts/natural_language_dev_smoke.py scripts/init_project.py
python3 .gstack/scripts/nontechnical_intent_router.py --raw "进行 UI 优化" --format json
python3 .gstack/scripts/nontechnical_next_step.py --raw "进行 UI 优化" --format json
python3 .gstack/scripts/natural_language_dev_smoke.py --format user
python3 -m unittest discover -s tests
python3 scripts/init_project.py --adapter default --validate-adapter --report
python3 scripts/init_project.py --adapter default --verify-runtime --report
python3 .gstack/scripts/gstack_doctor.py check
python3 .gstack/scripts/spec_sync_guard.py
git diff --check
```

## Lessons To Write Back

- Terse UI requests must be deterministic natural-language routes, not just prose in a skill.
