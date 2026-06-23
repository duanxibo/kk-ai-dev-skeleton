# 自主推进与 subagent 默认策略增强 Review

- 日期：2026-06-23
- 关联 requirement：`.gstack/requirements/2026-06-23_autonomy-subagent-defaults-requirement.md`
- 关联 boundary：`.gstack/task-boundaries/2026-06-23_autonomy-subagent-defaults.md`
- AI 语义复核: yes
- 结论：pass

## 复核结论

这是 framework runtime 能力增强，不是业务功能改动。当前缺口主要在两个地方：

- 确认回复过度保守，容易把低风险“同意继续”转成再次确认范围。
- 执行计划、skill 规则和自然语言回归没有把 subagent 调度作为 Codex 工程自决能力显式固化。

## 工程建议

- 修改自然语言 helper 的 deterministic 输出和 smoke 断言，确保新会话能稳定继承行为。
- 修改 `kk-task-kickoff`、`kk-natural-language-dev`、`kk-subagent-orchestrator` 和 framework knowledge，使规则不只存在于脚本输出。
- 同步到 `kk-ai-factory`，避免新平台项目继续使用旧 runtime。

## 验证计划

- `python3 -m py_compile` 覆盖修改脚本。
- `python3 .gstack/scripts/nontechnical_confirmation_response.py --raw "我确认" --format json/user`
- `python3 .gstack/scripts/nontechnical_continue.py --raw "继续做" --format user`
- `python3 .gstack/scripts/nontechnical_execution_plan.py ... --format json/user`
- `python3 .gstack/scripts/nontechnical_intent_router.py --raw "继续同步线上数据" --format json`
- `python3 .gstack/scripts/natural_language_dev_smoke.py --format user`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `git diff --check`
