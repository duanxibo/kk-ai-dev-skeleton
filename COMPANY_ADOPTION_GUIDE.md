# 公司内接入指南

这份指南用于把 KK Dev Skeleton 发给公司内其它团队，并判断一个新项目是否已经正确接入。

默认接入方式是：用户在目标项目里用自然语言告诉 Codex“请把当前项目接入 KK Dev Skeleton”。用户不需要手动执行初始化命令；命令和脚本是 Codex 背后的执行工具和排障工具。

推荐把骨架作为完整仓库目录发放，而不是只发提示词、单份文档或压缩后的 `.gstack/` 片段。完整骨架能保留 agent 规则、adapter、脚本、模板、任务边界、QA 证据和可持续回写能力。

内部安装器 / Codex 接入器的产品化路线见 [CODEX_ADOPTION_CONNECTOR.md](CODEX_ADOPTION_CONNECTOR.md)。当前阶段采用“完整骨架包 + Codex 自然语言接入”；V1 内部安装器已经提供 Codex 可调用的 detect、plan、apply、verify 和 report helper。

## 适用对象

- 想让团队用自然语言驱动 AI 开发的项目负责人。
- 需要把 AI 开发过程沉淀到仓库的工程团队。
- 需要在多个项目之间复用同一套协作规则，但保留项目专属路径、数据、测试和发布规则的团队。

## 发放包必须包含

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

不要只发以下内容：

- 单独的 prompt。
- 单独的 `.gstack/skills/`。
- 单独的 `adapters/default/`。
- 没有 `AGENTS.md` 的脚本包。

## 发放前检查

发放前让 Codex 完成这些检查：

- 框架核心不包含具体业务域、私有项目名、真实客户名、密钥或本机绝对路径。
- `adapters/default/adapter.md` 是中性模板，不写真实项目规则。
- `adapters/default/runtime.json` 只包含默认示例路径，不绑定某个真实项目。
- `AGENTS.md`、`README.md`、`.gstack/README.md` 和 `.gstack/knowledge/CODEMAP.md` 能解释从哪里开始。
- doctor 能运行。
- spec sync guard 能运行。
- natural language smoke 能运行。

如果 doctor 提醒当前目录不是 git worktree，可以接受；复制到真实项目并初始化 git 后应再次运行。

## 新项目自然语言接入

用户在目标项目里打开 Codex，然后直接说：

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

如果用户不知道源码或文档位置，可以写“不确定，请你先判断”。Codex 应先读仓库入口、识别已有结构，再提出 adapter 草案；只有业务含义、真实数据权限、生产风险、数据库变更或代码提交流程需要用户确认时才停下来问。

Codex 接到这条自然语言请求后，应负责：

- 判断当前项目是否已经包含骨架；如果没有，说明需要先把骨架文件加入仓库或工作区。
- 创建或更新 `adapters/<project>/adapter.md`。
- 创建或更新 `adapters/<project>/runtime.json`。
- 创建或保留 `stack/<project>/`，把它作为后续应用源码、spec、测试、fixtures 和项目脚本的默认真源目录。
- 如果目标项目已有根目录 `src/`、`prisma/`、`e2e/`、`package.json` 等应用代码或配置，列为迁移候选；不要在未确认迁移计划时自动移动。
- 设置或说明当前 adapter。
- 运行 doctor、guard 和 smoke 检查。
- 生成接入总结：已完成项、缺失信息、风险、下一步试点任务。

命令行形式只作为 Codex 内部执行和排障参考，不作为业务用户的接入方式。V1 内部安装器集中在 `scripts/init_project.py`，供 Codex 在接入任务里调用。

## 后续产品化路径

当前推荐给用户的是一段自然语言接入提示和完整骨架包。Codex 负责在后台调用 V1 内部安装器、写 adapter、运行检查和解释结果。

后续可以分两步产品化：

- 内部安装器：把骨架复制、版本对比、adapter 合并和接入自检收敛成确定性执行层，由 Codex 调用。
- Codex 接入器：使用 `plugins/kk-dev-skeleton-adoption/` 作为 repo-local plugin 源目录，把内部安装器包装成公司成员在 Codex 中可发现、可复用的能力，用户仍然只需要说“把当前项目接入 KK Dev Skeleton”。

当前 `plugins/kk-dev-skeleton-adoption/` 只是源目录和分发骨架，不会自动安装，也不会写 marketplace。公司要统一分发时，应再设计内部 marketplace 或安装流程。

当前仓库已经包含 repo-local marketplace source：`.agents/plugins/marketplace.json`。它指向 `plugins/kk-dev-skeleton-adoption/`，并配有安装升级说明：`plugins/MARKETPLACE_INSTALL.md`。

进入 marketplace / plugin 安装推广时，先使用 `plugins/MARKETPLACE_ROLLOUT.md` 组织七天试点，再让管理员按 `plugins/ADMIN_INSTALL_CHECKLIST.md` 安装，并用 `plugins/PILOT_FEEDBACK.md` 收集反馈。

