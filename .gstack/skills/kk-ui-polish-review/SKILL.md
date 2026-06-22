---
name: kk-ui-polish-review
description: |
  KK Dev Skeleton UI polish review 技能。适用于前端、HTML、dashboard、可视化或可点击原型实现后，
  检查页面是否符合 UI design brief、产品 archetype、信息层级、组件状态、响应式和视觉质量门槛。
---

# UI Polish Review

## Purpose

在功能验收前先检查 UI 质量，防止“功能可用但视觉粗糙、像 AI 默认模板、信息层级混乱”的页面进入完成状态。

## When To Use

- 实现了用户可见页面或 HTML。
- 修改了页面布局、导航、筛选、表格、表单、状态或空态。
- 用户对 UI 审美提出不满，或本任务来自“进行 UI 优化 / 优化界面 / 美化页面 / 提升视觉”等短句请求。
- QA 前需要判断是否可以进入交互验收。

## Required Reading

1. `.gstack/knowledge/ui-patterns.md`
2. `.gstack/knowledge/visual-quality-bar.md`
3. `.gstack/templates/ui-polish-review.template.md`
4. 本任务 UI design brief
5. active task boundary
6. 相关 frontend spec / requirement

## Workflow

1. 找到本任务的 UI design brief；没有则先回到 `kk-ui-design-kickoff`。
2. 实际打开页面或产物；如果无法打开，review 结论只能是 `blocked` 或 `partial`。
3. 按 `visual-quality-bar.md` 检查：
   - archetype-fit
   - information-hierarchy
   - layout-density
   - component-fit
   - state-completeness
   - visual-consistency
   - responsive-safety
   - accessibility-basics
   - anti-ai-slop
4. 记录必须修复项和可延后项。
5. 如果 P0 问题存在，不允许把 UI 任务标记完成。
6. review evidence 默认落 `.gstack/reviews/`；如已存在任务 review，可补 `UI Polish Review` 小节。
7. 之后仍需执行 Browser / Chrome / Playwright 交互 QA，并把结果写入 `.gstack/qa-reports/`。

## Output Rules

- 先列问题，不要只给主观评价。
- 评价必须绑定具体 viewport、页面区域、组件或状态。
- 对 UI 优化短句任务，review 结论必须说明设计 brief、实现结果和浏览器验收之间是否闭环。
- 不要把“看起来还行”当成 pass；必须逐项检查 checklist。
- 不要用截图外观替代控件可操作验证；polish review 之后仍要做交互 QA。
