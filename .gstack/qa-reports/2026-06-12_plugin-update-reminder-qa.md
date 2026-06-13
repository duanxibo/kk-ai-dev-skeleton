# plugin-update-reminder QA

- 日期：2026-06-12
- 任务：plugin-update-reminder
- Boundary：`.gstack/task-boundaries/2026-06-12_plugin-update-reminder.md`
- QA 类型：plugin helper / skill workflow / docs / unit tests
- 结论：通过

## 背景

用户要求把“伙伴如何感知插件更新”做成产品化自动提醒。

本轮交付：

- 新增 `plugins/kk-dev-skeleton-adoption/scripts/check_update.py`。
- 插件 skill 在 adoption / install / check / upgrade / report workflow 前执行非阻断式更新检查。
- 文档说明伙伴使用插件时会自动获得更新提醒。
- 测试覆盖 `current`、`outdated`、`ahead` 和 `unknown` 状态。

## 行为验证

### Browser / UI QA

结果：不需要。

原因：本次没有修改 Web UI、HTML、dashboard、可视化产物或浏览器交互；用户可见面是 Codex 插件工作流文本和 `check_update.py` 的 CLI 输出，已通过单测和真实远端 smoke 验证。

### Python 编译

```bash
python3 -m py_compile plugins/kk-dev-skeleton-adoption/scripts/check_update.py tests/test_plugin_update_check.py
```

结果：通过。

### 更新检查单测

```bash
python3 -m unittest tests/test_plugin_update_check.py
```

结果：通过，5 tests OK。

覆盖点：

- 本地版本等于远端版本时返回 `current`。
- 本地版本低于远端版本时返回 `outdated`，并输出 `codex plugin marketplace upgrade kk-dev-skeleton-internal`。
- 本地版本高于 GitHub `main` 远端版本时返回 `ahead`，避免开发 / 发布前误报。
- 远端不可读时返回 `unknown`，默认 exit code 仍为 0，不阻断插件任务。
- `--strict` 模式下 `outdated` 返回非 0 exit code。

### 真实远端 smoke

```bash
python3 plugins/kk-dev-skeleton-adoption/scripts/check_update.py --format json
```

结果：通过。

本地待发布版本为 `0.1.0+codex.20260612045315`，GitHub `main` 当前版本为 `0.1.0+codex.20260612040400`，脚本返回 `ahead`。这符合发布前状态；发布后远端版本会变为本地版本。

### 完整测试集

```bash
python3 -m unittest tests/test_git_marketplace_publish_docs.py tests/test_marketplace_rollout_docs.py tests/test_plugin_marketplace.py tests/test_plugin_update_check.py tests/test_init_project.py
```

结果：通过，27 tests OK。

### Plugin validator

```bash
python3 <codex-home>/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/kk-dev-skeleton-adoption
```

结果：通过。

### Skill validator

```bash
python3 <codex-home>/skills/.system/skill-creator/scripts/quick_validate.py plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption
```

结果：通过。

### Cachebuster

```bash
python3 <codex-home>/skills/.system/plugin-creator/scripts/update_plugin_cachebuster.py plugins/kk-dev-skeleton-adoption
```

结果：通过。版本从 `0.1.0+codex.20260612040400` 更新为 `0.1.0+codex.20260612045315`。

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
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-12_plugin-update-reminder.md
```

结果：通过。

## 未触碰范围

- 未修改真实试点项目 `<pilot-project>/`。
- 未修改 `.agents/plugins/marketplace.json`。
- 未修改当前机器 Codex plugin cache 或 personal marketplace。
- 未自动执行插件安装、插件升级、生产、数据库、真实数据或部署操作。

## 发布授权

- 用户已明确授权“发布”。
- 本报告随 `plugin-update-reminder` 修正提交进入 GitHub `main`。
- 发布后的远端 commit hash 以最终发布回执为准。

## 残余风险

- 该能力是“使用插件时提醒”，不是后台推送；伙伴长期不打开 Codex 或不触发插件时，不会被动收到通知。
- 真实更新仍需要伙伴或管理员刷新 marketplace / 重装插件；脚本只负责提醒，不自动修改安装状态。
