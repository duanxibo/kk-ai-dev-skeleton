# productization-review-followups Fast-lane Requirement

- 日期: 2026-06-13
- 负责人: Codex
- AI 语义复核: yes
- Flow Lane: fast-lane

## 背景

发布后的 review 指出公共骨架仍有几处产品化可迁移性和自检覆盖问题：

- 安装文档包含本机绝对路径。
- `scripts/setup_local_codex.sh` 在非 git worktree 发放包里会因为 hooks 安装失败而中断。
- doctor 的 core docs 检查没有覆盖新增产品化入口。
- context-isolation 的下一步说明没有区分 symlink 和普通目录。

## 用户目标

- 修复公开文档中的本机绝对路径。
- 让 setup 脚本在无 `.git` 的骨架包中自动跳过 hooks 并继续 doctor。
- 扩大 doctor 核心入口检查，覆盖新增用户入口、setup helper 和公共 workspace layers。
- 让 doctor 对外部 skill symlink / 普通目录给出准确下一步。

## 范围

- 允许修改插件安装文档、setup 脚本、doctor、相关测试和本次过程产物。
- 不改变 plugin manifest、marketplace name、版本号或已发布 Git remote。
- 不执行 commit / push，除非用户另行明确批准。

## 验收标准

- 公开文档不再出现 `<local-home>/...` 这类本机绝对路径。
- `scripts/setup_local_codex.sh` 在非 git worktree 中可以跳过 hooks 并运行 doctor。
- doctor core docs 能检查 `QUICK_START_FOR_PARTNERS.md`、`scripts/setup_local_codex.sh`、`blueprint/`、`archive/`、`shared/` 等新增入口。
- context-isolation 的用户下一步能根据 symlink / 普通目录区别说明。
- 新增或调整测试覆盖以上行为。

## Requirement Freeze

本 fast-lane requirement 同时作为 requirement-freeze。该任务只修复公共骨架产品化分发和自检问题，不改变具体项目 domain spec。
