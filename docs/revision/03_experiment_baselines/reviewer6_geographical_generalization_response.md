# Reviewer 2 Comment 6: Geographical Generalization Experiment and Response

## 1. Reviewer comment and translation

> In Section V, all experiments are conducted using a dataset collected within approximately a 9 km region around Xizhimen Subway Station in Beijing.

译：在第 V 节中，所有实验都使用了北京西直门地铁站周边约 9 km 区域内采集的数据集。

> However, the manuscript does not discuss the generalization capability of the proposed framework under different geographical distributions, heterogeneous traffic densities, or larger-scale MEC environments.

译：然而，稿件没有讨论所提出框架在不同地理分布、异构流量密度或更大规模 MEC 环境下的泛化能力。

这条意见实际要求同时回答三个问题：

1. 换到与西直门不同的地理区域后，MOS2 是否仍能完成 Stage I 和 Stage II；
2. 用户流量由稀疏变为聚集或偏斜后，结论是否保持；
3. 候选基站和空间覆盖范围扩大后，算法是否仍能产生有效解。

## 2. Experiment design

本次采用两层证据，避免只展示一组有利结果：

- **正文候选实验**：选择一个与原始西直门区域明显分离的真实基站区域，完整运行 Stage I 和 Stage II，并用三个随机种子检验稳定性。
- **扩大区域压力测试**：从另一组真实基站拓扑构建更大空间范围，在同一候选基站集合上分别生成 sparse、clustered 和 skewed 三种异构流量，完整运行两个阶段。

原始北京基站池解密、清洗和坐标去重后包含 2,215 个真实基站坐标。公开仓库只保存本实验使用的去标识化坐标子集，不保存原始受保护工作簿、密码或本地绝对路径。

需要严格区分数据来源：

- 候选基站位置来自真实北京基站坐标；
- 原稿西直门用户数据沿用原实验数据；
- 新区域的 sparse、clustered 和 skewed 用户流量由固定随机种子可复现生成；
- 因此不能把新流量描述为真实人口分布或真实运营商业务记录。

### 2.1 Dataset characteristics

| Dataset | Candidates | Users | Selected servers | Distance from original centroid | User footprint | Area ratio | Density CV | User NN distance |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Original Xizhimen | 20 | 130 | 10 | 0 km | 6.67 x 8.59 km | 1.00 | 0.2336 | 0.3395 km |
| Alternate real region | 40 | 130 | 10 | 24.20 km | 6.70 x 8.70 km | 1.02 | 0.3359 | 0.3348 km |
| Expanded sparse | 40 | 130 | 10 | 22.00 km | 13.30 x 12.40 km | 2.88 | 0.5409 | 0.5231 km |
| Expanded clustered | 40 | 130 | 10 | 22.00 km | 11.56 x 11.15 km | 2.25 | 0.5343 | 0.3658 km |
| Expanded skewed | 40 | 130 | 10 | 22.00 km | 12.63 x 11.08 km | 2.44 | 0.6001 | 0.3636 km |

The alternate-region reference center is approximately `(116.0938, 40.1078)`. The expanded-region reference center is approximately `(116.0321, 39.9929)`, and its real-station radius is 11.84 km.

译：正文候选区域的参考中心约为 `(116.0938, 40.1078)`；扩大区域的参考中心约为 `(116.0321, 39.9929)`，真实候选基站相对该中心的最大半径为 11.84 km。

### 2.2 Controlled settings

Stage I settings:

- target servers: 10;
- users: 130;
- service types: 8;
- coverage radius: 1.5 km;
- CLS iterations: 250;
- random baseline trials: 50;
- data-generation and Stage I seed: 42.

Stage II settings:

- population size: 50;
- generations: 200;
- seeds: 42, 43, and 44;
- methods: NS-P, GCP, GDP, and PSP;
- primary metrics: HV, IGD, and Best Q;
- Spacing is retained in the detailed CSV only and is not used as the main ranking criterion.

