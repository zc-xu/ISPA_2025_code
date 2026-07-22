# Change Log, 2026-07-17

## Reviewer 2 Comment 6

Implemented and validated an end-to-end geographical generalization evaluation in a geographically separate real-station region, including Stage I server placement, Stage II population-based service provisioning, and a learning-based DQN comparison.

## Code

- Updated `LocalSearch/run_real_region_stage2.py` to save complete metric rows for each configuration and seed.
- Added `LocalSearch/reviewer6_generalization_summary.py` to validate and aggregate the complete Reviewer 6 evidence.
- Added `LocalSearch/plot_reviewer6_topology.py` to reproduce the manuscript's service-aware geographical deployment style on the new region.
- Added `LocalSearch/plot_reviewer6_bestq.py` to generate the five-method Best Q comparison with sample-standard-deviation error bars.
- Added `LocalSearch/build_reviewer6_paper_workbook.mjs` to generate an editable template-matched Excel chart and evidence tables.

## Experiments

- Evaluated a new real-region instance with 40 candidate stations, 130 users, 10 deployed servers, and eight service types.
- Completed Stage II for NS-P, GCP, GDP, and PSP using seeds 42, 43, and 44, population 50, and 200 generations.
- Trained five preference-conditioned DQN policies per seed and reevaluated every output using the same equal-weight Best Q definition.

## Results

- CLS reduces the Stage I objective by 62.53% relative to the best recorded non-CLS initialization-only placement.
- PSP has the best mean HV, IGD, and Best Q among the four population-based methods and obtains the best HV and IGD in every tested seed.
- Under the common balanced-solution metric, PSP obtains `0.2678 +/- 0.0503`, compared with `0.5517 +/- 0.1021` for DQN.

## Artifacts

- Added a service-aware geographical deployment figure and a five-method Best Q figure in PNG and vector PDF formats.
- Added design, Stage I, Stage II, DQN, and common Best Q CSV tables.
- Added `output/excel/reviewer6_generalization_paper_style.xlsx`; all three sheets were rendered and visually checked, and the formula-error scan returned zero matches.

## Documentation

- Added the complete English/Chinese reviewer response, manuscript text, captions, interpretation, and rerun commands in `reviewer6_geographical_generalization_response.md`.
- Updated the concise real-region report, revision progress mapping, and cross-computer handoff.
