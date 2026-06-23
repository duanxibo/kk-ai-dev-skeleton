# Delivery summary next-step QA

- 任务：交付总结下一步建议强制输出
- 日期：2026-06-23
- 结论：`pass`
- 关联 requirement：`.gstack/requirements/2026-06-23_delivery-summary-next-step-requirement.md`
- 关联 review：`.gstack/reviews/2026-06-23_delivery-summary-next-step-review.md`
- 关联 boundary：`.gstack/task-boundaries/2026-06-23_delivery-summary-next-step.md`

## 验收重点

- 交付总结 JSON 输出必须包含 `next_step_suggestions`。
- 用户输出必须固定包含 `下一步建议`。
- intent router 的交付总结说明必须包含 `下一步建议`。
- next-step 路由到交付总结时，也必须保留 `下一步建议`。
- smoke 测试必须覆盖 JSON 字段和 user 输出片段。
- 本次不得改变 API、数据合同、runner 逻辑、真实服务接入或代码提交流程。

## 验证结果

- `python3 -m py_compile .gstack/scripts/nontechnical_delivery_summary.py .gstack/scripts/nontechnical_intent_router.py .gstack/scripts/natural_language_dev_smoke.py`：通过。
- `python3 .gstack/scripts/nontechnical_delivery_summary.py --raw "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险" --format json`：通过，输出包含 `next_step_suggestions`。
- `python3 .gstack/scripts/nontechnical_delivery_summary.py --raw "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险" --format user`：通过，输出包含 `下一步建议`。
- `python3 .gstack/scripts/nontechnical_next_step.py --raw "帮我写一段给团队看的完成说明，说明这次改了什么、怎么验收、还有什么风险" --format user`：通过，输出包含 `下一步建议`。
- `python3 .gstack/scripts/natural_language_dev_smoke.py --format user`：通过，覆盖“交付总结、验收方式、风险、未做事项和下一步建议”。
- `python3 -m unittest discover -s tests`：通过，48 个测试通过。
- `python3 scripts/init_project.py --adapter default --validate-adapter --report`：通过。
- `python3 scripts/init_project.py --adapter default --verify-runtime --report`：通过，runtime bundle present count 为 41，runtime 编译、loop contract smoke、chat-smoke、nl-smoke 和 natural-language smoke 均通过。
- `python3 .gstack/scripts/spec_sync_guard.py`：通过。
- `python3 .gstack/scripts/gstack_doctor.py check`：通过但总体为 `warn`；仅提示本机存在外部项目 skill symlink 和父目录命名线索，不影响本次公开骨架改动。
- `git diff --check`：通过。

## 残余说明

- Browser / Chrome / Playwright / local HTTP server：不适用。
- 原因：本次是 helper / skill / runtime 能力增强，不涉及 app page、HTML artifact、本地 HTTP server、dashboard 或浏览器渲染 UI。
