---
name: kk-doc-lifecycle
description: |
  KK Dev Skeleton 项目文档需要做“先同步、再归档”治理时使用。它负责先检查当前文档是否应按代码、
  spec、boundary、验证证据补更新；若文档已脱离当前项目真源或被新真源替代，再执行归档判断与落地。
  适用于“项目空间文档检查”“文档陈旧治理”“归档过期文档”“检查哪些文档该更新或进 archive”这类场景。
---

# Doc Lifecycle

## Overview

这个 skill 负责处理文档生命周期，而不只是单点同步。

它的默认顺序是：

1. 先判断当前文档还能不能继续作为主线真源维护
2. 如果还能维护，优先补更新
3. 只有确认已退出主线、被新真源替代或只剩历史追溯价值时，才归档

如果用户没有明确要求“只出报告 / 先判断”，默认按 execute 路径持续完成高置信度动作，而不是每做一小段就停下来等下一次“继续”。

## When To Use

在这些场景优先使用：

- 用户要求检查项目空间文档是否已脱离当前真源
- 用户想做文档治理、文档清扫、archive 归档或长期文档盘点
- 你怀疑有些文档没有跟上代码 / spec / boundary，想先补同步再决定是否归档
- 项目运行一段时间后，需要对旧说明、旧协作文档、旧入口页做兜底治理

这些场景通常不需要使用：

- 只是一次实现收口，需要补 review / QA / spec，同步目标已经明确
  这类优先使用 `kk-doc-sync`
- 还没建立边界就准备进入正式实现
  这类先回退到 `kk-task-kickoff`

## Required Inputs

优先读取：

- active boundary
- `.gstack/knowledge/doc-placement.md`
- 当前相关真源文档
- 当前 diff、最近实现产物或验证证据
- 用户点名要检查的文档、目录或项目空间范围

如果任务范围很大但没有 boundary，先回退到 `kk-task-kickoff` 补边界，不要直接全仓归档。

## Core Decision

对每份候选文档只允许落到这 5 类之一：

- `keep`
  仍是当前真源或有效入口，保持原位
- `update`
  仍属主线，但内容需要同步更新
- `distill`
  正文不再适合继续维护，但应提炼有效部分迁入 `.gstack/` 或新的真源文档
- `archive`
  已退出主线，只保留历史追溯价值，移入 `archive/`
- `rewrite`
  原文结构已不可信，不适合直接迁移，应新写一份当前版本，再让旧文归档

## Workflow

1. 先判断任务是“检查报告”还是“允许直接执行”
2. 读边界、真源和文档放置规则，确认当前应该信哪一层
3. 对候选文档逐份给出 `keep / update / distill / archive / rewrite`
4. 若能明确补更新路径，优先补当前真源文档，不要因为“旧文没跟上”就直接归档主线知识
5. 只有满足归档门禁时，才把旧文移入 `archive/`
6. 若旧路径仍可能被团队打开，补跳转说明、入口索引或 decision
7. 若发现长期归档判例，再补 `.gstack/knowledge/doc-placement.md` 或 `.gstack/decisions/`

对“项目空间治理”这种大范围执行，默认连续跑完这 3 段，直到没有高置信度后续动作为止：

1. 更新入口、说明、当前真源引用
2. 归档已退出主线的兼容页、备份稿、旧入口页，并修正主线文档里的过时定位说明
3. 清理杂项噪音并做一轮收尾复核

## Archive Gates

执行归档前，至少满足以下条件：

- 已确认它不是当前默认真源
- 已识别替代它的当前真源、入口或新的放置层
- 归档不会让当前任务缺少唯一可用说明
- 需要时已补跳转页、索引或 decision，避免团队继续从旧路径迷路

如果其中任一项拿不准，先落报告或 decision，不要直接归档。

## Output Rules

- 如果用户说“检查一下”，默认输出检查结论和建议动作，不直接大规模移动文件
- 如果用户说“直接归档”或“帮我处理”，允许直接执行高置信度的更新 / 归档动作
- 如果用户没有要求 audit-only，且任务是项目空间治理，默认连续完成高置信度的后续阶段，不需要每一轮都等用户再说“继续”
- 归档不是兜底替代同步；能补真源时优先补真源
- 严禁因为文档没更新就直接把当前主线真源扔进 `archive/`
- 涉及 QA、review、验收结论时，仍服从 `kk-doc-sync` 的证据门禁

## Template Source

这个 skill 的流程真源是：

- 文档放置与归档判定：
  `../../knowledge/doc-placement.md`
- 文档同步证据门禁：
  参考 `../kk-doc-sync/references/evidence-rules.md`
- 具体工作流与归档门禁：
  读取 [references/workflow.md](references/workflow.md)
  和 [references/archive-gates.md](references/archive-gates.md)
