# Task Boundary: UI quality check

## Goal

把 UI 风格判断、设计 brief 和 visual polish review 抽离为公开 KK Dev Skeleton 能力，并让目标项目通过 portable core 获得这套 UI 质量检查。

## Allowed Files

- `.gstack/requirements/2026-06-22_ui-quality-gate-fast-lane-requirement.md`
- `.gstack/reviews/2026-06-22_ui-quality-gate-fast-lane-review.md`
- `.gstack/task-boundaries/2026-06-22_ui-quality-gate.md`
- `.gstack/qa-reports/2026-06-22_ui-quality-gate-qa.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/ui-patterns.md`
- `.gstack/knowledge/visual-quality-bar.md`
- `.gstack/templates/ui-design-brief.template.md`
- `.gstack/templates/ui-polish-review.template.md`
- `.gstack/skills/README.md`
- `.gstack/skills/kk-task-kickoff/SKILL.md`
- `.gstack/skills/kk-ui-design-kickoff/SKILL.md`
- `.gstack/skills/kk-ui-polish-review/SKILL.md`
- `.gstack/templates/task-boundary.template.md`
- `.gstack/scripts/required_gates_audit.py`
- `.gstack/scripts/sync_repo_skills.sh`
- `.gstack/scripts/gstack_doctor.py`
- `scripts/init_project.py`
- `adapters/default/core_manifest.json`
- `tests/test_gstack_doctor_target_mode.py`
- `tests/test_productization_hardening.py`

## Forbidden Files

- `stack/`
- `archive/`
- `blueprint/`
- `shared/`
- `plugins/`
- `.agents/plugins/`
- `.env`、`.env.*`、`secrets/`
- 真实数据、生产配置、项目业务页面实现。

## Functional Non-goals

- 不直接重做任何 UI。
- 不引入 Figma 或外部设计服务。
- 不发布插件或执行 git workflow action。
- 不把私有 dogfood 项目的业务规则复制进公共骨架。

## User-visible Acceptance

- User-visible Change: no
- Expected Visible Behavior:
  - 后续目标项目 UI 任务可触发 `kk-ui-design-kickoff` 和 `kk-ui-polish-review`。
- User Actions To Verify:
  - 在目标项目查看 `.gstack/skills/kk-ui-design-kickoff/SKILL.md` 与 `.gstack/knowledge/visual-quality-bar.md`。
- Required Evidence: CLI 输出 / installer verify / doctor / tests。
- If No User-visible Change:
  本轮是骨架能力升级，不改业务页面。

## Generated Artifact Policy

- Surface Type: docs-only
- Acceptance URL: 不适用。
- Refresh / Regeneration: 目标项目通过 `scripts/init_project.py --apply-core` 或显式同步获得新文件。
- If No Visible Change: 本次不产生页面变化。
- Required Interaction Evidence: 不适用。

## Decision Mode

- Mode: 自主执行
- Source: user-this-task
- Internal Enum: codex-led
- Reason:
  用户已批准先在私有 dogfood 项目完善，再抽离公开骨架并同步到在线平台项目。

## Flow Lane

- Lane: fast-lane
- Reason:
  公共骨架侧是明确的低风险协作能力抽离，主要改文档、模板、skills 和安装器清单。
- Evidence Strategy:
  使用 fast-lane requirement、fast-lane review、boundary 和 QA。

## Autonomy Plan

- Codex May Do Without Asking:
  - 新增和同步公开骨架 UI 质量检查文件。
  - 更新安装器 portable core 清单和定向测试。
  - 运行本地验证。
- Codex Must Ask Before:
  - commit、push、PR、生产、DB、真实数据、破坏性命令。
- Gate Recovery:
  Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户。
- Goal Mode: not-used
  本轮可在当前会话完成。
- Local Restart: not-required

## Subagent Plan

- Mode: not-used
- Reason:
  文档和模板抽离范围清楚，无需 subagent。
- Main Agent Owns:
  - 公共骨架实现、目标项目同步和验证。
- Candidate Subagents:
  - name: not-used
    role: reviewer
    trigger stage: not-used
    write scope: read-only
    forbidden paths:
      - not-used
    output evidence: not-used
    status: not-used
- Result Integration:
  - 不使用 subagent。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-22_ui-quality-gate-fast-lane-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-22_ui-quality-gate-fast-lane-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-22_ui-quality-gate-fast-lane-requirement.md`
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-22_ui-quality-gate-fast-lane-review.md`
- domain-spec-readiness:
  status: done
  evidence: `.gstack/knowledge/ai-programming-framework.md`
- implement:
  status: done
  evidence: `.gstack/task-boundaries/2026-06-22_ui-quality-gate.md`
- qa:
  status: done
  command: `qa-only`
  evidence: `.gstack/qa-reports/2026-06-22_ui-quality-gate-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "不涉及真实数据、数据库、BI、接口接入或查数。"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ""
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "不涉及数据专项。"
  - gate_id: prototype-logic-extraction
    trigger_reason: "不涉及后端接口、读模型、service 或 snapshot 承接前端 / 原型业务逻辑。"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ""
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "不涉及原型逻辑迁移。"
  - gate_id: ui-design-quality
    trigger_reason: "本轮新增 UI 设计质量检查本身，需要定义触发条件、模板和 review 口径。"
    owner: kk-ui-design-kickoff
    required_before: implement
    status: done
    evidence_path: ".gstack/knowledge/visual-quality-bar.md"
    evidence_section: "UI Quality Gate"
    blocking_reason: ""
    done_criteria: "UI 风格路由、设计 brief、polish review 和 QA 口径已沉淀并可安装到目标项目。"
```

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `adapters/default/adapter.md`
- `adapters/default/runtime.json`

## Spec Sync Plan

- Spec Impact: updated
- Expected Spec Targets:
  - `.gstack/knowledge/ai-programming-framework.md`
  - `.gstack/knowledge/ui-patterns.md`
  - `.gstack/knowledge/visual-quality-bar.md`
  - `.gstack/skills/README.md`
  - `.gstack/skills/kk-task-kickoff/SKILL.md`
- Prototype Logic Evidence Sync: 不适用。
- Allowed No-Spec-Change Reason: 不适用。

## Verification

- `bash -n .gstack/scripts/sync_repo_skills.sh`
- `python3 -m unittest discover -s tests`
- `python3 scripts/init_project.py --adapter default --validate-adapter --report`
- `python3 scripts/init_project.py --adapter default --verify-runtime --report`
- `python3 .gstack/scripts/gstack_doctor.py check`
- `python3 .gstack/scripts/spec_sync_guard.py`
- 在 `kk-ai-factory` 验证 portable UI core 文件可用。

## Lessons To Write Back

- UI 质量检查属于 framework core；目标项目不应只获得脚本，还应获得设计 brief、visual quality bar 和 polish review skill。
