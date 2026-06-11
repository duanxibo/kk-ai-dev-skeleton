#!/usr/bin/env python3
"""Explain how a nontechnical first-time user can start with this skeleton.

This helper is deterministic and read-only. It does not create formal task
evidence, inspect private pages, connect to data sources, touch databases,
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
class FirstUseGuide:
    raw_request: str
    status: str
    start_path: list[str]
    send_now_template: list[str]
    example_message: str
    codex_next_actions: list[str]
    needs_user_confirmation: list[str]
    non_actions: list[str]


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def build_guide(args: argparse.Namespace) -> FirstUseGuide:
    raw = compact(args.raw)
    return FirstUseGuide(
        raw_request=raw,
        status="first-use-guide-ready",
        start_path=[
            "先用一句话说你想让谁完成什么事，不需要说技术方案。",
            "补一句成功后第一眼应该看到什么，这会变成验收标准。",
            "补一句这次不要碰什么，尤其是真实数据、数据库、生产环境、发布或代码提交流程。",
            "Codex 会把你的话整理成目标、范围、风险和验收方式，再拆成最小可见路径。",
            "信息足够后，你可以继续说“正式开工”；Codex 会先做开工预览和内部检查，不会跳过风险确认。",
        ],
        send_now_template=[
            "我想让谁使用：",
            "他们想完成：",
            "成功后第一眼应该看到：",
            "这次不要碰：",
            "是否涉及真实数据、线上、数据库、发布或代码提交流程：",
            "我会这样验收：",
        ],
        example_message=(
            "我想让运营同事使用。"
            "他们想完成：按月份和 条目 查看项目看板。"
            "成功后第一眼应该看到：一个能筛选月份和 条目 的结果表。"
            "这次不要碰：真实数据、数据库、发布和受限业务模块。"
            "是否涉及真实数据、线上、数据库、发布或代码提交流程：暂时都不涉及，先用假数据。"
            "我会这样验收：输入 条目 后只看到匹配结果。"
        ),
        codex_next_actions=[
            "如果你只发一句想法，Codex 会先问一个最影响结果的问题。",
            "如果你按模板补了几项，Codex 会检查还缺什么。",
            "如果你问“怎么推进”，Codex 会给阶段计划和每阶段验收方式。",
            "如果你确认“正式开工”，Codex 会先预览任务范围、验收方式和风险限制。",
            "如果涉及真实数据、生产、数据库、外部服务或代码提交流程，Codex 会先停下来确认。",
        ],
        needs_user_confirmation=[
            "现在只需要发一句业务目标，或直接照填上面的 6 行模板。",
        ],
        non_actions=NON_ACTIONS,
    )


def render_user(guide: FirstUseGuide) -> str:
    lines = [
        "我会按从想法到开工的新手开始路径处理。",
        "",
        "你可以这样开始：",
        *[f"- {item}" for item in guide.start_path],
        "",
        "现在只要这样发：",
        *[f"- {item}" for item in guide.send_now_template],
        "",
        "例子：",
        f"- {guide.example_message}",
        "",
        "Codex 的下一步：",
        *[f"- {item}" for item in guide.codex_next_actions],
        "",
        "需要你确认：",
        *[f"- {item}" for item in guide.needs_user_confirmation],
        "",
        "这次不会做什么：",
        *[f"- {item}" for item in guide.non_actions],
    ]
    return "\n".join(lines)


def render_markdown(guide: FirstUseGuide) -> str:
    lines = [
        "# 非技术新手开始说明",
        "",
        f"- 用户原话：{guide.raw_request}",
        f"- 状态：{guide.status}",
        "- 新手路径：",
        *[f"  - {item}" for item in guide.start_path],
        "- 现在可发送：",
        *[f"  - {item}" for item in guide.send_now_template],
        f"- 例子：{guide.example_message}",
        "- Codex 下一步：",
        *[f"  - {item}" for item in guide.codex_next_actions],
        "- 需要用户确认：",
        *[f"  - {item}" for item in guide.needs_user_confirmation],
        "- 不会执行：",
        *[f"  - {item}" for item in guide.non_actions],
    ]
    return "\n".join(lines)


def render_json(guide: FirstUseGuide) -> str:
    return json.dumps(asdict(guide), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original plain-language request.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    guide = build_guide(args)
    if args.format == "json":
        print(render_json(guide))
    elif args.format == "user":
        print(render_user(guide))
    else:
        print(render_markdown(guide))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
