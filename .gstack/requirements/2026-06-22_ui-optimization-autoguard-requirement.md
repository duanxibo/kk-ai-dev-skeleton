# UI optimization autoguard fast-lane requirement

- 需求名称：增强 UI 优化短句自动保障
- 提出人：用户
- 日期：2026-06-22
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-22_ui-optimization-autoguard.md`
- AI 语义复核：`yes`

## 需求一句话

- 用户只说“进行 UI 优化”时，骨架也应自动识别为 UI 任务，并保障先做 UI 设计梳理、再实现、最后做视觉复核和浏览器 QA，而不要求用户手动描述内部流程。

## 为什么可以走 fast-lane

- 范围小：是，主要增强自然语言路由、只读 helper、smoke、runtime bundle 和相关 skill 文档。
- 需求明确：是，短句 UI 优化必须自动触发 UI 质量链路。
- 不涉及业务口径多解：是。
- 不涉及 DB schema、真实数据、生产、外部服务或 git workflow action：是。
- 可本地验证：是，可运行自然语言 smoke、adapter validate、runtime verify、doctor 和单元测试。

## 本次必须做

- 新增或增强确定性自然语言路由，使“进行 UI 优化 / 优化界面 / 美化页面”等短句进入 UI 优化开工路径。
- 用户侧输出必须说明 Codex 会自动负责 UI 设计梳理、实现、视觉复核和浏览器验收。
- 内部路由必须指向 `kk-task-kickoff`、`kk-ui-design-kickoff`、`kk-ui-polish-review` 和 Browser QA 的链路。
- runtime bundle、manifest 和 smoke 必须覆盖新增 helper。
- 同步到 `kk-ai-factory` 已安装的 portable runtime。

## 本次明确不做

- 不实现任何具体项目 UI。
- 不接真实数据、生产、数据库、GitHub 或远程 runner。
- 不执行 commit、push、PR 或其它 git workflow action，除非用户另行明确授权。

## 冻结结论

- 本文件同时作为 fast-lane requirement brief 和 requirement freeze。
