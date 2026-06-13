# public-distribution-sanitization Fast-lane Requirement

- 日期: 2026-06-13
- 负责人: Codex
- AI 语义复核: yes
- Flow Lane: fast-lane

## 背景

review 指出当前公开骨架仍有分发风险：

- 默认运行 `bash scripts/setup_local_codex.sh` 会在 `set -u` 下因为空数组展开失败。
- 历史 `.gstack/` evidence 里仍可能残留本机绝对路径或源项目名。
- doctor core-docs 仍未覆盖 README 发放清单里的全部产品化入口。

## 用户目标

- 修复默认 setup 命令。
- 清理 tracked 文件中的本机绝对路径和源项目 / 试点项目命名残留。
- 让 doctor 覆盖完整发放清单。
- 增加全仓库敏感 token 扫描测试，防止回归。

## 范围

- 允许修改 `scripts/setup_local_codex.sh`、`.gstack/scripts/gstack_doctor.py`、测试和历史 `.gstack/` evidence 中的敏感路径 / 源项目名文本。
- 不改变 plugin manifest、marketplace name、版本号或业务逻辑。
- 不执行 commit / push，除非用户另行明确批准。

## 验收标准

- `CODEX_HOME=<tmp> bash scripts/setup_local_codex.sh` 不再因空数组失败。
- `git ls-files` 范围内不再出现本机绝对路径、源项目名或试点项目名残留。
- doctor core-docs 覆盖 `.agents/plugins/marketplace.json`、rollout 和 feedback 等 README 发放项。
- 单元测试覆盖默认 setup 路径和全仓库敏感 token 扫描。

## Requirement Freeze

本 fast-lane requirement 同时作为 requirement-freeze。该任务只修复公共骨架分发质量，不改变具体项目 domain spec。
