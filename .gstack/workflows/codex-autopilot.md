# Codex 协作模式与自动推进策略

本文件定义 KK Dev Skeleton 中 Codex 的默认协作模式、用户选择方式、门禁恢复策略和高风险升级边界。

核心原则：

- 模式只决定 Codex 什么时候停下来问用户，不决定是否遵守门禁。
- 所有模式都必须遵守 task boundary、Required Gates、spec sync、QA、经验回写和 git 授权约束。
- Codex 被门禁卡住时，先自行补齐可由本地证据证明的内容；只有本身无法补齐时才提示用户。
- 自动生成采用“AI 负责语义判断，脚本负责确定性骨架”的分工；脚本不得单独伪造需求已确认、review 已通过或 QA 已通过。

面向非技术用户时，默认先把用户自然语言整理成 `.gstack/templates/nontechnical-task-intake.template.md` 的业务输入，再由 Codex 转译为 requirement、review、boundary、Required Gates 和 QA 计划。用户不需要知道 `boundary`、`Spec Sync Plan` 或测试命令。

自然语言可用性需求的默认解释：

- 用户说“筛选、排序、搜索、操作入口、看不到页面变化、把页面做得更好用”时，Codex 默认按用户可见页面能力理解。
- Codex 必须在 requirement / review / boundary 中显式区分生成命令、CLI 参数、后端接口、页面内交互控件、用户可见 UI 变化和静态输出。
- 如果本轮只做 CLI、生成器参数、后端接口或静态文件，不会产生页面内可见变化，必须在 requirement 中写明，并用人话告诉用户怎么验收。
- fast-lane 可以小步快跑，但不能省略“用户期望的可见变化是什么”。

## 自动生成职责分工

Codex Autopilot 不是纯脚本流水线。

- AI 负责：读入口文档、判断需求是否明确、拆解任务、识别风险、决定 Flow Lane、写 review 结论、执行实现、运行验证、总结残余风险。
- 脚本负责：生成稳定路径、模板字段、active boundary 指针、重复门禁结构和基础一致性校验。
- guard 负责：检查 evidence 是否存在、boundary 结构是否完整、spec sync 是否遗漏、后端改动是否带测试和 domain spec。

纯脚本生成的内容只能作为 draft 或 scaffold；只有 Codex 已读上下文并明确完成语义复核后，才允许把 fast-lane requirement / review / gates 标记为 `done`、`pass` 或 `not-required`。

门禁要求：

- fast-lane 的 `requirement-brief`、`requirement-freeze`、`plan-ceo-review`、`plan-eng-review` evidence 必须写明 `AI 语义复核: yes`。
- fast-lane 的 requirement 必须写明用户可见变化拆解；UI / HTML / 可视化任务还必须有 `User-visible Acceptance` 和 `Generated Artifact Policy`。
- `draft-needs-codex-review`、`AI 语义复核: no`、模板占位 `yes / no` 或 boundary 中的 `pending-review` 都不能满足进入实现前门禁。
- `team_flow_guard.py` 负责在正式实现链路中阻断，`spec_sync_guard.py` 负责在收口检查时再次发现。
- 对声明用户可见 UI / HTML 交互的 active boundary，guard 只做轻量结构检查：QA done evidence 必须包含 Browser / Chrome / Playwright / 本地 HTTP server 交互证据，或明确 blocked / partial reason。避免对历史任务一次性 hard fail。

## 三档模式

| 中文模式 | 内部枚举 | 适用用户 / 场景 | Codex 行为 |
| --- | --- | --- | --- |
| 自主执行 | `codex-led` | 用户主要依赖 Codex 推荐方案和执行；需求明确的小改、bugfix、本地可验证任务 | Codex 自动拆解、开发、测试、补文档、修门禁、本地重启，只有高风险点问用户 |
| 关键确认 | `checkpoint` | 用户有技术背景，希望参与关键决策 | Codex 自动准备和推进，但在产品口径、架构取舍、数据模型、接口契约、大范围改动前暂停确认 |
| 手动控制 | `manual` | 用户只想先讨论方案、审查风险或亲自控制实现节奏 | Codex 只分析和建议；没有用户明确授权，不改代码、不落长期文档 |

默认模式：`自主执行`。

## 用户选择方式

用户不需要记英文枚举。推荐用中文自然表达：

```text
这次自主执行
这次全自动做完
切到自主执行模式

这次关键确认
关键地方问我
实现前让我确认

这次手动控制
先别改代码
只给方案
```

