# Fast-lane Requirement 模板

- 需求名称：
- 提出人：
- 日期：
- 当前状态：`ready-for-implementation / blocked`
- Flow Lane：`fast-lane`
- 协作模式：`自主执行 / 关键确认 / 手动控制`
- 关联 boundary：
- AI 语义复核：
  `yes / no`

## 需求一句话

- 用户要完成什么：

## 为什么可以走 fast-lane

- 范围小：
  `是 / 否`
- 需求明确：
  `是 / 否`
- 不涉及业务口径多解：
  `是 / 否`
- 不涉及 DB schema、生产操作或 git workflow action：
  `是 / 否`
- 可本地验证：
  `是 / 否`

## 本次必须做

-

## 用户可见变化拆解

- 生成命令 / CLI 参数：
  `不涉及 / 涉及，写清命令、参数和用户为什么需要知道`
- 后端接口：
  `不涉及 / 涉及，写清接口变化和页面是否会消费`
- 页面内交互控件：
  `不涉及 / 涉及，写清筛选、排序、搜索、操作入口或状态切换`
- 用户可见 UI 变化：
  `不涉及 / 涉及，写清用户第一眼会看到什么变化`
- 静态输出 / 生成文件：
  `不涉及 / 涉及，写清文件如何重新生成、如何打开最新版本`
- 用户期望的可见变化：
  `必须填写；fast-lane 不能省略`
- 如果用户说“筛选 / 排序 / 搜索 / 操作入口 / 看不到页面变化”：
  默认按页面内可见能力理解；如果本轮只做 CLI 或生成器参数，必须在这里写明原因并向用户解释。

## 本次明确不做

-

## 影响面

- 代码 / 文档路径：
- 数据 / 接口 / 权限：
  `不涉及 / 涉及，见 boundary Required Gates`
- spec impact：
  `updated / not-required / pending`

## 冻结结论

- 本文件同时作为 fast-lane 的 requirement brief 和 requirement freeze。
- 只有 `AI 语义复核: yes` 时，本文件才能满足 fast-lane freeze gate；draft 或 no 必须先补 Codex 语义复核。
- 如果后续发现需求有多解、影响面扩大或需要业务口径确认，必须退出 fast-lane，回到 standard / discovery 流程。

## 进入实现条件

- active boundary 已记录 `Decision Mode`、`Autonomy Plan`、`Subagent Plan`、`Required Gates` 和 `Spec Sync Plan`。
- fast-lane review 已落到 `.gstack/reviews/`。
