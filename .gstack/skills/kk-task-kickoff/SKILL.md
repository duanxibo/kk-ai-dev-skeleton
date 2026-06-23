---
name: kk-task-kickoff
description: |
  启动 KK Dev Skeleton 新任务时使用。它负责先读仓库入口、判断任务所在 stack domain、确认当前真源、
  判断 Required Gates、创建或更新 active task boundary，并明确 Spec Sync Plan。适用于正式实现、跨层任务、
  需求冻结前梳理、bug 修复前定边界，以及任何“不想再手动复制 AI 开工提示词”的场景。
  即便用户没有显式写出 skill 名，只要是在描述一个新任务、bug、正式实现或跨层需求，
  也应默认把它视为一次隐式的 task kickoff。
---

# Task Kickoff

## Overview

这个 skill 用来替代 `.gstack/templates/ai-task-kickoff.template.md` 的手动复制流程。

它的目标不是直接开始写代码，而是先把一次 KK Dev Skeleton 任务启动成“有上下文、有边界、有真源路由”的协作状态。

它是新任务总入口、调度器和 active boundary owner。数据相关任务不是绕过本 skill 直接进入实现，而是由本 skill 在 boundary 中声明 `data-access` gate 后，再调度 `kk-data-kickoff` 执行数据专项。

它也是 `prototype-logic-extraction` Required Gate owner。凡是后端接口、读模型、service 或 snapshot 承接已有前端 / 原型 / mock 的业务逻辑，必须由本 skill 在 active boundary 中声明该 gate，`required_before: plan-eng-review`；`kk-data-kickoff` 只在数据任务中协助发现，不拥有该 gate。

## When To Use

在这些场景优先使用：

- 新任务刚开始，还没判断属于哪个 `stack` domain，或是否只是 `.gstack` 协作治理
- 任务即将进入正式实现，需要先补或更新 task boundary
- 任务跨层，担心 AI 一上来就全仓搜索或误读 `archive/`
- 你不想每次都手动复制“先读什么文档”的开工 prompt

这些场景即便用户没有显式提到 `$kk-task-kickoff`，也默认应触发：

- 用户直接描述一个新需求或新 bug
- 用户要求开始正式实现、重构、联调、补测试
- 用户提出一个可能涉及多人协作、跨 domain 影响或长期文档同步的任务

这些场景通常不需要使用：

- 单文件极小修，且已有明确 active boundary
- 只是问一个不需要落文档的局部问题

## Required Inputs

用户至少需要给出：

- 本次任务目标
- 预期改动路径或相关模块；如果用户不懂技术，可以只给业务目标、使用者和期望结果

如果用户没给全，先根据仓库入口文档补足上下文。非技术用户只描述业务目标时，优先使用 `../../templates/nontechnical-task-intake.template.md` 的问题结构，把用户语言转成 requirement / review / boundary 输入；只有会改变产品结果、真实数据风险、生产风险、DB schema 或 git action 的问题才追问用户，不要跳过 boundary。

## Workflow

1. 先读仓库固定入口：
   `AGENTS.md`、`.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`、`.gstack/README.md`、`.gstack/knowledge/CODEMAP.md`、`.gstack/knowledge/doc-placement.md`、`.gstack/task-boundaries/CURRENT.md`
2. 根据任务类型补读角色入口和相关知识：
   产品任务读 `.gstack/entrypoints/product-manager.md`；工程任务读 `.gstack/entrypoints/engineer.md`；实现前补读 `.gstack/knowledge/implementation-guide.md` 和相关 knowledge/specs/pitfalls。
   前端、HTML、dashboard、可视化，或用户反馈“进行 UI 优化 / 优化界面 / 美化页面 / 提升视觉 / 界面难看 / 不专业 / 像模板”时，还必须补读 `.gstack/knowledge/ui-patterns.md`、`.gstack/knowledge/visual-quality-bar.md`，并调度 `kk-ui-design-kickoff`。
3. 识别 Codex 协作模式：
   - 如果用户明确说“自主执行 / 全自动做完 / 关键确认 / 关键地方问我 / 手动控制 / 先别改代码”等，先按 `kk-codex-mode` 解释并记录本次模式。
   - 如果没有明确指定，运行或参考 `python3 .gstack/scripts/codex_mode.py show --format json`；没有本机默认时使用 `自主执行`。
   - 模式只决定是否暂停确认，不替代固定研发流、Required Gates 或 git 授权规则。
