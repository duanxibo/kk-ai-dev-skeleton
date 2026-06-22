# Online Software Factory Readiness Review

- 主题：升级 KK Dev Skeleton 支持纯线上 AI Software Factory 平台
- 日期：2026-06-22
- Reviewer：Codex
- Flow Lane：`standard`
- 关联 requirement：`.gstack/requirements/2026-06-22_online-software-factory-readiness-standard-requirement.md`
- 关联 boundary：`.gstack/task-boundaries/2026-06-22_online-software-factory-readiness.md`
- AI 语义复核：`yes`

## 结论

- 推荐结论：`pass`
- 是否允许进入实现：`是`
- 复核说明：现有 `ai-dev-skeleton` 已具备 runtime bundle、adapter installer 和 plugin adoption connector，且本地 `--verify-runtime` 已通过；本轮应增量升级现有骨架，而不是重新抽取。

## 产品判断

- 用户偏好纯线上平台体验，因此公共骨架必须清楚承接“平台在线收需求、生成 claim、runner 执行、repo evidence 回写、用户在线验收”的协议。
- 平台产品应单独立项；公共骨架只负责工程协议、adapter、runtime bundle、授权边界和 smoke，不承载平台 UI / API 实现。
- 复用现有 `ai-dev-skeleton` 能避免三套骨架分叉：上游 dogfood、旧 skeleton、新 skeleton。

## 工程判断

- 本轮不需要改 runtime runner 的核心执行逻辑；先把协议和 adapter metadata 固定下来，并用 tests 防止回归。
- 默认 adapter 应声明 `online_flow_protocol`，但不得写入项目专属业务路径、非公共 skill 前缀或真实数据工具。
- 插件接入器应强调 existing project upgrade：检测、计划、dry-run、apply-core / apply-runtime / rewrite-adapter，而不是让用户重新接入。

## Codex 自主工程决策

- 新增一份公共骨架协议文档到 `.gstack/designs/`，不直接复制上游 dogfood 文件名和业务上下文。
- 更新 `.gstack/knowledge/ai-programming-framework.md` 的分层说明，而不是把上游 dogfood 长文整篇搬入。
- 在 `adapters/default/runtime.json` 添加机器可读 `online_flow_protocol` section，保持现有路径结构不变。
- 同步 `scripts/init_project.py` 内置 default runtime / schema，确保新项目通过 installer 接入后也带有 online flow metadata。
- 增加 focused pytest，验证协议文档存在、runtime metadata 完整、公共协议没有非公共 skill 前缀和上游业务路径泄漏。

## 用户决策边界

后续仍需用户另行确认：

- 是否新建 `ai-software-factory` 平台仓库。
- 纯线上平台 MVP 具体技术栈、Runner 隔离方式和 GitHub 授权方式。
- 是否允许平台写 GitHub、创建 PR、部署 staging 或生产发布。
- 是否执行任何 git workflow、生产、DB、真实数据或外部付费动作。

## 防技术甩锅检查

- 不要求用户选择实现细节；Codex 负责公共骨架升级路径、文档落点、metadata 和 tests。
- 用户只需判断产品路线是否继续：现有骨架作为公共上游，平台另起项目。

## Spec Sync Check

- Spec Impact：`updated`
- Expected Spec Targets：
  - `.gstack/designs/2026-06-22_online-software-factory-platform-protocol.md`
  - `.gstack/knowledge/ai-programming-framework.md`
  - `adapters/default/adapter.md`
  - `adapters/default/runtime.json`
  - `scripts/init_project.py`
  - `plugins/kk-dev-skeleton-adoption/README.md`
  - `plugins/kk-dev-skeleton-adoption/skills/kk-dev-skeleton-adoption/SKILL.md`
  - `tests/test_online_flow_protocol.py`

## 验证计划

- `python3 tests/test_online_flow_protocol.py`
- `python3 scripts/init_project.py --adapter default --validate-adapter --report`
- `python3 scripts/init_project.py --adapter default --verify-runtime --report`
- `python3 .gstack/scripts/gstack_loop_contract_smoke.py --format user`
- `python3 .gstack/scripts/natural_language_dev_smoke.py --format user`
- `python3 .gstack/scripts/spec_sync_guard.py`
- `git diff --check`

## 风险与退出条件

- 如果实现中发现需要改 installer 覆盖策略、连接真实平台服务、发布插件或执行 git workflow，立即暂停并单独建任务。
- 如果协议需要上游 dogfood 业务事实才能成立，说明抽象失败，必须回到公共 core / adapter 分界重新整理。
