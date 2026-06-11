---
name: kk-natural-language-dev
description: |
  KK Dev Skeleton 自然语言开发入口。Use when a nontechnical user describes a desired change in plain language,
  asks Codex to hide commands / boundary / gates / specs / QA details, or wants to develop through natural conversation.
  This skill wraps kk-task-kickoff and the repo-native evidence flow while keeping the user-facing conversation in business language.
---

# Natural Language Development

## Purpose

This skill is the user-facing surface for nontechnical development.

The user should not need to run commands or say words like `boundary`, `gate`, `spec`, `QA`, `Flow Lane`, or `Required Gates`.
Codex still maintains those repo-native artifacts internally.

## When To Use

Use this skill when:

- The user describes a feature, bug, workflow, page, or product outcome in natural language.
- The user asks to make development feel invisible or low-friction.
- The user is deciding what feature can validate the AI programming framework.
- The task is not a pure code-review, git, data-query, document-only, or production operation request.

If the user explicitly asks for engineering details, commands, review findings, or architecture analysis, answer at that level. Otherwise keep the user-facing conversation nontechnical.

## Core Rule

Separate the conversation into two layers:

- User-facing layer:
  plain-language understanding, scope, risk, progress, result, and what needs user judgment.
- Internal layer:
  `kk-task-kickoff`, requirement, review, task boundary, Required Gates, Spec Sync Plan, QA evidence, doctor, dashboard, and guards.

Never ask the user to execute repo commands. Run the required commands yourself and summarize the result in plain language.

Natural-language usability requests default to user-visible behavior.

- When the user says "make it easier to use", "filter", "sort", "search", "action entry", "I cannot see a page change", or equivalent Chinese wording, interpret it first as an expected page-visible capability.
- Before implementation, distinguish whether the work is a generated command, CLI parameter, backend API, in-page interaction control, user-visible UI change, static artifact, or documentation-only change.
- If the implementation will only change a CLI/generator parameter, backend endpoint, or static output and will not change what the user sees on a page, say that plainly in the user-facing layer and record the explanation in the requirement.
- Do not treat "the command can generate it" as sufficient when the user's success criterion is "I can operate it on the page".

Progress, ambiguity, and team-state requests have special handling.

