# Change Log - 2026-07-13

## Scope

This update preserves the reproducible experiment extensions completed after commit `b4dd6d5` and prepares the `dev` branch for continuation on another computer.

## Added

- Capacity-aware hybrid-anchor sensitivity experiment.
- Synthetic and real-region geographical generalization experiments.
- Small-scale exact joint-optimization comparison for the two-stage optimality-gap discussion.
- Representative input datasets, metrics, Pareto results, topology figures, and verification tables.
- `requirements-revision.txt` and a complete handoff note.

## Changed

- Parameterized the deterministic anchor size and service capacity in `ServiceSampling` and `ServiceRepair`.
- Allowed batch runs to disable repeated hybrid-process visualization.
- Regenerated the `10_130` Pareto metrics and figures with the four active methods only.
- Updated revision documentation to distinguish completed evidence, cautious conclusions, and remaining reviewer items.

## Removed From Active Work

- DQN runnable scripts and all generated DQN results.
- DQN method registration in Pareto metric generation.
- SPEA2 remains outside the active code because it is not a learning-based baseline.

The DQN reassessment document is retained only to record why the old design should not be restored.

## Verification

- All seven experiment entrypoints return help successfully.
- `pareto_batch_metrics.py --config 10_130` completes and reports exactly `NS-P`, `GCP`, `GDP`, and `PSP`.
- Active `LocalSearch/*.py` files contain no DQN or SPEA2 references.
- Selected PNG/PDF figures were visually checked for complete axes, legends, labels, and nonblank rendering.
