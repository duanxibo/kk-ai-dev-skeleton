# Runtime Bundle Plugin Sync Fast-lane Requirement

- 需求名称：同步上游 dogfood 增强后的公共骨架与 Codex 插件
- 提出人：用户
- 日期：2026-06-18
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-18_runtime-bundle-plugin-sync.md`
- AI 语义复核：
  `yes`

## 需求一句话

- 用户要完成什么：
  将上游 dogfood 项目中已经增强的 AI 开发骨架能力同步回 KK Dev Skeleton 抽离仓库，并同步更新 Codex Adoption 插件，使插件引导用户使用最新的 adapter installer、runtime bundle 安装和验证能力。

## 为什么可以走 fast-lane

- 范围小：
  `是`
- 需求明确：
  `是`
- 不涉及业务口径多解：
  `是`
- 不涉及 DB schema、生产操作或 git workflow action：
  `是`
- 可本地验证：
  `是`

## 本次必须做

- 将 adapter installer 从旧版接入 helper 同步到支持 portable core、explicit runtime script bundle、`--apply-runtime`、`--verify-runtime`、pilot runtime verification 和 adapter schema guard 的新版能力。
- 在公共骨架中补齐 runtime bundle 所需的 Loop runner 与 contract smoke 脚本，并把默认 skill 前缀、示例文案和目标路径保持为 `kk-*` / 通用项目表达。
- 更新 `adapters/default/adapter.md`、`runtime.json`、`core_manifest.json`、`runtime_schema.json` 和相关说明文档，使默认 adapter 说明 runtime bundle 的显式安装和验证策略。
- 更新仓库发布源 `plugins/kk-dev-skeleton-adoption/` 的 skill / README / manifest / checker，使 Codex 插件能识别并引导新版 helper。
- 同步个人本地插件源 `~/plugins/kk-dev-skeleton-adoption`，刷新 cachebuster，并验证插件 manifest。
- 落 QA evidence，证明脚本编译、adapter validation、runtime dry-run / verify、pilot、contract smoke、自然语言 smoke、插件校验和 diff 检查通过。

## 用户可见变化拆解

- 生成命令 / CLI 参数：
  `涉及；插件会引导 Codex 使用 --apply-runtime、--verify-runtime、--validate-adapter、--pilot 等新版 helper 能力。`
- 后端接口：
  `不涉及`
- 页面内交互控件：
  `不涉及`
- 用户可见 UI 变化：
  `不涉及`
- 静态输出 / 生成文件：
  `涉及；插件说明、adapter metadata 和 helper 报告会展示 runtime bundle 安装、验证和升级建议。`
- 用户期望的可见变化：
  已安装或发布的 Codex 插件不再停留在旧版 V1 adoption flow，而是能提示和驱动公共骨架的 runtime bundle 安装 / 验证路线。
- 如果用户说“筛选 / 排序 / 搜索 / 操作入口 / 看不到页面变化”：
  本轮不是页面或业务功能改动；验收以插件 skill 文档、installer CLI 输出、adapter metadata、runtime smoke 和插件 manifest 校验为准。

## 本次明确不做

- 不复制上游 dogfood 业务 `stack/`、`archive/`、`blueprint/`、真实数据配置、数据访问工具、凭证或本机路径到公共骨架。
- 不把 `tg-*` 项目专属 skill 前缀写入公共框架核心；公共骨架继续使用 `kk-*`。
- 不执行 commit、push、pull、PR、发布、生产、DB、真实数据或破坏性操作。
- 不创建新的 marketplace 条目；只更新已有仓库插件源和个人本地插件源。

## 影响面

- 代码 / 文档路径：
  `scripts/init_project.py`、`adapters/default/*`、`.gstack/scripts/gstack_loop.py`、`.gstack/scripts/gstack_loop_contract_smoke.py`、`.gstack/scripts/README.md`、`.gstack/knowledge/ai-programming-framework.md`、`plugins/kk-dev-skeleton-adoption/**`、`~/plugins/kk-dev-skeleton-adoption/**`、本轮 `.gstack` evidence。
- 数据 / 接口 / 权限：
  `不涉及`
- spec impact：
  `updated`

## 冻结结论

- 本文件同时作为 fast-lane 的 requirement brief 和 requirement freeze。
- 只有 `AI 语义复核: yes` 时，本文件才能满足 fast-lane freeze gate；draft 或 no 必须先补 Codex 语义复核。
- 如果后续发现需要真实数据、生产、DB、插件发布、marketplace 变更或 git workflow，必须退出 fast-lane 并另行确认。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `.gstack/reviews/`。