- For most nontechnical utterances, Codex should first run `python3 .gstack/scripts/nontechnical_next_step.py --raw "..." --format user` internally and use that as the draft user-facing reply.
  - This helper routes the utterance, runs the matching local helper, and sanitizes internal details.
  - Use its JSON format only for engineering inspection.
  - If the user asks to open the development home after opening the project, such as "打开开发首页", "现在能做什么", "我刚打开项目", "打开项目怎么开始", or equivalent wording, this helper may route to `nontechnical_home.py` and explain the current task, available actions, complex-request template, acceptance path, and recovery path in plain language.
  - If the user asks whether the current task can start implementation, such as "现在能开始实现了吗", "还差什么才能开始开发", "可以开始写代码了吗", or equivalent wording, this helper may route to `nontechnical_implementation_readiness.py` and explain completed preparation, missing preparation, Codex's next step, and whether user confirmation is needed.
  - If the user asks what they need to confirm right now, such as "现在需要我确认什么", "我该回复什么", "卡在我这里吗", or equivalent wording, this helper may route to `nontechnical_confirmation_brief.py` and explain whether Codex is waiting for the user, what needs confirmation, suggested replies, and Codex's next step.
  - If the user only replies "我确认", "可以", "同意", "按这个做", or equivalent terse confirmation, this helper may route to `nontechnical_confirmation_response.py` and explain what this confirms, what still needs explicit scope, safe next actions, suggested replies, and high-risk non-actions.
  - If the user asks "怎么推进", "你会怎么做", "执行计划", "拆任务", "排优先级", "里程碑", "每个阶段怎么验收", "什么时候需要我确认", or equivalent wording, this helper may route to `nontechnical_execution_plan.py` and explain phases, confirmation points, and acceptance in plain language.
  - If the user asks how to accept or verify a specific desired change, such as "我想做 X，怎么验收" or "X 的验收标准是什么", this helper may route to `nontechnical_acceptance_plan.py` and explain acceptance checks, user actions, expected results, confirmation points, and risks in plain language.
  - If the user asks a generic completion question such as "做完以后我怎么知道它真的好了" without a concrete new requirement, keep it as current active-task verification through `gstack_dashboard.py verify`.
  - If the user says the page did not change after refresh, such as "我刷新了页面但没看到变化", "页面还是旧的", or "没看到改动", this helper may route to `nontechnical_visible_change.py` and explain where to look, how to refresh or regenerate, why old content may still appear, and what Codex will check next.
  - If the user asks what information to provide for changing an existing page, such as "我想改一个已有页面，但是不知道该先给你什么信息", "改页面要怎么描述", or "需要我提供什么页面信息", this helper may route to `nontechnical_page_change_brief.py` and provide a fill-in brief: page location, current problem, desired change, acceptance method, and do-not-touch scope.
  - If the user asks for a general requirement template or pre-kickoff information checklist, such as "给我一个需求模板", "开工前我需要给你哪些信息", "我有个复杂需求但不知道怎么描述给你", or equivalent wording, this helper may route to `nontechnical_requirement_brief.py` and provide a fill-in brief: user, goal, current pain, first visible success, user operation, data source, do-not-touch scope, risk / permission, and acceptance method.
  - If the user asks whether a filled requirement is complete, such as "我按模板填了一版，你帮我看看还缺什么", "这些信息够不够开工", "需求是否完整", "我这样描述可以开始做了吗", or equivalent wording, this helper may route to `nontechnical_requirement_readiness.py` and explain what is clear, what is still missing, whether risk confirmation is needed, and what Codex can do next.
  - If the user asks how to start as a first-time nontechnical user, such as "我第一次用这个项目，不懂技术，应该怎么开始", "这个骨架怎么用来开发一个复杂需求", "我完全不会写代码，能不能带我从想法开始", or equivalent wording, this helper may route to `nontechnical_first_use.py` and explain the from-idea-to-kickoff path, what to send now, Codex's next actions, confirmation needs, and non-actions.
  - If Codex needs one deterministic entry to guide a complex request from blank template to readiness, execution plan, or read-only formal kickoff preview, use `python3 .gstack/scripts/nontechnical_guided_kickoff.py --raw "..." --format user` internally. This helper composes requirement readiness, execution plan, and formal kickoff preview; it remains read-only and treats explicit "do not touch production/database/real data" non-goals as safety constraints.
  - If the user says a GitHub / CI / PR check failed, such as "GitHub 检查失败了", "CI 没过", or "PR 检查挂了", this helper may route to `nontechnical_ci_failure.py` and explain the failed check type, Codex's next investigation area, whether the user needs to provide the failed check name or first log lines, and which risky actions Codex will not take.
  - If the user says "继续做", "按你刚才的计划继续推进", "那就先做第一步", or equivalent wording, this helper may route to `nontechnical_continue.py` and explain the current task, current stage, Codex's next step, whether confirmation is needed, and which risky actions Codex will not take.
  - If the user says "先停一下", "暂停这个任务", "不要继续做了", "先到这里", or equivalent wording, this helper may route to `nontechnical_pause.py` and explain the current task, pause understanding, stopped actions, preserved context, resume options, and high-risk non-actions.
  - If the user says "撤销刚才的改动", "不要这个改动了", "回到之前", "回滚刚才那步", or equivalent wording, this helper may route to `nontechnical_undo_request.py` and explain the current task, undo understanding, required undo scope, safe inspection actions, suggested replies, and high-risk non-actions.
  - If the user says "先别改代码", "只给方案", "关键地方问我", "全自动做完", "协作模式怎么选", or equivalent wording, this helper may route to `nontechnical_mode_control.py` and explain the collaboration mode, how this request will be handled, what needs confirmation, and which risky actions Codex will not take.
  - If the user says "我不懂技术", "你帮我选一个最合适的方案", "不要让我选技术方案", "你替我决定第一步", "页面、接数据还是导出先做哪个", or equivalent wording, this helper may route to `nontechnical_recommendation.py` and explain the recommended option, tradeoffs, and first safe step in plain language.
  - If the user says "先不要做导出", "只保留搜索和筛选", "不接真实数据先做可点击页面", "先给我一个能点的 demo，数据用假的", "先做静态页面看看效果，不接接口", "数据先用假的", "后面再接真实数据", "受限业务模块可以动但不要动数据库", or equivalent wording, this helper may route to `nontechnical_scope_change.py` and explain the included, excluded, and deferred scope in plain language.
  - If the user asks to list unfinished tasks, historical requirements, task lists, or equivalent wording such as "列一下未完成任务", "看看历史需求和未完成任务", or "给我任务清单", this helper may route to `nontechnical_task_list.py` and explain a read-only task overview in plain language.
  - If the user asks for team task-state sync, multi-person status, owner filtering, or equivalent wording, especially with "不要引入数据库", this helper may route to `nontechnical_team_sync.py` and explain the no-database capability boundary and repo evidence readonly view route.
  - If the user asks for a team-facing completion note, delivery summary, "这次改了什么", "怎么验收", and "还有什么风险", this helper may route to `nontechnical_delivery_summary.py` and generate a shareable summary from current task evidence.
  - If the user explicitly says "正式开工", "直接推进", "已经说清楚了", or equivalent wording, this helper may route to a formal kickoff preview. Pass `--ai-reviewed` only after Codex has semantically reviewed the request against the repo context; the helper remains read-only and must not write evidence.
  - If its reply reports a high-risk confirmation question, ask only that question before any risky action.
- Before choosing a helper for a nontechnical utterance, Codex may run `python3 .gstack/scripts/nontechnical_intent_router.py --raw "..." --format json` internally.
  - Use it to distinguish collaboration mode control, progress status, current confirmation brief, terse confirmation response explanation, pause-current-task explanation, undo / revert request explanation, task-list explanation, completion verification, request-specific acceptance planning, visible-change troubleshooting, existing-page change brief, general requirement brief, requirement readiness check, first-use guide, CI / GitHub check failure explanation, continuation, recommendation explanation, scope-change explanation, team-sync explanation, delivery summary, error recovery, natural-language smoke, execution plan, high-risk pause, formal kickoff preview, controlled starter, complex starter, and ordinary kickoff.
  - Use `--format user` or a plain-language summary for user-facing replies.
  - Never paste router commands, file paths, lane, boundary, gate, spec, or raw JSON to a nontechnical user.
