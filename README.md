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

如果只是把入口发给普通伙伴，优先发 [QUICK_START_FOR_PARTNERS.md](QUICK_START_FOR_PARTNERS.md)。那份文档只保留“在 Codex 里怎么说、做完怎么看结果、什么时候需要确认”。

## 推荐发放形式

公司内推广时，建议把它当作一个“可复制的仓库骨架”发放，而不是只发一份提示词或文档包。

完整接入流程见 [COMPANY_ADOPTION_GUIDE.md](COMPANY_ADOPTION_GUIDE.md)。内部安装器 / Codex 接入器的产品化路线见 [CODEX_ADOPTION_CONNECTOR.md](CODEX_ADOPTION_CONNECTOR.md)。

推荐交付内容：

- 完整仓库目录：`AGENTS.md`、`.gstack/`、`adapters/`、`scripts/`、`examples/` 和 `tests/`
- 普通伙伴短入口：`QUICK_START_FOR_PARTNERS.md`
- 公共 workspace layers：`blueprint/`、`archive/`、`shared/` 和 `stack/`
- 默认 adapter：`adapters/default/adapter.md` 给人读，`adapters/default/runtime.json` 给脚本读
- 自然语言接入提示：用户在目标项目里对 Codex 说明“请把当前项目接入 KK Dev Skeleton”
- 内部执行工具：`scripts/` 和 `.gstack/scripts/` 供 Codex 初始化、检查和排障，不要求业务用户手动运行
- repo-local plugin 源目录：`plugins/kk-dev-skeleton-adoption/`，供后续公司内部 Codex 接入器分发
- repo-local marketplace source：`.agents/plugins/marketplace.json`，供明确授权后的内部安装 / 升级流程使用
- published Git marketplace：`https://github.com/duanxibo/kk-ai-dev-skeleton.git`
- marketplace/plugin 推广包：`plugins/PARTNER_INSTALL.md`、`plugins/MARKETPLACE_ROLLOUT.md`、`plugins/ADMIN_INSTALL_CHECKLIST.md` 和 `plugins/PILOT_FEEDBACK.md`
- 本地产品化准备脚本：`scripts/setup_local_codex.sh`，供 Codex / 维护者同步 repo-native skills、安装 hooks 并复跑 doctor；普通伙伴不需要手动记这个命令

推荐路线：

- 现在：发完整骨架包或内部模板仓库，用户通过 Codex 自然语言接入。
- 下一步：使用 Codex 调用的 V1 内部安装器，把探测、计划、adapter 创建、检查和报告收敛成确定性 helper。
- 后续：使用 `plugins/kk-dev-skeleton-adoption/` 和 `.agents/plugins/marketplace.json` 作为公司内部 Codex 接入器源目录与 marketplace source；已经发布到 `https://github.com/duanxibo/kk-ai-dev-skeleton.git` 后，可按 `plugins/PARTNER_INSTALL.md` 和 `plugins/MARKETPLACE_ROLLOUT.md` 组织安装、升级和验收。
- 插件产品化：`kk-dev-skeleton-adoption` 内置非阻断式更新检查，伙伴下次使用插件时可自动感知 GitHub `main` 上是否有新版，并得到刷新 marketplace 的提醒。
- 已有项目升级：伙伴更新插件后，可以让 Codex 对当前项目生成增量升级计划并执行安全改造，不需要新建项目重新接入。

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
- 如果检测到根目录已有 `src/`、`prisma/`、`e2e/`、`package.json` 等应用代码或配置，优先用 adapter 适配现有布局，不自动搬迁；迁移是可选任务
- 运行 doctor、guard 和 smoke 检查
- 生成接入总结、剩余问题和试点任务建议

Codex 背后的 V1 内部安装器能力已经收敛在 `scripts/init_project.py`：支持 detect、plan、apply、verify 和 report。它是 Codex 的执行层，不是业务用户需要学习的入口。

已有项目升级时，用户对 Codex 说：

```text
请使用最新版 KK Dev Skeleton Adoption，按最新版骨架升级当前项目。
先生成增量升级计划，不要重新接入新项目，不要覆盖现有 adapter，不要移动业务代码。
```

Codex 应先运行 `--upgrade-plan`，只在用户授权和 boundary 允许时执行 `--upgrade-apply` 这类安全幂等改造。

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
- 面向纯线上 AI Software Factory 的协议层：`OnlineDemand / ClaimPackage / StatusEvent`、受控 runner 交接、repo evidence 回写和高风险授权隔离

## 协作蓝图

如果你要理解这套骨架为什么这样组织，先读：

- [`.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`](.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md)
- [`.gstack/knowledge/ai-programming-framework.md`](.gstack/knowledge/ai-programming-framework.md)
- [`.gstack/designs/2026-06-22_online-software-factory-platform-protocol.md`](.gstack/designs/2026-06-22_online-software-factory-platform-protocol.md)

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
  designs/          设计过程产物
  reviews/          评审证据
  qa-reports/       QA 证据
  decisions/        决策记录
  migrations/       迁移计划和迁移记录
  learnings/        可复用经验
