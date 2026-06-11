# Fast-lane Review 模板

- 主题：
- 日期：
- Reviewer：Codex
- Flow Lane：`fast-lane`
- 关联 requirement：
- 关联 boundary：
- AI 语义复核：
  `yes / no`

## 结论

- 推荐结论：
  `pass / pass-with-notes / blocked`
- 是否允许进入实现：
  `是 / 否`
- 复核说明：
  `只有 AI 语义复核为 yes 时，本 review 才能满足 fast-lane 的 plan review gate。`

## CEO 视角检查

- 用户目标是否明确：
  `通过 / 未通过`
- 用户期望的可见变化是否明确：
  `通过 / 未通过`
- 是否把“筛选 / 排序 / 搜索 / 操作入口 / 看不到页面变化”误解成了 CLI 参数或静态输出：
  `否 / 是，必须修正 requirement 或向用户解释`
- 是否有多个合理产品方向需要用户选择：
  `否 / 是，必须退出 fast-lane`
- 本次是否控制在最小可交付范围：
  `通过 / 未通过`
- 明确不做：
  -

## ENG 视角检查

- 改动路径是否清晰：
  `通过 / 未通过`
- 实现表面是否已区分：
  `生成命令 / CLI 参数 / 后端接口 / 页面内交互控件 / 用户可见 UI 变化 / 静态输出`
- 若本次是 HTML / 前端 / 可视化任务，是否已有验收 URL、刷新方式和交互验证计划：
  `通过 / 未通过 / 不适用`
- 是否涉及接口、数据模型、持久化或跨模块契约：
  `否 / 是，见 Required Gates 和 Spec Sync Plan`
- 是否需要 subagent：
  `否 / 是，见 Subagent Plan`
- 是否需要 goal mode：
  `否 / 是，见 Autonomy Plan`

## Spec Sync Check

- Spec Impact:
  `updated / not-required / pending`
- Expected Spec Targets:
  -
- If Not Required, Why:
  -

## 验证计划

- 需要运行的测试 / 脚本 / 页面验证：
  -
- 用户可见 UI / HTML / 可视化任务必须包含：
  - Browser / Chrome / Playwright 交互验收，或明确 blocked / partial reason。
  - 不得只用 `rg`、JSON、HTML 字符串或截图外观替代控件可操作验证。

## 风险与退出条件

- 如果实现中发现范围扩大、业务口径多解、真实数据或接口不确定、生产 / DB / git action 需求，立即退出 fast-lane 并提示用户。
