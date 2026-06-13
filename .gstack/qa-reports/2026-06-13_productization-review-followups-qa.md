# productization-review-followups QA

- 日期: 2026-06-13
- 负责人: Codex
- 关联 boundary: `.gstack/task-boundaries/2026-06-13_productization-review-followups.md`

## 验收结论

通过。

## 修复覆盖

- 安装文档不再包含 `<local-home>/...` 或 `.codex/skills/.system` 这类本机绝对路径。
- `scripts/setup_local_codex.sh` 在非 git worktree 中自动跳过 hooks 安装并继续 doctor。
- doctor core docs 检查从 18 个入口扩展为 29 个入口，覆盖普通伙伴快速入口、安装文档、setup helper 和公共 workspace layers。
- context-isolation 的下一步说明已区分外部 skill symlink 和普通目录。

## 验证命令

```bash
python3 -m unittest tests/test_productization_hardening.py -v
rg -n "<local-home>|\\.codex/skills/\\.system" README.md COMPANY_ADOPTION_GUIDE.md CODEX_ADOPTION_CONNECTOR.md QUICK_START_FOR_PARTNERS.md plugins .gstack/knowledge .gstack/scripts scripts --glob '!tests/**'
bash -n scripts/setup_local_codex.sh
python3 -m py_compile .gstack/scripts/gstack_doctor.py
python3 -m unittest discover -s tests -v
python3 .gstack/scripts/gstack_doctor.py check
python3 .gstack/scripts/natural_language_dev_smoke.py
python3 .gstack/scripts/spec_sync_guard.py
python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-13_productization-review-followups.md
python3 .gstack/scripts/runtime_artifact_guard.py
```

## 发放包模拟

```bash
tmpdir=$(mktemp -d)
rsync -a --exclude .git --exclude .idea ./ "$tmpdir"/
bash "$tmpdir/scripts/setup_local_codex.sh" --skip-skills
rm -rf "$tmpdir"
```

结果：

- setup 输出 `[SKIP] git hooks installation (not a git worktree)`。
- doctor 继续运行，没有被 hooks 安装中断。
- 因模拟包没有 `.git` 且跳过 skills，同步和 hooks 项为提醒；命令整体退出码为 0。

## 结果摘要

- `python3 -m unittest discover -s tests -v`
  - 40 tests passed.
- `python3 .gstack/scripts/gstack_doctor.py check`
  - overall: `ok`
  - `core-docs`: checked 29 entries.
- `python3 .gstack/scripts/natural_language_dev_smoke.py`
  - overall: `ok`
- `python3 .gstack/scripts/spec_sync_guard.py`
  - PASS.
- `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`
  - PASS.
- `python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-13_productization-review-followups.md`
  - PASS.
- `python3 .gstack/scripts/runtime_artifact_guard.py`
  - PASS.

## Browser / Chrome / Playwright QA

- status: not-required
- blocked / partial reason: 本次只修改 Markdown 文档、shell helper、doctor 诊断逻辑和单元测试，没有 Web UI、HTML、local HTTP server、dashboard 或浏览器交互表面变化。

## 风险与剩余项

- 本次没有发布、commit 或 push。
- `scripts/setup_local_codex.sh` 在非 git worktree 中只跳过 hooks；初始化为 git 仓库后仍应重新运行 setup 或 `install_git_hooks.sh`。
- 普通目录形式的外部 skills 不会被 doctor 自动删除，仍需用户确认后人工处理。
