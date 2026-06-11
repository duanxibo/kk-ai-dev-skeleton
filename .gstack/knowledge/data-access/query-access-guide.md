# Query Access Guide

本指南定义开发期只读查询规则。它不是数据库连接说明，也不包含任何真实凭据。

## 默认立场

- 默认不连接真实数据。
- 只有 adapter 明确允许，且用户确认 scope 后，才可以做开发期只读查询。
- 查询只能服务于需求澄清、接口设计、数据发现或 QA 验证。
- 查询结果必须脱敏，并控制行数。

## 查询前检查

- 是否有 active task boundary。
- boundary 是否声明 `data-access` 或 `data-query` gate。
- adapter 是否允许访问该数据源。
- 用户是否确认查询目的、时间范围、scope 和输出粒度。
- 是否有只读账号或只读代理。
- 是否能避免输出敏感字段。

## 查询结果记录

查询结论应写入：

- `.gstack/reviews/data-query/`
- `.gstack/knowledge/data-access/discovery-reports/`
- adapter 指定的项目 data docs

记录时写结论，不写凭据；必要 SQL 草案可保存，但不能包含秘密、token 或原始敏感输出。

## 高风险情况

以下情况必须暂停并向用户确认：

- 需要写数据库。
- 需要改 schema、索引、权限或生产配置。
- 需要导出大批量数据。
- 需要输出敏感字段原文。
- 查询 scope 可能影响生产性能。
- 查询目的超出 adapter 允许范围。
