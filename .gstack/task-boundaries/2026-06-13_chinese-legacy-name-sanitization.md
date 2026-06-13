# chinese-legacy-name-sanitization Task Boundary

- Task: chinese-legacy-name-sanitization
- 负责人: Codex
- 日期: 2026-06-13
- 相关 issue / doc: `.gstack/requirements/2026-06-13_chinese-legacy-name-sanitization-fast-lane-requirement.md`

## Goal

- 清理公开骨架中的中文旧项目名残留，并补测试防回归。

## Allowed Files

- `.gstack/requirements/2026-06-13_chinese-legacy-name-sanitization-fast-lane-requirement.md`
- `.gstack/reviews/2026-06-13_chinese-legacy-name-sanitization-fast-lane-review.md`
- `.gstack/task-boundaries/2026-06-13_chinese-legacy-name-sanitization.md`
- `.gstack/qa-reports/2026-06-13_chinese-legacy-name-sanitization-qa.md`
- `.gstack/requirements/2026-06-09_context-isolation-hardening.md`
- `tests/test_productization_hardening.py`

## Forbidden Files

- plugin manifest、marketplace name 或版本号
- `.env*`、真实凭证、生产配置、真实客户数据
- git workflow action，除非用户另行明确批准

## Functional Non-goals

- 不重构公开扫描策略。
- 不发布 / commit / push。

## User-visible Acceptance

- tracked tree 扫描不再发现中文旧项目名。
- 单元测试能覆盖该敏感 token。

## Generated Artifact Policy

- User-visible Change: `yes`
- Artifact Type: `markdown evidence, unit tests`
- Acceptance Surface:
  - `.gstack/requirements/2026-06-09_context-isolation-hardening.md`
  - `tests/test_productization_hardening.py`
- Browser QA: `not-required`
- Reason:
  本次不改变 Web UI、HTML、dashboard 或可视化交互。

## Decision Mode

- Mode: `自主执行`
- Source: `user-review-findings`
- Internal Enum: `codex-led`
- Reason:
  用户给出明确 review finding，可本地证明并修复。

## Flow Lane

- Lane: `fast-lane`
- Reason:
  极小范围文本净化和测试增强，不涉及业务口径、真实数据、DB schema、生产操作或 UI。

## Autonomy Plan

- Codex May Do Without Asking:
  - 在 Allowed Files 内实现。
  - 运行本地测试和 guards。
- Codex Must Ask Before:
  - 执行 commit、push、PR、生产部署、DB schema 变更、破坏性命令或真实数据写入。
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户`
- Goal Mode:
  `not-used`
- Local Restart:
  `not-required`

## Subagent Plan

- Mode: `not-used`
- Reason:
  fast-lane 小修复由 main agent 直接完成。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-13_chinese-legacy-name-sanitization-fast-lane-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-13_chinese-legacy-name-sanitization-fast-lane-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-13_chinese-legacy-name-sanitization-fast-lane-requirement.md`
  note: fast-lane requirement 同时作为 requirement freeze。
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-13_chinese-legacy-name-sanitization-fast-lane-review.md`
- domain-spec-readiness:
  status: not-required
  evidence: `.gstack/task-boundaries/2026-06-13_chinese-legacy-name-sanitization.md`
  note: 本次不改变具体应用 stack domain 产品或工程真源。
- implement:
  status: done
  evidence: `.gstack/requirements/2026-06-09_context-isolation-hardening.md`, `tests/test_productization_hardening.py`
- qa:
  status: done
  evidence: `.gstack/qa-reports/2026-06-13_chinese-legacy-name-sanitization-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "本任务不涉及真实数据、接口、查数或数据源选择"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-13_chinese-legacy-name-sanitization.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据源 / 接口 / 查数"
  - gate_id: data-query
    trigger_reason: "本任务不涉及复杂查数或高风险指标"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-13_chinese-legacy-name-sanitization.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不需要 Query Brief、SQL 或查询 review"
  - gate_id: prototype-logic-extraction
    trigger_reason: "本任务不迁移原型或旧项目业务逻辑"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-13_chinese-legacy-name-sanitization.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-13_chinese-legacy-name-sanitization.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；本轮不使用 subagent"
  - gate_id: doc-backfill
    trigger_reason: "本任务清理历史 requirement 文本，不是从已有代码反推文档"
    owner: kk-doc-backfill
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-13_chinese-legacy-name-sanitization.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "文本净化同步完成，不需要从代码反推"
  - gate_id: data-knowledge-sync
    trigger_reason: "本任务不新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-13_chinese-legacy-name-sanitization.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据知识同步"
```

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/task-boundaries/CURRENT.md`
- `adapters/default/adapter.md`
- `adapters/default/runtime.json`

## Spec Sync Plan

- Spec Impact: `not-required`
- Expected Spec Targets:
  - 不适用
- Allowed No-Spec-Change Reason:
  本次只清理公开发放文本和测试，不改变具体应用 stack domain 产品或工程真源。

## Verification

- `python3 -m unittest tests/test_productization_hardening.py -v`
- `python3 -m unittest discover -s tests -v`
- `python3 .gstack/scripts/gstack_doctor.py check`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`
- `python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-13_chinese-legacy-name-sanitization.md`
- `python3 .gstack/scripts/runtime_artifact_guard.py`

## Lessons To Write Back

- 如发现新坑，写入 `.gstack/knowledge/` 或 `.gstack/rules/`。
