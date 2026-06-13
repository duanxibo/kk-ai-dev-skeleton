# public-distribution-sanitization QA

- 日期: 2026-06-13
- 负责人: Codex
- 关联 boundary: `.gstack/task-boundaries/2026-06-13_public-distribution-sanitization.md`

## 验收结论

通过。

## 修复覆盖

- 默认 `bash scripts/setup_local_codex.sh` 不再因为 Bash 空数组展开失败。
- 无 `.git` 的骨架发放包会跳过 hooks 安装并继续运行 doctor。
- tracked tree 中的本机绝对路径、源项目名和试点项目名已替换成通用占位符。
- doctor core docs 检查扩展到 33 个入口，覆盖 `.agents` marketplace source、marketplace rollout、pilot feedback 和公共 workspace layers。
- 单元测试新增默认 setup 路径和全 tracked tree 敏感 token 扫描。

## 验证命令

```bash
bash -n scripts/setup_local_codex.sh
python3 -m py_compile .gstack/scripts/gstack_doctor.py
CODEX_HOME=$(mktemp -d) bash scripts/setup_local_codex.sh
python3 -m unittest discover -s tests -v
python3 .gstack/scripts/gstack_doctor.py check
python3 .gstack/scripts/natural_language_dev_smoke.py
python3 .gstack/scripts/spec_sync_guard.py
python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-13_public-distribution-sanitization.md
python3 .gstack/scripts/runtime_artifact_guard.py
```

## 发放包模拟

```bash
tmpdir=$(mktemp -d)
pkg=$(mktemp -d)
rsync -a --exclude .git --exclude .idea ./ "$pkg"/
CODEX_HOME="$tmpdir/codex" bash "$pkg/scripts/setup_local_codex.sh"
rm -rf "$tmpdir" "$pkg"
```

结果：

- setup 输出 hooks skipped for non-git worktree。
- doctor 继续运行，没有被 hooks 安装中断。
- 命令整体退出码为 0。

## 结果摘要

- `CODEX_HOME=$(mktemp -d) bash scripts/setup_local_codex.sh`
  - PASS.
- 发放包模拟
  - PASS.
- `python3 -m unittest discover -s tests -v`
  - 42 tests passed.
- `python3 .gstack/scripts/gstack_doctor.py check`
  - overall: `ok`
  - `core-docs`: checked 33 entries.
- 敏感 token 扫描
  - PASS: no tracked public distribution offenders.

## Browser / Chrome / Playwright QA

- status: not-required
- blocked / partial reason: 本次只修改 shell helper、doctor 诊断逻辑、历史 Markdown evidence 和单元测试，没有 Web UI、HTML、local HTTP server、dashboard 或浏览器交互表面变化。

## 风险与剩余项

- 本次没有发布、commit 或 push。
- 本地运行输出仍可能出现当前机器临时目录或本地 Codex home；这些不写入公开发放文件。
