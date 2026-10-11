# Framework reliability and scoped autonomy

## Goal
- 用户授权按评审建议修改框架，通过独立分支和 PR 交付。
- 修复 adapter 错误配置、拒绝静默回退；增加 CI；简化小任务记录；自动推进限定在已授权目标；保留已有项目布局。

## Allowed Files
- AGENTS.md
- README.md
- COMPANY_ADOPTION_GUIDE.md
- CODEX_ADOPTION_CONNECTOR.md
- adapters/default/
- scripts/init_project.py
- .gstack/scripts/
- .gstack/skills/
- .gstack/workflows/
- .gstack/templates/
- .gstack/knowledge/
- .gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md
- .gstack/task-boundaries/2026-10-11_framework-reliability.md
- .gstack/requirements/2026-10-11_framework-reliability.md
- .gstack/reviews/2026-10-11_framework-reliability.md
- .gstack/qa-reports/2026-10-11_framework-reliability.md
- tests/
- .github/workflows/

## Forbidden Files
- .env、secrets/、业务应用和历史任务证据。

## Functional Non-goals
- 不重构整个 Loop、不操作生产或数据库、不合并 main。

## User-visible Acceptance
- 错误配置报告具体字段；缺失 adapter 默认报错。
- 小任务可使用一份记录；独立建议不能自动成为新任务。
- PR 展示改动及可复现的测试结果，CI 执行回归检查。

## Generated Artifact Policy
- 临时输出保留在 /tmp，不提交。

## Collaboration Mode
- autonomous

## Flow Lane
- Lane: standard

## Autonomy Plan
- Goal Mode: not-used
- 仅推进用户已授权的框架改进范围。

## Subagent Plan
- Mode: not-used
- 原因：配置、模板和 smoke 契约耦合，当前连接需顺序建立完整快照后验证。

## Required Gates
- data-access: not-required；不访问业务数据。
- ui-interaction-qa: not-required；不修改 UI。
- doc-backfill: done；规则和安装器模板已同步。

## Verification Plan
- 定向 adapter 行为测试、完整 unittest、Loop contract 和自然语言 smoke、spec_sync_guard。

## Plan Review
- 优先修可复现错误和授权边界；避免先做大规模拆分。

## Decision Mode
- Mode: 自主执行
- Source: user-this-task

## Required Knowledge
- AGENTS.md
- .gstack/knowledge/ai-programming-framework.md
- adapters/default/adapter.md

## Lessons To Write Back
- 配置先校验再归一化；完成任务不构成新目标授权。

## Spec Sync Plan
- Spec Impact: updated
- Expected Spec Targets:
  - AGENTS.md
  - README.md
  - .gstack/knowledge/ai-programming-framework.md

## GStack Required Flow
- requirement-brief:
  status: done
  evidence: .gstack/requirements/2026-10-11_framework-reliability.md
- plan-ceo-review:
  status: done
  evidence: .gstack/reviews/2026-10-11_framework-reliability.md
- requirement-freeze:
  status: done
  evidence: .gstack/requirements/2026-10-11_framework-reliability.md
- plan-eng-review:
  status: done
  evidence: .gstack/reviews/2026-10-11_framework-reliability.md
- domain-spec-readiness:
  status: not-required
  evidence: .gstack/task-boundaries/2026-10-11_framework-reliability.md
  note: 不改变业务规格，框架契约已同步。
- implement:
  status: done
  evidence: .gstack/task-boundaries/2026-10-11_framework-reliability.md
- qa:
  status: done
  evidence: .gstack/qa-reports/2026-10-11_framework-reliability.md
