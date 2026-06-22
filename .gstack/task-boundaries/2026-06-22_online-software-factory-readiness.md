# Online Software Factory Readiness Task Boundary

- Task: 升级 KK Dev Skeleton 支持纯线上 AI Software Factory 平台
- 负责人: Codex
- 日期: 2026-06-22
- 相关 requirement: `.gstack/requirements/2026-06-22_online-software-factory-readiness-standard-requirement.md`

## Goal

把上游 dogfood 项目中已经验证的 AI 原生开发流程线上化协议抽象回公共 KK Dev Skeleton，使现有骨架成为未来纯线上 AI Software Factory 平台的底层协议、adapter metadata 和 runtime bundle 上游。

## Allowed Files

- `.gstack/requirements/2026-06-22_online-software-factory-readiness-standard-requirement.md`
- `.gstack/reviews/2026-06-22_online-software-factory-readiness-standard-review.md`
- `.gstack/task-boundaries/2026-06-22_online-software-factory-readiness.md`
- `.gstack/qa-reports/2026-06-22_online-software-factory-readiness-qa.md`
- `.gstack/requirements/2026-06-18_runtime-bundle-plugin-sync-fast-lane-requirement.md`
- `.gstack/reviews/2026-06-18_runtime-bundle-plugin-sync-fast-lane-review.md`
- `.gstack/task-boundaries/2026-06-18_runtime-bundle-plugin-sync.md`
- `.gstack/qa-reports/2026-06-18_runtime-bundle-plugin-sync-qa.md`
- `.gstack/designs/2026-06-22_online-software-factory-platform-protocol.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/README.md`
- `README.md`
- `CODEX_ADOPTION_CONNECTOR.md`
- `adapters/default/adapter.md`
- `adapters/default/runtime.json`
- `adapters/default/runtime_schema.json`
- `scripts/init_project.py`
- `plugins/kk-dev-skeleton-adoption/README.md`
- `plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption/SKILL.md`
- `tests/test_init_project.py`
- `tests/test_online_flow_protocol.py`
- `tests/test_productization_hardening.py`

## Forbidden Files

- `stack/**`
- `examples/**`
- `archive/**`，除非只读
- `blueprint/**`
- `shared/**`
- `.gstack/data-access/**`
- `.agents/plugins/**`
- `plugins/**/plugin.json`
- 真实数据、生产配置、凭证、`.env*`
- git workflow action，除非用户另行明确批准

## Functional Non-goals

- 不建设 Web 平台、API、数据库、远程 runner、MCP 或后台服务。
- 不调用 Codex SDK、GitHub API、webhook、服务器、生产环境或真实数据源。
- 不重新抽新骨架，不创建第二套公共 skeleton。
- 不把项目专属业务路径、非公共 skill 前缀、业务 scope 或真实数据工具写入公共框架核心。
- 不执行 commit、push、pull、branch、PR、发布、marketplace 安装或插件发布。
- 不覆盖目标项目已有 adapter 或 runtime scripts。

## User-visible Acceptance

- User-visible Change:
  `yes`
- Expected Visible Behavior:
  - 维护者能从公共骨架文档理解纯线上平台、Codex runner 和 repo evidence 如何协作。
  - 默认 adapter runtime 暴露 `online_flow_protocol`，未来平台可读取对象、状态、授权和 evidence 映射。
  - Codex adoption plugin 说明现有项目如何升级到 online-flow-ready 骨架。
  - 骨架 tests 能防止协议缺失或项目专属内容泄漏。
- User Actions To Verify:
  - 阅读协议文档、adapter 说明和插件 README。
  - 运行 adapter validation、runtime smoke 和 focused pytest。
- Required Evidence:
  `.gstack/qa-reports/2026-06-22_online-software-factory-readiness-qa.md`

## Generated Artifact Policy

- Surface Type:
  `docs-and-cli-output`
- Acceptance URL:
  `不适用；本轮没有 Web UI。`
- Refresh / Regeneration:
  重新运行 `python3 scripts/init_project.py --adapter default --validate-adapter --report`、`--verify-runtime --report` 和 `python3 -m pytest tests/test_online_flow_protocol.py`。
- If No Visible Change:
  检查是否阅读的是旧插件缓存或旧发布仓库；本地仓库以当前工作树文档为准。
- Required Interaction Evidence:
  本轮不涉及 Browser / Chrome / Playwright 页面交互。

## Decision Mode

- Mode: `autonomous`
- Source: `user-approved`
- Internal Enum: `codex-led`
- Reason:
  用户已确认“先更新升级 ai-dev-skeleton”；本轮不涉及高风险动作，工程落点和验证组合由 Codex 自主处理。

## Flow Lane

- Lane: `standard`
- Reason:
  涉及公共骨架协议、adapter metadata、插件文档和 tests，影响面跨多个协作层；虽不涉及业务实现，但需要完整 requirement / review / boundary / QA evidence。

## Autonomy Plan

- Codex May Do Without Asking:
  - 在 Allowed Files 内新增和更新公共协议、adapter metadata、插件说明和测试。
  - 自主做去项目化措辞、schema 调整、测试补充、验证失败修复和 QA evidence。
