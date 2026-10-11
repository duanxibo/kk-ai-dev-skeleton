# Evidence content, execution and coverage

Matching paths and handwritten pass statements are insufficient. Every evidence consumer must use the same contract, including compact gates, implementation completion and justified no-spec readiness. Test a complete lifecycle, not only artifact creation.

QA execution receipts bind exact adapter argv, exit status, log checksums and source snapshots. They fail after source/config changes and are local artifacts regenerated in each checkout. Repository writers can forge local records; independent CI and meaningful assertions provide stronger validation.

Do not infer no implementation changes from an example adapter. Audit discovered source against real adapter paths, and use the framework source adapter only inside the framework repository. Unknown languages/generated files remain a manual coverage responsibility.

Upgrade custom runtime conservatively: compare installed checksums before replacing files, report unresolved differences explicitly, and retain human customization.
