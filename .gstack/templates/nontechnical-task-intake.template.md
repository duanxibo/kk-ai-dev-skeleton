# 非技术任务入口模板

本模板用于把非技术用户的自然语言需求转换为 `.gstack` 正式任务输入。

使用原则：

- 用户只需要回答业务问题，不需要理解 `boundary`、`spec`、`Required Gates` 或测试命令。
- Codex 负责把本模板内容转成 requirement、review、task boundary、Spec Sync Plan 和 QA 计划。
- 如果信息不足，Codex 只追问会改变产品结果或风险等级的问题；能从仓库证据推断的内容不要反复问用户。

## 用户原话

- 用户想做什么：
- 用户为什么现在要做：
- 用户说“完成”的直观样子：

## 给谁用

- 目标用户：
- 使用场景：
- 使用频率：
- 现在线下或替代方案怎么做：

## 期望体验

- 用户第一眼应该看到什么：
- 用户必须能完成的动作：
- 用户期望的可见变化是什么：
- 这次需求属于哪种实现表面：
  `生成命令 / CLI 参数 / 后端接口 / 页面内交互控件 / 用户可见 UI 变化 / 静态输出 / 不确定`
- 如果用户说“筛选 / 排序 / 搜索 / 操作入口 / 看不到页面变化”，默认解释为：
  `页面内可见能力`
- 如果本次只做 CLI、生成器参数或后端接口而不会改变页面：
  - 是否已向用户解释：
    `是 / 否`
  - requirement 中的解释位置：
    `待补`
- 用户不应该被迫理解的技术细节：
- 失败或数据缺失时应该怎么提示：

## 数据与内容

- 需要展示或保存哪些信息：
- 数据从哪里来：
  `用户提供 / 现有页面 / 现有接口 / Excel / 数据库 / 暂不确定`
- 是否涉及真实生产数据：
  `是 / 否 / 不确定`
- 是否有样例：
  `有 / 没有 / 需要 Codex 从仓库找`

## 成功标准

- 最小可验收结果：
- 用户会如何判断它可用：
- 用户会在哪个页面、URL、文件或命令输出里看到变化：
- 如果用户刷新后看不到变化，应该先排查什么：
- 必须避免的错误：

## 本次不做

- 明确不做的功能：
- 明确不改的页面、数据或流程：
- 可以以后再做的增强：

## 风险确认

- 是否可能影响真实数据：
  `是 / 否 / 不确定`
- 是否可能影响生产环境：
  `是 / 否 / 不确定`
- 是否需要业务口径确认：
  `是 / 否 / 不确定`
- 是否需要 git action：
  `是 / 否 / 不确定`

## Codex 转译区

以下内容由 Codex 填写，用户不用手写。

- 推荐 Flow Lane：
  `fast-lane / standard / discovery`
- 推荐协作模式：
  `自主执行 / 关键确认 / 手动控制`
- 推断 stack domain：
- 需要的 Required Gates：
  - `data-access`: `required / not-required / unsure`
  - `data-query`: `required / not-required / unsure`
  - `prototype-logic-extraction`: `required / not-required / unsure`
  - `data-knowledge-sync`: `required / not-required / unsure`
  - `doc-backfill`: `required / not-required / unsure`
- 需要生成的 repo-native evidence：
  - requirement:
  - review:
  - boundary:
  - domain spec:
  - QA:
- 用户可见验收转译：
  - User-visible Acceptance:
  - Generated Artifact Policy:
  - 验收 URL / 打开方式:
  - 刷新 / 重新生成方式:
  - 交互证据要求:
- 需要追问用户的问题：
  - 问题：
    - 为什么必须问：
    - 推荐默认答案：

## 进入正式任务条件

- 已能用一句话说明目标用户和最小可验收结果。
- 已能说明用户期望的可见变化；如果没有可见页面变化，已解释为什么本轮只做 CLI / 参数 / 接口 / 静态输出。
- 已明确本次不做什么。
- 已判断是否涉及真实数据、生产、DB schema 或 git action。
- Codex 已能生成 requirement brief 和 task boundary，或已明确进入 discovery。
