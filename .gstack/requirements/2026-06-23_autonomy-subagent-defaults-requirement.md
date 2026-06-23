# 自主推进与 subagent 默认策略增强需求

- 日期：2026-06-23
- Flow Lane：fast-lane
- 状态：ready-for-implementation
- AI 语义复核: yes
- 关联 boundary：`.gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md`

## 背景

用户反馈新项目开发过程中几乎看不到 subagent 被使用，而且需要用户频繁回复“继续”，说明公开骨架没有把“工程自决”和“subagent 调度”变成足够强的默认能力。

## 需求

- 自主执行模式下，Codex 应在已声明的任务边界内连续推进本地可证明事项，不要每个内部阶段都停下来等用户说“继续”。
- 工程实现顺序、测试组合、门禁恢复、文档同步和 subagent 调度由 Codex 决策；用户只确认业务口径、产品 / 设计多解、真实数据、生产、数据库、破坏性命令和 git workflow 授权。
- 确认回复 helper 应区分“低风险继续推进”和“高风险授权”；一句“我确认 / 可以”不能授权高风险动作，但也不应阻止低风险本地闭环继续。
- 复杂任务执行计划应显式说明 subagent / 并行复核策略，避免新会话把 subagent 选择继续甩给用户。

## 本次不做

- 不改目标业务项目实现。
- 不实际接入后台常驻 agent 服务。
- 不执行 commit、push、PR、生产、数据库、真实数据或破坏性动作。
