# boundary 输出检查清单

调用 `kk-task-kickoff` 后，至少检查：

1. 如果用户最初没有显式写 skill 名，这次需求是否已经被正确当作“隐式 kickoff”处理
2. 本地 active boundary 是否已经自动设置完成
3. boundary 是否写清 `Allowed Files` 与 `Forbidden Files`
4. `Functional Non-goals` 是否足够防止范围漂移
5. `GStack Required Flow` 是否按固定顺序写清 `requirement-brief -> plan-ceo-review -> requirement-freeze/prototype-freeze -> plan-eng-review -> domain-spec-readiness -> implement -> qa/qa-only`
6. `Required Gates` 是否写清 data-access、data-query、prototype-logic-extraction、subagent-plan、doc-backfill 的状态、owner、required_before、evidence 和 done_criteria
7. 如果涉及数据源、接口、查数、字段口径、SQL、看板或跨系统复用，是否已有 `data-access` gate，且由 `kk-data-kickoff` 产出或计划产出 evidence
8. 如果后端接口、读模型、service 或 snapshot 承接已有前端 / 原型 / mock 业务逻辑，是否已有 `prototype-logic-extraction` gate，且写成 `owner: kk-task-kickoff`、`required_before: plan-eng-review`
9. `prototype-logic-extraction` 若是 `not-required`，是否写清排除原因；若是 `deferred`，是否写清批准来源、风险、删除条件或后续补齐路径
10. 需要逻辑抽取时，boundary 是否列出原型路径、前端路径、fixture 路径、逻辑归属表位置和 golden parity 真源
11. `Subagent Plan` 是否写清 `Mode`；不使用 subagent 时是否有 `not-used` 原因
12. 如果计划使用 subagent，是否写清 role、trigger stage、write scope、forbidden paths、output evidence 与结论回收方式
13. 如果任务要进入开发，前五项是否已经是 `done` 并指向 repo-native evidence
14. `Required Knowledge` 是否覆盖当前任务真正要读的文档
15. `Spec Sync Plan` 是否写清 expected spec targets，以及逻辑抽取 evidence 是否需要同步到模块 spec、接口设计、测试 fixture 或 QA 报告
16. `requirement-brief` 是否落在 `.gstack/requirements/`，且不是只留在聊天里
17. `requirement-freeze` 或 `prototype-freeze` 是否引用 CEO review 后的冻结结论
18. 如果涉及原型或历史 baseline 改动，是否已经声明目标 stack domain spec、来源引用、采纳 / 放弃项和触碰原因；不要新增旧交接证据
19. 如果涉及 stack 后端代码，是否把规范目标写到 `docs/specs/<module>/`，并列出后端测试
20. `Verification` 是否是可执行、可核对的，而不是空泛表述

如果以上任一项缺失，不要把任务当作“已经完成开工”。