- When the user asks to check whether the nontechnical development path has regressed, or uses Chinese wording such as "帮我检查非技术开发关键路径", run `python3 .gstack/scripts/natural_language_dev_smoke.py --format user` internally and summarize that output in plain language.
  - Do not paste markdown smoke check ids, command details, raw JSON, lane, boundary, gate, spec, or file paths to a nontechnical user.
  - If the user format reports failure, say which experience items need Codex repair and continue fixing locally when the fix is inside the current task boundary.
- When the user asks "where are we", "what is done", "what is blocked", or equivalent Chinese wording such as "现在做到哪一步了", first summarize the current local active task in plain language.
  - Internally prefer `gstack_doctor.py check` and `gstack_dashboard.py show --active-only`.
  - Treat `--open-only` and historical task lists as internal context only; do not present them as the current task unless the user explicitly asks for all open work.
  - Translate command output before replying. Never paste raw doctor, dashboard, active pointer, boundary path, or local filesystem output to a nontechnical user.
- When the user says "打开开发首页", "现在能做什么", "我刚打开项目", "打开项目怎么开始", or equivalent wording, do not treat it as a new feature request or a generic progress query.
  - Internally prefer `python3 .gstack/scripts/nontechnical_home.py --format user` or route through `python3 .gstack/scripts/nontechnical_next_step.py --raw "..." --format user`.
  - Explain current task, current state, Codex's next step, available actions, a complex-request fill-in template, current-result acceptance, and recovery path.
  - Keep it as a Codex-internal helper output: the user should not run commands or see paths, lane, boundary, gate, spec, raw JSON, or internal check ids.
  - If the utterance explicitly says first-time use, no-code, skeleton usage, or from-idea start, keep `nontechnical_first_use.py` as the more specific route.
- When the user says "现在能开始实现了吗", "还差什么才能开始开发", "可以开始写代码了吗", "正式开工后还差什么", or equivalent wording, do not route it to generic requirement readiness or current progress.
  - Internally prefer `python3 .gstack/scripts/nontechnical_implementation_readiness.py --format user` or route through `python3 .gstack/scripts/nontechnical_next_step.py --raw "..." --format user`.
  - Explain current task, overall readiness, completed preparation, missing preparation, Codex's next step, what needs user confirmation, and what risky actions will not be taken.
  - Keep it read-only. Do not update boundary status, advance gates, modify code, connect real data, write databases, run production actions, execute code workflow actions, or clean allowed sensitive configs.
  - Do not expose commands, paths, lane, boundary, gate, spec, raw JSON, or internal check ids to the user.
- When the user says "现在需要我确认什么", "我该回复什么", "卡在我这里吗", "哪些需要我拍板", or equivalent wording, do not route it to generic execution planning or requirement clarification.
  - Internally prefer `python3 .gstack/scripts/nontechnical_confirmation_brief.py --format user` or route through `python3 .gstack/scripts/nontechnical_next_step.py --raw "..." --format user`.
  - Explain current task, whether Codex is waiting for the user, what needs confirmation, suggested replies, Codex's next step, and high-risk non-actions.
  - Keep it read-only. Do not update boundary status, advance gates, modify code, connect real data, write databases, run production actions, execute code workflow actions, or clean allowed sensitive configs.
  - Do not expose commands, paths, lane, boundary, gate, spec, raw JSON, or internal check ids to the user.
- When the user only replies "我确认", "可以", "同意", "按这个做", "没问题", or equivalent terse confirmation, do not treat it as high-risk authorization, generic continuation, formal kickoff, collaboration mode control, or ordinary product clarification.
  - Internally prefer `python3 .gstack/scripts/nontechnical_confirmation_response.py --raw "..." --format user` or route through `python3 .gstack/scripts/nontechnical_next_step.py --raw "..." --format user`.
  - Explain current task, how Codex understands the confirmation, what it can confirm, what still needs explicit scope, safe next actions, suggested replies, and high-risk non-actions.
  - Keep it read-only. Do not update boundary status, advance gates, modify code, connect real data, write databases, run production actions, execute code workflow actions, delete, revert, reset, roll back, or clean files.
  - If the next step involves real data, production, databases, publishing, deletion, rollback, or code workflow, ask for precise scope and explicit authorization.
  - Do not expose commands, paths, lane, boundary, gate, spec, raw JSON, or internal check ids to the user.
- When the user explicitly asks to list unfinished tasks, historical requirements, open work, or task inventory, do not treat it as a new feature-intake clarification.
  - Internally prefer `python3 .gstack/scripts/nontechnical_task_list.py --raw "..." --format user`.
  - Explain that the overview reads only the current local checkout and current branch task records.
  - Show unfinished tasks, blocked tasks, and suggested next steps in plain language.
  - Do not promise real-time multi-person sync, cross-member writes, permissions, or owner filtering.
  - Do not create shared task status files, rewrite historical task records, connect real data, run production actions, write databases, execute code workflow actions, or clean allowed sensitive configs.
