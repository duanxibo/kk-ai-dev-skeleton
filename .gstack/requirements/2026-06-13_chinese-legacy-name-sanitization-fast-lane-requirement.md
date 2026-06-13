# chinese-legacy-name-sanitization Fast-lane Requirement

- 日期: 2026-06-13
- 负责人: Codex
- AI 语义复核: yes
- Flow Lane: fast-lane

## 背景

review 指出公开骨架仍有一个中文旧项目名残留，且全 tracked tree 扫描测试只覆盖英文和路径形态，未覆盖中文旧项目名。

## 用户目标

- 清理该中文旧项目名残留。
- 将中文旧项目名加入全 tracked tree 敏感 token 扫描。

## 范围

- 允许修改相关 requirement 文本、测试和本次过程产物。
- 不改变脚本行为、plugin manifest、marketplace name 或版本号。
- 不执行 commit / push，除非用户另行明确批准。

## 验收标准

- tracked tree 中不再出现中文旧项目名残留。
- 测试覆盖中文旧项目名，并避免测试文件自身写入该字面量。

## Requirement Freeze

本 fast-lane requirement 同时作为 requirement-freeze。
