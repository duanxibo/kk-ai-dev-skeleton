# Admin Install Checklist

本文面向管理员 / 发布负责人。只有在获得明确授权后，才可以安装或升级 repo-local marketplace 和 plugin。

普通业务用户不需要执行这里的命令。他们的入口是在 Codex 中用自然语言请求接入。

## 安装前确认

- 已确认本次要安装的 marketplace 是 `kk-dev-skeleton-internal`。
- 已确认本次要安装的 plugin 是 `kk-dev-skeleton-adoption`。
- 已确认 marketplace root 是当前仓库根目录或发布仓库 `https://github.com/duanxibo/kk-ai-dev-skeleton.git`。
- 已确认 `.agents/plugins/marketplace.json` 指向 `./plugins/kk-dev-skeleton-adoption`。
- 已确认安装动作已获得明确授权。
- 已确认试点项目不默认授权真实数据、生产、数据库或 git workflow action。

## 安装前验证

在仓库根目录运行以下检查：

```bash
python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  plugins/kk-dev-skeleton-adoption
```

```bash
python3 /Users/edy/.codex/skills/.system/skill-creator/scripts/quick_validate.py \
  plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption
```

```bash
python3 /Users/edy/.codex/skills/.system/plugin-creator/scripts/read_marketplace_name.py \
  --marketplace-path .agents/plugins/marketplace.json
```

预期 marketplace name：

```text
kk-dev-skeleton-internal
```

如果任一检查失败，不要继续安装。

## 首次安装

在明确授权后执行：

```bash
codex plugin marketplace add https://github.com/duanxibo/kk-ai-dev-skeleton.git --ref main
```

然后安装 plugin：

```bash
codex plugin add kk-dev-skeleton-adoption@kk-dev-skeleton-internal
```

安装完成后，新开 Codex 线程验证：

```text
请使用 KK Dev Skeleton Adoption，检查当前项目是否已经可以进入 KK Dev Skeleton 接入流程。

只做检查和报告，不要操作真实数据、生产、数据库、git commit 或 push。
```

## 升级

如果 plugin source 更新，先运行安装前验证，再按 `plugins/MARKETPLACE_INSTALL.md` 的升级流程处理。

升级后必须新开 Codex 线程验证。不要用旧线程判断新版本 skill 是否生效。

## 安装后验收

- 新 Codex 线程能识别 `KK Dev Skeleton Adoption`。
- Codex 的首条报告仍然把用户入口描述为自然语言接入。
- Codex 没有要求普通业务用户执行安装命令。
- Codex 没有默认连接真实数据、生产、数据库或执行 git workflow action。
- Codex 能说明目标仓库的 `AGENTS.md`、adapter、active boundary 和 guard 仍然是权威约束。

## 停止条件

出现以下情况时停止安装或升级：

- marketplace name 不是 `kk-dev-skeleton-internal`。
- plugin source 路径不是 `./plugins/kk-dev-skeleton-adoption`。
- validator 失败。
- 新线程无法触发 plugin。
- Codex 将普通用户引导到命令行安装。
- Codex 默认执行真实数据、生产、数据库、破坏性文件操作或 git workflow action。

停止后，把现象和日志摘要写入 `plugins/PILOT_FEEDBACK.md` 或对应 QA 文档。
