# 数据查询 Brief 模板

- 主题:
- 日期:
- 发起人 / 使用方:
- 推荐保存位置:
  `.gstack/requirements/data-query/<date>_<topic>-query-brief.md`；若已归属模块，放到对应 `docs/specs/<module>/data/query-briefs/`
- 当前阶段:
  `临时查数 / 口径确认 / 异常排查 / 会议同步 / 接口设计 / 看板固化`
- 相关 boundary / source / SQL:

## 业务问题

- 用户想解决什么问题:
- 结果用途:
- 期望输出:
  `总数 / 趋势 / TopN / 分组聚合 / 脱敏样例 / 其他`

## 指标与口径

- 指标名称:
- 口径定义:
- 是否包含退款、取消、作废、重复:
- 分子:
- 分母:
- 计算逻辑:
- 不明确项:

## Scope 与时间范围

- 时间范围:
- 主 scope:
  `<scope-key> / 待确认`
- 辅助 scope:
  `渠道 / 营期 / 利润中心 / 状态 / 版本 / 权限 / 待确认`
- 输出粒度:
  `日 / 月 / 条目 / 渠道 / 营期 / 用户 / 订单 / 待确认`

## 数据源发现要求

- 已知 source:
- 候选 source:
- rejected source:
- allowed SQL inputs:
  `source-registry / table source / curated topic / sql-drafts / discovery-reports`
- forbidden SQL inputs:
  `sql-evidence/cards direct SQL source / 未确认明细样例 / 账号密码连接串`
- 是否允许使用 analytics warehouse / BI evidence:
  `sql-evidence/` 仅限溯源、字段线索、join 风险和口径对照，不作为直接查询 SQL 来源。
  `是 / 否 / 待确认`
- 是否需要 relational database 正式读模型:
  `是 / 否 / 待确认`
- 如果找不到现有 source，是否输出 requirement gap:
  `是 / 否 / 待确认`

## 查询安全边界

- 是否允许真实查询:
  `是 / 否 / 待确认`
- 查询账号:
  `只读 / 待确认`
- 采样或 limit:
- 敏感字段:
  `手机号 / union_id / 企微关系 / 财务单据 / 地址 / 其他 / 无 / 待确认`
- 手机号处理:
  禁止输出手机号原文；如必须用于 join、去重或匹配，只能在数据库内部计算，不进入结果集、文档或最终答复。

## Subagent 分工建议

- Source Explorer:
- sql-evidence 使用边界:
  `not-used / provenance-only / field-join-risk-only`，不得作为 direct SQL source
  `需要 / 不需要`
- SQL Author:
  `需要 / 不需要`
- SQL Author 必须输出:
  `source 使用清单 / rejected source / sql-evidence 使用方式 / join 粒度与放大风险 / source 状态 / 假设与风险`
- SQL Reviewer:
  `需要 / 不需要`
- 触发理由:

## 验收方式

- 业务侧期望看到:
- 可接受风险:
- 必须阻断的问题:
  `手机号原文进入最终结果集或 SQL 输出列`
