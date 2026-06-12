# 仓库地图

这个文件是代码和文档任务的第一份路由文档。

开始编辑前，先确认：

1. 这次改动归属哪一层。
2. 哪个 adapter 定义了项目专属规则。
3. 哪份真源文档或实现路径适用。
4. 当前任务是否已有 active boundary。
5. 是否存在父目录、全局 skill 或旧项目缓存带来的上下文污染。

高层协作设计先读：

- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
- `.gstack/knowledge/ai-programming-framework.md`

## 分层

### `.gstack/`

协作操作层：skills、scripts、templates、task boundaries、reviews、QA reports、decisions、learnings 和可复用知识。

这一层用于：

- 工作流规则
- AI agent 行为
- requirement 和 review evidence
- QA evidence
- dashboard 和 doctor helper
- 上下文隔离规则
- 可复用经验

不要把应用业务实现放在这里。

优先读：

- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
- `.gstack/README.md`
- `.gstack/entrypoints/product-manager.md`
- `.gstack/entrypoints/engineer.md`
- `.gstack/knowledge/implementation-guide.md`
- `.gstack/knowledge/qa-dimensions.md`
- `.gstack/knowledge/data-access/README.md`

### `adapters/`

项目专属配置和规则。

这一层用于：

- 真源文档路径
- 实现路径
- 技术栈
- 测试命令
- forbidden paths
- 数据、API、部署和回滚规则

### `examples/`

小型示例，用来证明骨架可以脱离原项目复用。

示例只能使用虚构或脱敏数据。

### `tests/`

骨架级检查和 wrapper tests。

### 应用代码

每个使用本骨架的项目都应在 adapter 中定义自己的应用源码路径。默认推荐并由初始化 helper 创建：

- `stack/<project>/src/`
- `stack/<project>/specs/`
- `stack/<project>/tests/`
- `stack/<project>/fixtures/`
- `stack/<project>/scripts/`

已有项目如果在根目录存在 `src/`、`app/`、`prisma/`、`e2e/`、`packages/`、`services/` 或框架配置文件，应先列为迁移候选并生成迁移计划；不要把一级目录散落状态当成初始化后的最终目标。

框架核心不得写死某个业务项目路径，但可以保持 `stack/<project>/` 的可复用布局约束。

## Skill 入口

- `.gstack/skills/kk-natural-language-dev/SKILL.md`
- `.gstack/skills/kk-task-kickoff/SKILL.md`
- `.gstack/skills/kk-codex-mode/SKILL.md`
- `.gstack/skills/kk-doc-sync/SKILL.md`
- `.gstack/skills/kk-doc-lifecycle/SKILL.md`
- `.gstack/skills/kk-doc-backfill/SKILL.md`
- `.gstack/skills/kk-data-kickoff/SKILL.md`
- `.gstack/skills/kk-data-query/SKILL.md`
- `.gstack/skills/kk-subagent-orchestrator/SKILL.md`

## 实现路由

实现任务按以下顺序推进：

1. 读取 active adapter。
2. 读取或创建 task boundary。
3. 读取相关真源文档。
4. 读取 `.gstack/knowledge/context-isolation.md`，确认没有从外部路径或全局 skill 推断项目身份。
5. 确认 required gates。
6. 只在 allowed paths 内实现。
7. 验证并写 QA evidence。

## 公开安全规则

不要把私有项目历史、密钥、生产配置、真实客户数据或未脱敏 fixtures 拷进公开骨架。
