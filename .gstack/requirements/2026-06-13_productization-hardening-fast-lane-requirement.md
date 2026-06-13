# productization-hardening Fast-lane Requirement

- 日期: 2026-06-13
- 负责人: Codex
- AI 语义复核: yes
- Flow Lane: fast-lane

## 背景

当前公共骨架方向正确，但评阅指出它仍偏“方法论 + 脚本工具”，距离普通团队可无脑使用的产品还有差距。主要问题集中在概念门槛、接入流程依赖 agent 临场发挥、当前本机 doctor 存在上下文隔离提醒、git hooks 未安装、普通用户入口文档不够短。

## 用户目标

- 先解决当前本机 doctor 中可自动修复的 skills、context-isolation 和 git hooks 提醒。
- 把本机接入 / 修复动作沉淀成确定性产品化入口，减少 Codex 临场解释和漏步骤。
- 给普通伙伴一个更短的自然语言使用入口。
- 强化 hooks / guard 的本地强制执行说明和验证。

## 范围

- 允许新增或调整公共骨架产品化脚本、doctor 行为、README / 接入文档、测试和本次过程产物。
- 不改变真实业务项目代码。
- 不复制 TianGong 私有业务资料。
- 不执行 git commit / push，除非用户另行明确批准。

## 验收标准

- 当前本机可运行确定性命令完成 repo-native skills 同步和 git hooks 安装。
- doctor 对可修复串味风险给出明确自动修复路径；单纯父目录命名提醒不应把整体状态长期打成 warn。
- 普通用户能通过一份短文档知道应该怎么在 Codex 里说、做完怎么看结果、什么时候需要确认。
- 新增或调整内容有测试 / guard 证据。

## Requirement Freeze

本 fast-lane requirement 同时作为 requirement-freeze。该任务只处理公共骨架产品化硬化，不改变具体项目 domain spec。
