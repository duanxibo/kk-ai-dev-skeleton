# QA 报告模板

- 主题:
- 负责人:
- 日期:
- 环境:
- 范围:
- 相关 baseline / stack / review:

## 目标

- 这次 QA 或验收要证明什么

## 测试覆盖

- 测了哪些页面、接口、脚本或流程
- 用了哪些 fixture、账号、输入样例

## 测试方式

- 手测
- 脚本
- 回归
- 对照基线检查
- Browser / Chrome / Playwright 交互验收
- 本地 HTTP server 验收

## 用户可见 UI / HTML / 可视化验收

- 是否属于用户可见 UI / HTML / 可视化任务:
  `是 / 否`
- Generated Artifact Policy:
  `static-generated-html / dev-server-page / production-page / CLI-output / backend-api / docs-only / not-generated`
- 验收 URL:
  `不适用 / http://127.0.0.1:<port>/...`
- 刷新 / 重新生成方式:
  `不适用 / 写清命令或 dev server 刷新方式`
- Browser / Chrome / Playwright 是否实际打开:
  `通过 / 未通过 / blocked / 不适用`
- 若 file:// 或权限策略阻断，是否改用本地 HTTP server:
  `通过 / 未通过 / blocked / 不适用`
- 结构存在:
  `通过 / 未通过 / blocked / 不适用`
- 控件可见:
  `通过 / 未通过 / blocked / 不适用`
- 控件可操作:
  `通过 / 未通过 / blocked / 不适用`
- 状态变化正确:
  `通过 / 未通过 / blocked / 不适用`
- 空态正确:
  `通过 / 未通过 / blocked / 不适用`
- 刷新 / 重新生成说明清晰:
  `通过 / 未通过 / blocked / 不适用`
- 是否只用了 `rg`、JSON、HTML 字符串或截图外观替代交互验收:
  `否 / 是，不能标 done`
- 如果用户指出验收遗漏:
  `不适用 / 已创建 superseding QA / 已修正原 QA 结论`
- blocked / partial reason:
  `不适用 / 写清无法完成交互验收的原因和已尝试路径`

## 数据接口验证

- 输入输出是否清晰:
  `通过 / 未通过 / 不适用`
- 数据逻辑和字段口径是否对齐:
  `通过 / 未通过 / 不适用`
- scope 是否明确:
  `通过 / 未通过 / 不适用`
- 是否误用 analytics warehouse 或临时 SQL:
  `否 / 是 / 不适用`
- 是否绕过后端 API:
  `否 / 是 / 不适用`
- relational database 落表、改表或读模型新增是否经过人工确认:
  `通过 / 未通过 / 不适用`
- 正常输入:
  `通过 / 未通过 / 不适用`
- 空数据:
  `通过 / 未通过 / 不适用`
- 异常数据:
  `通过 / 未通过 / 不适用`
- 无权限、版本状态或 scope 不匹配:
  `通过 / 未通过 / 不适用`
- 关键字段口径:
  `通过 / 未通过 / 不适用`
- 是否验证前端未直连数据库:
  `通过 / 未通过 / 不适用`
- 是否验证未暴露任意 SQL 或内部表结构:
  `通过 / 未通过 / 不适用`

## Prototype Logic Parity

- 是否需要 `prototype-logic-extraction`:
  `是 / 否，原因 / 不确定`
- 逻辑抽取 evidence path:
  `不适用 / 待补`
- expected output 真源是否已验证:
  `通过 / 未通过 / blocked / 不适用`
- 是否使用原型 fixture 或人工确认样例验证后端输出:
  `通过 / 未通过 / blocked / 不适用`
- 正常值、空值、缺失、除零、负数、重复和跨 scope 是否覆盖:
  `通过 / 未通过 / partial / 不适用`
- 后端输出与 expected output 是否一致:
  `通过 / 未通过 / pending / 不适用`
- 差异分类:
  `none / prototype-corrected / backend-bug / scope-change / pending / 不适用`
- 前端是否只保留薄渲染职责:
  `通过 / 未通过 / partial / 不适用`
- 前端残留业务计算的临时性和删除路径是否明确:
  `通过 / 未通过 / 不适用`

## Spec Sync Check

- Spec Impact:
  `updated / not-required / pending`
- Updated Spec Files:
  - 列出本次验收对应的真源文档
- If Not Required, Why:
  - 如果没改 spec，这里必须说明为什么成立

## 发现

- 阻塞问题
- 非阻塞问题
- 通过项

## 证据

- 截图
- 日志
- 命令
- 页面路径
- Browser / Chrome / Playwright 操作记录
- 本地 HTTP server URL

## 残余风险

- 这次没有覆盖的内容
- 已知但暂不处理的风险

## 建议结论

- 可发布
- 修后复测
- 需要回到基线澄清

## 可回写候选

- 是否要补 `qa-dimensions`
- 是否要补 `pitfalls`
- 是否要补 `learnings`
