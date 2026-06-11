# AI 开工标准提示词模板

适用场景：

- 团队成员准备让 AI 开始一个新任务
- 希望 AI 先读对文档，再开始实现或产出文档
- 希望 AI 不把关键结论只留在聊天里

使用原则：

- 小任务可用精简版
- 正式实现、跨层任务、需求不清任务，优先用完整版
- 如果任务涉及 `archive/baseline/` 旧原型证据、`stack/`、`.gstack/` 跨层协作，不要省略“先读文档”和“需要落文档”的要求
- 如果用户只是直接描述一个新任务、bug 或正式实现需求，即便没有显式写“任务开工”，也应默认先按本模板建立上下文

---

## 一、最短版

适合：

- 小范围修改
- 已知目标明确
- 主要是想提醒 AI 不要跳过入口文档

可直接复制：

```text
先按仓库入口顺序读文档，再开始这次任务。

至少先读：
1. AGENTS.md
2. .gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md
3. .gstack/README.md
4. .gstack/knowledge/CODEMAP.md
5. .gstack/knowledge/doc-placement.md
6. .gstack/task-boundaries/CURRENT.md

然后再补读与本任务直接相关的 spec、knowledge、pitfalls。

不要一上来全仓搜索，也不要把 archive 误当当前真源。
如果这次任务涉及正式实现或长期协作产物，请同步判断是否需要更新 boundary、spec、review、QA、decision、learning。
不要把关键结论只留在聊天里，需要落到 repo 对应文档。
```

---

## 二、标准完整版

适合：

- 新需求
- 正式工程实现
- Bug 修复但可能影响边界
- 涉及多人协作和后续上下文延续

可直接复制：

```text
你先不要直接开始写代码或下结论，先按 KK Dev Skeleton 仓库约定建立上下文。

先读这些文档：
1. AGENTS.md
2. .gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md
3. .gstack/README.md
4. .gstack/knowledge/CODEMAP.md
5. .gstack/knowledge/doc-placement.md
6. 对应角色入口文档
7. .gstack/task-boundaries/CURRENT.md

然后根据任务类型补读：
- 如果涉及产品语义、需求冻结、页面行为：补读 `docs/specs/<module>/` 相关真源；需要追溯旧行为时再读 baseline
- 如果涉及正式实现：补读 .gstack/knowledge/implementation-guide.md、相关 specs、相关 pitfalls、相关 code patterns
- 如果涉及后端、持久化、接口、状态：补读 data-model.md、state-management.md、api-contracts
- 如果涉及前端承接：补读 ui-patterns.md
- 如果涉及 QA / 验收：补读 qa-dimensions.md

读完后先用你自己的话总结：
1. 这次任务属于哪个 stack domain，或是否只是 `.gstack` / `archive` / 历史 baseline 治理
2. 当前真源文档主要是哪些
3. 当前 active boundary 是什么
4. 这次可能需要落哪些文档

然后再开始执行。

执行过程中请遵守这些要求：
- 不要把 archive 当当前实现真源
- 不要在没有 domain spec evidence 的情况下直接改产品语义
- 不要只改代码，不检查 spec 和协作文档是否需要同步
- 不要把关键结论只留在聊天里

如果本次任务进入正式实现或协作主线，请主动判断并在需要时落这些文档：
- .gstack/requirements/ requirement brief
- .gstack/requirements/ requirement freeze 或 prototype freeze
- task boundary
- task boundary 中的 `Required Gates`；由 `kk-task-kickoff` 判断是否需要 `data-access`、`data-query`、`prototype-logic-extraction`、`doc-backfill` 等专项门禁
- 如果后端接口、读模型、service 或 snapshot 承接已有前端 / 原型 / mock 业务逻辑，`prototype-logic-extraction` 必须写 `owner: kk-task-kickoff`、`required_before: plan-eng-review`，并在工程评审前补齐 evidence 或写清 blocked / deferred 原因
- task boundary 中的 Subagent Plan；不使用 subagent 也要写 `Mode: not-used`
- stack domain spec readiness
- stack/specs 真源更新；如引用 baseline，只把它作为来源证据写进 domain spec / requirement / review / boundary
- review
- QA
- decision
- learning / rule / pitfall

如果你判断这次不需要更新某类文档，也请明确说出原因，不要默认跳过。
```

---

## 三、研发任务版

适合：

- 工程同学让 AI 帮忙做正式实现、重构、修 bug、补测试

可直接复制：

