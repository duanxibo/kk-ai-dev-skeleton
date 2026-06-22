# Target-aware doctor fast-lane review

- 主题：目标仓库 doctor 不应检查骨架源仓库发布文档
- 日期：2026-06-22
- Reviewer：Codex
- Flow Lane：`fast-lane`
- 关联 requirement：`.gstack/requirements/2026-06-22_target-aware-doctor-fast-lane-requirement.md`
- 关联 boundary：`.gstack/task-boundaries/2026-06-22_target-aware-doctor.md`
- AI 语义复核：`yes`

## 结论

- 推荐结论：`pass`
- 是否允许进入实现：是
- 复核说明：问题根因来自 doctor 未复用安装器已有的 skeleton source / target repo 分层，属于低风险协作脚本修复。

## CEO 视角检查

- 用户目标是否明确：通过。
- 用户期望的可见变化是否明确：通过，目标仓库 doctor 不再被源仓库发布文档阻塞。
- 是否把“筛选 / 排序 / 搜索 / 操作入口 / 看不到页面变化”误解成了 CLI 参数或静态输出：否。
- 是否有多个合理产品方向需要用户选择：否。
- 本次是否控制在最小可交付范围：通过。
- 明确不做：不进入线上平台业务开发，不改变用户本机 skill 清理策略，不提交代码。

## ENG 视角检查

- 改动路径是否清晰：通过。
- 实现表面：CLI 诊断行为、定向测试、协作文档。
- 若本次是 HTML / 前端 / 可视化任务，是否已有验收 URL、刷新方式和交互验证计划：不适用。
- 是否涉及接口、数据模型、持久化或跨模块契约：否。
- 是否需要 subagent：否，小范围脚本修复。
- 是否需要 goal mode：否。

## Spec Sync Check

- Spec Impact：updated。
- Expected Spec Targets：`.gstack/knowledge/ai-programming-framework.md`。
- If Not Required, Why：不适用。

## 验证计划

- 运行 doctor 脚本 Python compile。
- 运行新增目标仓库模式单元 / 集成回归。
- 运行现有产品化 hardening 测试，确保源仓库发布文档检查仍被覆盖。
- 运行安装器 validate / verify runtime smoke。
- 将更新后的 doctor 同步到 `kk-ai-factory` 并运行目标项目 doctor 验证。
- 运行 `python3 .gstack/scripts/spec_sync_guard.py`。

## 风险与退出条件

- 如果需要修改 runtime bundle 覆盖策略、真实项目结构或 git workflow，退出 fast-lane。
- 如果目标项目缺失 portable core 本身，doctor 仍应失败；本次只移除 source-only 文档误报。
