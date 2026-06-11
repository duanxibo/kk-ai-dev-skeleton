# kk-doc-backfill 工作流

## 1. 先定 backfill 范围

明确本次补文档的对象：

- 单个接口
- 单个后端模块
- 单个页面 / fixture / 脚本
- 最近一段 git 改动
- `doc_coverage_audit.py` 报告中的某个缺口

如果范围覆盖多个业务模块，先把任务拆成多个 backfill 小段，避免一次性补出混杂真源。

## 2. 证据收集顺序

推荐顺序：

1. active boundary
2. 当前真源 spec 或 baseline 文档
3. 代码入口：controller / DTO / service / mapper / frontend caller / script
4. 测试、fixture、harness、QA 输出
5. 最近 diff 或 git log
6. 相关 review、decision、learning

只在当前真源无法解释历史口径时才读 `archive/`。

## 3. 证据分级

文档里的关键结论应尽量带来源标记：

- `code-proven`：代码结构或常量能直接证明
- `test-proven`：测试、fixture、harness 或真实验证输出能证明
- `spec-proven`：现有真源文档能证明
- `inferred`：根据代码和命名推断，仍可能需要确认
- `needs-confirmation`：必须由业务、后端或数据负责人确认

不要把 `inferred` 写成确定口径。

## 4. 后端接口 backfill 最小字段

补后端接口文档时至少写清：

- 调用方
- endpoint / method
- 输入参数、类型、必填、默认值、合法范围
- 输出字段、类型、含义、来源、可空性
- 事实源
- scope，默认优先检查 `<scope-key>`
- 空数据、参数非法、权限不足、数据源异常策略
- 是否跨系统复用
- 不应暴露的内部结构
- 待确认项

如果现有数据无法满足接口字段、粒度或口径，先补数据需求缺口，不要直接设计新表。

## 5. 收口

完成 backfill 后：

- 如果只是补当前真源，运行 `spec_sync_guard.py`
- 如果补了 review / decision / learning，检查是否还需要 `kk-doc-sync`
- 如果发现长期规则或坑，写入 `.gstack/rules/` 或 `.gstack/knowledge/pitfalls/`
- 如果发现旧文档已退出主线，再交给 `kk-doc-lifecycle`
