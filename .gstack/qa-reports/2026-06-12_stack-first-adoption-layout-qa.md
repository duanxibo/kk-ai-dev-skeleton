# stack-first-adoption-layout QA

- 日期：2026-06-12
- 任务：stack-first-adoption-layout
- Boundary：`.gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md`
- QA 类型：helper / adapter / plugin static QA
- 结论：通过

## 背景

用户反馈：项目接入骨架后没有生成 `stack/`，应用代码和配置散落在仓库一级目录，不符合预期。

本轮修正目标：

- 初始化 helper 默认创建 `stack/<project>/`。
- 默认 adapter/runtime 改成 stack-first。
- 已有根目录代码只报告为迁移候选，不自动移动。
- plugin skill 明确接入时必须检查 stack layout。

## 行为验证

### Python 编译

```bash
python3 -m py_compile scripts/init_project.py tests/test_init_project.py
```

结果：通过。

### Init helper 单测

```bash
python3 -m unittest tests/test_init_project.py
```

结果：通过，9 tests OK。

覆盖点：

- `apply_adapter` 创建 `adapters/<adapter>/`。
- `apply_adapter` 同时创建 `stack/<adapter>/README.md`。
- `stack/<adapter>/specs/README.md` 被创建。
- `stack/<adapter>/src/.gitkeep`、`tests/.gitkeep`、`fixtures/.gitkeep`、`scripts/.gitkeep` 被创建。
- 已存在 adapter 时不覆盖 adapter，但仍确保 `stack/<adapter>/` 存在。
- `runtime.json` 中 `stack/default/` 模板路径会替换为 `stack/<adapter>/`。
- 检测根目录 `src`、`prisma`、`package.json` 作为迁移候选。
- 接入计划会提示迁移计划，不静默接受散落一级目录。

### 完整测试集

```bash
python3 -m unittest tests/test_git_marketplace_publish_docs.py tests/test_marketplace_rollout_docs.py tests/test_plugin_marketplace.py tests/test_init_project.py
```

结果：通过，22 tests OK。

### Detect CLI

```bash
python3 scripts/init_project.py --adapter default --detect --format json
```

结果：通过。输出包含：

- `stack_dir`
- `stack_dir_exists`
- `stack_specs_exists`
- `stack_src_exists`
- `root_code_paths`

`detect` 不写文件，因此本骨架仓库未生成 `stack/default/`；真实接入时由 `--apply` 创建。

## Plugin / Marketplace 验证

### Cachebuster

```bash
python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py plugins/kk-dev-skeleton-adoption
```

结果：通过。版本从 `0.1.0` 更新为 `0.1.0+codex.20260612040400`，避免后续 marketplace 更新被旧 cache 复用。

### Plugin validator

```bash
python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/kk-dev-skeleton-adoption
```

结果：通过。

### Skill validator

```bash
python3 /Users/edy/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption
```

结果：通过。

### Marketplace name

```bash
python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py --marketplace-path .agents/plugins/marketplace.json
```

结果：`kk-dev-skeleton-internal`。

## GStack 门禁

### Spec sync guard

```bash
python3 .gstack/scripts/spec_sync_guard.py
```

结果：通过。

### Team flow guard

```bash
python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD
```

结果：通过。

### Required gates audit

```bash
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md
```

结果：通过。

## 未触碰范围

- 未修改真实试点项目 `/Users/edy/work/codespace/ai/task-manager-cp/`。
- 未移动任何已有项目根目录代码。
- 未修改 marketplace manifest。
- 未执行生产、数据库、真实数据或部署操作。

## 发布授权

- 用户已明确授权“发布”。
- 本报告随 `stack-first-adoption-layout` 修正提交进入 GitHub `main`。
- 发布后的远端 commit hash 以最终发布回执为准。

## 残余风险

- 已接入过的项目不会自动重排目录。对 `task-manager-cp` 这类已有项目，需要另起迁移任务：先生成迁移计划，再把 `src/`、`prisma/`、`e2e/`、测试和配置逐步迁入 `stack/<project>/` 或在 adapter 中明确例外。
- 伙伴本机已经安装过旧版时，需要执行 `codex plugin marketplace upgrade kk-dev-skeleton-internal` 后重装插件，才能拿到本次 cachebuster 版本。