4. 判断 Flow Lane：
   - `fast-lane`：小需求、明确 bugfix、局部改动、无业务口径多解、可本地验证，不涉及生产 / DB schema / git action。
   - `standard`：普通正式开发，需求明确但影响面不小，或涉及多模块、接口、数据、前后端联动。
   - `discovery`：大需求、产品方向不清、存在多个合理方案或需要用户磨合；先 office-hours / plan review，冻结后再转入 standard / fast-lane。
   - 在 `手动控制` 下，默认不进入实现；除非用户明确授权，只输出分析或创建不落长期文档的临时方案。
5. 如果用户是非技术表达或没有给出改动路径：
   - 使用 `nontechnical-task-intake` 结构识别目标用户、成功样子、数据来源、不做什么和风险确认。
   - 显式区分本轮改动表面：生成命令 / CLI 参数 / 后端接口 / 页面内交互控件 / 用户可见 UI 变化 / 静态输出 / 文档。
   - 用户出现“筛选、排序、搜索、操作入口、看不到页面变化”等词时，默认按页面内可见能力理解；如果只做 CLI、生成器参数、后端接口或静态输出，必须在 requirement 中写明原因并在用户侧解释。
   - Codex 自行推断 stack domain、Expected Spec Targets、Required Gates 和验证计划。
   - 若可本地证明，直接生成 repo-native evidence；若涉及业务口径多解、真实数据、生产、DB 或 git action，再提示用户确认。
   - 用户已对低风险范围回复“同意 / 可以 / 我确认 / 继续做”时，继续在 active boundary 内推进本地可证明的实现、验证、文档同步、门禁恢复和 subagent 分工；不要把每个内部阶段都交回用户说“继续”。
6. 用自己的话确认：
   - 当前任务属于哪一层
   - 当前主要真源文档是什么
   - active boundary 是否足够
   - 当前 Flow Lane 是什么以及为什么
   - 是否需要 `data-access`、`data-query`、`prototype-logic-extraction`、`data-knowledge-sync`、`doc-backfill` 等 Required Gates
   - 是否需要 `ui-design-quality` gate；凡涉及前端 / HTML / dashboard / 可视化，或用户反馈 UI 质量问题，默认需要
   - 后续可能涉及哪些文档同步
7. 如果任务进入正式实现或长期协作主线：
   必须创建或更新 `.gstack/task-boundaries/` 下的 boundary，并自动设置本地 active boundary
8. 在 boundary 中至少写清楚：
   `Goal`、`Allowed Files`、`Forbidden Files`、`Functional Non-goals`、`User-visible Acceptance`、`Generated Artifact Policy`、`Decision Mode`、`Flow Lane`、`Autonomy Plan`、`Subagent Plan`、`GStack Required Flow`、`Required Gates`、`Required Knowledge`、`Spec Sync Plan`、`Verification`
   - HTML / 前端 / 可视化任务必须在 `Generated Artifact Policy` 写明验收 URL、刷新 / 重新生成方式，以及“看不到变化”的排查路径。
   - 静态生成文件必须写清它不会自动刷新；重新生成后要刷新浏览器或重新打开最新文件。
9. 如果任务会进入正式开发，`GStack Required Flow` 必须按顺序声明：
   `requirement-brief -> plan-ceo-review -> requirement-freeze/prototype-freeze -> plan-eng-review -> domain-spec-readiness -> implement -> qa/qa-only`
   开发前前五项必须是 `done` 且有 repo-native evidence；push 前 `implement` 与 `qa` 也必须是 `done`。
10. `fast-lane` evidence 使用：
   - `.gstack/templates/fast-lane-requirement.template.md`，产物落 `.gstack/requirements/`，可同时作为 `requirement-brief` 与 `requirement-freeze` evidence。
   - `.gstack/templates/fast-lane-review.template.md`，产物落 `.gstack/reviews/`，可同时作为 `plan-ceo-review` 与 `plan-eng-review` evidence。
   - QA 仍必须落 `.gstack/qa-reports/`。
   - fast-lane 不能省略“用户期望的可见变化是什么”；如果本轮没有页面变化，必须写清为什么没有以及如何验收。
   - Codex 已读上下文并确认 fast-lane 前提成立时，可用 `python3 .gstack/scripts/autopilot_bootstrap.py --topic <topic> --goal <goal> --ai-reviewed --activate` 生成起始 evidence 包；不带 `--ai-reviewed` 时只是 draft scaffold，不能冒充已 review。
