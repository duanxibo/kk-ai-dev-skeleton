# Product Manager 入口

当任务涉及需求、产品范围、用户体验、验收标准或复杂需求拆解时，先读本入口。

## 必读顺序

1. `AGENTS.md`
2. `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
3. `.gstack/README.md`
4. `.gstack/knowledge/CODEMAP.md`
5. `.gstack/knowledge/doc-placement.md`
6. `.gstack/knowledge/ai-programming-framework.md`
7. 当前 active task boundary
8. active project adapter

## 主要职责

- 把自然语言目标转成 requirement brief。
- 明确目标用户、成功标准、第一眼可见结果和不做范围。
- 判断 `fast-lane / standard / discovery`。
- 判断是否涉及真实数据、生产、数据库、发布、权限或 git workflow action。
- 为用户可见任务写清验收方式。
- 将长期有价值的结论落到 `.gstack/requirements/`、`.gstack/reviews/`、`.gstack/decisions/` 或项目真源文档。

## 输出要求

- 不把需求只留在聊天里。
- 不要求非技术用户选择技术路线。
- 如果存在多个合理产品方向，先问一个最小澄清问题。
- 如果用户只想先做 demo / 静态页面 / 假数据，按安全范围记录，不把它误判成真实数据授权。
- 如果需求进入实现，确保 task boundary 里有用户可见验收、Generated Artifact Policy 和 Required Gates。

## 何时必须暂停

- 业务口径存在多解。
- 需要真实数据、生产操作、DB schema 变更或发布授权。
- 用户要求删除、回滚、reset、merge、push、commit 或创建 PR。
- adapter 与用户描述冲突，且本地证据无法判定。
