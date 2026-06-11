# 数据发现报告模板

- 主题:
- 日期:
- 数据源:
- 查询环境:
  `只读 / 脱敏 / 待确认`
- 查询配置来源:
  `.gstack/data-access/.env.local / .gstack/data-access/config.local.yaml / 仅静态 SQL / 待确认`
- 推荐保存位置:
  探索期放 `.gstack/knowledge/data-access/discovery-reports/<date>_<topic>-discovery.md`；已归属模块后放 `docs/specs/<module>/data/discovery-reports/`
- 相关数据意图 / 数据源说明 / boundary:

## 探查目标

- 要验证的数据逻辑:
- 要确认的字段口径:
- 输出用途:
  `原型校验 / 接口设计 / 建模建议 / QA 样例`

## Scope 与查询范围

- 时间范围:
- 主 scope:
  `<scope-key> / 待确认`
- 辅助 scope:
  `profitCenter / 状态 / 版本 / 权限 / 待确认`
- 采样或 limit:

## 字段观察

| 字段 | 用途 | 口径观察 | 异常样例 |
| --- | --- | --- | --- |
| 待补 | 待补 | 待补 | 待补 |

## 查数结论

- 数据量级:
- 缺失情况:
- 异常数据:
- 边界样例:
- 与预期不一致:

## 对设计的影响

- 数据意图需调整:
- 接口输入输出需调整:
- SQL 草案位置:
- 现有数据是否满足需求:
  `满足 / 部分满足 / 不满足 / 待确认`
- 是否需要数据需求缺口文档:
  `是 / 否 / 待确认`
- 是否建议进入 relational database 读模型、快照或后端 API:

## 禁止事项确认

- [ ] 未写入账号、密码、连接串或私密环境变量
- [ ] 未保留未脱敏敏感样例
- [ ] 未输出手机号原文，且 SQL 结果、样例、截图、结论中不包含手机号
- [ ] 未把临时 SQL 当成正式接口契约
