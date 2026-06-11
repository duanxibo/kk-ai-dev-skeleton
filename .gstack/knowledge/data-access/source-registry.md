# Source Registry

本文件是数据源索引模板。

公开骨架默认不登记任何真实数据源。接入项目后，由 adapter 或项目任务在本索引中登记已确认的数据资产，并链接到 `sources/` 下的 source doc。

## 登记规则

- 只登记已经存在的数据资产、BI 报表、历史 SQL evidence 或已确认表说明。
- 不登记“希望未来有”的数据需求。
- 不记录账号、密码、连接串、密钥或原始敏感字段。
- 每条 source 都要标注证据等级和生命周期状态。

## Source Index

| source id | type | owner | status | evidence | notes |
| --- | --- | --- | --- | --- | --- |
| `example-source` | `example` | `adapter` | `template-only` | `adapters/default/adapter.md` | 示例占位，不是真实数据源 |

## 状态枚举

- `template-only`
- `candidate`
- `confirmed`
- `deprecated`
- `blocked`

## 证据等级

- `manual-note`
- `schema-doc`
- `read-only-query`
- `production-contract`
- `unknown`
