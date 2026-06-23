# KK Dev Skeleton Subagent 协作流程

本文件定义 KK Dev Skeleton 中 Codex subagent 的默认使用方式。

核心原则：

- subagent 是协作分工能力，不是跳过固定研发流程的捷径。
- main agent 始终负责流程、边界、集成、验证和最终答复。
- 每次正式任务都要在 active boundary 写 `Subagent Plan`；不使用也要写 `Mode: not-used` 和原因。
- subagent 的重要结论必须回收到 repo-native evidence，不只留在聊天里。
- 用户反馈“没看到使用 subagent / 需要用户说继续太频繁 / 没有为用户做好决策”时，默认视为协作体验缺口；main agent 应主动评估并优先安排 read-only explorer / reviewer，而不是等待用户指定角色或继续口令。

## 适用阶段

### 需求描述与 CEO Review

适合 `explore` 或 `review`：

- 一个 explorer 查 stack domain spec / 历史 decisions / 必要的 baseline 旧参考
- 一个 reviewer 从 CEO 视角检查范围、目标用户、成功标准和不做什么
- main agent 汇总到 requirement brief、CEO review 或 boundary

### ENG Review 与 Domain Spec Readiness

适合 `explore`、`review` 或 `mixed`：

- 一个 explorer 查数据模型、API、state、pitfalls
- 一个 reviewer 检查架构可执行性、测试路径、风险和迁移成本
- main agent 把结论写回 domain spec、review 或 Spec Sync Plan

### 开发阶段

适合 `execute`，但只在写范围能切开时使用：

- 后端实现、后端测试、前端接入、spec 补齐可以分给不同 worker
- 每个 worker 必须有明确 allowed paths / forbidden paths
- worker 不能回滚别人改动，结束时必须列出 changed files
- main agent 负责合并、冲突处理和最终验证

### Review / QA / 文档治理

适合 `review` 或 `governance`：

- reviewer 检查 diff 风险、SQL / LLM trust boundary、条件副作用、测试缺口
- QA agent 做只读验收报告
- governance agent 从 diff 反查缺失 spec、review、QA、decision、learning
- main agent 只在证据足够时写“已通过”结论

## 不适合使用的情况

- 单文件小修，main agent 直接完成更稳
- 下一个动作被某个结果强阻塞，等待 subagent 会拖慢主线
- 写范围高度耦合，拆分会制造冲突
- 没有明确 evidence 落点

不能因为“用户没有点名 subagent、没有选择 role、没有指定 checkpoint / deadline”而跳过 subagent；这些属于 Codex 的工程调度职责。

## Boundary 写法

优先复制：

- `.gstack/templates/subagent-plan.template.md`

最小有效写法：

```markdown
## Subagent Plan

- Mode: `not-used`
- Reason:
  本次是单文件小修，没有独立探索或评审面。
- Main Agent Owns:
  - 流程控制、实现、验证、最终答复
- Candidate Subagents:
  - name: `none`
    role: `not-used`
    write scope: `none`
    status: `not-used`
- Result Integration:
  无 subagent 产物。
```

复杂任务写法：

```markdown
## Subagent Plan

- Mode: `mixed`
- Reason:
  需求涉及 baseline、后端接口、测试和文档治理，可以拆出独立读写范围。
- Main Agent Owns:
  - active boundary
  - 任务拆分
  - 最终集成和验证
- Candidate Subagents:
  - name: `api-contract-explorer`
    role: `explorer`
    trigger stage: `plan-eng-review`
    write scope: `read-only`
    output evidence: `.gstack/reviews/<date>_<task>-api-contract-review.md`
    status: `planned`
  - name: `backend-test-worker`
    role: `worker`
    trigger stage: `implement`
    write scope: `app/backend/src/test/`
    forbidden paths:
      - `app/backend/src/main/`
    output evidence: changed files + test command output
    status: `planned`
- Result Integration:
  main agent 把 explorer / worker 结果回收到 boundary、review、QA 和相关 spec。
```

## Guard 关系

- `team_flow_guard.py` 会在实现类任务中检查 active boundary 是否包含 `Subagent Plan` 和合法 `Mode`
- `pre_commit_flow_guard.py` 与 `spec_sync_guard.py` 会把 `Subagent Plan` 作为 boundary 必填章节
- 缺失时，guard 会提示使用 `.gstack/templates/subagent-plan.template.md` 或 `$kk-subagent-orchestrator`
