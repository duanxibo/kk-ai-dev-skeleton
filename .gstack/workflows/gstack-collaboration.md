# KK Dev Skeleton x gstack 协作工作流

这里把 KK Dev Skeleton 的协作方式固定为 stack-only full-stack ownership：每个人都可以从需求到上线完整闭环，但所有闭环都必须落在同一套 `stack` 工程真源和 `.gstack` 保护栏里。

## Codex 协作模式

用户决策介入程度由 `kk-codex-mode` 统一管理，完整规则见 [codex-autopilot.md](codex-autopilot.md)。

三档中文模式：

- `自主执行`：默认模式。Codex 自动拆解、开发、测试、补文档、修门禁和重启本地项目；只有高风险点问用户。
- `关键确认`：Codex 自动准备和推进，但在产品口径、架构取舍、数据模型、接口契约、大范围改动前暂停确认。
- `手动控制`：Codex 只分析和建议；没有用户明确授权，不改代码、不落长期文档。

模式不替代固定功能开发流。小需求在 `自主执行` 下可以走 `fast-lane`，由 Codex 自动生成轻量 requirement / review / boundary / QA evidence 并推进；大需求或多解需求走 `discovery`，先进入 office-hours / plan review 磨合。

非技术用户入口：

- 用户可以只描述业务目标、给谁用、成功样子、数据来源和风险担心。
- Codex 使用 `.gstack/templates/nontechnical-task-intake.template.md` 转译为正式 requirement / boundary / QA 输入。
- 用户不需要理解 `boundary`、`domain-spec-readiness`、`Required Gates` 或测试命令。
- 本地状态异常先运行 `python3 .gstack/scripts/gstack_doctor.py check`，可修复的 active boundary 指针用 `python3 .gstack/scripts/gstack_doctor.py fix --active-boundary`。

Dashboard 规则：

- dashboard 只能是 generated view，从 repo-native evidence 实时生成。
- 不提交 `.gstack/dashboard.*`、`.gstack/status.json` 或任何多人共享聚合状态文件。
- 本地查看任务状态使用 `python3 .gstack/scripts/gstack_dashboard.py show`；JSON 输出使用 `python3 .gstack/scripts/gstack_dashboard.py show --format json`。

Flow Lane：

- `fast-lane`：小需求、明确 bugfix、局部改动、无业务口径多解、可本地验证。
- `standard`：普通正式开发，需求明确但影响面不小或涉及多模块协作。
- `discovery`：大需求、产品方向不清或存在多个合理方案，先澄清再冻结。

## 固定功能开发流

`/office-hours` 可以作为前置探索，但不替代下面任何强制阶段。

正式进入开发的团队任务必须按顺序完成：

1. `requirement-brief`
   输出：
   要解决的问题、目标用户、业务目标、成功标准、不做什么、数据/接口/权限影响、待确认问题
2. `/plan-ceo-review`
   输出：
   是否范围过大、先做什么、明确不做什么
3. `requirement-freeze` 或 `prototype-freeze`
   输出：
   CEO review 后的冻结需求、采纳/延后项和工程准备条件
4. `/plan-eng-review`
   输出：
   数据、接口、状态、测试、风险拆解
5. 建或更新 task boundary
   输出：
   `Decision Mode`、`Flow Lane`、`Autonomy Plan`、`GStack Required Flow`、`Required Gates`、`Subagent Plan` 与 `Spec Sync Plan`。boundary 可以在 `plan-eng-review` 前以 `planned` gate 状态建立，但 `prototype-logic-extraction` 这类 `required_before: plan-eng-review` 的 evidence 必须在进入工程评审前补齐为 `done / blocked / deferred`
6. `domain-spec-readiness`
   输出：
   更新或确认 `docs/specs/<module>/` 中的需求、数据、接口、前端、后端或测试口径。新任务不再新增 handoff 文档。
7. 如果任务适合拆分，用 `kk-subagent-orchestrator` 规划探索、评审、执行或治理 agent
8. 实现代码
9. 必要时先跑 `python3 .gstack/scripts/gstack_doctor.py check`
10. 跑 `python3 .gstack/scripts/spec_sync_guard.py`
11. `/qa-only` 或 `/qa`
12. 把新经验写回 `.gstack/knowledge/` 或 `.gstack/rules/`

严格规则：

