# Visual Quality Bar

本文件定义 KK Dev Skeleton 的 UI 审美能力门槛。它适用于前端、HTML、dashboard、可视化和用户可见交互任务。

目标不是让每个页面都“花哨”，而是让 Codex 在写 UI 前能判断合适的产品类型和视觉语言，避免产出粗糙、模板化、信息层级混乱的初版界面。

## UI Quality Gate

涉及以下任一场景时，必须触发 UI quality gate：

- 新增或重做前端页面、HTML、dashboard、可视化或可点击原型。
- 修改页面主结构、导航、筛选、表格、表单、流程、状态或空态。
- 用户反馈“难看、不高级、不专业、像 demo、像模板、页面乱、看不懂”。
- 新项目 MVP 需要给用户第一眼建立信任。

Gate 默认顺序：

1. `ui-style-routing`
2. `ui-design-brief`
3. implementation
4. `ui-polish-review`
5. interaction QA

## UI Archetype Router

Codex 必须先判断页面类型，再选视觉语言。

| Archetype | 适用场景 | 默认视觉方向 | 避免 |
| --- | --- | --- | --- |
| `saas-workbench` | 高频业务工具、运营后台、AI 开发平台、CRM、内部系统 | 克制、清晰、高密度、可扫描 | 大 hero、装饰渐变、低密度卡片墙 |
| `analytics-dashboard` | 指标看板、经营分析、数据追踪 | 指标层级清楚、图表克制、筛选强 | 图表堆砌、颜色过多、指标无解释 |
| `workflow-console` | 任务流、审批流、自动化执行链 | 状态机、timeline、queue、detail split | 单页堆所有信息、状态不明确 |
| `ai-command-center` | AI 对话、任务领取、runner 状态、确认队列 | chat + workbench 混合、状态透明 | 只有聊天框、缺少任务上下文 |
| `marketing-site` | 官网、产品介绍、转化页 | 第一屏强品牌信号、真实产品图、明确 CTA | 管理后台式密集表格 |
| `content-product` | 文档、知识库、课程、文章 | 阅读节奏、目录、内容卡片 | dashboard 化 |
| `game-or-playful` | 游戏、玩具、儿童向 | 视觉表现强、动效和图形可更丰富 | 企业 SaaS 风 |

AI 软件工厂、开发者平台、业务工作台和内部工具，默认使用 `saas-workbench`、`workflow-console` 或 `ai-command-center`，除非 requirement 明确要求营销官网。

## Design Brief 必填项

实现前的 UI design brief 至少包含：

- 目标用户和使用频率。
- 页面 archetype。
- 用户第一眼必须理解什么。
- 信息架构：导航、主区域、辅助区域、详情区、状态区。
- 主流程：用户如何开始、执行、确认、完成。
- 组件选择：tabs、segmented controls、filters、table、form、timeline、kanban、chat、empty state、drawer、modal 等。
- 视觉方向：字体层级、间距密度、色彩角色、图标策略、边框 / 阴影使用。
- 状态覆盖：loading、empty、error、disabled、selected、success、warning、permission。
- 响应式策略：桌面、窄屏、移动端的布局变化。
- 明确不采用的风格。

## Visual Quality Checklist

UI polish review 至少检查：

- `archetype-fit`：页面视觉语言是否匹配产品类型。
- `information-hierarchy`：标题、指标、表格、详情、操作是否有清楚主次。
- `layout-density`：密度是否适合使用频率；高频工具不能过度空洞，营销页不能像后台。
- `component-fit`：是否用合适控件承接行为，不用无意义卡片替代表格 / 表单 / tabs。
- `state-completeness`：loading、empty、error、disabled、selected、success、warning 是否完整。
- `visual-consistency`：颜色、字号、间距、边框、圆角、阴影是否统一。
- `responsive-safety`：小屏不溢出、不重叠、不遮挡关键操作。
- `accessibility-basics`：文字对比、按钮尺寸、焦点、标签和图标含义可理解。
- `anti-ai-slop`：避免大面积紫蓝渐变、装饰 orb、卡片套卡片、假数据堆叠、无意义宣传文案、风格混搭。

## 默认设计约束

- 卡片半径保持克制，除非项目设计系统另有要求。
- 工具按钮优先使用图标和 tooltip；不把常见工具动作写成冗长文字按钮。
- 表格、筛选、tabs、segmented controls、empty state 和错误提示要完整。
- 不使用单一色相铺满全页面；主色、语义色、中性色分工清楚。
- 不用 SVG / 渐变插画假装产品图；需要展示产品时优先展示真实页面状态或可生成的具体预览。
- 不在页面里写“这是一个现代化、高级、好看的界面”这类自述。

## 完成定义

UI 任务完成前，必须能回答：

- 为什么选这个 archetype？
- 用户第一眼看懂什么？
- 主要操作路径是否清楚？
- 哪些状态被覆盖？
- 桌面和移动端是否不会溢出 / 重叠？
- 有没有视觉残余风险？
- QA evidence 里是否记录了实际打开和操作页面的结果，或明确 blocked / partial？