For each configuration and seed, cost and delay are normalized using the pooled minimum and maximum across the compared methods. IGD uses the nondominated union of all compared fronts as the common empirical reference front. HV is computed with reference point `(1.1, 1.1)`, and Best Q uses equal cost-delay weights.

译：每个配置和随机种子分别使用所有对比方法的联合最小值和最大值归一化 cost 与 delay。IGD 的共同经验参考前沿是所有方法非支配解的并集，HV 的参考点为 `(1.1, 1.1)`，Best Q 对归一化 cost 和 delay 采用相同权重。

## 3. Results

### 3.1 Alternate real region: recommended main-paper evidence

Stage I result:

| CLS cost | Best non-CLS baseline cost | Reduction |
|---:|---:|---:|
| 2,304.7670 | 6,150.5741 | 62.5276% |

The best non-CLS result is the best value among the recorded random, density, distance-sum, greedy, and density-diverse initial deployments. CLS therefore retains a clear Stage I advantage after moving to a geographically separate real-station topology and doubling the candidate count from 20 to 40.

译：非 CLS 最好结果取记录到的 random、density、distance-sum、greedy 和 density-diverse 初始部署中的最小值。换到另一片真实基站区域并将候选基站数从 20 增加到 40 后，CLS 在 Stage I 中仍保持明显优势。

Stage II aggregate over three seeds:

| Method | HV mean +/- std | IGD mean +/- std | Best Q mean +/- std |
|---|---:|---:|---:|
| NS-P | 0.9574 +/- 0.0840 | 0.0498 +/- 0.0328 | 0.2953 +/- 0.0584 |
| GCP | 0.9799 +/- 0.0691 | 0.0446 +/- 0.0158 | 0.2800 +/- 0.0447 |
| GDP | 0.9742 +/- 0.0522 | 0.0408 +/- 0.0234 | 0.2733 +/- 0.0380 |
| **PSP** | **1.0116 +/- 0.0579** | **0.0129 +/- 0.0055** | **0.2678 +/- 0.0503** |

Compared with the strongest competing mean for each metric, PSP improves HV by 3.23%, reduces IGD by 68.28%, and reduces Best Q by 1.99%. PSP has the best HV and IGD in all three seeds and the best Best Q in two of the three seeds. The mean values of all three primary metrics are best for PSP.

译：相对于每个指标中最强的对比方法均值，PSP 的 HV 提高 3.23%，IGD 降低 68.28%，Best Q 降低 1.99%。在三个随机种子中，PSP 的 HV 和 IGD 均为最优，Best Q 在其中两个种子中最优；三个主要指标的跨种子均值均为 PSP 最优。

### 3.2 Expanded-region stress test: response or supplementary evidence

Stage I remains effective under all three traffic profiles:

| Traffic profile | CLS cost | Best baseline cost | CLS reduction |
|---|---:|---:|---:|
| Sparse | 23,479.4626 | 32,001.1812 | 26.6294% |
| Clustered | 7,859.9883 | 12,058.5490 | 34.8181% |
| Skewed | 4,924.3671 | 10,162.4348 | 51.5434% |

Stage II mean results show a more demanding and scientifically useful boundary:

| Profile | PSP HV | Best HV | PSP IGD | Best IGD | PSP Best Q | Best Best Q | Best method |
|---|---:|---:|---:|---:|---:|---:|---|
| Sparse | 0.9481 | 0.9781 | 0.0535 | 0.0397 | 0.2581 | 0.2421 | GDP |
| Clustered | 0.9520 | 1.0104 | 0.0432 | 0.0086 | 0.2631 | 0.2558 | GCP |
| Skewed | 1.0203 | 1.0669 | 0.0418 | 0.0078 | 0.2185 | 0.2089 | GCP |

All 36 Stage II method/configuration/seed records contain 50 valid solutions and 50 nondominated solutions. The complete two-stage pipeline therefore remains executable in the expanded region, but PSP is not uniformly best. The relative benefit of Stage II initialization is distribution dependent.

译：36 条 Stage II 方法/配置/随机种子记录均包含 50 个有效解和 50 个非支配解，说明完整两阶段流程在扩大区域中仍能稳定运行；但 PSP 并非始终最优，Stage II 初始化机制的相对优势会受到流量分布影响。

