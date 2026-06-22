# Target-aware doctor fast-lane requirement

- 需求名称：让 `gstack_doctor.py` 区分骨架源仓库和安装后的目标仓库
- 提出人：用户
- 日期：2026-06-22
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 关联 boundary：`.gstack/task-boundaries/2026-06-22_target-aware-doctor.md`
- AI 语义复核：`yes`

## 需求一句话

- 用户要完成什么：长期修复目标项目运行 doctor 时因为缺少骨架源仓库发布文档而失败的问题。

## 为什么可以走 fast-lane

- 范围小：是，只涉及协作脚本、定向测试和本次 evidence。
- 需求明确：是，`kk-ai-factory` 作为安装后目标仓库不应要求 `QUICK_START_FOR_PARTNERS.md`、插件发布文档等源仓库资料。
- 不涉及业务口径多解：是。
- 不涉及 DB schema、生产操作或 git workflow action：是。
- 可本地验证：是，可用临时安装目标仓库和真实 `kk-ai-factory` 跑 doctor。

## 本次必须做

- 将 doctor 的 core docs 检查拆分为 portable target core 与 skeleton source-only distribution docs。
- 复用与安装器一致的 skeleton marker 判断，避免 doctor 和 installer 口径分叉。
- 保持骨架源仓库继续检查发布、插件、伙伴安装文档。
- 让安装后的目标仓库只因为缺少 portable core、adapter metadata 或 runtime bundle 必需文件而失败。
- 补定向回归，证明目标仓库模式不会要求源仓库发布文档。

## 用户可见变化拆解

- 生成命令 / CLI 参数：涉及；用户仍运行 `python3 .gstack/scripts/gstack_doctor.py check`，命令不变。
- 后端接口：不涉及。
- 页面内交互控件：不涉及。
- 用户可见 UI 变化：不涉及。
- 静态输出 / 生成文件：涉及；doctor 输出会说明当前检查模式和检查了多少个入口文档。
- 用户期望的可见变化：在 `kk-ai-factory` 这类目标项目里，doctor 不再因为缺少骨架源仓库的发布文档而整体 fail。

## 本次明确不做

- 不重构安装器的 runtime bundle 写入策略。
- 不覆盖目标项目已有脚本的长期升级机制。
- 不清理用户本机全局 `tg-*` 或旧 `kk-*` skill symlink。
- 不开发线上 AI Software Factory 平台功能。
- 不执行 git commit、push 或 PR。

## 影响面

- 代码 / 文档路径：`.gstack/scripts/gstack_doctor.py`、`tests/`、本次 `.gstack/` evidence。
- 数据 / 接口 / 权限：不涉及。
- spec impact：updated，更新 `.gstack/knowledge/ai-programming-framework.md` 的 doctor 分层规则。

## 冻结结论

- 本文件同时作为 fast-lane 的 requirement brief 和 requirement freeze。
- 如果实现中发现需要改变 portable core 文件清单或安装器覆盖策略，退出 fast-lane 并另起标准任务。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `.gstack/reviews/`。
