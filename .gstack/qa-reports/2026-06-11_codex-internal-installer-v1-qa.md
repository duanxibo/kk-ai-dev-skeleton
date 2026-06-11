# codex-internal-installer-v1 QA

- 日期：2026-06-11
- 类型：script + docs QA
- 结论：pass
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md`
- 关联产物：
  - `scripts/init_project.py`
  - `scripts/dev_stack.sh`
  - `tests/test_init_project.py`
  - `CODEX_ADOPTION_CONNECTOR.md`
  - `COMPANY_ADOPTION_GUIDE.md`
  - `README.md`
  - `.gstack/knowledge/code-patterns.md`

## 验收范围

本次验证 V1 内部安装器能力是否可由 Codex 调用，并确认业务用户入口仍是自然语言接入。

本次不涉及 HTML、页面、dashboard、截图或交互 UI，因此 Browser QA 不需要。

## 验证结果

### Python compile

命令：

```bash
python3 -m py_compile scripts/init_project.py tests/test_init_project.py
```

结果：

- PASS。

### Unit tests

命令：

```bash
python3 -m unittest tests/test_init_project.py
```

结果：

- PASS。
- 7 tests passed。

覆盖点：

- adapter slug 规范化。
- `apply` 从 default adapter 创建新 adapter。
- `apply` 默认不覆盖已有 adapter。
- `detect` 能识别 adapter 和缺失 core。
- `plan` 保留现有 adapter 并强调自然语言入口。
- `verify` 命令能带上 active boundary。
- `report` 包含低风险试点任务建议。

### CLI smoke

命令：

```bash
python3 scripts/init_project.py --adapter default --detect
```

结果：

- PASS。
- 输出显示 default adapter、runtime、active boundary 和 framework core 均可检测。

命令：

```bash
python3 scripts/init_project.py --adapter default --plan
```

结果：

- PASS。
- 输出显示用户入口是对 Codex 说自然语言接入请求，执行方式是 Codex 调用内部 helper。

命令：

```bash
python3 scripts/init_project.py --adapter default --report
```

结果：

- PASS。
- 输出接入状态、接入计划和第一个低风险试点任务建议。

命令：

```bash
python3 scripts/init_project.py --adapter default --format json --plan
```

结果：

- PASS。
- 输出机器可读 JSON，包含 state 和 plan。

命令：

```bash
python3 scripts/init_project.py --adapter default --apply --report
```

结果：

- PASS。
- default adapter 已存在，`apply` 默认不覆盖，并输出需要 `--force` 才能替换。

命令：

```bash
python3 scripts/init_project.py --adapter default --verify --report
```

结果：

- PASS。
- 验证链路中 doctor、spec-sync、team-flow、required-gates、natural-language-smoke 全部通过。

兼容性检查：

- 用临时 adapter 名运行旧参数 `--create-adapter` 能创建 adapter 并输出下一步；临时 adapter 已删除。

### Guard

命令：

```bash
python3 .gstack/scripts/spec_sync_guard.py
```

结果：

- PASS：static skeleton guard passed。
- 备注：当前目录不是 git worktree，脚本按 static skeleton guard 运行，这是当前骨架目录的预期环境状态。

命令：

```bash
python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD
```

结果：

- PASS：static required gstack command chain is satisfied。

命令：

```bash
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_codex-internal-installer-v1.md
```

结果：

- PASS：static Required Gates audit passed。

### 文案检查

命令：

```bash
rg --hidden -n "用户.*执行.*python3|业务用户.*运行.*python3|在目标项目根目录内执行|复制到新项目后的最小步骤" CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md -S
```

结果：

- 无命中。
- `rg` 返回码为 1，符合“没有旧命令行优先文案”的预期。

命令：

```bash
rg --hidden -n "detect|plan|apply|verify|report|内部安装器|Codex 接入器" scripts/init_project.py CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md scripts/dev_stack.sh .gstack/knowledge/code-patterns.md -S
```

结果：

- 有预期命中。
- 命中覆盖脚本、产品化文档、接入指南、README、dev stack help 和 code pattern。

命令：

```bash
rg --hidden -n "lunhui|cohort|审批模块|review-service|TianGong|tiangong" scripts/init_project.py tests/test_init_project.py CODEX_ADOPTION_CONNECTOR.md COMPANY_ADOPTION_GUIDE.md README.md -S
```

结果：

- 无命中。
- `rg` 返回码为 1，符合“未引入具体业务项目名或旧项目上下文”的预期。

## 用户可见验收

- 业务用户入口仍是自然语言接入。
- Codex 背后已有 V1 内部安装器能力：detect、plan、apply、verify、report。
- `apply` 默认不覆盖已有 adapter。
- `verify` 可串联现有 guard 和 smoke。
- 文档已说明 V1 helper 是 Codex 的执行层，不是业务用户需要学习的入口。

## 残余风险

- 当前仍不是正式 Codex plugin；V2 需要另起任务设计分发形态。
- 当前目录不是 git worktree，因此 gstack guard 以 static audit 模式运行；复制到真实 git 项目后应再次运行。