当前发布仓库是 `https://github.com/duanxibo/kk-ai-dev-skeleton.git`。给伙伴的最短安装入口见 `plugins/PARTNER_INSTALL.md`。

注意：安装 marketplace 或 plugin 是管理员 / 发布动作，不是业务用户接入动作。只有在明确授权后，Codex 或管理员才应执行 `codex plugin marketplace add` 或 `codex plugin add`。

无论产品化到哪一步，都不应改变安全边界：真实数据、生产、数据库、破坏性操作和 git workflow action 仍需用户明确授权。

## Adapter 填写清单

接入团队用自然语言提供项目目标、路径、风险和限制；Codex 负责把这些信息落到两份 adapter 文件中。

### `adapter.md`

`adapter.md` 面向人和 AI 阅读，Codex 至少要写清：

- 项目目标。
- 主要用户。
- 第一个可见成功标准。
- 产品、API、数据、UI 和测试真源文档路径。
- 前端、后端、脚本、测试、fixtures 的实现路径。
- 禁止触碰的路径和业务范围。
- 数据、API、权限、发布和回滚规则。
- 项目专属 required gates。

### `runtime.json`

`runtime.json` 面向脚本读取，Codex 至少要写清：

- `implementation_prefixes`
- `spec_prefixes`
- `backend_implementation_prefixes`
- `backend_test_prefixes`
- `backend_domain_spec_prefix`
- `deprecated_backend_spec_prefixes`
- `data_access_trigger_prefixes`
- `frontend_hint_prefixes`
- `prototype_logic_evidence_prefixes`
- `commands.dev_stack_entry`

如果真实项目是 monorepo，把每个 package / service 的源码、测试和规格路径都放进对应前缀，避免 guard 漏判。

## 接入成功标准

一个新项目至少满足这些条件，才算接入成功：

- Codex 报告 doctor 中 `adapter-runtime` 为通过。
- Codex 报告已存在 `stack/<project>/`，或接入报告明确说明为何暂时只做迁移计划。
- Codex 报告 `dev-stack-entry` 为通过，或 adapter 明确声明该项目不需要统一启动入口。
- Codex 报告 spec sync guard 通过。
- Codex 报告 team flow guard 通过，或在非 git worktree 下进入 static audit 并通过。
- Codex 报告 Required Gates audit 能解析 active boundary。
- Codex 报告 natural language smoke 通过。
- agent 不从父目录名、旧项目缓存或全局 skill 推断项目身份。

## 试点任务

第一个试点任务应故意选小，不要从真实数据、生产发布或跨模块重构开始。

推荐试点：

- 修改一处文档说明。
- 调整一个静态页面文案。
- 补一个只读脚本参数。
- 给已有页面补一个空态说明。

试点任务必须验证：

- 是否生成 requirement、review、boundary 和 QA evidence。
- active boundary 是否指向本次任务。
- Required Gates 是否能写清 `not-required` 的原因。
- 如果有用户可见页面变化，是否真的用 Browser、Chrome、Playwright 或等价方式验收。
- delivery summary 是否能转成非技术团队看得懂的完成说明。

## 安全边界

接入期间不要默认授权这些动作：

- git workflow action。
- 生产环境操作。
- 数据库 schema 变更。
- 真实数据写入或批量导出。
- 破坏性文件操作。
- 修改 adapter 未允许的路径。

如果确实需要这些动作，必须让用户在当前任务中明确授权，并把授权范围写入 task boundary。

## 常见失败与处理

### doctor 提醒上下文串味

对 Codex 说：

```text
doctor 提醒上下文串味。请只按当前仓库、当前 adapter、active boundary 和我的输入判断项目身份，检查并修复接入状态。
```

Codex 的处理顺序：

1. 确认 `KK_ADAPTER` 指向当前项目 adapter。
2. 确认 `adapter.md` 已写入当前项目目标和术语。
3. 同步当前仓库的 repo-native skills。
4. 如本机不再需要旧项目 skill symlink，再按 README 的清理说明处理。
5. 新开会话后重新运行 doctor。

### guard 没有识别项目路径

对 Codex 说：

```text
guard 没有识别当前项目路径。请优先检查 adapter runtime，不要直接改 guard 代码。
```

大多数路径误判都应该通过 `adapters/<project>/runtime.json` 修复。

### 非技术用户看不懂输出

优先修非技术 helper 或 delivery summary，不要要求用户学习 boundary、gate、spec、runtime 等内部词。

## 升级策略

后续升级骨架时，优先保留项目自己的 adapter。

对 Codex 说：

```text
请升级当前项目里的 KK Dev Skeleton 框架核心，但保留并人工合并当前项目 adapter。升级后重跑接入自检，并用一个小试点任务确认仍然可用。
```

Codex 推荐顺序：

1. 更新 framework core：`.gstack/`、`scripts/`、`AGENTS.md`、`README.md`。
2. 保留或人工合并 `adapters/<project>/adapter.md`。
3. 保留或人工合并 `adapters/<project>/runtime.json`。
4. 重跑 doctor、guard、smoke。
5. 用一个小试点任务确认接入仍然可用。

不要用新的 default adapter 直接覆盖真实项目 adapter。
