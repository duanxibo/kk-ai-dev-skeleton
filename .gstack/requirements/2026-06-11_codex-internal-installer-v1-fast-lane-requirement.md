# codex-internal-installer-v1 Fast-lane Requirement

- 需求名称：codex-internal-installer-v1
- 提出人：用户
- 日期：2026-06-11
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md`
- 生成方式：
  `deterministic-scaffold`
- AI 语义复核：
  `yes`

## 需求一句话

- 用户要完成什么：实现 V1 内部安装器能力：在保留自然语言用户入口的前提下，为 Codex 提供 detect / plan / apply / verify / report 确定性 helper

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

- 增强 `scripts/init_project.py`，提供 Codex 可调用的 detect / plan / apply / verify / report 内部安装器能力。
- 保留旧参数 `--adapter`、`--create-adapter`、`--force`、`--run-doctor` 的兼容行为。
- 增加脚本级测试，覆盖 slug、detect、plan、apply 不覆盖、report 和 verify 命令编排。
- 更新产品化文档和接入指南，说明 V1 内部安装器已具备可执行 helper。
- 写 QA evidence 并运行 guard。

## 本次明确不做

- 不实现正式 Codex plugin。
- 不接入外部分发平台。
- 不默认覆盖已有 adapter。
- 不做生产、数据库、真实数据或 git workflow 自动化。

## 影响面

- 代码 / 文档路径：
  - `scripts/init_project.py`
  - `scripts/dev_stack.sh`
  - `tests/test_init_project.py`
  - `CODEX_ADOPTION_CONNECTOR.md`
  - `COMPANY_ADOPTION_GUIDE.md`
  - `README.md`
  - `.gstack/knowledge/code-patterns.md`
  - `.gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md`
  - `.gstack/qa-reports/2026-06-11_codex-internal-installer-v1-qa.md`
- 数据 / 接口 / 权限：
  `不涉及`
- spec impact：
  `not-required`

## 冻结结论

- 本文件已由 Codex 基于当前上下文复核，可同时作为 fast-lane 的 requirement brief 和 requirement freeze。
- 如果后续发现需求有多解、影响面扩大或需要业务口径确认，必须退出 fast-lane，回到 standard / discovery 流程。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Flow Lane`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `.gstack/reviews/2026-06-11_codex-internal-installer-v1-fast-lane-review.md`。
