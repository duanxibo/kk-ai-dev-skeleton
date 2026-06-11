#!/usr/bin/env python3
"""Explain natural-language Codex collaboration mode requests.

This helper is deterministic and read-only. It recognizes phrases such as
"先别改代码", "关键地方问我", and "全自动做完", then produces a plain
user-facing explanation of how Codex should behave for this request. It does
not write .gstack/codex-mode.local.md, create evidence, touch secrets, run git
actions, connect to data sources, or operate on production systems.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass


MODE_SPECS = {
    "codex-led": {
        "label": "自主执行",
        "description": "你说目标，Codex 做完。",
        "keywords": (
            "自主执行",
            "自主执行模式",
            "全自动做完",
            "全自动",
            "自动执行",
            "你自己决定并做完",
            "你自己看着办并做完",
            "你来决定并做完",
        ),
    },
    "checkpoint": {
        "label": "关键确认",
        "description": "Codex 推进，关键点问你。",
        "keywords": (
            "关键确认",
            "关键确认模式",
            "关键地方问我",
            "关键点问我",
            "重要决策问我",
            "重要地方问我",
            "实现前让我确认",
            "其他你继续推进",
        ),
    },
    "manual": {
        "label": "手动控制",
        "description": "Codex 只分析，你授权才动。",
        "keywords": (
            "手动控制",
            "手动控制模式",
            "先别改代码",
            "先不要改代码",
            "不要改代码",
            "别改代码",
            "只给方案",
            "只给我方案",
            "先给方案",
            "只分析",
            "不要自动执行",
        ),
    },
}

MODE_QUERY_KEYWORDS = (
    "协作模式",
    "现在是什么模式",
    "当前是什么模式",
    "现在是什么协作模式",
    "模式怎么选",
    "协作模式怎么选",
    "切换协作模式",
    "有哪些协作模式",
)

LOCAL_DEFAULT_KEYWORDS = (
    "以后默认",
    "以后都",
    "以后",
    "默认用",
    "默认",
    "长期",
    "切换到",
)

CURRENT_TASK_KEYWORDS = (
    "这次",
    "本次",
    "这轮",
    "当前任务",
    "当前这个任务",
)

HIGH_RISK_NON_ACTIONS = [
    "不会连接真实数据或外部数据源。",
    "不会操作生产环境。",
    "不会写入或变更数据库。",
    "不会执行破坏性命令。",
    "不会执行代码提交流程。",
    "不会清理、删除或改写允许入仓的敏感配置。",
]


@dataclass(frozen=True)
class ModeControlResult:
    raw_request: str
    status: str
    mode: str
    internal_enum: str
    description: str
    scope: str
    writes_local_mode: bool
    needs_user_confirmation: list[str]
    codex_behavior: list[str]
    non_actions: list[str]
    choices: list[str]


def compact(raw: str) -> str:
    return re.sub(r"\s+", " ", raw.strip())


def normalize(raw: str) -> str:
    return re.sub(r"\s+", "", raw.strip().lower())


def has_any(text: str, *keywords: str) -> bool:
    normalized = normalize(text)
    return any(normalize(keyword) in normalized for keyword in keywords)


def detect_mode(raw: str) -> str:
    # More restrictive modes win when a sentence mixes instructions.
    for enum in ("manual", "checkpoint", "codex-led"):
        if has_any(raw, *MODE_SPECS[enum]["keywords"]):
            return enum
    return ""


def is_mode_query(raw: str) -> bool:
    return has_any(raw, *MODE_QUERY_KEYWORDS)


def scope_for(raw: str) -> str:
    if has_any(raw, *LOCAL_DEFAULT_KEYWORDS):
        return "local-default-request"
    if has_any(raw, *CURRENT_TASK_KEYWORDS):
        return "current-task"
    return "current-request"


def choices() -> list[str]:
    return [
        f"{spec['label']}：{spec['description']}"
        for spec in MODE_SPECS.values()
    ]


def behavior_for(enum: str, scope: str) -> list[str]:
    if enum == "manual":
        behavior = [
            "这次我会按手动控制处理。",
            "只做分析、方案和风险说明；没有你明确授权，不改代码、不落长期文档。",
        ]
    elif enum == "checkpoint":
        behavior = [
            "这次我会按关键确认处理。",
            "Codex 可以继续推进，但关键产品口径、真实数据、生产、数据库、破坏性命令或代码提交流程会先问你。",
        ]
    elif enum == "codex-led":
        behavior = [
            "这次我会按自主执行处理。",
            "Codex 会在任务范围内自动拆解、实现、验证和同步必要文档。",
        ]
    else:
        behavior = [
            "我还没有识别到明确模式。",
            "你可以选择自主执行、关键确认或手动控制。",
        ]

    if scope == "local-default-request":
        behavior.append("你像是在要求切换以后默认模式；这个说明 helper 只读，不会写本机默认模式。")
    return behavior


def confirmations_for(enum: str, scope: str) -> list[str]:
    if enum == "manual":
        confirmations = [
            "如果要我进入实现、修改文件或写长期记录，需要你明确授权。",
        ]
    elif enum == "checkpoint":
        confirmations = [
            "关键产品口径、真实数据权限、生产操作、数据库变更、破坏性命令或代码提交流程需要你确认。",
        ]
    elif enum == "codex-led":
        confirmations = [
            "只有真实数据、生产环境、数据库、破坏性命令、代码提交流程或长期默认模式切换需要你确认。",
        ]
    else:
        confirmations = [
            "请回复一个模式名：自主执行、关键确认或手动控制。",
        ]

    if scope == "local-default-request":
        confirmations.append("如果要把它设成以后默认，需要你明确授权写入本机偏好。")
    return confirmations


def build_result(args: argparse.Namespace) -> ModeControlResult:
    raw = compact(args.raw)
    enum = detect_mode(raw)
    scope = scope_for(raw)

    if enum:
        spec = MODE_SPECS[enum]
        return ModeControlResult(
            raw_request=raw,
            status="mode-recognized",
            mode=str(spec["label"]),
            internal_enum=enum,
            description=str(spec["description"]),
            scope=scope,
            writes_local_mode=False,
            needs_user_confirmation=confirmations_for(enum, scope),
            codex_behavior=behavior_for(enum, scope),
            non_actions=HIGH_RISK_NON_ACTIONS,
            choices=choices(),
        )

    status = "mode-choice-needed" if is_mode_query(raw) else "not-mode-control"
    return ModeControlResult(
        raw_request=raw,
        status=status,
        mode="",
        internal_enum="",
        description="",
        scope=scope,
        writes_local_mode=False,
        needs_user_confirmation=confirmations_for("", scope),
        codex_behavior=behavior_for("", scope),
        non_actions=HIGH_RISK_NON_ACTIONS,
        choices=choices(),
    )


def render_user(result: ModeControlResult) -> str:
    lines: list[str] = ["当前协作模式：" + (result.mode or "需要你选择")]
    if result.mode:
        lines.append(f"模式含义：{result.description}")
    else:
        lines.extend(["", "可选协作模式：", *[f"- {choice}" for choice in result.choices]])

    lines.extend(["", "这次怎么执行：", *[f"- {item}" for item in result.codex_behavior]])
    lines.extend(["", "需要你确认：", *[f"- {item}" for item in result.needs_user_confirmation]])
    lines.extend(["", "这次不会做什么：", *[f"- {item}" for item in result.non_actions]])
    return "\n".join(lines)


def render_markdown(result: ModeControlResult) -> str:
    lines = [
        "# 非技术协作模式说明",
        "",
        f"- 用户原话：{result.raw_request}",
        f"- 状态：{result.status}",
        f"- 模式：{result.mode or '未指定'}",
        f"- 内部枚举：{result.internal_enum or '未指定'}",
        f"- 作用范围：{result.scope}",
        f"- 是否写本机默认模式：{'是' if result.writes_local_mode else '否'}",
        "- Codex 行为：",
        *[f"  - {item}" for item in result.codex_behavior],
        "- 需要用户确认：",
        *[f"  - {item}" for item in result.needs_user_confirmation],
        "- 不会执行：",
        *[f"  - {item}" for item in result.non_actions],
    ]
    return "\n".join(lines)


def render_json(result: ModeControlResult) -> str:
    return json.dumps(asdict(result), ensure_ascii=False, indent=2)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw", required=True, help="User's original plain-language request.")
    parser.add_argument("--format", choices=("markdown", "json", "user"), default="markdown")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    result = build_result(args)
    if args.format == "json":
        print(render_json(result))
    elif args.format == "user":
        print(render_user(result))
    else:
        print(render_markdown(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
