# QA 报告：context-isolation-hardening

- 主题: context-isolation-hardening
- 负责人: Codex
- 日期: 2026-06-09
- 环境: local
- 范围: 上下文隔离规则、doctor、skill 同步脚本
- 相关 requirement / review / boundary:
  - `.gstack/requirements/2026-06-09_context-isolation-hardening.md`
  - `.gstack/reviews/2026-06-09_context-isolation-hardening-review.md`
  - `.gstack/task-boundaries/2026-06-09_context-isolation-hardening.md`

## 目标

- 证明骨架不会鼓励 agent 从父目录路径或全局 skills 推断项目名。
- 证明 doctor 能提示外部 `tg-*` skill symlink 和可疑父路径。
- 证明 sync 脚本默认安全，只在显式参数下清理 `tg-*` symlink。

## 测试覆盖

- AGENTS / README 上下文隔离说明。
- `.gstack/knowledge/context-isolation.md`。
- doctor context isolation check。
- sync 脚本 `--remove-tg-links` 选项。
- JSON 输出可解析。
- smoke / guard。

## 测试方式

- 静态扫描。
- CLI 验证。

## 用户可见 UI / HTML / 可视化验收

- 是否属于用户可见 UI / HTML / 可视化任务:
  `否`
- Generated Artifact Policy:
  `CLI-output / docs-only`
- Browser / Chrome / Playwright 是否实际打开:
  `不适用`

## Spec Sync Check

- Spec Impact:
  `not-required`
- Updated Spec Files:
  - `.gstack/knowledge/context-isolation.md`
- If Not Required, Why:
  本次不改变业务逻辑、接口、数据模型或持久化；只加固公开骨架协作层。

## 发现

- 通过项:
  - `AGENTS.md` 已加入上下文隔离规则，明确项目身份只能来自用户输入、当前仓库、active adapter 和 active boundary。
  - `README.md` 已加入“使用后感觉串味”排查步骤。
  - `.gstack/knowledge/context-isolation.md` 已新增。
  - `gstack_doctor.py check` 已新增 `context-isolation` 检查，能提示父目录旧项目命名片段和外部 `tg-*` symlink。
  - `sync_repo_skills.sh` 已支持 `--remove-tg-links`，默认不删除旧 symlink。
  - 已运行默认 skill 同步，`kk-*` symlink 已接入本机 Codex。
- 非阻塞问题:
  - 本机仍存在 `tg-*` symlink；doctor 会提示风险。是否清理取决于用户是否仍需要旧项目 skills。
  - 当前骨架路径仍位于包含旧项目名的父目录下；doctor 会提示不能据此推断项目身份。

## 证据

- `bash -n .gstack/scripts/sync_repo_skills.sh`
  - 通过，无输出。
- `bash .gstack/scripts/sync_repo_skills.sh --help`
  - 输出中文帮助，说明默认同步 `kk-*`，不删除其它项目 `tg-*` skills。
- `bash .gstack/scripts/sync_repo_skills.sh`
  - 已同步 9 个 `kk-*` skills。
  - 输出 warning：发现 `tg-*` skills，可能让新 Codex 会话串到旧项目上下文。
- `python3 -m py_compile .gstack/scripts/gstack_doctor.py`
  - 通过，无输出。
- `python3 .gstack/scripts/gstack_doctor.py check`
  - `skills`: 通过，repo-native skills 已同步。
  - `context-isolation`: 提醒，检测到父目录旧项目命名片段和外部 `tg-*` skill symlink。
- `python3 .gstack/scripts/gstack_doctor.py check --format json | python3 -m json.tool`
  - 通过，JSON 可解析。
- `python3 .gstack/scripts/gstack_doctor.py explain`
  - 中文解释中包含“上下文隔离：有串味风险；Codex 必须只按当前仓库、adapter、boundary 和用户输入判断项目身份。”
- `python3 .gstack/scripts/gstack_dashboard.py show --limit 5`
  - 当前任务 `context-isolation-hardening` 显示 `7/7`、全部完成、正常。
- `python3 .gstack/scripts/spec_sync_guard.py`
  - `PASS: static skeleton guard passed.`
- `python3 .gstack/scripts/natural_language_dev_smoke.py --format user`
  - `非技术开发关键路径检查通过。`

## 残余风险

- 如果用户继续在包含旧项目名的父目录中运行，模型仍可能看到绝对路径；AGENTS 和 doctor 已明确禁止从路径推断项目身份。
- 如果用户保留 `tg-*` symlink，某些会话的可用 skills 列表仍会显示旧 skills；doctor 会提示，AGENTS 明确要求忽略这些外部 skill。
