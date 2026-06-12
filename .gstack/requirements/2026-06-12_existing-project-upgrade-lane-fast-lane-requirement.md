# existing-project-upgrade-lane Fast-lane Requirement

- 主题：existing-project-upgrade-lane
- 日期：2026-06-12
- Flow Lane：`fast-lane`
- 协作模式：`自主执行`
- 来源：用户希望插件更新后，伙伴可以方便地对已有项目做增量改造，而不是重新起一个新项目重新接入。
- AI 语义复核: yes

## 用户目标

伙伴更新 `kk-dev-skeleton-adoption` 插件后，可以在已有项目中直接对 Codex 说“按最新版骨架升级当前项目”，Codex 应基于当前项目状态生成增量升级计划，并只执行安全、幂等的改造。

## 最小交付范围

- 在 V1 helper 中新增已有项目升级计划入口。
- 支持安全增量应用：创建缺失的 `stack/<adapter>/` layout，但不覆盖 adapter、不移动业务代码。
- 插件 skill 明确已有项目升级 workflow，不要求用户重新创建项目。
- 文档给伙伴一条自然语言升级指令。
- 测试覆盖升级计划和安全应用。

## 明确不做

- 不自动覆盖或重写已有 `adapters/<project>/adapter.md` / `runtime.json`。
- 不自动移动 `src/`、`prisma/`、`e2e/`、`package.json` 等根目录代码。
- 不实现 framework core 文件全量同步器。
- 不执行 git workflow action 或发布。

## 验收标准

- `python3 scripts/init_project.py --adapter <adapter> --upgrade-plan` 输出“增量升级计划”，并说明不是重新接入。
- `--upgrade-apply` 在已有 adapter 时创建缺失的 `stack/<adapter>/`。
- 已有根目录代码只作为迁移候选输出。
- 插件 skill 包含“Existing Project Upgrade”流程。

## Requirement Freeze

本 fast-lane requirement 同时作为 requirement freeze；如实现中需要自动覆盖 adapter、迁移业务代码或同步 framework core 文件，应退出 fast-lane 并重新确认。
