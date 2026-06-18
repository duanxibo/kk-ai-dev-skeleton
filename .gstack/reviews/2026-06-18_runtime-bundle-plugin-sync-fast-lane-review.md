# Runtime Bundle Plugin Sync Fast-lane Review

- 主题：同步 TianGong 增强后的公共骨架与 Codex 插件
- 日期：2026-06-18
- Reviewer：Codex
- Flow Lane：`fast-lane`
- 关联 requirement：`.gstack/requirements/2026-06-18_runtime-bundle-plugin-sync-fast-lane-requirement.md`
- 关联 boundary：`.gstack/task-boundaries/2026-06-18_runtime-bundle-plugin-sync.md`
- AI 语义复核：
  `yes`

## 结论

- 推荐结论：
  `pass-with-notes`
- 是否允许进入实现：
  `是`
- 复核说明：
  本轮是公共骨架和 Codex 插件同步，不改变具体业务产品语义，不接真实数据，不执行发布或 git workflow。

## CEO 视角检查

- 用户目标是否明确：
  `通过`
- 用户期望的可见变化是否明确：
  `通过`
- 是否把“筛选 / 排序 / 搜索 / 操作入口 / 看不到页面变化”误解成了 CLI 参数或静态输出：
  `否`
- 是否有多个合理产品方向需要用户选择：
  `否`
- 本次是否控制在最小可交付范围：
  `通过`
- 明确不做：
  - 不发布 marketplace，不执行 plugin marketplace upgrade / reinstall 命令。
  - 不复制 TianGong 业务资料或数据访问工具。
  - 不改生产、DB、真实数据、外部服务或 git workflow。

## ENG 视角检查

- 改动路径是否清晰：
  `通过`
- 实现表面是否已区分：
  `生成命令 / CLI 参数 + adapter metadata + runtime scripts + Codex plugin skill`
- 若本次是 HTML / 前端 / 可视化任务，是否已有验收 URL、刷新方式和交互验证计划：
  `不适用`
- 是否涉及接口、数据模型、持久化或跨模块契约：
  `否`
- 是否需要 subagent：
  `否，见 Subagent Plan`
- 是否需要 goal mode：
  `否，见 Autonomy Plan`

## Spec Sync Check

- Spec Impact:
  `updated`
- Expected Spec Targets:
  - `scripts/init_project.py`
  - `adapters/default/adapter.md`
  - `adapters/default/runtime.json`
  - `adapters/default/core_manifest.json`
  - `adapters/default/runtime_schema.json`
  - `.gstack/scripts/README.md`
  - `.gstack/knowledge/ai-programming-framework.md`
  - `plugins/kk-dev-skeleton-adoption/README.md`
  - `plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption/SKILL.md`
- If Not Required, Why:
  `not-applicable`

## 验证计划

- 需要运行的测试 / 脚本 / 页面验证：
  - `python3 -m py_compile scripts/init_project.py .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py`
  - `python3 scripts/init_project.py --adapter default --apply-runtime --dry-run --report`
  - `python3 scripts/init_project.py --adapter default --validate-adapter --report`
  - `python3 scripts/init_project.py --adapter default --verify --verify-core --verify-runtime --report`
  - `python3 scripts/init_project.py --adapter default --pilot --report`
  - `python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json`
  - `python3 .gstack/scripts/gstack_loop.py chat-smoke --format json`
  - `python3 .gstack/scripts/gstack_loop.py nl-smoke --format json`
  - `python3 .gstack/scripts/natural_language_dev_smoke.py --format user`
  - `python3 .gstack/scripts/spec_sync_guard.py`
  - `python3 ../TianGong/.gstack/scripts/spec_sync_guard.py`
  - `python3 <plugin-creator>/scripts/validate_plugin.py plugins/kk-dev-skeleton-adoption`
  - `python3 <plugin-creator>/scripts/validate_plugin.py ~/plugins/kk-dev-skeleton-adoption`
  - `git diff --check`
- 用户可见 UI / HTML / 可视化任务必须包含：
  - 本轮不涉及 UI / HTML / 可视化任务。

## 风险与退出条件

- 如果同步过程中发现需要真实数据、生产、DB、对外发布、marketplace 管理或 git workflow，立即停止并询问用户。
- 如果脚本去项目化后 contract smoke 无法在公共骨架通过，先修公共脚本和 adapter metadata，不把 TianGong 专属 fixture 复制进公共骨架。
