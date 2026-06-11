# Task Boundary：chinese-first-skeleton-docs

- Task: chinese-first-skeleton-docs
- 负责人: Codex
- 日期: 2026-06-09
- 相关 issue / doc:
  - `.gstack/requirements/2026-06-09_chinese-first-skeleton-docs.md`
  - `.gstack/reviews/2026-06-09_chinese-first-skeleton-docs-review.md`

## Goal

- 将公开骨架调整为中文优先表达，同时保留机器可读英文标识和原有开发骨架能力。

## Allowed Files

- `README.md`
- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/knowledge/**`
- `.gstack/skills/README.md`
- `.gstack/scripts/gstack_doctor.py`
- `adapters/default/**`
- `examples/simple-web-app/**`
- `.gstack/requirements/2026-06-09_chinese-first-skeleton-docs.md`
- `.gstack/reviews/2026-06-09_chinese-first-skeleton-docs-review.md`
- `.gstack/task-boundaries/2026-06-09_chinese-first-skeleton-docs.md`
- `.gstack/qa-reports/2026-06-09_chinese-first-skeleton-docs-qa.md`

## Forbidden Files

- `.env`
- `.env.*`
- `secrets/**`
- production configs
- real data
- `.gstack/skills/kk-*/SKILL.md`，除非只是修正明显标题文案
- `.gstack/scripts/**`，除 `.gstack/scripts/gstack_doctor.py` 的人读输出中文化外

## Functional Non-goals

- 不重命名 `kk-*` skills。
- 不改脚本接口。
- 不改 YAML key 或环境变量名。
- 不发布外部仓库。
- 不执行代码提交流程。

## User-visible Acceptance

- User-visible Change:
  `yes`
- Expected Visible Behavior:
  - 新用户打开 `README.md`、`AGENTS.md`、`.gstack/README.md`、knowledge、adapter 和 example 文档时，正文以中文为主。
  - 示例 Web App 的页面标题、筛选控件、任务标题、状态标签和空态文案为中文。
  - `gstack_doctor.py check` 的默认人读输出为中文，保留 JSON 状态枚举和 check id。
  - 固定机制名仍可被搜索和工具解析。
- User Actions To Verify:
  - 阅读 `README.md` 和 `AGENTS.md`。
  - 打开 `examples/simple-web-app/stack/frontend/index.html`。
  - 运行 smoke 和 doctor。
- Required Evidence:
  `CLI 输出 / QA 报告 / 文案扫描`
- If No User-visible Change:
  不适用。

## Generated Artifact Policy

- Surface Type:
  `docs-only / HTML`
- Acceptance URL:
  `examples/simple-web-app/stack/frontend/index.html`
- Refresh / Regeneration:
  重新打开 HTML 文件，或用本地 HTTP server 预览。
- If No Visible Change:
  不适用。
- Required Interaction Evidence:
  示例 HTML 文案变化需至少有静态文案检查；若后续继续打磨示例交互，再补浏览器 QA。

## Decision Mode

- Mode: `autonomous`
- Source:
  `user-confirmed`
- Internal Enum:
  `codex-led`
- Reason:
  用户已确认中文优先方向；本次是低风险文档和示例文案调整。

## Flow Lane

- Lane: `fast-lane`
- Reason:
  范围明确、低风险、可本地验证，不涉及真实数据、生产、数据库或 git workflow action。
- Evidence Strategy:
  - fast-lane requirement, review, boundary, QA.

## Autonomy Plan

- Codex May Do Without Asking:
  - 中文化公开入口文档、knowledge、adapter 和 example 文案。
  - 运行本地 smoke、doctor 和 guard。
- Codex Must Ask Before:
  - git workflow action
  - production action
  - real data access
  - database changes
  - 发布外部仓库
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户`
- Goal Mode:
  `not-used`
- Local Restart:
  `not-required`

## Subagent Plan

- Mode: `not-used`
- Reason:
  小范围文档和示例文案调整，无需 subagent。
- Main Agent Owns:
  - 中文化改动
  - QA evidence
- Candidate Subagents:
  - name: `not-used`
    role: `reviewer`
    trigger stage: `qa`
    write scope: `read-only`
    forbidden paths:
      - `**`
    output evidence: `.gstack/qa-reports/2026-06-09_chinese-first-skeleton-docs-qa.md`
    status: `not-used`
- Result Integration:
  - 不适用。

## GStack Required Flow

- requirement-brief:
  status: `done`
  evidence: `.gstack/requirements/2026-06-09_chinese-first-skeleton-docs.md`
- plan-ceo-review:
  status: `done`
  evidence: `.gstack/reviews/2026-06-09_chinese-first-skeleton-docs-review.md`
- requirement-freeze:
  status: `done`
  evidence: `.gstack/requirements/2026-06-09_chinese-first-skeleton-docs.md`
- plan-eng-review:
  status: `done`
  evidence: `.gstack/reviews/2026-06-09_chinese-first-skeleton-docs-review.md`
- domain-spec-readiness:
  status: `done`
  evidence: `.gstack/knowledge/ai-programming-framework.md examples/simple-web-app/stack/specs/requirements.md examples/simple-web-app/stack/specs/frontend.md examples/simple-web-app/stack/specs/testing.md`
- implement:
  status: `done`
  evidence: `README.md AGENTS.md .gstack/knowledge examples/simple-web-app/stack/frontend/index.html examples/simple-web-app/stack/frontend/main.js`
- qa:
  status: `done`
  command: `qa-only`
  evidence: `.gstack/qa-reports/2026-06-09_chinese-first-skeleton-docs-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "本次不涉及真实数据源、接口、查数或外部系统。"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: "不适用"
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "不涉及数据专项"
  - gate_id: prototype-logic-extraction
    trigger_reason: "本次只调整文档和示例文案，没有把前端或原型业务逻辑迁移到后端。"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: "不适用"
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "不涉及原型逻辑承接"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent。"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-09_chinese-first-skeleton-docs.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "已声明不使用 subagent"
```

## Required Knowledge

- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/qa-dimensions.md`

## Spec Sync Plan

- Spec Impact:
  `not-required`
- Expected Spec Targets:
  - `.gstack/knowledge/ai-programming-framework.md`
  - `.gstack/knowledge/CODEMAP.md`
  - `examples/simple-web-app/stack/specs/requirements.md`
  - `examples/simple-web-app/stack/specs/frontend.md`
  - `examples/simple-web-app/stack/specs/testing.md`
- If Not Required, Why:
  本次不改变应用业务行为、接口、数据模型或持久化；只调整公开骨架语言和示例文案。

## Verification

- `rg` 扫描主要入口文档中明显英文说明残留。
- `python3 .gstack/scripts/natural_language_dev_smoke.py --format user`
- `python3 .gstack/scripts/gstack_doctor.py check`
- `python3 .gstack/scripts/gstack_doctor.py --help`
- `python3 .gstack/scripts/spec_sync_guard.py`

## Lessons To Write Back

- 公开骨架面向中文团队时，应采用“中文正文 + 英文机制标识”的双层表达，避免翻译破坏工具链。
