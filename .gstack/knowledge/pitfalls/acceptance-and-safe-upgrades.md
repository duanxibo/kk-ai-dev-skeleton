# Acceptance and upgrades need full lifecycle verification

Do not equate a zero exit code with product acceptance. Bind task criteria to designated assertion commands and invalidate receipts when task semantics change. Preserve execution-only diagnostics for existing tooling while explaining the acceptance migration requirement explicitly.

Exercise installed helpers against a broken product, its fix, and a fresh checkout without local receipts. A source-only smoke can miss target adapter generation and missing runtime imports. The core-only installer must remain standalone until runtime installation.

Partial pristine upgrades can break customized bundles. Preflight conflicts before any bundle write, verify an isolated staged copy and restore the previous bundle and manifest on failed writes. Report the remaining process-crash and uncontrolled-concurrency limits accurately.

Keep validation responsibilities in small shared modules; avoid copying policy implementations into a large orchestrator or claiming that mappings prove semantic test completeness.
