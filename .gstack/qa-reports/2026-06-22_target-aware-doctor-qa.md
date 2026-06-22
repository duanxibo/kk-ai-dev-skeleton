# Target-aware doctor QA

- 日期：2026-06-22
- 任务：`.gstack/task-boundaries/2026-06-22_target-aware-doctor.md`
- 结论：pass

## 验收目标

- 骨架源仓库继续检查完整 partner / plugin / marketplace / setup 发放清单。
- 安装后的目标仓库只检查 portable core、adapter metadata 和 runtime essentials。
- 目标仓库不再因为缺少 source-only 发布资料导致 doctor fail。

## 验证命令

| 命令 | 结果 | 说明 |
| --- | --- | --- |
| `python3 -m py_compile .gstack/scripts/gstack_doctor.py` | pass | doctor 脚本语法通过 |
| `python3 -m unittest tests.test_gstack_doctor_target_mode tests.test_productization_hardening` | pass | 11 个定向回归通过 |
| `python3 -m unittest discover -s tests` | pass | 48 个测试通过 |
| `python3 .gstack/scripts/gstack_doctor.py check` | pass-with-warnings | 源仓库 `core-docs` 为 `skeleton-source`，检查 40 个入口文档；剩余 warnings 来自本机 skill 链接提醒 |
| `python3 scripts/init_project.py --adapter default --validate-adapter --report` | pass | adapter metadata 静态验证通过 |
| `python3 scripts/init_project.py --adapter default --verify-runtime --report` | pass | runtime bundle、Python compile、Loop smoke、自然语言 smoke 通过 |
| `python3 .gstack/scripts/spec_sync_guard.py` | pass | 当前 diff 无 implementation 变更阻塞 |
| 目标项目 `python3 .gstack/scripts/gstack_doctor.py check` | pass-with-warnings | `core-docs` 为 `target-repo`，检查 16 个 portable 入口；source-only 发布资料不再要求随目标仓库安装 |

## 目标项目结果

- 修复前：目标项目 doctor 的 `core-docs` 因缺少 partner、plugin、marketplace 和源仓库归档入口而 fail。
- 修复后：目标项目 doctor 的 `core-docs` 通过，并明确输出 `target-repo` 检查模式。
- 目标项目整体状态为 `warn`，非阻塞项为：
  - 目录还不是 git worktree，暂不检查 hooks。
  - 本机 repo-native skills 链接仍指向旧来源。
  - 本机仍存在外部 `tg-*` skill symlink。
  - adapter 声明了 `scripts/dev_stack.sh`，但当前最小 scaffold 还未提供完整开发环境启动入口。

## 覆盖点

- 新增集成测试会在临时目录安装 portable core 和 runtime bundle，重写 adapter，再运行目标仓库 doctor。
- 现有产品化测试继续保证 source-only 发放入口仍属于源仓库完整清单。
- portable target 清单明确排除 source-only 发放资料，避免再次把源仓库发布文档当作业务目标仓库必需文件。

## 残余风险

- 既有目标项目的 runtime 脚本默认采用 preserve-existing 策略，不会自动覆盖旧 `gstack_doctor.py`；已对当前目标项目手动同步修复版脚本。
- 本次没有改变全局 Codex skill 链接清理策略；这些 warnings 不阻塞目标项目继续开发。
