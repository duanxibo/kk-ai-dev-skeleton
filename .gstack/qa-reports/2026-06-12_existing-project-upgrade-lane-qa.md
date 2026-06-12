# existing-project-upgrade-lane QA

- 日期：2026-06-12
- 任务：existing-project-upgrade-lane
- Boundary：`.gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md`
- QA 类型：helper / plugin workflow / docs / unit tests
- 结论：通过

## 背景

用户希望插件更新后，伙伴可以在已有项目里方便地应用新版骨架能力，而不是重新创建项目或重新走首次接入。

本轮交付：

- `scripts/init_project.py` 新增 `--upgrade-plan`。
- `scripts/init_project.py` 新增 `--upgrade-apply`。
- `--upgrade-apply` 只做安全幂等改造：确保 `stack/<adapter>/` layout；不覆盖 adapter，不移动根目录业务代码。
- 插件 skill 新增 Existing Project Upgrade lane。
- 伙伴安装和推广文档新增“更新后改造已有项目”自然语言入口。

## 行为验证

### Browser / UI QA

结果：不需要。

原因：本次没有修改 Web UI、HTML、dashboard、可视化产物或浏览器交互；用户可见面是 Codex 插件 workflow 文本和 `init_project.py` CLI 输出。

### Python 编译

```bash
python3 -m py_compile scripts/init_project.py tests/test_init_project.py
```

结果：通过。

### Init helper 单测

```bash
python3 -m unittest tests/test_init_project.py
```

结果：通过，13 tests OK。

新增覆盖点：

- 已有项目升级计划说明“不新建项目、不重新接入”。
- 缺失 `stack/<adapter>/` 时，升级计划标记 `stack-layout` 为 safe apply。
- runtime 未引用 stack 路由时，只生成 planned 项，不自动改 adapter。
- `--upgrade-apply` 保留已有 adapter 内容并创建 `stack/<adapter>/`。
- adapter 缺失时，`--upgrade-apply` 阻塞并提示先走首次接入。

### Upgrade plan smoke

```bash
python3 scripts/init_project.py --adapter default --upgrade-plan
python3 scripts/init_project.py --adapter default --upgrade-plan --format json
```

结果：通过。输出包含：

- `已有项目增量升级计划`
- `原则：不新建项目、不重新接入、不默认覆盖 adapter、不自动移动业务代码`
- `stack-layout`
- `plugin-update-reminder`

未执行 `--upgrade-apply` 于本骨架仓库，避免为模板仓库生成不需要提交的 `stack/default/`。

### 完整测试集

```bash
python3 -m unittest tests/test_git_marketplace_publish_docs.py tests/test_marketplace_rollout_docs.py tests/test_plugin_marketplace.py tests/test_plugin_update_check.py tests/test_init_project.py
```

结果：通过，31 tests OK。

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

### Cachebuster

```bash
python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py plugins/kk-dev-skeleton-adoption
```

结果：通过。版本从 `0.1.0+codex.20260612073926` 更新为 `0.1.0+codex.20260612074242`。

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
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-12_existing-project-upgrade-lane.md
```

结果：通过。

## 未触碰范围

- 未修改真实试点项目 `/Users/edy/work/codespace/ai/task-manager-cp/`。
- 未修改 `.agents/plugins/marketplace.json`。
- 未修改当前机器 Codex plugin cache 或 personal marketplace。
- 未自动覆盖 adapter。
- 未自动移动业务代码。
- 未自动执行插件安装、插件升级、生产、数据库、真实数据或部署操作。

## 发布授权

- 用户已明确授权“发布”。
- 本报告随 `existing-project-upgrade-lane` 修正提交进入 GitHub `main`。
- 发布后的远端 commit hash 以最终发布回执为准。

## 残余风险

- `upgrade-apply` 当前只覆盖安全 layout 修复；framework core 文件同步、adapter 合并和业务代码迁移仍需要后续更细的计划能力。
- 已有项目如果 helper 版本太旧，更新后的插件会先引导生成升级计划；要获得最新 helper 行为，还需要在该项目中同步新版 `scripts/init_project.py` 或执行经过确认的 framework core 合并计划。
