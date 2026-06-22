# Online Software Factory Platform Protocol

- 日期：2026-06-22
- 状态：`active`
- 适用范围：KK Dev Skeleton framework core、project adapter、未来纯线上 AI Software Factory 平台
- 关联 requirement：`../requirements/2026-06-22_online-software-factory-readiness-standard-requirement.md`
- 关联 boundary：`../task-boundaries/2026-06-22_online-software-factory-readiness.md`

## 定位

本协议定义纯线上 AI Software Factory 平台如何消费 KK Dev Skeleton。

目标体验是：用户只使用线上平台提出需求、确认 PRD、查看任务状态、验收结果和审批高风险动作；Codex runner 在受控环境中读取 `ClaimPackage`，把工程事实落回 repo-native evidence，并通过 `StatusEvent` 回写平台。

```text
Online Platform
  -> OnlineDemand
  -> MvpConfirmation
  -> ClaimPackage
  -> Codex Runner
  -> Repo-native Evidence
  -> StatusEvent
  -> Platform Acceptance
```

该协议不是 Web 平台实现，也不是远程 runner 实现。KK Dev Skeleton 只提供协议、adapter、runtime bundle、授权边界、smoke 和 evidence 约定。

## 三方职责

### Online Platform

线上平台负责用户协作面：

- 收集自然语言需求、附件、验收方式、不做范围和风险标记。
- 引导用户完成需求澄清、PRD 确认、架构确认和验收。
- 展示项目状态、阻塞原因、确认队列、测试摘要和交付摘要。
- 生成 `ClaimPackage`，交给受控 Codex runner。
- 接收 `StatusEvent`，并按幂等键去重展示。
- 记录独立授权事件，尤其是 Git、生产、数据库、真实数据、破坏性动作和外部付费动作。

线上平台不直接替代 repo evidence，不静默修改仓库事实，不把用户的一句“可以”泛化成高风险授权。

### Codex Runner

Codex runner 负责工程执行面：

- 校验 `ClaimPackage` 的 revision、checksum、授权边界和 adapter。
- 在隔离工作区读取目标仓库和 adapter。
- 创建或更新 requirement、review、task boundary、Required Gates 和 QA plan。
- 在 active boundary 内执行代码、文档、测试和 QA。
- 失败时先修复本地可证明的问题，超过策略限制后回写 blocked。
- 把进度、确认点、QA 和交付摘要回写为 `StatusEvent`。

runner 不能因为平台发出 claim 就自动获得 Git、生产、数据库、真实数据或破坏性权限。

### Repo Skeleton

KK Dev Skeleton 负责工程真源：

- 保存 requirement、review、boundary、QA、decision 和 learning。
- 提供 adapter：真源路径、实现路径、测试命令、禁触路径、Required Gates 和发布规则。
- 提供 runtime bundle：自然语言入口、dashboard、doctor、loop runtime、授权分类和 smoke。
- 提供 guard：检查实现、文档、测试、boundary 和 evidence 是否对齐。

repo-native evidence 是工程完成的证明；平台状态是用户协作和展示 surface。

## 核心对象

### OnlineDemand

线上需求池中的用户意图。

必填字段：

```yaml
online_demand_id: "需求唯一 ID"
revision: 1
title: "一句话标题"
requester:
  name: "提出人"
  contact: "可选"
audience: "谁会用"
problem: "当前问题或机会"
desired_outcome: "希望完成什么"
first_visible_success: "成功后第一眼看到什么"
acceptance_method: "用户会怎么验收"
non_goals:
  - "本次明确不做什么"
risk_flags:
  real_data: "yes/no/unknown"
  production: "yes/no/unknown"
  database: "yes/no/unknown"
  destructive: "yes/no/unknown"
  git_workflow: "yes/no/unknown"
created_at: "ISO-8601"
```

规则：

- `revision` 在需求正文、验收方式、不做范围或风险标记改变时递增。
- `unknown` 风险不能被 runner 当作授权。
- 附件默认只作为引用；敏感性未知时不得直接读取内容。

### MvpConfirmation

MVP 确认循环的冻结结果。

```yaml
online_demand_id: "关联需求 ID"
mvp_slice: "本轮最小可交付切片"
deferred_items:
  - "明确延后项"
acceptance_checks:
  - "用户实际会做的验收动作"
confirmed_non_goals:
  - "确认不碰范围"
required_confirmations:
  - confirmation_id: "确认项 ID"
    type: "business/real_data/production/database/git/destructive"
    question: "需要用户确认什么"
    status: "pending/confirmed/rejected/not-required"
confirmed_at: "可选时间"
confirmed_by: "可选确认人"
```

规则：

- MVP 确认只确认需求和范围，不授权高风险动作。
- 如果 MVP 切片仍不清楚，不得进入 `ready-for-codex`。

### ClaimPackage

平台交给 Codex runner 的开工包。

```yaml
claim_id: "领取 ID"
online_demand_id: "需求 ID"
source_revision: 1
claim_reason: "ready-for-codex"
repo:
  name: "目标仓库"
  default_branch: "main"
  target_branch: "可选"
adapter:
  name: "default"
  runtime_version: "可选"
workflow:
  workflow_map_stage: "requirement-pool/mvp-confirmation-loop/automated-development-chain/post-launch-loop"
  flow_lane: "fast-lane/standard/discovery"
  expected_surface: "repo-docs/page/api/backend/frontend/unknown"
scope:
  allowed_paths_hint:
    - "建议路径，可为空"
  forbidden_paths:
    - "不能碰的路径或业务范围"
  functional_non_goals:
    - "不做什么"
evidence_targets:
  requirement: ".gstack/requirements/<date>_<topic>.md"
  review: ".gstack/reviews/<date>_<topic>.md"
  boundary: ".gstack/task-boundaries/<date>_<topic>.md"
  qa: ".gstack/qa-reports/<date>_<topic>.md"
authorization:
  local_repo_edits: "allowed/ask-first/not-allowed"
  git_workflow: "not-authorized"
  production: "not-authorized"
  database: "not-authorized"
  real_data_write: "not-authorized"
  destructive: "not-authorized"
payload_checksum: "用于防止领取后内容被静默改写"
issued_at: "ISO-8601"
```