如果用户主动唤起“协作模式”但没有给出参数，Codex 应提示三选一：

```text
请选择协作模式：
1. 自主执行：你说目标，Codex 做完。
2. 关键确认：Codex 推进，关键点问你。
3. 手动控制：Codex 只分析，你授权才动。
```

如果当前环境支持交互式选项，使用这三个中文选项作为按钮或参数；否则在聊天里要求用户回复模式名或序号。

本机默认模式可用 helper 管理：

```bash
python3 .gstack/scripts/codex_mode.py show
python3 .gstack/scripts/codex_mode.py choices
python3 .gstack/scripts/codex_mode.py set 自主执行
python3 .gstack/scripts/codex_mode.py set 关键确认
python3 .gstack/scripts/codex_mode.py set 手动控制
python3 .gstack/scripts/codex_mode.py clear
```

## 作用范围

- 用户说“这次”：只覆盖当前任务。
- 用户说“以后默认 / 默认用 / 切换到”：写入本机 `.gstack/codex-mode.local.md`。
- `.gstack/codex-mode.local.md` 是 gitignored 本机偏好，不提交到 repo。
- 每个正式任务的具体 boundary 应记录本次实际模式：
  - `Decision Mode: 自主执行 / 关键确认 / 手动控制`
  - `Autonomy Plan: 本轮 Codex 可自动做什么、哪些点必须问用户`

## 与任务流程的关系

`kk-codex-mode` 只决定用户介入程度。正式任务仍由 `kk-task-kickoff` 维护 active boundary 和 Required Gates。

推荐顺序：

1. 识别用户是否指定协作模式。
2. 如果用户只是切换模式，使用 `kk-codex-mode` 完成设置并停止。
3. 如果用户同时给出任务目标和模式，先记录模式，再进入 `kk-task-kickoff`。
4. `kk-task-kickoff` 根据模式决定是否在需求澄清、plan review、实现前或高风险点暂停确认。

## Flow Lane 分流

`kk-task-kickoff` 应在创建 boundary 时声明本轮 `Flow Lane`：

| Flow Lane | 适用场景 | Evidence 要求 |
| --- | --- | --- |
| `fast-lane` | 小需求、明确 bugfix、局部改动、无业务口径多解、可本地验证 | `fast-lane-requirement` + `fast-lane-review` + boundary + QA |
| `standard` | 普通正式开发，需求明确但影响面不小或涉及多模块协作 | 完整 requirement -> review -> freeze -> eng review -> domain spec readiness -> QA |
| `discovery` | 大需求、产品方向不清、存在多个合理方案、需要用户磨合 | office-hours / plan review 先澄清；冻结后再转入 standard 或 fast-lane |

小需求和明确改动在 `自主执行` 下不需要多轮确认，但仍应自动产出最小 requirement / boundary / QA / spec sync evidence。

fast-lane 推荐 evidence：

- `.gstack/requirements/YYYY-MM-DD_<topic>-fast-lane-requirement.md`
  使用 [../templates/fast-lane-requirement.template.md](../templates/fast-lane-requirement.template.md)，同时满足 `requirement-brief` 和 `requirement-freeze`。
- `.gstack/reviews/YYYY-MM-DD_<topic>-fast-lane-review.md`
  使用 [../templates/fast-lane-review.template.md](../templates/fast-lane-review.template.md)，同时满足 `plan-ceo-review` 和 `plan-eng-review` 的轻量 evidence。
- `.gstack/qa-reports/YYYY-MM-DD_<topic>-qa.md`
  使用 [../templates/qa-report.template.md](../templates/qa-report.template.md)，记录实际验证。

Codex 已经读完上下文并确认 fast-lane 前提成立时，可用 helper 生成起始 evidence 包：

```bash
python3 .gstack/scripts/autopilot_bootstrap.py \
  --topic <topic> \
  --title <中文任务名> \
  --goal <一句话目标> \
  --allowed <允许路径> \
  --verification <验证命令> \
  --ai-reviewed \
  --activate
```

不带 `--ai-reviewed` 时，helper 只生成 draft scaffold，不应直接进入实现。

大需求、产品方向不明或存在多个合理方案时，即使在 `自主执行` 下，也应先通过 office-hours 或 plan review 做必要磨合。

## Gate Recovery Policy

门禁失败后，Codex 不应立即把问题甩给用户。

Codex 必须先读取失败原因，并尝试自行补齐以下内容：

