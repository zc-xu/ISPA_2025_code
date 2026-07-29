# Operation Log

## Repository History Used for This Snapshot

| Commit | Recorded work |
|---|---|
| `b4dd6d5` | Revision workflow and CLS initialization-sensitivity foundation. |
| `cbca119` | Reproducible batch experiments and reviewer-response handoff. |
| `f9845d0` | Restored DQN learning-based baseline and verified evidence. |
| `cf46316` | Added alternate-region generalization experiment. |
| `0f74d0d` | Strengthened Reviewer 2 Comment 6 generalization evidence. |

## 2026-07-19 to 2026-07-22 Work

1. Recovered the authoritative Stage-II values from the original paper workbook and audited the submitted seed/protocol.
2. Rebuilt the two Stage-II scale-sweep figures with DQN as the fifth method while preserving the paper's visual style.
3. Reconstructed Fig. 1, the Stage-II evolutionary-optimization panel, CLS sensitivity, Stage-I figures, and hybrid-initialization figure for final layout dimensions.
4. Prepared clean and marked TeX manuscripts from the first-submission baseline and compiled both locally.
5. Built the item-by-item response letter as Word and PDF, replaced screenshot placeholders with exact revised manuscript text, and converted formulas to native Word equations.
6. Produced a Chinese one-to-one response audit and a complete bilingual manuscript-change audit.
7. Restyled the alternate-region DQN bar to use the same outline/hatch system as the manuscript figures.
8. Verified the final response letter visually: `19` pages, `112` native equation objects, `13` revised-manuscript text boxes, and no raw formula markers or screenshot placeholders.
9. Restored the alternate-region DQN source CSV/NPZ to the public reproducibility set and regenerated the three-seed aggregate and Best-Q figure from those saved results.

## GitHub Archival Procedure

1. Confirmed that `zc-xu/ISPA_2025_code` is a public repository and that `dev` is the active research branch.
2. Created a clean clone from `origin/dev`; the existing local experiment workspace was not reset or altered.
3. Copied only current experiment code, validated data, final figures, editable sources, manuscript files, and response materials.
4. Excluded `tmp/node_modules`, map tiles, QA page renders, duplicated previews, local settings, and the restricted full station pool.
5. Added repository-relative provenance paths and ignore rules for transient files.
6. Added this snapshot, data manifest, reproduction guide, thesis-extension guide, and SHA-256 inventory.
7. Validated syntax, generated artifacts, file sizes, staged scope, and secret/path scans before pushing.

## Preservation Rule

The files under `research_archive/2026-07-22_round1/` form a historical snapshot. Future work should create a new dated snapshot or modify canonical code outside this directory. Do not silently replace past data or figures; document corrected results in a new commit and record the relationship to the earlier artifact.