- When the user says the page still looks old after refresh, do not treat it as a new feature request.
  - Internally prefer `python3 .gstack/scripts/nontechnical_visible_change.py --raw "..." --format user`.
  - Explain whether the current task is actually page-visible, where the user should look, what must be refreshed or regenerated, and whether Codex needs the opened page address or screenshot.
  - If the current task is not a page / HTML / visualization change, say that refreshing a page may show no change and redirect to the correct acceptance path.
- When the user says GitHub / CI / PR checks failed, do not treat it as a generic local doctor problem.
  - Internally prefer `python3 .gstack/scripts/nontechnical_ci_failure.py --raw "..." --format user`.
  - Explain which check area is likely involved: natural-language development, runtime artifacts, backend tests, restricted-module, zm-demo, or spec sync.
  - If the failed check name or log is not locally visible, ask only for the failed check name or the first few error lines.
  - Do not answer "local collaboration state is normal" as the main conclusion for a CI failure.
  - Do not execute git workflow actions, connect to production, write databases, touch real data, or clean allowed sensitive configs.
- When the user says "继续做", "按刚才计划继续推进", "那就先做第一步", or equivalent wording, do not treat it as a fresh product-intake clarification.
  - Internally prefer `python3 .gstack/scripts/nontechnical_continue.py --raw "..." --format user`.
  - Explain the current task, current stage, Codex's next step, whether confirmation is needed, and what risky actions will not be taken.
  - If there is no active task, ask only to recover or identify the task to continue; do not invent task state.
  - Do not ask unrelated new-intake questions such as target user or first-eye success criteria when active context exists.
- When the user says "先停一下", "暂停这个任务", "不要继续做了", "先到这里", or equivalent wording, do not treat it as collaboration mode control, continuation, scope change, or a fresh product-intake clarification.
  - Internally prefer `python3 .gstack/scripts/nontechnical_pause.py --raw "..." --format user` or route through `python3 .gstack/scripts/nontechnical_next_step.py --raw "..." --format user`.
  - Explain the current task, that Codex will pause current progress, what will not continue, what remains preserved, how to resume, whether user confirmation is needed, and what risky actions will not be taken.
  - Keep it read-only. Do not write `.gstack/codex-mode.local.md`, update boundary status, advance gates, modify code, delete files, reset or roll back changes, connect real data, write databases, run production actions, execute code workflow actions, or clean allowed sensitive configs.
  - If the user explicitly asks to undo, delete, reset, revert, or roll back, treat that as a separate high-risk request and ask for precise scope and authorization before any action.
  - Do not expose commands, paths, lane, boundary, gate, spec, raw JSON, or internal check ids to the user.
- When the user says "撤销刚才的改动", "不要这个改动了", "回到之前", "恢复到改之前", "回滚刚才那步", "删掉刚才改的", or equivalent wording, do not treat it as pause, continuation, scope change, collaboration mode control, or ordinary clarification.
  - Internally prefer `python3 .gstack/scripts/nontechnical_undo_request.py --raw "..." --format user` or route through `python3 .gstack/scripts/nontechnical_next_step.py --raw "..." --format user`.
  - Explain the current task, undo / revert understanding, required scope confirmation, what Codex can safely inspect first, suggested replies, and high-risk non-actions.
  - Keep it read-only. Do not delete files, reset, revert, roll back, clean edits, update boundary status, advance gates, modify code, connect real data, write databases, run production actions, execute code workflow actions, or clean allowed sensitive configs.
  - Ask for precise undo scope before any file-changing action. If the confirmed scope would require delete, reset, revert, roll back, or code workflow action, ask for explicit authorization again before that action.
  - Do not expose commands, paths, lane, boundary, gate, spec, raw JSON, or internal check ids to the user.
- When the user says "先别改代码", "只给方案", "关键地方问我", "全自动做完", "协作模式怎么选", or equivalent wording, do not treat it as a new product-intake clarification or as ordinary continuation.
  - Internally prefer `python3 .gstack/scripts/nontechnical_mode_control.py --raw "..." --format user`.
  - Explain `自主执行 / 关键确认 / 手动控制`, this request's execution behavior, what needs user confirmation, and what Codex will not do.
  - Keep the helper read-only. Do not write `.gstack/codex-mode.local.md`, modify code, create long-term evidence, or change default mode unless the user separately authorizes that scope.
  - If the user requests `手动控制`, do not modify files or create long-term repo documents until the user explicitly authorizes implementation or documentation.
  - Do not clean, delete, or rewrite sensitive configs that the current project allows in the repository.
- When the user says "我不懂技术", "你帮我选一个最合适的方案", "不要让我选技术方案", "你替我决定第一步", "页面、接数据还是导出先做哪个", or equivalent wording, do not ask the user to choose a technical implementation route.
  - Internally prefer `python3 .gstack/scripts/nontechnical_recommendation.py --raw "..." --format user`.
  - Explain the recommended option, why it is recommended, what is not chosen yet, the first safe step, what needs confirmation, and what risky actions will not be taken.
  - If the user lists page, data, and export choices, recommend a minimal visible / clickable path first, then defer real data, backend interface, export, or team-sync work until the visible path is accepted.
  - Ask the user only for business result, data permission, production / database risk, or code workflow authorization; do not ask them to choose frontend, backend, API, database, or export implementation details.
  - Keep the helper read-only. Do not create or rewrite business task evidence, connect real data, write databases, run production actions, execute code workflow actions, or clean allowed sensitive configs.
