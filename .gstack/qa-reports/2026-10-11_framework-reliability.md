# 框架可靠性与轻量流程 QA

## 改动
- adapter 加载默认 strict，先做类型和 repo-relative 路径检查；显式诊断回退不带业务路径。
- 低风险 fast-lane 可使用 --compact-evidence 合并记录；QA 必须填写实际命令和结果。
- 完成任务后需要核对下一项授权；独立建议不自动执行。
- 保留已有源码布局；升级报告 preserved_differences 和双方 SHA-256，保留现有文件。
- PR CI 覆盖 Python 3.11/3.12 单元和集成测试、adapter 校验、契约与自然语言旅程。

## 实际验证
- Python 3.12.14：python3 -m unittest discover -s tests -v：63 tests，OK。
- python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json：36 checks，0 failed，status ok。
- python3 .gstack/scripts/natural_language_dev_smoke.py --format json：74 checks，overall ok。
- python3 scripts/init_project.py --adapter default --validate-adapter --format json：退出 0。
- python3 .gstack/scripts/spec_sync_guard.py：通过；默认 adapter 只将 stack/default 路径识别为实现，当前框架脚本 diff 不进入业务实现阻断分支。
- git diff --check：通过。

## 回归范围
- 缺失、损坏、错误类型、不完整配置、越界路径、显式兼容回退。
- compact 记录单文件输出、阶段证据、缺失 review、standard 不可绕过、QA 命令与结果要求。
- 已完成任务不能凭“继续做”自动授权独立建议；未完成任务可在范围内继续。
- 升级时差异报告不覆盖用户定制。

## 限制
- 当前环境仅实测 Python 3.12；3.11 交给 PR CI。
- 记录与 guard 不代替权限隔离或独立审查；本轮 review 来自实现 agent。
- SHA-256 差异不能自动区分旧版本和用户定制；需要审查后升级。
- 未重构整个 Loop，未操作生产、数据库或合并 main。
