# 文档放置规则

这份指南用于判断长期文档应该放在哪里。

## 核心规则

先问三个问题：

1. 这是可复用协作行为吗？
2. 这是某个具体项目 adapter 的规则吗？
3. 这是应用真源或实现细节吗？

## 放入 `.gstack/`

`.gstack/` 用于：

- task boundaries
- requirement briefs 和 freezes
- review reports
- QA reports
- decision records
- reusable learnings
- workflow skills
- templates
- guard 和 dashboard 规则
- 可复用 AI 协作知识

不要把完整应用 spec 或业务实现细节放在这里，除非它们只是 examples。

## 放入 `adapters/`

`adapters/<name>/` 用于项目专属规则：

- 技术栈
- 真源路径
- 实现路径
- 测试命令
- 数据和 API 策略
- forbidden paths
- 部署和回滚规则
- 项目专属 gates

## 放入应用源码

项目应用路径用于：

- product specs
- API contracts
- data models
- implementation docs
- fixtures
- tests
- application source code

具体路径由 adapter 定义。

## 放入 `examples/`

`examples/` 用于脱敏 demo app 和教学流程。

example 内容不能成为真实项目的默认真源。

## 放入 `tests/`

`tests/` 用于跨项目验证框架行为的骨架级检查。

## 链接

长期文档应使用 repo-relative 路径，避免本机绝对路径。
