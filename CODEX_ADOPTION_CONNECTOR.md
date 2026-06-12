# Codex 接入器产品化方案

这份方案定义 KK Dev Skeleton 在公司内的推荐发放形式：

```text
用户入口：对 Codex 说自然语言目标
执行主体：Codex 调用骨架内确定性 helper 和 guard
后续产品化：内部安装器 / Codex 接入器 / 内部 plugin
```

核心判断：不要把接入方式设计成“用户手动执行命令”。命令、脚本和 guard 是 Codex 背后的执行工具；用户只需要在目标项目里说明项目目标、边界和风险。

## 推荐形态

### 短期：完整骨架包 + Codex 自然语言接入

适合现在立即推广。

发给团队的内容是完整仓库骨架，而不是单独 prompt 或单独 `.gstack/`：

- `AGENTS.md`
- `README.md`
- `COMPANY_ADOPTION_GUIDE.md`
- `CODEX_ADOPTION_CONNECTOR.md`
- `.gstack/`
- `adapters/`
- `scripts/`
- `examples/`
- `tests/`
- `plugins/`
- `.agents/plugins/marketplace.json`

用户在目标项目里对 Codex 说：

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

Codex 负责判断是否需要复制骨架文件、创建 adapter、运行自检和生成接入总结。

### 中期：内部安装器

内部安装器不是给业务用户直接操作的命令行工具，而是 Codex 可以调用的确定性执行层。

它应提供这些能力：

- 检测目标项目是否已接入骨架。
- 对比 framework core 版本，列出缺失或过期文件。
- 复制或更新 `AGENTS.md`、`.gstack/`、`scripts/`、`examples/` 和 `tests/`。
- 保留并合并真实项目的 `adapters/<project>/adapter.md` 和 `runtime.json`。
- 创建或保留 `stack/<project>/`，并把后续应用源码、spec、测试、fixtures 和项目脚本默认路由到该目录。
- 检测根目录已有应用代码和配置，输出迁移候选清单；不在未确认迁移计划时自动移动业务代码。
- 生成接入计划、变更摘要和回滚提示。
- 调用 doctor、spec sync guard、team flow guard、Required Gates audit 和 natural language smoke。
- 给出第一个低风险试点任务建议。

内部安装器的输出应该面向 Codex 和用户同时可读：

- Codex 需要机器可读结果：哪些文件变更、哪些检查通过、哪些检查阻塞。
- 用户需要自然语言摘要：已经接入什么、还缺什么、下一步做什么。

### 长期：Codex 接入器 / 内部 Plugin

当短期流程稳定后，把内部安装器包装成 Codex 可发现、可复用的接入器。

当前仓库已提供 repo-local plugin 源目录：

- `plugins/kk-dev-skeleton-adoption/`

它包含：

- `.codex-plugin/plugin.json`
- `skills/kk-dev-skeleton-adoption/SKILL.md`
- plugin README 和脚本说明

这还是源目录和分发骨架，不是已安装 marketplace。后续如果要在公司范围内安装或展示，需要另起 marketplace / 发布流程。

当前仓库也提供 repo-local marketplace source：

- `.agents/plugins/marketplace.json`
- `.agents/plugins/README.md`
- `plugins/MARKETPLACE_INSTALL.md`

这个 marketplace source 指向 `./plugins/kk-dev-skeleton-adoption`。它不会自动安装；公司内部安装或升级必须作为明确的 admin / release action 执行。

长期形态应该具备：

- 一个稳定的自然语言入口，例如“把这个项目接入 KK Dev Skeleton”。
- 一个 adapter wizard，把用户自然语言转成 adapter 草案。
- 一个安装 / 升级执行器，负责复制、合并和校验 framework core。
- 一个接入报告，展示完成项、缺失项、风险和试点建议。
- 一个版本策略，支持 framework core 升级但不覆盖项目 adapter。
- 一个组织级分发方式，方便公司成员在 Codex 中发现和使用。

接入器不应该绕过仓库规则。所有长期约束仍以目标项目的 `AGENTS.md`、adapter、active boundary 和 repo-native evidence 为准。

## Codex 接入器职责边界

### 必须负责

- 识别当前仓库、adapter 和已有骨架状态。
- 询问最少必要信息：项目名、主要用户、项目目标、源码位置、真源文档位置、本次禁止触碰内容和风险动作。
- 创建或更新项目 adapter。
- 运行接入自检。
- 将接入过程落为 repo-native evidence。
- 给出非技术用户能看懂的接入总结。

### 必须避免

- 要求业务用户手动学习脚本参数。
- 默认连接真实数据、生产环境或数据库。
- 默认执行 git workflow action。
- 默认覆盖已有真实项目 adapter。
- 把本机绝对路径、密钥、客户数据或私有历史项目规则写进 framework core。
- 把一次性聊天结论当成团队真源。

## 产品化阶段

### V0：自然语言接入手册

当前阶段。

交付物：

- `README.md`
- `COMPANY_ADOPTION_GUIDE.md`
- `CODEX_ADOPTION_CONNECTOR.md`
- 默认 adapter
- doctor、guard、smoke helper

验收标准：

- 用户能只通过自然语言描述启动接入。
- Codex 能把接入信息落到 adapter。
- Codex 能运行检查并解释结果。
- 文档不再把“用户执行命令”作为默认路径。

