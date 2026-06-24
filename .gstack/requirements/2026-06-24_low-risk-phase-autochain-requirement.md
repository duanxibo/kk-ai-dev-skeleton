# 低风险阶段自动串联需求

- 日期：2026-06-24
- Flow Lane：fast-lane
- 状态：ready-for-implementation
- AI 语义复核: yes
- 关联 boundary：`.gstack/task-boundaries/2026-06-24_low-risk-phase-autochain.md`

## 背景

上游协作骨架验证中已修复一个协作体验缺口：低风险任务完成后，如果 phase plan、交付总结或下一步建议里的下一项仍是本地可验证低风险任务，Codex 不应停下来等待用户再说“继续”，而应创建或激活下一段最小任务范围并继续推进。

公开骨架当前已支持“低风险确认后在当前任务内连续推进”，但还缺“完成一个低风险小任务后自动串联下一段低风险任务”的明确规则和回归。

## 需求

- 在公开骨架 AGENTS、kk-* skills 和 framework knowledge 中固化低风险 phase auto-chain。
- `nontechnical_continue.py` 对已完成任务输出可审计的自动串联状态。
- `nontechnical_delivery_summary.py` 的下一步建议明确区分低风险自动继续、业务决策等待用户、高风险动作等待授权。
- `natural_language_dev_smoke.py` 增加已完成低风险任务的 auto-chain 回归。

## 本次不做

- 不改 adapter 业务模板、examples、真实项目源码或线上平台协议对象。
- 不实现后台常驻自动执行器。
- 不执行 commit、push、PR、生产、数据库、真实数据、外部服务或破坏性动作。
