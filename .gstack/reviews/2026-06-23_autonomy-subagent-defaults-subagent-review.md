# 自主推进与 subagent 默认策略 subagent Review

- 日期：2026-06-23
- 类型：read-only reviewer evidence
- 关联 boundary：`.gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md`
- 结论：accepted

## 复核要点

- `我确认 / 可以 / 同意` 不能授权高风险动作，但在 active task 且原话无高风险意图时，应允许 Codex 继续低风险本地闭环。
- `继续做` 不能重新追问目标用户、成功样子等新需求信息；它应读取 active task 并继续下一阶段。
- subagent 使用与否、role、checkpoint、deadline、回收 evidence 属于 Codex 工程调度，不应交给非技术用户选择。
- 高风险短句如“继续同步线上数据”必须进入风险确认，不能被普通 continue 吞掉。

## 集成结论

本轮已把复核点同步到 helper、skill、knowledge、workflow、回归 smoke 和 task boundary。实际使用 subagent 时，main agent 仍负责最终判断、集成、验证和用户答复。