- Codex Must Ask Before:
  - 扩大到 Web 平台实现、远程 runner、GitHub API、插件发布、marketplace 配置、生产、DB、真实数据、外部服务或 git workflow action。
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户。`
- Goal Mode:
  `not-used`
  当前任务可在本轮完成，不启用长期 goal。

## Subagent Plan

- Mode: `not-used`
- Reason:
  本轮是公共骨架文档 / metadata / tests 的集中升级，主 agent 可直接完成并验证。
- Main Agent Owns:
  - 协议抽象、实现改动、测试、QA evidence 和最终汇报。
- Candidate Subagents:
  - name: `none`
    role: `not-used`
    trigger stage: `not-used`
    write scope: `none`
    forbidden paths:
      - `stack/**`
      - `examples/**`
      - `archive/**`
      - `shared/**`
      - `.agents/plugins/**`
    output evidence: `not-used`
    status: `not-used`
- Result Integration:
  无 subagent 产物；main agent 直接写 QA。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-22_online-software-factory-readiness-standard-requirement.md`
- plan review:
  status: done
  evidence: `.gstack/reviews/2026-06-22_online-software-factory-readiness-standard-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-22_online-software-factory-readiness-standard-requirement.md`
- engineering review:
  status: done
  evidence: `.gstack/reviews/2026-06-22_online-software-factory-readiness-standard-review.md`
- source-of-truth readiness:
  status: done
  evidence: `.gstack/knowledge/ai-programming-framework.md`, `adapters/default/runtime.json`
  note: 本轮是公共 framework / adapter 协议升级，不需要应用业务 spec。
- implementation:
  status: done
  evidence: `.gstack/designs/2026-06-22_online-software-factory-platform-protocol.md`, `.gstack/knowledge/ai-programming-framework.md`, `adapters/default/runtime.json`, `scripts/init_project.py`, `plugins/kk-dev-skeleton-adoption/**`, `tests/test_online_flow_protocol.py`
- QA:
  status: done
  command: qa-only
  evidence: `.gstack/qa-reports/2026-06-22_online-software-factory-readiness-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "本轮不涉及真实数据、接口、查数、数据源选择或跨系统复用"
    owner: kk-data-kickoff
    required_before: engineering review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-22_online-software-factory-readiness.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据源 / 接口 / 查数"
  - gate_id: prototype-logic-extraction
    trigger_reason: "本轮不涉及前端 / 原型业务逻辑迁移到后端"
    owner: kk-task-kickoff
    required_before: engineering review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-22_online-software-factory-readiness.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确没有前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent；本轮不启动 subagent"
    owner: kk-subagent-orchestrator
    required_before: implementation
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-22_online-software-factory-readiness.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；Mode: not-used 和原因已写明"
  - gate_id: doc-backfill
    trigger_reason: "本轮需要把上游 dogfood 已验证的线上化协议回填成公共骨架真源"
    owner: kk-doc-backfill
    required_before: QA
    status: done
    evidence_path: ".gstack/designs/2026-06-22_online-software-factory-platform-protocol.md"
    evidence_section: "全部"
    blocking_reason: ""
    done_criteria: "公共协议、framework 文档、adapter metadata 和插件说明已同步"
```

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/knowledge/implementation-guide.md`
- `.gstack/knowledge/qa-dimensions.md`
- `.gstack/task-boundaries/CURRENT.md`
- `adapters/default/adapter.md`
- `adapters/default/runtime.json`
- `plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption/SKILL.md`
- Upstream dogfood source evidence: `.gstack/designs/2026-06-18_online-ai-dev-flow-platform-protocol-design.md`
- Upstream dogfood source evidence: `.gstack/designs/2026-06-18_ai-native-development-workflow-map-design.md`

## Spec Sync Plan

- Spec Impact:
  `updated`
- Expected Spec Targets:
  - `.gstack/designs/2026-06-22_online-software-factory-platform-protocol.md`
  - `.gstack/knowledge/ai-programming-framework.md`
  - `adapters/default/adapter.md`
  - `adapters/default/runtime.json`
  - `scripts/init_project.py`
  - `plugins/kk-dev-skeleton-adoption/README.md`
  - `plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption/SKILL.md`
  - `tests/test_init_project.py`
  - `tests/test_online_flow_protocol.py`
- Prototype Logic Evidence Sync:
  `not-required`
- Allowed No-Spec-Change Reason:
  `not-applicable`

## Verification

```bash
python3 tests/test_online_flow_protocol.py
python3 -m unittest tests.test_init_project
python3 scripts/init_project.py --adapter default --validate-adapter --report
python3 scripts/init_project.py --adapter default --verify-runtime --report
python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user
python3 .gstack/scripts/natural_language_dev_smoke.py --format user
python3 .gstack/scripts/spec_sync_guard.py
git diff --check
```

## Lessons To Write Back

- 如果发现公共协议仍需要依赖上游 dogfood 业务概念，应回写到 `.gstack/knowledge/ai-programming-framework.md` 的 Core / Adapter 分界。
