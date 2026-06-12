# Baseline Archive

`archive/baseline/` 用于保存历史原型、旧 demo、旧页面行为、旧 mock、旧 fixture 或已冻结的 baseline snapshot。

## 使用场景

- 需要从旧原型追溯交互或字段语义。
- 需要对照历史输出做 golden parity。
- 需要维护一个已经明确不再作为当前真源的 demo。
- 需要把旧 baseline 的采纳 / 放弃结论同步到当前 stack spec。

## 约束

- 不要把 baseline 当作当前产品或工程真源。
- 不要把新需求写回 baseline。
- 不要新增 handoff 作为默认门禁；采纳结论应写入当前 requirement、review、boundary 或 `stack/<project>/specs/`。
- 如果后端接口、读模型、service 或 snapshot 承接 baseline / 原型逻辑，必须声明 `prototype-logic-extraction` gate。

## 占位

公共骨架不提供真实 baseline 内容。真实项目如需保留旧原型，应放入自己的脱敏或授权材料。
