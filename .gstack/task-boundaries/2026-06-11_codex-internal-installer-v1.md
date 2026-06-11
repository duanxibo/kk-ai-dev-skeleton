# codex-internal-installer-v1 Task Boundary

- Task: codex-internal-installer-v1
- 负责人: Codex
- 日期: 2026-06-11
- 相关 issue / doc: `.gstack/requirements/2026-06-11_codex-internal-installer-v1-fast-lane-requirement.md`

## Goal

- 实现 V1 内部安装器能力：在保留自然语言用户入口的前提下，为 Codex 提供 detect / plan / apply / verify / report 确定性 helper

## Allowed Files

- .gstack/requirements/2026-06-11_codex-internal-installer-v1-fast-lane-requirement.md
- .gstack/reviews/2026-06-11_codex-internal-installer-v1-fast-lane-review.md
- .gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md
- .gstack/qa-reports/2026-06-11_codex-internal-installer-v1-qa.md
- scripts/init_project.py
- scripts/dev_stack.sh
- tests/test_init_project.py
- README.md
- COMPANY_ADOPTION_GUIDE.md
- CODEX_ADOPTION_CONNECTOR.md
- .gstack/knowledge/code-patterns.md

## Forbidden Files

- adapter 真实项目配置与 default adapter 内容
- `.gstack/scripts/` 下已有 guard、doctor、dashboard、smoke 行为
- 应用代码、示例应用和测试夹具
- 数据库配置、真实凭证、`.env*`、`.gstack/data-access/*.local.*`
- git workflow action，除非用户另行明确批准

## Functional Non-goals

- 不实现正式 Codex plugin 或外部分发平台。
- 不自动覆盖已有真实项目 adapter。
- 不默认执行生产、数据库、真实数据或 git workflow action。
- 不改变业务用户的自然语言接入方式。
- 不重写 doctor、guard 或 smoke 的核心判断逻辑。

## User-visible Acceptance

- Codex 可以调用 `scripts/init_project.py` 的 detect / plan / apply / verify / report 能力，获得确定性接入报告。
- 旧用法 `python3 scripts/init_project.py --adapter <name> --create-adapter` 继续可用。
- `apply` 在 adapter 已存在时默认不覆盖，除非显式传 `--force`。
- `verify` 能串联现有 doctor、spec sync guard、team flow guard、Required Gates audit 和 natural language smoke，并以非零退出码表示失败。
- README、公司接入指南和产品化方案仍说明：业务用户通过 Codex 自然语言接入，脚本只是 Codex 背后的执行工具。

## Generated Artifact Policy

- User-visible Change: `no`
- Artifact Type: `CLI helper output and markdown docs`
- Acceptance Surface: `terminal output and repo documentation`
- Browser QA: `not-required`
- Reason:
  本次不生成 HTML、页面、dashboard、截图或可交互 UI；用户可见变化是 Codex 背后的接入 helper 能力和文档说明。

## Decision Mode

- Mode: `自主执行`
- Source:
  `repo-default`
- Internal Enum:
  `codex-led`
- Reason:
  Codex 语义复核后确认 fast-lane 任务范围明确，按当前协作模式自动生成最小 evidence。

## Flow Lane

- Lane: `fast-lane`
- Reason:
  小需求 / 明确改动，无业务口径多解、生产操作、DB schema 或 git workflow action。
- Evidence Strategy:
  - 使用 fast-lane requirement、fast-lane review、boundary 和 QA evidence。

## Autonomy Plan

- Codex May Do Without Asking:
  - 补齐 fast-lane evidence。
  - 在 Allowed Files 内实现。
  - 运行本地验证和门禁。
