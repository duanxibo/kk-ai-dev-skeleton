# Adapter Runtime 与模板初始化入口 Fast-lane Requirement

- 需求名称：Adapter Runtime 与模板初始化入口
- 提出人：用户
- 日期：2026-06-11
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_adapter-runtime-and-template-installer.md`
- 生成方式：
  `deterministic-scaffold`
- AI 语义复核：
  `yes`

## 需求一句话

- 用户要完成什么：将骨架路径规则从核心脚本抽离到 adapter runtime，并补充公司内复用时可执行的初始化/自检入口。

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

- 新增 adapter runtime 机器可读配置，承载实现路径、spec 路径、数据门禁路径和本地启动入口。
- 让 spec_sync_guard、required_gates_audit、team_flow_guard、gstack_doctor 读取 adapter runtime，减少核心脚本硬编码项目路径。
- 补一个面向团队复制骨架后的初始化/自检入口，并在 README 和 default adapter 中说明使用方式。

## 本次明确不做

- 不引入具体业务域、私有项目名或真实数据源。
- 不执行 git workflow action，不创建分支、commit、push 或 PR。
- 不改示例应用的业务行为。

## 影响面

- 代码 / 文档路径：
  - .gstack/scripts/
  - .gstack/workflows/team-development-flow.toml
  - .gstack/requirements/
  - .gstack/reviews/
  - .gstack/task-boundaries/
  - .gstack/qa-reports/
  - adapters/default/
  - scripts/
  - README.md
  - AGENTS.md
- 数据 / 接口 / 权限：
  `不涉及`
- spec impact：
  `not-required`

## 冻结结论

- 本文件已由 Codex 基于当前上下文复核，可同时作为 fast-lane 的 requirement brief 和 requirement freeze。
- 如果后续发现需求有多解、影响面扩大或需要业务口径确认，必须退出 fast-lane，回到 standard / discovery 流程。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Flow Lane`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `.gstack/reviews/2026-06-11_adapter-runtime-and-template-installer-fast-lane-review.md`。
