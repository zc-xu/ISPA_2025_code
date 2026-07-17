# Change Log, 2026-07-17

## Reviewer 2 Comment 6

Implemented and validated a two-level geographical generalization evaluation:

- a geographically separate real-station case for the main manuscript;
- an expanded-region sparse/clustered/skewed stress test for the response or supplementary material.

## Code

- Updated `LocalSearch/run_real_region_stage2.py` to save complete metric rows for each configuration and seed.
- Added `LocalSearch/reviewer6_generalization_summary.py` to validate, aggregate, and visualize the complete Reviewer 6 evidence.
- Added `LocalSearch/build_reviewer6_workbook.mjs` to generate a formula-linked, seven-sheet Excel evidence package.

## Experiments

- Retained the alternate real-region candidate with 40 stations, 130 users, and 10 deployed servers.
- Completed expanded-region Stage I experiments for sparse, clustered, and skewed traffic.
- Completed Stage II for all three profiles using seeds 42, 43, and 44, population 50, and 200 generations.
- Validated 36 Stage II records, four methods per profile/seed, and 50 valid nondominated solutions per record.

## Results

- Alternate region: CLS reduces Stage I cost by 62.53%; PSP has the best mean HV, IGD, and Best Q across three seeds.
- Expanded region: CLS reduces Stage I cost by 26.63%, 34.82%, and 51.54% for sparse, clustered, and skewed traffic.
- PSP is not uniformly best in the expanded-region Stage II results; the documentation explicitly limits the claim accordingly.

## Artifacts

- Added three publication-style PNG figures and matching vector PDFs.
- Added design, Stage I, Stage II detail, aggregate, and PSP-gap CSV tables.
- Added `output/excel/reviewer6_generalization_evidence.xlsx`; all seven sheets were rendered and visually checked, and the formula-error scan returned zero matches.

## Documentation

- Added the complete English/Chinese reviewer response, manuscript text, captions, interpretation, and rerun commands in `reviewer6_geographical_generalization_response.md`.
- Updated the concise real-region report, revision progress mapping, README, and cross-computer handoff.
