# codex-git-marketplace-publish Task Boundary

- Task: codex-git-marketplace-publish
- 负责人: Codex
- 日期: 2026-06-11
- 相关 issue / doc: `.gstack/requirements/2026-06-11_codex-git-marketplace-publish-fast-lane-requirement.md`

## Goal

- 发布 KK Dev Skeleton 到 GitHub Git marketplace：补充 duanxibo/kk-ai-dev-skeleton 安装说明，验证 plugin/marketplace，并初始化 git commit/push 到用户提供的发布仓库

## Allowed Files

- .gstack/requirements/2026-06-11_codex-git-marketplace-publish-fast-lane-requirement.md
- .gstack/reviews/2026-06-11_codex-git-marketplace-publish-fast-lane-review.md
- .gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md
- .gstack/qa-reports/2026-06-11_codex-git-marketplace-publish-qa.md
- plugins/PARTNER_INSTALL.md
- plugins/MARKETPLACE_INSTALL.md
- plugins/MARKETPLACE_ROLLOUT.md
- plugins/ADMIN_INSTALL_CHECKLIST.md
- plugins/README.md
- .agents/plugins/README.md
- README.md
- COMPANY_ADOPTION_GUIDE.md
- CODEX_ADOPTION_CONNECTOR.md
- tests/test_git_marketplace_publish_docs.py
- tests/test_marketplace_rollout_docs.py

## Forbidden Files

- V2 plugin manifest / skill 内容：`plugins/kk-dev-skeleton-adoption/**`
- repo-local marketplace manifest：`.agents/plugins/marketplace.json`
- 当前机器 Codex plugin 安装状态
- 个人 marketplace：`~/.agents/plugins/marketplace.json`
- 数据库配置、真实凭证、`.env*`、`.gstack/data-access/*.local.*`
- git workflow action，除非用户另行明确批准；本次用户已提供 GitHub 发布仓库并要求“存放在这里，进行发布”，视为本次 `git init / remote add / commit / push` 的明确授权。

## Functional Non-goals

- 不发布到官方公共 marketplace。
- 不修改 plugin manifest、plugin skill 或 marketplace manifest。
- 不在当前 Codex 环境安装 plugin。
- 不写个人 marketplace。
- 不做远程权限服务、MCP server 或 app UI。
- 不接触真实数据、生产、数据库或部署系统。

## User-visible Acceptance

- 文档给出伙伴可直接复制给 Codex 的自然语言安装提示。
- 文档给出 Git marketplace 等价命令，方便管理员或 Codex 执行。
- 文档明确目标 GitHub 仓库：`https://github.com/duanxibo/kk-ai-dev-skeleton.git`。
- 本地验证 plugin、skill、marketplace 和文档结构。
- 当前骨架被初始化为 git 仓库并推送到 `duanxibo/kk-ai-dev-skeleton.git`。

## Generated Artifact Policy

- User-visible Change: `no`
- Artifact Type: `published Git marketplace repository and markdown install docs`
- Acceptance Surface:
  - `plugins/PARTNER_INSTALL.md`
  - Git remote `https://github.com/duanxibo/kk-ai-dev-skeleton.git`
  - plugin / marketplace validation output
- Browser QA: `not-required`
- Reason:
  本次不生成 HTML、页面、dashboard、截图或交互 UI；验收面是 Git marketplace 发布、安装文档和命令验证。

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
    output evidence: `.gstack/qa-reports/2026-06-11_codex-git-marketplace-publish-qa.md`
    status: `not-used`
- Result Integration:
  - 本轮验证结果写入 QA 报告和 final summary。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-11_codex-git-marketplace-publish-fast-lane-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-11_codex-git-marketplace-publish-fast-lane-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-11_codex-git-marketplace-publish-fast-lane-requirement.md`
  note: fast-lane requirement 同时作为 requirement freeze。
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-11_codex-git-marketplace-publish-fast-lane-review.md`
- domain-spec-readiness:
  status: not-required
  evidence: `.gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md`
  note: 本次 fast-lane 小需求不改变 stack domain 产品或工程真源。
- implement:
  status: done
  evidence: `.gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md`
- qa:
  status: done
  command: qa-only
  evidence: `.gstack/qa-reports/2026-06-11_codex-git-marketplace-publish-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "AI 已确认 fast-lane 不涉及真实数据、接口、查数或数据源选择；如实现中发现涉及，必须退出 fast-lane 或改为 planned"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确本任务不涉及数据源 / 接口 / 查数"
  - gate_id: data-query
    trigger_reason: "AI 已确认 fast-lane 不涉及复杂查数或高风险指标"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不需要 Query Brief、SQL 或查询 review"
  - gate_id: prototype-logic-extraction
    trigger_reason: "AI 已确认 fast-lane 不涉及前端 / 原型业务逻辑迁后端"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确没有前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；本轮不使用 subagent"
  - gate_id: doc-backfill
    trigger_reason: "AI 已确认 fast-lane 不是代码已有但文档缺失的 backfill 场景"
    owner: kk-doc-backfill
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "新增文档同步创建，不需要从代码反推"
  - gate_id: data-knowledge-sync
    trigger_reason: "AI 已确认 fast-lane 不新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据知识同步"
```

## Required Knowledge

- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
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

- `python3 -m unittest tests/test_git_marketplace_publish_docs.py`
- `python3 -m unittest tests/test_marketplace_rollout_docs.py`
- `python3 -m unittest tests/test_plugin_marketplace.py`
- `python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/kk-dev-skeleton-adoption`
- `python3 /Users/edy/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption`
- `python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py --marketplace-path .agents/plugins/marketplace.json`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`
- `python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md`
- `rg --hidden -n "(sk-[A-Za-z0-9_-]{20,}|BEGIN (RSA|OPENSSH|PRIVATE) KEY|AKIA[0-9A-Z]{16})" . -g '!*.pyc' -g '!__pycache__/**' -S`
- `git status --short --ignored`
- `git push -u origin main`

## Lessons To Write Back

- 如发现新坑，写入 `.gstack/knowledge/` 或 `.gstack/rules/`。

## 本地激活

- 自动激活时由 `python3 .gstack/scripts/autopilot_bootstrap.py ... --activate` 写入本机 `CURRENT.local.md`。
