# UI Patterns

本文件记录 KK Dev Skeleton 可复用的 UI 工作规则。项目专属设计系统、品牌色、业务术语和页面路径应放进 adapter 或项目自己的 specs。

## UI-001 - UI 任务先做风格路由

- tags: `frontend`, `ui-quality`, `design-gate`
- rule:
  只要任务涉及前端页面、HTML、dashboard、可视化、交互控件或用户明确反馈“界面难看 / 不专业 / 像模板”，进入实现前先触发 `kk-ui-design-kickoff`。Codex 必须先判断页面类型、用户使用频率、信息密度、主流程、组件结构、视觉风格和不适合的风格，再写代码。

## UI-002 - SaaS / 工具类默认克制高密度

- tags: `frontend`, `saas`, `dashboard`, `workbench`
- rule:
  SaaS 工作台、运营后台、AI 工具、CRM、内部系统和开发平台类界面，默认按成熟工作台处理：克制色彩、清晰导航、紧凑但有呼吸感的信息层级、表格 / tabs / filters / segmented controls / status badges / empty states 完整，不做营销页式大 hero、装饰渐变、卡片套卡片或低信息密度海报布局。

## UI-003 - 视觉质量门禁不是装饰美化

- tags: `frontend`, `visual-review`, `qa`
- rule:
  UI polish review 检查的是产品类型匹配、布局结构、信息层级、组件状态、响应式、可读性、可访问性和视觉一致性，不是最后补阴影、圆角、渐变。若页面功能可用但显著粗糙、拥挤、模板化、文字溢出、状态缺失或风格不符合用户场景，不能把 UI 任务标记完成。

## UI-004 - 用户可见能力按页面理解

- tags: `frontend`, `nontechnical`, `interaction`, `acceptance`
- rule:
  非技术用户说“筛选、排序、搜索、操作入口、看不到页面变化、把功能做得更好用”时，默认先按用户可见页面能力理解。若本轮只做生成命令、CLI 参数、后端接口或静态输出，必须在 requirement 中写明不会产生页面内变化，并向用户解释验收方式。

## UI-005 - 生成 HTML 必须声明刷新路径

- tags: `frontend`, `html`, `generated-artifact`, `dashboard`
- rule:
  静态生成 HTML 不是自动刷新的应用页面。boundary 必须写明最新文件路径、验收 URL、重新生成命令和“看不到变化”的排查路径；用户打开旧 `/tmp` 文件时不能把任务判定为 UI 未生效或已完成。

## UI-006 - UI polish review 必须留 evidence

- tags: `frontend`, `ui-quality`, `review`, `qa`
- rule:
  涉及 UI 的正式任务必须在 review、QA 或 boundary 中记录 visual polish review 结论。至少说明采用的 UI archetype、设计参考方向、主要组件、状态覆盖、桌面 / 移动适配、残余视觉风险和是否需要继续迭代。
