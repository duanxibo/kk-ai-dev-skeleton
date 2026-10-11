# Evidence integrity and source coverage

## Allowed Files
- `.gstack/scripts/`
- `.gstack/knowledge/`
- `.gstack/task-boundaries/2026-10-11_evidence-integrity.md`
- `.gstack/requirements/2026-10-11_evidence-integrity.md`
- `.gstack/reviews/2026-10-11_evidence-integrity.md`
- `.gstack/qa-reports/2026-10-11_evidence-integrity.md`
- `adapters/`
- `tests/`
- `scripts/init_project.py`
- `.github/workflows/ci.yml`
- `plugins/kk-dev-skeleton-adoption/.codex-plugin/plugin.json`
- `README.md`

## Forbidden Files
- Credentials, production and real data

## Functional Non-goals
- Full Loop refactoring, deployment, automatic merge

## User-visible Acceptance
- Both evidence checkers agree; fabricated or stale QA cannot pass.
- Source paths outside adapter coverage are reported.
- Small task evidence is concise; release and upgrade behavior is explicit.

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
  evidence_path: .gstack/reviews/2026-10-11_evidence-integrity.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: Agent reports reviewed and integrated
- gate_id: data-access
  trigger_reason: Framework-only work; no real data
  owner: Codex
  required_before: implement
  status: not-required
  evidence_path: .gstack/task-boundaries/2026-10-11_evidence-integrity.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: No real data access
- gate_id: ui-interaction-qa
  trigger_reason: No UI changes
  owner: Codex
  required_before: qa
  status: not-required
  evidence_path: .gstack/task-boundaries/2026-10-11_evidence-integrity.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: No visible surface changes
- gate_id: prototype-logic-extraction
  trigger_reason: No frontend or prototype business logic involved
  owner: kk-task-kickoff
  required_before: plan-eng-review
  status: not-required
  evidence_path: .gstack/task-boundaries/2026-10-11_evidence-integrity.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: Framework validators only
```

## Required Knowledge
- CODEMAP, ai-programming-framework, adapter runtime, evidence policy

## Lessons To Write Back
- Textual QA claims are not execution evidence; coverage must be audited.

## Verification
- Unit tests, Loop contract smoke, natural-language smoke, source coverage and spec sync.

## Goal
- Repair evidence consistency, executed QA, source coverage and concise task/release contracts.

## Collaboration Mode
- autonomous

## Plan Review
- Fix reproducible validation bypasses before structural refactoring.

## Spec Sync Plan
- Spec Impact: updated
- Expected Spec Targets:
  - README.md
  - .gstack/knowledge/ai-programming-framework.md

## GStack Required Flow
- requirement-brief:
  status: done
  evidence: .gstack/requirements/2026-10-11_evidence-integrity.md
- plan-ceo-review:
  status: done
  evidence: .gstack/reviews/2026-10-11_evidence-integrity.md
- requirement-freeze:
  status: done
  evidence: .gstack/requirements/2026-10-11_evidence-integrity.md
- plan-eng-review:
  status: done
  evidence: .gstack/reviews/2026-10-11_evidence-integrity.md
- domain-spec-readiness:
  status: not-required
  evidence: .gstack/task-boundaries/2026-10-11_evidence-integrity.md
  note: Framework contract documented in README and framework knowledge.
- implement:
  status: done
  evidence: .gstack/task-boundaries/2026-10-11_evidence-integrity.md
- qa:
  status: done
  evidence: .gstack/qa-reports/2026-10-11_evidence-integrity.md
