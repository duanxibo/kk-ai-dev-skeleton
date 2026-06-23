#!/usr/bin/env python3
"""Route a nontechnical user utterance to the right internal helper.

This helper is deterministic and read-only. It does not create formal evidence,
connect to data sources, open browsers, or run git actions. Codex uses it before
the normal natural-language development flow so user-facing replies stay plain.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass

from nontechnical_intake import IntakeSummary, build_summary


FORMAL_KICKOFF_KEYWORDS = (
    "正式开工",
    "正式开始",
    "开始正式做",
    "直接开工",
    "直接开始",
    "直接推进",
    "进入正式任务",
    "生成正式开工包",
    "开工包",
    "我已经说清楚",
    "已经说清楚了",
    "不用再问",
    "不要再拆了",
    "formal kickoff",
)

HOME_KEYWORDS = (
    "打开开发首页",
    "开发首页",
    "项目首页",
    "打开项目首页",
    "我刚打开项目",
    "刚打开项目",
    "codex 打开项目",
    "codex打开项目",
    "打开项目后",
    "打开项目之后",
    "现在能做什么",
    "我现在能做什么",
    "现在可以做什么",
    "我可以做什么",
    "从这里开始",
    "开始使用",
)

HOME_START_KEYWORDS = (
    "怎么开始",
    "如何开始",
    "从哪里开始",
)

IMPLEMENTATION_READINESS_KEYWORDS = (
    "能开始实现了吗",
    "可以开始实现了吗",
    "能不能开始实现",
    "能开始开发了吗",
    "可以开始开发了吗",
    "能不能开始开发",
    "可以开始写代码了吗",
    "能开始写代码了吗",
    "能不能开始写代码",
    "还差什么才能开始开发",
    "还差什么才能开始实现",
    "还差什么才能写代码",
    "正式开工后还差什么",
    "开工后还差什么",
    "实现前还差什么",
    "开发前还差什么",
    "进入实现前还差什么",
    "什么时候可以开始实现",
    "什么时候可以开始开发",
)

CONFIRMATION_BRIEF_KEYWORDS = (
    "现在需要我确认什么",
    "需要我确认什么",
    "我该回复什么",
    "我要回复什么",
    "要我回复什么",
    "你现在等我什么",
    "卡在我这里吗",
    "是不是卡在我这里",
    "哪些需要我决定",
    "有哪些需要我决定",
    "哪些需要我拍板",
    "需要我拍板什么",
    "我现在要确认什么",
)

CONFIRMATION_RESPONSE_KEYWORDS = (
    "我确认",
    "确认了",
    "确认",
    "可以",
    "可以的",
    "同意",
    "没问题",
    "没问题，继续",
    "按这个做",
    "按你说的做",
    "按你说的来",
    "就按这个",
)

PAUSE_KEYWORDS = (
    "先停一下",
    "先暂停",
    "暂停一下",
    "暂停这个任务",
    "暂停当前任务",
    "暂停推进",
    "这轮先暂停",
    "本轮先暂停",
    "先到这里",
    "今天先到这里",
    "先别继续",
    "先不要继续",
    "不要继续做了",
    "不用继续做了",
    "暂时不要继续",
    "暂时不用继续",
    "停止推进",
    "停止当前任务",
)

UNDO_REQUEST_KEYWORDS = (
    "撤销刚才",
    "撤销这个改动",
    "撤销这次改动",
    "不要这个改动",
    "不要刚才的改动",
    "回到之前",
    "恢复到之前",
    "恢复到改之前",
    "把刚才做的撤回",
    "撤回刚才",
    "回滚刚才",
    "回滚这个改动",
    "回滚这次改动",
    "删掉刚才改的",
    "删除刚才改的",
    "不想要这个版本",
)

FIRST_USE_EXCLUSION_KEYWORDS = (
    "第一次",
    "初次",
    "新手",
    "不会写代码",
    "完全不会",
    "不懂技术",
    "从想法开始",
    "这个骨架",
    "这个项目怎么用",
    "怎么用这个项目",
    "怎么用这个骨架",
    "骨架怎么用",
    "用来开发一个复杂需求",
    "开发复杂需求",
)

EXECUTION_PLAN_KEYWORDS = (
    "怎么推进",
    "你会怎么做",
    "会怎么做",
    "执行计划",
    "开发计划",
    "实施计划",
    "推进计划",
    "推进顺序",
    "先做什么",
    "后做什么",
    "路线图",
    "怎么安排",
    "什么时候需要我确认",
    "拆任务",
    "拆成几个小任务",
    "拆成小任务",
    "任务拆解",
    "拆解任务",
    "排优先级",
    "排一下优先级",
    "优先级",
    "定顺序",
    "里程碑",
    "阶段怎么验收",
    "每个阶段怎么验收",
    "每一步验收",
    "每一步怎么验收",
    "先做哪几个",
    "execution plan",
)

ACCEPTANCE_PLAN_KEYWORDS = (
    "怎么验收",
    "如何验收",
    "验收标准",
    "验收方式",
    "验收清单",
    "怎么知道它真的好了",
    "怎么知道真的好了",
    "做完以后我怎么知道",
    "我怎么知道它好了",
    "我怎么知道真的好了",
    "完成后怎么看",
    "怎么判断",
    "acceptance criteria",
)

VISIBLE_CHANGE_KEYWORDS = (
    "刷新了页面但没看到变化",
    "刷新页面但没看到变化",
    "刷新了页面没变化",
    "刷新后没变化",
    "刷新后还是旧的",
    "页面还是旧的",
    "还是旧页面",
    "看不到页面变化",
    "看不到变化",
    "没看到变化",
    "没看到改动",
    "打开后还是旧页面",
    "打开还是旧的",
    "页面没变",
    "页面没有变",
)

CI_FAILURE_CONTEXT_KEYWORDS = (
    "github",
    "github actions",
    "ci",
    "workflow",
    "pr 检查",
    "pull request",
    "工程检查",
    "engineering-smoke",
    "natural-language-dev",
    "runtime-artifact-guard",
    "lunhui-backend",
    "product-review",
    "zm-demo",
)

CI_FAILURE_WORDS = (
    "失败",
    "没过",
    "挂了",
    "红了",
    "failed",
    "failure",
    "failing",
)

CONTINUE_KEYWORDS = (
    "继续做",
    "继续推进",
    "继续优化",
    "按你刚才的计划继续",
    "按刚才的计划继续",
    "按这个继续",
    "按这个推进",
    "按计划继续",
    "你继续",
    "那就继续",
    "开始第一步",
    "先做第一步",
    "那就先做第一步",
    "按第一步开始",
    "就这样做",
    "就这样推进",
    "开始做吧",
    "下一步继续",
)

TEAM_SYNC_CONTEXT_KEYWORDS = (
    "团队",
    "所有人",
    "多人状态",
    "多人任务",
    "负责人筛选",
    "跨成员",
    "team",
    "shared status",
)

TEAM_SYNC_STATUS_KEYWORDS = (
    "任务状态",
    "状态同步",
    "同步起来",
    "实时状态",
    "所有人的任务",
    "团队状态",
    "负责人",
)

DELIVERY_SUMMARY_KEYWORDS = (
    "完成说明",
    "交付说明",
    "交付总结",
    "完成总结",
    "结果说明",
    "团队看的",
    "给团队看",
    "给老板看",
    "发给团队",
    "发给老板",
    "汇报",
    "总结一下这次",
    "这次改了什么",
    "改了什么",
    "还有什么风险",
    "风险说明",
)

TASK_LIST_KEYWORDS = (
    "未完成任务",
    "没做完的任务",
    "还没做完的任务",
    "待处理任务",
    "卡住的任务",
    "历史需求",
    "任务清单",
    "任务列表",
    "任务概览",
    "需求清单",
    "需求列表",
    "列一下任务",
    "列一下现在",
    "列一下未完成",
    "列一下还没做完",
    "看看有哪些任务",
    "看看有哪些历史需求",
    "有哪些未完成",
    "有哪些还没做完",
    "所有任务",
    "全部任务",
)

MODE_CONTROL_KEYWORDS = (
    "协作模式",
    "自主执行",
    "全自动做完",
    "自动执行",
    "你自己决定并做完",
    "关键确认",
    "关键地方问我",
    "关键点问我",
    "重要决策问我",
    "实现前让我确认",
    "手动控制",
    "先别改代码",
    "先不要改代码",
    "不要改代码",
    "别改代码",
    "只给方案",
    "只给我方案",
    "先给方案",
    "只分析",
    "不要自动执行",
    "现在是什么模式",
    "模式怎么选",
)

MODE_CHOICE_ONLY_KEYWORDS = (
    "协作模式怎么选",
    "切换协作模式",
    "有哪些协作模式",
    "模式怎么选",
)

FIRST_USE_KEYWORDS = (
    "第一次用",
    "初次使用",
    "新手",
    "怎么开始",
    "如何开始",
    "从哪里开始",
    "从想法开始",
    "带我从想法开始",
    "怎么用这个项目",
    "这个项目怎么用",
    "怎么用这个骨架",
    "这个骨架怎么用",
    "骨架怎么用来",
    "用这个骨架",
    "用来开发一个复杂需求",
    "开发复杂需求",
    "完全不会写代码",
    "不会写代码",
)

RECOMMENDATION_KEYWORDS = (
    "我不懂技术",
    "不懂技术",
    "你帮我选",
    "帮我选",
    "帮我选一个",
    "选一个最合适",
    "最合适的方案",
    "推荐一个",
    "直接推荐",
    "你推荐",
    "给我推荐",
    "不要让我选技术方案",
    "不让我选技术方案",
    "不要让我选",
    "不用我选",
    "替我决定",
    "你替我决定",
    "你来决定",
    "你决定第一步",
    "决定第一步",
    "几种做法",
    "几种方案",
    "哪种方案",
    "方案取舍",
    "技术方案",
)

SCOPE_CHANGE_KEYWORDS = (
    "需求改一下",
    "改一下需求",
    "刚才的需求",
    "这个需求",
    "刚才说的不对",
    "先不要做",
    "先不做",
    "不要做导出",
    "只保留",
    "改成",
    "换成",
    "不接真实数据",
    "暂时不接真实数据",
    "先不接真实数据",
    "先做原型",
    "做一个原型",
    "做个原型",
    "可点击原型",
    "原型给我看",
    "prototype",
    "先给我一个 demo",
    "先给我一个demo",
    "做一个 demo",
    "做一个demo",
    "做个 demo",
    "做个demo",
    "能点的 demo",
    "能点的demo",
    "可点击 demo",
    "可点击demo",
    "先做静态页面",
    "先做静态页",
    "静态页面",
    "静态页",
    "不接接口",
    "先不接接口",
    "暂时不接接口",
    "数据先用假的",
    "数据用假的",
    "用假数据",
    "假的数据",
    "假数据",
    "mock",
    "模拟数据",
    "可点击页面",
    "能点的版本",
    "后面再接真实数据",
    "后续再接真实数据",
    "商品审核可以动",
    "可以动商品审核",
    "不要动数据库",
)

PAGE_CHANGE_BRIEF_CONTEXT_KEYWORDS = (
    "已有页面",
    "现有页面",
    "改页面",
    "页面改动",
    "页面需求",
    "页面信息",
    "页面要改",
    "页面想改",
    "前端页面",
)

PAGE_CHANGE_BRIEF_HELP_KEYWORDS = (
    "不知道该先给你什么信息",
    "不知道先给你什么信息",
    "不知道给你什么信息",
    "要给你什么信息",
    "需要我提供什么",
    "需要提供什么",
    "该提供什么",
    "要怎么描述",
    "怎么描述",
    "怎么说清楚",
    "才能让你直接开工",
    "怎么提需求",
)

REQUIREMENT_BRIEF_KEYWORDS = (
    "需求模板",
    "需求信息",
    "信息卡",
    "照着填",
    "照填",
    "怎么描述需求",
    "怎么描述给你",
    "不知道该怎么描述",
    "不知道怎么描述",
    "不知道怎么说需求",
    "开工前我需要给你哪些信息",
    "开工前需要给你哪些信息",
    "开工前要给你哪些信息",
    "需要给你哪些信息",
    "要给你哪些信息",
    "要提供哪些信息",
    "需要提供哪些信息",
    "怎么提需求",
    "如何提需求",
    "需求怎么写",
    "需求描述",
    "帮我整理需求",
    "帮我把需求说清楚",
    "问我几个问题",
    "一步步问我",
    "需求表单",
)

REQUIREMENT_READINESS_KEYWORDS = (
    "还缺什么",
    "缺什么信息",
    "缺哪些信息",
    "信息够不够",
    "信息够吗",
    "够不够开工",
    "够开工吗",
    "够不够开始",
    "可以开始做了吗",
    "可以开工了吗",
    "能不能开工",
    "能开工了吗",
    "能不能开始做",
    "需求是否完整",
    "需求完整吗",
    "需求够完整吗",
    "检查一下需求",
    "检查需求",
    "审一下需求",
    "帮我审需求",
    "看看需求",
    "按模板填",
    "填了一版",
    "我这样描述",
    "这样描述可以",
    "这样写可以",
)

UI_OPTIMIZATION_KEYWORDS = (
    "进行 ui 优化",
    "进行ui优化",
    "ui 优化",
    "ui优化",
    "优化 ui",
    "优化ui",
    "优化界面",
    "界面优化",
    "优化页面",
    "页面优化",
    "美化页面",
    "美化界面",
    "页面美化",
    "界面美化",
    "提升视觉",
    "视觉优化",
    "视觉美化",
    "优化视觉",
    "提升审美",
    "提升界面质感",
    "提升页面质感",
    "界面太丑",
    "页面太丑",
    "界面不好看",
    "页面不好看",
    "不够好看",
    "不够专业",
    "不高级",
    "像模板",
    "像 demo",
    "像demo",
)


@dataclass(frozen=True)
class IntentRoute:
    raw_request: str
    intent: str
    confidence: str
    route_reason: str
    internal_entry: str
    can_continue: bool
    needs_user_confirmation: bool
    user_next_step: str
    user_question: str
    risk_status: str
    complexity: str
    likely_surface: str
    acceptance_focus: list[str]


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def has_any(text: str, *keywords: str) -> bool:
    lowered = text.lower()
    return any(keyword.lower() in lowered for keyword in keywords)


def is_formal_kickoff_request(text: str) -> bool:
    return has_any(text, *FORMAL_KICKOFF_KEYWORDS)


def is_home_request(text: str) -> bool:
    if is_formal_kickoff_request(text) or is_mode_control_request(text):
        return False
    if has_any(text, *HOME_KEYWORDS):
        return True
    if has_any(text, *HOME_START_KEYWORDS) and not has_any(text, *FIRST_USE_EXCLUSION_KEYWORDS):
        return True
    return False


def is_implementation_readiness_request(text: str) -> bool:
    if is_formal_kickoff_request(text) or is_mode_control_request(text):
        return False
    return has_any(text, *IMPLEMENTATION_READINESS_KEYWORDS)


def is_confirmation_brief_request(text: str) -> bool:
    if is_formal_kickoff_request(text) or is_mode_control_request(text):
        return False
    return has_any(text, *CONFIRMATION_BRIEF_KEYWORDS)


def is_confirmation_response_request(text: str) -> bool:
    if is_formal_kickoff_request(text) or is_mode_control_request(text):
        return False
    if is_implementation_readiness_request(text):
        return False
    if is_confirmation_brief_request(text):
        return False
    if is_requirement_readiness_request(text):
        return False
    if has_any(text, "吗", "么", "？", "?"):
        return False
    compacted = text.strip()
    if compacted in {"好", "好的", "行", "行的", "嗯", "嗯嗯"}:
        return True
    return has_any(text, *CONFIRMATION_RESPONSE_KEYWORDS)


def is_high_risk_authorization_text(text: str) -> bool:
    return has_any(
        text,
        "真实数据",
        "生产",
        "线上",
        "数据库",
        "上线",
        "发布",
        "提交",
        "推送",
        "commit",
        "push",
        "merge",
        "pr",
        "删除",
        "撤销",
        "回滚",
        "reset",
        "破坏性",
    )


def is_pause_request(text: str) -> bool:
    if is_formal_kickoff_request(text):
        return False
    if is_undo_request(text):
        return False
    return has_any(text, *PAUSE_KEYWORDS)


def is_undo_request(text: str) -> bool:
    if is_formal_kickoff_request(text) or is_mode_control_request(text):
        return False
    return has_any(text, *UNDO_REQUEST_KEYWORDS)


def is_execution_plan_request(text: str) -> bool:
    return has_any(text, *EXECUTION_PLAN_KEYWORDS)


def is_acceptance_plan_request(text: str, summary: IntakeSummary) -> bool:
    if not has_any(text, *ACCEPTANCE_PLAN_KEYWORDS):
        return False
    if summary.likely_surface != "不确定":
        return True
    if summary.risks:
        return True
    if summary.complexity in {"中等需求", "复杂需求", "高风险需求", "高风险复杂需求"}:
        return True
    return False


def is_visible_change_request(text: str) -> bool:
    return has_any(text, *VISIBLE_CHANGE_KEYWORDS)


def is_ci_failure_request(text: str) -> bool:
    lowered = text.lower()
    return any(word.lower() in lowered for word in CI_FAILURE_WORDS) and any(
        keyword.lower() in lowered for keyword in CI_FAILURE_CONTEXT_KEYWORDS
    )


def is_continue_request(text: str) -> bool:
    if is_formal_kickoff_request(text):
        return False
    if is_high_risk_authorization_text(text):
        return False
    if has_any(text, "出错", "报错", "失败", "门禁", "继续不了", "怎么继续", "下一步怎么办"):
        return False
    return has_any(text, *CONTINUE_KEYWORDS)


def is_team_sync_request(text: str) -> bool:
    if "多人验收" in text and not has_any(text, "任务状态", "团队", "负责人", "所有人"):
        return False
    return has_any(text, *TEAM_SYNC_CONTEXT_KEYWORDS) and has_any(text, *TEAM_SYNC_STATUS_KEYWORDS)


def is_delivery_summary_request(text: str) -> bool:
    if has_any(text, *DELIVERY_SUMMARY_KEYWORDS):
        return True
    return has_any(text, "怎么验收", "验收", "风险") and has_any(text, "团队", "完成", "总结")


def is_task_list_request(text: str) -> bool:
    if is_mode_control_request(text):
        return False
    if is_team_sync_request(text):
        return False
    if has_any(text, "当前任务") and has_any(text, "完成了吗", "进度", "状态"):
        return False
    return has_any(text, *TASK_LIST_KEYWORDS)


def is_mode_control_request(text: str) -> bool:
    return has_any(text, *MODE_CONTROL_KEYWORDS)


def is_mode_choice_only_request(text: str) -> bool:
    if not has_any(text, *MODE_CHOICE_ONLY_KEYWORDS):
        return False
    explicit_modes = (
        "自主执行",
        "全自动做完",
        "关键确认",
        "关键地方问我",
        "手动控制",
        "先别改代码",
        "只给方案",
    )
    return not has_any(text, *explicit_modes)


def is_recommendation_request(text: str) -> bool:
    if is_mode_control_request(text):
        return False
    return has_any(text, *RECOMMENDATION_KEYWORDS)


def is_first_use_request(text: str) -> bool:
    if is_mode_control_request(text) or is_formal_kickoff_request(text):
        return False
    if is_recommendation_request(text) and not has_any(
        text,
        "第一次",
        "怎么开始",
        "如何开始",
        "从想法开始",
        "从哪里开始",
        "这个骨架",
        "这个项目",
    ):
        return False
    return has_any(text, *FIRST_USE_KEYWORDS)


def is_scope_change_request(text: str) -> bool:
    if is_mode_control_request(text):
        return False
    if is_recommendation_request(text):
        return False
    return has_any(text, *SCOPE_CHANGE_KEYWORDS)


def is_page_change_brief_request(text: str) -> bool:
    if is_visible_change_request(text) or is_mode_control_request(text):
        return False
    return has_any(text, *PAGE_CHANGE_BRIEF_CONTEXT_KEYWORDS) and has_any(
        text, *PAGE_CHANGE_BRIEF_HELP_KEYWORDS
    )


def is_requirement_readiness_request(text: str) -> bool:
    if is_visible_change_request(text) or is_mode_control_request(text):
        return False
    if is_team_sync_request(text) or is_task_list_request(text):
        return False
    if is_delivery_summary_request(text):
        return False
    if is_execution_plan_request(text) or is_acceptance_plan_request(text, build_summary_for_text(text)):
        return False
    return has_any(text, *REQUIREMENT_READINESS_KEYWORDS)


def is_requirement_brief_request(text: str) -> bool:
    if is_visible_change_request(text) or is_mode_control_request(text):
        return False
    if is_requirement_readiness_request(text):
        return False
    if is_page_change_brief_request(text):
        return False
    if is_team_sync_request(text) or is_task_list_request(text):
        return False
    if is_execution_plan_request(text) or is_acceptance_plan_request(text, build_summary_for_text(text)):
        return False
    return has_any(text, *REQUIREMENT_BRIEF_KEYWORDS)


def is_ui_optimization_request(text: str) -> bool:
    if is_mode_control_request(text):
        return False
    if is_visible_change_request(text) or is_page_change_brief_request(text):
        return False
    if has_any(text, "继续"):
        return False
    return has_any(text, *UI_OPTIMIZATION_KEYWORDS)


def build_summary_for_text(text: str) -> IntakeSummary:
    return build_summary(
        argparse.Namespace(raw=text, audience="", success="", non_goal="", risk_confirmation="")
    )


def build_intake_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        raw=args.raw,
        audience=args.audience,
        success=args.success,
        non_goal=args.non_goal,
        risk_confirmation=args.risk_confirmation,
    )


def acceptance_focus_for(summary: IntakeSummary, intent: str) -> list[str]:
    if intent == "nontechnical_home":
        return ["展示当前任务、可选下一步、复杂需求开始模板、当前结果验收方式和出错恢复路径"]
    if intent == "implementation_readiness":
        return ["读取当前任务记录，说明是否可以开始实现、还缺哪些准备、Codex 下一步和是否需要用户确认"]
    if intent == "confirmation_brief":
        return ["读取当前任务记录，说明现在是否等用户确认、需要确认什么、用户可怎么回复和 Codex 下一步"]
    if intent == "confirmation_response":
        return ["读取当前任务记录，说明模糊确认能确认什么、还需要明确什么、Codex 可以安全做什么和不会把它当成高风险授权"]
    if intent == "pause_current_task":
        return ["读取当前任务记录，说明已按暂停理解、暂停后不会继续做什么、保留了什么和之后怎么恢复"]
    if intent == "undo_request":
        return ["读取当前任务记录，说明这是需要确认范围的撤销 / 回滚请求、可以先安全查看什么、用户可怎么回复和不会直接执行的高风险动作"]
    if intent == "mode_control":
        return ["说明当前协作模式、本次怎么执行、需要用户确认什么、以及不会执行的高风险动作"]
    if intent == "recommendation":
        return ["说明推荐方案、为什么推荐、暂不选择的方案、第一安全步、需要用户确认什么，以及不会执行的高风险动作"]
    if intent == "first_use_guide":
        return ["说明第一次使用项目骨架时从哪里开始、现在只要发什么、Codex 下一步和不会执行的高风险动作"]
    if intent == "scope_change":
        return ["说明这次保留什么、先不做什么、后续再做什么、是否需要用户确认，以及不会执行的高风险动作"]
    if intent == "page_change_brief":
        return ["说明改已有页面需要提供哪些信息、照填模板、Codex 下一步、需要用户确认什么，以及不会执行的高风险动作"]
    if intent == "requirement_brief":
        return ["说明通用需求需要提供哪些信息、照填模板、Codex 下一步、需要用户确认什么，以及不会执行的高风险动作"]
    if intent == "requirement_readiness":
        return ["说明需求信息完整度、已具备信息、优先缺失项、风险确认、Codex 下一步，以及不会执行的高风险动作"]
    if intent == "progress_status":
        return ["说明当前任务、完成状态、是否卡住、下一步和是否需要用户确认"]
    if intent == "completion_verify":
        return ["说明看哪里、做什么、预期看到什么、刷新方式和 QA 状态"]
    if intent == "acceptance_plan":
        return ["围绕用户提出的具体需求，说明验收清单、实际操作、预期结果、确认点和风险说明"]
    if intent == "visible_change_troubleshoot":
        return ["确认当前任务查看位置、刷新或重新生成方式、看不到变化时的排查步骤和是否需要用户补充页面线索"]
    if intent == "ci_failure_explain":
        return ["确认失败检查名、检查类型、Codex 下一步、是否需要用户提供失败日志，以及不会执行的高风险动作"]
    if intent == "continue_current_task":
        return ["按当前任务或持续目标继续推进，说明当前任务状态、Codex 下一步、是否需要用户确认，以及不会执行的高风险动作"]
    if intent == "team_sync_explain":
        return ["说明无数据库团队状态同步的能力边界、repo evidence 只读视图路线、需要用户确认项，以及不会执行的高风险动作"]
    if intent == "delivery_summary":
        return ["读取当前任务 evidence，生成可给团队看的交付总结、验收方式、风险和未做事项、下一步建议"]
    if intent == "task_list_explain":
        return ["读取 repo-native task evidence，生成未完成任务、卡住任务和下一步建议的用户可读概览"]
    if intent == "ui_optimization_kickoff":
        return [
            "先识别页面、目标用户、第一眼理解目标和主流程",
            "实现前完成 UI 设计梳理，覆盖页面类型、信息架构、组件计划、视觉方向、状态和响应式策略",
            "实现后进行视觉复核和浏览器验收，确认 API、数据合同、runner 逻辑和真实服务接入不被改变",
        ]
    if intent == "error_recovery":
        return ["说明当前是否能继续、Codex 可修复项、需要用户确认项和下一步"]
    if intent == "natural_language_smoke":
        return ["说明关键路径检查通过 / 未通过、覆盖了什么、是否需要用户确认"]
    if summary.risks and summary.risk_confirmation_status != "safe-to-draft":
        return ["只确认风险范围和授权，不执行真实数据、生产、数据库或代码提交流程"]
    if summary.risks and summary.risk_confirmation_status == "safe-to-draft":
        return ["只整理开发起点、任务范围和验收口径，不执行高风险动作"]
    if intent == "formal_kickoff_preview":
        return ["预览正式开工包，确认任务范围、推进方式和完成后验收方式；不自动写入正式记录"]
    if intent == "execution_plan":
        return ["说明推进顺序、Codex 可自动处理事项、需要用户确认的点和最终验收方式"]
    if summary.can_continue and summary.complexity in {"复杂需求", "高风险复杂需求", "中等需求"}:
        return ["先固定需求和验收口径，再拆最小可见路径、数据 / 接口边界和 QA evidence"]
    if summary.can_continue:
        return ["进入小范围正式任务，保留可复现验证命令和 QA evidence"]
    return ["先问一个会影响产品结果或风险判断的问题"]


def route_meta_intent(raw: str, summary: IntakeSummary) -> IntentRoute | None:
    if is_home_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="nontechnical_home",
            confidence="high",
            route_reason="用户在通过 Codex 打开项目后的总入口询问现在能做什么，需要展示自然语言开发首页，而不是进入单一需求澄清",
            internal_entry="nontechnical_home.user",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会打开非技术开发首页，用人话说明当前任务、可做选项、复杂需求怎么开始、怎么验收和出错后怎么继续。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "nontechnical_home"),
        )

    if is_implementation_readiness_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="implementation_readiness",
            confidence="high",
            route_reason="用户在询问当前任务是否已具备进入实现的准备，需要把内部流程和检查状态翻译成可读的实现就绪说明",
            internal_entry="nontechnical_implementation_readiness.user",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会读取当前任务记录，用人话说明是否可以开始实现、还差哪些准备、下一步怎么补齐和是否需要你确认。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "implementation_readiness"),
        )

    if is_confirmation_brief_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="confirmation_brief",
            confidence="high",
            route_reason="用户在询问当前是否卡在自己确认上，需要读取当前任务记录并输出确认事项说明，而不是进入泛化执行计划或需求澄清",
            internal_entry="nontechnical_confirmation_brief.user",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会读取当前任务记录，用人话说明现在是否等你确认、需要确认什么、你可以怎么回复和 Codex 下一步。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "confirmation_brief"),
        )

    if is_confirmation_response_request(raw):
        high_risk_confirmation = is_high_risk_authorization_text(raw)
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="confirmation_response",
            confidence="high",
            route_reason="用户给出简短确认；低风险确认可继续本地推进，但不能把它当成真实数据、生产、数据库、撤销、删除或代码提交流程授权",
            internal_entry="nontechnical_confirmation_response.user",
            can_continue=True,
            needs_user_confirmation=high_risk_confirmation,
            user_next_step=(
                "Codex 会把这句话当成确认回复和低风险继续确认，在当前任务范围内继续本地推进；高风险动作仍需单独授权。"
                if not high_risk_confirmation
                else "Codex 会把这句话当成含高风险语义的确认回复，先说明还需要明确哪些授权范围。"
            ),
            user_question=(
                ""
                if not high_risk_confirmation
                else "请补充确认范围；如果只是允许低风险整理，可以说“不操作真实数据、不写数据库、不发布、不提交”。"
            ),
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "confirmation_response"),
        )

    if is_pause_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="pause_current_task",
            confidence="high",
            route_reason="用户在要求暂停当前推进，需要输出暂停说明和恢复方式，而不是切换协作模式、继续推进或重新澄清需求",
            internal_entry="nontechnical_pause.user",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会按暂停当前推进处理，说明当前任务、暂停后不会继续做什么、保留了什么和之后怎么恢复。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "pause_current_task"),
        )

    if is_undo_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="undo_request",
            confidence="high",
            route_reason="用户在要求撤销、回滚或恢复到之前，需要先确认撤销范围和授权，而不是自动删除、reset、回滚或普通暂停",
            internal_entry="nontechnical_undo_request.user",
            can_continue=True,
            needs_user_confirmation=True,
            user_next_step="Codex 会把这句话当成撤销 / 回滚请求，先说明需要确认的范围、能安全查看什么，以及不会直接删除或回滚任何改动。",
            user_question="请说明要撤销哪一部分；如果只是先看撤销方案，可以说“只先给撤销计划，不改文件”。",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "undo_request"),
        )

    if is_mode_control_request(raw):
        choice_only = is_mode_choice_only_request(raw)
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="mode_control",
            confidence="high",
            route_reason="用户在控制或询问本次 Codex 协作模式，需要先解释执行方式，而不是当成普通需求澄清或继续推进",
            internal_entry="nontechnical_mode_control.user",
            can_continue=True,
            needs_user_confirmation=choice_only,
            user_next_step="Codex 会先说明当前协作模式、本次怎么执行、需要你确认什么、以及这次不会做什么。",
            user_question="请选择自主执行、关键确认或手动控制。" if choice_only else "",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "mode_control"),
        )

    if is_first_use_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="first_use_guide",
            confidence="high",
            route_reason="用户在询问第一次使用项目骨架或不会写代码时如何从想法开始，需要给出新手路径，而不是普通推荐或泛化澄清",
            internal_entry="nontechnical_first_use.user",
            can_continue=True,
            needs_user_confirmation=True,
            user_next_step="Codex 会先给出从想法到开工的新手路径、现在只要发什么、下一步怎么拆和不会执行的高风险动作。",
            user_question="你可以先发一句业务目标，或照填新手模板。",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "first_use_guide"),
        )

    if is_recommendation_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="recommendation",
            confidence="high",
            route_reason="用户要求 Codex 推荐方案或第一步，需要给出推荐、取舍和第一安全步，而不是让用户选择技术实现",
            internal_entry="nontechnical_recommendation.user",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会先给出推荐方案、为什么推荐、暂不选择什么、第一安全步和是否需要确认。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "recommendation"),
        )

    if is_scope_change_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="scope_change",
            confidence="high",
            route_reason="用户在调整已有需求范围，需要先说明保留、排除和后续范围，而不是当成新需求澄清或真实数据风险暂停",
            internal_entry="nontechnical_scope_change.user",
            can_continue=True,
            needs_user_confirmation=has_any(raw, "可以动", "商品审核可以动", "刚才说的不对"),
            user_next_step="Codex 会按需求范围调整处理，先说明这次保留什么、先不做什么、后续再做什么和是否需要确认。",
            user_question="如果要放开之前禁止的业务范围，需要确认这个新范围确实覆盖当前任务。" if has_any(raw, "可以动", "商品审核可以动", "刚才说的不对") else "",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "scope_change"),
        )

    if is_page_change_brief_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="page_change_brief",
            confidence="high",
            route_reason="用户在询问改已有页面需要提供什么信息，需要给出照填信息卡，而不是当成普通模糊需求澄清",
            internal_entry="nontechnical_page_change_brief.user",
            can_continue=True,
            needs_user_confirmation=True,
            user_next_step="Codex 会先给出改已有页面需要提供的信息清单、照填模板、例子和不会执行的高风险动作。",
            user_question="把页面位置、现在的问题、希望改成什么、怎么验收和本次不要碰什么发给我即可。",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "page_change_brief"),
        )

    if is_requirement_readiness_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="requirement_readiness",
            confidence="high",
            route_reason="用户在要求检查需求描述是否完整或是否足够开工，需要输出完整度检查和缺失项，而不是只追问一个泛化问题",
            internal_entry="nontechnical_requirement_readiness.user",
            can_continue=True,
            needs_user_confirmation=True,
            user_next_step="Codex 会先检查需求信息完整度，说明已具备信息、优先缺失项、风险确认和下一步。",
            user_question="如果输出仍提示缺失，请补充最关键的 1-3 项即可。",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "requirement_readiness"),
        )

    if is_ui_optimization_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="ui_optimization_kickoff",
            confidence="high",
            route_reason="用户在用短句要求 UI 优化，需要自动进入 UI 设计梳理、实现、视觉复核和浏览器验收链路，而不是要求用户手动说内部流程",
            internal_entry="kk-task-kickoff.ui-optimization -> kk-ui-design-kickoff -> kk-ui-polish-review -> browser-qa",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会把它当成用户可见界面优化任务：先识别页面和目标用户，做 UI 设计梳理，再实现视觉、布局、信息层级、状态和响应式优化，最后做视觉复核和浏览器验收。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface="用户可见页面能力",
            acceptance_focus=acceptance_focus_for(summary, "ui_optimization_kickoff"),
        )

    if is_requirement_brief_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="requirement_brief",
            confidence="high",
            route_reason="用户在要求需求描述模板或开工前信息清单，需要给出通用照填信息卡，而不是只追问一个问题",
            internal_entry="nontechnical_requirement_brief.user",
            can_continue=True,
            needs_user_confirmation=True,
            user_next_step="Codex 会先给出通用需求信息清单、照填模板、例子和不会执行的高风险动作。",
            user_question="你可以先按模板补充已知信息；只知道一部分也可以先发。",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "requirement_brief"),
        )

    if has_any(raw, "检查非技术开发关键路径", "非技术开发关键路径", "自然语言开发能力有没有退化", "关键路径有没有退化"):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="natural_language_smoke",
            confidence="high",
            route_reason="用户在检查自然语言开发关键路径是否健康",
            internal_entry="natural_language_dev_smoke.user",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会检查非技术开发关键路径，并用人话说明是否通过、覆盖了什么、是否需要你确认。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "natural_language_smoke"),
        )

    if is_ci_failure_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="ci_failure_explain",
            confidence="high",
            route_reason="用户在反馈 GitHub / CI / PR 检查失败，需要 CI 失败解释而不是本地 doctor",
            internal_entry="nontechnical_ci_failure.user",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会先识别失败检查类型，再说明会排查哪一块；如果本地看不到日志，会请你提供失败检查名或报错前几行。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "ci_failure_explain"),
        )

    if has_any(raw, "出错了", "报错", "失败了", "门禁失败", "下一步怎么办", "怎么继续", "继续不了"):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="error_recovery",
            confidence="high",
            route_reason="用户在询问出错后的恢复路径",
            internal_entry="gstack_doctor.explain",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会先检查本地协作状态，再说明哪些可以自动修、哪些需要你确认。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "error_recovery"),
        )

    if is_visible_change_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="visible_change_troubleshoot",
            confidence="high",
            route_reason="用户在反馈页面刷新后仍看不到变化，需要可见变化排查而不是新需求澄清",
            internal_entry="nontechnical_visible_change.user",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会先检查当前任务记录里的查看位置、刷新方式和看不到变化时的排查路径。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "visible_change_troubleshoot"),
        )

    if is_continue_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="continue_current_task",
            confidence="high",
            route_reason="用户在已有上下文中要求继续推进，需要读取当前任务状态，而不是重新当成新需求澄清",
            internal_entry="nontechnical_continue.user",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会按继续推进处理，先读取当前任务状态，再说明下一步和是否需要你确认。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "continue_current_task"),
        )

    if is_team_sync_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="team_sync_explain",
            confidence="high",
            route_reason="用户在询问团队任务状态同步，需要先解释无数据库路线的能力边界，而不是泛化成数据库风险暂停",
            internal_entry="nontechnical_team_sync.user",
            can_continue=False,
            needs_user_confirmation=True,
            user_next_step="Codex 会先说明无数据库团队同步能做什么、不能做什么，并确认你是否接受 repo evidence 只读生成视图。",
            user_question="你是否接受这种无数据库的 repo evidence 只读生成视图？",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "team_sync_explain"),
        )

    if is_delivery_summary_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="delivery_summary",
            confidence="high",
            route_reason="用户在要求给团队看的完成说明，需要读取当前任务记录生成交付总结，而不是当成新需求验收计划",
            internal_entry="nontechnical_delivery_summary.user",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会把当前任务记录转成可给团队看的交付总结，说明改了什么、怎么验收、风险和未做事项，以及下一步建议。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "delivery_summary"),
        )

    if is_task_list_request(raw):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="task_list_explain",
            confidence="high",
            route_reason="用户在要求查看历史需求、任务清单或未完成任务，需要读取任务记录生成概览，而不是当成新需求澄清",
            internal_entry="nontechnical_task_list.user",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会读取当前本机仓库已有任务记录，并用人话列出未完成任务、卡住任务和建议下一步。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "task_list_explain"),
        )

    if is_execution_plan_request(raw):
        if summary.risks and summary.risk_confirmation_status != "safe-to-draft":
            return IntentRoute(
                raw_request=summary.raw_request,
                intent="execution_plan",
                confidence="high",
                route_reason="用户在询问推进计划，但需求含高风险信号，需要先输出受控计划和确认点",
                internal_entry="nontechnical_execution_plan.user",
                can_continue=False,
                needs_user_confirmation=True,
                user_next_step="Codex 会先说明受控推进计划和需要你确认的风险点，不执行高风险动作。",
                user_question=summary.suggested_question,
                risk_status=summary.risk_confirmation_status,
                complexity=summary.complexity,
                likely_surface=summary.likely_surface,
                acceptance_focus=acceptance_focus_for(summary, "execution_plan"),
            )
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="execution_plan",
            confidence="high",
            route_reason="用户在询问需求会如何推进或需要什么执行计划",
            internal_entry="nontechnical_execution_plan.user",
            can_continue=summary.can_continue,
            needs_user_confirmation=not summary.can_continue,
            user_next_step="Codex 会用人话说明推进顺序、自动处理事项、需要你确认的点和最终验收方式。",
            user_question="" if summary.can_continue else summary.suggested_question,
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "execution_plan"),
        )

    if has_any(raw, "现在做到哪", "做到哪一步", "当前进度", "进度怎么样", "完成了吗", "卡住了吗", "现在状态", "做完了吗"):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="progress_status",
            confidence="high",
            route_reason="用户在询问当前任务进度或是否卡住",
            internal_entry="gstack_dashboard.explain",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会读取当前任务记录，并用人话说明做到哪一步、是否卡住、下一步是什么。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "progress_status"),
        )

    if is_acceptance_plan_request(raw, summary):
        if summary.risks and summary.risk_confirmation_status != "safe-to-draft":
            return IntentRoute(
                raw_request=summary.raw_request,
                intent="acceptance_plan",
                confidence="high",
                route_reason="用户在询问具体需求的验收方式，但需求含高风险信号，需要先暂停确认",
                internal_entry="nontechnical_acceptance_plan.user",
                can_continue=False,
                needs_user_confirmation=True,
                user_next_step="Codex 会先说明该需求的验收风险和需要你确认的问题，不执行高风险动作。",
                user_question=summary.suggested_question,
                risk_status=summary.risk_confirmation_status,
                complexity=summary.complexity,
                likely_surface=summary.likely_surface,
                acceptance_focus=acceptance_focus_for(summary, "acceptance_plan"),
            )
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="acceptance_plan",
            confidence="high",
            route_reason="用户在询问某个具体需求应该如何验收",
            internal_entry="nontechnical_acceptance_plan.user",
            can_continue=summary.can_continue,
            needs_user_confirmation=not summary.can_continue,
            user_next_step="Codex 会围绕这个需求生成验收清单、实际操作、预期结果、需要确认的点和风险说明。",
            user_question="" if summary.can_continue else summary.suggested_question,
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "acceptance_plan"),
        )

    if has_any(raw, "怎么验收", "如何验收", "怎么知道它真的好了", "怎么知道真的好了", "做完以后我怎么知道", "我怎么知道它好了", "我怎么知道真的好了"):
        return IntentRoute(
            raw_request=summary.raw_request,
            intent="completion_verify",
            confidence="high",
            route_reason="用户在询问完成后的验收方式",
            internal_entry="gstack_dashboard.verify",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会读取当前任务验收记录，并说明看哪里、做什么、预期看到什么。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "completion_verify"),
        )

    return None


def route_request(summary: IntakeSummary) -> IntentRoute:
    raw = summary.raw_request
    if summary.risks and summary.risk_confirmation_status != "safe-to-draft":
        return IntentRoute(
            raw_request=raw,
            intent="risk_confirmation",
            confidence="high",
            route_reason="需求命中真实数据、生产、数据库、破坏性命令或代码提交流程风险",
            internal_entry="nontechnical_intake.risk_pause",
            can_continue=False,
            needs_user_confirmation=True,
            user_next_step="Codex 会先暂停高风险动作，只问一个范围和授权问题。",
            user_question=summary.suggested_question,
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "risk_confirmation"),
        )

    if is_formal_kickoff_request(raw) and summary.can_continue:
        return IntentRoute(
            raw_request=raw,
            intent="formal_kickoff_preview",
            confidence="high",
            route_reason="用户明确表达要正式开工或直接推进，且当前信息足够生成正式开工预览",
            internal_entry="nontechnical_formal_kickoff.preview",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会先预览正式开工包，确认任务范围、推进方式和完成后验收方式；写入前仍需要 Codex 完成语义复核。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "formal_kickoff_preview"),
        )

    if summary.risks and summary.risk_confirmation_status == "safe-to-draft":
        return IntentRoute(
            raw_request=raw,
            intent="controlled_starter",
            confidence="high",
            route_reason="需求有高风险信号，但用户给出了只整理 / 只读 / 不写库 / 不发布 / 不提交等安全约束",
            internal_entry="nontechnical_task_starter.controlled",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 可以先整理开发起点、任务范围和验收口径，但不会执行高风险动作。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "controlled_starter"),
        )

    if summary.can_continue and summary.complexity in {"复杂需求", "高风险复杂需求", "中等需求"}:
        return IntentRoute(
            raw_request=raw,
            intent="complex_task_starter",
            confidence="high",
            route_reason="需求信息足够，且包含复杂或多表面交付信号",
            internal_entry="nontechnical_task_starter.preview",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会先把复杂需求拆成开发起点、可交付步骤和验收清单，再进入正式任务。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "complex_task_starter"),
        )

    if summary.can_continue:
        return IntentRoute(
            raw_request=raw,
            intent="task_kickoff",
            confidence="medium",
            route_reason="需求信息足够且未命中高风险或复杂多表面信号",
            internal_entry="tg_task_kickoff.fast_lane_candidate",
            can_continue=True,
            needs_user_confirmation=False,
            user_next_step="Codex 会先建立正式任务范围和验收计划，再做小范围实现。",
            user_question="",
            risk_status=summary.risk_confirmation_status,
            complexity=summary.complexity,
            likely_surface=summary.likely_surface,
            acceptance_focus=acceptance_focus_for(summary, "task_kickoff"),
        )

    return IntentRoute(
        raw_request=raw,
        intent="clarification",
        confidence="medium",
        route_reason="还缺少会影响产品结果、实现表面或风险判断的信息",
        internal_entry="nontechnical_intake.clarify",
        can_continue=False,
        needs_user_confirmation=True,
        user_next_step="Codex 会先问一个最关键的问题，再进入正式任务。",
        user_question=summary.suggested_question,
        risk_status=summary.risk_confirmation_status,
        complexity=summary.complexity,
        likely_surface=summary.likely_surface,
        acceptance_focus=acceptance_focus_for(summary, "clarification"),
    )


def build_route(args: argparse.Namespace) -> IntentRoute:
    summary = build_summary(build_intake_args(args))
    meta_route = route_meta_intent(summary.raw_request, summary)
    if meta_route:
        return meta_route
    return route_request(summary)


def humanize(value: str) -> str:
    replacements = {
        "git workflow action": "代码提交流程",
        "git 操作": "代码提交流程",
        "git": "代码提交流程",
        "DB": "数据库",
        "raw JSON": "内部数据",
        "JSON": "内部数据",
    }
    result = value
    for old, new in replacements.items():
        result = result.replace(old, new)
    result = result.replace("或 代码提交流程", "或代码提交流程")
    return result


def user_text(route: IntentRoute) -> str:
    lines = [
        f"我会这样处理：{humanize(route.user_next_step)}",
    ]
    if route.user_question:
        lines.extend(["", f"需要你确认：{humanize(route.user_question)}"])
    else:
        lines.extend(["", "需要你确认：暂时不需要。"])
    lines.extend(["", "这次不会直接操作真实数据、生产环境、数据库、破坏性命令或代码提交流程。"])
    return "\n".join(lines)


def render_markdown(route: IntentRoute) -> str:
    lines = [
        "# 非技术自然语言意图路由",
        "",
        f"- 用户原话：{route.raw_request}",
        f"- 识别意图：{route.intent}",
        f"- 置信度：{route.confidence}",
        f"- 路由原因：{route.route_reason}",
        f"- 内部入口：{route.internal_entry}",
        f"- 是否可继续：{'是' if route.can_continue else '否'}",
        f"- 是否需要用户确认：{'是' if route.needs_user_confirmation else '否'}",
        f"- 用户下一步说明：{route.user_next_step}",
        f"- 建议追问：{route.user_question or '无'}",
        f"- 风险确认状态：{route.risk_status}",
        f"- 复杂度：{route.complexity}",
        f"- 可能实现表面：{route.likely_surface}",
        "- 验收关注点：",
        *[f"  - {item}" for item in route.acceptance_focus],
    ]
    return "\n".join(lines)


def render_json(route: IntentRoute) -> str:
    return json.dumps(asdict(route), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original plain-language request.")
    parser.add_argument("--audience", default="", help="Optional target user or usage context.")
    parser.add_argument("--success", default="", help="Optional visible success criteria.")
    parser.add_argument("--non-goal", default="", help="Optional explicit non-goals or forbidden scope.")
    parser.add_argument("--risk-confirmation", default="", help="Optional user confirmation that constrains high-risk actions.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    route = build_route(args)
    if args.format == "json":
        print(render_json(route))
    elif args.format == "user":
        print(user_text(route))
    else:
        print(render_markdown(route))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