11. `requirement-brief` 默认落 `.gstack/requirements/`；它是 `plan-ceo-review` 的输入，不要只留在聊天里。
12. `requirement-freeze` 或 `prototype-freeze` 是 CEO review 后、工程 review 前的冻结证据；`domain-spec-readiness` 必须引用它，而不是临时重写需求。
13. 如果任务涉及 adapter 标记为 prototype / baseline / archive 的旧原型路径，boundary 必须写清目标真源、采纳 / 放弃项和为什么需要触碰历史原型路径；不要新增 handoff 文档作为默认门禁。
14. 如果任务涉及 adapter 标记为 backend implementation 的路径，`Spec Sync Plan` 必须指向 adapter 定义的项目真源文档，`Verification` 必须列出后端测试或等价契约测试；不要把新后端规范写入 adapter 标记为 deprecated 的旧目录。
15. 每个正式任务都必须填写 `Subagent Plan`；小任务写 `Mode: not-used` 和原因，复杂任务先用 `kk-subagent-orchestrator` 拆分探索、评审、执行或治理 agent。是否使用 subagent、使用什么 role、读哪些文件、checkpoint / deadline 和回收方式由 Codex 判断，不让用户替 Codex 做工程分工。用户反馈“没看到使用 subagent / 需要用户说继续太频繁”时，默认把这视为协作体验缺口，至少规划 read-only reviewer / explorer，除非 active boundary 证明不适合。
16. 每个正式任务都必须在 `Autonomy Plan` 中填写 `Goal Mode: enabled / not-used / ask-first`；中大型 `自主执行` 任务可自动启用，`手动控制` 默认不启用。
17. 如果任务出现以下任一信号，必须在 `Required Gates` 中声明 `data-access`，并调度 `kk-data-kickoff` 产出 gate evidence：
   - 页面、原型、看板接真实数据
   - 前端 mock 替换后端接口
   - 新增或调整后端接口输入、输出、事实源或 scope
   - 涉及 relational database、analytics warehouse、BI、SQL、字段口径或查询结果
   - 受限业务模块、计划系统、项目工作台之间复用数据
   - 需要判断数据源是否存在、是否满足需求、是否要写 SQL draft 或 requirement gap
18. 如果任务出现以下任一信号，必须在 `Required Gates` 中声明 `prototype-logic-extraction`，由本 skill 作为 owner 写入 boundary：
   - 后端接口、读模型、service 或 snapshot 用于替换前端 mock / fixture
   - 后端接口字段来自已有页面展示字段、原型字段或前端 mock 结构
   - 目标页面已有 helper、computed、selector、formatter、聚合函数、派生字段、状态流转或业务校验
   - 任务从 `archive/baseline/` 原型迁移到 `stack/` 正式实现
   - diff 同时涉及 frontend 和 backend，且不是纯展示、文案、样式或请求地址修复
   - 用户描述包含“把页面接后端”“按原型补接口”“把 demo 做成服务”“前端 mock 替换真实接口”“读模型承接页面逻辑”等意图
19. `prototype-logic-extraction` 的 boundary 条目必须写 `owner: kk-task-kickoff`、`required_before: plan-eng-review`。状态为 `not-required` 时必须写清排除原因；状态为 `deferred` 时必须写清批准来源、延期原因、风险、删除条件或后续补齐路径。
20. 该 gate 的 evidence 默认使用 `../../templates/prototype-logic-extraction.template.md` 或模块内等价真源，至少包括代码证据、逻辑归属表、golden parity 真源和前端残留逻辑检查。
21. 如果任务预计新增或调整后端 API、DTO、migration、读模型、snapshot、projection、relational database 表、Entity、Mapper、Repository、DAO、MyBatis XML 或对外数据产品，必须在 `Required Gates` 中声明 `data-knowledge-sync`：
   - `owner: kk-doc-sync`
   - `required_before: review`
   - 默认状态：实现前为 `planned`，不涉及新增表 / 接口时为 `not-required`
   - done criteria：新增表已有 source doc + registry；新增接口已有 stack domain spec / interface doc；文档已标注生命周期状态、证据等级和待确认项。
22. `data-knowledge-sync` 不替代实现前 `data-access` gate。`data-access` 判断能否进入实现；`data-knowledge-sync` 判断实现后新增的表、接口和读模型知识是否回写。
23. 如果后续门禁失败，先执行 Gate Recovery：
   - 优先运行 `python3 .gstack/scripts/gstack_doctor.py check` 判断 active boundary、skills、hooks 和本地脚本是否正常。
   - 读取失败输出。
   - 自行补齐可由本地证据证明的 boundary、flow、review、QA、spec sync 或 gate evidence。
   - 必要时按 `.gstack/templates/gate-recovery-report.template.md` 落 gate recovery 报告。
   - 只有业务口径、真实数据权限、生产 / DB / git action 或无法本地证明时才提示用户。

