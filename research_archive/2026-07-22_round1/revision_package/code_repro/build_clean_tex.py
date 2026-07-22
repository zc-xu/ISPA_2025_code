from __future__ import annotations

import argparse
import re
from pathlib import Path


REVISION_PREAMBLE = re.compile(
    r"\\newif\\ifshowrevisions\s*\n"
    r"\\showrevisionstrue\s*\n"
    r"\\ifshowrevisions.*?"
    r"\\newcommand\{\\revcolor\}\{\\ifshowrevisions\\color\{blue\}\\fi\}\s*\n",
    re.DOTALL,
)


def unwrap_command(source: str, command: str) -> str:
    needle = f"\\{command}{{"
    output: list[str] = []
    cursor = 0

    while True:
        start = source.find(needle, cursor)
        if start < 0:
            output.append(source[cursor:])
            break

        output.append(source[cursor:start])
        content_start = start + len(needle)
        depth = 1
        pos = content_start
        while pos < len(source) and depth:
            if source[pos] == "{" and (pos == 0 or source[pos - 1] != "\\"):
                depth += 1
            elif source[pos] == "}" and (pos == 0 or source[pos - 1] != "\\"):
                depth -= 1
            pos += 1

        if depth:
            raise ValueError(f"Unbalanced \\{command} command at offset {start}")

        output.append(source[content_start : pos - 1])
        cursor = pos

    return "".join(output)


def build_clean(source: str) -> str:
    clean, count = REVISION_PREAMBLE.subn("", source, count=1)
    if count != 1:
        raise ValueError("Revision preamble was not found exactly once")

    clean = clean.replace("\\begin{revision}", "")
    clean = clean.replace("\\end{revision}", "")
    clean = clean.replace("\\revcolor", "")
    clean = unwrap_command(clean, "rev")
    return clean


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    source = args.source.read_text(encoding="utf-8")
    clean = build_clean(source)
    args.destination.write_text(clean, encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
