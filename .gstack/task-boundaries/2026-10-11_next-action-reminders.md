# Next action reminders and copyable user input

## Allowed Files
- `AGENTS.md`
- `QUICK_START_FOR_PARTNERS.md`
- `.gstack/skills/kk-natural-language-dev/SKILL.md`
- `.gstack/scripts/`
- `.gstack/knowledge/`
- `.gstack/task-boundaries/2026-10-11_next-action-reminders.md`
- `.gstack/requirements/2026-10-11_next-action-reminders.md`
- `.gstack/reviews/2026-10-11_next-action-reminders.md`
- `.gstack/qa-reports/2026-10-11_next-action-reminders.md`
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
- Background notifications, message sending, new-task authorization, deployment, automatic merge of the new PR

## User-visible Acceptance
- The home, progress, continuation and delivery views suggest a concrete next action and copyable user input without requiring technical knowledge.
- Missing, blocked, unverified and completed task states produce distinct safe reminders; suggestions never authorize new tasks or high-risk actions.
- Installed projects receive the reminder module and agent instructions; existing routes, acceptance checks and core-only installation continue working.

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
- Read-only independent review of merge and reminder authorization/compatibility; implementation remains with the primary agent.

## Required Gates
```yaml
required_gates:
- gate_id: subagent-plan
  trigger_reason: Cross-module framework review and bounded independent implementation
  owner: Codex
  required_before: implement
  status: done
  evidence_path: .gstack/reviews/2026-10-11_next-action-reminders.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: Agent reports reviewed and integrated
- gate_id: data-access
  trigger_reason: Framework-only work; no real data
  owner: Codex
  required_before: implement
  status: not-required
  evidence_path: .gstack/task-boundaries/2026-10-11_next-action-reminders.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: No real data access
- gate_id: ui-interaction-qa
  trigger_reason: Terminal guidance changes, verified through actual installed CLI interactions; no HTML layout change
  owner: Codex
  required_before: qa
  status: done
  evidence_path: .gstack/qa-reports/2026-10-11_next-action-reminders.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: CLI interactions cover entry, progress, pause, manual mode and delivery reminders.
- gate_id: prototype-logic-extraction
  trigger_reason: No frontend or prototype business logic involved
  owner: kk-task-kickoff
  required_before: plan-eng-review
  status: not-required
  evidence_path: .gstack/task-boundaries/2026-10-11_next-action-reminders.md
  evidence_section: ""
  blocking_reason: ""
  done_criteria: Framework validators only
```

## Required Knowledge
- CODEMAP, ai-programming-framework, adapter runtime, evidence policy

## Lessons To Write Back
- Next-action reminders are guidance, not authorization; make optional reply and required business decision distinct.

## Verification
- Unit tests, Loop contract smoke, natural-language smoke, source coverage and spec sync.

## Goal
- Provide state-aware next actions and copyable user input at existing entry and delivery surfaces.

## Collaboration Mode
- autonomous

## Plan Review
- Use one read-only reminder selector, additive JSON fields and explicit per-intent priority; preserve completion evidence and authorization boundaries.

## Spec Sync Plan
- Spec Impact: updated
- Expected Spec Targets:
  - README.md
  - .gstack/knowledge/ai-programming-framework.md

## GStack Required Flow
- requirement-brief:
  status: done
  evidence: .gstack/requirements/2026-10-11_next-action-reminders.md
- plan-ceo-review:
  status: done
  evidence: .gstack/reviews/2026-10-11_next-action-reminders.md
- requirement-freeze:
  status: done
  evidence: .gstack/requirements/2026-10-11_next-action-reminders.md
- plan-eng-review:
  status: done
  evidence: .gstack/reviews/2026-10-11_next-action-reminders.md
- domain-spec-readiness:
  status: not-required
  evidence: .gstack/task-boundaries/2026-10-11_next-action-reminders.md
  note: Framework contract documented in README and framework knowledge.
- implement:
  status: done
  evidence: .gstack/task-boundaries/2026-10-11_next-action-reminders.md
- qa:
  status: done
  evidence: .gstack/qa-reports/2026-10-11_next-action-reminders.md

## Acceptance Verification
```json
{"version": 1, "criteria": [{"id": "AC-1", "description": "The home, progress, continuation and delivery views suggest a concrete next action and copyable user input without requiring technical knowledge.", "command_keys": ["qa_verify"]}, {"id": "AC-2", "description": "Missing, blocked, unverified and completed task states produce distinct safe reminders; suggestions never authorize new tasks or high-risk actions.", "command_keys": ["qa_verify"]}, {"id": "AC-3", "description": "Installed projects receive the reminder module and agent instructions; existing routes, acceptance checks and core-only installation continue working.", "command_keys": ["qa_verify"]}]}
```
