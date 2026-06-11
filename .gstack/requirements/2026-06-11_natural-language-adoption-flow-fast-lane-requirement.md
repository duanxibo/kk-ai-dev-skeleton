# 自然语言接入方式修正 Fast-lane Requirement

- 需求名称：自然语言接入方式修正
- 提出人：用户
- 日期：2026-06-11
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_natural-language-adoption-flow.md`
- 生成方式：
  `deterministic-scaffold`
- AI 语义复核：
  `yes`

## 需求一句话

- 用户要完成什么：将公司内接入指南从用户手动执行命令改为通过 Codex 自然语言完成接入。

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

- 把接入步骤改成用户在 Codex 中用自然语言提出接入目标，Codex 负责执行初始化、自检和证据沉淀。
- README 的推荐发放形式不再把命令作为用户接入方式，而是提供自然语言示例。
- 保留命令作为 Codex 内部验证或排障参考，但明确不要求业务用户手动执行。

## 本次明确不做

- 不改运行脚本、guard 或 adapter runtime 行为。
- 不执行 git workflow action，不创建分支、commit、push 或 PR。
- 不修改示例应用或真实业务代码。

## 影响面

- 代码 / 文档路径：
  - COMPANY_ADOPTION_GUIDE.md
  - README.md
  - .gstack/requirements/
  - .gstack/reviews/
  - .gstack/task-boundaries/
  - .gstack/qa-reports/
- 数据 / 接口 / 权限：
  `不涉及`
- spec impact：
  `not-required`

## 冻结结论

- 本文件已由 Codex 基于当前上下文复核，可同时作为 fast-lane 的 requirement brief 和 requirement freeze。
- 如果后续发现需求有多解、影响面扩大或需要业务口径确认，必须退出 fast-lane，回到 standard / discovery 流程。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Flow Lane`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `.gstack/reviews/2026-06-11_natural-language-adoption-flow-fast-lane-review.md`。
