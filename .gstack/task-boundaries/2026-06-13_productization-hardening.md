# productization-hardening Task Boundary

- Task: productization-hardening
- 负责人: Codex
- 日期: 2026-06-13
- 相关 issue / doc: `.gstack/requirements/2026-06-13_productization-hardening-fast-lane-requirement.md`

## Goal

- 修复当前本机可自动处理的 doctor warning，并把接入产品化硬化为更确定的本地准备入口、普通用户短文档和更准确的 doctor 诊断。

## Allowed Files

- `.gstack/requirements/2026-06-13_productization-hardening-fast-lane-requirement.md`
- `.gstack/reviews/2026-06-13_productization-hardening-fast-lane-review.md`
- `.gstack/task-boundaries/2026-06-13_productization-hardening.md`
- `.gstack/qa-reports/2026-06-13_productization-hardening-qa.md`
- `.gstack/scripts/gstack_doctor.py`
- `.gstack/scripts/sync_repo_skills.sh`
- `.gstack/scripts/install_git_hooks.sh`
- `.gstack/knowledge/CODEMAP.md`
- `README.md`
- `COMPANY_ADOPTION_GUIDE.md`
- `CODEX_ADOPTION_CONNECTOR.md`
- `plugins/PARTNER_INSTALL.md`
- `QUICK_START_FOR_PARTNERS.md`
- `scripts/setup_local_codex.sh`
- `tests/**`
- 本机 `~/.codex/skills` 中 repo-native kk-* symlink 和可清理的 tg-* symlink
- 本仓库 `.git/config` 的 `core.hooksPath`

## Forbidden Files

- `<private-source-project>/**`
- `<pilot-project>/**`
- 真实试点项目代码
- `.env*`、真实凭证、生产配置、真实客户数据
- 当前机器 Codex plugin cache / personal marketplace，除非只做只读诊断
- git workflow action，除非用户另行明确批准

## Functional Non-goals

- 不重写整个插件安装机制。
- 不移动真实项目代码。
- 不删除普通目录形式的外部 skills。
- 不把内部工程概念从完整文档中删除。
- 不发布 / commit / push。

## User-visible Acceptance

- Codex 可以用确定性脚本完成本地准备，而不是手动记多条命令。
- 普通伙伴有一份短入口文档，不需要理解内部术语即可开始。
- doctor 输出更符合产品化语义：真实串味风险 warn，单纯父目录命名只提示。
- hooks 接入和 skills 同步可被验证。

## Generated Artifact Policy

- User-visible Change: `yes`
- Artifact Type: `markdown docs, shell helper, python doctor behavior, unit tests, QA report`
- Acceptance Surface:
  - `QUICK_START_FOR_PARTNERS.md`
  - `scripts/setup_local_codex.sh`
  - `.gstack/scripts/gstack_doctor.py`
- Browser QA: `not-required`
- Reason:
  本次不改变 Web UI、HTML、dashboard 或可视化交互。

## Decision Mode

- Mode: `自主执行`
- Source: `user-request`
- Internal Enum: `codex-led`
- Reason:
  用户给出明确评阅和优先级，希望继续完善。

## Flow Lane

- Lane: `fast-lane`
- Reason:
  产品化硬化范围明确，不涉及业务口径、真实数据、DB schema、生产操作或 UI。

## Autonomy Plan

- Codex May Do Without Asking:
  - 在 Allowed Files 内实现。
  - 运行本机 skills 同步和 hooks 安装脚本。
  - 运行本地测试、doctor 和 guards。
- Codex Must Ask Before:
  - 删除非 symlink 的外部 skills。
  - 修改真实业务项目。
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
  fast-lane 小任务由 main agent 直接完成。

## GStack Required Flow

- requirement-brief:
  status: done
  evidence: `.gstack/requirements/2026-06-13_productization-hardening-fast-lane-requirement.md`
- plan-ceo-review:
  status: done
  evidence: `.gstack/reviews/2026-06-13_productization-hardening-fast-lane-review.md`
- requirement-freeze:
  status: done
  evidence: `.gstack/requirements/2026-06-13_productization-hardening-fast-lane-requirement.md`
  note: fast-lane requirement 同时作为 requirement freeze。
- plan-eng-review:
  status: done
  evidence: `.gstack/reviews/2026-06-13_productization-hardening-fast-lane-review.md`
- domain-spec-readiness:
  status: not-required
  evidence: `.gstack/task-boundaries/2026-06-13_productization-hardening.md`
  note: 本次不改变具体应用 stack domain 产品或工程真源。
- implement:
  status: done
  evidence: `.gstack/task-boundaries/2026-06-13_productization-hardening.md`
- qa:
  status: done
  evidence: `.gstack/qa-reports/2026-06-13_productization-hardening-qa.md`

## Required Gates

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "本任务不涉及真实数据、接口、查数或数据源选择"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-13_productization-hardening.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及数据源 / 接口 / 查数"
  - gate_id: data-query
    trigger_reason: "本任务不涉及复杂查数或高风险指标"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-13_productization-hardening.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不需要 Query Brief、SQL 或查询 review"
  - gate_id: prototype-logic-extraction
    trigger_reason: "本任务不迁移原型或旧项目业务逻辑"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-13_productization-hardening.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "已明确不涉及前端 / 原型逻辑抽取"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/2026-06-13_productization-hardening.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；本轮不使用 subagent"
  - gate_id: doc-backfill
    trigger_reason: "本任务新增产品化文档，不是从已有代码反推文档"
    owner: kk-doc-backfill
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-13_productization-hardening.md"
    evidence_section: "Required Gates"
    blocking_reason: ""
    done_criteria: "新增文档同步创建，不需要从代码反推"
  - gate_id: data-knowledge-sync
    trigger_reason: "本任务不新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: ".gstack/task-boundaries/2026-06-13_productization-hardening.md"
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

## Spec Sync Plan

- Spec Impact: `not-required`
- Expected Spec Targets:
  - 不适用
- Allowed No-Spec-Change Reason:
  本次为公共骨架产品化入口、doctor 和本地准备能力增强，不改变具体应用 stack domain 产品或工程真源。

## Verification

- `bash -n scripts/setup_local_codex.sh`
- `python3 -m py_compile .gstack/scripts/gstack_doctor.py`
- `python3 -m unittest discover -s tests -p 'test_*.py'`
- `bash scripts/setup_local_codex.sh --remove-tg-links`
- `python3 .gstack/scripts/gstack_doctor.py check`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`
- `python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-13_productization-hardening.md`

## Lessons To Write Back

- 如发现新坑，写入 `.gstack/knowledge/` 或 `.gstack/rules/`。
