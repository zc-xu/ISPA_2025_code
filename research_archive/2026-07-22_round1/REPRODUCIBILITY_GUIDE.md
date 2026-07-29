# Reproducibility Guide

Run all commands from the repository root.

## 1. Install Dependencies

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-revision.txt
```

Primary packages are NumPy, pandas, Matplotlib, pymoo, openpyxl, msoffcrypto-tool, and xlrd. The response-letter builder additionally requires `python-docx`, `lxml`, and Pillow.

## 2. Rebuild the Stage-II Five-Method Evidence

To retrain DQN:

```powershell
python LocalSearch/dqn_service_baseline.py --configs all --weights 0.1 0.3 0.5 0.7 0.9 --episodes 320 --dqn-seeds 42
```

To combine the archived four-method paper values with the DQN outputs and validate PSP's rank:

```powershell
python LocalSearch/build_stage2_paper_comparison.py
python LocalSearch/plot_stage2_five_method.py
```

Expected validation file:

`output/csv/stage2_bestq_original_with_dqn_validation.csv`

Every row must report `PSP_Is_Lowest=True`.

## 3. Rebuild CLS Initialization Sensitivity

```powershell
python LocalSearch/cls_initialization_sensitivity.py --configs all_new --random-runs 50 --seed 42 --max-iter 200
```

Key outputs:

- `output/csv/cls_init_sensitivity_paper_table.csv`
- `output/pdf/cls_init_sensitivity_130_heatmap.pdf`
- `output/pdf/cls_init_random_vs_greedy_10_150.pdf`

## 4. Rebuild Hybrid-Anchor Sensitivity

```powershell
python LocalSearch/hybrid_anchor_sensitivity.py --configs 5_130 10_130 10_150 10_180 15_130 20_130 --varpi-values 1 2 3 Vj --capacities 4 --seeds 42 43 44
```

The raw NPZ results are preserved under `output/npz/res_hybrid_anchor*.npz` so figures and summary tables can be regenerated without rerunning every evolutionary search.

## 5. Rebuild the Small Joint-Optimization Comparison

Run one seed:

```powershell
python LocalSearch/joint_optimality_gap.py --n-candidates 6 --k 3 --n-users 30 --num-services 4 --capacity 2 --seed 42
```

Repeat with seeds `43` and `44`, then compare against:

`output/csv/joint_gap_summary_c6_u30_k3_s4_seeds42_44.csv`

## 6. Rebuild the Alternate-Region Summary

The selected experiment-ready input is already versioned. Rebuild the saved-run summary and figures with:

```powershell
python LocalSearch/reviewer6_generalization_summary.py
python LocalSearch/plot_reviewer6_topology.py
python LocalSearch/plot_reviewer6_bestq.py
```

The saved DQN evidence consumed by the summary is versioned at:

- `output/csv/dqn_summary_real_sparse_r04_c40_u130_k10_s1.csv`
- `output/npz/res_dqn_real_sparse_r04_c40_u130_k10_s1.npz`

An immutable copy is also preserved under `revision_package/data/` in this snapshot.

Regenerating candidate regions from the full station pool requires an authorized source workbook:

```powershell
$env:MEC_STATION_POOL_PASSWORD = '<local credential>'
python LocalSearch/real_region_generalization.py --station-pool <authorized-workbook> --password $env:MEC_STATION_POOL_PASSWORD --candidate-count 40 --target-servers 10 --users 130 --user-modes sparse clustered skewed --repeats 2 --max-regions 10 --skip-stage2 --run-label c40_u130_k10
```

Do not commit the source workbook, extracted full station pool, or credential.

## 7. Rebuild Snapshot Figures and Response Letter

The date-stamped tooling resolves paths relative to the snapshot directory:

```powershell
python research_archive/2026-07-22_round1/tooling/plot_dqn_five_bar.py
python research_archive/2026-07-22_round1/tooling/plot_real_region_bestq_response.py
python research_archive/2026-07-22_round1/tooling/build_response_letter_docx.py
```

The Word builder uses Microsoft Office's `MML2OMML.XSL` to create native Word equations. If Office is installed elsewhere, set `MML2OMML_XSL` to that file before running it.

## 8. Verification Checklist

```powershell
python -m compileall -q LocalSearch research_archive/2026-07-22_round1/tooling
git diff --check
```

Then verify:

- clean and marked manuscript PDFs compile;
- the response letter opens and its equations are editable Word equations;
- figure labels remain readable at final two-column layout size;
- CSV/Excel values match the plotted bars;
- no absolute personal path, credential, `tmp/`, map cache, or `node_modules/` is staged.
