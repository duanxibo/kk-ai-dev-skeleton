# Archive

`archive/` 是历史归档层。

它只用于保存已经退出当前真源链路、但仍有追溯价值的材料，例如旧原型、旧实现、旧规格、废弃方案、兼容说明或历史迁移快照。

## 默认规则

- `archive/` 不是当前实现入口。
- 新功能默认不要从 `archive/` 直接实现。
- 如果需要复用历史材料，必须在 requirement、review、task boundary 或当前 stack spec 中说明采纳项、放弃项和替代真源。
- 历史材料进入正式实现前，必须同步到 `stack/<project>/specs/`、adapter 或 `.gstack/` 的当前真源位置。
- 不要把真实客户数据、密钥、生产导出、未脱敏 Excel / CSV / SQL evidence 放进公共骨架。

## 推荐子目录

- `archive/baseline/`
  历史原型、旧 demo、旧页面行为和 baseline snapshot。
- `archive/legacy/`
  已废弃但需要追溯的旧实现或旧文档。

真实项目可以按 adapter 规则扩展子目录，但必须保持“只读追溯，不做默认实现来源”的原则。
