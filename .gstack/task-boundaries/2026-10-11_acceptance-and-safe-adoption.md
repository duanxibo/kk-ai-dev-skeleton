# Acceptance verification and safe adoption

## Allowed Files
- `.gstack/scripts/`
- `.gstack/knowledge/`
- `.gstack/task-boundaries/2026-10-11_acceptance-and-safe-adoption.md`
- `.gstack/requirements/2026-10-11_acceptance-and-safe-adoption.md`
- `.gstack/reviews/2026-10-11_acceptance-and-safe-adoption.md`
- `.gstack/qa-reports/2026-10-11_acceptance-and-safe-adoption.md`
- `adapters/`
- `tests/`
- `scripts/init_project.py`
- `.github/workflows/ci.yml`
- `plugins/kk-dev-skeleton-adoption/.codex-plugin/plugin.json`
- `.gstack/templates/`
- `.gstack/workflows/`
- `examples/`
- `README.md`

## Forbidden Files
- Credentials, production and real data

## Functional Non-goals
- Full Loop refactoring, deployment, automatic merge

## User-visible Acceptance
- Every required acceptance criterion maps to successful verification; missing or changed task evidence blocks completion.
- Installed projects receive explicit QA setup and optional CI without overwriting existing pipelines.
- Runtime upgrades preflight conflicts and compatibility; failures restore the prior bundle and manifest.

## Generated Artifact Policy
- Logs and receipts are local artifacts; no secrets or generated dashboard committed.

## Decision Mode
- Mode: 自主执行

## Flow Lane
- Lane: standard

## Autonomy Plan
- Goal Mode: not-used

## Subagent Plan
- Mode: mixed
- Read-only review plus independent bounded source coverage and compact/release work.

## Required Gates
```yaml
required_gates:
- gate_id: subagent-plan
  trigger_reason: Cross-module framework review and bounded independent implementation
  owner: Codex
  required_before: implement
  status: done
  evidence_path: .gstack/reviews/2026-10-11_acceptance-and-safe-adoption.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: Agent reports reviewed and integrated
- gate_id: data-access
  trigger_reason: Framework-only work; no real data
  owner: Codex
  required_before: implement
  status: not-required
  evidence_path: .gstack/task-boundaries/2026-10-11_acceptance-and-safe-adoption.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: No real data access
- gate_id: ui-interaction-qa
  trigger_reason: No UI changes
  owner: Codex
  required_before: qa
  status: not-required
  evidence_path: .gstack/task-boundaries/2026-10-11_acceptance-and-safe-adoption.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: No visible surface changes
- gate_id: prototype-logic-extraction
  trigger_reason: No frontend or prototype business logic involved
  owner: kk-task-kickoff
  required_before: plan-eng-review
  status: not-required
  evidence_path: .gstack/task-boundaries/2026-10-11_acceptance-and-safe-adoption.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: Framework validators only
```

## Required Knowledge
- CODEMAP, ai-programming-framework, adapter runtime, evidence policy

## Lessons To Write Back
- Command success is not product acceptance; require frozen criteria and command mappings, meaningful target tests and reversible upgrades.

## Verification
- Unit tests, Loop contract smoke, natural-language smoke, source coverage and spec sync.

## Goal
- Bind acceptance to verification and verify real target adoption; isolate safe upgrade behavior without wholesale Loop refactoring.

## Collaboration Mode
- autonomous

## Plan Review
- Preserve low-level receipt inspection, but task completion requires acceptance coverage. Fail closed for unconfigured target QA. Small modules separate acceptance and runtime upgrade responsibility.

## Spec Sync Plan
- Spec Impact: updated
- Expected Spec Targets:
  - README.md
  - .gstack/knowledge/ai-programming-framework.md

## GStack Required Flow
- requirement-brief:
  status: done
  evidence: .gstack/requirements/2026-10-11_acceptance-and-safe-adoption.md
- plan-ceo-review:
  status: done
  evidence: .gstack/reviews/2026-10-11_acceptance-and-safe-adoption.md
- requirement-freeze:
  status: done
  evidence: .gstack/requirements/2026-10-11_acceptance-and-safe-adoption.md
- plan-eng-review:
  status: done
  evidence: .gstack/reviews/2026-10-11_acceptance-and-safe-adoption.md
- domain-spec-readiness:
  status: not-required
  evidence: .gstack/task-boundaries/2026-10-11_acceptance-and-safe-adoption.md
  note: Framework contract documented in README and framework knowledge.
- implement:
  status: done
  evidence: .gstack/task-boundaries/2026-10-11_acceptance-and-safe-adoption.md
- qa:
  status: done
  evidence: .gstack/qa-reports/2026-10-11_acceptance-and-safe-adoption.md

## Acceptance Verification
```json
{"version": 1, "criteria": [{"id": "AC-1", "description": "Every required acceptance criterion maps to successful verification; missing or changed task evidence blocks completion.", "command_keys": ["qa_verify"]}, {"id": "AC-2", "description": "Installed projects receive explicit QA setup and optional CI without overwriting existing pipelines.", "command_keys": ["qa_verify"]}, {"id": "AC-3", "description": "Runtime upgrades preflight conflicts and compatibility; failures restore the prior bundle and manifest.", "command_keys": ["qa_verify"]}]}
```
