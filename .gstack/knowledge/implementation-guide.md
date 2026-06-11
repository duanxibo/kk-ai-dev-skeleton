# 实现指南

实现任务按以下顺序推进。

1. 读取 `.gstack/knowledge/CODEMAP.md`。
2. 读取 `.gstack/knowledge/doc-placement.md`。
3. 读取 active adapter。
4. 创建或更新具体 task boundary。
5. 补齐所选 lane 需要的 required flow evidence。
6. 读取相关真源文档。
7. 只在 allowed paths 内实现。
8. 运行 adapter 定义的相关测试或检查。
9. 写 QA evidence。
10. 运行 `python3 .gstack/scripts/spec_sync_guard.py`。
11. 记录可复用 pitfalls、rules 或 learnings。

## Flow Lanes（流程通道）

- `fast-lane`：小、明确、低风险、可本地验证。
- `standard`：普通功能或 bug 任务，通常涉及多个文件或 spec。
- `discovery`：产品或架构不清晰。先澄清并 freeze，再进入实现。

## Required Gates（必要门禁）

在 boundary 中声明 gates。常见 gates：

- `data-access`
- `data-query`
- `prototype-logic-extraction`
- `subagent-plan`
- `doc-backfill`
- `data-knowledge-sync`
- `ui-interaction-qa`

如果某个 gate 不需要，写明原因。

## 用户可见任务

UI、HTML、dashboard、可视化或生成产物任务必须说明：

- 用户应该看到什么
- 哪些动作必须可用
- 如何打开页面或产物
- 如何刷新或重新生成
- 必须验证交互，而不只是确认文件存在