```text
这是一个研发任务。先不要直接改代码，先读文档并确认边界。

至少先读：
1. AGENTS.md
2. .gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md
3. .gstack/README.md
4. .gstack/knowledge/CODEMAP.md
5. .gstack/knowledge/doc-placement.md
6. .gstack/entrypoints/engineer.md
7. .gstack/task-boundaries/CURRENT.md
8. .gstack/knowledge/implementation-guide.md

再补读与改动路径直接相关的：
- stack specs
- pitfalls
- code patterns
- 如果涉及后端：data-model、state-management、api-contracts
- 如果涉及前端：ui-patterns
- 如果后端接口 / 读模型 / service 承接已有前端或原型逻辑：prototype-logic-extraction，先抽取页面内部业务逻辑，再进入接口或读模型设计

读完后先告诉我：
1. 这次改动的主 domain 是什么
2. 当前应该信哪些真源文档
3. 当前 boundary 是否足够
4. 这次是否适合使用 subagent；如果不适合，也要说明原因
5. 这次预期会不会影响 spec、review、QA 或 learning

然后再开始实现。

实现时请特别注意：
- 不要跨 domain 顺手改语义
- 不要把业务真相塞回前端
- 不要跳过 `prototype-logic-extraction`：金额、计划、利润、转化率、状态流转、scope 隔离等业务计算默认由后端承接；前端只保留薄渲染职责
- 如果实现代码变了，请同步检查是否需要更新 spec
- 如果任务复杂到适合并行探索、独立评审、分范围执行或文档治理，请先用 `kk-subagent-orchestrator` 规划
- 如果任务进入正式交付，请不要把关键结论只留在聊天里，要落到 repo 文档
```

---

## 四、产品任务版

适合：

- 产品同学让 AI 帮忙梳理需求，并直接沉淀到 stack domain spec

可直接复制：

```text
这是一个产品 / stack domain spec 任务。先不要直接给方案结论，先读文档建立上下文。

至少先读：
1. AGENTS.md
2. .gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md
3. .gstack/README.md
4. .gstack/knowledge/CODEMAP.md
5. .gstack/knowledge/doc-placement.md
6. .gstack/entrypoints/product-manager.md
7. docs/specs/<module>/ 相关真源
8. 如需追溯旧行为，再读 archive/baseline/README.md 和相关旧原型

读完后先告诉我：
1. 这次任务主要落在哪个 stack domain
2. 当前产品 + 工程真源主要是哪些文档
3. 还缺哪些需求、字段、接口、前端、后端或测试信息
4. 这次是否需要补 requirement brief、requirement freeze、domain spec readiness 或 decision

然后再开始整理需求。

请特别注意：
- 新任务直接在 stack domain spec 定义产品语义
- 不要新增 handoff 文档
- 不要让关键需求结论只停留在聊天里
- 需求描述先落 `.gstack/requirements/`，再进入 `plan-ceo-review`
- 一旦需求已经进入协作主线，请把结果落到 stack domain spec 或 .gstack 对应过程文档
```

---

## 五、Bug 修复版

适合：

- 团队成员希望 AI 先查根因，不要看到现象就直接改

可直接复制：

```text
这是一个 bug 修复任务。先不要直接写修复方案，先读文档并确认边界和真源。

至少先读：
1. AGENTS.md
2. .gstack/KK-Dev-Skeleton-gstack工程化协作蓝图.md
3. .gstack/knowledge/CODEMAP.md
4. .gstack/task-boundaries/CURRENT.md
5. 与该路径相关的 specs
6. 与该路径相关的 pitfalls

如果涉及后端 / 状态 / 接口，再补读：
- data-model.md
- state-management.md
- api-contracts

读完后先输出：
1. 你判断的根因范围
2. 当前不该碰的边界
3. 这次修复会不会影响 domain spec 或 QA
4. 修完后需要补哪些文档

然后再开始修。

请特别注意：
- 不要只看页面现象就下结论
- 不要修一个点却破坏其他 scope
- 不要只改代码，不补必要的 review / QA / learning
```

---

## 六、什么时候必须显式提醒 AI

下面这些场景，不要假设 AI 会完全自动化处理，建议显式加上“先读文档”和“需要落文档”的要求：

- 新任务刚开始
- 任务跨 `archive/baseline/`、`stack/`、`.gstack/`
- 需要正式实现
- 需要更新行为、接口、数据模型、测试口径
- 任务会影响他人协作
- 需要把结论沉淀成长期资产
- 需要让下一个人或下一个会话接得上上下文

## 七、什么时候可以只用最短版

- 单文件小修
- 明确不改行为语义
- 不涉及跨层
- 不涉及长期文档
- 不涉及多人协作上下文延续

即便如此，也建议至少提醒 AI：

- 先读 `CODEMAP`
- 看 `CURRENT.md` 说明页
- 不要把关键结论只留在聊天里