## 4. Defensible conclusions

The evidence supports the following claims:

1. The complete MOS2 workflow can be transferred to geographically different real base-station topologies.
2. CLS retains a clear Stage I advantage in the alternate region and in all three expanded-region traffic profiles.
3. PSP achieves the best mean HV, IGD, and Best Q in the alternate-region three-seed experiment.
4. Under substantially expanded and heterogeneous traffic, Stage II method rankings vary; PSP should not be claimed as universally superior.

译：证据可以支撑 MOS2 完整流程能迁移到不同真实基站拓扑、CLS 的 Stage I 优势具有较好的地理和流量稳健性，以及 PSP 在正文候选区域的三个主要均值指标上最优；但不能声称 PSP 在所有扩大区域和流量分布下都绝对最优。

The alternate case was retained from a reproducible multi-region screen. Presenting only this favorable case without the expanded stress test would weaken the response and could be interpreted as result selection. The strongest defensible revision is therefore to place the alternate-region result in the main paper and disclose the complete expanded-region stress test in the response letter or supplementary material.

译：正文候选来自可复现的多区域筛选。若只展示这组有利结果而完全不披露扩大区域压力测试，容易被质疑为选择性展示。最稳妥的方案是正文展示候选区域结果，同时在回复信或补充材料中完整报告扩大区域压力测试及其结论边界。

## 5. Recommended English response to the reviewer

> **Response:** Thank you for pointing out the limited geographical scope of the original evaluation. We have added two complementary generalization experiments using a pool of 2,215 real base-station coordinates in Beijing. First, we evaluated the complete two-stage framework in a geographically separate region whose candidate-station centroid is 24.20 km from that of the original Xizhimen setting. This case contains 40 candidate stations, 130 users, and 10 deployed servers. In Stage I, CLS obtains a cost of 2,304.7670, compared with 6,150.5741 for the best recorded non-CLS initialization baseline, corresponding to a 62.53% reduction. In Stage II, using a population of 50, 200 generations, and three random seeds, PSP obtains mean HV, IGD, and Best Q values of 1.0116, 0.0129, and 0.2678, respectively, which are the best mean values among NS-P, GCP, GDP, and PSP.
>
> We further conducted an expanded-region stress test using another real base-station topology. The user footprints are 2.25-2.88 times the area of the original setting, and sparse, clustered, and skewed traffic profiles were generated reproducibly. CLS reduces the Stage I cost relative to the best recorded baseline by 26.63%, 34.82%, and 51.54%, respectively. The complete Stage II pipeline produces valid Pareto sets for every method, profile, and random seed. However, the relative ranking of the Stage II initialization methods varies across traffic profiles, and PSP is not uniformly best in this more demanding setting. We report this result to clarify that the framework remains applicable under changed geography and traffic heterogeneity, while the benefit of a particular Stage II initialization strategy is distribution dependent.
>
> The revised manuscript now describes the new data construction, experimental settings, quantitative results, and scope of the generalization claim. We also clarify that the base-station coordinates are real, whereas the new heterogeneous user-traffic profiles are reproducibly generated and are not presented as measured population data.

### 对应中文