- When the user says "第一次用", "怎么开始", "这个骨架怎么用", "这个骨架怎么用来开发复杂需求", "完全不会写代码", "从想法开始", or equivalent wording, do not route it to generic recommendation or one-question clarification.
  - Internally prefer `python3 .gstack/scripts/nontechnical_first_use.py --raw "..." --format user`.
  - Explain the new-user start path, what the user can send now, an example message, Codex's next actions, what needs user confirmation, and what will not be touched.
  - Keep this separate from `nontechnical_recommendation.py`: recommendation is for choosing among options; first-use is for explaining how to begin with the skeleton.
  - Keep the helper read-only. Do not create formal business requirement evidence, modify code, connect real data, write databases, run production actions, execute code workflow actions, or clean allowed sensitive configs.
- When the user says "先不要做导出", "只保留搜索和筛选", "不接真实数据先做可点击页面", "先给我一个能点的 demo，数据用假的", "先做静态页面看看效果，不接接口", "数据先用假的", "后面再接真实数据", "受限业务模块可以动但不要动数据库", or equivalent wording, do not treat it as a fresh product-intake clarification or as a generic real-data / interface risk pause.
  - Internally prefer `python3 .gstack/scripts/nontechnical_scope_change.py --raw "..." --format user`.
  - Explain what this round will include / keep, what it will exclude, what is deferred, Codex's next step, whether confirmation is needed, and what risky actions will not be taken.
  - If the user explicitly says not to connect real data or to use fake data first, keep it as prototype-first or mock-first scope; do not pause merely because the words "真实数据" appear.
  - If the user explicitly asks for a demo, prototype, static page, or no-interface version first, keep it as prototype-first scope; do not pause merely because the words "接口" or "demo" appear.
  - If the user relaxes a business forbidden scope but still forbids database or production work, keep the database / production prohibition and ask for confirmation before actual implementation changes.
  - Keep the helper read-only. Do not rewrite existing business task scope, connect real data, write databases, run production actions, execute code workflow actions, or clean allowed sensitive configs.
- When the user asks what to send before changing an existing page, do not ask only "what should success look like".
  - Internally prefer `python3 .gstack/scripts/nontechnical_page_change_brief.py --raw "..." --format user`.
  - The user-facing reply should include page location, current problem, desired change, acceptance method, and do-not-touch scope.
  - Keep this separate from visible-change troubleshooting; "刷新页面但没看到变化" still routes to `nontechnical_visible_change.py`.
  - Keep the helper read-only. Do not create business task evidence, inspect private pages, connect real data, write databases, run production actions, execute code workflow actions, or clean allowed sensitive configs.
- When the user asks for a general requirement template, pre-kickoff checklist, or how to describe a complex requirement, do not ask only one broad clarification question.
  - Internally prefer `python3 .gstack/scripts/nontechnical_requirement_brief.py --raw "..." --format user`.
  - The user-facing reply should include `你可以这样描述需求`, `照填模板`, `谁会用`, `成功后第一眼`, `数据来源`, `这次不做`, `怎么验收`, `Codex 的下一步`, `需要你确认`, and `这次不会做什么`.
  - Keep this separate from existing-page change briefs; if the utterance is explicitly about changing an existing page, `nontechnical_page_change_brief.py` still wins.
  - Keep the helper read-only. Do not create formal business requirement evidence, modify code, connect real data, write databases, run production actions, execute code workflow actions, or clean allowed sensitive configs.
- When the user asks whether a filled requirement is complete, do not fall back to a generic clarification or repeat the full template.
  - Internally prefer `python3 .gstack/scripts/nontechnical_requirement_readiness.py --raw "..." --format user`.
  - The user-facing reply should include `需求完整度检查`, `整体判断`, `已经说清楚`, `还需要补充`, `Codex 的下一步`, `需要你确认`, and `这次不会做什么`.
  - If the text mentions real data, production, databases, publishing, or code workflow actions without a safe constraint, ask for risk confirmation before any action in that risk area.
  - Keep the helper read-only. Do not create formal business requirement evidence, modify code, connect real data, write databases, run production actions, execute code workflow actions, or clean allowed sensitive configs.
- When the user mentions team sync, all teammates, 多人状态, 负责人筛选, realtime status, shared status, or cross-member task visibility, do not assume it is possible from local files.
  - Internally prefer `python3 .gstack/scripts/nontechnical_team_sync.py --raw "..." --format user` when the request is about team task-state sync.
  - Explain that without a shared database or service, Codex cannot promise real-time collaboration, permissions, reliable owner filtering, or cross-member writes.
  - Offer a repo evidence readonly generated view as the no-database route, and ask for confirmation before implementation.
  - If the user forbids a module such as 受限业务模块, keep that forbidden scope; user-facing output should say it will avoid 受限业务模块 without exposing paths.
