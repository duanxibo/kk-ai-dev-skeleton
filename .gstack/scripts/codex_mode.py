#!/usr/bin/env python3
"""Read and write the local KK Dev Skeleton Codex collaboration mode."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_MODE_FILE = REPO_ROOT / ".gstack" / "codex-mode.local.md"
DEFAULT_LABEL = "自主执行"
MODES = {
    "codex-led": {
        "label": "自主执行",
        "description": "你说目标，Codex 做完。",
        "aliases": {
            "自主执行",
            "自主执行模式",
            "全自动",
            "全自动做完",
            "自动执行",
            "codex-led",
            "autopilot",
        },
    },
    "checkpoint": {
        "label": "关键确认",
        "description": "Codex 推进，关键点问你。",
        "aliases": {
            "关键确认",
            "关键确认模式",
            "关键地方问我",
            "重要决策问我",
            "checkpoint",
        },
    },
    "manual": {
        "label": "手动控制",
        "description": "Codex 只分析，你授权才动。",
        "aliases": {
            "手动控制",
            "手动控制模式",
            "先别改代码",
            "只给方案",
            "manual",
        },
    },
}


@dataclass(frozen=True)
class Mode:
    enum: str
    label: str
    description: str
    source: str


def normalize_token(raw: str) -> str:
    return re.sub(r"\s+", "", raw.strip().lower())


def parse_mode(raw: str, *, source: str = "input") -> Mode:
    wanted = normalize_token(raw)
    for enum, spec in MODES.items():
        labels = {str(spec["label"]), enum, *spec["aliases"]}  # type: ignore[arg-type]
        if wanted in {normalize_token(item) for item in labels}:
            return Mode(
                enum=enum,
                label=str(spec["label"]),
                description=str(spec["description"]),
                source=source,
            )
    valid = " / ".join(str(spec["label"]) for spec in MODES.values())
    raise ValueError(f"unknown collaboration mode `{raw}`; choose one of: {valid}")


def read_local_mode() -> Mode | None:
    if not LOCAL_MODE_FILE.exists():
        return None
    text = LOCAL_MODE_FILE.read_text(encoding="utf-8")
    for pattern in (
        r"^\s*-\s*Mode:\s*`?(?P<mode>[^`\n]+)`?\s*$",
        r"^\s*-\s*Internal Enum:\s*`?(?P<mode>[a-z-]+)`?\s*$",
    ):
        match = re.search(pattern, text, flags=re.MULTILINE)
        if match:
            return parse_mode(match.group("mode"), source="local-default")
    return None


def current_mode() -> Mode:
    return read_local_mode() or parse_mode(DEFAULT_LABEL, source="repo-default")


def write_local_mode(mode: Mode) -> None:
    LOCAL_MODE_FILE.write_text(
        "\n".join(
            [
                "# Codex 本机协作模式",
                "",
                "这个文件只保存当前机器 / 当前 worktree 的 Codex 协作偏好。",
                "",
                "它已加入 gitignore，不应提交。",
                "",
                "## Active Mode",
                "",
                f"- Mode: `{mode.label}`",
                f"- Internal Enum: `{mode.enum}`",
                f"- Description: {mode.description}",
                "",
            ]
        ),
        encoding="utf-8",
    )


def mode_payload(mode: Mode) -> dict[str, str]:
    return {
        "mode": mode.label,
        "internal_enum": mode.enum,
        "description": mode.description,
        "source": mode.source,
        "local_file": LOCAL_MODE_FILE.relative_to(REPO_ROOT).as_posix(),
    }


def print_mode(mode: Mode, *, output_format: str) -> None:
    payload = mode_payload(mode)
    if output_format == "json":
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return
    if output_format == "plain":
        print(f"{payload['mode']} ({payload['internal_enum']}) - {payload['description']}")
        return
    print(
        "\n".join(
            [
                f"- Mode: `{payload['mode']}`",
                f"- Internal Enum: `{payload['internal_enum']}`",
                f"- Source: `{payload['source']}`",
                f"- Description: {payload['description']}",
            ]
        )
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    show = subparsers.add_parser("show", help="Show the active collaboration mode.")
    show.add_argument("--format", choices=("markdown", "plain", "json"), default="markdown")

    parse = subparsers.add_parser("parse", help="Parse a mode alias without writing local state.")
    parse.add_argument("mode")
    parse.add_argument("--format", choices=("markdown", "plain", "json"), default="markdown")

    set_mode = subparsers.add_parser("set", help="Set the local default collaboration mode.")
    set_mode.add_argument("mode")
    set_mode.add_argument("--format", choices=("markdown", "plain", "json"), default="markdown")

    clear = subparsers.add_parser("clear", help="Clear the local mode and return to repo default.")
    clear.add_argument("--format", choices=("markdown", "plain", "json"), default="markdown")

    choices = subparsers.add_parser("choices", help="List available collaboration modes.")
    choices.add_argument("--format", choices=("markdown", "plain", "json"), default="markdown")
    return parser


def list_choices(*, output_format: str) -> None:
    modes = [
        {
            "mode": str(spec["label"]),
            "internal_enum": enum,
            "description": str(spec["description"]),
        }
        for enum, spec in MODES.items()
    ]
    if output_format == "json":
        print(json.dumps(modes, ensure_ascii=False, indent=2))
        return
    if output_format == "plain":
        for mode in modes:
            print(f"{mode['mode']} ({mode['internal_enum']}) - {mode['description']}")
        return
    for mode in modes:
        print(f"- `{mode['mode']}`: {mode['description']}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "show":
            print_mode(current_mode(), output_format=args.format)
            return 0
        if args.command == "parse":
            print_mode(parse_mode(args.mode), output_format=args.format)
            return 0
        if args.command == "set":
            mode = parse_mode(args.mode, source="local-default")
            write_local_mode(mode)
            print_mode(mode, output_format=args.format)
            return 0
        if args.command == "clear":
            if LOCAL_MODE_FILE.exists():
                LOCAL_MODE_FILE.unlink()
            print_mode(current_mode(), output_format=args.format)
            return 0
        if args.command == "choices":
            list_choices(output_format=args.format)
            return 0
    except ValueError as exc:
        print(f"[codex-mode] {exc}", file=sys.stderr)
        return 2
    parser.error("unhandled command")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
