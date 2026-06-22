# KK Skills 使用说明

公开可复用 skills 使用 `kk-` 命名空间：

- `kk-natural-language-dev`
- `kk-task-kickoff`
- `kk-codex-mode`
- `kk-doc-sync`
- `kk-doc-lifecycle`
- `kk-doc-backfill`
- `kk-data-kickoff`
- `kk-data-query`
- `kk-subagent-orchestrator`
- `kk-ui-design-kickoff`
- `kk-ui-polish-review`

项目专属行为应放进 adapters，不要通过新的 skill 前缀写进框架核心。

## UI 质量能力

- `kk-ui-design-kickoff`
  前端、HTML、dashboard、可视化或用户反馈“界面难看 / 不专业 / 像模板”时使用。它负责先判断 UI archetype、信息架构、组件计划、视觉方向、状态覆盖和响应式策略，再进入实现。
- `kk-ui-polish-review`
  页面实现后、交互 QA 前使用。它检查 archetype fit、信息层级、密度、组件匹配、状态完整、响应式安全、可访问性和 anti-AI-slop，防止功能可用但视觉粗糙的页面进入完成状态。