- When the user asks for a completion note, delivery summary, team update, boss update, "这次改了什么", "怎么验收", or "还有什么风险", do not treat it as a new requirement acceptance plan.
  - Internally prefer `python3 .gstack/scripts/nontechnical_delivery_summary.py --raw "..." --format user`.
  - Read current task evidence and summarize what changed, how to verify, current QA status, risks and non-actions, and whether the note is final or only a progress summary.
  - If there is no active task, say Codex must recover or identify the task before generating a reliable completion note; do not invent completed work.
  - Do not expose commands, paths, lane, boundary, gate, spec, raw JSON, or internal check ids.
- When the user says a broad goal such as "make this easier for nontechnical users" or "improve the AI development flow", do not start implementation immediately.
  - Ask one business / experience question to choose the first pain point.
  - Recommended question: `你最想先改善哪一段体验：提需求、看进度、验收结果，还是出错后怎么继续？`
  - Internally classify this as `discovery` unless the user already gave a small, verifiable target.
- When Codex needs to help the user start a complex requirement without choosing among many helper scripts, prefer `nontechnical_guided_kickoff.py` as the internal guide.
  - With no raw request it prints a fill-in template.
  - With partial information it returns requirement readiness and priority missing fields.
  - With sufficient information it returns an execution plan.
  - With `--formal --ai-reviewed` it returns a read-only formal kickoff preview.
  - It must not write evidence, connect real data, run production / DB actions, or run git workflow actions.
  - If the user's non-goal explicitly says not to touch production, databases, real data, publishing, or code workflow, preserve that as a safety constraint instead of asking the user to confirm the same prohibition again.
- When the user gives a complex product goal, for example a complete dashboard, multiple page operations, data sync, export, multi-person acceptance, permissions, or a full workflow, do not treat it as a small single change.
  - Internally prefer `python3 .gstack/scripts/nontechnical_intake.py --raw "..."` to produce complexity, recommended path, delivery slices, first safe step, risks, and the single most useful follow-up question.
  - If the request has enough audience, success, non-goal, and risk information, internally use `python3 .gstack/scripts/nontechnical_task_starter.py --raw "..." --dry-run` to preview a draft starter package; use `--format user` when Codex needs a plain-language user-facing summary; use `--write` only when Codex intentionally wants draft evidence for follow-up semantic review.
  - If the user asks how Codex will proceed before formal kickoff, internally use `python3 .gstack/scripts/nontechnical_execution_plan.py --raw "..." --format user` to explain phases, what Codex can do automatically, what requires confirmation, and how acceptance will work.
  - If the user asks to split a request into tasks, priorities, milestones, or per-stage acceptance, also route to `nontechnical_execution_plan.py`; do not use current active-task verification merely because the utterance contains "怎么验收".
  - If the user asks how this specific request should be accepted or verified, internally use `python3 .gstack/scripts/nontechnical_acceptance_plan.py --raw "..." --format user` to explain acceptance checks, actual user actions, expected results, confirmation points, and risk notes. Do not use the current active-task dashboard for a request-specific acceptance question.
  - After Codex has read the repo context and semantically reviewed the request, use `python3 .gstack/scripts/nontechnical_formal_kickoff.py --raw "..." --ai-reviewed --write --activate` when the next useful move is to create a formal repo-native kickoff package from the nontechnical request.
  - Never pass `--ai-reviewed` merely because the helper returned `can_continue`; Codex must first confirm the request, risks, non-goals, and expected gates against current repo truth.
  - A formal kickoff package is not implementation completion. If the generated boundary leaves data-access, plan-eng-review, or domain-spec-readiness pending, continue those gates before implementation.
  - Explain the delivery slices and acceptance checks in plain language before implementation: first freeze the goal and acceptance, then build the smallest visible path, then clarify data or interface boundaries, then record QA evidence.
  - If the helper reports real data, production, DB, destructive command, or git risk, pause for user confirmation before any action in that risk area.
  - If the user confirms a safe scope such as only planning, read-only exploration, no production operation, no database writes, and no code workflow action, Codex may use `--risk-confirmation` to create a controlled starter package. This still only prepares the development starting point and acceptance; it does not authorize the risky action itself.
  - Never present starter package draft files as completed requirement freeze, plan review, or implementation readiness. Never show lane, boundary, gate, spec, raw JSON, or starter file paths to a nontechnical user unless asked.
  - Do not expose `fast-lane`, `standard`, `discovery`, `boundary`, `gate`, or raw JSON to the user unless asked.
- When using `nontechnical_execution_plan.py`, preserve task-breakdown semantics.
  - User-facing output should include `执行计划`, `推进顺序`, `需要你确认`, and `完成后可以这样验收`.
  - For plan-only requests such as `拆任务 / 排优先级 / 里程碑 / 每个阶段怎么验收`, output a phase framework and one confirmation question when business details are missing.
  - Do not route milestone or per-stage acceptance requests to `gstack_dashboard.py verify`; that helper is only for generic current-task completion verification.
- When the user mentions team sync in the context of a broader product request rather than a task-state sync request, keep the same constraints.
  - Explain that the current dashboard is generated from repo-native evidence in the current checkout.
  - Without a shared database or service, do not promise real-time collaboration, permissions, reliable owner filtering, or cross-member writes.
  - Offer a repo-evidence generated view as the no-database route, and ask for confirmation before implementation.
  - If the user forbids a module such as 受限业务模块, put the matching path, for example `app/restricted-module/**`, in Forbidden Files.
