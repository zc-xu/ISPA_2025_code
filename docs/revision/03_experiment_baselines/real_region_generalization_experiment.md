# Real-Station Geographical Generalization Experiment

## Purpose

This experiment evaluates the complete MOS2 pipeline after changing the real base-station geography, doubling the candidate-station count, and increasing spatial density heterogeneity.

## Reproducible Instance

Configuration: `real_sparse_r04_c40_u130_k10_s1`

| Property | Value |
|---|---:|
| Deduplicated real Beijing base-station pool | 2,215 coordinates |
| Candidate stations | 40 |
| Selected servers | 10 |
| Users | 130 |
| Service types | 8 |
| Candidate-centroid shift from Xizhimen | 24.2044 km |
| Candidate nearest-neighbor distance | 0.4038 km |
| Coverage-density coefficient of variation | 0.3359 |

The corresponding original-instance values are 20 candidate stations, a candidate nearest-neighbor distance of 0.9451 km, and a coverage-density coefficient of variation of 0.2336.

Input file:

`data/real_region/input_data_real_sparse_r04_c40_u130_k10_s1_8.xlsx`

## Stage I

Settings:

- coverage radius: 1.5 km;
- CLS maximum iterations: 250;
- random initialization-only trials: 30;
- base seed: 42;
- derived data-generation and Stage-I seed: 4060.

Results:

| Placement | Objective |
|---|---:|
| CLS | **2,304.7670** |
| Best random trial | 6,150.5741 |
| Random-trial mean | 13,540.5175 |
| Density | 22,206.4751 |
| Distance-sum | 28,513.3397 |
| Greedy | 28,513.3397 |
| Density-diverse | 19,031.7959 |

CLS reduces the best recorded non-CLS initialization-only objective by 62.5276%.

## Stage II Population Methods

Settings:

- methods: NS-P, GCP, GDP, and PSP;
- population size: 50;
- generations: 200;
- random seeds: 42, 43, and 44;
- shared Stage-I deployment within each run.

Three-seed aggregate:

| Method | HV mean +/- std | IGD mean +/- std | Best Q mean +/- std |
|---|---:|---:|---:|
| NS-P | 0.9574 +/- 0.0840 | 0.0498 +/- 0.0328 | 0.2953 +/- 0.0584 |
| GCP | 0.9799 +/- 0.0691 | 0.0446 +/- 0.0158 | 0.2800 +/- 0.0447 |
| GDP | 0.9742 +/- 0.0522 | 0.0408 +/- 0.0234 | 0.2733 +/- 0.0380 |
| PSP | **1.0116 +/- 0.0579** | **0.0129 +/- 0.0055** | **0.2678 +/- 0.0503** |

The refreshed runs reproduce the archived HV, IGD, and Best Q values exactly for all four methods and all three seeds. The seed-level NPZ files are stored under `output/npz/seed_checks/`.

## DQN Balanced-Solution Comparison

DQN settings:

- preference weights: 0.1, 0.3, 0.5, 0.7, and 0.9;
- training episodes per preference: 320;
- DQN seeds: 42, 43, and 44;
- fixed cross-method evaluation weight: 0.5 for normalized cost and 0.5 for normalized delay;
- exact seed-specific normalization bounds from the four population methods.

The training preference selects a policy output, but it is not used as the cross-method metric. Every DQN output is reevaluated using the fixed common definition

`Best Q = 0.5 x normalized cost + 0.5 x normalized delay`.

| Seed | Best DQN preference | Cost | Delay | Common Best Q |
|---:|---:|---:|---:|---:|
| 42 | 0.9 | 1,984.6548 | 218.2309 | 0.4388 |
| 43 | 0.5 | 2,115.1869 | 234.7720 | 0.6377 |
| 44 | 0.5 | 2,300.8531 | 232.9600 | 0.5785 |
| Mean +/- sample std | - | - | - | **0.5517 +/- 0.1021** |

PSP obtains a 51.45% lower mean Best Q than DQN. HV and IGD remain the equal-cardinality comparison for the four 50-solution population outputs; DQN participates through the common balanced-solution metric because it returns five preference-conditioned outputs per seed.

## Commands

Run a Stage II seed and archive all four NPZ outputs:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\run_real_region_stage2.py `
  --screen-csv output\csv\real_region_stage1_screen_c40_u130_k10.csv `
  --configs real_sparse_r04_c40_u130_k10_s1 `
  --pop-size 50 --n-gen 200 --seed 42 `
  --output-prefix reviewer6_main_stage2_seed42_refresh --archive-npz
```

The same command is run with seeds 43 and 44.

Run DQN with seed-specific reference bounds and the fixed evaluation metric:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\dqn_service_baseline.py `
  --screen-csv output\csv\real_region_stage1_screen_c40_u130_k10.csv `
  --configs real_sparse_r04_c40_u130_k10_s1 `
  --weights 0.1 0.3 0.5 0.7 0.9 `
  --episodes 320 --dqn-seeds 42 43 44 `
  --stage-seed 42 --stage1-iter 200 `
  --reference-by-seed --evaluation-alpha 0.5
```

Generate validated summaries and figures:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\reviewer6_generalization_summary.py
```

Generate the formatted evidence workbook:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\plot_reviewer6_topology.py
.\LocalSearch\Scripts\python.exe .\LocalSearch\plot_reviewer6_bestq.py
node .\LocalSearch\build_reviewer6_paper_workbook.mjs
```

## Outputs

Validated CSV files:

- `output/csv/reviewer6_generalization_design.csv`
- `output/csv/reviewer6_main_candidate_stage1.csv`
- `output/csv/reviewer6_main_candidate_stage2_detail.csv`
- `output/csv/reviewer6_main_candidate_stage2_aggregate.csv`
- `output/csv/reviewer6_main_candidate_dqn_weighted.csv`
- `output/csv/reviewer6_main_candidate_bestq_detail.csv`
- `output/csv/reviewer6_main_candidate_bestq_aggregate.csv`

Figures:

- `output/png/reviewer6_generalization_topology.png`
- `output/pdf/reviewer6_generalization_topology.pdf`
- `output/png/reviewer6_generalization_bestq.png`
- `output/pdf/reviewer6_generalization_bestq.pdf`

Workbook:

- `output/excel/reviewer6_generalization_paper_style.xlsx`
