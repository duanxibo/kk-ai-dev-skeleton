# 公司内接入指南 QA

- 日期：2026-06-11
- QA 类型：`qa-only`
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_company-adoption-guide.md`
- Spec Impact: `not-required`

## 结论

- 状态：`pass`
- 本次只新增公司内接入文档和 README 入口，不涉及页面、应用行为、真实数据、生产环境、数据库或 git workflow action。
- 指南覆盖发放包、发放前检查、新项目接入步骤、adapter 填写清单、接入成功标准、试点任务、安全边界、常见失败处理和升级策略。

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
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_company-adoption-guide.md
```

- 结果：`pass`
- 说明：Required Gates block 可解析，所有专项 gate 均为明确的 `not-required` 或 `done`。

```bash
rg --hidden -n "lunhui|cohort|审批模块|review-service" COMPANY_ADOPTION_GUIDE.md README.md -S
```

- 结果：`pass`
- 说明：无命中。

```bash
rg --hidden -n "源项目|source-project" COMPANY_ADOPTION_GUIDE.md README.md -S
```

- 结果：`pass`
- 说明：无命中。

```bash
python3 .gstack/scripts/gstack_dashboard.py explain --all --query company-adoption-guide --limit 1
```

- 结果：执行成功。
- 收口前状态：`5/7`，implement 和 QA 待标记。

## 文档检查

- `README.md` 已新增 `COMPANY_ADOPTION_GUIDE.md` 入口。
- `COMPANY_ADOPTION_GUIDE.md` 使用 repo-relative 路径，不包含本机绝对路径。
- 指南没有引入具体业务域、私有项目名或真实数据源。

## 残余风险

- 当前目录不是 git worktree，因此 git diff 相关检查以 static audit 方式验证；真实项目接入后仍应在 git worktree 中重跑。
- 本轮没有真实项目试点；下一步应选择一个低风险项目创建真实 adapter 并跑一个小任务。

## 用户验收

- 打开 `README.md` 可以找到 `COMPANY_ADOPTION_GUIDE.md`。
- 新团队可以按 `COMPANY_ADOPTION_GUIDE.md` 完成骨架复制、adapter 创建、doctor 自检和首个试点任务选择。

