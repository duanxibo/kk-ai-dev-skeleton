# productization-hardening Fast-lane Review

- 日期: 2026-06-13
- Reviewer: Codex
- AI 语义复核: yes
- 关联 requirement: `.gstack/requirements/2026-06-13_productization-hardening-fast-lane-requirement.md`

## CEO / Product Review

当前最大缺口不是功能缺失，而是产品入口不够“短”：伙伴不应该先理解 adapter、boundary、gate、evidence 才能开始。他们只需要知道在 Codex 里怎么说、什么时候看结果、什么时候会被要求确认。维护者和 Codex 才需要理解内部机制。

决策：新增普通用户短入口，把复杂概念降到结果层；保留完整工程规则作为幕后执行协议。

## Engineering Review

doctor 已经能发现 hooks、skills 和上下文串味问题，但还缺一个一键式本地准备入口。现有 `sync_repo_skills.sh` 与 `install_git_hooks.sh` 可复用，不应重写逻辑。

决策：新增薄封装脚本串联本机准备步骤；doctor 的 context-isolation 应区分“真实外部 skill 污染”和“父目录名提醒”。前者继续 warn，后者作为 detail 提示，避免健康检查长期误报。

## Risk Review

- 本机 skills 同步会改 `~/.codex/skills` symlink，应只处理 repo-native kk-* 和用户明确要求清理的 tg-* symlink。
- hooks 安装只改本仓库 local git config，不自动提交。
- 不应把产品化入口写成必须由普通用户执行命令；命令只给 Codex / 维护者作为幕后确定性动作。

## Decision

通过 fast-lane。实现应保持小范围，优先补脚本、doctor、短文档、测试和 QA evidence。
