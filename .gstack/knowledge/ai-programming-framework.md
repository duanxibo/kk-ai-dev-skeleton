# AI 编程框架

KK Dev Skeleton 把可复用 AI 开发能力和项目专属规则分开。

## 分层

### Framework Core（框架核心）

应该能在任何项目中复用的行为：

- 自然语言首页和下一步路由
- 需求收集
- 首次使用引导
- 需求完整度检查
- 任务开工
- 协作模式
- flow lanes
- task boundaries
- required gates
- evidence registry
- dashboard
- doctor
- QA evidence
- delivery summary
- guard checks
- knowledge feedback

### Project Adapter（项目适配器）

每个项目不同的规则：

- 项目目标
- 技术栈
- 应用源码路径
- 真源文档
- 测试、构建和启动命令
- 数据和 API 策略
- 授权和部署策略
- forbidden paths
- 项目专属 gates

### Runtime / Product Surface（运行与产品化表面）

可选的产品化表面：

- 自然语言 command center
- task dashboard
- preview server
- QA 截图和录屏证据
- PR 和发布授权 UI
- adapter installer

## 能力保真

不要用被动文档替代可执行行为，从而削弱框架能力。

只有保留或提升以下能力，才算能力保真：

- 自然语言用户旅程
- 确定性 helper scripts
- task boundary 创建
- required gates
- QA evidence 质量
- dashboard 生成行为
- doctor 诊断
- smoke 覆盖
- knowledge feedback

## 断链保真

能力保真还包括引用完整性：

- skill Required Reading 指向的文件必须存在。
- template 中要求复制或补读的文件必须存在。
- workflow 中写死的路径如果属于项目专属内容，必须迁入 adapter 或明确标记为 example。
- doctor 应尽量检查核心入口、skills、scripts 和 active boundary 是否可用。

如果为了抽离而删除某份 源项目 文档，必须判断它属于哪类：

- 业务真源：删除或迁到 example。
- 私有历史证据：删除。
- 可复用协作规则：泛化后保留。
- 仍被 skill / template / workflow 引用：补通用版或修引用。

## 好骨架检查清单

- 首次使用路径清晰
- 支持自然语言任务收集
- 用户可以问下一步做什么
- 用户可以问现在能不能开始实现
- 用户可以问当前需要确认什么
- 模糊确认不会被当成高风险授权
- 暂停、继续和撤销请求可控
- 范围变化不会导致整个任务重来
- 非技术用户得到推荐方案，而不是被迫选择技术路线
- dashboard 从 evidence 生成，而不是提交共享状态文件
- UI 任务必须交互验证
- CI 失败用普通语言解释
- delivery summary 可从 evidence 生成
- 新经验会回写到仓库

## Adapter Contract（适配器契约）

每个真实项目都应提供 adapter，并说明：

- 真源路径
- allowed implementation roots
- forbidden roots
- commands
- data rules
- release rules
- QA expectations
- glossary

框架核心可以读取这份 contract，但不应写死 adapter 内容。
