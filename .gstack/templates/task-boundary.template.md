# Task Boundary 模板

- Task:
- 负责人:
- 日期:
- 相关 issue / doc:

## Goal

- 这次要完成什么

## Allowed Files

- 允许改动的目录或文件

## Forbidden Files

- 明确不要碰的目录或文件

## Functional Non-goals

- 本次不扩展的功能边界

## User-visible Acceptance

- User-visible Change:
  `yes / no`
- Expected Visible Behavior:
  - 用户第一眼应该看到什么变化
  - 用户必须能完成哪些页面内动作
- User Actions To Verify:
  - 需要实际操作的控件、流程或页面状态
- Required Evidence:
  `Browser / Chrome / Playwright 交互记录 / CLI 输出 / API 测试 / blocked reason`
- If No User-visible Change:
  如果本次只做 CLI 参数、生成命令、后端接口或文档，写清为什么用户不会直接看到页面变化，以及如何向用户解释。

## Generated Artifact Policy

- Surface Type:
  `static-generated-html / dev-server-page / production-page / CLI-output / backend-api / docs-only / not-generated`
- Acceptance URL:
  HTML / 前端 / 可视化任务必须填写本地或生产验收 URL；CLI / API / docs-only 写 `不适用` 和替代证据。
- Refresh / Regeneration:
  写清重新生成、刷新、重启 dev server 或清缓存方式。
- If No Visible Change:
  写清用户看不到变化时的排查路径，例如是否打开旧 `/tmp` 文件、是否未重跑生成命令、是否需要本地 HTTP server、是否打开了错误分支或旧页面。
- Required Interaction Evidence:
  HTML / 前端 / 可视化任务必须写 Browser / Chrome / Playwright 交互证据要求；如果 file:// 或权限策略阻断，改用本地 HTTP server 打开同一页面。

## Decision Mode

- Mode: `自主执行 / 关键确认 / 手动控制`
- Source:
  `repo-default / local-default / user-this-task / user-default`
- Internal Enum:
  `codex-led / checkpoint / manual`
- Reason:
  为什么本轮采用该模式

## Flow Lane

- Lane: `fast-lane / standard / discovery`
- Reason:
  为什么本轮采用该 lane
- Evidence Strategy:
  - `fast-lane`：使用 `fast-lane-requirement`、`fast-lane-review`、boundary 和 QA
  - `standard`：使用完整 requirement / review / freeze / eng review / domain spec readiness / QA
  - `discovery`：先 office-hours / plan review 澄清，冻结后再转入 `standard` 或 `fast-lane`

## Autonomy Plan

- Codex May Do Without Asking:
  - 例如：需求拆解、文档同步、本地测试、门禁恢复、本地开发服务重启
- Codex Must Ask Before:
  - 例如：业务口径多解、较大架构取舍、DB schema 变更、生产操作、git workflow action
- Gate Recovery:
  `Codex 先自行补齐可由本地证据证明的门禁缺口；无法自行证明时再提示用户`
- Goal Mode:
  `enabled / not-used / ask-first`
  如果启用，写清 goal objective；如果不启用，写清原因
- Local Restart:
  `allowed / not-required / ask-first`
  如果允许，写清命令，例如 `bash scripts/dev_stack.sh restart`

## Subagent Plan

- Mode: `not-used / explore / review / execute / governance / mixed`
- Reason:
  为什么这次使用或不使用 subagent
- Main Agent Owns:
  - 流程控制、active boundary、最终集成、最终答复
- Candidate Subagents:
  - name: `<agent-name>`
    role: `explorer / reviewer / worker`
    trigger stage: `requirement-brief / plan-ceo-review / plan-eng-review / domain-spec-readiness / implement / review / qa`
    write scope: `read-only` 或明确到 repo-relative 路径
    forbidden paths:
      - 不允许触碰的路径
    output evidence: `.gstack/reviews/<file>.md` 或 `.gstack/qa-reports/<file>.md`
    status: `planned / running / done / not-used`
