# plugin-update-reminder Fast-lane Requirement

- 主题：plugin-update-reminder
- 日期：2026-06-12
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 来源：用户要求“做成 产品化成自动提醒”
- AI 语义复核: yes

## 用户目标

当 KK Dev Skeleton GitHub 仓库发布新版插件后，伙伴在 Codex 中使用插件时能够自动感知“插件有更新”，而不是完全依赖人工群通知或阅读文档。

## 最小交付范围

- 在 `kk-dev-skeleton-adoption` 插件中提供非阻断式版本检查能力。
- 插件 workflow 开始时要求 Codex 运行更新检查。
- 本地版本落后远端 GitHub `main` 插件版本时，给出清晰升级提醒和自然语言/命令等价指引。
- 更新检查失败时不阻断用户继续使用插件。
- 增加测试覆盖版本相同、版本落后和无法检查三种状态。

## 明确不做

- 不实现后台常驻进程、系统通知、推送弹窗或自动安装。
- 不自动执行 `marketplace upgrade`、插件重装或 git workflow action。
- 不修改伙伴已有项目。
- 不改变 marketplace 安装策略。

## 验收标准

- 本地插件版本低于远端版本时，检查脚本输出包含 `codex plugin marketplace upgrade kk-dev-skeleton-internal`。
- Skill 文档明确把更新检查作为 adoption workflow 的前置非阻断步骤。
- 测试覆盖更新检查 helper。
- Plugin validator 和 skill validator 通过。

## Requirement Freeze

本 fast-lane requirement 同时作为 requirement freeze；如实现中需要后台通知、自动升级或外部服务，应退出 fast-lane 并重新确认。
