# Pitfalls

本目录记录跨项目可复用的坑。

公开骨架默认不放具体业务坑；项目接入后可以按技术栈、模块或任务类型添加文件，例如：

- `frontend.md`
- `backend.md`
- `data-access.md`
- `deploy.md`
- `testing.md`

## 写入标准

只有满足以下条件之一，才写入 pitfall：

- 同类问题可能再次发生。
- 已导致 QA 失败、用户回改或 CI 失败。
- 能形成明确的预防规则。

每条 pitfall 应包含：

- 触发场景
- 错误表现
- 根因
- 正确做法
- 验证方式
- 适用范围