- Result Integration:
  - subagent 结论如何回收到 boundary、review、QA 或 spec

## GStack Required Flow

- requirement-brief:
  status: `pending / done / not-required`
  evidence: `.gstack/requirements/<requirement-brief>.md`
- plan-ceo-review:
  status: `pending / done / not-required`
  evidence: `.gstack/reviews/<plan-ceo-review-result>.md`
- requirement-freeze:
  status: `pending / done / not-required`
  evidence: `.gstack/requirements/<requirement-freeze>.md`
  note: 也可以用 `prototype-freeze` 记录替代，evidence 指向 `.gstack/requirements/`、`archive/baseline/example-baseline/docs/` 或 `.gstack/designs/`
- plan-eng-review:
  status: `pending / done / not-required`
  evidence: `.gstack/reviews/<plan-eng-review-result>.md`
- domain-spec-readiness:
  status: `pending / done / not-required`
  evidence: `docs/specs/<module>/<spec-file>.md`
- implement:
  status: `pending / in-progress / done`
  evidence: `.gstack/task-boundaries/<this-boundary>.md`
- qa:
  status: `pending / done / not-required`
  command: `qa / qa-only`
  evidence: `.gstack/qa-reports/<qa-or-qa-only-result>.md`

## Required Gates

`Required Gates` 不替代上面的固定研发流。它只声明本任务在固定流中额外需要哪些专项门禁、由哪个专项 skill 或责任方执行、最晚在哪个阶段前补齐证据。

```yaml
required_gates:
  - gate_id: data-access
    trigger_reason: "本任务是否涉及数据源 / 接口 / 查数；不涉及时也要写清排除原因"
    owner: kk-data-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: "待补"
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "已明确事实源、source 状态、字段 / 口径风险、接口输入输出和当前 scope 可实现边界"
  - gate_id: data-query
    trigger_reason: "本任务是否涉及复杂查数或高风险指标；不涉及时写清排除原因"
    owner: kk-data-query
    required_before: plan-eng-review
    status: not-required
    evidence_path: "待补"
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "已完成 Query Brief、SQL、review 结论和敏感字段检查"
  - gate_id: prototype-logic-extraction
    trigger_reason: "本任务是否涉及前端 / 原型业务逻辑迁后端；不涉及时写清排除原因"
    owner: kk-task-kickoff
    required_before: plan-eng-review
    status: not-required
    evidence_path: "待补"
    evidence_section: "逻辑归属表"
    blocking_reason: ""
    done_criteria: "已列出前端 / 原型中的业务计算、状态派生、筛选聚合、口径映射，并明确 backend-owned / frontend-owned / shared-contract 归属、后端承接方式和 golden parity 真源"
  - gate_id: subagent-plan
    trigger_reason: "正式任务必须声明是否使用 subagent"
    owner: kk-subagent-orchestrator
    required_before: implement
    status: done
    evidence_path: ".gstack/task-boundaries/<this-boundary>.md"
    evidence_section: "Subagent Plan"
    blocking_reason: ""
    done_criteria: "active boundary 中已有 Subagent Plan；不使用 subagent 时写 Mode: not-used 和原因"
  - gate_id: doc-backfill
    trigger_reason: "本任务是否属于代码已有但文档缺失的 backfill 场景；不涉及时写清排除原因"
    owner: kk-doc-backfill
    required_before: review
    status: not-required
    evidence_path: "待补"
    evidence_section: ""
    blocking_reason: ""
    done_criteria: "已有从代码 / diff / 测试反推的文档证据，或明确说明无需 backfill"
  - gate_id: data-knowledge-sync
    trigger_reason: "本任务是否预计新增或调整后端 API / DTO / migration / 表 / 读模型 / 快照 / projection；不涉及时写清排除原因"
    owner: kk-doc-sync
    required_before: review
    status: not-required
    evidence_path: "待补"
    evidence_section: "Data Knowledge Sync"
    blocking_reason: ""
    done_criteria: "新增表已有 source doc + registry；新增接口已有 stack domain spec / interface doc；生命周期状态、证据等级和待确认项已标注"
  - gate_id: ui-design-quality
    trigger_reason: "本任务是否涉及页面、HTML、dashboard、可视化、交互控件或用户明确反馈 UI 不够好看；不涉及时写清排除原因"
    owner: kk-ui-design-kickoff
    required_before: implement
    status: not-required
    evidence_path: "待补"
    evidence_section: "UI Design Brief"
    blocking_reason: ""
    done_criteria: "已完成 UI 风格路由、信息密度、主流程、组件结构、视觉质量标准和 polish review 计划"
```

