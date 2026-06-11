# Adapter Runtime 与模板初始化入口 QA

- 日期：2026-06-11
- QA 类型：`qa-only`
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_adapter-runtime-and-template-installer.md`
- Spec Impact: `not-required`

## 结论

- 状态：`pass-with-environment-warnings`
- 本次改动不涉及页面、HTML、前端交互、真实数据、生产环境、数据库或 git workflow action。
- 新增 adapter runtime、初始化脚本和 guard 接入均已通过本地静态验证。

## 验证命令

```bash
python3 -m py_compile \
  .gstack/scripts/adapter_runtime.py \
  .gstack/scripts/gstack_doctor.py \
  .gstack/scripts/spec_sync_guard.py \
  .gstack/scripts/required_gates_audit.py \
  .gstack/scripts/team_flow_guard.py \
  .gstack/scripts/nontechnical_delivery_summary.py \
  scripts/init_project.py
```

- 结果：`pass`

```bash
python3 .gstack/scripts/gstack_doctor.py check
```

- 结果：`warn`
- 说明：`adapter-runtime` 和 `dev-stack-entry` 均为 `ok`；提醒项为当前目录不是 git worktree，以及本机父路径 / 全局 `tg-*` skill symlink 存在串味风险。

```bash
KK_ADAPTER=default python3 .gstack/scripts/gstack_doctor.py check --format json
```

- 结果：`warn`
- 说明：`adapter-runtime: ok`，`dev-stack-entry: ok`。

```bash
python3 .gstack/scripts/spec_sync_guard.py
```

- 结果：`pass`
- 说明：当前不是 git worktree，脚本进入 static skeleton guard，并通过 active boundary 结构检查。

```bash
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_adapter-runtime-and-template-installer.md
```

- 结果：`pass`
- 说明：当前不是 git worktree，脚本进入 static boundary audit，Required Gates block 可解析。

```bash
python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD
```

- 结果：`pass`
- 说明：当前不是 git worktree，脚本进入 static boundary audit，固定研发流记录可解析。

```bash
python3 .gstack/scripts/natural_language_dev_smoke.py
```

- 结果：`pass`
- 说明：完整非技术用户 smoke 为 `Overall: ok`；修复了 delivery summary 用户格式中暴露命令行词的问题。

```bash
python3 scripts/init_project.py --adapter default
```

- 结果：`pass`
- 说明：初始化入口能输出 default adapter 的后续修改步骤。

```bash
python3 scripts/init_project.py --adapter smoke-runtime --create-adapter --run-doctor
```

- 结果：`pass`
- 说明：临时 adapter 可复制，doctor 能读取 `adapters/smoke-runtime/runtime.json`；测试后已删除临时 adapter 文件。

## 残余风险

- 当前骨架目录不是 git worktree，因此 git-diff 路径的 pre-commit / pre-push 行为未在本目录验证；已补 static audit，真实项目初始化 git 后仍需在 git worktree 中再跑一次。
- doctor 的 `context-isolation` 提醒来自本机路径和全局 `tg-*` symlink，不属于骨架代码失败；真实发布时应在干净环境或按 README 清理旧 symlink 后复测。

## 用户验收

- 复制骨架后运行 `python3 scripts/init_project.py --adapter <project-slug> --create-adapter` 应生成项目 adapter。
- 设置 `KK_ADAPTER=<project-slug>` 后运行 doctor，应看到 `adapter-runtime` 检查项读取对应 `adapters/<project-slug>/runtime.json`。

