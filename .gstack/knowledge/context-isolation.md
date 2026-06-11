# 上下文隔离

这个文件定义公开骨架如何避免“串味”。

## 项目身份真源

当前项目身份只来自：

- 用户本轮明确描述
- 当前仓库 `README.md` / `AGENTS.md` / `.gstack/README.md`
- active project adapter
- active task boundary
- 当前仓库内的 requirement、review、QA、decision 和长期 spec

## 不可信外部线索

这些信息只能作为环境线索，不能作为项目语义：

- 父目录名
- 绝对路径片段
- 全局可用 skills 列表
- 兄弟仓库或旧仓库
- 缓存、历史会话、终端历史、浏览器历史
- 本机用户名或工作区命名

## Skill 命名规则

本骨架的公开工作流使用 `kk-*`。

如果全局 skill 列表中出现其它项目的私有前缀，例如 `tg-*`，只说明本机曾安装过其它项目 skill。除非用户明确点名，或者当前仓库 `.gstack/skills/` 中存在对应 skill，否则不要把这些 skill 当成当前项目规则来源。

## 对话规则

- 用户说 DataWorks / ODPS，就按 DataWorks / ODPS 理解。
- 用户说新 CRM、BI、SaaS、游戏或内部工具，就按用户描述和 adapter 理解。
- 不要因为父路径、旧 skill 或历史文档里出现其它项目名，就把当前项目称为那个旧项目。
- 如果当前仓库真源和用户描述冲突，先问一个最小澄清问题。

## 本地排查

```bash
python3 .gstack/scripts/gstack_doctor.py check
bash .gstack/scripts/sync_repo_skills.sh
```

如果本机已经不需要旧的 `tg-*` symlink，可以显式清理：

```bash
bash .gstack/scripts/sync_repo_skills.sh --remove-tg-links
```
