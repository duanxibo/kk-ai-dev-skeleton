# AI 文档落地提示词清单

适用场景：

- 团队成员已经知道“这次该补什么文档”
- 想直接复制一段提示词给 AI
- 希望 AI 先读对文档，再把产物落到 repo 正确位置

使用原则：

- 每条都默认要求 AI 先读入口文档和相关真源
- 每条都默认要求 AI 不要只在聊天里总结
- 如果 AI 判断这次不需要补该类文档，也要明确说明原因

建议固定前缀：

```text
先读仓库入口和本任务相关真源文档，再执行。
不要把关键结论只留在聊天里，需要直接落到 repo 对应文档。
如果你判断这次不需要落这类文档，也要明确说明理由。
```

---

## 1. 需求刚提出时，补 `.gstack/requirements/` requirement brief

适用时机：

- 需求还没有进入 CEO review
- 目标、范围、用户、成功标准或不做什么仍需要稳定输入
- 不想让需求只停留在聊天里

可直接复制：

```text
先读仓库入口和本任务相关真源文档，再执行。
不要把关键结论只留在聊天里，需要直接落到 repo 对应文档。
如果你判断这次不需要落这类文档，也要明确说明理由。

这个需求还没有进入 review。请你先读：
1. AGENTS.md
2. .gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md
3. .gstack/knowledge/CODEMAP.md
4. .gstack/knowledge/doc-placement.md
5. .gstack/requirements/README.md
6. .gstack/templates/requirement-brief.template.md

然后帮我把这次需求整理成 requirement brief，落到 .gstack/requirements/。

文档里请明确：
1. 要解决的问题
2. 目标用户和场景
3. 业务目标和成功标准
4. 本次必须做 / 明确不做 / 可延后
5. 是否涉及原型、数据、接口、权限或口径
6. 待确认问题

如果当前信息不足以进入 plan-ceo-review，请列出缺口，不要硬写成 ready。
```

---

## 2. CEO review 后，补 requirement freeze / prototype freeze

适用时机：

- requirement brief 已经存在
- `plan-ceo-review` 已经给出调整意见
- 需求准备进入 `plan-eng-review` 或 domain spec readiness

可直接复制：

```text
先读仓库入口和本任务相关真源文档，再执行。
不要把关键结论只留在聊天里，需要直接落到 repo 对应文档。
如果你判断这次不需要落这类文档，也要明确说明理由。

这个需求已经完成 CEO review。请你先读：
1. AGENTS.md
2. .gstack/requirements/README.md
3. 对应 requirement brief
4. 对应 plan-ceo-review 结果
5. .gstack/templates/requirement-freeze.template.md

然后帮我整理 requirement freeze 或 prototype freeze，落到 .gstack/requirements/。

文档里请写清楚：
1. 冻结后的需求范围
2. CEO review 后采纳、拒绝或延后的调整
3. 本次工程承接范围
4. 必须保持不变的产品口径
5. domain spec readiness 必须引用的真源
```

---

## 3. 需求确认后，补 `stack` domain spec

适用时机：

- 需求已经基本确认
- 目标行为和范围已有初步答案
- 需要把口头结论变成产品 + 工程统一真源

可直接复制：

```text
先读仓库入口和本任务相关真源文档，再执行。
不要把关键结论只留在聊天里，需要直接落到 repo 对应文档。
如果你判断这次不需要落这类文档，也要明确说明理由。

这个需求已经基本确认。请你先读：
1. AGENTS.md
2. .gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md
3. .gstack/knowledge/CODEMAP.md
4. .gstack/knowledge/doc-placement.md
5. 当前相关 `docs/specs/<module>/` 真源文档
6. .gstack/entrypoints/product-manager.md

然后帮我把这次需求整理进对应 `docs/specs/<module>/` 文档。

文档里请明确：
1. 目标和范围
2. 页面行为 / 业务语义
3. 字段含义
4. 验收标准
5. 本次不做什么

如果你判断当前信息还不足以冻结，请先列出缺失信息，不要硬写成定稿。
```

---

## 4. 正式实现前，补 domain spec readiness

适用时机：

- requirement freeze 已经清楚
- 准备进入正式实现
- 需要确认需求、数据、接口、前端、后端、测试已经落到同一套 stack 真源

可直接复制：

```text
先读仓库入口和本任务相关真源文档，再执行。
不要把关键结论只留在聊天里，需要直接落到 repo 对应文档。
如果你判断这次不需要落这类文档，也要明确说明理由。

这个需求已经准备进入正式实现。请你先读：
1. AGENTS.md
2. .gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md
3. .gstack/knowledge/CODEMAP.md
4. .gstack/knowledge/doc-placement.md
5. 对应 requirement brief
6. 对应 requirement/prototype freeze
7. 相关 `docs/specs/<module>/` 文档
8. .gstack/entrypoints/product-manager.md

然后帮我补齐或确认 domain spec readiness。不要新增 handoff 文档。

文档里请写清楚：
1. 本次目标行为
2. 需求、数据、接口、前端、后端、测试分别落在哪些 domain spec 文件
3. 如果复用 baseline / 原型 / 历史设计材料，来源是什么，采纳和放弃项是什么
4. 未决问题 / 风险点
5. 实现前必须重点关注的接口、数据、测试点

请直接生成 repo 文档草稿，不要只做聊天总结。
```

---

## 5. 实质性实现前，补 `.gstack/task-boundaries/`

适用时机：

- 任务要进入正式实现
- 会改多个文件或多个模块
- 需要明确允许范围和非目标范围

可直接复制：

