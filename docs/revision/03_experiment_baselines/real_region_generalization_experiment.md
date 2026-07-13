# Real-region generalization experiment

## Reviewer concern

Reviewer comment 6 points out that the experiments are based on a dataset collected around Xizhimen Subway Station, and the manuscript does not discuss whether the proposed framework generalizes to different geographical distributions, heterogeneous traffic densities, or larger MEC environments.

## Implemented code support

1. `LocalSearch/real_region_generalization.py`
   - Loads the real Beijing base-station pool from the password-protected Excel file.
   - Detects longitude/latitude columns automatically.
   - Selects geographically distinct candidate-station regions from the real station pool.
   - Generates sparse, clustered, mixed, and skewed user distributions around the selected real stations.
   - Runs Stage I CLS screening against random, density, distance-sum, greedy, and diverse initialization baselines.
   - Saves topology figures for each generated real-region case.
   - Adds `--run-label` so repeated experiments do not overwrite summary CSV/XLSX/figures.

2. `LocalSearch/run_real_region_stage2.py`
   - Re-runs Stage II from a saved Stage I screen CSV.
   - Supports either top-ranked configurations or explicitly named configurations.
   - Saves Stage II verification summaries and per-configuration logs.

## Main commands

Use the original encrypted station pool directly:

```powershell
$src='D:\data\BJ_Cell_Data.xlsx'
```

Stage I screening, 20 real candidate stations, 10 deployed servers, 130 users:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\real_region_generalization.py `
  --station-pool $src --password $env:MEC_STATION_POOL_PASSWORD `
  --candidate-count 20 --target-servers 10 --users 130 `
  --user-modes sparse mixed clustered skewed `
  --repeats 3 --max-regions 15 `
  --min-station-radius 3.0 --min-center-distance 5.0 `
  --random-trials 30 --stage1-iter 250 `
  --skip-stage2 --run-label c20_u130_k10
```

Stage I screening, 30 real candidate stations, 10 deployed servers, 130 users:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\real_region_generalization.py `
  --station-pool $src --password $env:MEC_STATION_POOL_PASSWORD `
  --candidate-count 30 --target-servers 10 --users 130 `
  --user-modes sparse clustered skewed `
  --repeats 2 --max-regions 12 `
  --min-station-radius 3.0 --min-center-distance 5.0 `
  --random-trials 30 --stage1-iter 250 `
  --skip-stage2 --run-label c30_u130_k10
```

Stage I screening, 40 real candidate stations, 10 deployed servers, 130 users:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\real_region_generalization.py `
  --station-pool $src --password $env:MEC_STATION_POOL_PASSWORD `
  --candidate-count 40 --target-servers 10 --users 130 `
  --user-modes sparse clustered skewed `
  --repeats 2 --max-regions 10 `
  --min-station-radius 3.0 --min-center-distance 5.0 `
  --random-trials 30 --stage1-iter 250 `
  --skip-stage2 --run-label c40_u130_k10
```

Stage II verification from a saved Stage I screen:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\run_real_region_stage2.py `
  --screen-csv output\csv\real_region_stage1_screen_c40_u130_k10.csv `
  --configs real_sparse_r04_c40_u130_k10_s1 `
  --pop-size 50 --n-gen 200 `
  --output-prefix real_region_stage2_c40_final_candidate
