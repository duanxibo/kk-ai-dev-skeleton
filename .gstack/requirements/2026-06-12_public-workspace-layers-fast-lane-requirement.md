# public-workspace-layers Fast-lane Requirement

- 主题：public-workspace-layers
- 日期：2026-06-12
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 来源：用户确认要补齐公共骨架中缺失的 `archive/`、`blueprint/`、`shared/` 等能力落点。
- AI 语义复核: yes

## 用户目标

公共骨架不应复制 TianGong 私有历史内容，但应保留可复用的工作区层能力：历史归档、前置蓝图、共享输入、设计记录和迁移记录。

## 最小交付范围

- 新增空的公共目录和 README / template：
  - `archive/`
  - `archive/baseline/`
  - `blueprint/`
  - `shared/`
  - `.gstack/designs/`
  - `.gstack/migrations/`
- 更新文档放置规则、仓库地图、README 和默认 adapter。
- 让 `scripts/init_project.py` 在 apply / upgrade-apply 时确保这些 workspace layers 存在。
- 增加测试覆盖初始化 helper 会创建这些层。

## 明确不做

- 不复制 TianGong 的历史 archive、baseline、blueprint 或 shared 数据。
- 不引入真实 Excel、CSV、SQL evidence、旧页面、旧业务脚本或私有设计内容。
- 不发布、commit、push。
- 不修改真实试点项目。

## 验收标准

- 公共骨架本身包含上述空层和说明。
- 初始化 helper 能创建上述空层。
- README 目录结构能看到 `archive/`、`blueprint/`、`shared/`、`.gstack/designs/`、`.gstack/migrations/`。
- 测试和 gstack guards 通过。

## Requirement Freeze

本 fast-lane requirement 同时作为 requirement freeze；如实现中需要复制项目业务资产或真实数据，应退出 fast-lane 并重新确认。
