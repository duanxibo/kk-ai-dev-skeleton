# Partner Install

本文是发给公司伙伴的最短安装入口。伙伴不需要理解本仓库结构，也不需要手动学习脚本参数。

## 直接发给伙伴的话

让伙伴在 Codex 新线程里发送：

```text
请帮我安装 KK Dev Skeleton 的 Codex plugin。

Marketplace Git 地址：https://github.com/duanxibo/kk-ai-dev-skeleton.git
Marketplace name：kk-dev-skeleton-internal
Plugin name：kk-dev-skeleton-adoption

请你先添加这个 marketplace，再安装 plugin。安装完成后，告诉我下一步如何用自然语言把当前项目接入 KK Dev Skeleton。

不要连接真实数据、生产环境、数据库，也不要执行 git commit、push 或部署。
```

安装完成后，伙伴需要新开一个 Codex 线程，然后发送：

```text
请使用 KK Dev Skeleton Adoption，帮我把当前项目接入 KK Dev Skeleton。

项目名：<项目名>
主要用户：<谁会用这个项目>
项目目标：<这个项目要解决什么问题>
源码大致位置：<例如 app/、src/、packages/，不知道可以写“不确定，请你判断”>
产品 / API / 数据 / UI / 测试文档位置：<如果不知道，请你先扫描并建议>
本次不要碰：<明确不要改的目录、业务范围或风险动作>
先不要操作：真实数据、生产环境、数据库、代码提交流程。

请你创建或更新项目 adapter，运行接入自检，告诉我还缺什么，以及建议第一个低风险试点任务。
```

## Codex 背后的等价安装动作

Codex 或管理员会执行的等价命令是：

```bash
codex plugin marketplace add https://github.com/duanxibo/kk-ai-dev-skeleton.git --ref main
codex plugin add kk-dev-skeleton-adoption@kk-dev-skeleton-internal
```

普通伙伴可以不知道这些命令。它们只用于安装排障、管理员检查或自动化说明。

## 验收标准

- Codex 能列出或安装 `kk-dev-skeleton-adoption`。
- 安装后新线程能触发 `KK Dev Skeleton Adoption`。
- 首次接入输出仍然要求目标项目的 `AGENTS.md`、adapter、active boundary 和 guard 作为权威约束。
- 安装流程不会默认触碰真实数据、生产环境、数据库或 git workflow action。

## 升级

发布仓库更新后，伙伴可以让 Codex 执行：

```text
请升级 KK Dev Skeleton 的 Codex marketplace，并重新安装 kk-dev-skeleton-adoption。升级后新开线程验证。
```

Codex 背后的等价动作是：

```bash
codex plugin marketplace upgrade kk-dev-skeleton-internal
codex plugin add kk-dev-skeleton-adoption@kk-dev-skeleton-internal
```
