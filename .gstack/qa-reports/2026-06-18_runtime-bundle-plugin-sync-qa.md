# Runtime Bundle Plugin Sync QA

- 日期：2026-06-18
- 任务：同步 TianGong 增强后的公共骨架与 Codex 插件
- 关联 requirement：`.gstack/requirements/2026-06-18_runtime-bundle-plugin-sync-fast-lane-requirement.md`
- 关联 review：`.gstack/reviews/2026-06-18_runtime-bundle-plugin-sync-fast-lane-review.md`
- 关联 boundary：`.gstack/task-boundaries/2026-06-18_runtime-bundle-plugin-sync.md`
- 结论：`pass`

## 覆盖范围

- adapter installer V9：portable core、explicit runtime bundle、schema guard、pilot、runtime smoke。
- default adapter metadata：`adapter.md`、`runtime.json`、`core_manifest.json`、`runtime_schema.json`。
- Loop runtime：`gstack_loop.py`、`gstack_loop_contract_smoke.py`、chat-smoke、nl-smoke。
- Codex plugin：仓库插件源与个人本地插件源。
- repo-native 过程产物：requirement、review、boundary、QA、目录 README。

## 验证结果

| 命令 | 结果 | 说明 |
| --- | --- | --- |
| `python3 -m py_compile scripts/init_project.py .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py` | pass | 新增/同步脚本可编译 |
| `python3 scripts/init_project.py --adapter default --detect --format json` | pass | core、portable core、runtime bundle 均完整 |
| `python3 scripts/init_project.py --adapter default --apply-runtime --dry-run --report` | pass | dry-run 显示 adapter、portable core、runtime bundle 已存在 |
| `python3 scripts/init_project.py --adapter default --validate-adapter --report` | pass | adapter metadata 与 runtime schema guard 通过 |
| `python3 scripts/init_project.py --adapter default --verify --verify-core --verify-runtime --report` | pass | portable core、doctor、natural-language smoke、spec sync、runtime bundle、Python compile、loop smoke 全部通过 |
| `python3 scripts/init_project.py --adapter default --pilot --report` | pass | 临时目标项目可完成 apply、apply-core、apply-runtime、rewrite 和 verification |
| `python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json` | pass | 36 项契约检查通过，历史 source-only boundary fixture 在 portable runtime 中安全跳过 |
| `python3 .gstack/scripts/gstack_loop.py chat-smoke --format json` | pass | chat-first Loop 端到端 smoke 通过 |
| `python3 .gstack/scripts/gstack_loop.py nl-smoke --format json` | pass | 真实自然语言入口 dry-run smoke 通过 |
| `python3 .gstack/scripts/natural_language_dev_smoke.py --format user` | pass | 非技术开发关键路径检查通过 |
| `python3 .gstack/scripts/spec_sync_guard.py` | pass | 本轮无应用 implementation / backend 变更，spec sync guard 不阻塞 |
| `python3 ../TianGong/.gstack/scripts/spec_sync_guard.py` | pass | TianGong 源仓已有增强 diff 的 guard 不阻塞 |
| `python3 <plugin-creator>/scripts/validate_plugin.py plugins/kk-dev-skeleton-adoption` | pass | 仓库插件源结构校验通过 |
| `python3 <plugin-creator>/scripts/validate_plugin.py ~/plugins/kk-dev-skeleton-adoption` | pass | 个人本地插件源结构校验通过 |
| `python3 -m py_compile plugins/kk-dev-skeleton-adoption/scripts/check_update.py ~/plugins/kk-dev-skeleton-adoption/scripts/check_update.py` | pass | 插件更新提醒脚本可编译 |
| `codex plugin add kk-dev-skeleton-adoption@personal` | pass | 插件已从 personal marketplace 重新安装 |
| `codex plugin list` | pass | `kk-dev-skeleton-adoption@personal` 显示为 installed, enabled，版本为 `0.1.0+codex.20260618051113` |
| `python3 <plugin-creator>/scripts/validate_plugin.py <installed-cache-plugin>` | pass | 安装后的插件 cache 结构校验通过 |
| `git diff --check` | pass | diff 无 whitespace error |

## 插件同步证据

- 仓库插件源：`plugins/kk-dev-skeleton-adoption`
- 个人本地插件源：`~/plugins/kk-dev-skeleton-adoption`
- personal marketplace source：`~/.agents/plugins/plugins/kk-dev-skeleton-adoption`
- 最终插件版本：`0.1.0+codex.20260618051113`
- 发布动作：已执行 `codex plugin add kk-dev-skeleton-adoption@personal`。
- 本轮未执行 marketplace upgrade、远端发布、commit、push 或 PR。

## 风险与未覆盖项

- 未执行 commit、push、PR、marketplace 发布或插件安装；这些动作需要用户另行明确授权。
- 未连接真实数据、生产环境、数据库或外部服务。
- 已保留旧 `--upgrade-plan` / `--upgrade-apply` 作为 retired vocabulary 说明，不作为可执行升级入口。
- 当前 Codex 线程可能仍持有旧插件缓存；新线程或重新加载插件后才会读取刷新后的 manifest cachebuster。