### V1：确定性内部安装器

当前已提供第一版确定性内部安装器能力，目标是减少 Codex 临场判断和复制错误。

现有 helper：

- `scripts/init_project.py`：承担 adapter 创建和接入计划生成。
- `.gstack/scripts/gstack_doctor.py`：承担环境和上下文诊断。
- `.gstack/scripts/spec_sync_guard.py`：承担真源同步检查。
- `.gstack/scripts/team_flow_guard.py`：承担 task boundary 和 evidence 检查。
- `.gstack/scripts/required_gates_audit.py`：承担 Required Gates 检查。
- `.gstack/scripts/natural_language_dev_smoke.py`：承担自然语言接入路径 smoke。

`scripts/init_project.py` 已提供 Codex 内部可调用的动作：

- `detect`：检测当前骨架、adapter、active boundary 和 git worktree 状态。
- `plan`：生成接入计划。
- `apply`：安全创建 adapter；默认不覆盖已有 adapter。
- `apply`：同时确保 `stack/<adapter>/` 存在；已有根目录代码只列为迁移候选。
- `verify`：串联 doctor、spec sync guard、team flow guard、Required Gates audit 和 natural language smoke。
- `report`：生成接入报告和低风险试点任务建议。

V1 不要求用户直接运行这些工具。Codex 在自然语言任务中调用它们，并把结果翻译成接入总结。

### V2：Codex 接入器

当前已提供 repo-local Codex 接入器 plugin 源目录，目标是让接入动作在 Codex 中成为稳定能力。

当前 plugin 包装能力：

- 自然语言入口：用户说“接入 KK Dev Skeleton”。
- 非阻断式更新提醒：工作流开始时检查 GitHub `main` 上的插件版本，落后时提醒刷新 `kk-dev-skeleton-internal` marketplace。
- V1 helper 调度：检测、计划、应用、验证和报告。
- adapter 保护：默认不覆盖已有项目 adapter。
- 安全边界：生产、数据库、真实数据和 git workflow action 仍需用户明确授权。
- repo-native evidence：继续服从目标仓库的 `AGENTS.md`、adapter、task boundary 和 QA evidence。

V2 的用户体验仍然是自然语言，不是命令面板优先。

### V3：组织级产品化

当前已提供 repo-local marketplace source 和安装升级说明。目标是让公司内多项目持续升级。

已具备：

- repo-local marketplace：`.agents/plugins/marketplace.json`
- published Git marketplace：`https://github.com/duanxibo/kk-ai-dev-skeleton.git`
- 伙伴安装入口：`plugins/PARTNER_INSTALL.md`
- marketplace 安装说明：`plugins/MARKETPLACE_INSTALL.md`
- marketplace 推广计划：`plugins/MARKETPLACE_ROLLOUT.md`
- 管理员安装清单：`plugins/ADMIN_INSTALL_CHECKLIST.md`
- 试点反馈表：`plugins/PILOT_FEEDBACK.md`
- plugin source：`plugins/kk-dev-skeleton-adoption/`
- marketplace 结构测试：`tests/test_plugin_marketplace.py`

后续仍可增加：

- framework core 版本登记
- 项目接入状态登记
- adapter drift 检测
- 升级变更预览
- 统一 QA evidence 摘要
- 管理员策略：哪些目录、数据源、生产动作永远需要人工确认

## 安全策略

接入器必须默认保守：

- 写入前先说明会触碰的文件类型。
- 覆盖已有 adapter 前必须要求确认或生成合并计划。
- 生产、数据库、真实数据、破坏性文件操作和 git workflow action 必须由用户明确授权。
- 所有长期文档使用 repo-relative 路径。
- 任何检查失败都不能伪装成接入成功。

## 接入成功定义

一个项目算完成接入，至少满足：

- 有项目 adapter。
- adapter runtime 能被 helper 解析。
- doctor 通过，或只剩已解释的环境提醒。
- spec sync guard 通过。
- team flow guard 能解析 active boundary。
- Required Gates audit 能解析 active boundary。
- natural language smoke 通过。
- 有一个低风险试点任务建议。
- 用户知道下一步对 Codex 说什么。

## 当前推荐给用户的形式

现在给公司内部用户的推荐形式是：

1. 提供完整骨架包或内部模板仓库。
2. 提供一段自然语言接入提示。
3. 明确告诉用户：脚本由 Codex 调用，用户不需要手动执行。
4. 让 Codex 完成 adapter、检查和接入总结。
5. 用一个低风险试点任务验证骨架真的可用。
6. 如果团队要产品化分发，可以从 `plugins/kk-dev-skeleton-adoption/` 作为内部 Codex plugin 源目录继续包装。
7. 如果团队要进入公司内部分发，可以使用 `.agents/plugins/marketplace.json` 作为 repo-local marketplace source，并按 `plugins/MARKETPLACE_INSTALL.md` 执行明确授权的安装 / 升级流程。
8. 如果团队要让伙伴直接安装，可以使用发布仓库 `https://github.com/duanxibo/kk-ai-dev-skeleton.git`，并把 `plugins/PARTNER_INSTALL.md` 中的自然语言安装入口发给伙伴。

等流程稳定后，再把这套动作产品化成内部安装器和 Codex 接入器。
