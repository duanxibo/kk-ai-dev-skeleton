# kk-doc-backfill 产物选择矩阵

| 缺口类型 | 优先产物 | 说明 |
| --- | --- | --- |
| 产品行为缺文档 | `docs/specs/<module>/` | 当前产品行为统一补到 stack domain spec；旧 `archive/baseline/` 只作证据来源 |
| 正式工程行为缺文档 | `docs/specs/` 或对应项目 docs | 补接口、数据模型、测试设计、部署说明等工程真源 |
| 后端接口输入输出缺失 | data-interface 文档或 `docs/specs/<module>/` | 写清调用方、输入、输出、事实源、scope、异常；不要写入旧 `04_后端设计/` |
| 现有表无法满足需求 | data requirement gap | 不把需求伪装成 source，不直接进入落表实现 |
| 只有 SQL 思路或探查结论 | SQL 草案 / data discovery report | 不能写成正式 API 或长期前端依赖 |
| 风险、边界或评审缺口 | `.gstack/reviews/` | 可以基于代码证据补 review，但不能冒充 QA |
| 取舍、例外或分层裁定 | `.gstack/decisions/` | 写清背景、选项、决策和影响 |
| 可复用经验 | `.gstack/learnings/`、`.gstack/rules/`、`pitfalls` | 只沉淀未来高概率复用的经验 |
| 验证结果缺失 | 待验证清单 | 没有真实执行证据时，不写 QA 通过 |
