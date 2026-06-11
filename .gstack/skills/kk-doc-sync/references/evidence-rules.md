# kk-doc-sync 证据门禁

以下文档允许默认自动落：

- `.gstack/reviews/`
- `.gstack/decisions/`
- `.gstack/learnings/`
- `.gstack/knowledge/` 下的路由与原则文档
- `README`、`stack/specs/`、`archive/baseline/` 历史引用的说明性同步

以下文档必须先有证据再落：

- `.gstack/qa-reports/`
  需要真实执行过的验证命令、页面检查、接口验证或回归步骤

以下内容禁止编造：

- “已通过 QA”
- “验收完成”
- “验证无异常”
- 任何用户、测试、浏览器或脚本未实际执行过的结果

如果证据不足，应该：

1. 明确说明当前只能补 review / decision / learning，不能补 QA 通过结论
2. 列出缺哪些验证动作
3. 在需要时先落待验证的 review 或 decision，而不是空写 QA
