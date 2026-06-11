# codex-adoption-marketplace-v3 Fast-lane Requirement

- 需求名称：codex-adoption-marketplace-v3
- 提出人：用户
- 日期：2026-06-11
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_codex-adoption-marketplace-v3.md`
- 生成方式：
  `deterministic-scaffold`
- AI 语义复核：
  `yes`

## 需求一句话

- 用户要完成什么：创建公司内部 marketplace 源和安装升级策略，连接 V2 plugin 源目录，但不在当前环境执行安装

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

- 创建 repo-local marketplace source：`.agents/plugins/marketplace.json`。
- 编写内部 marketplace 安装与升级说明，明确安装是管理员 / 发布步骤，不是业务用户默认入口。
- 增加测试验证 marketplace JSON 结构、policy 字段、source path 和 plugin manifest 存在。
- 更新 README、公司接入指南和产品化方案，说明 V3 分发路径。
- 写 QA evidence 并运行 plugin validator、skill validator、marketplace name reader、unit test 和 gstack guard。

## 本次明确不做

- 不在当前环境执行 `codex plugin marketplace add` 或 `codex plugin add`。
- 不写个人 marketplace。
- 不修改 V1 helper 行为。
- 不修改 V2 plugin manifest / skill 行为。
- 不实现远程 marketplace、权限服务、MCP server 或 app UI。

## 影响面

- 代码 / 文档路径：
  - `.agents/plugins/marketplace.json`
  - `.agents/plugins/README.md`
  - `plugins/MARKETPLACE_INSTALL.md`
  - `tests/test_plugin_marketplace.py`
  - `CODEX_ADOPTION_CONNECTOR.md`
  - `COMPANY_ADOPTION_GUIDE.md`
  - `README.md`
  - `.gstack/knowledge/code-patterns.md`
  - `.gstack/task-boundaries/2026-06-11_codex-adoption-marketplace-v3.md`
  - `.gstack/qa-reports/2026-06-11_codex-adoption-marketplace-v3-qa.md`
- 数据 / 接口 / 权限：
  `不涉及`
- spec impact：
  `not-required`

## 冻结结论

- 本文件已由 Codex 基于当前上下文复核，可同时作为 fast-lane 的 requirement brief 和 requirement freeze。
- 如果后续发现需求有多解、影响面扩大或需要业务口径确认，必须退出 fast-lane，回到 standard / discovery 流程。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Flow Lane`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `.gstack/reviews/2026-06-11_codex-adoption-marketplace-v3-fast-lane-review.md`。
