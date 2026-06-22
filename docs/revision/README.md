# MOS2 Revision Notes

This directory collects the manuscript revision notes, reviewer-response planning notes, and experiment-reproducibility notes for the MOS2 journal revision.

## Start Here

Read `HANDOFF_2026-06-22.md` first. It records the current GitHub handoff status, reviewer-comment mapping, implemented code changes, generated result files, reproducibility commands, and remaining tasks.

## Directory Layout

- `HANDOFF_2026-06-22.md`
  - Current handoff note for continuing the revision on another computer.
- `01_review_comments/`
  - Reviewer/editor comments translation and item-by-item revision plan.
- `02_manuscript_editing/`
  - Overleaf editing workflow and first-round manuscript text patches.
- `03_experiment_baselines/`
  - Experiment-side progress mapping, Pareto metric notes, CLS initialization sensitivity, and baseline reassessment notes.

## Current Experiment Code Status

The current code keeps the reproducibility improvements:

- explicit experiment configuration manifest in `LocalSearch/experiment_configs.py`;
- reusable data-loading and Stage-I context helpers in `LocalSearch/experiment_utils.py`;
- batch experiment entrypoint in `LocalSearch/batch_service_experiments.py`;
- Pareto metric and figure generation in `LocalSearch/pareto_batch_metrics.py`.

DQN-related runnable code and generated DQN artifacts have been removed from the active experiment code for now. Extra baseline candidates are kept only as revision notes in `03_experiment_baselines/`; they are not part of the active experiment pipeline.

## Common Commands

Run metrics for the reproduced `10_130` case:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\pareto_batch_metrics.py --config 10_130
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
