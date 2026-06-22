# Runtime Bundle Plugin Sync Task Boundary

- Task: 同步上游 dogfood 增强后的公共骨架与 Codex 插件
- 负责人: Codex
- 日期: 2026-06-18
- 相关 issue / doc: `.gstack/requirements/2026-06-18_runtime-bundle-plugin-sync-fast-lane-requirement.md`

## Goal

- 将上游 dogfood 项目中已验证的 runtime bundle installer 增强同步到 KK Dev Skeleton，并同步 Codex Adoption 插件，使插件能引导新版 `--apply-runtime` / `--verify-runtime` / pilot / runtime smoke 工作流。

## Allowed Files

- `.gstack/requirements/2026-06-18_runtime-bundle-plugin-sync-fast-lane-requirement.md`
- `.gstack/requirements/README.md`
- `.gstack/reviews/2026-06-18_runtime-bundle-plugin-sync-fast-lane-review.md`
- `.gstack/reviews/README.md`
- `.gstack/task-boundaries/2026-06-18_runtime-bundle-plugin-sync.md`
- `.gstack/qa-reports/2026-06-18_runtime-bundle-plugin-sync-qa.md`
- `.gstack/qa-reports/README.md`
- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/scripts/README.md`
- `.gstack/scripts/gstack_loop.py`
- `.gstack/scripts/gstack_loop_contract_smoke.py`
- `scripts/init_project.py`
- `adapters/default/adapter.md`
- `adapters/default/runtime.json`
- `adapters/default/core_manifest.json`
- `adapters/default/runtime_schema.json`
- `plugins/kk-dev-skeleton-adoption/**`
- personal plugin source `~/plugins/kk-dev-skeleton-adoption/**`

## Forbidden Files

- `stack/**`
- `archive/**`，除非只读
- `blueprint/**`
- `shared/**`
- `.gstack/data-access/**`
- 真实数据、生产配置、凭证、`.env*`
- marketplace 配置文件，除非用户另行明确要求
- git workflow action，除非用户另行明确批准

## Functional Non-goals

- 不做业务功能、不改应用源码、不新增后端接口或数据库。
- 不把上游 dogfood 业务路径、业务模块、真实数据工具或项目专属 skill 前缀写入公共框架核心。
- 不自动执行插件安装、marketplace upgrade、commit、push、PR 或发布。
- 不覆盖目标项目已有 runtime scripts；installer 仍保持 create-missing / preserve-existing。

## User-visible Acceptance

- User-visible Change:
  `yes`
- Expected Visible Behavior:
  - Codex 插件 skill 会提示并使用新版 adapter installer 能力。
  - 公共骨架 `scripts/init_project.py --apply-runtime --dry-run --report` 会展示 runtime bundle 安装预览。
  - `--verify-runtime --report` 会验证 runtime bundle 文件、Python compile、contract smoke、chat-smoke 和 nl-smoke。
- User Actions To Verify:
  - 通过插件 skill 文档、installer CLI 输出和 smoke 报告确认能力可见。
- Required Evidence:
  `CLI 输出、plugin validation、QA report`
- If No User-visible Change:
  `not-applicable`

## Generated Artifact Policy

- Surface Type:
  `CLI-output`
- Acceptance URL:
  `不适用；验收入口是插件 skill 文档、installer CLI、adapter metadata 和 smoke 输出。`
- Refresh / Regeneration:
  重新运行 `scripts/init_project.py --apply-runtime --dry-run --report`、`--verify-runtime --report` 或插件校验命令。
- If No Visible Change:
  检查是否仍在旧线程使用旧插件缓存；插件 manifest cachebuster 更新后需要新线程加载。
- Required Interaction Evidence:
  本轮不涉及 Browser / Chrome / Playwright 页面交互。

## Decision Mode

- Mode: `autonomous`
- Source:
  `repo-default`
- Internal Enum:
  `codex-led`
- Reason:
  用户要求同步插件更新，属于明确工程同步任务；代码结构、同步路径和验证组合由 Codex 在 boundary 内自主决定。

## Flow Lane

- Lane: `fast-lane`
- Reason:
  目标明确、范围集中、无业务口径多解、无真实数据 / 生产 / DB / git workflow，可用本地 smoke 和插件校验验证。
- Evidence Strategy:
  - 使用 fast-lane requirement、fast-lane review、boundary 和 QA。

## Autonomy Plan

- Codex May Do Without Asking:
  - 在 Allowed Files 内同步 installer、adapter metadata、runtime scripts、插件 skill 和 QA evidence。
  - 自主做去项目化替换、脚本编译、adapter validation、runtime smoke、plugin validation 和 cachebuster 更新。
  - 验证失败时先本地修复并重跑。
- Codex Must Ask Before:
  - 执行 commit、push、pull、PR、marketplace upgrade、plugin reinstall、生产、DB、真实数据、外部服务或破坏性操作。
  - 扩大范围到业务 `stack/`、真实数据配置或 marketplace 配置。
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户`
- Goal Mode:
  `not-used`
  当前任务可在本轮完成，不启用长期 goal。
- Local Restart:
  `not-required`

## Subagent Plan

- Mode: `not-used`
- Reason:
  本轮是集中同步和确定性验证；读写范围虽跨两个本地目录，但不需要并行 subagent。
- Main Agent Owns:
  - 源差异判断、实现同步、验证、QA evidence 和最终答复
- Candidate Subagents:
  - name: `none`
    role: `not-used`
    trigger stage: `not-used`
    write scope: `none`
    forbidden paths:
      - `stack/**`
      - `archive/**`
      - `blueprint/**`
      - `.gstack/data-access/**`
    output evidence: `not-used`
    status: `not-used`
- Result Integration:
  无 subagent 产物；main agent 直接写 QA。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-18_runtime-bundle-plugin-sync-fast-lane-requirement.md`
- plan review:
  status: done
  evidence: `.gstack/reviews/2026-06-18_runtime-bundle-plugin-sync-fast-lane-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-18_runtime-bundle-plugin-sync-fast-lane-requirement.md`
- engineering review:
  status: done
  evidence: `.gstack/reviews/2026-06-18_runtime-bundle-plugin-sync-fast-lane-review.md`
- source-of-truth readiness:
  status: done
  evidence: `.gstack/knowledge/ai-programming-framework.md`, `adapters/default/runtime_schema.json`
  note: 本轮是公共 framework / adapter / plugin，不需要应用业务 spec。
- implementation:
  status: done
  evidence: `scripts/init_project.py`, `adapters/default/*`, `.gstack/scripts/gstack_loop*.py`, `plugins/kk-dev-skeleton-adoption/**`
- QA:
  status: done
  command: qa-only
  evidence: `.gstack/qa-reports/2026-06-18_runtime-bundle-plugin-sync-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "本轮不涉及真实数据、接口、查数、数据源选择或跨系统复用"
    owner: kk-data-kickoff
    required_before: engineering review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-18_runtime-bundle-plugin-sync.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据源 / 接口 / 查数"
  - gate_id: prototype-logic-extraction
    trigger_reason: "本轮不涉及前端 / 原型业务逻辑迁移到后端"
    owner: kk-task-kickoff
    required_before: engineering review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-18_runtime-bundle-plugin-sync.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确没有前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent；本轮不启动 subagent"
    owner: kk-subagent-orchestrator
    required_before: implementation
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-18_runtime-bundle-plugin-sync.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；Mode: not-used 和原因已写明"
  - gate_id: plugin-validation
    trigger_reason: "本轮更新 Codex plugin source 和本地 personal plugin source"
    owner: template-review
    required_before: QA
    status: done
    evidence_path: ".gstack/qa-reports/2026-06-18_runtime-bundle-plugin-sync-qa.md"
    evidence_section: "证据"
    blocking_reason: ""
    done_criteria: "仓库插件源与个人插件源均通过 validate_plugin.py"
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
- `plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption/SKILL.md`
- Upstream dogfood source evidence: `.gstack/requirements/2026-06-17_runtime-script-bundle-install-fast-lane-requirement.md`
- Upstream dogfood source evidence: `.gstack/reviews/2026-06-17_runtime-script-bundle-install-fast-lane-review.md`
- Upstream dogfood source evidence: `.gstack/task-boundaries/2026-06-17_runtime-script-bundle-install.md`
- Upstream dogfood source evidence: `.gstack/qa-reports/2026-06-17_runtime-script-bundle-install-qa.md`

## Spec Sync Plan

- Spec Impact:
  `updated`
- Expected Spec Targets:
  - `scripts/init_project.py`
  - `adapters/default/adapter.md`
  - `adapters/default/runtime.json`
  - `adapters/default/core_manifest.json`
  - `adapters/default/runtime_schema.json`
  - `.gstack/scripts/README.md`
  - `.gstack/knowledge/ai-programming-framework.md`
  - `plugins/kk-dev-skeleton-adoption/README.md`
  - `plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption/SKILL.md`
- Prototype Logic Evidence Sync:
  `not-required`
- Allowed No-Spec-Change Reason:
  `not-applicable`

## Verification

```bash
python3 -m py_compile scripts/init_project.py .gstack/scripts/gstack_loop.py .gstack/scripts/gstack_loop_contract_smoke.py
python3 scripts/init_project.py --adapter default --apply-runtime --dry-run --report
python3 scripts/init_project.py --adapter default --validate-adapter --report
python3 scripts/init_project.py --adapter default --verify --verify-core --verify-runtime --report
python3 scripts/init_project.py --adapter default --pilot --report
python3 .gstack/scripts/gstack_loop_contract_smoke.py --format json
python3 .gstack/scripts/gstack_loop.py chat-smoke --format json
python3 .gstack/scripts/gstack_loop.py nl-smoke --format json
python3 .gstack/scripts/natural_language_dev_smoke.py --format user
python3 .gstack/scripts/spec_sync_guard.py
python3 <plugin-creator>/scripts/validate_plugin.py plugins/kk-dev-skeleton-adoption
python3 <plugin-creator>/scripts/validate_plugin.py ~/plugins/kk-dev-skeleton-adoption
git diff --check
```

## Lessons To Write Back

- 如发现插件同步遗漏导致 adoption skill 与 skeleton helper 脱节，回写到 `.gstack/knowledge/ai-programming-framework.md` 或插件 README。

## 本地激活

- 本轮执行：
  `bash .gstack/scripts/use_boundary.sh .gstack/task-boundaries/2026-06-18_runtime-bundle-plugin-sync.md`
