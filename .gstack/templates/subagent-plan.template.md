# Subagent Plan 模板

## Subagent Plan

- Mode: `not-used / explore / review / execute / governance / mixed`
- Reason:
  简短说明为什么使用或不使用 subagent。
- Main Agent Owns:
  - 流程控制
  - active boundary
  - 任务拆分与写范围分配
  - 最终集成、验证和用户答复
- Candidate Subagents:
  - name: `<agent-name>`
    role: `explorer / reviewer / worker`
    trigger stage: `requirement-brief / plan-ceo-review / plan-eng-review / domain-spec-readiness / implement / review / qa`
    task:
      这个 subagent 只负责什么。
    write scope:
      `read-only` 或明确 repo-relative 路径；worker 必须是互不重叠的写范围。
    forbidden paths:
      - 不允许触碰的路径
    required inputs:
      - 需要读取的文档、spec、boundary 或 diff
    output evidence:
      `.gstack/reviews/<file>.md`、`.gstack/qa-reports/<file>.md` 或本轮最终集成说明。
    status: `planned / running / done / not-used`
- Result Integration:
  - subagent 结论必须由 main agent 整合到 boundary、review、QA、decision、learning 或相关 spec；不能只留在聊天里。

## 判断规则

- `not-used`：
  小任务、单文件修改、没有独立验证面，或 subagent 会增加同步成本。
- `explore`：
  多个模块需要并行读代码、读 specs、找历史 evidence，但暂不改文件。
- `review`：
  需要独立视角做 CEO / ENG / code review / QA 风险检查。
- `execute`：
  可以拆出互不覆盖的写范围，例如后端测试、文档补齐、前端接入分别由不同 worker 执行。
- `governance`：
  需要从 diff 反查文档缺口、补 learning / pitfall / decision 草案。
- `mixed`：
  同时存在探索、评审、执行或治理。
