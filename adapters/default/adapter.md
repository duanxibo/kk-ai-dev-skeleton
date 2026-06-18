# 默认项目 Adapter

这个 adapter 是模板。复制到 `adapters/<project-name>/adapter.md` 后，填入项目专属规则。
同目录下的 `runtime.json` 是机器可读配置，供 guard、doctor、dashboard 和 Loop runtime helper 判断路径、命令和 gate 触发规则。真实项目复制 adapter 后，必须同时改 `adapter.md` 和 `runtime.json`。

## 项目目标

- 说明这个项目要构建什么。
- 说明主要用户是谁。
- 说明第一个可见成功标准是什么。

## 真源文档

- 产品 spec：`stack/<project>/specs/`
- API 契约：`stack/<project>/specs/api/`
- 数据模型：`stack/<project>/specs/data/`
- UI 行为：`stack/<project>/specs/ui/`
- 测试口径：`stack/<project>/specs/testing/`
- 前置蓝图：`blueprint/`
- 历史归档：`archive/`
- 共享输入：`shared/`

根据你的项目调整这些路径。机器可读路径在 `adapters/default/runtime.json`。

## 实现路径

默认初始化会创建 `stack/<project>/`。如果真实项目已有 `src/`、`prisma/`、`e2e/`、`packages/`、`services/` 或其它根目录代码，不要让 Codex 静默接受散落一级目录的最终形态；先生成迁移计划，再分步迁入项目自己的正式实现路径。

推荐默认：

- 前端：`stack/<project>/src/frontend/`
- 后端：`stack/<project>/src/backend/`
- 脚本：`stack/<project>/scripts/`
- 测试：`stack/<project>/tests/`
- Fixtures：`stack/<project>/fixtures/`

## 命令

```bash
python3 scripts/init_project.py --adapter default --detect
python3 scripts/init_project.py --adapter default --plan
python3 scripts/init_project.py --adapter default --verify --report
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --apply --dry-run
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --apply
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --apply-core --dry-run
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --apply-core
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --apply-runtime --dry-run --report
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --apply-runtime --report
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --rewrite-adapter --dry-run
python3 scripts/init_project.py --repo-root /path/to/project --project-name "Example" --adapter default --rewrite-adapter
python3 scripts/init_project.py --adapter default --validate-adapter --report
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --validate-adapter --report
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --verify --verify-core --report
python3 scripts/init_project.py --repo-root /path/to/project --adapter default --verify-runtime --report
python3 scripts/init_project.py --adapter default --pilot --report
python3 scripts/init_project.py --adapter default --pilot --pilot-output /tmp/adapter-pilot --report
python3 .gstack/scripts/gstack_loop.py plan --format user
python3 .gstack/scripts/gstack_loop.py eng-review --format user
python3 .gstack/scripts/gstack_loop.py subagents --format user
python3 .gstack/scripts/gstack_loop.py repair-loop --dry-run --format user
python3 .gstack/scripts/gstack_loop.py write-back --dry-run --format user --evidence .gstack/scripts/gstack_loop.py
python3 .gstack/scripts/gstack_loop.py authorize --raw "继续做" --format user
python3 .gstack/scripts/gstack_loop.py chat-smoke --format user
python3 .gstack/scripts/gstack_loop.py nl-smoke --format user
python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user
python3 .gstack/scripts/gstack_doctor.py check
python3 .gstack/scripts/natural_language_dev_smoke.py --format user
python3 .gstack/scripts/spec_sync_guard.py
```

## Loop Runtime Capabilities

- Chat-first execution protocol for natural-language goals.
- Stage skill routing, stage state machine, controlled local verification, and explicit stage write-back.
- ENG review decisioner: Codex owns technical choices, users own business choices and high-risk authorization.
- Subagent orchestration protocol with checkpoint, deadline, retry, result schema, and evidence collection.
- Test-repair loop protocol: failure classification, local repair guidance, rerun order, and QA evidence policy.
- Chat authorization classifier for continue / confirmation / git / production / database / destructive scopes.
- `chat-smoke`, `nl-smoke`, and `gstack_loop_contract_smoke.py` for deterministic regression evidence.

## Forbidden Paths（禁止路径）

- `.env`
- `.env.*`
- `secrets/`
- 生产部署配置
- 生成的构建产物
- 真实客户数据
- 未经迁移计划批准的根目录业务代码移动
- 未经明确授权写入 `archive/` 的历史材料
- 未经脱敏或授权的 `shared/` 输入文件

## Runtime Bundle 策略

- `apply-core` 只创建缺失的 portable core 文件，保留目标项目已有文件。
- `apply-runtime` 是显式 opt-in：先确保 adapter metadata 和 portable core，再从 skeleton source checkout 复制 allowlisted runtime scripts。
- `verify-runtime` 检查 runtime script 文件、Python compile、Loop contract smoke、chat-smoke 和 nl-smoke。
- runtime bundle 不包含 data-access、SQL、ClickHouse、Metabase、生产、DB、凭证工具或具体项目业务 `stack/`。

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
