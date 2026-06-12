# KK Dev Skeleton

KK Dev Skeleton 是一个可公开复用、以仓库为真源的 AI 开发骨架。

它适合希望让 AI coding agent 根据自然语言目标推进开发、同时保留工程纪律的团队。骨架会把需求、任务边界、评审记录、QA 证据、决策和可复用经验都沉淀在仓库里，而不是只留在聊天记录中。

## 怎么使用

你不需要先学会所有内部术语。直接告诉 agent：

- 这个功能给谁用
- 用户应该能做什么
- 做成以后第一眼应该看到什么
- 本次明确不能碰什么
- 是否涉及真实数据、生产环境、数据库、部署或代码提交流程

agent 应该把这些自然语言目标整理成：

- requirement brief
- task boundary
- flow lane：`fast-lane / standard / discovery`
- required gates
- 实现改动
- QA evidence
- delivery summary

## 推荐发放形式

公司内推广时，建议把它当作一个“可复制的仓库骨架”发放，而不是只发一份提示词或文档包。

完整接入流程见 [COMPANY_ADOPTION_GUIDE.md](COMPANY_ADOPTION_GUIDE.md)。内部安装器 / Codex 接入器的产品化路线见 [CODEX_ADOPTION_CONNECTOR.md](CODEX_ADOPTION_CONNECTOR.md)。

推荐交付内容：

- 完整仓库目录：`AGENTS.md`、`.gstack/`、`adapters/`、`scripts/`、`examples/` 和 `tests/`
- 默认 adapter：`adapters/default/adapter.md` 给人读，`adapters/default/runtime.json` 给脚本读
- 自然语言接入提示：用户在目标项目里对 Codex 说明“请把当前项目接入 KK Dev Skeleton”
- 内部执行工具：`scripts/` 和 `.gstack/scripts/` 供 Codex 初始化、检查和排障，不要求业务用户手动运行
- repo-local plugin 源目录：`plugins/kk-dev-skeleton-adoption/`，供后续公司内部 Codex 接入器分发
- repo-local marketplace source：`.agents/plugins/marketplace.json`，供明确授权后的内部安装 / 升级流程使用
- published Git marketplace：`https://github.com/duanxibo/kk-ai-dev-skeleton.git`
- marketplace/plugin 推广包：`plugins/PARTNER_INSTALL.md`、`plugins/MARKETPLACE_ROLLOUT.md`、`plugins/ADMIN_INSTALL_CHECKLIST.md` 和 `plugins/PILOT_FEEDBACK.md`

推荐路线：

- 现在：发完整骨架包或内部模板仓库，用户通过 Codex 自然语言接入。
- 下一步：使用 Codex 调用的 V1 内部安装器，把探测、计划、adapter 创建、检查和报告收敛成确定性 helper。
- 后续：使用 `plugins/kk-dev-skeleton-adoption/` 和 `.agents/plugins/marketplace.json` 作为公司内部 Codex 接入器源目录与 marketplace source；已经发布到 `https://github.com/duanxibo/kk-ai-dev-skeleton.git` 后，可按 `plugins/PARTNER_INSTALL.md` 和 `plugins/MARKETPLACE_ROLLOUT.md` 组织安装、升级和验收。
- 插件产品化：`kk-dev-skeleton-adoption` 内置非阻断式更新检查，伙伴下次使用插件时可自动感知 GitHub `main` 上是否有新版，并得到刷新 marketplace 的提醒。

新项目接入时，用户对 Codex 说：

```text
请把当前项目接入 KK Dev Skeleton。

项目名：my-project
主要用户：<谁会用这个项目>
项目目标：<这个项目要解决什么问题>
源码大致位置：<例如 app/、src/、packages/，不知道可以写“不确定，请你判断”>
产品 / API / 数据 / UI / 测试文档位置：<如果不知道，请你先扫描并建议>
本次不要碰：<明确不要改的目录、业务范围或风险动作>
先不要操作：真实数据、生产环境、数据库、代码提交流程。

请你创建或更新项目 adapter，运行接入自检，告诉我还缺什么，以及建议第一个低风险试点任务。
```

Codex 应负责：

- 创建或更新 `adapters/my-project/adapter.md`
- 创建或更新 `adapters/my-project/runtime.json`
- 创建或保留 `stack/my-project/`，作为后续应用源码、spec、测试、fixtures 和项目脚本的默认真源目录
- 如果检测到根目录已有 `src/`、`prisma/`、`e2e/`、`package.json` 等应用代码或配置，先输出迁移计划，不自动搬迁
- 运行 doctor、guard 和 smoke 检查
- 生成接入总结、剩余问题和试点任务建议

Codex 背后的 V1 内部安装器能力已经收敛在 `scripts/init_project.py`：支持 detect、plan、apply、verify 和 report。它是 Codex 的执行层，不是业务用户需要学习的入口。

