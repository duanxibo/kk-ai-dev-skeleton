---
name: kk-ui-design-kickoff
description: |
  KK Dev Skeleton UI 设计开工技能。适用于前端页面、HTML、dashboard、可视化、AI 工具界面、用户反馈“进行 UI 优化 / 优化界面 / 美化页面 /
  提升视觉 / 界面难看 / 不专业 / 像模板”，或任何需要在实现前判断 UI 风格、信息架构和视觉质量门槛的任务。
---

# UI Design Kickoff

## Purpose

让 Codex 在写前端代码前先做产品类型和视觉语言判断，避免“功能能用但第一版很丑”。

本技能不是生成装饰风格，也不是替代产品 requirement。它负责把 UI 需求翻译成可实现、可验收的设计 brief。

## When To Use

只要出现以下任一信号，必须使用：

- 新增或重做页面、HTML、dashboard、可视化、可点击原型。
- 修改页面主结构、导航、筛选、表格、表单、任务流、状态或空态。
- 用户只说“进行 UI 优化 / 优化界面 / 美化页面 / 提升视觉 / 页面不好看”。
- 用户说“界面难看 / 不够好看 / 不高级 / 不专业 / 像 demo / 像模板 / 页面乱 / 看不懂”。
- 新项目 MVP 需要建立第一眼信任感。

通常不需要使用：

- 纯后端、纯脚本、纯数据查询。
- 只改不可见 bug 且不影响页面结构或状态。

## Required Reading

1. `.gstack/knowledge/ui-patterns.md`
2. `.gstack/knowledge/visual-quality-bar.md`
3. `.gstack/templates/ui-design-brief.template.md`
4. active task boundary
5. 当前项目 adapter 指向的 product / frontend spec；若没有，先在 requirement / review 中写清 no-spec-change 原因

## Workflow

1. 确认当前任务是否已有 active boundary；没有则回到 `kk-task-kickoff`。
2. 判断 UI archetype：
   - `saas-workbench`
   - `analytics-dashboard`
   - `workflow-console`
   - `ai-command-center`
   - `marketing-site`
   - `content-product`
   - `game-or-playful`
   - `other`
3. 生成或补齐 UI design brief，默认落到 `.gstack/designs/` 或当前 requirement / review 的 UI section。
4. 写清：
   - 用户第一眼必须理解什么
   - 信息架构
   - 主流程
   - 组件计划
   - 视觉方向
   - 状态覆盖
   - 响应式策略
   - 明确不采用的风格
5. 更新 active boundary：
   - `Required Gates` 增加或确认 `ui-design-quality`
   - `Generated Artifact Policy` 写清验收 URL / 刷新方式
   - `Verification` 写入 UI polish review 和浏览器交互 QA
6. 如果用户要求的是 SaaS / dashboard / 工作台 / AI 工具，默认克制高密度，不做营销页式 hero。
7. 如果存在多个合理设计方向，只给用户 2-3 个业务 / 视觉选择；工程细节由 Codex 在 boundary 内决定。

## Output Rules

- 不要只说“我会美化 UI”，必须产出设计判断。
- 不要要求用户手动说出本技能名；短句 UI 优化请求也应自动进入设计、实现、复核和浏览器验收链路。
- 不要在没有 UI design brief 的情况下直接实现复杂页面。
- 不要把页面类型判断留在聊天里；长期任务要写入 repo-native evidence。
- 不要把 visual polish review 当成 QA 的替代；它是 QA 前的视觉质量门禁。