- When using `nontechnical_task_starter.py`, preserve inferred forbidden scopes.
  - Engineering output may include paths such as `app/restricted-module/**`.
  - User-facing output should only say the business scope will be avoided, for example `我会避开受限业务模块`.
- When using `nontechnical_task_starter.py`, preserve acceptance checks.
  - Engineering output should keep the structured `acceptance_checks` list for draft requirement / review / boundary follow-up.
  - User-facing output should explain `完成后可以这样验收` without exposing lane, boundary, gate, spec, raw JSON, or draft paths.
- When using `nontechnical_acceptance_plan.py`, preserve the distinction between current-task verification and request-specific acceptance planning.
  - User-facing output should include `可以这样验收`, `你要实际看到 / 操作`, and `预期应该看到`.
  - High-risk request-specific acceptance questions should pause for risk confirmation instead of producing executable acceptance actions.
- When using `nontechnical_visible_change.py`, preserve visible-change troubleshooting.
  - User-facing output should include `先确认你看的地方`, `怎么刷新 / 重新生成`, `如果刷新后还是旧的`, and `Codex 的下一步` when active task evidence is available.
  - Do not ask unrelated product-intake questions such as target user or success criteria for a refresh / stale-page complaint.
- When using `nontechnical_ci_failure.py`, preserve CI-failure troubleshooting.
  - User-facing output should include `先确认失败的是哪类检查`, `Codex 的下一步`, `需要你确认`, and `这次不会做什么`.
  - Do not route GitHub / CI / PR check failures to `gstack_doctor.py explain` unless the failure is explicitly about local hooks, active boundary, skills, or local collaboration state.
  - Do not treat allowed sensitive configuration files as runtime-artifact defects.
- When using `nontechnical_continue.py`, preserve continuation semantics.
  - User-facing output should include `我会按继续推进处理`, `当前任务`, `Codex 的下一步`, `需要你确认`, and `这次不会做什么` when active task evidence is available.
  - Do not route terse continuation prompts to `clarification`, `task_kickoff`, CI failure, error recovery, or formal kickoff unless the user explicitly adds those signals.
- When using `nontechnical_recommendation.py`, preserve recommendation semantics.
  - User-facing output should include `我会先给推荐方案`, `推荐方案`, `为什么推荐`, `暂不选择`, `第一安全步`, `需要你确认`, and `这次不会做什么`.
  - Do not route "这个需求有几种做法你直接推荐一个" to `scope_change`; it is a recommendation request even if it contains "这个需求".
  - Do not ask the user to choose technical implementation details merely because several approaches exist.
- When using `nontechnical_first_use.py`, preserve first-use semantics.
  - User-facing output should include `新手开始路径`, `你可以这样开始`, `现在只要这样发`, `Codex 的下一步`, `需要你确认`, and `这次不会做什么`.
  - Do not route first-time usage, skeleton-usage, no-code, or from-idea-start questions to generic `clarification` or `recommendation`.
  - Do not expose commands, paths, lane, boundary, gate, spec, raw JSON, or internal check ids to the user.
- When using `nontechnical_scope_change.py`, preserve scope-change semantics.
  - User-facing output should include `我会按需求范围调整处理`, `这次先做 / 保留`, `这次先不做 / 排除`, `后续再做` when applicable, `需要你确认`, and `这次不会做什么`.
  - Do not route "不接真实数据，先做可点击页面" to generic `risk_confirmation`; it is a safe prototype-first constraint unless the user also asks to operate real data.
  - Do not rewrite existing requirement / boundary / scope or implementation merely because the helper parsed a range change; actual implementation still needs the active task flow and confirmation when scope expands.
- When using `nontechnical_task_list.py`, preserve task-list semantics.
  - User-facing output should include `任务概览`, `未完成任务`, `卡住任务`, `优先看的任务`, `Codex 的下一步`, `需要你确认`, and `这次不会做什么`.
  - Do not route "列一下未完成任务 / 看看历史需求和未完成任务 / 给我任务清单" to `clarification`, `task_kickoff`, current-task progress, or team-sync unless the user explicitly asks for real-time multi-person sync.
- When using `nontechnical_requirement_brief.py`, preserve general intake-template semantics.
  - User-facing output should include a fill-in template and explain that partial information is acceptable.
  - Do not route existing-page requests to this generic helper when `nontechnical_page_change_brief.py` is a better fit.
  - Do not expose commands, paths, lane, boundary, gate, spec, raw JSON, or internal check ids to the user.
  - Treat it as a read-only overview of local repo-native task evidence; do not create shared status files, rewrite task records, execute code workflow actions, or clean allowed sensitive configs.
- When using `nontechnical_requirement_readiness.py`, preserve readiness-check semantics.
  - User-facing output should explain what is clear enough, what must be added first, and whether the next step is a kickoff preview, one missing business detail, or risk confirmation.
  - Do not route "这些信息够不够开工 / 我这样描述可以开始做了吗" to `clarification`, `task_kickoff`, generic `requirement_brief`, or formal kickoff unless Codex has separately reviewed and authorized the formal flow.
  - Do not expose commands, paths, lane, boundary, gate, spec, raw JSON, or internal check ids to the user.
  - Keep it read-only; do not create shared status files, rewrite task records, execute code workflow actions, or clean allowed sensitive configs.
