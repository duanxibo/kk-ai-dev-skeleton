# 角色入口

本目录提供通用角色入口。它们不定义具体业务规则，只告诉 agent 在不同任务类型下应该先读什么、产出什么、何时停止确认。

- `product-manager.md`
  用于需求澄清、范围拆解、验收标准和非技术用户沟通。
- `engineer.md`
  用于实现、bugfix、refactor、测试和工程交付。

项目专属规则仍由 `adapters/<project>/adapter.md` 提供。