24. UI 质量门禁：
   - 凡涉及前端页面、HTML、dashboard、可视化、可点击原型、导航、筛选、表格、表单、状态、空态，或用户反馈“界面难看 / 不够好看 / 不高级 / 不专业 / 像模板”，必须在 `Required Gates` 中声明 `ui-design-quality`。
   - `ui-design-quality` 默认 owner 为 `kk-ui-design-kickoff`，required_before 为 `implement`；实现后、交互 QA 前使用 `kk-ui-polish-review`。
   - 该 gate 的 evidence 默认使用 `.gstack/templates/ui-design-brief.template.md` 和 `.gstack/templates/ui-polish-review.template.md`，至少包括 UI archetype、信息架构、组件计划、视觉方向、状态覆盖、响应式策略、明确不采用的风格和 polish review 结论。
   - 对 SaaS / dashboard / 工作台 / AI 工具类页面，默认采用克制、高密度、可扫描的产品界面，不做营销页式大 hero、装饰渐变、卡片套卡片或低信息密度布局。

25. QA 对用户可见 UI / HTML / 可视化任务的硬要求：
   - 不得只用 `rg`、JSON、HTML 字符串或截图外观替代交互验收。
   - 必须用 Browser / Chrome / Playwright 操作页面；若 `file://` 或权限策略阻断，改用本地 HTTP server 打开同一页面继续验收。
   - 仍无法验收时只能把 QA 结论标成 `blocked` 或 `partial`，不能标 `done`。
   - QA 报告必须区分结构存在、控件可见、控件可操作、状态变化正确、空态正确、刷新 / 重新生成说明清晰。
   - 如果用户指出上一份 QA 漏验，必须创建 superseding QA 或修正原 QA 结论，不能保留误导性的 done。

## Output Rules

- 默认应该直接落 boundary 文档，而不是只给聊天建议
- 如果用户只是直接描述任务，而没有显式调用 skill，默认按“隐式 kickoff”处理
- 如果已有 boundary 足够且无需更新，可以不新建；但必须明确说明原因
- 只要创建或切换了具体 boundary，默认应自动调用仓库脚本设置本地 active boundary；不要把这个步骤甩给用户
- 不要在没有证据时声称“已完成实现”或“已通过 QA”
- 不要把“这次可能要补哪些文档”只留在口头总结里，至少写进 boundary 的 `Spec Sync Plan`
- 不要把“这次采用什么协作模式、Codex 可以自动做什么、哪些点必须问用户”只留在口头总结里，必须写进 boundary 的 `Decision Mode` 和 `Autonomy Plan`
- 不要把 Flow Lane 只留在口头判断里，必须写进 boundary；fast-lane 必须有 fast-lane requirement 和 fast-lane review evidence
- 不要把“这次是否使用 subagent”只留在口头判断里，必须写进 boundary 的 `Subagent Plan`
- 不要把“是否继续下一步、测试怎么跑、门禁怎么恢复、subagent 怎么分工”作为低风险任务的反复确认点；这些属于 Codex 在 boundary 内的自主推进事项
- 不要把“这次是否需要 data-access / data-query / prototype-logic-extraction / data-knowledge-sync / doc-backfill”只留在口头判断里，必须写进 boundary 的 `Required Gates`
- 不要把“这次是否需要 UI design gate / polish review”只留在口头判断里；涉及前端、HTML、dashboard 或可视化时，必须写进 boundary 的 `Required Gates`、`Generated Artifact Policy` 和 `Verification`
- 如果 `prototype-logic-extraction` 被标记为 `planned / done / blocked / deferred`，必须填写 `evidence_path` 或阻塞 / 延期说明；如果标记为 `not-required`，必须填写明确排除原因
- 如果用户显式点名 `kk-data-kickoff` 但还没有 active boundary，先回到本 skill 创建或补齐 boundary，再执行数据专项
- 不要跳过 `requirement-brief`、`plan-ceo-review`、`requirement-freeze/prototype-freeze`、`plan-eng-review`、`domain-spec-readiness`、开发、`qa/qa-only` 这条固定链路；如果确实是非业务流程维护任务，必须在 boundary 里说明 `not-required` 原因

## Template Source

这个 skill 以仓库模板为真源：

- 主模板：`../../templates/ai-task-kickoff.template.md`
- 使用说明：读取 [references/workflow.md](references/workflow.md)
- 输出检查清单：读取 [references/boundary-checklist.md](references/boundary-checklist.md)
