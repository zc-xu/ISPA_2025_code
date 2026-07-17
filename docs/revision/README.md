# MOS2 Revision Notes

This directory collects the manuscript revision notes, reviewer-response planning notes, and experiment-reproducibility notes for the MOS2 journal revision.

## Start Here

Read `HANDOFF_2026-07-17.md` first. It records the current GitHub handoff status, the completed Reviewer 2 Comment 6 generalization experiments, validated results, reproducibility commands, and manuscript-use boundaries.

## Directory Layout

- `HANDOFF_2026-07-17.md`
  - Current handoff for the alternate-region and expanded-region geographical generalization experiments.
- `HANDOFF_2026-07-14.md`
  - Previous handoff, including the restored DQN baseline and its verified results.
- `HANDOFF_2026-07-13.md`
  - Previous handoff before the DQN baseline was restored.
- `HANDOFF_2026-06-22.md`
  - Previous handoff at commit `b4dd6d5`.
- `01_review_comments/`
  - Reviewer/editor comments translation and item-by-item revision plan.
- `02_manuscript_editing/`
  - Overleaf editing workflow and first-round manuscript text patches.
- `03_experiment_baselines/`
  - Experiment-side progress mapping, Pareto metric notes, CLS initialization sensitivity, hybrid-anchor sensitivity, geography generalization checks, and baseline reassessment notes.
  - `real_region_generalization_report_cn.md` gives the Chinese summary for the final real-region generalization candidate.
  - `reviewer6_geographical_generalization_response.md` contains the validated alternate-region and expanded-region experiments, English/Chinese response text, manuscript-ready wording, figure captions, and rerun commands for Reviewer 2 Comment 6.
  - `joint_optimality_gap_response.md` gives the response-only support for the two-stage decomposition and optimality-gap concern.

## Current Experiment Code Status

The current code keeps the reproducibility improvements:

- explicit experiment configuration manifest in `LocalSearch/experiment_configs.py`;
- reusable data-loading and Stage-I context helpers in `LocalSearch/experiment_utils.py`;
- batch experiment entrypoint in `LocalSearch/batch_service_experiments.py`;
- Pareto metric and figure generation in `LocalSearch/pareto_batch_metrics.py`.
- synthetic geography and traffic-distribution generalization entrypoint in `LocalSearch/generalization_experiments.py`;
- real Beijing base-station generalization entrypoint in `LocalSearch/real_region_generalization.py`;
- Stage-II verification from a saved real-region screen in `LocalSearch/run_real_region_stage2.py`.
- Reviewer 2 Comment 6 result aggregation and publication-figure generation in `LocalSearch/reviewer6_generalization_summary.py`.
- Reviewer 2 Comment 6 auditable workbook generation in `LocalSearch/build_reviewer6_workbook.mjs`.
- capacity-aware hybrid-anchor sensitivity in `LocalSearch/hybrid_anchor_sensitivity.py`;
- small-scale joint exact comparison in `LocalSearch/joint_optimality_gap.py`.

DQN is included as the Stage-II learning-based baseline. It is evaluated as five preference-weighted solution points and is never connected into a misleading continuous Pareto curve. SPEA2 remains excluded because it is not a learning-based method and does not address the reviewer request.

## Common Commands

Run metrics for the reproduced `10_130` case:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\pareto_batch_metrics.py --config 10_130
```

Run the reproducible DQN baseline for all seven controlled configurations:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\dqn_service_baseline.py --configs all --weights 0.1 0.3 0.5 0.7 0.9 --episodes 320 --dqn-seeds 42
.\LocalSearch\Scripts\python.exe .\LocalSearch\plot_dqn_control_results.py
```

Run the batch entrypoint for one configuration, keeping the NSGA-II initialization baselines:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\batch_service_experiments.py --configs 10_130
```

List available experiment configurations:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\batch_service_experiments.py --help
```

Run the CLS initialization sensitivity experiment on all `_new` datasets:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\cls_initialization_sensitivity.py --configs all_new --random-runs 50 --seed 42 --max-iter 200
```

Run the geography generalization summary using the saved Stage-II results:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\generalization_experiments.py --scenarios sparse_suburban uniform_large clustered_hotspot --skip-nsga
```

Run real-region Stage I screening from the encrypted Beijing base-station workbook:

```powershell
$src='D:\data\BJ_Cell_Data.xlsx'
.\LocalSearch\Scripts\python.exe .\LocalSearch\real_region_generalization.py --station-pool $src --password $env:MEC_STATION_POOL_PASSWORD --candidate-count 40 --target-servers 10 --users 130 --user-modes sparse clustered skewed --repeats 2 --max-regions 10 --skip-stage2 --run-label c40_u130_k10
```

Run Stage II verification from a saved real-region Stage I screen:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\run_real_region_stage2.py --screen-csv output\csv\real_region_stage1_screen_c40_u130_k10.csv --configs real_sparse_r04_c40_u130_k10_s1 --pop-size 50 --n-gen 200 --output-prefix real_region_stage2_c40_final_candidate
```

Regenerate the Reviewer 2 Comment 6 evidence tables and paper-style figures from the saved three-seed results:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\reviewer6_generalization_summary.py
```
