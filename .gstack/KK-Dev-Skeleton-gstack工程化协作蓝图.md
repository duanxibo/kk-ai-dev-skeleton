# KK Dev Skeleton gstack 工程化协作蓝图

这份文档是 KK Dev Skeleton 的协作总章程。

它解释这个骨架为什么这样组织，以及 AI agent 在任何接入项目中应该如何从自然语言目标推进到可验证交付。具体项目的业务、技术栈、数据源和发布规则不写在这里，统一放到 `adapters/<project>/`。

## 核心命题

AI 开发质量不只取决于模型能力，还取决于仓库是否给了足够稳定的工作系统。

KK Dev Skeleton 的目标是把一次临时对话变成可持续积累的工程协作：

```text
协作质量 = 约束层 x 任务边界层 x 知识层 x 反馈层
```

- 约束层：
  `AGENTS.md`、`.gstack/README.md`、adapter 和安全规则，定义永远不能越过的边界。
- 任务边界层：
  `.gstack/task-boundaries/*.md`，定义本次能做什么、不能做什么、怎么验收。
- 知识层：
  `.gstack/knowledge/`、`.gstack/entrypoints/` 和项目真源文档，告诉 AI 此刻应该信哪一层。
- 反馈层：
  `.gstack/reviews/`、`.gstack/qa-reports/`、`.gstack/learnings/` 和 `.gstack/rules/`，把这次踩坑回写给下一次。

## 四层架构

```text
repo
├─ AGENTS.md                     约束层：agent 默认工作规则
├─ adapters/<project>/           项目适配层：业务、技术栈、路径、命令、数据规则
├─ app / src / stack / packages  应用真源层：具体项目代码、spec、tests、fixtures
└─ .gstack/
   ├─ knowledge/                 可复用协作知识
   ├─ entrypoints/               角色入口
   ├─ templates/                 evidence 模板
   ├─ skills/                    kk-* 工作流技能
   ├─ workflows/                 固定流程说明和 guard 配置
   ├─ task-boundaries/           每次任务边界
   ├─ requirements/              需求 brief / freeze
   ├─ reviews/                   计划、工程、代码和设计 review
   ├─ qa-reports/                QA evidence
   ├─ decisions/                 长期决策记录
   ├─ learnings/                 可复用经验
   └─ rules/                     长期规则和 pitfalls
```

`.gstack/` 是协作操作层，不是应用业务规格库。应用产品语义、API、数据模型、测试和实现真源由 adapter 指向项目自己的目录。

## Core / Adapter / Runtime

### Framework Core

应该在所有项目复用：

- 自然语言开发入口
- 首次使用引导
- 需求完整度检查
- 协作模式
- flow lane
- task boundary
- required gates
- repo-native evidence
- dashboard
- doctor
- QA evidence
- knowledge feedback

### Project Adapter

必须由每个项目自己提供：

- 项目目标和术语表
- 真源文档路径
- allowed implementation roots
- forbidden roots
- 测试、构建、本地启动命令
- 数据、API、权限和发布规则
- 项目专属 gates
- 项目专属 forbidden scope 映射

### Runtime / Product Surface

可以后续产品化：

- command center
- task dashboard
- preview server
- QA 截图和录屏
- PR / 发布授权 UI
- adapter installer

## 固定研发流

正式任务默认按以下 evidence chain 推进：

```text
requirement-brief
-> plan review
-> requirement-freeze or prototype-freeze
-> engineering review
-> source-of-truth readiness
-> implementation
-> QA
```

小任务可以走 `fast-lane`，但不能没有记录：

- 最小 requirement
- 最小 review
- task boundary
- QA evidence

大需求、业务目标不清、存在多个合理方案或涉及真实数据 / 生产 / DB / 发布时，进入 `discovery` 或 `standard`，先澄清再实现。

## 三条主工作流

### 功能开发

1. 识别 adapter 和真源路径。
2. 落 requirement brief。
3. 做 plan review，确认先做什么、不做什么。
4. 冻结 requirement 或 prototype。
5. 做 engineering review，确认数据、接口、状态、测试和风险。
6. 建 task boundary，声明 allowed files、forbidden files、Required Gates、Subagent Plan 和 Spec Sync Plan。
7. 在 allowed paths 内实现。
8. 运行 guard、测试和 QA。
9. 将新经验写回 knowledge / rules / learnings。

### Bug 修复

1. 先调查根因，不先猜修法。
2. 读取 CODEMAP、adapter 和相关 pitfalls。
3. 落最小 requirement 和 boundary。
4. 修复时保持 scope 隔离。
5. 增加或更新定向验证。
6. 写 QA evidence。
7. 如果发现可复用坑，回写 knowledge / rules。

### 经验回收

1. 对比 AI 原始改动和后续人工回改。
2. 分类偏差：命名、边界、职责、测试、交互、数据、权限。
3. 判断写回位置：
   - `knowledge/code-patterns.md`
   - `knowledge/pitfalls/`
   - `rules/`
   - `learnings/`
4. 删除或归档过期规则，不让知识层无限膨胀。

## Required Gates

Required Gates 表达专项风险，不替代固定研发流。

常见 gates：

- `data-access`
- `data-query`
- `prototype-logic-extraction`
- `subagent-plan`
- `doc-backfill`
- `data-knowledge-sync`
- `ui-interaction-qa`

每个 gate 必须说明：

- 为什么需要或为什么不需要
- owner
- required_before
- status
- evidence_path
- done_criteria

## Dashboard 规则

dashboard 是 generated view，不是共享真源。

允许：

- 从 requirement、boundary、review、QA 和本地 active pointer 生成视图
- 输出到 stdout、本地 `output/` 或 CI artifact

禁止：

- 提交共享 `.gstack/dashboard.*`
- 提交共享 `.gstack/status.json`
- 用单个多人编辑状态文件替代 repo-native evidence

## 用户体验原则

非技术用户不需要理解 boundary、gate、spec、QA 或路径。

用户只需要说明：

- 谁会用
- 想完成什么
- 成功后第一眼看到什么
- 本次不做什么
- 是否涉及真实数据、生产、数据库、发布或 git workflow
- 怎么验收

Codex 负责把这些内容转译为 requirement、boundary、review、QA evidence 和必要的 adapter 检查。

## 完成定义

任务完成前必须能回答：

- 本次改动是否始终在 boundary 内？
- 真源文档是否已更新，或是否有合理的 no-spec-change 原因？
- Required Gates 是否 done、not-required、blocked 或 deferred，并有证据？
- 用户如何验证结果？
- QA evidence 是否记录了命令、结果、阻塞和残余风险？
- 是否有需要回写的 pitfall、pattern 或 decision？

如果这些问题无法回答，不能把任务标为完成。
