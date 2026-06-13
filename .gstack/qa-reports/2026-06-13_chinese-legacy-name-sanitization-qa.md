# chinese-legacy-name-sanitization QA

- 日期: 2026-06-13
- 负责人: Codex
- 关联 boundary: `.gstack/task-boundaries/2026-06-13_chinese-legacy-name-sanitization.md`
- 关联 requirement: `.gstack/requirements/2026-06-13_chinese-legacy-name-sanitization-fast-lane-requirement.md`

## Scope

- 清理历史 requirement 中的中文旧项目名残留。
- 将中文旧项目名加入公开分发敏感 token 扫描。
- 避免测试文件自身写入该敏感字面量。

## Evidence

- 历史 requirement 已改为通用“旧项目名”表述。
- `tests/test_productization_hardening.py` 已通过字符串拼接构造中文旧项目名 token，并纳入全 tracked tree 扫描。
- 敏感 token 扫描覆盖旧项目英文命名、路径形态、本机绝对路径标记、示例旧应用 slug 和中文旧项目名，未发现 tracked 内容残留。

## Verification

- `python3 -m unittest tests/test_productization_hardening.py -v`: passed, 10 tests.
- `python3 -m unittest discover -s tests -v`: passed, 42 tests.
- `python3 .gstack/scripts/gstack_doctor.py check`: passed, overall ok.
- `python3 .gstack/scripts/spec_sync_guard.py`: passed.
- `python3 .gstack/scripts/team_flow_guard.py --mode audit --base HEAD`: passed.
- `python3 .gstack/scripts/required_gates_audit.py --boundary .gstack/task-boundaries/2026-06-13_chinese-legacy-name-sanitization.md`: passed.
- `python3 .gstack/scripts/runtime_artifact_guard.py`: passed.
- `git diff --check`: passed.
- sensitive-token scan: passed, no tracked content matches.

## UI / Browser QA

- Not required.
- 本次只影响公开骨架文本和分发测试，不改变 Web UI、HTML、dashboard 或交互产物。

## Residual Risk

- 后续如果引入新的旧项目别名，需要继续加入同一公开分发扫描。
