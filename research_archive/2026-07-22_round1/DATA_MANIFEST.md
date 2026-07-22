# Data and Evidence Manifest

## 1. Original Paper Scale Sweep and DQN

Authoritative inputs:

- `data/paper_archive/stage2_bestq_original_paper.csv`
- `data/paper_archive/stage2_original_paper_template.xlsx`
- `output/npz/res_dqn_<config>.npz`

Derived evidence:

- `output/csv/stage2_bestq_original_with_dqn.csv`
- `output/csv/stage2_bestq_original_with_dqn_validation.csv`
- `output/spreadsheet_dqn/stage2_five_method_comparison_original_paper.xlsx`
- `output/pdf/stage2_fixed_servers_with_dqn_original_paper.pdf`
- `output/pdf/stage2_fixed_users_with_dqn_original_paper.pdf`

Protocol:

- Four evolutionary values are transcribed from the original paper workbook.
- DQN uses seed `42` and five preference weights: `0.1`, `0.3`, `0.5`, `0.7`, and `0.9`.
- Best Q is lower-is-better.
- PSP is the lowest-Q method in all seven distinct configurations represented by the two four-panel figures.

## 2. CLS Initialization Sensitivity

Authoritative outputs:

- `output/csv/cls_init_sensitivity_detail.csv`
- `output/csv/cls_init_sensitivity_paper_table.csv`
- `output/pdf/cls_init_sensitivity_130_heatmap.pdf`
- `output/pdf/cls_init_random_vs_greedy_10_150.pdf`

Protocol:

- Initializations: Random, Density, DistSum, marginal Greedy, and Diverse.
- Random is averaged over `50` independent runs.
- Fixed-130-user configurations: `5/130`, `10/130`, `15/130`, and `20/130`.
- Diagnostic configuration: `10/150`.
- The gap is measured against the best final transmission cost observed in the same configuration.

Interpretation:

- The fixed-130-user results show that the tested initializations reach the same best final cost, apart from a small Random mean gap at `10/130`.
- The `10/150` diagnostic shows that a deterministic marginal-greedy preference can lead to a substantially poorer local optimum than unbiased Random initialization.

## 3. Hybrid Anchor Sensitivity

Authoritative outputs:

- `output/csv/hybrid_anchor_sensitivity_detail.csv`
- `output/csv/hybrid_anchor_sensitivity_paper_table.csv`
- `output/csv/hybrid_anchor_sensitivity_summary.csv`
- `output/npz/res_hybrid_anchor*.npz`

Protocol:

- Seeds: `42`, `43`, and `44`.
- Capacity-four sweep: anchor sizes `1`, `2`, `3`, and `V_j=4`.
- Additional capacity-relative cases are preserved for later thesis analysis.

Status:

- These results document the explored parameter behavior and are intentionally retained for future research.
- The manuscript uses the interpretable proportional default rather than claiming a universal empirical optimum from this finite sweep.

## 4. Small-Scale Joint Optimization Gap

Exact inputs:

- `data/joint_gap/input_data_joint_gap_c6_u30_k3_s4_seed42.xlsx`
- `data/joint_gap/input_data_joint_gap_c6_u30_k3_s4_seed43.xlsx`
- `data/joint_gap/input_data_joint_gap_c6_u30_k3_s4_seed44.xlsx`

Authoritative outputs:

- `output/csv/joint_gap_summary_c6_u30_k3_s4_seeds42_44.csv`
- `output/npz/res_joint_exact_joint_gap_c6_u30_k3_s4_seed<seed>.npz`
- `output/npz/res_mos2_psp_joint_gap_c6_u30_k3_s4_seed<seed>.npz`

Results:

| Seed | HV gap (%) | IGD gap | Best Q gap | Exact/MOS2 runtime ratio |
|---:|---:|---:|---:|---:|
| 42 | 6.4466 | 0.0289 | 0.0000 | 4.9865 |
| 43 | 4.1811 | 0.0199 | 0.0000 | 5.1532 |
| 44 | 0.9836 | 0.0660 | 0.0000 | 5.3985 |

This is a response-only small-instance diagnostic, not a claim of exact equivalence on large MEC instances.

## 5. Alternate Real-Region Generalization

Selected input:

- `data/real_region/input_data_real_sparse_r04_c40_u130_k10_s1_8.xlsx`

Design and evidence:

- `output/csv/reviewer6_generalization_design.csv`
- `output/csv/real_region_final_candidate_summary.csv`
- `output/csv/reviewer6_main_candidate_stage2_detail.csv`
- `output/csv/reviewer6_main_candidate_stage2_aggregate.csv`
- `output/csv/dqn_summary_real_sparse_r04_c40_u130_k10_s1.csv`
- `output/npz/res_dqn_real_sparse_r04_c40_u130_k10_s1.npz`
- `output/csv/reviewer6_main_candidate_bestq_aggregate.csv`
- `output/excel/reviewer6_generalization_evidence.xlsx`
- `output/pdf/reviewer6_generalization_topology.pdf`
- `output/pdf/reviewer6_generalization_bestq.pdf`

Configuration:

- `40` candidate stations, `10` deployed servers, `130` users, and `8` service types.
- Alternate center is approximately `24.20 km` from the original Xizhimen center.
- Stage-I CLS cost is `2304.7670`; the best tested Stage-I baseline cost is `6150.5741`, a `62.53%` reduction.
- Across seeds `42`, `43`, and `44`, PSP has the best mean HV (`1.0116`) and mean IGD (`0.0129`) among the four population-based methods.
- In the five-method scalarized comparison, PSP has mean Best Q `0.2678`, while DQN has mean Best Q `0.5517` over the same three seeds.

## Data Access Boundary

The original full Beijing base-station workbook is not redistributed in this public repository. It may be regenerated only from an authorized local copy. The selected experiment-ready instance and all reported aggregate results are versioned so the documented comparison can be audited without exposing the full source pool or a credential.
