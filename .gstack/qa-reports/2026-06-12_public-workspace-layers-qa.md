# public-workspace-layers QA

- 日期：2026-06-12
- 任务：public-workspace-layers
- Boundary：`.gstack/task-boundaries/2026-06-12_public-workspace-layers.md`
- QA 类型：workspace layout / helper / docs / unit tests
- 结论：通过

## 背景

用户确认要补齐公共骨架缺失的 `archive/`、`blueprint/`、`shared/` 等能力落点。

本轮交付：

- 新增 `archive/` 和 `archive/baseline/` 空层说明。
- 新增 `blueprint/` 空层说明和 topic template。
- 新增 `shared/` 空层说明和 raw-inputs / fixtures / generated 占位目录。
- 新增 `.gstack/designs/README.md` 和 `.gstack/migrations/README.md`。
- 更新 README、CODEMAP、doc-placement 和默认 adapter。
- `scripts/init_project.py` 在 apply / create-adapter / upgrade-apply 时确保这些公共 workspace layers 存在。
- `detect` 输出 workspace layer 状态。

## 行为验证

### Browser / UI QA

结果：不需要。

原因：本次没有修改 Web UI、HTML、dashboard、可视化产物或浏览器交互；验收面是仓库目录、文档和 CLI helper 输出。

### Python 编译

```bash
python3 -m py_compile scripts/init_project.py tests/test_init_project.py
```

结果：通过。

### Init helper 单测

```bash
python3 -m unittest tests/test_init_project.py
```

结果：通过，14 tests OK。

新增覆盖点：

- `apply_adapter` 会创建 `archive/README.md`。
- `apply_adapter` 会创建 `archive/baseline/README.md`。
- `apply_adapter` 会创建 `blueprint/README.md` 和 `blueprint/00_阅读入口.md`。
- `apply_adapter` 会创建 `shared/README.md`、`shared/raw-inputs/.gitkeep`、`shared/generated/.gitkeep`。
- `apply_adapter` 会创建 `.gstack/designs/README.md` 和 `.gstack/migrations/README.md`。
- 已有 README 不会被覆盖。
- `detect` 会报告 workspace layer 状态。

### Detect smoke

```bash
python3 scripts/init_project.py --adapter default --detect --format json
```

结果：通过。输出 `workspace_layers`，且当前公共骨架中 `archive`、`archive_baseline`、`blueprint`、`shared`、`gstack_designs`、`gstack_migrations` 均为 `true`。

### 完整测试集

```bash
python3 -m unittest tests/test_git_marketplace_publish_docs.py tests/test_marketplace_rollout_docs.py tests/test_plugin_marketplace.py tests/test_plugin_update_check.py tests/test_init_project.py
```

结果：通过，32 tests OK。

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
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-12_public-workspace-layers.md
```

结果：通过。

## 未触碰范围

- 未复制 TianGong 私有 `archive/`、`blueprint/` 或 `shared/` 内容。
- 未修改真实试点项目 `/Users/edy/work/codespace/ai/task-manager-cp/`。
- 未修改 `.agents/plugins/marketplace.json`。
- 未修改当前机器 Codex plugin cache 或 personal marketplace。
- 未引入真实客户数据、Excel、CSV、SQL evidence、旧页面或旧业务脚本。

## 发布授权

- 用户已明确授权“发布”。
- 本报告随 `public-workspace-layers` 修正提交进入 GitHub `main`。
- 发布后的远端 commit hash 以最终发布回执为准。

## 残余风险

- 本轮只补公共空层和初始化能力；已有已接入项目需要通过 `--upgrade-plan` / `--upgrade-apply` 或后续 framework core 合并计划获得这些目录。
- `archive/` 的规则是只读追溯；如果团队把它当当前实现真源，需要在 adapter / boundary 中继续强化 guard。
