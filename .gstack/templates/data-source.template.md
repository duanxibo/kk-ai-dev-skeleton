# 数据源说明模板

- 数据源名称:
- 数据源类型:
  `relational database / analytics warehouse`
- 日期:
- 状态:
  `draft / confirmed / deprecated / evidence-only / manual-review`
- 证据等级:
  `code-proven / test-proven / spec-proven / inferred / needs-confirmation`
- 相关任务 / boundary:

说明：

- 状态表示生命周期，不表示证据强度。
- 证据等级表示当前结论来自代码、测试、spec、推断还是仍待确认。
- 不要把 `code-proven / test-proven / spec-proven / inferred / needs-confirmation` 写进状态字段。

## 用途与边界

- 业务用途:
- 当前定位:
  `事实源 / 快照 / 读模型 / 探查主题 / 待确认`
- 是否已有后端 API:
  `有 / 无 / 待确认`
- 是否可开发期查询:
  `可用本机只读配置 / 仅静态说明 / 待确认`
- 禁止直接暴露给:
  `前端 / 跨系统调用方 / 待确认`

## Scope 与粒度

- 主 scope:
  `<scope-key> / 待确认`
- 辅助 scope:
  `profitCenter / 状态 / 版本 / 权限 / 待确认`
- 数据粒度:
- 刷新或更新时间:

## 字段与口径

| 字段 | 含义 | 用途 | 口径 / 计算逻辑 | 异常值说明 |
| --- | --- | --- | --- | --- |
| 待补 | 待补 | 筛选 / 展示 / 计算 / 分组 | 待补 | 待补 |

## 数据逻辑

- 有效记录判断:
- 去重或版本选择:
- 关键指标计算:
- 排序或分组:

## 异常状态

- 空数据:
- 缺失字段:
- 异常值:
- 数据延迟:
- 权限或脱敏要求:
- 手机号处理:
  禁止输出手机号原文；如果该 source 包含手机号字段，只能记录字段存在和用途风险，不在样例或结果中保留手机号原文。

## 后续动作

- 是否需要接口设计:
  `是 / 否 / 待确认`
- 是否需要 relational database 落表、改表或读模型:
  `否 / 仅提案待确认`
