---
name: kk-doc-backfill
description: |
  KK Dev Skeleton 缺文档、文档滞后或需要从代码 / diff / 测试 / 现有 spec 反推当前真实行为时使用。
  适用于“补接口文档”“补后端实现说明”“代码已经写了但文档没跟上”“按模块 backfill docs”
  “从最近改动反查应沉淀哪些文档”等场景。它负责先收集证据、标注可信度，再补 spec、
  review、decision、learning、data-interface 或 requirement-gap；没有验证证据时不得补 QA 通过结论。
---

# Doc Backfill

## Overview

这个 skill 负责把“缺文档时很费劲”的动作封装成固定流程。

它不是写总结，也不是把代码翻译成散文；它的目标是从现有证据反推当前真实行为，并把可证明的部分补回正确的 repo-native 文档位置。

## When To Use

优先使用：

- 代码、接口或数据逻辑已经存在，但对应 spec / 接口设计 / review / decision 缺失
- 最近一段实现改动被 `doc_coverage_audit.py` 标出文档覆盖缺口
- 后端 controller / DTO / service 已经写出，但输入输出、事实源、scope、异常策略没沉淀
- migration、Entity、Mapper、Repository、DAO、MyBatis XML、读模型、快照、projection 或后端接口已经存在，但 source doc / registry / interface doc / domain spec 缺失
- 需要从 diff、测试、fixture、脚本或页面行为反推当前真实工程状态
- 文档陈旧但仍是主线真源，应该先补更新而不是归档

通常不要用：

- 只是任务收口且已有清晰验证证据：优先用 `kk-doc-sync`
- 大范围文档归档或生命周期治理：优先用 `kk-doc-lifecycle`
- 新任务尚未建边界：先回退到 `kk-task-kickoff`

## Required Inputs

优先读取：

- active task boundary
- `.gstack/knowledge/doc-placement.md`
- 相关 `stack/` 真源文档；旧 `archive/baseline/` 只作证据来源
- 目标代码路径、当前 diff、最近 git 改动或 `doc_coverage_audit.py` 输出
- 相关测试、fixture、harness、QA 证据

证据不足时，可以补“待确认”文档，但必须明确哪些结论来自代码、哪些来自推断、哪些需要人工确认。

## Workflow

1. 确认任务是否已有 active boundary；没有则先回到 `kk-task-kickoff`。
2. 读 `doc-placement.md`，判断要补的是业务真源、工程 spec、协作过程产物还是长期经验。
3. 收集证据：代码、diff、spec、测试、fixture、脚本、接口调用、验证输出。
4. 给每个结论标注证据等级：
   - `code-proven`
   - `test-proven`
   - `spec-proven`
   - `inferred`
   - `needs-confirmation`
5. 按产物类型落文档：
   - 行为 / 接口 / 数据口径变化：优先补 `docs/specs/<module>/`；旧 `archive/baseline/` 只作证据来源
   - 后端接口输入输出：补 data-interface 或 `docs/specs/<module>/` 下的模块规范；不要写入旧 `04_后端设计/`
   - 已存在的新表 / 读模型 / 快照 / projection：补 source doc，必要时同步 `source-registry.md` 和模块 `data.md`
   - 已存在的新 API / DTO：补 interface doc 或模块 `backend.md` / `data.md`
   - 风险、边界、缺口：补 `.gstack/reviews/` 或 `.gstack/decisions/`
   - 可复用经验：补 `.gstack/learnings/`、`.gstack/rules/` 或 `pitfalls`
6. 如果没有真实验证证据，不补 QA 通过结论；只列出待验证项。
7. 完成后建议再运行 `kk-doc-sync` 或 `spec_sync_guard.py` 做收口检查。

## Output Rules

- 默认直接补高置信度文档，不只在聊天里总结
- 文档中必须保留证据来源和待确认项
- 不把 `archive/` 当当前真源反推实现
- 不把临时 SQL、analytics warehouse 探查或内部表结构写成正式 API
- 不编造用户确认、测试通过、QA 完成或业务口径已冻结
- 不在长期文档里写本机绝对路径
- 从代码反推的新表或接口默认最多标注为 `code-proven`；有测试覆盖时可标注 `test-proven`，有 domain spec 对齐时可标注 `spec-proven`。
- `inferred` 只能用于合理推断，必须列出推断依据；`needs-confirmation` 必须列出需要谁确认、确认什么。
- source 文档生命周期状态只使用 `draft / confirmed / deprecated / evidence-only / manual-review`；不要把 `code-proven / test-proven / spec-proven / inferred / needs-confirmation` 写进状态字段。
- 没有人工确认、正式 review 或 domain spec readiness 证据时，不把代码反推结果写成 `confirmed`。

## Reference

- 详细流程：读取 [references/workflow.md](references/workflow.md)
- 产物选择：读取 [references/output-matrix.md](references/output-matrix.md)
- QA 证据门禁：参考 `../kk-doc-sync/references/evidence-rules.md`