规则：

- `source_revision` 必须等于 runner 领取时看到的 `OnlineDemand.revision`。
- `local_repo_edits: allowed` 只允许 active boundary 内本地实现、文档和验证。
- 平台需求变更后必须生成新 claim 或阻塞事件，不能静默覆盖旧 boundary。

### StatusEvent

runner 回写平台的状态事件。

```yaml
event_id: "事件 ID"
idempotency_key: "claim_id + repo_stage + event_type + attempt"
online_demand_id: "需求 ID"
claim_id: "领取 ID"
actor: "runner/user/system"
event_type: "claimed/kickoff-prepared/stage-started/stage-completed/needs-confirmation/blocked/qa-passed/qa-failed/delivery-ready/reopened/cancelled"
workflow_map_stage: "requirement-pool/mvp-confirmation-loop/automated-development-chain/post-launch-loop"
repo_stage: "requirement-brief/plan-review/requirement-freeze/engineering-review/source-of-truth-readiness/implementation/qa/complete"
status: "ok/pending/blocked/failed/done"
summary_for_user: "给用户看的摘要"
evidence:
  requirement: "可选 repo-relative path"
  review: "可选 repo-relative path"
  boundary: "可选 repo-relative path"
  qa: "可选 repo-relative path"
needs_user_confirmation:
  - confirmation_id: "可选"
    question: "需要确认的问题"
    authorization_type: "business/real_data/production/database/git/destructive"
blocked_reason: "可选"
created_at: "ISO-8601"
```

规则：

- `summary_for_user` 不暴露本机绝对路径、raw secrets、内部命令噪音或长日志。
- `needs_user_confirmation` 只问会改变业务结果或风险级别的问题。
- 平台必须按 `idempotency_key` 去重。

## 状态机

主路径：

```text
draft
  -> needs-triage
  -> mvp-confirming
  -> ready-for-codex
  -> claimed
  -> kickoff-prepared
  -> in-development
  -> qa
  -> ready-for-acceptance
  -> accepted
  -> done
```

旁路状态：

```text
needs-user-confirmation
blocked
deferred
cancelled
reopened
```

## Evidence Mapping

| Platform Object | Repo Evidence | 说明 |
| --- | --- | --- |
| `OnlineDemand` | `.gstack/requirements/` | 用户意图、成功样子、不做范围、风险 |
| `MvpConfirmation` | `.gstack/requirements/` + `.gstack/reviews/` | MVP 切片、取舍、可实现性 |
| `ClaimPackage` | `.gstack/task-boundaries/` | allowed / forbidden / gates / verification |
| `StatusEvent` | boundary stage、review 或 QA 摘要 | 阶段推进、阻塞、确认点 |
| `QaResult` | `.gstack/qa-reports/` | 验证命令、结果、失败修复 |
| `DeliverySummary` | QA report + platform note | 面向用户的交付说明 |
| `PostLaunchFeedback` | 新 `OnlineDemand` 或 reopened demand | 反馈回流 |

## 授权协议

默认 claim 只授权：

- 读取需求。
- 在本地或隔离 runner 工作区准备 repo-native evidence。
- 在 active boundary 允许范围内实现、文档同步和本地验证。
- 生成 QA、交付摘要和状态事件。

必须单独授权：

- 创建 / 切换分支。
- commit、amend、squash、rebase、merge、push、pull、创建 PR。
- 发布、部署、上线、回滚。
- 生产操作、生产重启、线上数据修复。
- 数据库 schema、migration、真实数据写入。
- 删除、reset、回滚、清理文件等破坏性动作。
- 外部付费服务或可能产生费用的调用。

“我确认 / 可以 / 同意”只确认当前低风险方案，不能授权上述高风险动作。

## MVP+ Platform Boundary

如果后续建设纯线上平台，建议 MVP+ 包含：

- 用户登录和项目创建。
- 需求对话、成熟度评分、PRD 生成和用户确认。
- 架构方案生成和用户确认。
- GitHub 仓库绑定或创建。
- 生成 `ClaimPackage`。
- 受控 runner 执行 Codex、测试和修复循环。
- 创建 PR 或 staging deploy 前的独立授权队列。
- QA 摘要、交付说明和用户在线验收。

MVP+ 仍不应包含：

- Kubernetes、多云、复杂企业权限、多模型投票。
- 自动生产数据库变更。
- 无人工审批的生产发布。
- 任意老项目的完全自动深度理解。

## Adapter Requirements

每个项目 adapter 至少要告诉平台和 runner：

- 项目名称和目标。
- 真源文档路径。
- 实现路径。
- 测试、构建、本地启动命令。
- forbidden paths。
- Required Gates。
- 发布和回滚规则。
- 高风险授权策略。

默认 adapter 的 `runtime.json` 应声明 `online_flow_protocol`，使平台知道当前骨架支持哪些对象、状态、evidence mapping 和 non-actions。

## Non-actions

KK Dev Skeleton 不做：

- 不托管 Web 平台状态数据库。
- 不自己创建云端 runner。
- 不保存密钥、token 或生产凭证。
- 不把聚合 dashboard 提交进仓库。
- 不把平台状态当成工程完成证明。
- 不绕过目标仓库 `AGENTS.md`、adapter、boundary 或授权规则。
