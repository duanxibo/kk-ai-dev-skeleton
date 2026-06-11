# Scripts

This plugin intentionally keeps executable adoption behavior in the target repository.

Codex should call the target repository's V1 helper:

```bash
python3 scripts/init_project.py --adapter <adapter> --detect
python3 scripts/init_project.py --adapter <adapter> --plan
python3 scripts/init_project.py --adapter <adapter> --apply
python3 scripts/init_project.py --adapter <adapter> --verify --report
```

Keeping the executable layer in the repository preserves adapter rules, task boundaries, guard checks, and repo-native QA evidence.
