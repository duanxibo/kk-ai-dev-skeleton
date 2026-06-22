# Online Software Factory Readiness Requirement

- 需求名称：升级 KK Dev Skeleton 支持纯线上 AI Software Factory 平台
- 提出人：用户
- 日期：2026-06-22
- 当前状态：`ready-for-implementation`
- Flow Lane：`standard`
- 协作模式：`autonomous`
- 关联 boundary：`.gstack/task-boundaries/2026-06-22_online-software-factory-readiness.md`
- AI 语义复核：`yes`

## 需求一句话

将上游 dogfood 项目中已经验证的 AI 原生开发流程线上化协议回灌到 KK Dev Skeleton，让本公共骨架成为未来纯线上 AI Software Factory 平台的底层工程协议、runtime bundle 和项目 adapter 基础。

## 背景

用户已经抽离了一份可安装的骨架插件，用于让项目接入 KK Dev Skeleton。近期上游 dogfood 项目继续演进了 AI 原生开发流程地图、线上化协议、GitHub Issue v0 领取协议和 `OnlineDemand / ClaimPackage / StatusEvent` 等对象，但公共骨架还没有完整吸收这些能力。

用户明确同意：不重新抽一份新骨架，先升级现有 `ai-dev-skeleton`，把它作为唯一公共骨架上游。未来的 AI Software Factory 平台应单独立项，消费本骨架提供的协议和 runtime，而不是把平台代码写入骨架仓库。

## 本次必须做

- 在 KK Dev Skeleton 中沉淀可复用的线上化协议，说明线上平台、Codex runner 和 repo-native evidence 的职责边界。
- 更新 `ai-programming-framework`，把 `workflow map / online flow protocol / runner handoff / platform product surface` 纳入 framework core 与 product surface 边界。
- 更新默认 adapter 的人读说明和机器可读 runtime metadata，声明 online flow protocol 能力、对象 schema、状态机、授权边界和平台集成非目标。
- 更新 installer 内置 default runtime / schema，确保后续新项目接入时也继承 online flow protocol metadata。
- 更新插件接入说明，让已安装项目能按最新版骨架生成增量升级计划，而不是重新接入或另起骨架。
- 增加骨架级测试，防止公共骨架缺失线上化协议、默认 runtime 缺少协议声明，或把项目专属 skill 前缀 / 业务路径泄漏进公共协议。
- 写 QA evidence 并运行骨架自检、runtime smoke、spec sync 和相关 unittest。

## 本次明确不做

- 不建设 AI Software Factory 平台 Web UI、API、数据库或远程 runner。
- 不连接 Codex SDK / GitHub API / webhook / 服务器 / 生产环境。
- 不执行 commit、push、pull、创建 PR、发布或 marketplace 安装升级。
- 不复制上游 dogfood 项目的业务 `stack/`、真实数据配置、数据工具或项目专属 skill 规则。
- 不重抽新骨架，不创建第二套公共 skeleton。
- 不覆盖目标项目已有 adapter 或 runtime scripts。

## 用户可见变化

- 维护者能在骨架文档中看到纯线上平台如何消费 KK Dev Skeleton。
- Codex adoption plugin 文档会引导用户走“升级现有骨架能力”的路径。
- `adapters/default/runtime.json` 会暴露 `online_flow_protocol` 机器可读能力，供未来平台或安装器读取。
- 骨架级测试能阻止协议缺失或项目专属内容泄漏。

## 影响面

- 主要路径：
  - `.gstack/designs/`
  - `.gstack/knowledge/ai-programming-framework.md`
  - `adapters/default/adapter.md`
  - `adapters/default/runtime.json`
  - `plugins/kk-dev-skeleton-adoption/`
  - `tests/`
- 数据 / 接口 / 权限：
  不涉及真实数据、生产接口或权限系统实现；只定义协议和授权边界。
- spec impact：
  `updated`

## 冻结结论

本文件同时作为 requirement brief 和 requirement freeze。范围冻结为“升级现有 KK Dev Skeleton 的公共协议、adapter metadata、plugin 文档和测试”，不进入平台实现、不另起骨架、不执行 git workflow。

## 进入实现条件

- active boundary 已记录 allowed / forbidden files、Required Gates、Subagent Plan、Spec Sync Plan 和 Verification。
- standard review 已落到 `.gstack/reviews/2026-06-22_online-software-factory-readiness-standard-review.md`。
