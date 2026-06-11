# Relational Database Source Guide

本指南用于登记 relational database source。它不授权连接真实数据库。

## 进入条件

只有在以下信息至少部分存在时，才创建 source doc：

- 表或视图已经存在。
- 用户或项目文档提供了字段说明。
- 只读查询已经在允许 scope 内验证。
- adapter 允许该数据源用于开发期探查。

## 必填信息

- source id
- 所属系统或服务
- 表 / 视图 / API 名称
- 字段说明和敏感级别
- 主键或业务唯一键
- 时间字段和新鲜度假设
- scope 边界
- 允许用途
- 禁止用途
- evidence path

## 禁止

- 不把建表需求写成已存在 source。
- 不写连接串、账号、密码或网络地址。
- 不输出手机号、身份证、token、密钥等敏感字段原文。
- 不让前端直接依赖 relational database 表结构。
- 不用临时查询结果替代 API 契约。

## 推荐落点

- source doc：
  `.gstack/knowledge/data-access/sources/<type>/<source-id>.md`
- 数据缺口：
  `.gstack/knowledge/data-access/requirement-gaps/<date>_<topic>.md`
- SQL 草案：
  `.gstack/knowledge/data-access/sql-drafts/<date>_<topic>.sql`

进入具体项目实现后，优先迁移到 adapter 指定的项目真源目录。