> **回复：** 感谢审稿人指出原始实验地理范围有限的问题。我们使用包含 2,215 个北京真实基站坐标的基站池，新增了两组互补的泛化实验。首先，我们在一片与原西直门设置明显分离的区域中完整评估两阶段框架，该区域候选基站质心与原区域相距 24.20 km，包含 40 个候选基站、130 个用户，并部署 10 台服务器。Stage I 中 CLS 的 cost 为 2,304.7670，而记录到的最好非 CLS 初始化基线为 6,150.5741，相当于降低 62.53%。Stage II 采用种群规模 50、200 代和三个随机种子，PSP 的平均 HV、IGD 和 Best Q 分别为 1.0116、0.0129 和 0.2678，均为 NS-P、GCP、GDP 和 PSP 四种方法中的最优均值。
>
> 我们还使用另一组真实基站拓扑进行了扩大区域压力测试。三种流量设置的用户覆盖面积为原设置的 2.25-2.88 倍，并以可复现方式生成 sparse、clustered 和 skewed 流量分布。相对于记录到的最好基线，CLS 在 Stage I 中分别降低 cost 26.63%、34.82% 和 51.54%。所有方法、流量分布和随机种子均能在 Stage II 中产生有效 Pareto 解集。但是，在这一更具挑战性的设置下，Stage II 初始化方法的相对排名会随流量分布变化，PSP 并非始终最优。该结果说明框架在改变地理位置和流量异质性后仍然适用，同时也表明特定 Stage II 初始化策略的收益具有分布依赖性。
>
> 修改后的稿件补充了新数据的构造方式、实验设置、定量结果和泛化结论的适用范围。我们还明确说明候选基站坐标来自真实数据，而新增的异构用户流量是可复现生成的，不将其描述为实际测量的人口数据。

## 6. Recommended manuscript text

### English text for the main manuscript

> **Geographical and Traffic-Distribution Generalization:** To evaluate transferability beyond the original Xizhimen setting, we constructed an additional MEC instance from real base-station coordinates in a geographically separate region of Beijing. The candidate-station centroid is 24.20 km from that of the original instance. The new instance contains 40 candidate stations, 130 users, and 10 deployed servers, while its coverage-density coefficient of variation increases from 0.2336 to 0.3359. In Stage I, CLS obtains a cost of 2,304.7670 and reduces the cost of the best recorded non-CLS initialization baseline by 62.53%. In Stage II, over three random seeds, PSP achieves mean HV, IGD, and Best Q values of 1.0116, 0.0129, and 0.2678, respectively, outperforming NS-P, GCP, and GDP in all three mean metrics. These results indicate that the proposed two-stage framework remains effective after changing the underlying real-station topology and increasing the number of candidate stations.

### 对应中文解释

> **地理与流量分布泛化：** 为评估框架在原西直门设置之外的迁移能力，我们使用北京另一片区域的真实基站坐标构建了新的 MEC 实例。该实例候选基站质心与原实例相距 24.20 km，包含 40 个候选基站、130 个用户和 10 台部署服务器，其覆盖密度变异系数由 0.2336 增加到 0.3359。Stage I 中 CLS 的 cost 为 2,304.7670，相对于记录到的最好非 CLS 初始化基线降低 62.53%。Stage II 的三个随机种子结果显示，PSP 的平均 HV、IGD 和 Best Q 分别为 1.0116、0.0129 和 0.2678，三个均值指标均优于 NS-P、GCP 和 GDP。结果表明，在更换真实基站拓扑并增加候选基站数量后，所提出的两阶段框架仍然有效。

### Optional text for the response or supplementary material

> To further assess scale and traffic heterogeneity, we expanded the user footprint to 2.25-2.88 times that of the original setting and generated reproducible sparse, clustered, and skewed traffic profiles over a common real-station topology. CLS reduces the best recorded Stage I baseline cost by 26.63%, 34.82%, and 51.54%, respectively. All Stage II variants generate valid Pareto sets under all profiles and seeds. The relative ranking of the initialization strategies nevertheless varies across profiles, showing that the framework is portable but that the advantage of a specific Stage II initialization is distribution dependent.

### 对应中文解释

> 为进一步评估规模和流量异质性，我们将用户覆盖面积扩大到原设置的 2.25-2.88 倍，并在同一真实基站拓扑上可复现地生成 sparse、clustered 和 skewed 三种流量分布。CLS 相对于记录到的 Stage I 最好基线分别降低 cost 26.63%、34.82% 和 51.54%。所有 Stage II 变体在全部流量分布和随机种子下均生成有效 Pareto 解集；但初始化策略的相对排名会随流量分布变化，说明框架具有可迁移性，而特定 Stage II 初始化策略的优势具有分布依赖性。

## 7. Figure and table captions

### Geography comparison

> **Fig. X. Geographical configurations used for the generalization evaluation.** The original Xizhimen instance is compared with a geographically separate real-station instance and an expanded real-station instance. Circles denote users, triangles denote candidate base stations, and stars denote the servers selected by CLS.

