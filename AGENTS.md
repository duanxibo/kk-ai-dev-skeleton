# KK Dev Skeleton Agent 工作说明

本文定义 AI agent 在这个骨架中的默认工作方式。正文中文优先；`kk-*`、脚本名、YAML key、环境变量和固定字段保留英文，方便工具链解析。

## 第一原则

任何代码、bugfix、refactor、QA、review 或长期文档任务，都必须先读：

1. `.gstack/README.md`
2. `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
3. `.gstack/knowledge/CODEMAP.md`
4. `.gstack/knowledge/doc-placement.md`
5. `.gstack/knowledge/ai-programming-framework.md`
6. `.gstack/task-boundaries/CURRENT.md`
7. active project adapter，默认从 `adapters/default/adapter.md` 和 `adapters/default/runtime.json` 开始

不要一上来就全仓库搜索。先确认当前任务所在层、真源、active boundary 和 adapter。

## 上下文隔离

当前项目身份只能来自这些真源：

- 用户本轮明确描述的项目目标、业务域和命名
- 当前仓库的 `README.md`、`AGENTS.md`、`.gstack/README.md`
- active project adapter
- active task boundary
- 当前仓库内的长期 spec / requirement / review / QA evidence

不要从以下外部线索推断项目名、业务域或工作规则：

- 父目录名或绝对路径片段
- 兄弟仓库、旧仓库或缓存中的文档
- 全局可用 skills 列表
- 其它项目的 `tg-*`、私有前缀或历史 skill
- 本机用户名、工作区目录名、终端历史或浏览器历史

全局 skills 列表只表示“工具可能可用”，不是当前项目上下文。除非用户明确点名，或当前仓库 `.gstack/skills/` 明确提供，否则不要使用其它项目的 skill 作为当前项目规则来源。本骨架的公开工作流默认使用 `kk-*`。

如果用户描述的是 DataWorks、ODPS、BI、CRM、SaaS、游戏或任何其它业务域，以用户描述和 adapter 为准。不要因为骨架所在父目录、旧 skill 或历史路径里出现其它项目名，就把当前项目改称为那个旧项目。

如果项目身份、adapter 或真源互相冲突，先说明冲突并问一个最小澄清问题；不要编造项目名。

## Core / Adapter 分界

框架核心只保留可复用协作能力：自然语言入口、任务边界、Required Gates、repo-native evidence、dashboard、doctor、QA 和知识回写。

项目专属内容必须放进 adapter 或示例项目，包括：

- 业务模块名
- 项目源码路径
- spec 路径
- adapter runtime 路径配置
- CI check 名称
- forbidden scope 映射
- 本地启动命令
- 数据源和权限规则

如果发现框架核心里出现某个具体项目名、业务模块名或私有路径，优先把它迁移到 adapter 或 example。

## 协作模式

默认模式是 `autonomous`：用户说明目标，agent 负责需求整理、实现、验证、文档同步和本地恢复。

用户可以为单次任务切换：

- `autonomous`：除非遇到高风险决策，否则继续推进
- `checkpoint`：在重要产品或架构选择前暂停确认
- `manual`：只分析，不在授权前改文件

高风险动作必须先获得用户明确批准：

- git workflow actions：创建/切换分支、commit、amend、squash、rebase、push、pull、merge、cherry-pick、reset、创建 PR
- 生产环境操作
- 数据库 schema 变更
- 破坏性文件系统操作
- 超出 adapter 规则的真实数据访问
- 对外发布

## 任务边界

在进入实质性实现前，先在 `.gstack/task-boundaries/` 下创建或更新具体 task boundary 文件。共享的 `CURRENT.md` 是稳定入口文档，不是共享 active pointer。

每个 boundary 必须包含：

- allowed files
- forbidden files
- non-goals
- user-visible acceptance
- generated artifact policy
- collaboration mode
- flow lane
- autonomy plan
- subagent plan
- required gates
- spec sync plan
- verification plan

## Required Flow（固定流程）

正式任务使用这条 evidence chain：

```text
requirement-brief
-> plan review
-> requirement-freeze or prototype-freeze
-> engineering review
-> source-of-truth readiness
-> implementation
-> QA
```

小任务可以走 `fast-lane`，但仍需要最小 requirement、review、boundary 和 QA evidence。

## 用户可见任务

如果任务改变 UI、HTML、dashboard、可视化产物或用户交互：

- 记录预期可见行为
- 记录 URL 或产物路径
- 记录刷新或重新生成步骤
- 使用 Browser、Chrome、Playwright 或等价交互检查验证
- 不要只靠 `rg`、JSON、HTML 字符串或截图外观就标记完成

如果任务没有可见 UI 变化，说明用户应该如何验证。

## 公开 Skill 命名空间

使用 `kk-*` skills：

- `kk-task-kickoff`
- `kk-natural-language-dev`
- `kk-codex-mode`
- `kk-doc-sync`
- `kk-doc-lifecycle`
- `kk-doc-backfill`
- `kk-data-kickoff`
- `kk-data-query`
- `kk-subagent-orchestrator`

不要把项目专属前缀引入可复用框架核心。

## 完成检查

宣告任务完成前：

1. 确认改动始终在 task boundary 内。
2. 确认真源文档已经更新，或明确说明本次不需要。
3. 运行相关测试、smoke checks 或交互 QA。
4. 运行 `python3 .gstack/scripts/spec_sync_guard.py`。
5. 在 `.gstack/qa-reports/` 下写 QA evidence。
6. 把可复用 pitfall 或 pattern 写入 `.gstack/knowledge/`、`.gstack/rules/` 或 `.gstack/learnings/`。
