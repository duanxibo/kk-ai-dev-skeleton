#!/usr/bin/env python3
"""Give nontechnical users a fill-in brief for describing a new requirement.

This helper is deterministic and read-only. It does not create formal
requirement evidence, inspect code, connect to data sources, touch databases,
operate production systems, or run code workflow actions.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass


NON_ACTIONS = [
    "不会创建正式业务需求或正式任务范围。",
    "不会修改页面、后端、接口或数据模型。",
    "不会连接真实数据或外部数据源。",
    "不会操作生产环境。",
    "不会写入或变更数据库。",
    "不会执行破坏性命令。",
    "不会执行代码提交流程。",
    "不会清理、删除或改写允许入仓的敏感配置。",
]


@dataclass(frozen=True)
class RequirementBrief:
    raw_request: str
    status: str
    brief_fields: list[str]
    fill_in_template: list[str]
    example_message: str
    codex_next_actions: list[str]
    needs_user_confirmation: list[str]
    non_actions: list[str]


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def build_brief(args: argparse.Namespace) -> RequirementBrief:
    raw = compact(args.raw)
    return RequirementBrief(
        raw_request=raw,
        status="ready-to-collect-requirement",
        brief_fields=[
            "谁会用：主要使用者是谁，他们现在在做什么事。",
            "想完成什么：你希望系统帮他们完成哪件具体工作。",
            "现在为什么要改：当前哪里慢、乱、看不懂、容易错，或者必须人工处理。",
            "成功后第一眼看到什么：页面、数据、提示、按钮、导出结果或流程状态应该变成什么样。",
            "用户会怎么操作：从哪里进入、点什么、输入什么、筛选什么、最后看到什么。",
            "数据从哪里来：用假数据、现有页面数据、接口、表格文件、真实数据，还是暂时不接数据。",
            "这次不做什么：哪些页面、模块、导出、权限、真实数据、数据库、生产环境或代码提交流程不要碰。",
            "风险或权限：是否涉及线上环境、数据库、真实数据、外部服务、发布或代码提交流程。",
            "怎么验收：完成后你会用什么步骤判断它真的好了。",
        ],
        fill_in_template=[
            "谁会用：",
            "他们想完成：",
            "现在的问题是：",
            "成功后第一眼应该看到：",
            "用户会这样操作：",
            "数据来源 / 是否接真实数据：",
            "这次不做 / 不要碰：",
            "是否涉及线上、数据库、真实数据、发布或代码提交流程：",
            "我会这样验收：",
        ],
        example_message=(
            "谁会用：运营同事。他们想完成：按月份和 条目 查看经营结果。"
            "现在的问题是：数据分散，筛选和核对很慢。"
            "成功后第一眼应该看到：一个能筛选月份和 条目 的看板。"
            "用户会这样操作：选择月份，搜索 条目，查看表格，再导出结果。"
            "数据来源 / 是否接真实数据：先用假数据，不接真实数据。"
            "这次不做 / 不要碰：不做权限，不碰数据库，不发布。"
            "是否涉及线上、数据库、真实数据、发布或代码提交流程：暂时都不涉及。"
            "我会这样验收：打开页面后能筛选、搜索，并看到符合条件的结果。"
        ),
        codex_next_actions=[
            "你可以直接照填下面模板；如果只知道一部分，也可以先填已知部分。",
            "Codex 会把你填的内容整理成目标、范围、不做事项、验收方式和风险确认点。",
            "如果信息足够，Codex 会继续拆成可交付步骤。",
            "如果还缺关键信息，Codex 只追问一个最影响结果的问题。",
            "如果涉及真实数据、生产环境、数据库、外部服务或代码提交流程，Codex 会先停下来确认。",
        ],
        needs_user_confirmation=[
            "暂时不需要；你可以先按模板补充信息。",
        ],
        non_actions=NON_ACTIONS,
    )


def render_user(brief: RequirementBrief) -> str:
    lines = [
        "你可以这样描述需求。",
        "",
        "请尽量说明：",
        *[f"- {item}" for item in brief.brief_fields],
        "",
        "照填模板：",
        *[f"- {item}" for item in brief.fill_in_template],
        "",
        "例子：",
        f"- {brief.example_message}",
        "",
        "Codex 的下一步：",
        *[f"- {item}" for item in brief.codex_next_actions],
        "",
        "需要你确认：",
        *[f"- {item}" for item in brief.needs_user_confirmation],
        "",
        "这次不会做什么：",
        *[f"- {item}" for item in brief.non_actions],
    ]
    return "\n".join(lines)


def render_markdown(brief: RequirementBrief) -> str:
    lines = [
        "# 非技术通用需求信息卡",
        "",
        f"- 用户原话：{brief.raw_request}",
        f"- 状态：{brief.status}",
        "- 建议说明：",
        *[f"  - {item}" for item in brief.brief_fields],
        "- 照填模板：",
        *[f"  - {item}" for item in brief.fill_in_template],
        f"- 例子：{brief.example_message}",
        "- Codex 下一步：",
        *[f"  - {item}" for item in brief.codex_next_actions],
        "- 需要用户确认：",
        *[f"  - {item}" for item in brief.needs_user_confirmation],
        "- 不会执行：",
        *[f"  - {item}" for item in brief.non_actions],
    ]
    return "\n".join(lines)


def render_json(brief: RequirementBrief) -> str:
    return json.dumps(asdict(brief), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original plain-language request.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    brief = build_brief(args)
    if args.format == "json":
        print(render_json(brief))
    elif args.format == "user":
        print(render_user(brief))
    else:
        print(render_markdown(brief))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
