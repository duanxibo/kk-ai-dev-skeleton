# codex-adoption-plugin-v2 Fast-lane Requirement

- 需求名称：codex-adoption-plugin-v2
- 提出人：用户
- 日期：2026-06-11
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_codex-adoption-plugin-v2.md`
- 生成方式：
  `deterministic-scaffold`
- AI 语义复核：
  `yes`

## 需求一句话

- 用户要完成什么：创建 repo-local Codex 接入器 plugin 骨架，包装 V1 内部安装器，让公司内部后续可产品化分发

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

- 创建 repo-local Codex plugin 源目录 `plugins/kk-dev-skeleton-adoption/`。
- 提供 `.codex-plugin/plugin.json`，让 plugin validator 通过。
- 提供 plugin skill，包装 V1 内部安装器的 detect / plan / apply / verify / report 工作流。
- 更新 README、公司接入指南和产品化方案，说明 V2 是可分发 plugin 源目录，不是已安装 marketplace。
- 写 QA evidence 并运行 plugin validator、gstack guard 和文案检索。

## 本次明确不做

- 不安装 plugin 到当前 Codex。
- 不创建或修改 marketplace 文件。
- 不实现 MCP server、app、hook 或真实外部连接器。
- 不修改 V1 内部安装器行为。
- 不做生产、数据库、真实数据或 git workflow 自动化。

## 影响面

- 代码 / 文档路径：
  - `plugins/kk-dev-skeleton-adoption/`
  - `plugins/README.md`
  - `CODEX_ADOPTION_CONNECTOR.md`
  - `COMPANY_ADOPTION_GUIDE.md`
  - `README.md`
  - `.gstack/knowledge/code-patterns.md`
  - `.gstack/task-boundaries/2026-06-11_codex-adoption-plugin-v2.md`
  - `.gstack/qa-reports/2026-06-11_codex-adoption-plugin-v2-qa.md`
- 数据 / 接口 / 权限：
  `不涉及`
- spec impact：
  `not-required`

## 冻结结论

- 本文件已由 Codex 基于当前上下文复核，可同时作为 fast-lane 的 requirement brief 和 requirement freeze。
- 如果后续发现需求有多解、影响面扩大或需要业务口径确认，必须退出 fast-lane，回到 standard / discovery 流程。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Flow Lane`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `.gstack/reviews/2026-06-11_codex-adoption-plugin-v2-fast-lane-review.md`。
