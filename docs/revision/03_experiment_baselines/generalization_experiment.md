# Generalization Experiment for Reviewer Comment 6

## 1. Reviewer Comment and Revision Target

Reviewer comment:

> In Section V, all experiments are conducted using a dataset collected within approximately a 9 km region around Xizhimen Subway Station in Beijing. However, the manuscript does not discuss the generalization capability of the proposed framework under different geographical distributions, heterogeneous traffic densities, or larger-scale MEC environments.

中文含义：

第 V 节现有实验主要基于北京西直门地铁站周边约 9 km 区域的数据。审稿人关心的是：所提出的两阶段框架在不同地理分布、异构流量密度、更大规模 MEC 环境下是否仍然有效，而不是只在一个固定区域上有效。

本次实验目标：

1. 保留原始 `10_130` 西直门真实数据作为 baseline。
2. 生成可复现的 synthetic geography scenarios，用来模拟不同地理分布和异构流量密度。
3. 对每个场景完整运行 Stage I 和 Stage II，并输出拓扑图、Pareto front 和 Pareto 指标。
4. 根据结果判断这组实验适合写入论文主文、补充材料，还是仅用于 response letter。

## 2. Implemented Code

新增入口：

```text
LocalSearch/generalization_experiments.py
```

新增数据：

```text
data/generalization/input_data_gen_sparse_suburban_10_130_8.xlsx
data/generalization/input_data_gen_uniform_large_10_130_8.xlsx
data/generalization/input_data_gen_clustered_hotspot_10_130_8.xlsx
```

新增输出：

```text
output/csv/generalization_stage1_summary.csv
output/excel/generalization_stage1_summary.xlsx
output/csv/generalization_pareto_metrics_summary.csv
output/excel/generalization_pareto_metrics_summary.xlsx
output/png/generalization_topology_*.png
output/pdf/generalization_topology_*.pdf
output/png/generalization_pareto_metrics_summary.png
output/pdf/generalization_pareto_metrics_summary.pdf
output/png/pareto_front_gen_*.png
output/pdf/pareto_front_gen_*.pdf
output/png/pareto_metrics_gen_*.png
output/pdf/pareto_metrics_gen_*.pdf
```

The script uses stable scenario-specific seed offsets, so the synthetic datasets are reproducible when the same `--seed` is used.

## 3. Experimental Design

Baseline:

- `10_130`: the original Xizhimen real-data case from `data/input_data_10_130_8_new.xlsx`.

Synthetic scenarios:

- `sparse_suburban`: a larger-area sparse-suburban-like distribution with one main hotspot, one secondary cluster, and dispersed users.
- `uniform_large`: a larger-area uniform distribution with lower spatial concentration.
- `clustered_hotspot`: a heterogeneous distribution with two strong hotspots and a more skewed service-request profile.

The synthetic scenarios use the same coordinate scale, candidate count, user count, service-type dimension, and Stage II method set as the original experiment. This isolates the effect of spatial distribution and traffic heterogeneity without changing the problem dimension at the same time.

Important limitation:

These synthetic datasets are not real Changping data. They can be described as sparse-suburban-like or heterogeneous synthetic scenarios, but should not be written as real measurements from Changping unless a real Changping dataset is collected and used.

## 4. Reproducibility Commands

Run the sparse-suburban representative case from Stage I to Stage II:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\generalization_experiments.py --no-baseline --scenarios sparse_suburban --pop-size 40 --n-gen 100 --regenerate-data --force-nsga
```

Run the other two synthetic scenarios:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\generalization_experiments.py --no-baseline --scenarios uniform_large clustered_hotspot --pop-size 40 --n-gen 100 --regenerate-data --force-nsga
```

