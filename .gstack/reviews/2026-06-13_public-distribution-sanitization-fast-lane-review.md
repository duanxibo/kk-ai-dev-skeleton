# public-distribution-sanitization Fast-lane Review

- 日期: 2026-06-13
- Reviewer: Codex
- AI 语义复核: yes
- 关联 requirement: `.gstack/requirements/2026-06-13_public-distribution-sanitization-fast-lane-requirement.md`

## Product Review

公开骨架如果完整发放 `.gstack/`，历史 evidence 也属于用户可见资产。仅清理入口文档不够，必须把 tracked tree 作为发放面整体扫描。

决策：保留历史 evidence 的结构和验证价值，但把本机路径、源项目名和试点项目名替换为通用占位符。

## Engineering Review

setup 默认路径失败来自 Bash `set -u` 下空数组展开。最小修复是不用空数组，按参数分支直接调用 skill sync 脚本。

doctor core docs 应反映 README 发放清单，包括 marketplace source、rollout 和 feedback 文件。

## Risk Review

- 机械清理只改文本 evidence，不改变脚本行为。
- 全仓库扫描测试需要避免测试自身引入敏感 token。
- 不执行 git workflow action。

## Decision

通过 fast-lane。
