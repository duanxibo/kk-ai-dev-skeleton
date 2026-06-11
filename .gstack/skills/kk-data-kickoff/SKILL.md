---
name: kk-data-kickoff
description: |
  KK Dev Skeleton data-access gate 专项流程。适用于页面或原型接真实数据、前端 mock 替换接口、
  新增或调整后端接口、读取 relational database 或 analytics warehouse 辅助开发、跨系统复用数据、用户提供表说明或查数主题等场景。
  它在 kk-task-kickoff 的 boundary 语境下读取 data-access 知识库，确认数据意图、数据源、scope、接口输入输出和复用边界，并输出 gate evidence。
---

# Data Kickoff

## Overview

这个 skill 是 `data-access` 专项 gate 的执行入口，不是 KK Dev Skeleton 新任务的通用开工入口。

它负责实现前准入，不负责实现后知识回写。`kk-data-kickoff` 可以在接口设计或数据源确认阶段发现后续可能需要 `data-knowledge-sync`，并提醒 `kk-task-kickoff` 写入 boundary；但 `data-knowledge-sync` 的 owner 应是 `kk-doc-sync`，代码已存在但文档缺失时由 `kk-doc-backfill` 承接。

它只协助发现 `prototype-logic-extraction`，不拥有该 gate。如果数据任务来源是已有前端页面、原型、fixture 或 mock，并且后端接口、读模型或 service 要承接其中业务逻辑，必须回到 `kk-task-kickoff` 在 active boundary 中声明 `prototype-logic-extraction`，`owner: kk-task-kickoff`，`required_before: plan-eng-review`。

它是数据任务运行时入口，而不是让用户手工建设脚手架的说明书。

用户可以只描述需求、提供已有表说明、给出 SQL 或提出看板目标；AI 负责读取 data-access 知识库，基于已有数据资产创建或更新数据源说明、数据意图草案、接口设计草案、SQL 草案、数据发现报告和数据需求缺口文档。用户只需要确认业务口径、事实源、权限边界和 relational database 落表等决策点。

它不直接实现业务代码、不新增数据库连接、不改 relational database 表结构，也不创建独立工程任务 boundary。它的职责是在 `kk-task-kickoff` 已有或正在创建的 boundary 语境下，把数据任务整理成可评审、可复用、可作为 `data-access` gate evidence 的协作状态。

## When To Use

在这些场景优先使用：

- 页面、原型、看板需要接真实数据
- 前端 mock 要替换成后端接口
- 新增或调整后端接口
- 用户提供 relational database 表说明、字段口径或 analytics warehouse 查数主题
- 需要开发期真实数据探查
- 用户用业务语言提出查数需求，但不知道库表或字段结构
- 受限业务模块、计划系统、项目工作台之间发生数据复用
- 任务涉及数据源、事实源、scope、指标口径、接口输入输出或跨系统调用边界

这些场景通常不需要使用：

- 纯样式、文案或静态布局调整，且没有数据字段或接口变化
- 已有明确接口契约且只做无语义的小修

## Required Reading

0. 当前 task boundary：
   先确认 `kk-task-kickoff` 已创建或补齐 active boundary，并且其中有 `data-access` gate；如果没有，先回到 `kk-task-kickoff`。
1. 数据脚手架入口：
   `.gstack/knowledge/data-access/README.md`
2. 按任务补读：
   - 数据源索引：`.gstack/knowledge/data-access/source-registry.md`
   - relational database 表说明：`.gstack/knowledge/data-access/mysql-source-guide.md`
   - analytics warehouse 探查：`.gstack/knowledge/data-access/clickhouse-discovery-guide.md`
   - 实际查数配置：`.gstack/knowledge/data-access/query-access-guide.md`
   - 接口实现或跨系统复用：`.gstack/knowledge/data-access/interface-design-guide.md`
   - 前期数据查询专用 skill：`.gstack/skills/kk-data-query/SKILL.md`
   - 数据查询流程设计：以 `.gstack/skills/kk-data-query/SKILL.md` 和 `.gstack/knowledge/data-access/query-access-guide.md` 为准；具体项目补充放入 adapter 或项目真源文档。

