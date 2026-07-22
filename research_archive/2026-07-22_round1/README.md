# MOS2 Round-1 Research Snapshot

Snapshot date: **2026-07-22**

This directory preserves the exact round-1 revision materials and their supporting evidence. It is intended for three uses:

1. reconstruct the submission and response package;
2. audit how each reviewer comment was addressed;
3. provide a stable starting point for later thesis modules without losing the original experiment protocol.

## Authoritative Files

| Purpose | File |
|---|---|
| Clean manuscript source | `revision_package/manuscript/conference_101719_targeted_revision_clean.tex` |
| Clean compiled manuscript | `revision_package/manuscript/conference_101719_targeted_revision_clean.pdf` |
| Marked manuscript source | `revision_package/manuscript/conference_101719_targeted_revision_marked.tex` |
| Marked compiled manuscript | `revision_package/manuscript/conference_101719_targeted_revision_marked.pdf` |
| First-submission source | `revision_package/manuscript/conference_101719_first_submission.tex` |
| Final response letter | `revision_package/07_response_to_editor_and_reviewers_revised.docx` |
| Response-letter PDF | `revision_package/07_response_to_editor_and_reviewers_revised.pdf` |
| Chinese response audit | `revision_package/08_response_to_reviewers_chinese_translation.md` |
| Full bilingual manuscript audit | `revision_package/06_complete_original_vs_revised_bilingual_audit.md` |
| Side-by-side manuscript comparison | `revision_package/04_original_vs_revised_marked_side_by_side.pdf` |

## Snapshot Contents

- `revision_package/manuscript/`: original, clean, and marked TeX/PDF files plus all required figure PDFs.
- `revision_package/figures/`: final publication figures in vector PDF and selected editable/vector formats.
- `revision_package/response_evidence/`: plots and tables embedded in the response letter.
- `revision_package/source_visio/`: preserved Visio sources for Fig. 1 and the architecture figure.
- `revision_package/spreadsheets/`: editable five-method Stage-II workbook.
- `revision_package/data/` and `experiment_inputs/`: exact CSV/XLSX inputs needed to audit the displayed results.
- `tooling/`: scripts used to build the response letter, figures, comparison PDFs, and clean manuscript.

## Validated Results Preserved Here

- Stage-II paper-scale comparison: PSP has the lowest Best Q in all seven distinct tested configurations; its reduction over the best alternative evolutionary initialization is `2.26%` to `9.53%`, with a mean of `4.11%`.
- Representative `10 servers / 130 users`: PSP Best Q is `0.3282`; DQN Best Q is `0.6125`.
- CLS initialization study: under the fixed 130-user settings, the tested deterministic initializations reach the same best final cost; in the `10 servers / 150 users` diagnostic, Random has a `1.27%` mean gap and marginal Greedy has a `15.88%` gap.
- Small joint comparison: the MOS2 and exact joint search have the same Best Q for seeds `42`, `43`, and `44`, while exact joint search requires approximately `4.99x` to `5.40x` the runtime.
- Alternate real-region case: Stage-I CLS reduces cost by `62.53%` relative to the best tested baseline; across seeds `42` to `44`, PSP has the best mean HV and IGD among the four population-based methods.
- Alternate real-region scalar comparison: PSP has mean Best Q `0.2678`, compared with `0.5517` for DQN over seeds `42` to `44`.

These statements are tied to the files listed in `DATA_MANIFEST.md`; broader claims should not be inferred beyond the documented protocol.

## Integrity

`SHA256SUMS.txt` records the checksum of every archived file except the checksum file itself. Regenerate it only when intentionally creating a new snapshot revision.
