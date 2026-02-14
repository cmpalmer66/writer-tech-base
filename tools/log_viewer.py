#!/usr/bin/env python3
"""Terminal log viewer for regex filtering and hash code aliasing."""

from __future__ import annotations

import argparse
import curses
import itertools
import re
from dataclasses import dataclass
from pathlib import Path

BASE_NAMES = [
    "Alice",
    "Bob",
    "Carol",
    "Dave",
    "Eve",
    "Frank",
    "Grace",
    "Heidi",
    "Ivan",
    "Judy",
    "Mallory",
    "Niaj",
    "Olivia",
    "Peggy",
    "Rupert",
    "Sybil",
    "Trent",
    "Uma",
    "Victor",
    "Walter",
    "Xavier",
    "Yvonne",
    "Zara",
]

NATO_NAMES = [
    "Alpha",
    "Bravo",
    "Charlie",
    "Delta",
    "Echo",
    "Foxtrot",
    "Golf",
    "Hotel",
    "India",
    "Juliet",
    "Kilo",
    "Lima",
    "Mike",
    "November",
    "Oscar",
    "Papa",
    "Quebec",
    "Romeo",
    "Sierra",
    "Tango",
    "Uniform",
    "Victor",
    "Whiskey",
    "Xray",
    "Yankee",
    "Zulu",
]

BRACKET_HASH_RE = re.compile(r"\[(\d{5,})\]")
INLINE_HASH_RE = re.compile(r"HashCode=(\d{5,})")


@dataclass
class LineRecord:
    source_line_number: int
    text: str
    included: bool


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Interactive console log viewer with regex filtering and object-hash aliasing."
        )
    )
    parser.add_argument("log_file", type=Path, help="Path to a text log file.")
    parser.add_argument(
        "--include",
        default=".*",
        help="Regex used to include lines (default: '.*').",
    )
    parser.add_argument(
        "--exclude",
        default=None,
        help="Regex used to exclude lines after include-matching.",
    )
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Start by showing both included and filtered-out lines.",
    )
    return parser.parse_args()


def build_name_generator():
    for name in BASE_NAMES:
        yield name
    for name in NATO_NAMES:
        yield name
    for index in itertools.count(1):
        yield f"Name{index}"


def preprocess_lines(lines: list[str]) -> list[str]:
    aliases: dict[str, str] = {}
    names = build_name_generator()

    def alias_for(hash_value: str) -> str:
        if hash_value not in aliases:
            aliases[hash_value] = next(names)
        return aliases[hash_value]

    processed = []
    for line in lines:
        updated = BRACKET_HASH_RE.sub(lambda m: f"[ {alias_for(m.group(1))} ]", line)
        updated = INLINE_HASH_RE.sub(lambda m: f"HashCode={alias_for(m.group(1))}", updated)
        processed.append(updated)

    return processed


def build_records(
    processed_lines: list[str], include_pattern: re.Pattern[str], exclude_pattern: re.Pattern[str] | None
) -> list[LineRecord]:
    records: list[LineRecord] = []
    for idx, line in enumerate(processed_lines, start=1):
        include_match = include_pattern.search(line) is not None
        excluded = exclude_pattern.search(line) is not None if exclude_pattern else False
        records.append(LineRecord(source_line_number=idx, text=line.rstrip("\n"), included=include_match and not excluded))
    return records


def run_viewer(stdscr: curses.window, records: list[LineRecord], start_show_all: bool) -> None:
    curses.curs_set(0)
    curses.use_default_colors()
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
    curses.init_pair(2, curses.COLOR_BLUE, -1)

    show_all = start_show_all
    cursor = 0
    top = 0

    def visible_records() -> list[LineRecord]:
        if show_all:
            return records
        return [r for r in records if r.included]

    while True:
        items = visible_records()
        if not items:
            items = [LineRecord(0, "No lines matched the current filter.", True)]

        cursor = max(0, min(cursor, len(items) - 1))
        height, width = stdscr.getmaxyx()
        body_height = max(1, height - 2)

        if cursor < top:
            top = cursor
        if cursor >= top + body_height:
            top = cursor - body_height + 1

        stdscr.erase()

        for row in range(body_height):
            idx = top + row
            if idx >= len(items):
                break
            record = items[idx]
            line = f"{record.source_line_number:>6} | {record.text}"
            line = line[: max(1, width - 1)]

            attr = curses.A_NORMAL
            if show_all and not record.included:
                attr |= curses.color_pair(2) | curses.A_DIM
            if idx == cursor:
                attr = curses.color_pair(1) | curses.A_BOLD

            stdscr.addnstr(row, 0, line, width - 1, attr)

        included_count = sum(1 for r in records if r.included)
        footer = (
            f"q quit | ↑/↓ move | PgUp/PgDn scroll | a toggle all ({'ON' if show_all else 'OFF'})"
            f" | showing {len(items)}/{len(records)} lines | included={included_count}"
        )
        stdscr.addnstr(height - 2, 0, footer, width - 1, curses.A_REVERSE)

        selected = items[cursor]
        detail = f"Line {selected.source_line_number}"
        stdscr.addnstr(height - 1, 0, detail, width - 1, curses.A_REVERSE)

        stdscr.refresh()
        key = stdscr.getch()

        if key in (ord("q"), ord("Q")):
            return
        if key in (curses.KEY_UP, ord("k")):
            cursor = max(0, cursor - 1)
        elif key in (curses.KEY_DOWN, ord("j")):
            cursor = min(len(items) - 1, cursor + 1)
        elif key == curses.KEY_PPAGE:
            cursor = max(0, cursor - body_height)
        elif key == curses.KEY_NPAGE:
            cursor = min(len(items) - 1, cursor + body_height)
        elif key in (ord("a"), ord("A")):
            current_line = items[cursor].source_line_number
            show_all = not show_all
            new_items = visible_records() or [LineRecord(0, "No lines matched the current filter.", True)]
            for index, rec in enumerate(new_items):
                if rec.source_line_number >= current_line:
                    cursor = index
                    break
            else:
                cursor = len(new_items) - 1


def main() -> int:
    args = parse_args()
    try:
        raw_lines = args.log_file.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    except FileNotFoundError:
        print(f"File not found: {args.log_file}")
        return 1

    processed = preprocess_lines(raw_lines)

    try:
        include_pattern = re.compile(args.include)
    except re.error as exc:
        print(f"Invalid --include regex: {exc}")
        return 2

    exclude_pattern = None
    if args.exclude:
        try:
            exclude_pattern = re.compile(args.exclude)
        except re.error as exc:
            print(f"Invalid --exclude regex: {exc}")
            return 2

    records = build_records(processed, include_pattern, exclude_pattern)
    curses.wrapper(run_viewer, records, args.show_all)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
