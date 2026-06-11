# codex-marketplace-rollout Fast-lane Requirement

- 需求名称：codex-marketplace-rollout
- 提出人：用户
- 日期：2026-06-11
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_codex-marketplace-rollout.md`
- 生成方式：
  `deterministic-scaffold`
- AI 语义复核：
  `yes`

## 需求一句话

- 用户要完成什么：准备 marketplace/plugin 安装推广包：管理员安装清单、试点伙伴说明、反馈表和回滚策略，不在当前环境执行安装

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

- 新增 marketplace/plugin 安装推广指南。
- 新增管理员安装检查清单。
- 新增试点反馈表。
- 更新现有 marketplace install 文档、README 和公司接入指南。
- 增加文档结构测试，确认推广材料关键章节存在且不把普通用户入口改成命令行。

## 本次明确不做

- 不在当前环境执行 `codex plugin marketplace add` 或 `codex plugin add`。
- 不修改 marketplace manifest、plugin manifest 或 plugin skill。
- 不写个人 marketplace。
- 不做远程 marketplace、权限服务、MCP server 或 app UI。

## 影响面

- 代码 / 文档路径：
  - `plugins/MARKETPLACE_ROLLOUT.md`
  - `plugins/ADMIN_INSTALL_CHECKLIST.md`
  - `plugins/PILOT_FEEDBACK.md`
  - `plugins/MARKETPLACE_INSTALL.md`
  - `plugins/README.md`
  - `.agents/plugins/README.md`
  - `tests/test_marketplace_rollout_docs.py`
  - `COMPANY_ADOPTION_GUIDE.md`
  - `README.md`
  - `CODEX_ADOPTION_CONNECTOR.md`
  - `.gstack/task-boundaries/2026-06-11_codex-marketplace-rollout.md`
  - `.gstack/qa-reports/2026-06-11_codex-marketplace-rollout-qa.md`
- 数据 / 接口 / 权限：
  `不涉及`
- spec impact：
  `not-required`

## 冻结结论

- 本文件已由 Codex 基于当前上下文复核，可同时作为 fast-lane 的 requirement brief 和 requirement freeze。
- 如果后续发现需求有多解、影响面扩大或需要业务口径确认，必须退出 fast-lane，回到 standard / discovery 流程。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Flow Lane`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `.gstack/reviews/2026-06-11_codex-marketplace-rollout-fast-lane-review.md`。
