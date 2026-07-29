from __future__ import annotations

import argparse
from pathlib import Path


def extract_revise_blocks(source: str) -> list[tuple[int, str]]:
    blocks: list[tuple[int, str]] = []
    needle = r"\revise{"
    cursor = 0

    while True:
        start = source.find(needle, cursor)
        if start < 0:
            break

        depth = 1
        end = start + len(needle)
        while end < len(source) and depth:
            if source[end] == "{" and source[end - 1] != "\\":
                depth += 1
            elif source[end] == "}" and source[end - 1] != "\\":
                depth -= 1
            end += 1

        if depth:
            raise ValueError(f"Unbalanced revise block beginning at offset {start}")

        line = source.count("\n", 0, start) + 1
        blocks.append((line, source[start + len(needle) : end - 1]))
        cursor = end

    return blocks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("tex", type=Path)
    parser.add_argument("--max-chars", type=int, default=240)
    args = parser.parse_args()

    source = args.tex.read_text(encoding="utf-8")
    for number, (line, block) in enumerate(extract_revise_blocks(source), start=1):
        compact = " ".join(block.split())
        if args.max_chars > 0:
            compact = compact[: args.max_chars]
        print(f"{number:02d}|L{line}|{compact}")


if __name__ == "__main__":
    main()
