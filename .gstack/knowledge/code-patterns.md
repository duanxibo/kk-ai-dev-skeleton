# Code Patterns

本文件记录跨项目可复用的工程 pattern。具体框架、目录和命令由 adapter 定义。

## 通用原则

- 优先使用项目已有模式，而不是引入新抽象。
- 小改动保持局部；共享行为变化才补共享 helper。
- 数据、API、权限和持久化规则由后端或服务层持有。
- 前端保持轻薄：渲染、请求编排、轻校验、瞬时 UI 状态。
- 测试覆盖按风险扩展：共享契约、跨模块行为和用户可见路径需要更强验证。

## 写回规则

当某个实现方式被重复采用，或能避免下次返工时，补充到这里。

每条 pattern 应包含：

- 适用场景
- 推荐做法
- 不适用场景
- 验证方式
- 相关 adapter 或项目路径

## Codex-facing Internal Helper

- 适用场景：
  对非技术用户保持自然语言入口，同时需要让 Codex 稳定执行探测、计划、应用、验证和报告等重复动作。
- 推荐做法：
  把用户入口写成自然语言接入提示；把确定性执行收敛为 Codex 可调用的 helper，并提供 text / JSON 输出、默认不覆盖的 apply 语义、可复用的 verify 命令编排和脚本级测试。
- 不适用场景：
  不适用于需要真实数据授权、生产操作、数据库 schema 变更或 git workflow action 的自动执行；这些动作仍必须由用户明确授权。
- 验证方式：
  覆盖 helper 的纯函数测试、CLI smoke、旧参数兼容路径、verify 链路和文案反向检索，确认没有把业务用户入口改回命令行优先。
- 相关 adapter 或项目路径：
  `scripts/init_project.py`、`CODEX_ADOPTION_CONNECTOR.md`、`COMPANY_ADOPTION_GUIDE.md`。

## Repo-local Codex Plugin Source

- 适用场景：
  需要把已经稳定的 Codex 工作流包装成可分发源目录，但还不准备安装到个人 marketplace 或组织 marketplace。
- 推荐做法：
  在仓库内创建 `plugins/<plugin-name>/`，保留 `.codex-plugin/plugin.json` 和 `skills/<skill-name>/SKILL.md`；manifest 通过 validator，skill 只描述可复用工作流，不绕过目标仓库的 `AGENTS.md`、adapter、boundary 和 guard。
- 不适用场景：
  不适用于需要立即安装、发布、授权外部服务、提供 MCP server 或 app UI 的场景；这些应另起发布或集成任务。
- 验证方式：
  运行 plugin validator、skill validator、gstack guard、文案反向检索和旧项目上下文检索。
- 相关 adapter 或项目路径：
  `plugins/kk-dev-skeleton-adoption/`、`CODEX_ADOPTION_CONNECTOR.md`。

## Repo-local Marketplace Source

- 适用场景：
  团队已经有可验证的 repo-local plugin source，并需要为公司内部安装、升级和展示准备一个可版本化 marketplace source。
- 推荐做法：
  把 marketplace manifest 放在 `.agents/plugins/marketplace.json`，让 entry 使用 `source.local` 和 repo-root-relative `./plugins/<plugin-name>`；配套写安装 / 升级说明，并用测试验证 marketplace 指向的 plugin manifest 和 skill 文件存在。
- 不适用场景：
  不适用于普通业务用户接入，也不适用于未获授权的本机 Codex 安装动作；`codex plugin marketplace add` 和 `codex plugin add` 仍是明确的 admin / release action。
- 验证方式：
  运行 marketplace structure test、plugin validator、skill validator、marketplace name reader、gstack guard，以及命令行优先文案和旧项目上下文检索。
- 相关 adapter 或项目路径：
  `.agents/plugins/marketplace.json`、`plugins/MARKETPLACE_INSTALL.md`、`tests/test_plugin_marketplace.py`。
