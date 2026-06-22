# `.gstack/` 协作层

这个目录是 KK Dev Skeleton 的 repo-native 协作层。

它不是应用业务真源。它告诉人和 AI agent 如何工作：该读哪里、该写哪里、如何定义 task boundary、如何验证结果，以及如何沉淀经验。

## 目录职责

- `knowledge/`
  框架知识、真源路由规则、上下文隔离、QA 维度和可复用 pattern。
- `templates/`
  requirement、review、task boundary、QA、decision、learning 和 gate 模板。
- `scripts/`
  用于自然语言路由、dashboard 生成、doctor 检查和 guards 的确定性 helper。
- `skills/`
  封装可重复工作流的 `kk-*` skills。
- `workflows/`
  协作流程文档。
- `task-boundaries/`
  具体任务边界。
- `requirements/`
  需求 brief 和 freeze。
- `designs/`
  设计过程产物、架构调整计划、原型逻辑抽取设计和线上平台协议。
- `reviews/`
  评审证据。
- `qa-reports/`
  QA 和验收证据。
- `decisions/`
  决策记录。
- `migrations/`
  迁移计划、目录重构记录和 framework core 升级计划。
- `learnings/`
  可复用经验。
- `rules/`
  长期规则和 pitfalls。

## 默认阅读顺序

1. `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
2. `.gstack/knowledge/CODEMAP.md`
3. `.gstack/knowledge/doc-placement.md`
4. `.gstack/knowledge/context-isolation.md`
5. `.gstack/knowledge/ai-programming-framework.md`
6. `.gstack/designs/2026-06-22_online-software-factory-platform-protocol.md`
7. `.gstack/task-boundaries/CURRENT.md`
8. `adapters/default/adapter.md`

## 核心检查

```bash
python3 .gstack/scripts/gstack_doctor.py check
python3 .gstack/scripts/gstack_dashboard.py show
python3 .gstack/scripts/natural_language_dev_smoke.py
python3 .gstack/scripts/spec_sync_guard.py
```

## 规则

框架核心保持泛化。项目专属业务规则放进 adapter。

如果 `skills/`、`templates/`、`workflows/` 或 `scripts/` 引用了某个文档，该文档必须随骨架提供；如果引用的是具体项目资源，必须明确标记为 adapter-provided。