- Codex Must Ask Before:
  - 业务口径多解。
  - 触碰 Forbidden Files。
  - 生产操作、DB schema 变更、真实数据写入、破坏性命令或 git workflow action。
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户`
- Goal Mode:
  `not-used`
  fast-lane 小任务默认不启用持续 goal。
- Local Restart:
  `not-required`

## Subagent Plan

- Mode: `not-used`
- Reason:
  fast-lane 小任务默认由 main agent 直接完成；如实现中范围扩大，再退出 fast-lane 并重新规划。
- Main Agent Owns:
  - 流程控制、active boundary、最终集成、最终答复
- Candidate Subagents:
  - name: `not-used`
    role: `reviewer`
    trigger stage: `review`
    write scope: `read-only`
    forbidden paths:
      - `stack/**`
    output evidence: `.gstack/qa-reports/2026-06-11_codex-internal-installer-v1-qa.md`
    status: `not-used`
- Result Integration:
  - 本轮验证结果写入 QA 报告和 final summary。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-11_codex-internal-installer-v1-fast-lane-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-11_codex-internal-installer-v1-fast-lane-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-11_codex-internal-installer-v1-fast-lane-requirement.md`
  note: fast-lane requirement 同时作为 requirement freeze。
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-11_codex-internal-installer-v1-fast-lane-review.md`
- domain-spec-readiness:
  status: not-required
  evidence: `.gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md`
  note: 本次 fast-lane 小需求不改变 stack domain 产品或工程真源。
- implement:
  status: done
  evidence: `scripts/init_project.py`
- qa:
  status: done
  command: qa-only
  evidence: `.gstack/qa-reports/2026-06-11_codex-internal-installer-v1-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "AI 已确认 fast-lane 不涉及真实数据、接口、查数或数据源选择；如实现中发现涉及，必须退出 fast-lane 或改为 planned"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确本任务不涉及数据源 / 接口 / 查数"
  - gate_id: data-query
    trigger_reason: "AI 已确认 fast-lane 不涉及复杂查数或高风险指标"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不需要 Query Brief、SQL 或查询 review"
  - gate_id: prototype-logic-extraction
    trigger_reason: "AI 已确认 fast-lane 不涉及前端 / 原型业务逻辑迁后端"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确没有前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；本轮不使用 subagent"
  - gate_id: doc-backfill
    trigger_reason: "AI 已确认 fast-lane 不是代码已有但文档缺失的 backfill 场景"
    owner: kk-doc-backfill
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "新增文档同步创建，不需要从代码反推"
  - gate_id: data-knowledge-sync
    trigger_reason: "AI 已确认 fast-lane 不新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据知识同步"
```

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/implementation-guide.md`
- `.gstack/knowledge/code-patterns.md`
- `.gstack/knowledge/qa-dimensions.md`
- `.gstack/entrypoints/engineer.md`
- `.gstack/workflows/codex-autopilot.md`
- `.gstack/templates/fast-lane-requirement.template.md`
- `.gstack/templates/fast-lane-review.template.md`

## Spec Sync Plan

- Spec Impact:
  `not-required`
- Expected Spec Targets:
  - 不适用
- Prototype Logic Evidence Sync:
  不适用。
- Allowed No-Spec-Change Reason:
  本次 fast-lane 小需求不改变 stack domain 产品或工程真源。

## Verification

- `python3 -m unittest tests/test_init_project.py`
- `python3 scripts/init_project.py --adapter default --detect`
- `python3 scripts/init_project.py --adapter default --plan`
- `python3 scripts/init_project.py --adapter default --report`
- `python3 scripts/init_project.py --adapter default --verify`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`
- `python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md`
- `rg --hidden -n "用户.*执行.*python3|业务用户.*运行.*python3|在目标项目根目录内执行|复制到新项目后的最小步骤" CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md -S`
- `rg --hidden -n "detect|plan|apply|verify|report|内部安装器|Codex 接入器" scripts/init_project.py CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md -S`

## Lessons To Write Back

- 如发现新坑，写入 `.gstack/knowledge/` 或 `.gstack/rules/`。

## 本地激活

- 自动激活时由 `python3 .gstack/scripts/autopilot_bootstrap.py ... --activate` 写入本机 `CURRENT.local.md`。
