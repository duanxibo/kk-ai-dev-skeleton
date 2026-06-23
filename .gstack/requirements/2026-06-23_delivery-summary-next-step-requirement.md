# Delivery summary next-step fast-lane requirement

- 需求名称：交付总结下一步建议强制输出
- 提出人：用户
- 日期：2026-06-23
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-23_delivery-summary-next-step.md`
- AI 语义复核：`yes`

## 需求一句话

- 完成交付总结、团队完成说明或最终收口时，公开骨架必须强制输出“下一步建议”，避免用户只看到“已完成”而不知道后续验收、反馈或下一轮修改。

## 为什么可以走 fast-lane

- 范围小：是，只改 framework core 的 helper、router、smoke、skill、knowledge 和 AGENTS 规则。
- 需求明确：是，用户输出必须包含 `下一步建议`。
- 不涉及业务口径多解：是。
- 不涉及 DB schema、真实数据、生产、外部服务或 git workflow action：是。
- 可本地验证：是，可运行自然语言 smoke 和 runtime verify。

## 本次必须做

- `nontechnical_delivery_summary.py` 增加 `next_step_suggestions` 字段。
- `nontechnical_delivery_summary.py --format user` 固定输出 `下一步建议`。
- `nontechnical_intent_router.py` 的交付总结路由说明同步包含下一步建议。
- `natural_language_dev_smoke.py` 覆盖 JSON 字段和用户输出片段。
- `kk-natural-language-dev`、framework knowledge 和 `AGENTS.md` 写入完成后下一步建议规则。

## 本次明确不做

- 不实现任何具体项目功能。
- 不接真实数据、生产、数据库、GitHub 或远程 runner。
- 不执行 commit、push、PR 或其它 git workflow action，除非用户另行明确授权。

## 冻结结论

- 本文件同时作为 fast-lane requirement brief 和 requirement freeze。
