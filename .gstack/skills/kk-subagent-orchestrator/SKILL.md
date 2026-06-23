---
name: kk-subagent-orchestrator
description: |
  KK Dev Skeleton 任务需要判断、规划或使用 Codex subagent 时使用。适用于复杂需求拆解、
  plan review、并行读代码、独立评审、分范围实现、QA、文档治理和“这次要不要开 subagent”的判断。
  它负责先更新 active boundary 的 Subagent Plan，再按读/评审/执行/治理四类模式拆分任务并回收证据。
---

# Subagent Orchestrator

## Overview

这个 skill 把 Codex subagent 能力接入 KK Dev Skeleton 固定研发流程。

它不鼓励“多开几个 AI 一起写代码”。它要求 main agent 先判断当前阶段、边界和写范围，再决定是否使用 subagent。

## When To Use

优先使用：

- 用户明确提到 subagent、多 agent、并行 agent、代理分工
- `requirement-brief`、`plan-ceo-review`、`plan-eng-review` 需要多个视角并行读证据
- 开发任务能拆成互不覆盖的写范围
- `review`、`qa-only` 或文档治理需要独立检查
- 不确定这次是否应该使用 subagent，需要做判断并写入 boundary

通常不用：

- 单文件小修
- 没有独立验证面的小文档改动
- main agent 的下一步被某个结果强阻塞，自己直接做更快

## Required Reading

1. 当前 active boundary
2. `.gstack/templates/subagent-plan.template.md`
3. `.gstack/workflows/subagent-collaboration.md`

如果任务尚未 kickoff，先使用 `kk-task-kickoff` 建 boundary。

## Workflow

1. 判断当前阶段：
   `requirement-brief / plan-ceo-review / requirement-freeze / plan-eng-review / domain-spec-readiness / implement / review / qa`
2. 更新 active boundary 的 `## Subagent Plan`：
   - 小任务写 `Mode: not-used` 和原因
   - 复杂任务写 `explore / review / execute / governance / mixed`
   - 用户反馈“没看到使用 subagent / 需要用户说继续太频繁 / 没有为用户做好决策”时，默认把这视为协作体验缺口；除非任务确实是单文件小改或没有独立 review surface，至少规划一个 read-only explorer / reviewer。
3. 为每个 subagent 写清：
   - role: `explorer / reviewer / worker`
   - task
   - write scope
   - forbidden paths
   - required inputs
   - output evidence
4. 只有在用户请求、当前任务确实需要，或协作体验反馈显示需要独立探索 / 评审时才启动 subagent。
5. worker 必须是互不重叠的写范围，并明确告诉它：
   - 不是独自在仓库里工作
   - 不要回滚别人改动
   - 只改自己负责的路径
   - 最终列出改过的文件
6. explorer / reviewer 默认 read-only。
7. subagent 完成后，main agent 必须整合结论：
   - 需要长期保存的，写入 `.gstack/reviews/`、`.gstack/qa-reports/`、`.gstack/decisions/`、`.gstack/learnings/` 或相关 spec
   - 更新 boundary 中对应 subagent 的 status
   - 不把重要结论只留在聊天里

## Decision Rules

- 用 subagent 做探索：
  多个模块、多个文档源、历史 evidence 可以独立读取时使用。
- 用 subagent 做评审：
  需要不同视角挑问题时使用，例如 CEO、ENG、QA、文档覆盖。
- 用 subagent 做执行：
  只有写范围能清楚切开时使用。
- 用 subagent 做治理：
  diff 已经较大，需要反查文档、QA、learning、pitfall 缺口时使用。
- 不用 subagent：
  任务小、写范围强耦合、下一步结果会阻塞主线、同步成本大于收益。
  不能把“用户没指定 subagent 角色 / 没要求并行 / 没给 checkpoint”当作不用的理由；这些由 Codex 决定。

## Output Rules

- 每次正式任务的 boundary 都必须有 `Subagent Plan`
- 不使用 subagent 也要写 `Mode: not-used` 和原因
- 用户已经反馈“没看到使用 subagent”时，如果仍不使用，必须写清具体工程原因，例如单文件小改、无独立评审面、或当前阶段结果会阻塞所有子任务
- 使用 subagent 时，main agent 仍然负责最终判断、集成、验证和用户答复
- subagent 产物必须回收到 repo-native evidence 或最终集成说明
- 不允许把 subagent 的猜测直接写成 QA 通过、接口真源或业务结论
