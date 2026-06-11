# Data Interface Design Guide

当数据发现结果进入 API、读模型、报表接口或跨系统复用时，先读本指南。

## 设计前提

- 已有 requirement brief。
- 已有 task boundary。
- 数据来源、scope 和字段口径已有 evidence。
- 如果后端承接前端 / 原型 / mock 逻辑，已声明 `prototype-logic-extraction` gate。

## 接口设计必须说明

- 调用方和使用场景
- 输入参数
- 输出字段
- 字段口径
- 事实源
- 时间范围和 scope
- 空态
- 异常态
- 权限和授权行为
- 缓存或新鲜度假设
- 兼容性和版本策略
- QA 验证样例

## 职责边界

- backend / service 持有持久化、计算、快照和事实源判断。
- frontend 只做渲染、请求编排、轻校验和瞬时 UI 状态。
- analytics warehouse / BI 查询不能成为前端长期依赖。
- 临时 SQL 只能作为发现证据，不能直接变成用户面契约。

## 推荐落点

- 已归属项目模块：
  adapter 指定的 product / API / data / testing 真源目录。
- 跨模块探索期：
  `.gstack/designs/` 或 `.gstack/knowledge/data-access/` 下的 discovery / gap / draft 文档。

## Review 检查

- 输入输出是否足够稳定。
- 字段是否有事实源。
- 空态和异常态是否明确。
- 权限和敏感字段是否处理。
- 是否有测试或 fixture。
- 是否需要 `data-knowledge-sync` 回写 source registry 或项目真源。
