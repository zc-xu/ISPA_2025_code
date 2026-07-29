# Change Log, 2026-07-14

## Decision Correction

The active revision decision is to retain DQN as the Stage II learning-based baseline. The previous 2026-07-13 statement that DQN had been removed is superseded. SPEA2 remains excluded because it is not a learning-based method.

## Code

- Added `LocalSearch/dqn_service_baseline.py` with a reproducible NumPy DQN, replay buffer, target network, preference weights, batch configuration selection, and original-objective evaluation.
- Added `LocalSearch/plot_dqn_control_results.py` to create paper-aligned and full-rerun controlled-variable figures.
- Updated `LocalSearch/pareto_batch_metrics.py` so DQN is automatically included when `res_dqn_<config>.npz` exists.
- Added spreadsheet inspection, update, and Excel-native chart-source scripts under `tools/spreadsheet_dqn/`.

## Experiments

- Reran seven configurations: `10_100`, `10_130`, `10_150`, `10_180`, `5_130`, `15_130`, and `20_130`.
- Used weights `0.1, 0.3, 0.5, 0.7, 0.9`, seed 42, and 320 episodes per weight.
- Stored deployment matrices, objective values, episode-level logs, five-method metric tables, and PNG/PDF figures.
- Verified that DQN is weaker than PSP on HV, IGD, and BestQ in all seven jointly normalized comparisons.

## Workbook

- Added DQN values to the original Stage II Excel workbook while preserving the existing layout.
- Expanded all eight native chart source ranges from four to five methods.
- Added `DQN_summary` with both normalization conventions.
- Verified five data points per chart and zero formula-error matches.

## Documentation

- Added `dqn_stage2_baseline_report.md` with method definition, exact commands, results, interpretation limits, and response-letter text.
- Added `HANDOFF_2026-07-14.md` as the current cross-computer continuation guide.
- Updated `README.md` and the reviewer-progress mapping to reflect the restored DQN baseline.
