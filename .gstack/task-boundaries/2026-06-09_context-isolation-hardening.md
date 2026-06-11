# Task Boundary：context-isolation-hardening

- Task: context-isolation-hardening
- 负责人: Codex
- 日期: 2026-06-09
- 相关 issue / doc:
  - `.gstack/requirements/2026-06-09_context-isolation-hardening.md`
  - `.gstack/reviews/2026-06-09_context-isolation-hardening-review.md`

## Goal

- 防止公开骨架从父目录路径、全局 skill 列表或旧项目上下文推断当前项目身份，保证中文团队使用时不串味。

## Allowed Files

- `README.md`
- `AGENTS.md`
- `.gstack/README.md`
- `.gstack/knowledge/**`
- `.gstack/scripts/gstack_doctor.py`
- `.gstack/scripts/sync_repo_skills.sh`
- `.gstack/requirements/2026-06-09_context-isolation-hardening.md`
- `.gstack/reviews/2026-06-09_context-isolation-hardening-review.md`
- `.gstack/task-boundaries/2026-06-09_context-isolation-hardening.md`
- `.gstack/qa-reports/2026-06-09_context-isolation-hardening-qa.md`

## Forbidden Files

- `.env`
- `.env.*`
- `secrets/**`
- production configs
- real data
- `.gstack/skills/kk-*/SKILL.md`
- `examples/simple-web-app/**`

## Functional Non-goals

- 不默认删除用户本机 `tg-*` skills。
- 不改 `kk-*` skill 命名。
- 不发布。
- 不执行代码提交流程。

## User-visible Acceptance

- User-visible Change:
  `yes`
- Expected Visible Behavior:
  - AGENTS 和 README 明确说明不能从父路径、全局 skill 或旧项目缓存推断项目名。
  - doctor 对外部 `tg-*` skills 和可疑父路径给出中文提醒。
  - skill 同步脚本默认只同步 `kk-*`，并提供显式选项清理 `tg-*` symlink。
- User Actions To Verify:
  - 运行 `python3 .gstack/scripts/gstack_doctor.py check`。
  - 阅读 `README.md` 的串味排查说明。
  - 运行 `bash .gstack/scripts/sync_repo_skills.sh --help`。
- Required Evidence:
  `CLI 输出 / QA 报告`
- If No User-visible Change:
  不适用。

## Generated Artifact Policy

- Surface Type:
  `CLI-output / docs-only`
- Acceptance URL:
  `不适用`
- Refresh / Regeneration:
  重新运行 doctor 和 sync 脚本。
- If No Visible Change:
  不适用。
- Required Interaction Evidence:
  不涉及 HTML 交互。

## Decision Mode

- Mode: `autonomous`
- Source:
  `user-reported`
- Internal Enum:
  `codex-led`
- Reason:
  用户报告使用体验异常，原因可由本地证据证明，修复风险低。

## Flow Lane

- Lane: `fast-lane`
- Reason:
  范围明确、低风险、可本地验证。
- Evidence Strategy:
  - fast-lane requirement, review, boundary, QA.

## Autonomy Plan

- Codex May Do Without Asking:
  - 修改上下文隔离规则、doctor 提示和 sync 脚本。
  - 运行本地验证。
- Codex Must Ask Before:
  - 删除用户本机仍可能需要的非 symlink skill 目录。
  - 执行 git workflow action。
  - 发布外部仓库。
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户`
- Goal Mode:
  `not-used`
- Local Restart:
  `not-required`

## Subagent Plan

- Mode: `not-used`
- Reason:
  小范围文档和脚本加固，无需 subagent。
- Main Agent Owns:
  - context isolation hardening
  - QA evidence
- Candidate Subagents:
  - name: `not-used`
    role: `reviewer`
    trigger stage: `qa`
    write scope: `read-only`
    forbidden paths:
      - `**`
    output evidence: `.gstack/qa-reports/2026-06-09_context-isolation-hardening-qa.md`
    status: `not-used`
- Result Integration:
  - 不适用。

## GStack Required Flow

- requirement-brief:
  status: `done`
  evidence: `.gstack/requirements/2026-06-09_context-isolation-hardening.md`
- plan-ceo-review:
  status: `done`
  evidence: `.gstack/reviews/2026-06-09_context-isolation-hardening-review.md`
- requirement-freeze:
  status: `done`
  evidence: `.gstack/requirements/2026-06-09_context-isolation-hardening.md`
- plan-eng-review:
  status: `done`
  evidence: `.gstack/reviews/2026-06-09_context-isolation-hardening-review.md`
- domain-spec-readiness:
  status: `done`
  evidence: `.gstack/knowledge/context-isolation.md`
- implement:
  status: `done`
  evidence: `README.md AGENTS.md .gstack/scripts/gstack_doctor.py .gstack/scripts/sync_repo_skills.sh`
- qa:
  status: `done`
  command: `qa-only`
  evidence: `.gstack/qa-reports/2026-06-09_context-isolation-hardening-qa.md`

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
    trigger_reason: "本次只调整协作规则和本地脚本，没有业务逻辑承接。"
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
    evidence_path: ".gstack/task-boundaries/2026-06-09_context-isolation-hardening.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "已声明不使用 subagent"
```

## Required Knowledge

- `.gstack/knowledge/CODEMAP.md`
- `.gstack/knowledge/doc-placement.md`
- `.gstack/knowledge/ai-programming-framework.md`

## Spec Sync Plan

- Spec Impact:
  `not-required`
- Expected Spec Targets:
  - `.gstack/knowledge/context-isolation.md`
- If Not Required, Why:
  本次不改变应用业务行为、接口、数据模型或持久化；只加固公开骨架协作层。

## Verification

- `python3 .gstack/scripts/gstack_doctor.py check`
- `python3 .gstack/scripts/gstack_doctor.py check --format json | python3 -m json.tool`
- `bash -n .gstack/scripts/sync_repo_skills.sh`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `python3 .gstack/scripts/natural_language_dev_smoke.py --format user`

## Lessons To Write Back

- 公开骨架必须防止 agent 把父目录名、全局 skill 列表或旧项目缓存当成当前项目语义。
