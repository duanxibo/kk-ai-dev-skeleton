# Acceptance and safe adoption requirement
- AI 语义复核: yes
- Spec Impact: updated
- Scope: Bind task acceptance to executed verification; generated adapters expose explicit QA setup; target project integration CI; runtime upgrades preserve entire old bundle on conflicts or failed compatibility checks.
- Acceptance: Message-only commands cannot satisfy mapped product tests; edited acceptance invalidates old verification; actual failing product test blocks installed target QA.
- Acceptance: Customized conflicts and failed upgrade verification leave prior scripts and manifest intact; existing pipelines are preserved.
- Non-goals: Guarantee semantic test completeness, production/deployment/merge, or wholesale rewrites of Loop and the natural-language router.
