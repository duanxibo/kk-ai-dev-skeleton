# codex-adoption-marketplace-v3 QA

- 日期：2026-06-11
- 类型：marketplace source + docs QA
- 结论：pass
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_codex-adoption-marketplace-v3.md`
- 关联产物：
  - `.agents/plugins/marketplace.json`
  - `.agents/plugins/README.md`
  - `plugins/MARKETPLACE_INSTALL.md`
  - `tests/test_plugin_marketplace.py`
  - `CODEX_ADOPTION_CONNECTOR.md`
  - `COMPANY_ADOPTION_GUIDE.md`
  - `README.md`
  - `.gstack/knowledge/code-patterns.md`

## 验收范围

本次验证公司内部 repo-local marketplace source 是否存在、指向 V2 plugin 源目录，并且安装 / 升级说明没有把普通业务用户入口改成命令行安装。

本次没有在当前 Codex 环境执行 `codex plugin marketplace add` 或 `codex plugin add`。

## 验证结果

### Marketplace structure

命令：

```bash
python3 -m unittest tests/test_plugin_marketplace.py
```

结果：

- PASS。
- 4 tests passed。

覆盖点：

- marketplace name 为 `kk-dev-skeleton-internal`。
- marketplace entry 指向 `./plugins/kk-dev-skeleton-adoption`。
- plugin manifest 和 skill 文件存在。
- policy 包含 `installation: AVAILABLE` 和 `authentication: ON_INSTALL`。
- 未设置 `policy.products` override。

命令：

```bash
python3 -m json.tool .agents/plugins/marketplace.json
```

结果：

- PASS：JSON 可解析。

命令：

```bash
python3 <codex-home>/skills/.system/plugin-creator/scripts/read_marketplace_name.py --marketplace-path .agents/plugins/marketplace.json
```

结果：

- PASS。
- 输出：`kk-dev-skeleton-internal`。

### Plugin and skill validation

命令：

```bash
python3 <codex-home>/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/kk-dev-skeleton-adoption
```

结果：

- PASS：Plugin validation passed。

命令：

```bash
python3 <codex-home>/skills/.system/skill-creator/scripts/quick_validate.py plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption
```

结果：

- PASS：Skill is valid。

### V1 helper smoke

命令：

```bash
python3 scripts/init_project.py --adapter default --verify --report
```

结果：

- PASS。
- V1 helper report 中 doctor、spec-sync、team-flow、required-gates、natural-language-smoke 全部通过。
- 输出仍说明用户入口是“对 Codex 说自然语言接入请求”，执行方式是 Codex 调用内部 helper。

### Guard

命令：

```bash
python3 .gstack/scripts/spec_sync_guard.py
```

结果：

- PASS：static skeleton guard passed。
- 备注：当前目录不是 git worktree，脚本按 static skeleton guard 运行，这是当前骨架目录的预期环境状态。

命令：

```bash
python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD
```

结果：

- PASS：static required gstack command chain is satisfied。

命令：

```bash
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_codex-adoption-marketplace-v3.md
```

结果：

- PASS：static Required Gates audit passed。

### 文案和范围检查

命令：

```bash
rg --hidden -n "用户.*执行.*python3|业务用户.*运行.*python3|在目标项目根目录内执行|复制到新项目后的最小步骤" CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md plugins .agents -S
```

结果：

- 无命中。
- `rg` 返回码为 1，符合“没有旧命令行优先文案”的预期。

命令：

```bash
rg --hidden -n "lunhui|cohort|审批模块|review-service|源项目|source-project" CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md plugins .agents tests/test_plugin_marketplace.py -S
```

结果：

- 无命中。
- `rg` 返回码为 1，符合“未引入具体业务项目名或旧项目上下文”的预期。

命令：

```bash
rg --hidden -n "\[TODO:|TODO" .agents plugins tests/test_plugin_marketplace.py -S
```

结果：

- 无命中。
- `rg` 返回码为 1，符合“无 TODO 占位符”的预期。

## 用户可见验收

- repo-local marketplace source 已存在：`.agents/plugins/marketplace.json`。
- marketplace entry 指向 `./plugins/kk-dev-skeleton-adoption`。
- 安装 / 升级说明已落到 `plugins/MARKETPLACE_INSTALL.md`。
- README、公司接入指南和产品化方案已说明 V3 分发路径。
- 普通业务用户入口仍是自然语言；安装 marketplace 是 admin / release action。

## 残余风险

- 当前没有安装到 Codex；这是本次 boundary 的明确 non-goal。
- 公司级远程 marketplace、权限策略、版本登记、adapter drift 检测仍需后续任务。
- 当前目录不是 git worktree，因此 gstack guard 以 static audit 模式运行；复制到真实 git 项目后应再次运行。
