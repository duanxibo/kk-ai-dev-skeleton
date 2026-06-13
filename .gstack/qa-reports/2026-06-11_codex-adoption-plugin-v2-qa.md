# codex-adoption-plugin-v2 QA

- 日期：2026-06-11
- 类型：plugin source + docs QA
- 结论：pass
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_codex-adoption-plugin-v2.md`
- 关联产物：
  - `plugins/kk-dev-skeleton-adoption/.codex-plugin/plugin.json`
  - `plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption/SKILL.md`
  - `plugins/kk-dev-skeleton-adoption/README.md`
  - `plugins/kk-dev-skeleton-adoption/scripts/README.md`
  - `plugins/README.md`
  - `CODEX_ADOPTION_CONNECTOR.md`
  - `COMPANY_ADOPTION_GUIDE.md`
  - `README.md`
  - `.gstack/knowledge/code-patterns.md`

## 验收范围

本次验证 V2 repo-local Codex 接入器 plugin 源目录是否存在、manifest 和 skill 是否有效，并确认没有自动写 marketplace 或把业务用户入口改成命令行优先。

本次不涉及 HTML、页面、dashboard、截图或交互 UI，因此 Browser QA 不需要。

## 验证结果

### Plugin validation

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
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_codex-adoption-plugin-v2.md
```

结果：

- PASS：static Required Gates audit passed。

### 文案和范围检查

命令：

```bash
rg --hidden -n "\[TODO:|TODO" plugins/kk-dev-skeleton-adoption -S
```

结果：

- 无命中。
- `rg` 返回码为 1，符合“无 TODO 占位符”的预期。

命令：

```bash
rg --hidden -n "用户.*执行.*python3|业务用户.*运行.*python3|在目标项目根目录内执行|复制到新项目后的最小步骤" CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md plugins/kk-dev-skeleton-adoption -S
```

结果：

- 无命中。
- `rg` 返回码为 1，符合“没有旧命令行优先文案”的预期。

命令：

```bash
rg --hidden -n "lunhui|cohort|审批模块|review-service|源项目|source-project" plugins/kk-dev-skeleton-adoption CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md -S
```

结果：

- 无命中。
- `rg` 返回码为 1，符合“未引入具体业务项目名或旧项目上下文”的预期。

命令：

```bash
find . -path './.agents/*' -o -path './plugins/kk-dev-skeleton-adoption/*' -maxdepth 5 -type f -print
```

结果：

- 只看到 `plugins/kk-dev-skeleton-adoption/` 下的 plugin 源文件。
- 未创建 `.agents/plugins/marketplace.json`。

## 用户可见验收

- 仓库内已有 repo-local plugin 源目录：`plugins/kk-dev-skeleton-adoption/`。
- plugin manifest 位于 `.codex-plugin/plugin.json`，并通过 validator。
- plugin skill 描述了自然语言接入、V1 helper 调度和安全边界。
- 文档说明当前 V2 是源目录 / 分发骨架，不是已安装 marketplace。
- 业务用户入口仍是自然语言。

## 残余风险

- 当前没有安装到 Codex，也没有创建 marketplace；这是本次 boundary 的明确 non-goal。
- 公司级 marketplace、安装策略、版本升级和权限策略仍需另起 V3 或发布任务。
- 当前目录不是 git worktree，因此 gstack guard 以 static audit 模式运行；复制到真实 git 项目后应再次运行。
