# QA Report：skeleton-blueprint-adapter-hardening

- 主题: skeleton-blueprint-adapter-hardening
- 负责人: Codex
- 日期: 2026-06-11
- 环境: local skeleton workspace
- 范围:
  - 协作蓝图补齐
  - 角色入口补齐
  - data-access 通用知识入口补齐
  - 明显项目残留泛化
  - doctor / guard / smoke 验证
- 相关 requirement / review / boundary:
  - `.gstack/requirements/2026-06-11_skeleton-blueprint-adapter-hardening.md`
  - `.gstack/reviews/2026-06-11_skeleton-blueprint-adapter-hardening-review.md`
  - `.gstack/task-boundaries/2026-06-11_skeleton-blueprint-adapter-hardening.md`

## 目标

- 证明公开骨架不再缺失协作蓝图、角色入口和 data-access 入口。
- 证明 `kk-task-kickoff`、`kk-data-kickoff`、`kk-data-query` 依赖的核心文档存在。
- 证明自然语言开发关键路径未被本次泛化破坏。
- 证明公开核心路径不再残留明显旧项目业务名。

## 测试覆盖

- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
- `.gstack/entrypoints/`
- `.gstack/knowledge/data-access/`
- `.gstack/knowledge/code-patterns.md`
- `.gstack/knowledge/state-management.md`
- `.gstack/knowledge/ui-patterns.md`
- `.gstack/knowledge/pitfalls/README.md`
- `.gstack/scripts/gstack_doctor.py`
- `.gstack/scripts/nontechnical_task_starter.py`
- `.gstack/scripts/nontechnical_delivery_summary.py`
- `.gstack/scripts/nontechnical_ci_failure.py`
- `.gstack/workflows/`
- `.gstack/templates/`
- `adapters/default/`

## 测试方式

- 脚本
- 静态扫描
- 自然语言 smoke
- Python compile

## 用户可见 UI / HTML / 可视化验收

- 是否属于用户可见 UI / HTML / 可视化任务:
  `否`
- Generated Artifact Policy:
  `docs-only`
- 验收 URL:
  `不适用`
- 刷新 / 重新生成方式:
  重新打开或搜索仓库文档。
- Browser / Chrome / Playwright 是否实际打开:
  `不适用`
- 若 file:// 或权限策略阻断，是否改用本地 HTTP server:
  `不适用`
- 结构存在:
  `不适用`
- 控件可见:
  `不适用`
- 控件可操作:
  `不适用`
- 状态变化正确:
  `不适用`
- 空态正确:
  `不适用`
- 刷新 / 重新生成说明清晰:
  `不适用`
- 是否只用了 `rg`、JSON、HTML 字符串或截图外观替代交互验收:
  `否；本次不是 UI 任务`
- 如果用户指出验收遗漏:
  `不适用`
- blocked / partial reason:
  `不适用`

## 数据接口验证

- 输入输出是否清晰:
  `不适用`
- 数据逻辑和字段口径是否对齐:
  `不适用`
- scope 是否明确:
  `不适用`
- 是否误用 analytics warehouse 或临时 SQL:
  `否`
- 是否绕过后端 API:
  `否`
- relational database 落表、改表或读模型新增是否经过人工确认:
  `不适用`
- 是否验证前端未直连数据库:
  `不适用`
- 是否验证未暴露任意 SQL 或内部表结构:
  `通过`

## Prototype Logic Parity

- 是否需要 `prototype-logic-extraction`:
  `否，原因：本次不迁移原型业务逻辑到后端`
- 逻辑抽取 evidence path:
  `不适用`
- expected output 真源是否已验证:
  `不适用`
- 是否使用原型 fixture 或人工确认样例验证后端输出:
  `不适用`
- 前端是否只保留薄渲染职责:
  `不适用`

## Spec Sync Check

- Spec Impact:
  `updated`
