# stack-first-adoption-layout Fast-lane Requirement

- 需求名称：stack-first-adoption-layout
- 提出人：用户
- 日期：2026-06-12
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-12_stack-first-adoption-layout.md`
- 生成方式：
  `deterministic-scaffold`
- AI 语义复核：
  `yes`

## 需求一句话

- 用户要完成什么：修正 KK Dev Skeleton 初始化策略：默认创建 stack/<project>/ 目录，adapter/runtime 采用 stack-first 路由，并对已有根目录代码输出迁移计划，避免初始化后代码散落在一级目录

## 为什么可以走 fast-lane

- 范围小：
  `是`
- 需求明确：
  `是`
- 不涉及业务口径多解：
  `是`
- 不涉及 DB schema、生产操作或 git workflow action：
  `是`
- 可本地验证：
  `是`

## 本次必须做

- 待补

## 本次明确不做

- 待补

## 影响面

- 代码 / 文档路径：
  - 待补
- 数据 / 接口 / 权限：
  `不涉及`
- spec impact：
  `not-required`

## 冻结结论

- 本文件已由 Codex 基于当前上下文复核，可同时作为 fast-lane 的 requirement brief 和 requirement freeze。
- 如果后续发现需求有多解、影响面扩大或需要业务口径确认，必须退出 fast-lane，回到 standard / discovery 流程。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Flow Lane`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `.gstack/reviews/2026-06-12_stack-first-adoption-layout-fast-lane-review.md`。
