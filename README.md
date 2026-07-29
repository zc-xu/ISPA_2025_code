# MOS2 Research Code and Revision Archive

This repository contains the implementation, experiment data, publication figures, and revision records for **MOS2: A Two-Stage Multi-Objective Framework for Server Deployment and Service Provisioning in Mobile Edge Computing**.

## Start Here

- Current handoff: [`docs/revision/HANDOFF_2026-07-22.md`](docs/revision/HANDOFF_2026-07-22.md)
- Revision notes: [`docs/revision/README.md`](docs/revision/README.md)
- Frozen round-1 snapshot: [`research_archive/2026-07-22_round1/README.md`](research_archive/2026-07-22_round1/README.md)
- Reproduction guide: [`research_archive/2026-07-22_round1/REPRODUCIBILITY_GUIDE.md`](research_archive/2026-07-22_round1/REPRODUCIBILITY_GUIDE.md)
- Data provenance: [`research_archive/2026-07-22_round1/DATA_MANIFEST.md`](research_archive/2026-07-22_round1/DATA_MANIFEST.md)

## Repository Layout

| Path | Contents |
|---|---|
| `LocalSearch/` | Stage-I/Stage-II algorithms, baselines, batch entrypoints, and reviewer-response experiments. |
| `data/` | Versioned experiment inputs and machine-readable paper-result archives. |
| `output/` | Validated CSV/XLSX/NPZ results and publication figures. |
| `docs/revision/` | Reviewer comments, experiment reports, manuscript-editing notes, and handoff records. |
| `research_archive/` | Date-stamped immutable snapshots of manuscripts, responses, source figures, and exact supporting evidence. |

## Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-revision.txt
```

Run commands from the repository root. The scripts also work with the historical local interpreter at `LocalSearch/Scripts/python.exe` when that environment is available.

## Common Reproduction Commands

```powershell
# DQN baseline and seven controlled Stage-II configurations
python LocalSearch/dqn_service_baseline.py --configs all --weights 0.1 0.3 0.5 0.7 0.9 --episodes 320 --dqn-seeds 42
python LocalSearch/build_stage2_paper_comparison.py
python LocalSearch/plot_stage2_five_method.py

# CLS initialization sensitivity
python LocalSearch/cls_initialization_sensitivity.py --configs all_new --random-runs 50 --seed 42 --max-iter 200

# Small-scale joint optimization comparison
python LocalSearch/joint_optimality_gap.py --n-candidates 6 --k 3 --n-users 30 --num-services 4 --capacity 2 --seed 42

# Aggregate saved real-region generalization runs
python LocalSearch/reviewer6_generalization_summary.py
```

## Data Boundary

The public repository does not contain the original full Beijing base-station pool or its access credential. It contains only the selected, experiment-ready instances and aggregated results required to audit the reported experiments. Set `MEC_STATION_POOL_PASSWORD` locally when regenerating candidate regions from an authorized source file.

## Commit Convention

Use Conventional Commits, for example:

- `feat(experiments): add a reproducible baseline`
- `fix(metrics): correct normalization bounds`
- `docs(revision): record reviewer-response evidence`
- `chore(data): archive validated experiment outputs`