允许状态：`not-required / planned / done / blocked / deferred`。
允许 owner：`kk-task-kickoff / kk-data-kickoff / kk-data-query / kk-subagent-orchestrator / kk-doc-sync / kk-doc-backfill / kk-ui-design-kickoff / kk-ui-polish-review / template-review`。
允许 `required_before`：`requirement-brief / plan-ceo-review / requirement-freeze / plan-eng-review / domain-spec-readiness / implement / review / qa`。

`prototype-logic-extraction` 规则：

- owner 固定为 `kk-task-kickoff`
- required_before 固定为 `plan-eng-review`
- 如果 `not-required`，`trigger_reason` 必须写清排除原因
- 如果 `planned / done / blocked / deferred`，必须写清原型路径、前端路径、fixture 路径、逻辑归属表位置和 golden parity 真源
- 如果 `deferred`，`blocking_reason` 必须写清批准来源、延期原因、风险、删除条件或后续补齐路径

`data-knowledge-sync` 规则：

- owner 默认使用 `kk-doc-sync`
- required_before 默认使用 `review`
- 如果预计新增或调整后端 API、DTO、migration、表、读模型、快照、projection 或对外数据产品，状态至少为 `planned`
- 如果代码已经存在但文档缺失，可同时声明 `doc-backfill`，由 `kk-doc-backfill` 从代码 / diff / 测试反推当前实现
- 如果 `not-required`，`trigger_reason` 必须写清没有新增表 / 接口 / 读模型 / 快照 / projection 的原因
- done 时必须能指向 source doc、`source-registry.md`、stack domain spec、interface doc 或 review evidence

## Required Knowledge

- 必读文档

## Spec Sync Plan

- Spec Impact:
  `updated / not-required / pending`
- Expected Spec Targets:
  预期会改到哪些 `docs/specs/<module>/` 或其他 stack 真源文档
  如果涉及 stack 后端代码，默认写入 `docs/specs/<module>/`，不要写旧 `docs/specs/archive/backend-legacy/`
- Prototype Logic Evidence Sync:
  如果涉及 `prototype-logic-extraction`，写清 evidence 后续是否同步到模块 spec、接口设计、测试 fixture 或 QA 报告
- Allowed No-Spec-Change Reason:
  如果本次允许不改 spec，这里必须写清原因

## Verification

- 最少要跑哪些测试、脚本、页面验证
- 如果涉及 HTML / 前端 / 可视化：
  - 写明验收 URL。
  - 写明刷新 / 重新生成方式。
  - 写明 Browser / Chrome / Playwright 要操作哪些控件。
  - 如果本地 `file://` 或权限策略阻断，必须改用本地 HTTP server；仍无法验收时只能标 `blocked` 或 `partial`，不能标 `done`。
- 如果涉及 `app/backend/src/main/` 或 `backend/pom.xml`，这里必须列出后端测试改动和执行命令

## Lessons To Write Back

- 如果发现新坑，准备写到哪里

## 本地激活

- 正常情况下由 `$kk-task-kickoff` 自动完成
- 只有维护脚本、排障或手工修复时，才执行：
  `bash .gstack/scripts/use_boundary.sh <this-boundary-file>`
