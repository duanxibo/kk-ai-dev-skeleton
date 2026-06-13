# productization-hardening QA

- 日期: 2026-06-13
- 负责人: Codex
- 关联 boundary: `.gstack/task-boundaries/2026-06-13_productization-hardening.md`

## 验收结论

通过。

## 本机状态修复证据

- 已运行 `bash .gstack/scripts/sync_repo_skills.sh --remove-tg-links`
  - 删除旧 `tg-*` symlink。
  - 同步 `kk-*` skills 到 `/Users/edy/.codex/skills`，目标指向当前公共骨架仓库。
- 已运行 `bash .gstack/scripts/install_git_hooks.sh`
  - `core.hooksPath=.githooks`
  - active hooks: `.githooks/pre-commit`, `.githooks/pre-push`

## 验证命令

```bash
bash -n scripts/setup_local_codex.sh
python3 -m py_compile .gstack/scripts/gstack_doctor.py
python3 -m unittest discover -s tests -p 'test_*.py'
bash scripts/setup_local_codex.sh --remove-tg-links
python3 .gstack/scripts/gstack_doctor.py check
python3 .gstack/scripts/spec_sync_guard.py
python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-13_productization-hardening.md
```

## Browser / Chrome / Playwright QA

- status: not-required
- blocked / partial reason: 本次只修改 Markdown 文档、shell helper、doctor 诊断逻辑和单元测试，没有 Web UI、HTML、local HTTP server、dashboard 或浏览器交互表面变化。

## 结果摘要

- `python3 -m unittest discover -s tests -p 'test_*.py'`
  - 36 tests passed.
- `bash scripts/setup_local_codex.sh --remove-tg-links`
  - repo-native skills synced.
  - git hooks installed.
  - doctor overall: `ok`.
- `python3 .gstack/scripts/gstack_doctor.py check`
  - overall: `ok`.
  - `git-hooks`: pass.
  - `skills`: pass.
  - `context-isolation`: pass.
  - 父目录 `tiangong` 仅作为命名提示保留，不再导致 warn。
- `python3 .gstack/scripts/spec_sync_guard.py`
  - PASS: no implementation changes detected, spec sync guard is not blocking this diff.
- `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`
  - PASS.
- `python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-13_productization-hardening.md`
  - PASS.

## 风险与剩余项

- 本次没有发布、commit 或 push。
- `QUICK_START_FOR_PARTNERS.md` 是普通用户入口；完整规则仍以 `AGENTS.md`、adapter 和 repo-native evidence 为准。
- `scripts/setup_local_codex.sh --remove-tg-links` 只应在确认本机不再需要旧 `tg-*` symlink 时使用；默认不删除旧 symlink。