## Workflow

1. 确认当前任务的 active boundary 和 `data-access` gate；没有 boundary 时，停止并回到 `kk-task-kickoff` 创建或补齐。
2. 判断数据专项属于哪个 `stack` domain，或是否仍处于跨系统 / 探索期。
3. 读取 `.gstack/knowledge/data-access/` 知识库，至少从 `README.md` 进入，再按任务读取 registry、relational database、analytics warehouse 或 interface guide。
4. 查 `.gstack/knowledge/data-access/source-registry.md` 和 `sources/`，确认是否已有对应数据源说明。
5. 如果已有表、已有 SQL 或已有看板证据尚未登记，AI 应按 `.gstack/templates/data-source.template.md` 创建或更新 source 文档，并同步更新 `source-registry.md`；source 只登记已有数据资产，不用于设计新表或表达未满足需求。
6. 如果用户只给页面、原型或看板需求，AI 应按 `.gstack/templates/data-intent.template.md` 创建数据意图草案，明确字段、数据逻辑、指标口径、scope、空状态和异常状态。
7. 如果发现接口、读模型或 service 来源于已有前端 / 原型 / mock 业务逻辑，提醒回到 `kk-task-kickoff` 在 boundary 中标记 `prototype-logic-extraction`；本 skill 可以引用逻辑抽取 evidence，但不能把自己写成 gate owner。
8. 如果用户用业务语言提出复杂查数需求，在当前 `data-access` gate 语境下调起 `.gstack/skills/kk-data-query/SKILL.md`，由它整理 Query Brief、定位 source、生成只读 SQL 并做 Query Review；只问时间范围、指标口径、scope、输出粒度和用途等业务问题，不要求用户提供库表或字段。需要长期保存时，Query Brief 放 `.gstack/requirements/data-query/`，Query Review 放 `.gstack/reviews/data-query/`。
9. 如果需要实际查询 relational database / analytics warehouse，先读取 `.gstack/knowledge/data-access/query-access-guide.md`，确认本机只读配置存在，并确认查询目标、scope、limit 和脱敏边界；查询结论按 `.gstack/templates/data-discovery-report.template.md` 或 `.gstack/templates/data-query-review.template.md` 落文档。
10. 如果现有表可以通过 SQL 组合、join、聚合或派生支持需求，AI 应把 SQL 草案放到 `.gstack/knowledge/data-access/sql-drafts/` 或 adapter 指定的项目 data 目录，并在数据发现报告中说明可满足部分、风险和替换路径；探索期数据发现报告放 `.gstack/knowledge/data-access/discovery-reports/`，不要直接放在 data-access 根目录。
11. 如果现有表无法满足字段、粒度或口径，AI 应按 `.gstack/templates/data-requirement-gap.template.md` 创建数据需求缺口文档，放到 `.gstack/knowledge/data-access/requirement-gaps/` 或 adapter 指定的项目 data 目录；不要把需求伪装成 source，也不要直接设计新表进入实现。
12. 如果进入 `stack` 后端、前端或跨系统复用，AI 应按 `.gstack/templates/data-interface-design.template.md` 创建接口设计草案，明确输入、输出、事实源、scope、异常返回和复用边界；若存在 `prototype-logic-extraction`，接口设计必须引用该 evidence path。
13. 如果接口设计或数据缺口决策预计会导致新增 API / DTO / migration / 表 / 读模型 / 快照 / projection，输出 `data-knowledge-sync` gate 建议，提醒 owner 使用 `kk-doc-sync`、`required_before: review`；如果代码已经存在但文档缺失，提醒改由 `kk-doc-backfill` 反推补齐。
14. 输出当前阶段结果：
   - 已创建或更新的文档路径
   - `stack-domain`：数据需求、数据逻辑、字段口径、接口输入输出、事实源、scope、异常返回和待确认问题
   - 跨系统：调用方、提供方、复用边界、禁止耦合的内部结构和待确认问题
