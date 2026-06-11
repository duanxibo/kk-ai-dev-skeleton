# Review 报告模板

- 主题:
- 评审人:
- 日期:
- 范围:
- 相关 diff / docs:

## 结论

- pass / pass-with-risks / changes-requested

## 发现

- 严重问题
- 中风险问题
- 低风险问题

## 证据

- 相关文件
- 相关行或模块
- 复现线索

## 覆盖范围

- 这次 review 覆盖了什么
- 明确没覆盖什么

## 数据接口检查

- 输入输出是否清晰:
  `是 / 否 / 不适用`
- 数据逻辑和字段口径是否对齐:
  `是 / 否 / 不适用`
- scope 是否明确:
  `是 / 否 / 不适用`
- 是否误用 analytics warehouse、临时 SQL 或内部表结构作为正式契约:
  `否 / 是 / 不适用`
- 是否绕过后端 API:
  `否 / 是 / 不适用`
- relational database 落表、改表或读模型新增是否经过人工确认:
  `是 / 否 / 不适用`
- 空数据、异常、权限、版本状态是否验证:
  `是 / 否 / 不适用`

## Prototype Logic Extraction Check

- 是否需要 `prototype-logic-extraction`:
  `是 / 否，原因 / 不确定`
- gate owner 是否为 `kk-task-kickoff` 且 `required_before: plan-eng-review`:
  `是 / 否 / 不适用`
- 是否引用逻辑抽取 evidence path:
  `是 / 否 / 不适用`
- 是否列出实际检查过的页面、组件、helper、fixture、mock、测试或脚本:
  `是 / 否 / 不适用`
- backend-owned / frontend-owned / shared-contract 归属是否清晰:
  `是 / 否 / 不适用`
- 前端是否残留金额、计划、利润、转化率、状态流转、scope 隔离等业务计算副本:
  `否 / 是，需处理 / 不适用`
- golden parity 真源是否来自冻结基线、模块 spec、人工确认口径或明确的 `prototype-corrected` 记录:
  `是 / 否 / 不适用`
- deferred 是否写清批准来源、风险、删除条件或后续补齐路径:
  `是 / 否 / 不适用`

## Data Knowledge Sync Check

- 是否需要 `data-knowledge-sync`:
  `是 / 否，原因 / 不确定`
- boundary 是否声明 `data-knowledge-sync` 且 `owner: kk-doc-sync`、`required_before: review`:
  `是 / 否 / 不适用`
- 本次是否新增或调整 API / DTO / migration / 表 / 读模型 / 快照 / projection:
  `是 / 否 / 不确定`
- 新表、读模型、快照或 projection 是否已有 source doc:
  `是 / 否 / 不适用`
- source doc 是否已同步 `source-registry.md`:
  `是 / 否 / 不适用`
- 新接口或 DTO 是否已同步 stack domain spec / interface doc:
  `是 / 否 / 不适用`
- 生命周期状态和证据等级是否分开标注:
  `是 / 否 / 不适用`
- 代码反推结论是否避免写成未经确认的 `confirmed`:
  `是 / 否 / 不适用`

## Spec Sync Check

- Spec Impact:
  `updated / not-required / pending`
- Updated Spec Files:
  - 列出本次实际更新的 `stack/specs/` 真源文档；如引用旧原型，说明 `archive/baseline/` 证据
- If Not Required, Why:
  - 如果没改 spec，这里必须说明为什么成立

## 建议动作

- 必须修改
- 建议后续跟进

## 残余风险

- 即使通过，仍然存在的风险

## 可回写候选

- 是否要补 `code-patterns`
- 是否要补 `pitfalls`
- 是否要补 `rules`
