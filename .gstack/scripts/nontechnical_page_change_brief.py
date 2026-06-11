#!/usr/bin/env python3
"""Give nontechnical users a fill-in brief for changing an existing page.

This helper is deterministic and read-only. It does not inspect the page,
open browsers, create formal evidence, connect to data sources, touch
databases, operate production systems, or run code workflow actions.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass


NON_ACTIONS = [
    "不会连接真实数据或外部数据源。",
    "不会操作生产环境。",
    "不会写入或变更数据库。",
    "不会执行破坏性命令。",
    "不会执行代码提交流程。",
    "不会清理、删除或改写允许入仓的敏感配置。",
]


@dataclass(frozen=True)
class PageChangeBrief:
    raw_request: str
    status: str
    what_to_send: list[str]
    fill_in_template: list[str]
    example_message: str
    codex_next_actions: list[str]
    needs_user_confirmation: list[str]
    non_actions: list[str]


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def build_brief(args: argparse.Namespace) -> PageChangeBrief:
    raw = compact(args.raw)
    return PageChangeBrief(
        raw_request=raw,
        status="page-change-brief-ready",
        what_to_send=[
            "页面位置：页面名称、链接、截图，或者从哪里点进去。",
            "现在看到的问题：哪里不好用、看不懂、找不到、点了没反应，或者结果不符合预期。",
            "你希望变成什么：想新增、隐藏、移动、改文案、改筛选、改表格、改按钮，还是改流程。",
            "完成后怎么验收：你会点哪里、输入什么、预期看到什么结果。",
            "本次不要碰什么：哪些页面、数据、权限、导出、真实数据、生产环境或数据库不要动。",
        ],
        fill_in_template=[
            "我要改的页面是：",
            "现在的问题是：",
            "我希望改成：",
            "我会这样验收：",
            "这次不要碰：",
        ],
        example_message=(
            "我要改的页面是：项目看板的条目筛选区域。现在的问题是：条目 太多时不好找。"
            "我希望改成：可以输入关键词过滤。"
            "我会这样验收：输入“钢琴”后只看到钢琴相关 条目。"
            "这次不要碰：真实数据、导出和数据库。"
        ),
        codex_next_actions=[
            "先把你发来的自然语言整理成页面改动目标、范围和验收方式。",
            "如果信息足够，再进入正式任务边界和验证计划。",
            "如果还缺关键信息，只追问一个最影响结果的问题。",
            "如果涉及真实数据、生产环境、数据库或代码提交流程，会单独暂停确认。",
        ],
        needs_user_confirmation=[
            "把页面位置、现在的问题、希望改成什么、怎么验收和本次不要碰什么发给我即可。",
        ],
        non_actions=NON_ACTIONS,
    )


def render_user(brief: PageChangeBrief) -> str:
    lines = [
        "你不用懂技术，改已有页面先给我这几项就够了。",
        "",
        "请尽量提供：",
        *[f"- {item}" for item in brief.what_to_send],
        "",
        "可以直接照这个格式发：",
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


def render_markdown(brief: PageChangeBrief) -> str:
    lines = [
        "# 非技术已有页面改动信息卡",
        "",
        f"- 用户原话：{brief.raw_request}",
        f"- 状态：{brief.status}",
        "- 建议提供：",
        *[f"  - {item}" for item in brief.what_to_send],
        "- 照填格式：",
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


def render_json(brief: PageChangeBrief) -> str:
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