## 核心能力

- 自然语言开发入口
- 首次使用引导和需求模板
- 带 allowed / forbidden paths 的任务开工流程
- 协作模式：`autonomous / checkpoint / manual`
- 面向小需求、常规需求和探索需求的 flow lanes
- 覆盖数据、API、原型逻辑、文档、QA 和 subagent 规划的 Required Gates
- 用户可见验收和生成产物策略
- 区分结构、可见性、交互、状态变化、空态和刷新说明的 QA 报告
- 基于 repo-native evidence 生成 dashboard
- 检查本地项目状态的 doctor
- 覆盖非技术用户关键路径的 smoke tests
- 可持续回写的 knowledge、rules、pitfalls 和 learnings

## 协作蓝图

如果你要理解这套骨架为什么这样组织，先读：

- [`.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`](.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md)
- [`.gstack/knowledge/ai-programming-framework.md`](.gstack/knowledge/ai-programming-framework.md)

一句话原则：

```text
协作质量 = 约束层 x 任务边界层 x 知识层 x 反馈层
```

框架核心保留可复用工作流；项目业务、技术栈、路径、命令、数据和发布规则放进 adapter。

## 公开 Skill 命名空间

所有公开 skill 都使用 `kk-` 前缀：

- `kk-natural-language-dev`
- `kk-task-kickoff`
- `kk-codex-mode`
- `kk-doc-sync`
- `kk-doc-lifecycle`
- `kk-doc-backfill`
- `kk-data-kickoff`
- `kk-data-query`
- `kk-subagent-orchestrator`

项目自己的 fork 应保留 `kk-` 命名空间来表达可复用框架行为，把项目专属行为放进 adapter。

## 目录结构

```text
.gstack/
  knowledge/        可复用框架知识
  templates/        requirement、review、boundary、QA、decision 模板
  scripts/          确定性 helper、dashboard、doctor、smoke
  skills/           kk-* 工作流技能
  workflows/        协作流程文档
  task-boundaries/  具体任务边界
  requirements/     需求 brief 和 freeze
  reviews/          评审证据
  qa-reports/       QA 证据
  decisions/        决策记录
  learnings/        可复用经验
adapters/
  default/          默认项目适配器模板
stack/
  <project>/        初始化后项目应用真源层，承载源码、spec、测试、fixtures 和项目脚本
examples/
  simple-web-app/   最小示例项目
tests/              骨架级 smoke wrapper
plugins/
  kk-dev-skeleton-adoption/
                    repo-local Codex 接入器 plugin 源目录
.agents/
  plugins/
    marketplace.json
                    repo-local internal marketplace source
```

## 快速检查

```bash
python3 .gstack/scripts/gstack_doctor.py check
python3 .gstack/scripts/gstack_dashboard.py show
python3 .gstack/scripts/natural_language_dev_smoke.py
python3 .gstack/scripts/spec_sync_guard.py
```

## 使用后感觉串味

如果 agent 把你的新项目称为旧项目名，或者从父目录、历史仓库、全局 skills 里拿到了不相关信息，按这个顺序处理：

1. 确认当前项目的真实业务域写进 adapter，例如 `adapters/default/adapter.md`。
2. 运行 `python3 .gstack/scripts/gstack_doctor.py check`，查看 `context-isolation` 提醒。
3. 运行 `bash .gstack/scripts/sync_repo_skills.sh`，同步当前仓库的 `kk-*` skills。
4. 如果你本机已经不需要旧的 `tg-*` symlink，再运行 `bash .gstack/scripts/sync_repo_skills.sh --remove-tg-links`。
5. 新开一个 Codex 会话或重启当前会话，让新的 AGENTS 和 skill 状态生效。

原则是：中文解释工作流，英文保留机器可读接口；项目语义只信当前仓库和 adapter，不信父目录名或全局 skill 列表。

## Adapter 优先

框架核心不应该写死你的业务领域或技术栈。项目专属规则应放在 `adapters/default/adapter.md`，或复制出新的 adapter。

一个 adapter 应说明：

- 项目目标
- 真源文档路径
- 实现路径
- 测试、构建和本地启动命令
- 数据和 API 规则
- forbidden paths
- 发布和回滚规则
- 项目专属 required gates

其中：

- `adapter.md` 面向人和 AI 读，解释项目语义和协作规则。
- `runtime.json` 面向脚本读，驱动 `spec_sync_guard`、`required_gates_audit`、`team_flow_guard` 和 `gstack_doctor` 的路径判断。

## 能力保真规则

改骨架时，不要移除自然语言旅程、gate、QA 维度、dashboard 行为或 doctor 检查。除非你用等价或更好的能力替代，并同步更新 smoke tests。
