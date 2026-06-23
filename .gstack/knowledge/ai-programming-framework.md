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
- UI style routing and visual quality gate
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
- 纯线上 AI Software Factory 平台

### Online Flow Protocol（线上流程协议）

当 KK Dev Skeleton 被纯线上平台消费时，平台和 runner 之间使用对象协议交接，而不是让平台直接替代仓库真源。

核心对象：

- `OnlineDemand`：平台中的用户需求、验收方式、不做范围和风险标记。
- `MvpConfirmation`：用户确认后的最小可交付切片、延后项和验收清单。
- `ClaimPackage`：平台交给 Codex runner 的开工包，包含 repo、adapter、scope、evidence target 和授权边界。
- `StatusEvent`：runner 回写平台的阶段、阻塞、确认点、QA 和交付摘要。

核心职责：

- 平台负责用户协作、状态展示、确认队列和授权事件。
- Codex runner 负责在隔离工作区执行本地闭环。
- repo skeleton 负责 requirement、review、boundary、QA、adapter、runtime bundle 和 guard。

主协议见 `../designs/2026-06-22_online-software-factory-platform-protocol.md`。

高风险规则保持不变：Git workflow、生产、数据库、真实数据写入、破坏性动作和外部付费调用必须单独明确授权；平台 claim 不能隐式授权这些动作。

### UI Quality Gate（UI 质量门禁）

当前端、HTML、dashboard、可视化或用户可见交互进入实现前，骨架必须先做 UI style routing，而不是直接写页面。

默认能力：

- 用户只说“进行 UI 优化 / 优化界面 / 美化页面 / 页面不好看”时，骨架应通过 natural-language router 自动进入 UI 设计梳理、实现、视觉复核和浏览器验收链路；用户不需要记住技能名或门禁名。
- `kk-ui-design-kickoff`：识别页面 archetype、用户第一眼目标、信息架构、组件计划、视觉方向、状态覆盖和响应式策略。
- `kk-ui-polish-review`：实现后检查 archetype fit、信息层级、布局密度、组件匹配、状态完整、视觉一致性、响应式安全、基础可访问性和 anti-AI-slop。

AI 软件工厂、开发者平台、业务工作台和内部工具默认采用成熟 SaaS / workflow console / AI command center 方向。除非 requirement 明确要求营销官网，不要默认做大 hero、装饰渐变、卡片套卡片或低信息密度海报页。

### Explicit Runtime Bundle（显式运行包）

runtime 脚本属于可执行协作能力，不应只停留在文档里。

默认 adapter 必须声明：

- `runtime_bundle.files`：可复制到目标项目的 allowlist。
- `runtime_bundle.write_policy`：默认 `create-missing-preserve-existing`，不覆盖目标项目已有脚本。
- `runtime_bundle.apply_command`：显式安装命令，通常是 `scripts/init_project.py --apply-runtime`。
- `runtime_bundle.verify_command`：安装后验证命令，通常是 `scripts/init_project.py --verify-runtime --report`。
- `runtime_bundle.required_smoke_commands`：安装后必须能在目标项目运行的 smoke。

Codex 同步骨架能力时，应先更新 adapter metadata、schema guard 和 runtime bundle 清单，再更新插件工作流。不要把源项目业务代码、历史 archive、真实数据、私有脚本或生产连接器放进 runtime bundle。

线上平台接入时，runtime bundle 仍是显式安装能力，不是后台常驻服务。平台可以触发 runner，但 runner 必须先校验 adapter、claim revision、checksum、active boundary 和授权状态。

### Loop Runtime Contract（Loop 运行契约）

Loop runtime 必须支持自然语言入口，而不是要求用户理解内部命令。

当前最小契约：

- chat-first protocol
- stage skill routing
- engineering review decisioner
- stage write-back closure
- subagent timeout policy
- controlled local runner
- test repair loop
- chat authorization classifier
- chat smoke / natural-language kickoff smoke / loop contract smoke

高风险授权必须保持显式：commit、branch、push、pull、merge、PR、deploy、生产操作、数据库 schema 变更、真实数据写入和破坏性命令，都不能由模糊确认自动触发。

低风险确认必须可连续推进：当 active boundary 已存在，用户只说“我确认 / 可以 / 同意 / 继续做”，且原话不包含真实数据、生产、数据库、发布、删除、回滚或 git workflow action 时，Codex 应继续本地可证明的实现、验证、文档同步、门禁恢复和 subagent 分工，不要每个内部阶段都要求用户再说一次“继续”。

subagent 策略属于 Codex 的工程调度能力：中大型任务、跨模块探索、独立 review、QA / 文档治理，或用户反馈“没看到使用 subagent”时，默认至少评估 read-only explorer / reviewer。只有单文件小改、强耦合写范围、无独立 evidence 落点或同步成本明显高于收益时，才记录 `Mode: not-used`。

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
- doctor 必须区分骨架源仓库和安装后的目标仓库：
  - 骨架源仓库检查完整发放清单，包括 partner、plugin、marketplace、setup 和历史归档入口。
  - 目标仓库只检查 portable core、adapter metadata 和 runtime essentials，不要求随业务项目复制骨架源仓库发布资料。

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
- 低风险确认后可以连续推进，不需要用户反复说“继续”
- 暂停、继续和撤销请求可控
- 范围变化不会导致整个任务重来
- 非技术用户得到推荐方案，而不是被迫选择技术路线
- 工程顺序、测试组合、门禁恢复和 subagent 策略由 Codex 决策并记录
- dashboard 从 evidence 生成，而不是提交共享状态文件
- UI 任务必须交互验证
- CI 失败用普通语言解释
- delivery summary 可从 evidence 生成，且必须包含下一步建议
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
- online flow protocol 支持状态

框架核心可以读取这份 contract，但不应写死 adapter 内容。

## Installer Contract（安装器契约）

`scripts/init_project.py` 是 Codex 面向目标项目的确定性 helper。

当前能力应覆盖：

- `--detect` / `--plan`：只读识别当前 adapter、portable core 和 runtime bundle 状态。
- `--apply`：只创建缺失的 adapter metadata。
- `--apply-core`：只创建缺失的 portable collaboration core。
- `--apply-runtime`：显式复制 allowlisted runtime scripts，默认保留目标已有文件。
- `--rewrite-adapter`：根据目标项目结构改写 adapter metadata，不迁移业务代码。
- `--validate-adapter`：校验 adapter markdown、runtime schema、Loop contract 和 runtime bundle metadata。
- `--verify --verify-core --verify-runtime --report`：输出可留档的验证证据。
- `--pilot` / `--pilot-output`：在隔离目录跑接入试点。

已接入项目升级时，不再使用旧的 `--upgrade-plan` 或 `--upgrade-apply` 口径。Codex 应先运行 detect/plan，再用 `--apply-core --dry-run`、`--apply-runtime --dry-run`、`--rewrite-adapter --dry-run` 形成增量计划，最后在 boundary 和用户授权范围内执行安全的 create-missing 或 metadata rewrite。
