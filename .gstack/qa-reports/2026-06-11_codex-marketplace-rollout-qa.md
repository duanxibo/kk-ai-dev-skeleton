# codex-marketplace-rollout QA

- 日期：2026-06-11
- 任务：codex-marketplace-rollout
- Boundary：`.gstack/task-boundaries/2026-06-11_codex-marketplace-rollout.md`
- QA 类型：doc / marketplace rollout static QA
- 结论：通过

## 验收范围

- 新增 marketplace / plugin 推广计划。
- 新增管理员安装清单。
- 新增试点反馈表。
- 更新 README、公司接入指南、Codex 接入器方案和 marketplace install 入口。
- 确认普通伙伴入口仍是 Codex 自然语言，不是手动执行命令。
- 确认没有修改 marketplace manifest、plugin manifest 或 plugin skill。

## 命令验证

### 文档测试

```bash
python3 -m unittest tests/test_marketplace_rollout_docs.py
```

结果：通过，5 tests OK。

### Marketplace 结构测试

```bash
python3 -m unittest tests/test_plugin_marketplace.py
```

结果：通过，4 tests OK。

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

### Marketplace name reader

```bash
python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py --marketplace-path .agents/plugins/marketplace.json
```

结果：`kk-dev-skeleton-internal`。

### Spec sync guard

```bash
python3 .gstack/scripts/spec_sync_guard.py
```

结果：通过。当前目录不是 git worktree，脚本执行 static skeleton guard。

### Team flow guard

```bash
python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD
```

结果：通过。当前目录不是 git worktree，脚本执行 static boundary audit。

### Required gates audit

```bash
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_codex-marketplace-rollout.md
```

结果：通过。当前目录不是 git worktree，脚本执行 static boundary audit。

## 文案检索

### 命令行优先文案

```bash
rg --hidden -n "用户.*执行.*python3|业务用户.*运行.*python3|在目标项目根目录内执行|复制到新项目后的最小步骤" plugins .agents COMPANY_ADOPTION_GUIDE.md README.md CODEX_ADOPTION_CONNECTOR.md -S
```

结果：无匹配。

### 旧项目上下文

```bash
rg --hidden -n "lunhui|cohort|审批模块|review-service|TianGong|tiangong" plugins .agents tests/test_marketplace_rollout_docs.py COMPANY_ADOPTION_GUIDE.md README.md CODEX_ADOPTION_CONNECTOR.md -S
```

结果：无匹配。

## 人工复核要点

- `plugins/MARKETPLACE_ROLLOUT.md` 明确普通伙伴使用 Codex 自然语言入口。
- `plugins/ADMIN_INSTALL_CHECKLIST.md` 明确安装命令只属于管理员 / 发布负责人，并需要明确授权。
- `plugins/PILOT_FEEDBACK.md` 覆盖命令行优先误导、真实数据、生产、数据库和 git workflow action 风险。
- `plugins/MARKETPLACE_INSTALL.md` 继续保留安装 / 升级命令，但新增了推广材料入口和非业务用户路径说明。
- 本次未执行 `codex plugin marketplace add`、`codex plugin add`、commit、push、merge 或其他 git workflow action。

## 残余风险

- 当前 QA 未真实安装 plugin；这是本任务 boundary 的非目标。首次安装应由管理员按 `plugins/ADMIN_INSTALL_CHECKLIST.md` 在明确授权后执行。
- 当前目录不是 git worktree，因此 git diff / commit 层验证不可用；已使用 static guard 和文档测试覆盖本次推广包。
