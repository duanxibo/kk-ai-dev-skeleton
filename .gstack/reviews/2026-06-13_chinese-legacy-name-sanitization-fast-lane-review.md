# chinese-legacy-name-sanitization Fast-lane Review

- 日期: 2026-06-13
- Reviewer: Codex
- AI 语义复核: yes
- 关联 requirement: `.gstack/requirements/2026-06-13_chinese-legacy-name-sanitization-fast-lane-requirement.md`

## Review

问题成立。公开分发扫描必须覆盖中英文旧项目命名形态，不能只覆盖英文路径或罗马化项目名。

决策：把历史 requirement 中的具体中文旧项目名改为通用“旧项目名”，并在测试中用字符串拼接构造该敏感 token，避免测试文件自身污染公开扫描。
