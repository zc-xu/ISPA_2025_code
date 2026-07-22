from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs" / "revision_package" / "manuscript" / "conference_101719_targeted_revision_marked.tex"
OUTPUT = ROOT / "tmp" / "revision_audit" / "blue_revision_segments.json"


def line_number(source: str, offset: int) -> int:
    return source.count("\n", 0, offset) + 1


def scan_balanced_commands(source: str, command: str) -> list[dict[str, object]]:
    needle = f"\\{command}{{"
    segments: list[dict[str, object]] = []
    cursor = 0
    while True:
        start = source.find(needle, cursor)
        if start < 0:
            break
        content_start = start + len(needle)
        depth = 1
        pos = content_start
        while pos < len(source) and depth:
            char = source[pos]
            escaped = pos > 0 and source[pos - 1] == "\\"
            if char == "{" and not escaped:
                depth += 1
            elif char == "}" and not escaped:
                depth -= 1
            pos += 1
        if depth:
            raise ValueError(f"Unbalanced {needle} at offset {start}")
        segments.append(
            {
                "type": command,
                "start_line": line_number(source, start),
                "end_line": line_number(source, pos - 1),
                "start_offset": start,
                "end_offset": pos,
                "content": source[content_start : pos - 1].strip(),
            }
        )
        cursor = pos
    return segments


def scan_environments(source: str, environment: str) -> list[dict[str, object]]:
    begin = f"\\begin{{{environment}}}"
    end = f"\\end{{{environment}}}"
    segments: list[dict[str, object]] = []
    cursor = 0
    while True:
        start = source.find(begin, cursor)
        if start < 0:
            break
        content_start = start + len(begin)
        close = source.find(end, content_start)
        if close < 0:
            raise ValueError(f"Missing {end} after offset {start}")
        finish = close + len(end)
        segments.append(
            {
                "type": environment,
                "start_line": line_number(source, start),
                "end_line": line_number(source, finish - 1),
                "start_offset": start,
                "end_offset": finish,
                "content": source[content_start:close].strip(),
            }
        )
        cursor = finish
    return segments


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    revision_blocks = scan_environments(source, "revision")
    rev_commands = scan_balanced_commands(source, "rev")

    # A command nested inside a revision environment is already covered by that block.
    top_level_commands = []
    for command in rev_commands:
        nested = any(
            block["start_offset"] <= command["start_offset"] < block["end_offset"]
            for block in revision_blocks
        )
        if not nested:
            top_level_commands.append(command)

    revcolor_lines = []
    for number, line in enumerate(source.splitlines(), start=1):
        if "\\revcolor" in line and "newcommand" not in line:
            revcolor_lines.append({"type": "revcolor", "start_line": number, "content": line.strip()})

    segments = sorted(
        revision_blocks + top_level_commands + revcolor_lines,
        key=lambda item: (int(item["start_line"]), item["type"]),
    )
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(segments, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "revision_blocks": len(revision_blocks),
                "top_level_rev_commands": len(top_level_commands),
                "revcolor_lines": len(revcolor_lines),
                "total_segments": len(segments),
                "output": str(OUTPUT),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
