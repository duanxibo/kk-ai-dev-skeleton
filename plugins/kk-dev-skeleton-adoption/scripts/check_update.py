#!/usr/bin/env python3
"""Non-blocking update checker for the KK Dev Skeleton Adoption plugin."""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


PLUGIN_NAME = "kk-dev-skeleton-adoption"
MARKETPLACE_NAME = "kk-dev-skeleton-internal"
DEFAULT_REMOTE_PLUGIN_JSON = (
    "https://raw.githubusercontent.com/duanxibo/kk-ai-dev-skeleton/"
    "main/plugins/kk-dev-skeleton-adoption/.codex-plugin/plugin.json"
)


def default_plugin_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_local_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def read_remote_json(remote_url: str, timeout: float) -> dict[str, Any]:
    if remote_url.startswith(("http://", "https://")):
        request = urllib.request.Request(
            remote_url,
            headers={"User-Agent": "kk-dev-skeleton-update-check/1.0"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))

    return read_local_json(Path(remote_url))


def load_local_manifest(plugin_root: Path) -> dict[str, Any]:
    manifest_path = plugin_root / ".codex-plugin" / "plugin.json"
    return read_local_json(manifest_path)


def parse_version(value: str) -> tuple[tuple[int, ...], int]:
    base, marker, build = value.partition("+codex.")
    parts: list[int] = []
    for part in base.split("."):
        match = re.match(r"(\d+)", part)
        parts.append(int(match.group(1)) if match else 0)

    while len(parts) < 3:
        parts.append(0)

    build_number = int(build) if marker and build.isdigit() else -1
    return tuple(parts), build_number


def compare_versions(local_version: str, latest_version: str) -> int:
    local = parse_version(local_version)
    latest = parse_version(latest_version)
    if local == latest:
        return 0
    return -1 if local < latest else 1


def build_result(
    *,
    local_manifest: dict[str, Any] | None,
    remote_manifest: dict[str, Any] | None,
    error: str | None,
    remote_url: str,
) -> dict[str, Any]:
    local_version = str(local_manifest.get("version", "")) if local_manifest else ""
    latest_version = str(remote_manifest.get("version", "")) if remote_manifest else ""

    status = "unknown"
    if local_version and latest_version:
        comparison = compare_versions(local_version, latest_version)
        if comparison == 0:
            status = "current"
        elif comparison < 0:
            status = "outdated"
        else:
            status = "ahead"

    return {
        "plugin": PLUGIN_NAME,
        "marketplace": MARKETPLACE_NAME,
        "status": status,
        "local_version": local_version,
        "latest_version": latest_version,
        "remote_url": remote_url,
        "error": error,
        "upgrade_command": f"codex plugin marketplace upgrade {MARKETPLACE_NAME}",
        "install_command": f"codex plugin add {PLUGIN_NAME}@{MARKETPLACE_NAME}",
        "natural_language_prompt": (
            "请刷新 kk-dev-skeleton-internal marketplace，并把 "
            "KK Dev Skeleton Adoption 插件更新到最新版本。"
        ),
    }


def check_update(plugin_root: Path, remote_url: str, timeout: float) -> dict[str, Any]:
    local_manifest: dict[str, Any] | None = None
    remote_manifest: dict[str, Any] | None = None
    error: str | None = None

    try:
        local_manifest = load_local_manifest(plugin_root)
        remote_manifest = read_remote_json(remote_url, timeout)
    except (
        FileNotFoundError,
        json.JSONDecodeError,
        OSError,
        TimeoutError,
        urllib.error.URLError,
        urllib.error.HTTPError,
    ) as exc:
        error = f"{type(exc).__name__}: {exc}"

    return build_result(
        local_manifest=local_manifest,
        remote_manifest=remote_manifest,
        error=error,
        remote_url=remote_url,
    )


def render_text(result: dict[str, Any]) -> str:
    status = result["status"]
    if status == "current":
        return (
            "KK Dev Skeleton 插件已是最新版本："
            f"{result['local_version']}。"
        )

    if status == "outdated":
        return "\n".join(
            [
                "检测到 KK Dev Skeleton 插件有更新。",
                f"- 本地版本：{result['local_version']}",
                f"- 最新版本：{result['latest_version']}",
                "",
                "建议先更新插件，再继续接入或检查项目：",
                f"1. 对 Codex 说：{result['natural_language_prompt']}",
                f"2. 等价命令：{result['upgrade_command']}",
                f"3. 如需重装：{result['install_command']}",
            ]
        )

    if status == "ahead":
        return (
            "本地 KK Dev Skeleton 插件版本高于 GitHub main："
            f"{result['local_version']} > {result['latest_version']}。"
            "这通常表示正在验证尚未发布的版本，不需要提醒伙伴升级。"
        )

    detail = f" 原因：{result['error']}" if result.get("error") else ""
    return (
        "暂时无法检查 KK Dev Skeleton 插件是否有更新；"
        f"不会阻断当前任务。{detail}\n"
        f"如需手动刷新，可执行：{result['upgrade_command']}"
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether the installed KK Dev Skeleton plugin is up to date.",
    )
    parser.add_argument(
        "--plugin-root",
        default=str(default_plugin_root()),
        help="Path to the plugin root. Defaults to the parent of this script directory.",
    )
    parser.add_argument(
        "--remote-url",
        default=DEFAULT_REMOTE_PLUGIN_JSON,
        help="Latest plugin.json URL or local file path.",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=3.0,
        help="Network timeout in seconds.",
    )
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when the plugin is outdated or update status is unknown.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    result = check_update(Path(args.plugin_root), args.remote_url, args.timeout)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(render_text(result))

    if args.strict and result["status"] == "outdated":
        return 20
    if args.strict and result["status"] == "unknown":
        return 21
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
