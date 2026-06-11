#!/usr/bin/env python3
"""Manage KK Dev Skeleton gstack rules and pitfalls.

Supported commands:
- lint: validate metadata, ids, and dates
- match: print rules matching tags, optionally touching last_hit
- touch: update last_hit for a specific rule id
- archive-stale: move old entries into rules/archive
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RULE_GLOBS = [
    ".gstack/rules/*.md",
    ".gstack/knowledge/pitfalls/*.md",
]
ARCHIVE_DIR = ROOT / ".gstack" / "rules" / "archive"
ENTRY_SPLIT_RE = re.compile(r"(?=^##\s+)", re.MULTILINE)
META_RE = re.compile(r"^- ([a-zA-Z0-9_]+):\s*(.*)$")


@dataclass
class Entry:
    file_path: Path
    header: str
    title: str
    rule_id: str
    metadata: dict[str, str]
    body: str

    @property
    def tags(self) -> set[str]:
        raw = self.metadata.get("tags", "")
        tags = re.findall(r"`([^`]+)`", raw)
        if tags:
            return {tag.strip().lower() for tag in tags if tag.strip()}
        return {
            tag.strip().lower()
            for tag in raw.split(",")
            if tag.strip()
        }

    @property
    def last_hit(self) -> date | None:
        raw = self.metadata.get("last_hit", "").strip().strip("`")
        if not raw:
            return None
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            return None

    def section_text(self) -> str:
        return f"{self.header}\n\n{self.body.strip()}\n"


def default_files() -> list[Path]:
    files: list[Path] = []
    for pattern in DEFAULT_RULE_GLOBS:
        files.extend(sorted(ROOT.glob(pattern)))
    return [path for path in files if path.is_file()]


def parse_entries(file_path: Path) -> list[Entry]:
    text = file_path.read_text(encoding="utf-8")
    pieces = ENTRY_SPLIT_RE.split(text)
    entries: list[Entry] = []
    for piece in pieces:
        stripped = piece.strip()
        if not stripped.startswith("## "):
            continue
        lines = stripped.splitlines()
        header = lines[0].strip()
        body_lines = lines[1:]
        metadata: dict[str, str] = {}
        for line in body_lines:
            match = META_RE.match(line.strip())
            if match:
                metadata[match.group(1)] = match.group(2).strip()
        title = header.removeprefix("## ").strip()
        rule_id = title.split(" - ", 1)[0].strip()
        entries.append(
            Entry(
                file_path=file_path,
                header=header,
                title=title,
                rule_id=rule_id,
                metadata=metadata,
                body="\n".join(body_lines).rstrip(),
            )
        )
    return entries


def read_file_header(file_path: Path) -> str:
    lines = file_path.read_text(encoding="utf-8").splitlines()
    header_lines: list[str] = []
    for line in lines:
        if line.startswith("## "):
            break
        header_lines.append(line)
    return "\n".join(header_lines).rstrip() + "\n"


def write_entries(file_path: Path, file_header: str, entries: Iterable[Entry]) -> None:
    content = file_header.rstrip() + "\n\n"
    sections = [entry.section_text().rstrip() for entry in entries]
    if sections:
        content += "\n\n".join(sections) + "\n"
    file_path.write_text(content, encoding="utf-8")


def print_match(entries: list[Entry]) -> None:
    if not entries:
        print("No matching entries.")
        return
    for entry in entries:
        tags = ", ".join(sorted(entry.tags))
        applies = entry.metadata.get("applies_when", "")
        print(f"{entry.rule_id}\t{entry.file_path.relative_to(ROOT)}")
        print(f"  title: {entry.title}")
        print(f"  tags: {tags or '-'}")
        if applies:
            print(f"  applies_when: {applies}")


def lint(files: list[Path]) -> int:
    errors: list[str] = []
    seen_ids: dict[str, Path] = {}
    seen_titles: dict[str, Path] = {}
    required_keys = {"status", "tags", "last_hit"}

    for file_path in files:
        for entry in parse_entries(file_path):
            for key in required_keys:
                if key not in entry.metadata or not entry.metadata[key].strip():
                    errors.append(f"{file_path.relative_to(ROOT)} {entry.rule_id}: missing `{key}`")
            if entry.last_hit is None:
                errors.append(f"{file_path.relative_to(ROOT)} {entry.rule_id}: invalid `last_hit`")
            if entry.rule_id in seen_ids:
                errors.append(
                    f"duplicate id `{entry.rule_id}` in "
                    f"{file_path.relative_to(ROOT)} and {seen_ids[entry.rule_id].relative_to(ROOT)}"
                )
            else:
                seen_ids[entry.rule_id] = file_path
            lowered_title = entry.title.lower()
            if lowered_title in seen_titles:
                errors.append(
                    f"duplicate title `{entry.title}` in "
                    f"{file_path.relative_to(ROOT)} and {seen_titles[lowered_title].relative_to(ROOT)}"
                )
            else:
                seen_titles[lowered_title] = file_path

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"Lint passed for {len(files)} files.")
    return 0


def touch_rule(rule_id: str, files: list[Path], target_date: date) -> int:
    for file_path in files:
        entries = parse_entries(file_path)
        touched = False
        for entry in entries:
            if entry.rule_id == rule_id:
                entry.metadata["last_hit"] = target_date.isoformat()
                touched = True
                body_lines = entry.body.splitlines()
                updated_lines = []
                replaced = False
                for line in body_lines:
                    if line.startswith("- last_hit:"):
                        updated_lines.append(f"- last_hit: `{target_date.isoformat()}`")
                        replaced = True
                    else:
                        updated_lines.append(line)
                if not replaced:
                    updated_lines.insert(0, f"- last_hit: `{target_date.isoformat()}`")
                entry.body = "\n".join(updated_lines)
                break
        if touched:
            write_entries(file_path, read_file_header(file_path), entries)
            print(f"Touched {rule_id} in {file_path.relative_to(ROOT)}")
            return 0
    print(f"Rule id not found: {rule_id}", file=sys.stderr)
    return 1


def match_tags(tag_query: set[str], files: list[Path], touch: bool, target_date: date) -> int:
    matched_entries: list[Entry] = []
    matched_ids: list[str] = []
    for file_path in files:
        entries = parse_entries(file_path)
        for entry in entries:
            if tag_query & entry.tags:
                matched_entries.append(entry)
                matched_ids.append(entry.rule_id)
    print_match(matched_entries)
    if touch:
        for rule_id in matched_ids:
            touch_rule(rule_id, files, target_date)
    return 0


def ensure_archive_header(file_path: Path, source_file: Path) -> str:
    if file_path.exists():
        return read_file_header(file_path)
    return (
        f"# Archived from {source_file.relative_to(ROOT)}\n\n"
        "These entries were auto-archived because `last_hit` exceeded the stale threshold.\n"
    )


def archive_stale(files: list[Path], months: int, today: date) -> int:
    cutoff = today - timedelta(days=months * 30)
    moved_total = 0
    ARCHIVE_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in files:
        if ARCHIVE_DIR in file_path.parents:
            continue
        entries = parse_entries(file_path)
        active_entries: list[Entry] = []
        stale_entries: list[Entry] = []
        for entry in entries:
            if entry.last_hit is not None and entry.last_hit < cutoff:
                stale_entries.append(entry)
            else:
                active_entries.append(entry)
        if not stale_entries:
            continue

        archive_file = ARCHIVE_DIR / file_path.name
        archive_header = ensure_archive_header(archive_file, file_path)
        existing_archived = parse_entries(archive_file) if archive_file.exists() else []
        write_entries(archive_file, archive_header, [*existing_archived, *stale_entries])
        write_entries(file_path, read_file_header(file_path), active_entries)
        moved_total += len(stale_entries)
        print(
            f"Archived {len(stale_entries)} entries from "
            f"{file_path.relative_to(ROOT)} -> {archive_file.relative_to(ROOT)}"
        )

    if moved_total == 0:
        print("No stale entries found.")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manage KK Dev Skeleton gstack rules.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("lint", help="Validate rule files.")

    match_parser = subparsers.add_parser("match", help="Match rules by tags.")
    match_parser.add_argument("--tags", required=True, help="Comma-separated tag list.")
    match_parser.add_argument("--touch", action="store_true", help="Update last_hit for matched rules.")

    touch_parser = subparsers.add_parser("touch", help="Update last_hit for one rule.")
    touch_parser.add_argument("--id", required=True, help="Rule id, such as SPEC-001.")

    archive_parser = subparsers.add_parser("archive-stale", help="Archive stale rules.")
    archive_parser.add_argument("--months", type=int, default=3, help="Staleness threshold in months.")

    parser.add_argument(
        "--today",
        help="Override date in YYYY-MM-DD format for deterministic runs.",
    )
    return parser.parse_args()


def resolve_today(raw: str | None) -> date:
    if not raw:
        return date.today()
    return datetime.strptime(raw, "%Y-%m-%d").date()


def main() -> int:
    args = parse_args()
    files = default_files()
    today = resolve_today(args.today)

    if args.command == "lint":
        return lint(files)
    if args.command == "match":
        tag_query = {tag.strip().lower() for tag in args.tags.split(",") if tag.strip()}
        return match_tags(tag_query, files, args.touch, today)
    if args.command == "touch":
        return touch_rule(args.id, files, today)
    if args.command == "archive-stale":
        return archive_stale(files, args.months, today)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
