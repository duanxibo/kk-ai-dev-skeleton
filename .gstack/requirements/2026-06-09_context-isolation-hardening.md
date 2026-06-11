# Fast-lane Requirement：context-isolation-hardening

- 需求名称：context-isolation-hardening
- 提出人：user
- 日期：2026-06-09
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`autonomous`
- 关联 boundary：`.gstack/task-boundaries/2026-06-09_context-isolation-hardening.md`
- AI 语义复核：
  `yes`

## 需求一句话

- 用户要完成什么：
  修复新骨架使用时把父目录路径、全局 `tg-*` skills 或旧项目上下文误当成当前项目语义的问题。

## 本次必须做

- 明确当前项目身份只来自当前仓库文档、active adapter、task boundary 和用户输入。
- 明确不能从父目录名、绝对路径、全局 skill 列表、兄弟仓库或缓存推断项目名。
- 让 doctor 能提示 `tg-*` 外部 skill symlink 和可疑父路径带来的上下文污染风险。
- 让 skill 同步脚本保留 `kk-*`，并提供显式选项清理旧 `tg-*` symlink。

## 用户可见变化拆解

- 用户期望的可见变化：
  在 DataWorks/ODPS 这类新项目里使用骨架时，agent 不应再把项目称为“天宫”，也不应把 `tg-*` skill 当成当前项目规则来源。

## 本次明确不做

- 不默认删除用户本机仍可能需要的 `tg-*` skills。
- 不改 `kk-*` skill 命名。
- 不执行代码提交流程。