- 门禁不区分单人模式或多人模式，只检查阶段 evidence；同一个人可以完成全部阶段。
- fast-lane 不跳过 evidence；它只允许用轻量 requirement 和轻量 review 同时满足需求描述、需求冻结、CEO review 和工程 review 的最小记录。
- `Required Gates` 不替代固定功能开发流；它只在 task boundary 阶段声明 data-access、data-query、prototype-logic-extraction、subagent-plan、doc-backfill 等专项门禁和证据。
- `kk-task-kickoff` 是 active boundary 与 `prototype-logic-extraction` gate owner；`prototype-logic-extraction` 固定 `required_before: plan-eng-review`。`kk-data-kickoff` 只拥有 `data-access` gate，并在数据任务中协助发现逻辑抽取需求。
- 门禁要求 active boundary 有 `Subagent Plan`；不使用 subagent 也要写 `Mode: not-used` 和原因。
- `data-access` 与 `prototype-logic-extraction` 可以同时存在但互不替代；页面 mock 替换真实接口通常两个 gate 都需要。
- `prototype-logic-extraction` 写 `deferred` 时必须写清批准来源、延期原因、风险、删除条件或后续补齐路径。
- 开发前，boundary 里的 `requirement-brief`、`plan-ceo-review`、`requirement-freeze/prototype-freeze`、`plan-eng-review`、`domain-spec-readiness` 必须是 `done`，且 evidence 指向 repo-native 文档。
- `requirement-brief` 是 `plan-ceo-review` 的输入；没有 brief，不能把 CEO review 标记为完成。
- `requirement-freeze/prototype-freeze` 是 `plan-eng-review` 和 domain spec readiness 的输入；没有冻结证据，不能进入正式实现。
- `domain-spec-readiness` 是正式实现前的统一产品 + 工程真源检查，默认指向 `docs/specs/<module>/` 或对应 stack 服务文档。
- `handoff` 已从新任务固定流中移除；不要再新增 `.gstack/designs/*handoff*.md` 作为门禁证据。历史 handoff 文件已归档到 `.gstack/designs/archive/`，只作为旧参考保留。
- push 前，boundary 里的 `implement` 和 `qa` 也必须是 `done`。
- `qa` 可以由 `/qa` 或 `/qa-only` 满足，但必须有 `.gstack/qa-reports/` 证据。
- 如果复用 `archive/baseline/`、原型或历史设计材料，直接在 domain spec、requirement、review 或 boundary 中引用来源并说明采纳 / 放弃项。
- `app/backend/src/main/` 或 `backend/pom.xml` 改动必须同时有后端测试改动和 `docs/specs/<module>/` 规范沉淀。
- 新后端规范不得继续写到或重建旧 `docs/specs/archive/backend-legacy/`；旧内容已归档，只作为历史追溯。
- 本规则由 `.gstack/workflows/team-development-flow.toml` 和 `.gstack/scripts/team_flow_guard.py` 执行。
- `Required Gates` 由 `.gstack/scripts/required_gates_audit.py` 独立审计；迁移初期只 warning，不把历史 boundary 一次性设为失败。

## Bug 修复流

Bug 修复可以先 `/investigate` 定根因，但只要进入正式代码修改，仍然必须进入同一条固定开发链。

1. `/investigate`
2. `requirement-brief`
3. `/plan-ceo-review`
4. `requirement-freeze` 或 `prototype-freeze`
5. `/plan-eng-review`
6. `domain-spec-readiness`
7. 建最小 task boundary，并写清 `GStack Required Flow`、`Required Gates` 与 `Subagent Plan`
8. 修复
9. 定向 `/qa-only` 或 `/qa`
10. 跑 `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`
11. 跑 `python3 .gstack/scripts/spec_sync_guard.py`
12. 回写新坑和新规则

## 经验回收流

场景：

- 功能完成后
- 一周一次
- 感觉 AI 写的代码被大量回改时

建议动作：

1. 看 `git diff` / `git log`
2. 分类偏差：
   命名、结构、边界、场景遗漏、测试遗漏、架构职责
3. 判断写回层：
   - `code-patterns.md`
   - `pitfalls/*.md`
   - `spec-rules.md`
   - `plan-rules.md`
   - `task-rules.md`

## 与 repo 真源的关系

- `.gstack/` 负责协作系统
- `docs/specs/` 负责产品、技术、测试统一真源
- `frontend/backend/scripts/tests/fixtures` 负责可执行真源
- `gstack_dashboard.py` 负责生成只读任务状态视图，不产生 repo 真源
- `team_flow_guard.py` 负责检查团队是否按固定 gstack 命令链推进
- `kk-subagent-orchestrator` 负责判断是否使用 subagent，并把计划写回 boundary
- `spec_sync_guard.py` 负责在任务收口时检查“实现改动”和“真源回写”是否对齐

不要把 `.gstack/` 当成第二套独立规格库。
