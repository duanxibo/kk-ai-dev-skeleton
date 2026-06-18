# .gstack/scripts

本目录保存 KK Dev Skeleton 可随项目复制的本地协作脚本。

- `gstack_loop.py`：自然语言开发闭环 runner。
- `gstack_loop_contract_smoke.py`：Loop 契约与安全边界 smoke。
- `natural_language_dev_smoke.py`：非技术用户开发路径 smoke。
- `spec_sync_guard.py`：实现、boundary、spec 与 QA 同步检查。
- `codex_mode.py` / `use_boundary.sh`：本地协作模式与 active boundary 辅助工具。

这些脚本不连接生产系统、不写真实数据、不执行 git workflow action。目标项目安装 runtime bundle 时应使用 `scripts/init_project.py --apply-runtime`，并用 `--verify-runtime --report` 留下验证证据。