- When using `nontechnical_team_sync.py`, preserve no-database team-sync limits.
  - User-facing output should include `不引入数据库`, `不能承诺实时多人同步`, `只读状态视图`, `需要你确认`, and the forbidden business scope when present.
  - Do not route no-database team task-state sync to generic `risk_confirmation` merely because the utterance contains `数据库`.
- When using `nontechnical_delivery_summary.py`, preserve delivery-summary semantics.
  - User-facing output should include `可以直接这样发给团队`, `本次交付`, `这次改了什么`, `怎么验收`, `风险和未做`, and `需要你确认`.
  - Do not route a team-facing completion note to `acceptance_plan` merely because the utterance contains `怎么验收`.
  - Do not invent QA completion if the current task is not complete or the QA stage is not done.
- When using `nontechnical_task_starter.py`, preserve risk confirmation controls.
  - Engineering output should keep `risk_confirmation_status` and `risk_controls`.
  - User-facing output should say Codex can first organize the development starting point and will not execute high-risk actions.
  - A vague confirmation such as `我确认` is insufficient; ask for the safe scope instead of continuing.

## Workflow

1. Interpret the user's natural-language goal with `.gstack/templates/nontechnical-task-intake.template.md` or the deterministic helper `.gstack/scripts/nontechnical_intake.py`.
   - For complex goals, use the helper's recommended path, delivery slices, and first safe step to decide the user-facing next step.
2. Decide whether enough information exists to proceed.
   - If yes, continue automatically.
   - If no, ask only the shortest business question that changes the product result or risk level.
3. Internally run the normal task flow through `kk-task-kickoff`.
   - Create or update requirement, review, task boundary, Required Gates, Subagent Plan, and QA plan.
   - Fill `User-visible Acceptance` and `Generated Artifact Policy` in the boundary.
   - For HTML / frontend / visualization tasks, record the acceptance URL, refresh/regeneration path, and "no visible change" troubleshooting path.
   - Set the active boundary locally.
   - Choose `fast-lane`, `standard`, or `discovery` internally; do not expose the term unless the user asks.
4. Tell the user only:
   - what Codex understood,
   - what Codex will change,
   - what Codex will not touch,
   - whether user confirmation is needed.
5. Implement inside the declared boundary.
6. Run verification yourself.
   - For user-visible UI, HTML, or visualization tasks, use Browser / Chrome / Playwright to operate the relevant controls.
   - Do not mark the task done using only `rg`, JSON, HTML strings, or a screenshot appearance check.
   - If `file://` or browser permission policy blocks validation, open the same page through a local HTTP server and continue. If validation is still impossible, report `blocked` or `partial`, not `done`.
7. Final reply should say:
   - what changed,
   - where the user can inspect or try it,
   - whether validation passed,
   - any real risk or unresolved user decision.

## User-Facing Language

Prefer:

- `我理解你想要的是...`
- `这次我会处理...`
- `这次不会碰...`
- `这里需要你确认一个业务判断...`
- `我已经完成，本地检查通过...`

Avoid unless the user asks:

- `boundary`
- `Required Gates`
- `domain-spec-readiness`
- `spec_sync_guard`
- `team_flow_guard`
- `active boundary`
- `Flow Lane`

## Confirmation Policy

Ask the user only when the answer cannot be proven locally and affects one of these:

- product meaning or business rule,
- real production data,
- production environment,
- DB schema,
- destructive command,
- git workflow action,
- spending or external service action.

Do not ask for:

- which template to use,
- which command to run,
- where to place repo-native evidence,
- whether to create a task boundary,
- what tests to run when the repository already defines them.

## Internal Evidence Requirements

For formal implementation tasks, still maintain:

- `.gstack/requirements/`
- `.gstack/reviews/`
- `.gstack/task-boundaries/`
- `.gstack/qa-reports/`
- relevant `stack/.../specs/` or `.gstack/knowledge/` updates

For user-visible work, QA evidence must distinguish:

- structure exists,
- controls are visible,
- controls are operable,
- state changes are correct,
- empty states are correct,
- refresh or regeneration instructions are clear.

If the work only improves the framework, the primary spec target is usually:

- `.gstack/knowledge/ai-programming-framework.md`
- `.gstack/skills/README.md`
- `.gstack/README.md`

## Failure Handling

When a guard fails:

1. Read the failure.
2. Fix missing internal evidence or docs when locally provable.
3. Re-run verification.
4. Tell the user only the meaningful product or risk implication.

If the blocker is a business decision or permission, ask one concise question and explain the tradeoff in plain language.

## Regression Cases

Use `.gstack/knowledge/natural-language-dev-regression-cases.md` to validate this skill after changes.

At minimum, re-test:

- current progress query,
- broad nontechnical-experience improvement,
- team sync /多人状态 /负责人筛选 without database,
- explicit forbidden scope,
- high-risk production data request,
- CI / GitHub check failure explanation,
- continuation after a prior plan or task,
- team task-state sync without database,
- team-facing completion / delivery summary,
- user asks how to verify completion.
