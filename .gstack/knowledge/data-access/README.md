# Data Access 知识入口

本目录定义通用数据访问协作规则。它不包含真实连接串、真实账号、客户数据或某个项目的私有表结构。

数据任务仍必须先经过 `kk-task-kickoff` 创建或更新 task boundary，并在 boundary 的 `Required Gates` 中声明 `data-access`。本目录只提供 gate 执行所需的通用知识和文档落点。

## 何时触发 data-access

- 页面、看板或报表需要接真实数据。
- 前端 mock / fixture 要替换为后端 API。
- 新增或调整 API 输入输出、事实源、scope 或错误语义。
- 需要读取 relational database、analytics warehouse、BI 报表或历史 SQL。
- 用户提供表说明、字段口径、查询主题或查数结论。
- 数据会跨系统复用。

## 目录职责

- `source-registry.md`
  数据源索引，只登记已存在且被确认的数据资产。
- `mysql-source-guide.md`
  relational database source 文档规则。
- `clickhouse-discovery-guide.md`
  analytics warehouse / BI 探查规则。
- `query-access-guide.md`
  开发期只读查询、安全和脱敏规则。
- `interface-design-guide.md`
  数据进入 API、读模型或跨系统接口前的设计规则。

可选子目录：

```text
sources/                 已确认 source docs
sql-drafts/              探索期 SQL 草案
discovery-reports/       只读数据发现报告
requirement-gaps/        现有数据无法满足时的缺口记录
```

## 基本原则

- 不把未满足的数据需求伪装成 source。
- 不把临时 SQL 当成正式 API。
- 不让前端直接依赖数据库表、analytics warehouse 查询或任意 SQL。
- 不把账号、密码、连接串写入 repo 文档。
- 不输出手机号、身份证、token、密钥或原始敏感字段。
- 真实数据访问必须符合 adapter 的权限、scope 和只读规则。
- 数据发现结论必须记录新鲜度、样本范围和残余风险。

## Gate 输出

`data-access` gate evidence 至少说明：

- 目标用户和业务问题
- 所需字段、指标和粒度
- 事实源和 source 状态
- scope、时间范围和权限边界
- 空态、异常态和缺失数据行为
- 是否需要 API / 读模型 / data product
- 是否存在数据缺口
- 是否可以进入实现

## 与 adapter 的关系

本目录只定义通用规则。项目必须在 adapter 中说明：

- 数据源类型
- 允许的查询方式
- 禁止访问的系统和字段
- API 和数据模型真源路径
- 数据相关测试命令
- 发布和回滚规则
