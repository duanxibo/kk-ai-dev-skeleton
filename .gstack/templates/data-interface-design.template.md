# 数据接口设计模板

- 接口主题:
- 日期:
- 所属系统 / 模块:
- 调用方:
- 相关数据意图 / 数据源 / boundary:
- 相关 Required Gate:
  `data-access`
- 相关 Data Knowledge Sync:
  status: `not-required / planned / done / blocked / deferred`
  evidence_path: `不适用 / docs/specs/<module>/backend.md / docs/specs/<module>/data.md / .gstack/designs/<date>_<topic>.md`
- 相关 Prototype Logic Extraction:
  evidence_path: `不适用 / .gstack/designs/<date>_<topic>-prototype-logic-extraction.md / stack/<service>/...`
  status: `not-required / planned / done / blocked / deferred`
- 设计状态:
  `draft / confirmed / deprecated / evidence-only / manual-review`
- 实现状态:
  `not-implemented / implemented / deprecated / needs-confirmation`
- 证据等级:
  `code-proven / test-proven / spec-proven / inferred / needs-confirmation`

说明：

- 设计状态表示接口说明生命周期，不表示证据强度；实现状态单独说明代码是否已经落地。
- 证据等级表示当前接口说明来自代码、测试、spec、推断还是仍待确认。
- 从代码反推的新接口默认不能写成 `confirmed`；没有人工确认、正式 review 或 domain-spec-readiness 证据时，最高只说明为代码或测试可证明的实现现状。

## 场景与边界

- 使用场景:
- 是否跨系统复用:
  `是 / 否 / 待确认`
- 正式事实源:
- 不应暴露的内部结构:

## 输入

| 参数 | 类型 | 必填 | 口径 / 合法范围 |
| --- | --- | --- | --- |
| 待补 | 待补 | 待补 | 待补 |

## 输出字段

| 字段 | 类型 | 含义 | 来源 | 口径 / 计算逻辑 |
| --- | --- | --- | --- | --- |
| 待补 | 待补 | 待补 | 待补 | 待补 |

## 前端逻辑迁移

- 前端逻辑来源:
  页面 / 组件 / helper / fixture / mock / 测试 / 脚本路径
- 迁移到后端的计算逻辑:
  金额 / 计划 / 利润 / 转化率 / 状态流转 / scope 隔离 / 其他
- 允许留在前端的展示逻辑:
  格式化 / 请求编排 / 输入校验 / 瞬时 UI 状态
- 后端派生字段:
  字段名、来源、计算口径、复算方式
- 前端残留业务计算检查:
  `未发现 / 已列出临时保留项和删除条件 / 待检查`

## Golden Parity

- expected output 真源:
  stack domain spec / requirement-freeze / prototype-freeze / 人工确认口径 / prototype-corrected 记录
- 输入 fixture:
- 后端输出:
- 差异处理:
  `none / prototype-corrected / backend-bug / scope-change / pending`

## 敏感字段边界

- 是否涉及手机号、union_id、企微关系、财务单据或地址:
  `否 / 是，待脱敏设计 / 待确认`
- 手机号处理:
  禁止输出手机号原文；正式接口输出字段不得包含手机号原文。

## Scope

- 主 scope:
  `<scope-key> / 待确认`
- 辅助 scope:
  `profitCenter / 状态 / 版本 / 权限 / 待确认`
- scope 不匹配时:

## 异常返回

| 场景 | 返回策略 | 调用方处理 |
| --- | --- | --- |
| 空数据 | 待补 | 待补 |
| 参数非法 | 待补 | 待补 |
| 无权限 | 待补 | 待补 |
| 数据源异常 | 待补 | 待补 |

## 实现前确认

- 是否已回写 active boundary 的 `Required Gates`:
  `否 / 已标 planned / 已标 done / blocked / deferred`
- `prototype-logic-extraction` evidence 是否已引用:
  `不适用 / 已引用 / 待补`
- 是否需要新增或修改 relational database 表:
  `否 / 需要人工确认`
- 是否依赖 analytics warehouse 探查:
  `否 / 是，且仅作为开发期依据`
- Review / QA 必测:
  输入、输出、scope、字段口径、空数据、异常状态、敏感字段禁出

## 实现后知识回写

- 新增或调整的 API / DTO:
  `无 / 已列出 / 待补`
- 是否已同步 stack domain spec:
  `不适用 / 已同步 / 待补`
- 是否涉及新增表、读模型、快照或 projection:
  `否 / 是，已补 source doc / 是，待补`
- 是否已同步 `source-registry.md`:
  `不适用 / 已同步 / 待补`
- 代码反推结论:
  `无 / code-proven / test-proven / spec-proven / inferred / needs-confirmation`