Regenerate all summary tables and figures using existing NPZ results:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\generalization_experiments.py --scenarios sparse_suburban uniform_large clustered_hotspot --skip-nsga
```

## 5. Stage I Distribution Summary

| Config | Scenario | K | Stage I cost | Width km | Height km | User NN mean km | Station density mean | Station density CV | Service entropy |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `10_130` | Xizhimen real-data baseline | 10 | 2969.6378 | 6.6696 | 8.5932 | 0.3395 | 15.9000 | 0.2336 | 2.0749 |
| `gen_sparse_suburban_10_130` | sparse_suburban | 10 | 36882.9736 | 13.3472 | 16.7876 | 0.6226 | 5.0500 | 0.9589 | 2.0471 |
| `gen_uniform_large_10_130` | uniform_large | 10 | 53621.6307 | 14.2795 | 18.4281 | 0.7365 | 2.5500 | 0.3610 | 2.0694 |
| `gen_clustered_hotspot_10_130` | clustered_hotspot | 10 | 9156.1593 | 10.5884 | 14.1613 | 0.3437 | 12.9500 | 1.2467 | 1.8714 |

Interpretation:

- `sparse_suburban` and `uniform_large` expand the spatial extent and increase mean nearest-neighbor distance, so they represent lower-density spatial distributions than the original Xizhimen case.
- `sparse_suburban` and `clustered_hotspot` have much larger station-density CV values than the original case, so they represent more heterogeneous traffic/candidate coverage.
- Stage I resolves to the same target server count `K = 10` in all cases, which makes the Stage II comparison structurally aligned.

## 6. Stage II Pareto Metrics

Metric directions:

- HV: higher is better.
- IGD: lower is better.
- Best Q: lower is better.
- BestCostNorm and BestDelayNorm: lower is better, after normalization within each scenario.

| Scenario | Method | HV | IGD | Best Q | BestCostNorm | BestDelayNorm |
|---|---|---:|---:|---:|---:|---:|
| Xizhimen real-data baseline | NS-P | 0.8191 | 0.0785 | 0.3894 | 0.0116 | 0.0934 |
| Xizhimen real-data baseline | GCP | 0.8596 | 0.0492 | 0.3550 | 0.0312 | 0.1004 |
| Xizhimen real-data baseline | GDP | 0.8945 | 0.0326 | 0.3363 | 0.0648 | 0.0320 |
| Xizhimen real-data baseline | PSP | 0.9470 | 0.0016 | 0.3282 | 0.0000 | 0.0000 |
| sparse_suburban | NS-P | 0.9662 | 0.0440 | 0.2814 | 0.0229 | 0.0450 |
| sparse_suburban | GCP | 0.9497 | 0.0355 | 0.2636 | 0.0665 | 0.0429 |
| sparse_suburban | GDP | 1.0141 | 0.0082 | 0.2602 | 0.0000 | 0.0062 |
| sparse_suburban | PSP | 0.9814 | 0.0222 | 0.2615 | 0.0344 | 0.0000 |
| uniform_large | NS-P | 0.8835 | 0.0575 | 0.3027 | 0.1333 | 0.0621 |
| uniform_large | GCP | 1.0000 | 0.0043 | 0.2958 | 0.0000 | 0.0046 |
| uniform_large | GDP | 0.9603 | 0.0226 | 0.3014 | 0.0264 | 0.0000 |
| uniform_large | PSP | 0.9646 | 0.0174 | 0.2942 | 0.0442 | 0.0086 |
| clustered_hotspot | NS-P | 0.9481 | 0.0325 | 0.3040 | 0.0481 | 0.0019 |
| clustered_hotspot | GCP | 0.8797 | 0.0733 | 0.3384 | 0.1223 | 0.0000 |
| clustered_hotspot | GDP | 0.9951 | 0.0080 | 0.2784 | 0.0000 | 0.0265 |
| clustered_hotspot | PSP | 0.8853 | 0.0712 | 0.3348 | 0.0632 | 0.0543 |

## 7. Current Conclusion

The results support the following careful conclusion:

The two-stage pipeline can be executed consistently under the original Xizhimen distribution and under several synthetic distributions with larger spatial extent and more heterogeneous traffic density. The generated Pareto fronts remain valid and non-degenerate in all tested scenarios, which provides preliminary evidence that the framework is not restricted to a single spatial layout.

The results do not support the stronger claim that PSP is always best under every generalized distribution. PSP is best on the original Xizhimen case and obtains the best `Best Q` in the large-area uniform case. In the sparse-suburban and clustered-hotspot scenarios, GDP gives the best aggregate Pareto metrics, while PSP remains competitive only in part of the trade-off region.

Recommended manuscript use:

- If this experiment is included in the paper, use cautious wording such as "generalization check" or "additional robustness evaluation" rather than "comprehensive proof of geographic generalization."
- The safest figure to include is the topology comparison plus a short table of Stage I distribution statistics. The full Pareto metric comparison can be placed in a response letter or supplementary material unless further tuning improves PSP's generalized performance.
- Do not describe the synthetic sparse-suburban case as real Changping data.

## 8. Remaining Work

To fully address the reviewer comment, a stronger final revision should add at least one of the following:

1. A real second-area dataset, such as a verified Changping or other Beijing region sample, then rerun the same command path.
2. A larger-scale setting using available `20_300` data, or newly generated 30/40-candidate datasets if those are later added.
3. A concise manuscript paragraph explaining that the current additional experiment evaluates spatial distribution and traffic heterogeneity, while larger-scale MEC deployment is partially covered by the existing server/user scaling experiments.
