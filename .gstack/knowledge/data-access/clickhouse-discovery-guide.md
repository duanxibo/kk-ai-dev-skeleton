# Analytics Warehouse Discovery Guide

本指南用于 analytics warehouse、BI 或报表 SQL 的开发期探查。具体技术可以是 ClickHouse、BigQuery、ODPS、Snowflake、Redshift 或项目 adapter 指定的其它系统。

## 目标

- 判断现有数据是否支持需求。
- 提炼字段、指标、粒度和时间范围。
- 识别数据缺口和口径风险。
- 为 API / 读模型 / 报表设计提供证据。

## 必须记录

- 查询目的
- 查询 scope
- 数据新鲜度
- 样本限制
- 字段口径
- join / 聚合 / 去重规则
- 空值、重复、异常值处理
- 敏感字段处理
- 残余风险

## 输出类型

- discovery report
- SQL draft
- data requirement gap
- query review

## 禁止

- 不把 analytics warehouse SQL 直接暴露给前端。
- 不把 BI 查询当成正式服务契约。
- 不把探索期 SQL 写成长期 API 实现。
- 不输出原始敏感字段。
- 不在没有 adapter 授权时连接真实数据。
