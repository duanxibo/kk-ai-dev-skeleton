# Marketplace / Plugin 安装推广计划

本文用于把 `kk-dev-skeleton-adoption` 从“已经有 repo-local marketplace source”推进到“公司伙伴可以试点使用”。它面向推广负责人、管理员和试点伙伴。

普通伙伴的入口不是命令行，而是在 Codex 里用自然语言发起接入。安装 marketplace 和 plugin 是管理员 / 发布负责人在明确授权后的动作。

## 当前推广形态

- Marketplace name: `kk-dev-skeleton-internal`
- Plugin name: `kk-dev-skeleton-adoption`
- Marketplace source: `.agents/plugins/marketplace.json`
- Plugin source: `plugins/kk-dev-skeleton-adoption/`
- Published Git marketplace: `https://github.com/duanxibo/kk-ai-dev-skeleton.git`
- Partner install entry: `plugins/PARTNER_INSTALL.md`
- 安装说明: `plugins/MARKETPLACE_INSTALL.md`
- 管理员清单: `plugins/ADMIN_INSTALL_CHECKLIST.md`
- 试点反馈表: `plugins/PILOT_FEEDBACK.md`

## 角色分工

- 推广负责人：选择试点项目、确认试点范围、收集反馈、决定是否扩大范围。
- 管理员 / 发布负责人：在明确授权后安装或更新 repo-local marketplace 和 plugin。
- 试点伙伴：在 Codex 中用自然语言请求接入，不直接执行安装命令。
- Skeleton owner：根据反馈修正文档、adapter 规则、plugin skill 或 V1 helper。

## 七天推广节奏

### Day 0: 准备

- 确认本仓库是本次推广的来源。
- 选择 2 到 3 个低风险试点项目。
- 确认试点不涉及真实数据写入、生产环境、数据库 schema、批量导出或 git workflow action。
- 管理员按 `plugins/ADMIN_INSTALL_CHECKLIST.md` 完成安装前检查。
- 推广负责人把 `plugins/PILOT_FEEDBACK.md` 发给试点伙伴。

### Day 1: 首次安装和首个线程

- 管理员在明确授权后安装 `kk-dev-skeleton-internal` marketplace。
- 管理员安装 `kk-dev-skeleton-adoption@kk-dev-skeleton-internal`。
- 如果使用公开发布仓库，优先按 `plugins/PARTNER_INSTALL.md` 使用 Git marketplace 地址安装。
- 试点伙伴新开 Codex 线程，并用本文的试点提示发起接入。
- 首次试点只要求生成接入报告和第一个低风险试点任务建议。

### Day 3: 反馈修正

- 汇总试点伙伴反馈。
- 优先修复三类问题：自然语言提示不清、adapter 草案不准、验证报告不可读。
- 如果问题来自 plugin skill 或 V1 helper，先在本仓库修复并重新验证，再让管理员按安装说明升级。

### Day 7: 扩大或暂停

- 如果两个以上试点能完成接入报告和低风险试点任务建议，可以扩大到下一批团队。
- 如果反馈集中在安全边界、权限或安装不稳定，暂停扩大，先修复推广材料或接入器。
- 如果出现真实数据、生产、数据库或 git workflow action 的误触发风险，暂停推广并更新安全规则。

## 试点伙伴自然语言入口

试点伙伴在已安装 plugin 的 Codex 环境中新开线程，然后发送：

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

如果试点伙伴不确定项目结构，可以把路径写成“不确定，请你判断”。Codex 应先读当前项目入口和 adapter，再给出接入计划。

## 管理员安装入口

管理员按 `plugins/ADMIN_INSTALL_CHECKLIST.md` 操作。安装命令只应在明确授权后执行。

核心安装动作是：

```bash
codex plugin marketplace add https://github.com/duanxibo/kk-ai-dev-skeleton.git --ref main
codex plugin add kk-dev-skeleton-adoption@kk-dev-skeleton-internal
```

安装后必须新开 Codex 线程验证 plugin 是否可见；不要在旧线程里判断安装结果。

## 成功标准

- Codex 中能看到或触发 `kk-dev-skeleton-adoption`。
- 试点伙伴能用自然语言启动接入，不需要手动学习脚本参数。
- Codex 能生成 adapter 草案、接入自检结果和第一个低风险试点任务建议。
- 接入报告能明确哪些检查通过、哪些缺失、哪些动作需要用户授权。
- 试点任务没有默认触碰真实数据、生产、数据库或 git workflow action。
- 至少一份 `plugins/PILOT_FEEDBACK.md` 被完整填写。

## 暂停和回滚策略

遇到以下任一情况，暂停向新伙伴推广：

- plugin 无法稳定安装或新线程无法触发。
- Codex 把普通伙伴引导到命令行安装流程。
- Codex 默认触碰真实数据、生产、数据库或 git workflow action。
- adapter 被覆盖而没有明确确认。
- 接入报告让非技术用户无法判断下一步。

回滚时，先停止继续安装和分享入口，再由管理员按公司当前 Codex plugin 管理方式停用或移除该 plugin / marketplace。回滚完成后，把原因记录到 `plugins/PILOT_FEEDBACK.md` 或新的 repo-native QA / review 文档里。

## 推广负责人检查口径

推广负责人每轮只看四件事：

- 伙伴是否能只靠自然语言开始。
- Codex 是否能正确识别当前项目，而不是套用旧项目上下文。
- 输出是否能让非技术伙伴看懂。
- 安全边界是否在报告里被明确保留。
