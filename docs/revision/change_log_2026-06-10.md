# Change Log - 2026-06-10

## Update - 2026-06-22

Prepared the GitHub handoff package for continuing the revision on another computer.

Added:

- `docs/revision/HANDOFF_2026-06-22.md`
  - summarizes the current branch, active code changes, reviewer-comment mapping, reproduced results, exact commands, and remaining tasks;
  - explicitly records that DQN and SPEA2 are not part of the active experiment pipeline.
- `output/pdf/cls_init_sensitivity_130_heatmap.pdf`
  - recommended main figure for the CLS initialization sensitivity response under the fixed 130-user setting.
- `output/pdf/cls_init_random_vs_greedy_10_150.pdf`
  - auxiliary figure showing that a marginal greedy initialization can be worse in one case.
- `output/csv/cls_init_sensitivity_all_data_scan.csv`
  - extra scan over available Excel files; no ideal case was found where random has zero gap while all other deterministic initializations are clearly worse.

Verified:

- `cls_initialization_sensitivity.py --help` runs successfully.
- `pareto_batch_metrics.py --help` runs successfully.
- Active experiment scripts under `LocalSearch/*.py` do not contain DQN or SPEA2 baseline logic.

## Purpose

Clean up the experiment code after reassessing extra baselines. DQN and the extra evolutionary baseline are temporarily removed from the active experiment pipeline, while the reproducibility and batch-experiment improvements are kept.

## Removed or Disabled

- Removed the runnable DQN baseline script:
  - `LocalSearch/dqn_service_baseline.py`
- Removed DQN command-line options from:
  - `LocalSearch/batch_service_experiments.py`
- Removed DQN loading, colors, markers, and plotting logic from:
  - `LocalSearch/pareto_batch_metrics.py`
- Removed generated DQN artifacts:
  - `output/csv/dqn_summary_*.csv`
  - `output/csv/dqn_training_*.csv`
  - `output/npz/res_dqn_*.npz`
  - `output/pdf/dqn_training_*.pdf`
  - `output/png/dqn_training_*.png`
- Removed extra evolutionary baseline command-line support and generated artifacts:
  - removed the extra baseline option from `LocalSearch/batch_service_experiments.py`;
  - removed extra baseline loading, colors, markers, and plotting logic from `LocalSearch/pareto_batch_metrics.py`;
  - removed generated result files for the extra baseline.
- Added CLS initialization sensitivity experiment:
  - `LocalSearch/cls_initialization_sensitivity.py`;
  - compares random, density-based, distance-sum, greedy marginal, and density-diverse initialization;
  - runs random initialization with 50 seeds on all `_new` datasets;
  - writes detail, summary, and paper-table outputs to `output/csv`, `output/excel`, `output/pdf`, and `output/png`;
  - generated PDFs were rendered with Poppler and checked for clipping.

## Kept

- Dataset/configuration manifest:
  - `LocalSearch/experiment_configs.py`
- Reusable experiment helper functions:
  - `LocalSearch/experiment_utils.py`
- Batch experiment entrypoint:
  - `LocalSearch/batch_service_experiments.py`
- Pareto metric and figure generation:
  - `LocalSearch/pareto_batch_metrics.py`
- CLS initialization sensitivity experiment:
  - `LocalSearch/cls_initialization_sensitivity.py`
- Re-generated Pareto metrics and figures for:
  - `10_130`
  - `5_130`
  - CLS initialization sensitivity on all `_new` datasets

## Verification

Confirmed that the active `LocalSearch/*.py` source files no longer contain DQN or extra-baseline references.

Confirmed the batch entrypoint help no longer exposes DQN or extra-baseline options:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\batch_service_experiments.py --help
```

Re-generated metrics with only the active comparison methods:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\pareto_batch_metrics.py --config 10_130
.\LocalSearch\Scripts\python.exe .\LocalSearch\pareto_batch_metrics.py --config 5_130
```

## Current Recommendation

Do not include the temporary extra-baseline results in the main paper figures. If a learning-based baseline is required later, revisit a more rigorous preference-conditioned or multi-objective learning baseline.