adapters/
  default/          默认项目适配器模板
blueprint/
  README.md         前置蓝图层，记录系统构想、核心对象和阶段演进
archive/
  baseline/         历史原型、旧 demo 和 baseline snapshot，只作追溯
stack/
  <project>/        初始化后项目应用真源层，承载源码、spec、测试、fixtures 和项目脚本
shared/
  raw-inputs/       经过授权或脱敏的共享输入样例
  fixtures/         跨 stack 复用的 fixtures
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
```

如果 Codex 需要一次性整理本机 Codex 接入状态，可在幕后运行：

```bash
bash scripts/setup_local_codex.sh
```

如果 doctor 明确提示存在旧 `tg-*` symlink 且本机不再需要它们，可运行：

```bash
bash scripts/setup_local_codex.sh --remove-tg-links
```

更细的检查命令：

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

## 历史和蓝图层

公共骨架保留空的 `blueprint/`、`archive/` 和 `shared/` 层，但不提供任何真实业务资产。

- `blueprint/`：前置构想、核心对象、初版原则和阶段演进。
- `archive/`：已退出当前真源链路的历史材料，只作追溯。
- `archive/baseline/`：历史原型、旧 demo、旧页面行为和 baseline snapshot。
- `shared/`：跨模块共享的脱敏输入、fixtures 和可复用中间产物。

新功能默认从 `stack/<project>/specs/` 和 adapter 出发。只有 active boundary 明确需要历史追溯时，才读 `archive/`；采纳结论必须回写到当前真源。

## 能力保真规则

改骨架时，不要移除自然语言旅程、gate、QA 维度、dashboard 行为或 doctor 检查。除非你用等价或更好的能力替代，并同步更新 smoke tests。

## 轻量接入与授权范围

- 已有项目默认保留源码布局，由 adapter 指向现有源码、规格和测试；目录迁移不是接入前提。
- 低风险小任务可用 `python3 .gstack/scripts/autopilot_bootstrap.py --compact-evidence ...`，将需求、评审、边界、QA 合并为一份记录。QA 完成必须通过 `qa_verify.py --boundary <任务边界>` 执行验收映射中的命令并记录回执；仅执行普通命令不能标记产品验收完成。
- 自动推进只限用户已授权目标；独立下一步建议不能自动变成新任务。已明确授权的动作不重复询问。
- adapter 缺失、JSON 损坏或字段类型不合法时，关键 guard 默认报错。旧 adapter 至少应显式声明 `paths.implementation_prefixes`（纯元数据 adapter 可用空列表），其余路径以项目实际情况填写。`load_adapter_runtime(..., strict=False)` 仅用于显式兼容/诊断，返回告警和空路径，不代表检查通过。
- `.github/workflows/ci.yml` 在 PR 和 main push 上运行 Python 3.11/3.12 行为测试、adapter 校验和 smoke。流程记录不替代测试、独立审查或权限隔离。

已有项目升级时，`--apply-runtime --dry-run --format json` 的 `preserved_differences` 会列出与来源不同的文件及双方 SHA-256。它不能区分旧版本和用户定制，必须先审查差异；现有文件仍保留。

### Runtime 版本与升级

当前 plugin 与 runtime bundle release 为 `0.2.0`。JSON `version` 是配置 schema 版本，不能代替发布版本。使用固定 tag 或 commit 的骨架 checkout 安装，避免把浮动 main 当成可复现版本。

安装记录 `.gstack/runtime-install.json` 保存已安装文件的 SHA-256。显式执行 `scripts/init_project.py --apply-runtime --upgrade-runtime --dry-run` 预览，然后去掉 `--dry-run` 应用：先整包检查和隔离兼容验证，有定制冲突就整包停止；写入失败恢复旧脚本和安装清单。旧安装没有记录时保守保留差异，人工合并后重新运行安装建立基线。release 号表示来源；`preserved_differences` 必须清空后才能认定完整升级。

语义复核通过、无风险且不改变 UI/API/数据，并通过 `--allowed` 明确实际文件范围的 fast-lane 正式 kickoff 自动使用一份简短记录；草稿和复杂任务保留完整流程。QA 仍需实际执行与执行 receipt。

实际项目接入时，先用 `target_verification.py --configure-command-json '<实际产品测试的 JSON argv>'` 配置断言测试，再在 boundary 的 `Acceptance Verification` 中对应每项验收。`qa_verify.py --boundary <任务路径>` 自动运行所有映射命令；旧的 `--command-key` 单独执行仍可用于诊断，不构成产品验收。可选 `target_verification.py --install-ci-boundary <任务路径>` 安装独立 CI，保留已有 workflow；依赖安装及后续任务选择由项目配置。

升级兼容检查覆盖脚本编译、adapter 以及 Loop/QA 命令依赖；不替代产品验收，也不保证断电或进程被杀时原子恢复。
