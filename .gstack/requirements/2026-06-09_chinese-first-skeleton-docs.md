# Fast-lane Requirement：chinese-first-skeleton-docs

- 需求名称：chinese-first-skeleton-docs
- 提出人：user
- 日期：2026-06-09
- 当前状态：`ready-for-implementation`
- Flow Lane：`fast-lane`
- 协作模式：`autonomous`
- 关联 boundary：`.gstack/task-boundaries/2026-06-09_chinese-first-skeleton-docs.md`
- AI 语义复核：
  `yes`

## 需求一句话

- 用户要完成什么：
  将公开骨架调整为中文优先表达，保留 `kk-*`、脚本名、YAML key、环境变量和固定机制名等机器可读英文标识。

## 本次必须做

- 中文化公开入口文档、AGENTS、`.gstack/README.md`、knowledge、adapter 和示例项目说明。
- 中文化示例 Web App 的用户可见文案。
- 不削弱 `kk-*` skills、doctor、dashboard、smoke、guard 和 task boundary 能力。

## 用户可见变化拆解

- 用户期望的可见变化：
  新用户打开骨架时，主要说明、使用路径、示例验收和页面文案都以中文为主。

## 本次明确不做

- 不重命名 `kk-*` skills。
- 不翻译脚本文件名、YAML key、环境变量或固定英文机制字段。
- 不发布外部仓库。
- 不执行代码提交流程。
