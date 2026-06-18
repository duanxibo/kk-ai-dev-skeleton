# Scripts

This plugin keeps project adoption behavior in the target repository, but owns a small productized update reminder.

## Plugin update reminder

Codex should run the non-blocking checker at the start of plugin workflows:

```bash
python3 scripts/check_update.py --format text
```

The checker compares the installed plugin manifest with the GitHub `main` manifest. If the local plugin is stale, it prints both the natural-language update prompt and equivalent CLI commands:

```bash
codex plugin marketplace upgrade kk-dev-skeleton-internal
codex plugin add kk-dev-skeleton-adoption@kk-dev-skeleton-internal
```

Network or remote errors do not block the current user task.

## Target repository adoption helper

Executable adoption behavior stays in the target repository.

Codex should call the target repository's V9 helper:

```bash
python3 scripts/init_project.py --adapter <adapter> --detect
python3 scripts/init_project.py --adapter <adapter> --plan
python3 scripts/init_project.py --adapter <adapter> --apply
python3 scripts/init_project.py --adapter <adapter> --apply-core --dry-run --report
python3 scripts/init_project.py --adapter <adapter> --apply-runtime --dry-run --report
python3 scripts/init_project.py --adapter <adapter> --rewrite-adapter --dry-run --report
python3 scripts/init_project.py --adapter <adapter> --validate-adapter --report
python3 scripts/init_project.py --adapter <adapter> --verify --verify-core --verify-runtime --report
```

Keeping the executable layer in the repository preserves adapter rules, task boundaries, guard checks, and repo-native QA evidence.
