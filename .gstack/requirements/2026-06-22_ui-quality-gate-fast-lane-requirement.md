# UI quality check fast-lane requirement

- 需求名称：抽离可复用 UI 风格判断和视觉质量检查
- 提出人：用户
- 日期：2026-06-22
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-22_ui-quality-gate.md`
- AI 语义复核：`yes`

## 需求一句话

- 用户要完成什么：把已在私有 dogfood 项目验证过的 UI 审美能力抽离为公开骨架的 `kk-*` 能力，并使目标项目可通过 portable core 获得该能力。

## 为什么可以走 fast-lane

- 范围小：是，主要是 `.gstack` knowledge、templates、skills、安装器清单和测试。
- 需求明确：是，目标是 UI design kickoff + UI polish review。
- 不涉及业务口径多解：是。
- 不涉及 DB schema、生产操作或 git workflow action：是。
- 可本地验证：是，可运行安装器、doctor、runtime verify 和单元测试。

## 本次必须做

- 新增 `.gstack/knowledge/ui-patterns.md` 与 `.gstack/knowledge/visual-quality-bar.md`。
- 新增 `ui-design-brief` 和 `ui-polish-review` 模板。
- 新增 `kk-ui-design-kickoff` 与 `kk-ui-polish-review` skills。
- 更新 `kk-task-kickoff`、skills README、sync 脚本、doctor portable docs 和 installer portable core。
- 让在线平台目标项目可同步这套 UI 能力。

## 用户可见变化拆解

- 生成命令 / CLI 参数：涉及；目标项目升级后可运行 `kk-ui-design-kickoff` / `kk-ui-polish-review`。
- 后端接口：不涉及。
- 页面内交互控件：不涉及。
- 用户可见 UI 变化：不涉及本轮；影响后续 UI 任务质量。
- 静态输出 / 生成文件：涉及；新增 repo-native docs、templates 和 skills。
- 用户期望的可见变化：后续前端任务不直接写粗糙 UI，而是先做风格路由和设计 brief。

## 本次明确不做

- 不直接重做任何项目页面。
- 不连接 Figma 或外部设计服务。
- 不发布插件，不提交 / 推送。

## 影响面

- 代码 / 文档路径：`.gstack/knowledge/`、`.gstack/templates/`、`.gstack/skills/`、`.gstack/scripts/`、`scripts/init_project.py`、`adapters/default/core_manifest.json`、tests。
- 数据 / 接口 / 权限：不涉及。
- spec impact：updated。

## 冻结结论

- 本文件同时作为 fast-lane requirement brief 和 requirement freeze。
- 如果需要改真实 UI 页面或设计品牌系统，另起任务。
