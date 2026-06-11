# 自然语言接入方式修正 QA

- 日期：2026-06-11
- QA 类型：`qa-only`
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md`
- Spec Impact: `not-required`

## 结论

- 状态：`pass`
- 本次只修改公司内接入指南和 README 文档，不涉及脚本逻辑、adapter runtime、示例应用、真实数据、生产环境、数据库或 git workflow action。
- 接入方式已从“用户手动执行命令”改为“用户通过 Codex 自然语言提出接入目标，Codex 负责初始化、自检和证据沉淀”。

## 验证命令

```bash
python3 .gstack/scripts/spec_sync_guard.py
```

- 结果：`pass`
- 说明：当前不是 git worktree，脚本进入 static skeleton guard，并通过 active boundary 结构检查。

```bash
python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD
```

- 结果：`pass`
- 说明：当前不是 git worktree，脚本进入 static boundary audit，固定研发流记录可解析。

```bash
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md
```

- 结果：`pass`
- 说明：Required Gates block 可解析，专项 gate 均为明确的 `not-required` 或 `done`。

```bash
rg --hidden -n "在目标项目根目录内执行|复制到新项目后的最小步骤|用户.*执行.*python3|业务用户.*运行.*python3" COMPANY_ADOPTION_GUIDE.md README.md -S
```

- 结果：`pass`
- 说明：无命中，旧的用户手动执行命令表述已移除。

```bash
rg --hidden -n "通过 Codex|自然语言|对 Codex 说|用户对 Codex" COMPANY_ADOPTION_GUIDE.md README.md -S
```

- 结果：`pass`
- 说明：命中 README 和接入指南中的自然语言接入说明。

```bash
rg --hidden -n "lunhui|cohort|审批模块|review-service|TianGong|tiangong" COMPANY_ADOPTION_GUIDE.md README.md -S
```

- 结果：`pass`
- 说明：无命中，对外文档未引入旧项目或私有业务关键词。

## 文档检查

- `README.md` 已将新项目接入方式改为用户对 Codex 说出项目目标、路径、限制和安全边界。
- `COMPANY_ADOPTION_GUIDE.md` 已明确“用户不需要手动执行初始化命令；命令和脚本是 Codex 背后的执行工具和排障工具”。
- 接入成功标准已改为“Codex 报告检查通过”，而不是要求业务用户自行运行命令。
- 常见失败处理已改为“对 Codex 说”，保留 Codex 背后的排障责任。

## 残余风险

- 当前目录不是 git worktree，因此 git diff 相关检查以 static audit 方式验证；真实项目接入后仍应在 git worktree 中重跑。
- 本轮没有真实项目试点；下一步仍应选择一个低风险项目，用自然语言让 Codex 完成一次完整接入。

