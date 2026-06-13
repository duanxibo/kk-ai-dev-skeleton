# QA 报告：chinese-first-skeleton-docs

- 主题: chinese-first-skeleton-docs
- 负责人: Codex
- 日期: 2026-06-09
- 环境: local
- 范围: 公开骨架中文优先文档和示例文案
- 相关 requirement / review / boundary:
  - `.gstack/requirements/2026-06-09_chinese-first-skeleton-docs.md`
  - `.gstack/reviews/2026-06-09_chinese-first-skeleton-docs-review.md`
  - `.gstack/task-boundaries/2026-06-09_chinese-first-skeleton-docs.md`

## 目标

- 证明公开骨架主要入口文档已改为中文优先。
- 证明示例 Web App 用户可见文案已改为中文。
- 证明 `kk-*`、脚本名、YAML key 和固定机制名没有被破坏。

## 测试覆盖

- 入口文档中文化。
- knowledge 文档中文化。
- adapter 和 example 说明中文化。
- 示例 HTML / JS 用户可见文案中文化。
- doctor 默认人读输出和 help 文案中文化。
- 自然语言开发 smoke。
- doctor。
- spec sync guard。

## 测试方式

- 静态扫描。
- CLI smoke。
- 静态 HTML / JS 文案检查。

## 用户可见 UI / HTML / 可视化验收

- 是否属于用户可见 UI / HTML / 可视化任务:
  `是，示例 Web App 文案变化`
- Generated Artifact Policy:
  `docs-only / HTML`
- 验收 URL:
  `examples/simple-web-app/stack/frontend/index.html`
- 刷新 / 重新生成方式:
  `重新打开 HTML 文件，或用本地 HTTP server 预览。`
- Browser / Chrome / Playwright 是否实际打开:
  `已用 Chrome DevTools 打开 file:// 示例页面。`
- 结构存在:
  `通过`
- 控件可见:
  `静态检查通过`
- 控件可操作:
  `通过；搜索框使用 DevTools fill 验证，状态筛选通过触发原生 change 事件验证。`
- 状态变化正确:
  `通过；搜索“部署”后显示 1 个任务，切到 done 后显示 0 个任务和空态，清空搜索并切到 open 后显示 2 个任务。`
- 空态正确:
  `通过；空态文案为“没有任务匹配当前筛选条件。”`
- blocked / partial reason:
  `DevTools fill 未能直接操作原生 select；已通过聚焦/快照确认控件存在，并用页面 change 事件验证筛选逻辑。`

## Spec Sync Check

- Spec Impact:
  `not-required`
- Updated Spec Files:
  - `.gstack/knowledge/CODEMAP.md`
  - `.gstack/knowledge/ai-programming-framework.md`
  - `.gstack/knowledge/doc-placement.md`
  - `.gstack/knowledge/implementation-guide.md`
  - `.gstack/knowledge/natural-language-dev-regression-cases.md`
  - `.gstack/knowledge/qa-dimensions.md`
  - `examples/simple-web-app/stack/specs/requirements.md`
  - `examples/simple-web-app/stack/specs/frontend.md`
  - `examples/simple-web-app/stack/specs/testing.md`
- If Not Required, Why:
  本次不改变业务逻辑、接口、数据模型或持久化；只是公开骨架语言和示例文案调整。

## 发现

- 通过项:
  - `README.md`、`AGENTS.md`、`.gstack/README.md` 已中文优先。
  - `.gstack/knowledge/*.md` 已中文优先。
  - `adapters/default/adapter.md` 和 `adapters/default/gates.yaml` 已中文优先。
  - `examples/simple-web-app` 的说明、spec、HTML 和 JS 用户文案已中文优先。
  - `gstack_doctor.py check` 默认 markdown 输出已中文优先，JSON 输出保持机器可读字段。
  - `gstack_doctor.py --help` 已中文优先。
  - `kk-*` skill 命名、脚本名、YAML key 和机制字段仍保留英文。
  - 示例页面已通过 Chrome DevTools 打开并验证中文文案、搜索、状态筛选逻辑和空态。
- 非阻塞问题:
  - DevTools 的 select fill 未直接成功，已用页面事件验证逻辑；如后续公开发布示例站点，建议补一次完整 Playwright 端到端检查。

## 证据

- `rg` 扫描主要入口文档明显英文说明残留：
  - 仅剩固定机制名、路径、命令、skill 名和少量保留英文品牌名。
- `python3 .gstack/scripts/natural_language_dev_smoke.py --format user`
  - `非技术开发关键路径检查通过。`
- `python3 .gstack/scripts/gstack_doctor.py check`
  - `总体状态: warn`；仅预期 warning：不是 git worktree、`kk-*` skills 未同步、本示例无真实 dev stack 入口。
- `python3 .gstack/scripts/gstack_doctor.py --help`
  - help 文案为中文，命令名和参数名保留英文。
- `python3 -m py_compile .gstack/scripts/gstack_doctor.py`
  - 通过，无输出。
- `python3 .gstack/scripts/gstack_doctor.py check --format json | python3 -m json.tool`
  - 通过；`overall/status/check_id` 等机器可读字段保持稳定，message/details 为中文。
- `python3 .gstack/scripts/gstack_dashboard.py show --limit 5`
  - 当前任务 `chinese-first-skeleton-docs` 显示 `7/7`、全部完成、正常。
- `rg` 扫描保留英文说明模式和私有残留：
  - 明显英文说明残留：无输出。
  - `tg-`、`源项目`、私有业务路径、本地敏感配置残留：无输出。
- `python3 .gstack/scripts/spec_sync_guard.py`
  - `PASS: static skeleton guard passed.`
- Chrome DevTools 打开 `file://<repo-root>/examples/simple-web-app/stack/frontend/index.html`
  - 页面标题：`简单任务看板`
  - H1：`任务看板`
  - 搜索 `部署` 后：`当前显示 1 个任务`
  - 切到 `done` 后：`当前显示 0 个任务`，空态显示 `没有任务匹配当前筛选条件。`
  - 清空搜索并切到 `open` 后：`当前显示 2 个任务`

## 残余风险

- 如果后续面向英文开源用户发布，需要补英文 README 或双语版本。
- 如果后续要求示例页面也达到完整交互 QA，应启动本地预览并补浏览器证据。
