# kk-task-kickoff 工作流映射

这个 skill 对应的 prompt 真源是：

- `.gstack/templates/ai-task-kickoff.template.md`

使用映射：

- 用户只是想提醒 AI “先读入口文档”：
  参考模板中的“最短版”
- 用户没有提 skill 名，但直接在描述新需求、正式实现、bug 修复或跨层任务：
  也按本 skill 处理，视为隐式 kickoff
- 用户要启动正式工程任务：
  参考“标准完整版”或“研发任务版”
- 用户要启动产品 / 基线任务：
  参考“产品任务版”
- 用户要启动 bug 修复：
  参考“Bug 修复版”

skill 的职责不是原样复读整份模板，而是：

1. 选对模板场景
2. 读对仓库入口和相关真源
3. 形成当前任务的 boundary 或明确说明无需更新 boundary 的原因
4. 在 boundary 中声明 `Required Gates`，由本 skill 统一判断是否需要 `data-access`、`data-query`、`prototype-logic-extraction`、`doc-backfill` 等专项 gate
5. 如果需要 `data-access`，调度 `kk-data-kickoff` 产出 gate evidence；如果需要复杂查数，再由 `kk-data-kickoff` 调度 `kk-data-query`
6. 如果需要 `prototype-logic-extraction`，本 skill 必须把 gate 写入 boundary：`owner: kk-task-kickoff`、`required_before: plan-eng-review`；数据专项只能协助发现，不能把 owner 改成 `kk-data-kickoff`
7. boundary 可以早于 `plan-eng-review` 先以 `planned` 建立；逻辑抽取 evidence 必须在进入 `plan-eng-review` 前补齐为 `done / blocked / deferred`
8. 如有具体 boundary 落地，自动完成本地 active boundary 设置，不要求用户手动执行脚本
