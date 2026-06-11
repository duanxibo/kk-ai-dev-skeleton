# Engineer 入口

当任务涉及代码、bugfix、refactor、测试、脚本、CI 或工程交付时，先读本入口。

## 必读顺序

1. `AGENTS.md`
2. `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
3. `.gstack/README.md`
4. `.gstack/knowledge/CODEMAP.md`
5. `.gstack/knowledge/doc-placement.md`
6. `.gstack/knowledge/implementation-guide.md`
7. `.gstack/knowledge/qa-dimensions.md`
8. 当前 active task boundary
9. active project adapter
10. 与改动路径相关的项目真源、tests、fixtures 和 pitfalls

## 工程规则

- 先确认 allowed files 和 forbidden files。
- 实现只在 boundary 允许范围内进行。
- adapter 定义的测试、构建和启动命令优先于通用猜测。
- UI / HTML / 可视化任务必须实际打开或操作；无法操作时 QA 只能标 `blocked` 或 `partial`。
- 后端、数据、API、权限或持久化变化必须同步项目真源文档，或写清 no-spec-change 原因。
- 新发现的可复用坑写回 `.gstack/knowledge/`、`.gstack/rules/` 或 `.gstack/learnings/`。

## 交付前检查

- requirement / review / boundary / QA evidence 是否齐全。
- Required Gates 是否有明确状态和 evidence。
- 用户可见验收是否真实覆盖。
- adapter 命令是否运行，失败时是否记录原因。
- `python3 .gstack/scripts/spec_sync_guard.py` 是否通过或有明确阻塞说明。

## 不自动执行

- git workflow action
- 生产操作
- DB schema 变更
- 真实数据写入
- 大范围删除或回滚
- 超出 adapter 的外部系统访问