译：**图 X. 泛化评估使用的地理配置。** 对比原西直门实例、另一片真实基站实例和扩大范围的真实基站实例。圆点表示用户，三角形表示候选基站，星形表示 CLS 选择的服务器。

### Heterogeneous traffic

> **Fig. Y. Reproducible heterogeneous traffic profiles over the same expanded real-station topology.** The sparse, clustered, and skewed profiles use the same 40 real candidate stations, 130 users, and 10 selected servers. The user locations and requests are generated with fixed seeds; they are not presented as measured population data.

译：**图 Y. 同一扩大真实基站拓扑上的可复现异构流量分布。** sparse、clustered 和 skewed 三组实验使用相同的 40 个真实候选基站、130 个用户和 10 台部署服务器。用户位置和请求由固定随机种子生成，不作为真实人口测量数据表述。

### Result summary

> **Fig. Z. Generalization results in the expanded region.** Stage I reports the CLS cost reduction relative to the best recorded initialization baseline. Stage II reports the mean and sample standard deviation of HV, IGD, and Best Q over seeds 42, 43, and 44.

译：**图 Z. 扩大区域中的泛化结果。** Stage I 展示 CLS 相对于记录到的最好初始化基线的 cost 降幅；Stage II 展示随机种子 42、43 和 44 下 HV、IGD 和 Best Q 的均值与样本标准差。

## 8. Reproducibility commands

Generate the expanded-region datasets and Stage I results:

```powershell
$src='D:\data\BJ_Cell_Data.xlsx'
$env:MEC_STATION_POOL_PASSWORD='<password>'
.\LocalSearch\Scripts\python.exe .\LocalSearch\real_region_generalization.py `
  --station-pool $src `
  --password $env:MEC_STATION_POOL_PASSWORD `
  --candidate-count 40 `
  --target-servers 10 `
  --users 130 `
  --user-modes sparse clustered skewed `
  --repeats 1 `
  --max-regions 1 `
  --min-station-radius 10 `
  --min-center-distance 10 `
  --coverage-radius 1.5 `
  --stage1-iter 250 `
  --random-trials 50 `
  --seed 42 `
  --skip-stage2 `
  --run-label review6_large_c40_u130_k10
```

Run Stage II for all three profiles and seeds:

```powershell
$configs = @(
  'real_review6_large_c40_u130_k10_sparse_r00_c40_u130_k10_s0',
  'real_review6_large_c40_u130_k10_clustered_r00_c40_u130_k10_s0',
  'real_review6_large_c40_u130_k10_skewed_r00_c40_u130_k10_s0'
)
foreach ($seed in 42,43,44) {
  .\LocalSearch\Scripts\python.exe .\LocalSearch\run_real_region_stage2.py `
    --screen-csv output\csv\real_region_stage1_screen_review6_large_c40_u130_k10.csv `
    --configs $configs `
    --pop-size 50 `
    --n-gen 200 `
    --seed $seed `
    --output-prefix "review6_large_region_stage2_seed$seed"
}
```

Regenerate summary tables and figures from the saved results:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\reviewer6_generalization_summary.py
```

## 9. Evidence files

Primary figures:

- `output/png/reviewer6_geography_comparison.png`
- `output/png/reviewer6_heterogeneous_traffic.png`
- `output/png/reviewer6_large_region_results.png`
- matching vector PDFs under `output/pdf/`

Primary tables:

- `output/csv/reviewer6_generalization_design.csv`
- `output/csv/reviewer6_large_region_stage1.csv`
- `output/csv/reviewer6_large_region_stage2_detail.csv`
- `output/csv/reviewer6_large_region_stage2_aggregate.csv`
- `output/csv/reviewer6_main_candidate_stage2_detail.csv`
- `output/csv/reviewer6_main_candidate_stage2_aggregate.csv`
- `output/excel/reviewer6_generalization_evidence.xlsx`

The source raw station-pool export and local workbook path are intentionally excluded from version control.
