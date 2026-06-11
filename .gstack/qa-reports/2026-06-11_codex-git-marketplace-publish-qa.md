# codex-git-marketplace-publish QA

- 日期：2026-06-11
- 任务：codex-git-marketplace-publish
- Boundary：`.gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md`
- QA 类型：Git marketplace publish / plugin distribution QA
- 结论：通过

## 发布目标

- GitHub repo：`https://github.com/duanxibo/kk-ai-dev-skeleton.git`
- Branch：`main`
- Marketplace name：`kk-dev-skeleton-internal`
- Plugin name：`kk-dev-skeleton-adoption`

## 本次改动

- 新增 `plugins/PARTNER_INSTALL.md`，提供可直接发给伙伴的自然语言安装入口。
- 更新 marketplace install / rollout / admin checklist / README / 公司接入指南 / Codex 接入器方案，写入发布仓库地址。
- 新增 `tests/test_git_marketplace_publish_docs.py`，验证 Git marketplace 发布文档。
- 初始化本地 git 仓库，添加 remote，并推送到 GitHub `main`。

## 命令验证

### 文档和 helper 测试

```bash
python3 -m unittest tests/test_git_marketplace_publish_docs.py tests/test_marketplace_rollout_docs.py tests/test_plugin_marketplace.py tests/test_init_project.py
```

结果：通过，20 tests OK。

### Plugin validator

```bash
python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/kk-dev-skeleton-adoption
```

结果：通过。

### Skill validator

```bash
python3 /Users/edy/.codex/skills/.system/skill-creator/scripts/quick_validate.py plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption
```

结果：通过。

### Marketplace name reader

```bash
python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py --marketplace-path .agents/plugins/marketplace.json
```

结果：`kk-dev-skeleton-internal`。

### Spec sync guard

```bash
python3 .gstack/scripts/spec_sync_guard.py
```

结果：通过。

### Team flow guard

```bash
python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD
```

结果：通过。

### Required gates audit

```bash
python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-11_codex-git-marketplace-publish.md
```

结果：通过。

### 敏感信息扫描

```bash
rg --hidden -n "\b(sk-proj|sk)-[A-Za-z0-9_-]{20,}\b|BEGIN (RSA|OPENSSH|PRIVATE) KEY|AKIA[0-9A-Z]{16}" . -g '!*.pyc' -g '!__pycache__/**' -S
```

结果：无匹配。

## Git 发布验证

### Remote

```bash
git remote -v
```

结果：`origin` 指向 `https://github.com/duanxibo/kk-ai-dev-skeleton.git`。

### 首次提交

```bash
git commit -m "feat: 发布 KK Dev Skeleton marketplace"
```

结果：提交 `b6d7264` 创建成功。

### 推送

```bash
git push -u origin main
```

结果：通过，`main` 已推送到 GitHub 并设置 upstream。

## 发布后伙伴入口

给伙伴发送：

```text
请帮我安装 KK Dev Skeleton 的 Codex plugin。

Marketplace Git 地址：https://github.com/duanxibo/kk-ai-dev-skeleton.git
Marketplace name：kk-dev-skeleton-internal
Plugin name：kk-dev-skeleton-adoption

请你先添加这个 marketplace，再安装 plugin。安装完成后，告诉我下一步如何用自然语言把当前项目接入 KK Dev Skeleton。

不要连接真实数据、生产环境、数据库，也不要执行 git commit、push 或部署。
```

## 未执行事项

- 未在当前 Codex 环境安装 plugin。
- 未执行 `codex plugin marketplace add` 或 `codex plugin add`。
- 未触碰真实数据、生产、数据库或部署系统。

## 残余风险

- 本次验证确认 Git repo 已发布、plugin source 有效、marketplace name 可读；没有在第三方伙伴机器上真实安装。首批伙伴安装后应按 `plugins/PILOT_FEEDBACK.md` 收集反馈。
