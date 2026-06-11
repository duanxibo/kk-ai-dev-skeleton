---
name: kk-codex-mode
description: |
  协作模式：选择以下三个之一：自主执行、关键确认、手动控制。Use when the user asks about
  "协作模式"、"自主执行"、"关键确认"、"手动控制"、"全自动做完"、"关键地方问我"、"先别改代码"、"现在是什么模式"，
  or when Codex needs to choose how much user confirmation is required for a task.
---

# Codex 协作模式

## Overview

这个 skill 负责解释、选择和记录 KK Dev Skeleton 的三档用户决策介入模式。

它不是三条独立研发流程。模式只决定 Codex 什么时候停下来问用户；所有模式仍然遵守 KK Dev Skeleton 的 boundary、spec、QA、gate recovery 和 git 授权规则。

## 三档模式

- `自主执行`
  用户说目标，Codex 推荐方案并自动执行。适合小需求、明确 bugfix、明确局部改动、可本地验证的工程任务。
- `关键确认`
  Codex 自动准备和推进，但在关键产品口径、架构取舍、数据模型、接口契约、较大范围改动前暂停确认。
- `手动控制`
  Codex 只做分析、方案和风险说明；没有用户明确授权，不改代码、不落长期文档。

内部稳定枚举：

- `自主执行` / `自主执行模式` -> `codex-led`
- `关键确认` / `关键确认模式` -> `checkpoint`
- `手动控制` / `手动控制模式` -> `manual`

## 用户表达识别

识别这些中文表达：

- 自主执行：`自主执行`、`自主执行模式`、`这次自主执行`、`全自动做完`、`你自己决定并做完`
- 关键确认：`关键确认`、`关键确认模式`、`关键地方问我`、`重要决策问我`、`实现前让我确认`
- 手动控制：`手动控制`、`手动控制模式`、`先别改代码`、`只给方案`、`不要自动执行`

如果用户只说“协作模式怎么选”或“切换协作模式”，直接提示三选一：

```text
请选择协作模式：
1. 自主执行：你说目标，Codex 做完。
2. 关键确认：Codex 推进，关键点问你。
3. 手动控制：Codex 只分析，你授权才动。
```

如果可用交互式选择工具，用这三个中文选项展示；否则用普通聊天消息让用户回复模式名或序号。

## 默认与持久化

默认模式：`自主执行`。

本机模式 helper：

```bash
python3 .gstack/scripts/codex_mode.py show
python3 .gstack/scripts/codex_mode.py choices
python3 .gstack/scripts/codex_mode.py set 自主执行
python3 .gstack/scripts/codex_mode.py set 关键确认
python3 .gstack/scripts/codex_mode.py set 手动控制
python3 .gstack/scripts/codex_mode.py clear
```

非技术自然语言说明 helper：

```bash
python3 .gstack/scripts/nontechnical_mode_control.py --raw "这次先别改代码，只给我方案" --format user
python3 .gstack/scripts/nontechnical_mode_control.py --raw "这次关键地方问我，其他你继续推进" --format user
python3 .gstack/scripts/nontechnical_next_step.py --raw "这次全自动做完" --format user
```

`nontechnical_mode_control.py` 只读，只解释本次应按哪个模式执行；它不会写 `.gstack/codex-mode.local.md`，不会创建长期 evidence，不会修改代码，也不会清理允许入仓的敏感配置。只有用户明确要求长期默认模式时，才使用 `codex_mode.py set <模式>`。

模式作用范围：

- 用户说“这次”：只覆盖当前任务，并写入当前 task boundary 的 `Decision Mode` 或 `Autonomy Plan`。
- 用户说“以后默认 / 切换到 / 默认用”：使用 `python3 .gstack/scripts/codex_mode.py set <模式>` 写入本机 gitignored 文件 `.gstack/codex-mode.local.md`。
- 没有本地模式文件时，使用 repo 默认 `自主执行`。

`.gstack/codex-mode.local.md` 只保存本机偏好，不提交到 repo。

## 门禁恢复规则

如果门禁失败，Codex 默认先自行修复可补证据：

- 可自行补：boundary、requirement brief、review 记录、freeze 记录、spec sync、QA 报告、测试、`Subagent Plan`、Required Gates 中的 `not-required` 排除原因。
- 必须问用户：业务口径多解、真实数据权限、生产操作、DB schema 变更、破坏性命令、git workflow action、无法由本地证据证明的结论。
- 不允许为了过门禁编造“已验证”“已确认”“已通过 QA”等结论。

## 安全边界

无论模式如何，以下动作仍需用户明确批准：

- 创建或切换分支、commit、amend、squash、rebase、push、pull、merge、cherry-pick、reset、创建 PR
- 生产部署、生产重启、线上数据修复
- relational database / analytics warehouse schema 变更、写入真实生产数据、破坏性命令
- 写入真实凭证或把本机绝对路径写入长期 repo 文档

`自主执行模式` 可以自动重启本地开发服务，例如 `bash scripts/dev_stack.sh restart`，但不能自动重启生产服务。

## Subagent 与 Goal Mode

- subagent 是并行分工工具。小任务通常不用；大需求、多模块探索、独立 review、互不重叠的实现范围或数据专项分工可以用。
- goal mode 是持续推进工具。目标明确、验收条件清晰、任务可能跨多轮时可以用；方案讨论、手动控制、小改默认不用。
- `自主执行`：中大型任务可自动使用 goal mode，并按 boundary 决定是否使用 subagent。
- `关键确认`：可用 subagent 做探索 / review，可开 goal，但关键决策点暂停确认。
- `手动控制`：默认不开 goal，不启动 worker subagent；除非用户明确同意，只能做 read-only 分析。

## 输出规则

- 切换模式后，用一句话确认当前模式和作用范围。
- 如果用户在同一条消息里同时给出任务和模式，先记录模式，再继续任务 kickoff。
- 如果用户问“模式怎么选”，给三档选择和推荐，不进入代码修改。
- 如果用户要求手动控制，除非后续明确授权，不创建或修改长期 repo 文档。
