from __future__ import annotations

import difflib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL = ROOT / "outputs" / "revision_package" / "manuscript" / "conference_101719_first_submission.tex"
REVISED = ROOT / "outputs" / "revision_package" / "manuscript" / "conference_101719_targeted_revision_clean.tex"
OUTPUT = ROOT / "tmp" / "revision_audit" / "original_vs_clean_diff_hunks.json"


def main() -> None:
    original_lines = ORIGINAL.read_text(encoding="utf-8").splitlines()
    revised_lines = REVISED.read_text(encoding="utf-8").splitlines()
    matcher = difflib.SequenceMatcher(a=original_lines, b=revised_lines, autojunk=False)
    hunks = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        hunks.append(
            {
                "tag": tag,
                "original_start_line": i1 + 1,
                "original_end_line": i2,
                "revised_start_line": j1 + 1,
                "revised_end_line": j2,
                "original": "\n".join(original_lines[i1:i2]).strip(),
                "revised": "\n".join(revised_lines[j1:j2]).strip(),
            }
        )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(hunks, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"hunks": len(hunks), "output": str(OUTPUT)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
