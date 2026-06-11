# Prototype Logic Extraction

- 主题:
- 日期:
- 目标系统 / 模块:
- 来源页面 / 原型:
- 相关 fixture / mock:
- 相关接口 / 读模型 / service:
- active boundary:
- Required Gate:
  `prototype-logic-extraction`
- owner:
  `kk-task-kickoff`
- required_before:
  `plan-eng-review`
- 状态:
  `draft / reviewed / implemented / blocked / deferred`

## Gate 状态

- status:
  `planned / done / blocked / deferred`
- evidence_path:
- blocking_reason:
  deferred 时必须写清批准来源、延期原因、风险、删除条件或后续补齐路径

## 代码证据

| 类型 | 路径 / 函数 | 检查内容 | 结论 |
| --- | --- | --- | --- |
| 页面 / 组件 / helper / fixture / mock / 测试 / 脚本 | 待补 | 待补 | 待补 |

## 逻辑归属表

| 前端逻辑 | 代码位置 / 函数 | fixture / mock 来源 | 业务含义 | 归属 | 后端承接方式 | 验收证据 |
| --- | --- | --- | --- | --- | --- | --- |
| 待补 | 待补 | 待补 | 待补 | backend-owned / frontend-owned / shared-contract | API / read model / snapshot / service / none | golden parity / QA / review / 待补 |

## 未发现项

- 未发现的金额、计划、利润、GMV、退款、ROI、转化率等指标计算:
- 未发现的保存、提交、审批、重算、快照或审计状态流转:
- 未发现的 `<scope-key>`、营期、利润中心、版本或权限 scope 隔离逻辑:
- 检查证据:

## Golden Parity

- expected output 真源:
  stack domain spec / requirement-freeze / prototype-freeze / 人工确认口径 / prototype-corrected 记录
- 输入 fixture:
- 后端输出:
- 差异处理:
  `prototype-corrected / backend-bug / scope-change / none / pending`
- 如果 pending，阻塞原因和补齐路径:

## 前端残留逻辑

- 允许保留:
- 必须移除:
- 临时保留:
- 临时保留的批准来源:
- 删除条件或后续补齐路径:

## Spec Sync Plan

- 是否同步到模块 spec / 接口设计 / 测试 fixture / QA 报告:
- 目标文档:
- Allowed No-Spec-Change Reason:
