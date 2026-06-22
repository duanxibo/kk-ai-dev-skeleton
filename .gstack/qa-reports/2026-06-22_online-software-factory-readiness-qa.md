# Online Software Factory Readiness QA

- 任务：升级 KK Dev Skeleton 支持纯线上 AI Software Factory 平台
- 日期：2026-06-22
- Flow Lane：`standard`
- 关联 requirement：`.gstack/requirements/2026-06-22_online-software-factory-readiness-standard-requirement.md`
- 关联 review：`.gstack/reviews/2026-06-22_online-software-factory-readiness-standard-review.md`
- 关联 boundary：`.gstack/task-boundaries/2026-06-22_online-software-factory-readiness.md`
- QA 结论：`pass`

## 验收范围

- 公共线上化协议已落到 `.gstack/designs/2026-06-22_online-software-factory-platform-protocol.md`。
- Framework 文档、default adapter、runtime schema、installer helper 和 plugin adoption 说明已同步 online flow protocol。
- Focused unittest 覆盖协议存在性、default runtime metadata、installer 生成 runtime metadata 和项目专属内容泄漏检查。
- `tests.test_init_project` 已更新到当前 installer V9 API，覆盖 `apply-core`、`rewrite-adapter`、CLI JSON、schema version 和 runtime bundle dry-run。
- 本轮没有 Web UI、API、远程 runner、真实数据、生产、DB 或 git workflow 动作。

## 验证命令

| 命令 | 结果 | 说明 |
| --- | --- | --- |
| `python3 -m json.tool adapters/default/runtime.json` | pass | default runtime JSON 可解析 |
| `python3 -m json.tool adapters/default/runtime_schema.json` | pass | runtime schema JSON 可解析 |
| `python3 -m py_compile scripts/init_project.py` | pass | installer helper 语法可编译 |
| `python3 -m unittest tests.test_init_project` | pass | 14 个 installer V9 API unittest 通过 |
| `python3 tests/test_online_flow_protocol.py` | pass | 5 个 focused unittest 通过 |
| `python3 -m unittest tests.test_init_project tests.test_online_flow_protocol tests.test_productization_hardening tests.test_plugin_update_check` | pass | 34 个核心 unittest 通过 |
| `python3 scripts/init_project.py --adapter default --validate-adapter --report` | pass | adapter metadata / schema guard 通过 |
| `python3 scripts/init_project.py --adapter default --verify-runtime --report` | pass | runtime bundle、Python compile、contract smoke、chat-smoke、nl-smoke、natural-language smoke 均通过 |
| `python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user` | pass | Loop contract smoke 通过 |
| `python3 .gstack/scripts/natural_language_dev_smoke.py --format user` | pass | 非技术自然语言关键路径 smoke 通过 |
| `python3 .gstack/scripts/spec_sync_guard.py` | pass | 无 implementation files；spec sync guard 不阻塞 |
| `python3 -m unittest tests.test_productization_hardening` | pass | 10 个产品化硬化测试通过；旧项目名残留已清理 |
| `python3 -m unittest tests.test_plugin_update_check` | pass | 5 个插件更新检查测试通过 |
| `git diff --check` | pass | diff 无 whitespace error |

## 失败 / 非阻塞记录

- `python3 -m pytest tests/test_online_flow_protocol.py`
  - 结果：`blocked`
  - 原因：当前环境没有安装 `pytest`。
  - 处理：该测试文件使用 `unittest`，已改用 `python3 tests/test_online_flow_protocol.py` 并通过。
- `python3 -m unittest tests.test_init_project`
  - 原结果：`failed-existing-test-drift`
  - 处理：已将测试更新到当前 installer V9 API，并补充 generated schema version / online flow protocol 回归覆盖。
  - 当前结果：`pass`

## 用户可见验收

- 维护者可阅读：
  - `.gstack/designs/2026-06-22_online-software-factory-platform-protocol.md`
  - `.gstack/knowledge/ai-programming-framework.md`
  - `adapters/default/adapter.md`
  - `plugins/kk-dev-skeleton-adoption/README.md`
- 机器可读验收：
  - `adapters/default/runtime.json` 包含 `online_flow_protocol`。
  - `scripts/init_project.py` 生成的 target runtime 也包含 `online_flow_protocol`。
  - `adapters/default/runtime_schema.json` 将 `online_flow_protocol` 纳入 required runtime object。
  - `scripts/init_project.py` 生成的 target runtime schema version 与磁盘 schema 保持 `3`。

## Required Gates

- `data-access`：`not-required`，本轮不涉及真实数据、接口、查数或数据源。
- `prototype-logic-extraction`：`not-required`，本轮不涉及原型 / 前端逻辑迁移。
- `subagent-plan`：`done`，boundary 记录 `Mode: not-used`。
- `doc-backfill`：`done`，公共协议、framework 文档、adapter metadata 和插件说明已同步。

## 残余风险

- 线上 AI Software Factory 平台本身尚未实现；本轮只完成公共协议和骨架 readiness。
- 远程 Codex runner 的隔离、密钥、成本、日志和失败清理仍需平台项目单独设计。
