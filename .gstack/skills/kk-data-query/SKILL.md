---
name: kk-data-query
description: |
  KK Dev Skeleton 前期数据查询专用技能。适用于业务伙伴用自然语言提出查数需求、
  需要把业务问题整理为 Query Brief、定位候选数据源、编写只读 SQL、校验 SQL 和结果的场景。
  它只能由 kk-data-kickoff 在 data-access gate 语境中调起使用，专注于前期数据查询，不替代 kk-task-kickoff 或 kk-subagent-orchestrator。
---

# Data Query

## Overview

这个 skill 专注于前期数据查询。

它面向的默认用户不是懂数据库的人，而是只知道业务问题的伙伴。用户可以只说“查 5 月声乐 GMV”“看昨天某渠道进量是否异常”“查某个营期二阶转化”。AI 负责把业务语言整理成 Query Brief，再按数据脚手架规则查 source、写 SQL、复核结果和输出风险。

它不负责通用任务开工、active boundary、Required Gates 汇总或通用 subagent 编排，不替代 `kk-task-kickoff` 或 `kk-subagent-orchestrator`。它只在 `kk-data-kickoff` 已经确认 `data-access` gate 的语境下运行。

## When To Use

优先使用：

- 用户用业务语言提出查数需求，但不知道库表或字段结构
- 需要真实数据样例、指标结果、异常排查或口径确认
- 查询涉及 GMV、退款、利润、ROI、转化率等高风险指标
- 查询涉及多表 join、去重、状态过滤、退款或取消处理
- source 是 `draft`、`evidence-only` 或仅有 BI SQL evidence
- 查询结果将用于会议、看板、接口设计、data discovery report 或后续实现
- 查询路径涉及手机号、union_id、企微关系或财务单据等敏感字段

通常不用：

- 只解释字段或 source 文档
- 只判断 source 是否存在
- 已有明确接口契约且不需要查数
- 通用 subagent 编排、代码实现拆分、文档治理或 QA 分工

## Required Reading

0. 当前 `data-access` gate 语境和 `kk-data-kickoff` 输出说明；没有 gate 语境时回到 `kk-data-kickoff`。
1. `.gstack/knowledge/data-access/README.md`
2. `.gstack/knowledge/data-access/source-registry.md`
3. `.gstack/knowledge/data-access/query-access-guide.md`
4. 当前项目 adapter
5. `.gstack/templates/data-query-brief.template.md`
6. `.gstack/templates/data-query-review.template.md`

按任务补读：

- relational database source：`.gstack/knowledge/data-access/mysql-source-guide.md`
- analytics warehouse / BI evidence：`.gstack/knowledge/data-access/clickhouse-discovery-guide.md`
- 接口设计：`.gstack/knowledge/data-access/interface-design-guide.md`

## Workflow

1. 先做 Business Intake，只问业务问题，不要求用户提供库表或字段：
   - 时间范围
   - 条目、营期、渠道、利润中心等 scope
   - 指标口径
   - 输出粒度
   - 结果用途
   - 可接受风险
2. 按 `.gstack/templates/data-query-brief.template.md` 整理 Query Brief。
3. 做 Source Explorer：
   - 查 `source-registry.md`
   - 查 relational database source
   - 查 analytics warehouse 表级 source、curated topic 和人工可用性反馈
   - 只在需要溯源或风险对照时查 BI `sql-evidence/`
   - 查已有 SQL draft 和 data discovery report
   - 标记 source 状态：`confirmed / draft / evidence-only / gap`
   - 输出 `recommended_sources`、`rejected_sources`、`source_status`、`allowed_sql_inputs`、`forbidden_sql_inputs`、`join_keys_and_risks`
4. 如果缺少事实源、字段、粒度、口径或权限，先输出待确认问题或 requirement gap，不硬写 SQL。
5. 如果可以查，SQL Author 写只读 SQL：
   - 必须带时间范围
   - 必须带 scope、limit 或聚合约束
   - 不执行 DDL / DML / 删除 / 更新 / 授权
   - 不把临时 SQL 当正式 API
   - 不直接复制或参数替换 `sql-evidence/cards/` 中的 BI 原 SQL
   - 必须附 source 使用清单、rejected source、`sql-evidence` 使用方式、join 粒度与放大风险、source 状态、假设和风险
