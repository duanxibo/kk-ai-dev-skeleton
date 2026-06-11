# 默认项目 Adapter

这个 adapter 是模板。复制到 `adapters/<project-name>/adapter.md` 后，填入项目专属规则。

同目录下的 `runtime.json` 是机器可读配置，供 guard、doctor 和 dashboard helper 判断路径、命令和 gate 触发规则。真实项目复制 adapter 后，必须同时改 `adapter.md` 和 `runtime.json`。

## 项目目标

- 说明这个项目要构建什么。
- 说明主要用户是谁。
- 说明第一个可见成功标准是什么。

## 真源文档

- 产品 spec：
  `docs/specs/`
- API 契约：
  `docs/api/`
- 数据模型：
  `docs/data/`
- UI 行为：
  `docs/ui/`
- 测试口径：
  `docs/testing/`

根据你的项目调整这些路径。

机器可读路径在：

- `adapters/default/runtime.json`

如果你的真实项目使用 `src/`、`packages/`、`services/` 或 monorepo 结构，把对应前缀写入 `runtime.json` 的 `paths` 区块。

## 实现路径

- 前端：
  `app/frontend/`
- 后端：
  `app/backend/`
- 脚本：
  `scripts/`
- 测试：
  `tests/`
- Fixtures：
  `fixtures/`

## Forbidden Paths（禁止路径）

- `.env`
- `.env.*`
- `secrets/`
- 生产部署配置
- 生成的构建产物
- 真实客户数据

## Forbidden Scope Mapping（禁止业务范围映射）

自然语言里出现“不要动某个业务范围”时，Codex 可以把业务词映射成 forbidden paths。

默认映射文件：

- `adapters/default/forbidden-scopes.json`

默认只提供一个中性示例：

- `受限业务模块` -> `app/restricted-module/**`

真实项目应复制并改写这份配置，不要把某个私有项目的模块名写进 framework core。

## 命令

```bash
python3 .gstack/scripts/gstack_doctor.py check
python3 .gstack/scripts/gstack_dashboard.py show
python3 .gstack/scripts/natural_language_dev_smoke.py
python3 .gstack/scripts/spec_sync_guard.py
python3 scripts/init_project.py --adapter <project-slug> --create-adapter
```

补充项目专属命令：

```bash
# 示例
npm test
npm run build
bash scripts/dev_stack.sh check
```

## 数据和 API 规则

- 除非用户明确授权数据 scope，否则不要连接真实数据。
- 不要暴露密钥或原始敏感字段。
- 不要让前端代码依赖临时数据库查询。
- 实现前先定义 API 输入、输出、错误、空态和授权行为。

## 发布规则

- Git workflow actions 必须获得用户明确批准。
- 生产部署必须获得用户明确批准。
- 回滚必须获得用户明确批准，并且要有具体目标。

## Required Gates（必要门禁）

只在相关时使用 gates：

- `data-access`
- `data-query`
- `prototype-logic-extraction`
- `subagent-plan`
- `doc-backfill`
- `data-knowledge-sync`
- `ui-interaction-qa`

如果某个 gate 不需要，在 task boundary 中记录原因。
