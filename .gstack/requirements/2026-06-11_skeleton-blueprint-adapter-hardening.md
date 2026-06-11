# Fast-lane Requirement：skeleton-blueprint-adapter-hardening

- 需求名称：skeleton-blueprint-adapter-hardening
- 提出人：用户
- 日期：2026-06-11
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-11_skeleton-blueprint-adapter-hardening.md`
- AI 语义复核：
  `yes`

## 需求一句话

- 用户要完成什么：
  继续完善从 TianGong 抽离出的公开 AI 开发骨架，补回不该丢失的协作蓝图和入口知识，修复已发现的文档断链，并减少框架核心里的项目专属残留。

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

- 新增通用版 `.gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md`。
- 新增通用角色入口 `.gstack/entrypoints/`。
- 新增通用 data-access 知识库骨架，满足 `kk-data-*` skills 的 Required Reading。
- 修正明显断链引用。
- 清理或降级最明显的项目专属残留，避免公开骨架默认带 `restricted-module / 受限业务模块` 语义。
- 运行 doctor、spec guard 和自然语言 smoke。
- 写 QA evidence。

## 用户可见变化拆解

- 生成命令 / CLI 参数：
  `不涉及`
- 后端接口：
  `不涉及`
- 页面内交互控件：
  `不涉及`
- 用户可见 UI 变化：
  `不涉及`
- 静态输出 / 生成文件：
  `涉及，新增和修正文档；用户通过打开 README、AGENTS、.gstack 文档和运行本地检查验证。`
- 用户期望的可见变化：
  用户打开骨架时能看到完整协作蓝图、角色入口和 data-access 入口，不再遇到 skill 要求读取但文件不存在的问题。

## 本次明确不做

- 不发布 npm / pip / brew / CLI 安装器。
- 不创建或切换 git 分支，不 commit，不 push。
- 不把 TianGong 的业务数据、历史设计或真实数据资产复制到公开骨架。
- 不重构所有 guard 为完整 adapter runtime；本轮只修明显断链和高风险残留。
- 不改变 `kk-*` skill 命名空间。

## 影响面

- 代码 / 文档路径：
  `.gstack/`、`adapters/default/`、`README.md`、`AGENTS.md`
- 数据 / 接口 / 权限：
  `不涉及`
- spec impact：
  `updated`

## 冻结结论

- 本文件同时作为 fast-lane 的 requirement brief 和 requirement freeze。
- 只有 `AI 语义复核: yes` 时，本文件才能满足 fast-lane freeze gate；draft 或 no 必须先补 Codex 语义复核。
- 如果后续发现需要完整 adapter runtime 或 CLI 产品化，退出 fast-lane，另开 standard / discovery 任务。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `.gstack/reviews/`。