6. SQL Reviewer 独立复核：
   - 是否回答原业务问题
   - 时间范围、scope、粒度是否正确
   - join 是否放大
   - 去重、状态过滤、退款和取消处理是否合理
   - 是否误用 `draft / evidence-only`
   - 是否直接依赖 BI 原 SQL 而没有基于 Query Brief 重新生成
   - 是否泄露敏感字段
   - 是否存在 analytics warehouse `FULL OUTER JOIN + coalesce`、Nullable join key、模糊文本过滤等兼容性或口径风险
7. 输出 `PASS / PASS_WITH_RISKS / FAIL`：
   - `PASS`：可以输出业务结论
   - `PASS_WITH_RISKS`：必须说明风险，不能包装成 confirmed
   - `FAIL`：仅用于手机号原文进入最终结果集、SQL 输出列、文档样例、subagent 输出或最终答复；其他问题默认退回修正或标记 `PASS_WITH_RISKS`
8. 最终由 main agent 交付：
   - 业务结论
   - 查询口径
   - 可复跑 SQL
   - 结果摘要
   - source 状态
   - 风险和待确认项
   - 是否需要沉淀 SQL draft、data discovery report、interface design 或 requirement gap

## Hard Boundaries

- “禁止输出手机号原文”对整个数据能力生效，不只限本 skill。
- SQL 最终结果集不得包含 `phone`、`mobile`、`tel`、`手机号`、`手机` 等手机号字段。
- 手机号如必须参与 join、去重、匹配或缺失率计算，只能留在数据库内部计算，不进入结果集、repo 文档、subagent 输出或最终答复。
- 历史 BI SQL evidence 中出现手机号时，只能作为敏感字段风险信号，不能照抄为新查询输出。
- 未脱敏明细不得写入 repo 文档。
- 真实账号、密码、连接串不能写入 repo、skill、模板或聊天交付。
- 不把 analytics warehouse / BI 临时查询包装成正式业务口径、正式 API 或长期依赖。
- 不把 `sql-evidence/cards/` 作为直接查询来源；历史 SQL 只能提供字段、join、过滤和看板上下文线索。

## Output Rules

- 默认输出业务口径和风险，而不是只输出 SQL。
- 业务问题不清楚时先问用户，不猜口径。
- 用户不懂库表时，由 AI 查 registry 和 source docs，不把问题抛回给用户。
- 复杂查数必须有 Query Brief 和 Query Review。
- 结果要用于会议、看板、接口设计或实现时，必须说明 source 状态和残余风险。
- Query Brief / Query Review / Data Discovery Report 必须按模板推荐落点保存；不要直接写在 `.gstack/knowledge/data-access/` 根目录。
- 输出回到 `kk-data-kickoff`，由它汇总为 `data-access` gate evidence；本 skill 不创建独立 boundary，不直接决定实现准入。

## Document Storage Rules

一次查询需求产生的过程产物必须按职责保存，不能全部堆到 `data-access` 根目录：

- Query Brief：探索期放 `.gstack/requirements/data-query/`；已归属项目后放 adapter 指定的项目 data / specs 目录。
- Query Review：探索期放 `.gstack/reviews/data-query/`；已归属项目后放 adapter 指定的项目 data / specs 目录。
- Data Discovery Report：探索期放 `.gstack/knowledge/data-access/discovery-reports/`；已归属项目后放 adapter 指定的项目 data / specs 目录。
- SQL Draft：探索期放 `.gstack/knowledge/data-access/sql-drafts/`；已归属项目后放 adapter 指定的项目 data / specs 目录。
- Requirement Gap：探索期放 `.gstack/knowledge/data-access/requirement-gaps/`；已归属项目后放 adapter 指定的项目 data / specs 目录。
- `data-access` 根目录只保留 `README.md`、guide、registry 和跨源汇总；新的一次性查询报告不得直接放根目录。

如果同一查询同时产出 SQL draft、discovery report 和 review，三者应互相链接，并在 `.gstack/knowledge/data-access/source-registry.md` 保留索引。

## Template Sources

- Query Brief：`../../templates/data-query-brief.template.md`
- Query Review：`../../templates/data-query-review.template.md`
- Data Discovery Report：`../../templates/data-discovery-report.template.md`
- SQL Draft：`../../knowledge/data-access/sql-drafts/`
- Requirement Gap：`../../templates/data-requirement-gap.template.md`
