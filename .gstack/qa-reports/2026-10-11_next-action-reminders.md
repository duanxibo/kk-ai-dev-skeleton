# Next-action reminder QA
- AI 语义复核: yes
- Status: done
- Spec Impact: updated
- Scope: Shared next-action selector, natural-language entry, home/progress/continue/delivery and installed agent rules.
- Acceptance Boundary: .gstack/task-boundaries/2026-10-11_next-action-reminders.md

## Verification
- 132 unit/integration tests passed; 36 Loop contract checks and 74 natural-language checks passed.
- Actual freshly installed CLI lifecycle covered no task, unfinished work, missing acceptance, successful product assertions, source changes reopening acceptance, explicit pause and manual control.
- Every generated reminder input routed through the real intent router; failure replaces stale continuation guidance.
- Default adapter validation, source coverage and strict specification synchronization passed.
- Independent review findings fixed: manual-mode priority/body consistency and copied text entering the wrong route.

## Limits
- Reminders appear during agent replies and status queries; there is no background push or scheduled message sender.
- Agent rules guide behavior; repo-native rules are not a permission boundary. Suggestions do not authorize new tasks or risky actions.
- Initial goal templates contain visible placeholders for users to fill; meaningful acceptance still depends on project assertions.
- Existing target files remain preserved by installation defaults; updated agent instructions for customized targets require an explicit reviewed merge.

- Execution Receipt: output/qa/4079a2a17e6445f99cc81bbc392245ad/receipt.json
- Result: pass — 132 tests, 36 Loop checks, 74 natural-language checks and spec synchronization passed in task-bound verification.