```text
先读仓库入口和本任务相关真源文档，再执行。
不要把关键结论只留在聊天里，需要直接落到 repo 对应文档。
如果你判断这次不需要落这类文档，也要明确说明理由。

这次任务准备进入正式实现。请你先读：
1. AGENTS.md
2. .gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md
3. .gstack/README.md
4. .gstack/knowledge/CODEMAP.md
5. .gstack/knowledge/doc-placement.md
6. .gstack/entrypoints/engineer.md
7. .gstack/task-boundaries/CURRENT.md

然后先不要直接写代码，先为这次任务补一份 .gstack/task-boundaries/ 下的 boundary 文档，并自动完成当前任务的 active boundary 设置。

boundary 里请明确：
1. Goal
2. Allowed Files
3. Forbidden Files
4. Functional Non-goals
5. Required Knowledge
6. Spec Sync Plan
7. Verification
8. Lessons To Write Back

如果你判断当前已有 boundary 足够，请说明理由，不要默认跳过。
```

---

## 6. 行为或契约变化时，更新 stack domain 真源

适用时机：

- 页面行为变了
- 接口契约变了
- 数据模型或测试口径变了
- 工程实现已超出原有 spec 描述

可直接复制：

```text
先读仓库入口和本任务相关真源文档，再执行。
不要把关键结论只留在聊天里，需要直接落到 repo 对应文档。
如果你判断这次不需要落这类文档，也要明确说明理由。

这次改动会影响行为 / 接口 / 数据契约。请你先读：
1. AGENTS.md
2. .gstack/knowledge/CODEMAP.md
3. .gstack/knowledge/doc-placement.md
4. 当前 active boundary
5. 相关 `docs/specs/<module>/` 真源文档

然后请你先判断这次变化应该更新哪些 domain spec 文档：
- 产品行为 / 页面语义 -> `frontend.md`、`requirements.md` 或模块 README
- 工程规格 / 接口 / 数据模型变化 -> `backend.md`、`data.md`、`testing.md`

判断后直接补对应真源文档，不要只改代码。

如果你判断这次不需要改真源文档，请明确写出原因。
```

---

## 7. 完成前，补 `review` 或 `QA`

适用时机：

- 任务准备收口
- 需要留下正式验证记录
- 需要说明风险、检查项和完成判断

可直接复制：

```text
先读仓库入口和本任务相关真源文档，再执行。
不要把关键结论只留在聊天里，需要直接落到 repo 对应文档。
如果你判断这次不需要落这类文档，也要明确说明理由。

这次任务准备收口。请你先读：
1. 当前 active boundary
2. 相关真源 spec
3. 这次实现改动
4. 如果做 QA，再补读 .gstack/knowledge/qa-dimensions.md

然后请你判断这次更适合补 review 还是 QA：
- 如果重点是结构、风险、边界、回归隐患，请补 .gstack/reviews/
- 如果重点是验收、测试结果、页面 / 接口验证，请补 .gstack/qa-reports/

请直接落一份正式文档，并写清楚：
1. 检查了什么
2. 发现了什么风险
3. 当前是否可判定完成
4. 后续还需补什么

不要只在聊天里说“看起来没问题”。
```

---

## 8. 有边界争议时，补 `decision`

适用时机：

- 产品和研发理解不一致
- 文档分层拿不准
- 是否允许某种折中方案有争议
- 是否改 baseline 语义拿不准

可直接复制：

```text
先读仓库入口和本任务相关真源文档，再执行。
不要把关键结论只留在聊天里，需要直接落到 repo 对应文档。
如果你判断这次不需要落这类文档，也要明确说明理由。

这个问题现在有边界 / 分层 / 取舍争议。请你先读：
1. AGENTS.md
2. .gstack/knowledge/doc-placement.md
3. 相关 baseline / stack / .gstack 文档
4. 当前任务 boundary

然后不要急着继续实现，先帮我在 .gstack/decisions/ 里写一份 decision 文档，说明：
1. 争议点是什么
2. 可选方案有哪些
3. 最终采用哪种方案
4. 为什么这样定
5. 对后续协作有什么约束

不要把这次裁定只留在聊天里。
```

---

## 9. 有长期经验时，补 `learning`、`rule`、`pitfall`

适用时机：

- 发现某类任务反复误判
- 某个模块反复踩坑
- 某种做法值得固化成规则
- 某种 QA 维度值得长期保留

可直接复制：

```text
先读仓库入口和本任务相关真源文档，再执行。
不要把关键结论只留在聊天里，需要直接落到 repo 对应文档。
如果你判断这次不需要落这类文档，也要明确说明理由。

这次任务里暴露出一些以后还会重复遇到的问题。请你先结合这次：
1. diff
2. review
3. QA
4. 实现过程

然后判断哪些经验值得沉淀，并分类写回合适的位置：
- 可复用经验 -> .gstack/learnings/
- 长期规则 -> .gstack/rules/
- 容易重复踩的坑 -> .gstack/knowledge/pitfalls/
- 可复用代码做法 -> .gstack/knowledge/code-patterns.md

请不要泛泛总结，要写成下次人和 AI 都能直接复用的内容。
如果你判断某条经验不值得沉淀，也请说明原因。
```

---

## 10. 团队使用建议

建议给团队统一说明三条：

1. 不要只说“帮我做一下”，要同时说清楚“先读什么”和“落到哪里”。
2. 只要任务进入正式协作主线，就不要让关键结论只停留在聊天里。
3. 如果 AI 判断这次不需要补某类文档，也要让它明确说出原因。