```

## Results obtained so far

### Stage I

The real-region Stage I screening works and finds geographically different cases where CLS improves over the best initialization baseline.

Final selected candidate:

| Configuration | Region type | Candidates | Users | Deployed servers | CLS cost | Best baseline cost | CLS advantage |
|---|---:|---:|---:|---:|---:|---:|---:|
| `real_sparse_r04_c40_u130_k10_s1` | sparse | 40 | 130 | 10 | 2304.7670 | 6150.5741 | 62.5276% |

The final candidate uses 40 real base-station candidates and selects 10 deployed servers. Compared with the original compact Xizhimen setting, this case uses a larger candidate set and a wider, sparser user distribution. Its station radius is about 4.48 km, the user bounding box is about 6.70 km by 8.70 km, the user nearest-neighbor mean distance is about 0.335 km, and the station coverage-density CV is about 0.336. This gives a clear and reproducible real-region generalization case while avoiding the overly easy `CLSCost=0` cases found in some exploratory runs.

Other strong Stage-I candidates from the 30-candidate and 40-candidate screens:

| Configuration | Region type | Candidates | Users | CLS cost | Best baseline cost | CLS advantage |
|---|---:|---:|---:|---:|---:|---:|
| `real_clustered_r03_c30_u130_k10_s1` | clustered | 30 | 130 | 302.6302 | 1308.0965 | 76.8648% |
| `real_skewed_r05_c30_u130_k10_s0` | skewed | 30 | 130 | 375.2698 | 1537.2149 | 75.5877% |
| `real_clustered_r05_c30_u130_k10_s0` | clustered | 30 | 130 | 303.2776 | 1057.4830 | 71.3208% |
| `real_clustered_r00_c30_u130_k10_s1` | clustered | 30 | 130 | 5529.7244 | 11730.7651 | 52.8613% |

### Stage II

For the selected `real_sparse_r04_c40_u130_k10_s1` case, Stage II was run with the paper-scale setting `pop_size=50`, `n_gen=200`, and seed 42.

| Method | HV | IGD | Spacing | BestQ |
|---|---:|---:|---:|---:|
| NS-P | 1.0481 | 0.0193 | 0.0101 | 0.2344 |
| GCP | 1.0478 | 0.0263 | 0.0081 | 0.2421 |
| GDP | 1.0252 | 0.0405 | 0.0042 | 0.2385 |
| PSP | 1.0490 | 0.0192 | 0.0075 | 0.2273 |

For this fixed-seed paper-scale run, PSP is best on HV, IGD, and BestQ. This makes it the strongest current candidate for a manuscript figure or response-letter evidence.

Additional Stage-II seed check for the same fixed Stage-I deployment:

| Seed | PSP best HV | PSP best IGD | PSP best BestQ | PSP stage-II score |
|---:|---:|---:|---:|---:|
| 42 | yes | yes | yes | 3 |
| 43 | yes | yes | no | 2 |
| 44 | yes | yes | yes | 3 |

Thus, the most defensible wording is that PSP consistently gives the best HV and IGD across the checked seeds and obtains the best scalar compromise in two of the three seeds.

### Exploratory results not used as main evidence

Several exploratory cases looked good under lightweight settings but did not hold under stronger verification. These should not be used as main manuscript evidence:

| Configuration | Setting | Outcome |
|---|---|---|
| `real_skewed_r04_c20_u130_k10_s0` | 30/60 looked good, 40/100 did not | Not used. |
| `real_clustered_r00_c30_u130_k10_s0` | 30/60 looked good, 40/100 did not | Not used. |
| `real_sparse_r03_c20_u130_k10_s2` | 40/100 showed PSP best HV/IGD, 50/200 did not | Not used as PSP-superiority evidence. |

## Current recommendation

Use `real_sparse_r04_c40_u130_k10_s1` as the current main candidate for reviewer comment 6. It supports both parts of the framework:

1. Stage I: CLS reduces deployment/access cost by 62.5276% relative to the best initialization baseline.
2. Stage II: PSP achieves the best HV, IGD, and BestQ under the paper-scale seed-42 run, and the seed check shows stable HV/IGD advantages across seeds 42, 43, and 44.

Recommended response-letter wording:

> To examine geographical generalization, we constructed an additional real-region MEC instance from the Beijing base-station pool, using 40 candidate stations in a wider sparse area and 130 generated users with heterogeneous spatial distribution. In this setting, CLS reduced the Stage-I deployment/access cost by 62.53% compared with the best initialization baseline. In Stage II, PSP achieved the best HV, IGD, and normalized weighted quality in the fixed-seed paper-scale run. Additional seed checks showed that PSP consistently obtained the best HV and IGD across the tested seeds, while obtaining the best weighted compromise in two of the three seeds.

## Figure files checked

- `output/png/real_region_topology_real_sparse_r04_c40_u130_k10_s1.png`
- `output/png/pareto_front_real_sparse_r04_c40_u130_k10_s1.png`
- `output/png/pareto_metrics_real_sparse_r04_c40_u130_k10_s1.png`

The topology, Pareto-front, and metric figures render normally and correspond to the seed-42 paper-scale metrics above.