15. 判断是否可以进入实现；如果缺数据源说明、输入输出、scope、事实源、查询边界、数据缺口决策或 relational database 人工确认，先停在待确认状态。
16. 输出 `data-access` gate readiness：`done / planned / blocked / deferred / not-required`、evidence_path、blocking_reason、next action、是否协助发现了 `prototype-logic-extraction`、是否需要 `data-knowledge-sync`、是否需要回到 `kk-task-kickoff` 汇总 gates。最终实现准入由 `kk-task-kickoff` 汇总所有 gates 后决定。

## Output Rules

- 默认输出数据需求、数据源、接口设计和待确认问题，而不是直接写业务实现。
- 默认由 AI 创建或更新脚手架文档，不要求用户手工复制模板。
- 如果当前没有 active boundary 或 `data-access` gate，先提示需要回到 `kk-task-kickoff`；不要自行创建独立 boundary。
- 如果当前需要 `prototype-logic-extraction`，只输出协助触发建议和 evidence path，不要把 `kk-data-kickoff` 写成 owner。
- 如果当前后续需要 `data-knowledge-sync`，只输出协助触发建议和 reason，不要把 `kk-data-kickoff` 写成 owner。
- 只产出数据专项证据和 next action，不单独决定整个任务是否可以进入实现。
- source 文档只登记已有数据资产、已有 SQL 或已有看板证据；不能把未满足的数据需求写成 source。
- 如果现有数据不满足，先产出 SQL 草案和数据需求缺口文档，供后续数据/开发决策。
- 不能把临时 SQL 当成正式 API。
- 不能把查询账号、密码、连接串写进 repo 文档、skill 或模板正文。
- 不能输出手机号原文；手机号如必须参与 join、去重或匹配，只能在数据库内部计算，不进入结果集、repo 文档、subagent 输出或最终答复。
- 不能让前端或其他系统直接依赖内部表结构、analytics warehouse 查询或任意 SQL。
- 涉及 relational database 落表、改表、索引或读模型新增时，只能提出方案，等待人工确认。
- 如果用户只给了表说明，优先落数据源说明和接口设计草案。
- 如果用户只给了页面需求，优先落数据意图草案。

## Document Storage Rules

`kk-data-kickoff` 负责把数据专项产物放到正确位置，不能把所有过程文档直接写到 `.gstack/knowledge/data-access/` 根目录：

- 数据源说明：已有 relational database 表、analytics warehouse 表、BI 看板或历史 SQL evidence 放 `sources/mysql/` 或 `sources/clickhouse/`，并更新 `source-registry.md`。
- Query Brief：探索期放 `.gstack/requirements/data-query/`；已归属项目后放 adapter 指定的项目 data / specs 目录。
- Query Review：探索期放 `.gstack/reviews/data-query/`；已归属项目后放 adapter 指定的项目 data / specs 目录。
- Data Discovery Report：探索期放 `.gstack/knowledge/data-access/discovery-reports/`；已归属项目后放 adapter 指定的项目 data / specs 目录。
- SQL Draft：探索期放 `.gstack/knowledge/data-access/sql-drafts/`；已归属项目后放 adapter 指定的项目 data / specs 目录。
- Requirement Gap：探索期放 `.gstack/knowledge/data-access/requirement-gaps/`；已归属项目后放 adapter 指定的项目 data / specs 目录。
- 接口设计、读模型设计或正式领域规范：已进入实现边界时，优先放 adapter 指定的项目真源目录；还在跨模块探索期时放 `.gstack/designs/`。

`data-access` 根目录只保留 `README.md`、guide、registry 和少量跨源汇总。迁移或新增文档后，要同步更新 `source-registry.md` 或对应目录 README。

## Template Sources

- 数据意图：`../../templates/data-intent.template.md`
- 数据源说明：`../../templates/data-source.template.md`
- 接口设计：`../../templates/data-interface-design.template.md`
- 数据发现报告：`../../templates/data-discovery-report.template.md`
- 数据需求缺口：`../../templates/data-requirement-gap.template.md`
- 数据查询 Brief：`../../templates/data-query-brief.template.md`
- 数据查询 Review：`../../templates/data-query-review.template.md`
- 查询 env 模板：`../../templates/data-query-env.template`
- 查询 YAML 模板：`../../templates/data-query-config.template.yaml`
