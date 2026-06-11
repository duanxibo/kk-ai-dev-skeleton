# kk-doc-sync 模板映射

这个 skill 对应的 prompt 真源是：

- `.gstack/templates/ai-doc-sync-prompts.template.md`

场景映射：

- 需求已确认，需补产品真源：
  使用“补 stack domain spec”
- 正式实现前需要确认统一真源：
  使用“补 domain spec readiness”
- 正式实现前，需先补 boundary：
  这类场景应回退到 `kk-task-kickoff`
- 行为或契约变化：
  使用“更新 stack domain 真源”
- 完成前需要收口：
  使用“补 review 或 QA”
- 有边界争议：
  使用“补 decision”
- 有长期经验：
  使用“补 learning / rule / pitfall”

skill 的职责不是原样复制模板，而是根据当前任务自动选择最合适的文档落点。