- 本地 active boundary、skills、hooks 或脚本状态；优先运行 `python3 .gstack/scripts/gstack_doctor.py check`
- active boundary 或 `GStack Required Flow`
- `Subagent Plan`
- requirement brief / requirement freeze
- plan review 或小需求的轻量 review evidence
- domain spec readiness 或 no-spec-change 原因
- QA 报告、测试命令和验证证据
- UI / HTML / 可视化任务的验收 URL、刷新 / 重新生成路径、Browser / Chrome / Playwright 交互 evidence
- Required Gates 的 `not-required` 排除原因或 evidence path
- `implement` / `qa` 状态同步

Codex 不得为了通过门禁编造证据。以下情况必须提示用户：

- 需要业务负责人决定产品口径
- 真实数据源、字段口径、权限或 owner 无法由仓库证据确认
- 生产部署、生产重启、线上数据修复
- relational database / analytics warehouse schema 变更、生产写入、破坏性命令
- git workflow action：创建 / 切换分支、commit、amend、rebase、push、pull、merge、cherry-pick、reset、PR
- 本地无法运行验证，且没有等价证据

提示用户时必须说明：

- 哪个门禁卡住
- Codex 已经尝试了什么
- 缺少哪类决策或外部证据
- 推荐选择是什么

## 本地重启策略

`自主执行模式` 下，Codex 可以在任务完成后自动重启本地开发项目并验证页面或接口。

允许：

```bash
bash scripts/dev_stack.sh restart
```

禁止自动执行：

- 生产服务重启
- 远端部署
- 需要 SSH / 云平台 / 线上账号的操作
- 任何会写真实生产数据的命令

## 与 subagent 和 goal mode 的关系

subagent 是并行分工工具；goal mode 是持续推进和防中断工具。两者都不替代 main agent 的最终判断、集成、验证和用户答复。

### subagent 使用规则

适合使用 subagent：

- 大需求需要并行读取多个模块、spec、历史 evidence 或数据源说明。
- 需要独立 review，例如产品、工程、QA、文档覆盖分别复核。
- 实现能拆成互不重叠的写范围。
- diff 较大，需要独立只读复核。
- 数据任务需要 source explorer / SQL author / SQL reviewer 这类分工。

不适合使用 subagent：

- 小需求、单文件改动或低风险文档小改。
- 写范围强耦合，拆分会增加合并风险。
- 主 agent 自己直接做更快。
- 没有独立验证面的任务。

使用要求：

- active boundary 必须先写 `Subagent Plan`。
- explorer / reviewer 默认 read-only。
- worker 必须有互不重叠的 repo-relative write scope。
- subagent 输出必须由 main agent 回收到 boundary、review、QA、decision、learning 或相关 spec。
- subagent 的猜测不能直接写成“已通过 QA”“业务已确认”或接口真源。

### goal mode 使用规则

适合使用 goal mode：

- 用户给了明确目标，但任务会跨多轮推进。
- 任务需要持续跑完整链路：拆解、开发、测试、文档、门禁恢复。
- 任务可能被中断，需要保留当前目标和完成状态。
- `自主执行` 下的大中型任务。

不适合使用 goal mode：

- 用户只是在问方案或做产品探索。
- `手动控制` 模式。
- 一两步能完成的小改。
- 当前目标不清楚，还在 office-hours 或需求磨合阶段。

### 按协作模式的默认行为

| 模式 | subagent 默认行为 | goal mode 默认行为 |
| --- | --- | --- |
| 自主执行 | 小任务通常 `not-used`；中大型任务可按 boundary 自动使用 | 中大型任务可自动开启；小任务通常不需要 |
| 关键确认 | 可用于 read-only 探索 / review；worker 执行前遇关键决策需确认 | 可开启，但关键决策点暂停给用户确认 |
| 手动控制 | 默认不启动 worker；可在用户同意后使用 read-only reviewer | 默认不开；除非用户明确要求持续推进 |

每个正式任务的 boundary 应记录：

- `Subagent Plan`: 是否使用 subagent、使用原因、写范围和证据回收方式。
- `Goal Mode`: `enabled / not-used / ask-first`，以及原因和目标。

## 输出要求

当模式被选择或切换后，Codex 应简短确认：

```text
已切到自主执行模式。本次我会自动拆解、开发、测试、补文档和修门禁；遇到生产、DB schema 或 git 操作会再问你。
```

当用户问“怎么选”时，给出三档选择，不直接进入实现。