- Updated Spec Files:
  - `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`
  - `.gstack/entrypoints/README.md`
  - `.gstack/entrypoints/product-manager.md`
  - `.gstack/entrypoints/engineer.md`
  - `.gstack/knowledge/data-access/README.md`
  - `.gstack/knowledge/data-access/source-registry.md`
  - `.gstack/knowledge/data-access/mysql-source-guide.md`
  - `.gstack/knowledge/data-access/clickhouse-discovery-guide.md`
  - `.gstack/knowledge/data-access/query-access-guide.md`
  - `.gstack/knowledge/data-access/interface-design-guide.md`
  - `.gstack/knowledge/code-patterns.md`
  - `.gstack/knowledge/state-management.md`
  - `.gstack/knowledge/ui-patterns.md`
  - `.gstack/knowledge/pitfalls/README.md`
  - `.gstack/knowledge/ai-programming-framework.md`
  - `adapters/default/adapter.md`
  - `adapters/default/forbidden-scopes.json`
- If Not Required, Why:
  不适用。

## 发现

- 阻塞问题:
  - 无。
- 非阻塞问题:
  - `gstack_doctor.py check` 仍为 `warn`，原因是当前目录不是 git worktree、父路径包含旧项目命名片段、用户本机仍有外部 `tg-*` skill symlink、默认开发启动入口 `scripts/dev_stack.sh` 不存在。
  - 这些 warning 不阻塞本次骨架硬化；它们是环境 / 后续产品化问题。
- 通过项:
  - 核心文档断链检查通过。
  - static skeleton guard 通过。
  - 自然语言开发 smoke 通过。
  - Python compile 通过。
  - 核心路径旧业务名扫描无命中。

## 证据

```bash
python3 .gstack/scripts/gstack_doctor.py check
```

结果：`warn`

- `active-boundary`: 通过
- `codex-mode`: 通过
- `git-hooks`: 提醒，当前目录还不是 git worktree
- `skills`: 通过
- `context-isolation`: 提醒，父目录和外部 `tg-*` symlink 有串味风险
- `scripts`: 通过
- `core-docs`: 通过，已检查 17 个入口文档
- `dev-stack-entry`: 提醒，缺少 `scripts/dev_stack.sh`

```bash
python3 .gstack/scripts/spec_sync_guard.py
```

结果：`PASS: static skeleton guard passed.`

```bash
python3 .gstack/scripts/natural_language_dev_smoke.py
```

结果：`Overall: ok`

```bash
python3 -m py_compile .gstack/scripts/gstack_doctor.py .gstack/scripts/nontechnical_task_starter.py .gstack/scripts/nontechnical_delivery_summary.py .gstack/scripts/nontechnical_ci_failure.py
```

结果：通过，无输出。

```bash
rg --hidden -n "stack/app-stack|review-service|审批模块|product-review|lunhui|cohort|camp-budget|budgetdata" .gstack/scripts .gstack/skills .gstack/templates .gstack/workflows adapters README.md AGENTS.md -S
```

结果：无命中。

核心断链存在性检查：

- `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`: OK
- `.gstack/entrypoints/product-manager.md`: OK
- `.gstack/entrypoints/engineer.md`: OK
- `.gstack/knowledge/data-access/README.md`: OK
- `.gstack/knowledge/data-access/source-registry.md`: OK
- `.gstack/knowledge/data-access/mysql-source-guide.md`: OK
- `.gstack/knowledge/data-access/clickhouse-discovery-guide.md`: OK
- `.gstack/knowledge/data-access/query-access-guide.md`: OK
- `.gstack/knowledge/data-access/interface-design-guide.md`: OK

## 残余风险

- 这还不是完整公司级安装器；没有实现 `init / update / doctor` 的外部分发 CLI。
- guard 仍主要使用默认路径配置，尚未完整实现多 adapter runtime。
- 当前目录不是 git worktree，无法验证 git hooks 的真实安装状态。
- 默认开发启动入口 `scripts/dev_stack.sh` 仍未提供；应由真实项目 adapter 或后续模板任务补齐。
- 用户本机仍存在外部 `tg-*` skill symlink；本次不清理用户环境。

## 建议结论

- 当前任务可收口。
- 下一步若要给公司试用，建议单独做 `adapter runtime + template repo cleanup` 任务。

## 可回写候选

- 已回写到 `.gstack/knowledge/ai-programming-framework.md`：
  抽离时必须区分业务真源、私有历史证据、可复用协作规则和仍被引用的文件。
