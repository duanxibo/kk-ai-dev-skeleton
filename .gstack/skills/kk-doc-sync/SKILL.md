---
name: kk-doc-sync
description: |
  KK Dev Skeleton 任务接近收口或实现已变化时使用。它负责判断这次改动该同步哪些 repo-native 文档，
  并在证据足够时直接落 review、decision、learning、真源说明或 QA 记录。适用于“不想再手动复制
  文档落地 prompt”的场景，但它不得在无验证证据时编造 QA 或“已通过”结论。
---

# Doc Sync

## Overview

这个 skill 用来替代 `.gstack/templates/ai-doc-sync-prompts.template.md` 的手动复制流程。

它的目标不是“写一篇泛泛总结”，而是根据当前 diff、boundary、真源和验证证据，判断哪类文档需要被同步，并在合适时直接落到 repo。

## When To Use

在这些场景优先使用：

- 实现代码、行为口径或协作结论已经变化，担心只改代码没补文档
- 任务准备收口，需要判断该补 review、QA、decision、learning 还是 spec
- 任务 diff 新增或调整后端 API、DTO、migration、表、读模型、快照、projection，需要执行 `data-knowledge-sync`
- 你知道这次需要文档同步，但不想每次手动复制长 prompt

这些场景通常不需要使用：

- 没有任何变更或结论，只是做初步讨论
- 用户明确要求“先不要落文档，只给我建议”

## Required Inputs

优先读取：

- active boundary
- 相关真源文档
- 当前 diff 或本次已完成的产物
- 已执行过的验证结果

如果没有验证证据，不要假装有 QA 结果。

## Decision Rules

优先判断以下目标：

- `stack` domain spec readiness 或历史 baseline 采纳说明
- `.gstack/reviews/`
- `.gstack/qa-reports/`
- `.gstack/decisions/`
- `.gstack/learnings/`
- `.gstack/rules/` 或 `.gstack/knowledge/pitfalls/`
- `README`、`specs`、`knowledge` 等真源说明
- `data-knowledge-sync`：新表、新接口、新读模型、新快照、新 projection 的 source doc、registry、stack domain spec 和 interface doc 是否回写

判断原则：

- 行为、接口、数据口径变化：
  优先补真源文档
- 结构、边界、风险为主：
  优先补 review
- 有明确验证动作和结果：
  才能补 QA
- 有取舍争议或分层裁定：
  补 decision
- 有长期可复用经验：
  补 learning / rule / pitfall

## Data Knowledge Sync

任务收口时，如果当前 diff 或已完成产物出现以下任一信号，必须执行 `data-knowledge-sync` 检查：

- 新增或调整 Controller / Route / API handler。
- 新增或调整 Request / Response DTO，且改变输入、输出、字段含义或异常语义。
- 新增 migration、`CREATE TABLE`、`ALTER TABLE`、`CREATE INDEX`。
- 新增 Entity、Mapper、Repository、DAO、MyBatis XML、读模型、快照、projection 或 shadow table。
- 新增对外数据产品、跨系统接口、数据导出接口或前端替换 mock 的后端接口。

收口时优先补齐：

- 已归属模块的 stack domain spec：`docs/specs/<module>/backend.md`、`data.md` 或等价文档。
- 接口说明或 data-interface：输入、输出、事实源、scope、异常返回、权限和不应暴露的内部结构。
- 数据源说明：已有表、读模型、快照、projection 或 shadow table 的 source doc。
- `source-registry.md` 索引：让新增 source doc 可检索。
- review 报告中的 `Data Knowledge Sync` 检查项。

证据规则：

- 有验证证据时，才能补 QA 通过结论；没有验证证据时，只写待验证项。
- source 生命周期状态只使用 `draft / confirmed / deprecated / evidence-only / manual-review`。
- 证据等级单独标注为 `code-proven / test-proven / spec-proven / inferred / needs-confirmation`。
- 从代码或 diff 反推的表 / 接口默认不能写成 `confirmed`；除非有人工确认、正式 review 或 domain spec readiness 证据。

## Output Rules

- 默认允许自动落高置信度文档：
  review、decision、learning、knowledge 路由、README、spec 说明
- 只有在有证据时才允许自动落 QA
- 严禁在没有实际验证时写“通过 QA”或“验收完成”
- 如果判断“不需要补某类文档”，必须明确说明原因

## Template Source

这个 skill 以仓库模板为真源：

- 主模板：`../../templates/ai-doc-sync-prompts.template.md`
- 场景映射：读取 [references/template-map.md](references/template-map.md)
- 自动落文档门禁：读取 [references/evidence-rules.md](references/evidence-rules.md)
