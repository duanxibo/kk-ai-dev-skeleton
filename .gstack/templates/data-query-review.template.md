# 数据查询 Review 模板

- 主题:
- 日期:
- Reviewer:
- Query Brief:
- SQL 草案:
- 查询结果:
- 推荐保存位置:
  `.gstack/reviews/data-query/<date>_<topic>-query-review.md`；若已归属模块，放到对应 `docs/specs/<module>/data/query-reviews/`
- Review 状态:
  `PASS / PASS_WITH_RISKS / FAIL`

## Review 结论

- 是否回答原业务问题:
  `是 / 否 / 部分`
- 是否可向用户输出业务结论:
  `是 / 否 / 带风险`
- 主要风险:

## Query Brief 对齐

- 时间范围是否一致:
- scope 是否一致:
- 输出粒度是否一致:
- 指标口径是否一致:
- 用户未确认项是否被明确标注:

## SQL 检查

- 是否只读:
- 是否有时间范围:
- 是否有 scope、limit 或聚合约束:
- 是否存在 analytics warehouse `FULL OUTER JOIN + coalesce` 默认值风险:
- Nullable join key 是否显式处理:
- 模糊文本过滤是否会扩大口径:
- join key 是否合理:
- 是否存在 join 放大风险:
- 是否存在重复计数风险:
- 状态过滤是否合理:
- 退款、取消、作废处理是否合理:
- distinct / 去重逻辑是否合理:

## 结果复核

- 是否运行成功:
- 行数或聚合结果:
- 对照 SQL / count / distinct / sample 复核:
- 与预期不一致:
- 空值、异常值或边界样例:

## Source 风险

- source 状态:
  `confirmed / draft / evidence-only / gap / 待确认`
- 是否误用 evidence-only 为正式口径:
- 是否直接复制或参数替换 BI 原 SQL:
  `no / yes / n/a`
- sql-evidence 使用方式:
  `not-used / provenance-only / field-join-risk-only / direct-sql-source`
- direct-sql-source 处理:
  `标记风险并退回重写 SQL；除非同时触发手机号直出，否则不作为硬 FAIL`
- 是否需要 owner 确认:
- 是否需要 requirement gap:

## 敏感字段检查

- 最终结果集是否包含手机号原文:
  `否 / 是，必须 FAIL`
- SQL 输出列是否包含 `phone`、`mobile`、`tel`、`手机号`、`手机`:
  `否 / 是，必须 FAIL`
- 手机号是否仅用于数据库内部计算:
  `是 / 否 / 不适用`
- 是否包含其他未脱敏敏感字段:
- 是否可写入 repo 文档:
  `是 / 否`

## 状态判定规则

- `FAIL`:
  手机号原文进入最终结果集、SQL 输出列、文档样例、subagent 输出或最终答复。
- `PASS_WITH_RISKS`:
  source 未 confirmed、direct-sql-source、缺少时间/scope、join 放大、analytics warehouse 兼容性风险、指标口径未确认、其他敏感字段需脱敏等。
- `PASS`:
  无手机号直出，SQL 与 Query Brief 对齐，source 状态、风险和限制均已清楚披露。

## 后续动作

- 可直接交付:
  `是 / 否 / 带风险`
- 需要 SQL Author 修正:
- 需要 Main Agent 回问用户:
- 建议沉淀:
  `SQL draft / data discovery report / requirement gap / interface design / 不需要`
