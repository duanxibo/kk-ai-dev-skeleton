# Task Boundary: target-aware doctor

## Goal

长期修复 `gstack_doctor.py` 的仓库身份判断：骨架源仓库继续检查完整发放清单，安装后的目标仓库只检查 portable collaboration core、adapter metadata 和 runtime bundle 所需入口，避免 `kk-ai-factory` 这类目标项目因缺少源仓库发布资料而 fail。

## Allowed Files

- `.gstack/scripts/gstack_doctor.py`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/requirements/2026-06-22_target-aware-doctor-fast-lane-requirement.md`
- `.gstack/reviews/2026-06-22_target-aware-doctor-fast-lane-review.md`
- `.gstack/task-boundaries/2026-06-22_target-aware-doctor.md`
- `.gstack/qa-reports/2026-06-22_target-aware-doctor-qa.md`
- `tests/test_productization_hardening.py`
- `tests/test_gstack_doctor_target_mode.py`
- 当前本机目标项目 `kk-ai-factory` 的 `.gstack/scripts/gstack_doctor.py`，仅用于把已修复 runtime script 同步到当前目标项目后做验证；长期文档不记录本机绝对路径。

## Forbidden Files

- `stack/`
- `blueprint/`
- `archive/`
- `shared/`
- `plugins/`
- `.agents/plugins/`
- 目标项目业务实现文件。
- `.env`、`.env.*`、`secrets/`、真实数据、生产配置。

## Functional Non-goals

- 不开发线上 AI Software Factory 平台。
- 不改变 portable core 或 runtime bundle 的文件清单，除非测试证明必须同步。
- 不自动覆盖所有既有目标项目 runtime 文件的升级策略。
- 不清理全局 Codex skills。
- 不执行 git workflow action。

## User-visible Acceptance

- 在骨架源仓库运行 doctor 时，`core-docs` 仍覆盖 partner / plugin / marketplace / setup 等 source-only docs。
- 在安装后的目标仓库运行 doctor 时，`core-docs` 不再要求 `QUICK_START_FOR_PARTNERS.md`、`COMPANY_ADOPTION_GUIDE.md`、`plugins/`、`.agents/plugins/`、`archive/baseline/README.md` 等源仓库资料。
- `kk-ai-factory` 的 doctor 不再因 source-only docs 缺失而整体 fail；若仍有本机 skill 或 git hooks 提醒，应保持 warn 而不是 fail。

## Generated Artifact Policy

- Artifact Type：Python doctor behavior、unit test、QA evidence。
- 本次没有 HTML、前端、可视化或浏览器交互产物。
- 用户通过重新运行 `python3 .gstack/scripts/gstack_doctor.py check` 验证结果。

## Decision Mode

- Mode: 自主执行
- Source: repo-default
- Internal Enum: codex-led
- Reason:
  本次为低风险脚本修复；不涉及业务口径、生产、DB、真实数据或 git action。

## Flow Lane

- Lane: fast-lane
- Reason:
  问题明确、影响面局部、可通过本地命令和临时目标仓库回归验证。
- Evidence Strategy:
  使用 fast-lane requirement、fast-lane review、boundary 和 QA evidence。

## Autonomy Plan

- Codex May Do Without Asking:
  - 文档证据、脚本修改、测试、门禁恢复和本地目标项目 doctor 验证。
- Codex Must Ask Before:
  - commit、push、branch、PR、生产、DB、破坏性命令。
- Gate Recovery:
  Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户。
- Goal Mode: not-used
  原因：小范围 fast-lane 修复，不需要跨轮 goal tracking。
- Local Restart: not-required

## Subagent Plan

- Mode: not-used
- Reason:
  单脚本诊断逻辑和小范围测试，无需并行 agent。
- Main Agent Owns:
  - 流程控制、active boundary、最终集成、最终答复。
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
  - 不使用 subagent，无需结果集成。

## GStack Required Flow

- requirement-brief：done，`.gstack/requirements/2026-06-22_target-aware-doctor-fast-lane-requirement.md`
- plan-ceo-review：done，`.gstack/reviews/2026-06-22_target-aware-doctor-fast-lane-review.md`
- requirement-freeze：done，fast-lane requirement 同时作为 freeze。
- plan-eng-review：done，fast-lane review 同时作为 engineering review。
- domain-spec-readiness：done，本次为 framework core doctor 行为，真源同步到 `.gstack/knowledge/ai-programming-framework.md`。
- implement：planned。
- qa/qa-only：planned。

## Required Gates

- data-access：not-required；不访问真实数据、数据库、BI 或业务数据源。
- data-query：not-required；不写 SQL，不查数。
- prototype-logic-extraction：not-required；不从 prototype / mock 承接业务逻辑。
- data-knowledge-sync：not-required；不新增表、接口、读模型或数据产品。
- ui-interaction-qa：not-required；无 UI / HTML / 可视化改动。
- doc-backfill：not-required；本次是明确前向修复，不是从代码反推缺文档。

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/implementation-guide.md`
- `.gstack/knowledge/qa-dimensions.md`
- `adapters/default/adapter.md`
- `adapters/default/runtime.json`

## Spec Sync Plan

- Spec Impact: updated
- Expected Spec Targets:
  - `.gstack/knowledge/ai-programming-framework.md`
- Prototype Logic Evidence Sync:
  不适用。
- Allowed No-Spec-Change Reason:
  不适用；本次会更新 framework core knowledge。
- Plan:
  - 更新 `.gstack/knowledge/ai-programming-framework.md`，记录 doctor 必须 target-aware：源仓库检查发放清单，目标仓库检查 portable core 和 runtime essentials。
  - QA evidence 记录源仓库和目标仓库验证结果。

## Verification

- `python3 -m py_compile .gstack/scripts/gstack_doctor.py`
- `python3 -m unittest tests.test_gstack_doctor_target_mode tests.test_productization_hardening`
- `python3 scripts/init_project.py --adapter default --validate-adapter --report`
- `python3 scripts/init_project.py --adapter default --verify-runtime --report`
- `python3 .gstack/scripts/spec_sync_guard.py`
- 在当前本机目标项目 `kk-ai-factory` 运行 `python3 .gstack/scripts/gstack_doctor.py check`

## Lessons To Write Back

- 记录到 `.gstack/knowledge/ai-programming-framework.md`：doctor 必须基于 repo mode 分层检查，不得把 skeleton source-only docs 当成 target repo 必需文件。
