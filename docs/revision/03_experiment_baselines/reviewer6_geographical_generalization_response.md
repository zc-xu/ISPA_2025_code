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

The alternate-region case primarily tests geographical and real-station-topology transfer: its candidate centroid moves 24.20 km and the candidate count doubles from 20 to 40, but its user-footprint area is only 1.02 times that of the original case. It must therefore not be used alone as evidence of a larger spatial scale. The three expanded-region profiles provide the separate evidence for spatial scale and traffic heterogeneity.

译：正文候选案例主要检验地理位置和真实基站拓扑迁移：候选基站质心移动了 24.20 km，候选基站数由 20 增至 40，但用户覆盖面积仅为原案例的 1.02 倍。因此不能仅凭该案例声称空间尺度已经显著扩大；更大空间尺度和流量异质性的证据由三组扩大区域实验单独提供。

### 2.2 Controlled settings

Common Stage I settings:

- target servers: 10;
- users: 130;
- service types: 8;
- coverage radius: 1.5 km;
- CLS iterations: 250.

The two experiment groups use different recorded screening budgets and must not be conflated:

- alternate-region main candidate: 30 random initialization-only trials; base seed 42 and derived generation/Stage-I seed 4060 for `r04/s1/sparse`;
- expanded-region stress test: 50 random initialization-only trials; base seed 42 and derived generation/Stage-I seeds 43, 45, and 46 for sparse, clustered, and skewed traffic, respectively.

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

Complete Stage I audit values:

| Placement result | Coverage/access objective |
|---|---:|
| CLS after local search | **2,304.7670** |
| Random mean over 30 initialization-only trials | 13,540.5175 |
| Random best over 30 initialization-only trials | **6,150.5741** |
| Density initialization | 22,206.4751 |
| Distance-sum initialization | 28,513.3397 |
| Greedy initialization | 28,513.3397 |
| Density-diverse initialization, audit value | 19,031.7959 |

Here, `CLSCost` is the Stage I coverage/access objective under fixed `K=10`. If the distance from user `i` to the nearest selected server is `d_i`, the implementation evaluates `20 * sum_i(0 if d_i <= 1.5 km else 10*d_i)`. The values are therefore code-defined objective units, not the complete Stage II cost-delay objective. `BestBaselineCost` is 6,150.5741 from the best of the recorded random, density, distance-sum, and greedy initialization-only placements; the density-diverse value is reported separately for audit and does not change the minimum.

译：这里的 `CLSCost` 是固定 `K=10` 时的 Stage I 覆盖/access 目标值。若用户 `i` 到最近已选服务器的距离为 `d_i`，代码计算 `20 * sum_i(0 if d_i <= 1.5 km else 10*d_i)`。因此这些数值是代码定义的目标单位，不是 Stage II 的完整 cost-delay 目标。`BestBaselineCost=6150.5741` 来自记录到的 random、density、distance-sum 和 greedy 初始化结果中的最小值；density-diverse 作为补充审计值单独列出，不影响该最小值。

Across all five recorded non-CLS initial deployments, the minimum remains the best random trial at 6,150.5741; the separately audited density-diverse result is also worse. CLS therefore retains a clear Stage I advantage after moving to a geographically separate real-station topology and doubling the candidate count from 20 to 40.

译：在五类已记录的非 CLS 初始部署中，最小值仍是 random 的最好一次 6,150.5741，单独审计的 density-diverse 结果也更差。换到另一片真实基站区域并将候选基站数从 20 增加到 40 后，CLS 在 Stage I 中仍保持明显优势。

Stage II aggregate over three seeds:

| Method | HV mean +/- sample std | IGD mean +/- sample std | Best Q mean +/- sample std |
|---|---:|---:|---:|
| NS-P | 0.9574 +/- 0.0840 | 0.0498 +/- 0.0328 | 0.2953 +/- 0.0584 |
| GCP | 0.9799 +/- 0.0691 | 0.0446 +/- 0.0158 | 0.2800 +/- 0.0447 |
| GDP | 0.9742 +/- 0.0522 | 0.0408 +/- 0.0234 | 0.2733 +/- 0.0380 |
| **PSP** | **1.0116 +/- 0.0579** | **0.0129 +/- 0.0055** | **0.2678 +/- 0.0503** |

Complete per-seed Stage II values:

| Seed | Method | HV | IGD | Best Q | Primary-metric winner(s) |
|---:|---|---:|---:|---:|---|
| 42 | NS-P | 1.0481 | 0.0193 | 0.2344 | -- |
| 42 | GCP | 1.0478 | 0.0263 | 0.2421 | -- |
| 42 | GDP | 1.0252 | 0.0405 | 0.2385 | -- |
| 42 | **PSP** | **1.0490** | **0.0192** | **0.2273** | HV, IGD, Best Q |
| 43 | NS-P | 0.8824 | 0.0458 | 0.3509 | -- |
| 43 | GCP | 0.9097 | 0.0534 | 0.3293 | -- |
| 43 | **GDP** | 0.9208 | 0.0176 | **0.3139** | Best Q |
| 43 | **PSP** | **0.9448** | **0.0096** | 0.3241 | HV, IGD |
| 44 | NS-P | 0.9417 | 0.0845 | 0.3006 | -- |
| 44 | GCP | 0.9822 | 0.0542 | 0.2687 | -- |
| 44 | GDP | 0.9766 | 0.0643 | 0.2674 | -- |
| 44 | **PSP** | **1.0408** | **0.0100** | **0.2521** | HV, IGD, Best Q |

Compared with the strongest competing mean for each metric, PSP improves HV by 3.23%, reduces IGD by 68.28%, and reduces Best Q by 1.99%. PSP has the best HV and IGD in all three seeds and the best Best Q in two of the three seeds. The mean values of all three primary metrics are best for PSP.

译：相对于每个指标中最强的对比方法均值，PSP 的 HV 提高 3.23%，IGD 降低 68.28%，Best Q 降低 1.99%。在三个随机种子中，PSP 的 HV 和 IGD 均为最优，Best Q 在其中两个种子中最优；三个主要指标的跨种子均值均为 PSP 最优。

The three-seed comparison (`n=3`) is descriptive rather than an inferential significance test. The manuscript should therefore say “across the three tested seeds” instead of claiming statistical significance or universal stochastic robustness.

译：三个随机种子的比较（`n=3`）属于描述性稳定性检查，不是统计显著性检验。因此正文应写“在测试的三个随机种子中”，不能写成已经证明统计显著或普遍随机稳健。

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

Complete three-seed aggregate values (`mean +/- sample std`):

| Profile | Method | HV | IGD | Best Q |
|---|---|---:|---:|---:|
| Sparse | NS-P | 0.9610 +/- 0.0545 | 0.0461 +/- 0.0241 | 0.2534 +/- 0.0216 |
| Sparse | GCP | 0.9533 +/- 0.0116 | 0.0624 +/- 0.0269 | 0.2658 +/- 0.0170 |
| Sparse | **GDP** | **0.9781 +/- 0.0253** | **0.0397 +/- 0.0083** | **0.2421 +/- 0.0196** |
| Sparse | PSP | 0.9481 +/- 0.0234 | 0.0535 +/- 0.0052 | 0.2581 +/- 0.0189 |
| Clustered | NS-P | 0.9708 +/- 0.0163 | 0.0345 +/- 0.0147 | 0.2690 +/- 0.0097 |
| Clustered | **GCP** | **1.0104 +/- 0.0192** | **0.0086 +/- 0.0061** | **0.2558 +/- 0.0117** |
| Clustered | GDP | 0.9584 +/- 0.0390 | 0.0327 +/- 0.0213 | 0.2666 +/- 0.0078 |
| Clustered | PSP | 0.9520 +/- 0.0398 | 0.0432 +/- 0.0240 | 0.2631 +/- 0.0071 |
| Skewed | NS-P | 0.9886 +/- 0.0638 | 0.0550 +/- 0.0108 | 0.2264 +/- 0.0355 |
| Skewed | **GCP** | **1.0669 +/- 0.0293** | **0.0078 +/- 0.0034** | **0.2089 +/- 0.0360** |
| Skewed | GDP | 1.0523 +/- 0.0392 | 0.0215 +/- 0.0142 | 0.2140 +/- 0.0355 |
| Skewed | PSP | 1.0203 +/- 0.0578 | 0.0418 +/- 0.0163 | 0.2185 +/- 0.0377 |

All 36 Stage II method/configuration/seed records contain 50 evaluated solutions, all of which are nondominated within their corresponding method output under the computed objectives. The complete two-stage pipeline therefore remains executable in the expanded region, but this count alone is not evidence of superior solution quality. PSP is not uniformly best, and the relative benefit of Stage II initialization is distribution dependent.

译：36 条 Stage II 方法/配置/随机种子记录均包含 50 个已评价解，并且在对应方法输出和计算目标下均为方法内部非支配解。这个数量可以说明流程完成运行，但不能单独证明解质量更优。PSP 并非始终最优，Stage II 初始化机制的相对优势会受到流量分布影响。

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

> **Response:** Thank you for pointing out the limited geographical scope of the original evaluation. We have added two complementary generalization experiments using a pool of 2,215 real base-station coordinates in Beijing. First, we evaluated the complete two-stage framework in a geographically separate region whose candidate-station centroid is 24.20 km from that of the original Xizhimen setting. This case contains 40 candidate stations, 130 users, and 10 deployed servers. Its user-footprint area is comparable to the original case (1.02 times), so this experiment specifically evaluates transfer to a different real-station topology with twice as many candidate stations rather than spatial-scale expansion. In Stage I, CLS obtains a coverage/access objective value of 2,304.7670, compared with 6,150.5741 for the best recorded non-CLS initialization-only placement, corresponding to a 62.53% reduction. In Stage II, using a population of 50, 200 generations, and three random seeds, PSP obtains mean HV, IGD, and Best Q values of 1.0116, 0.0129, and 0.2678, respectively, which are the best mean values among NS-P, GCP, GDP, and PSP.
>
> We further conducted an expanded-region stress test using another real base-station topology. The user footprints are 2.25-2.88 times the area of the original setting, and sparse, clustered, and skewed traffic profiles were generated reproducibly. CLS reduces the Stage I coverage/access objective relative to the best recorded initialization-only placement by 26.63%, 34.82%, and 51.54%, respectively. All 36 Stage II method-profile-seed combinations completed and returned 50 evaluated solutions per method. However, the relative ranking of the Stage II initialization methods varies across traffic profiles, and PSP is not uniformly best in this more demanding setting. We report this result to clarify that the framework remains applicable under changed geography, larger spatial coverage, and traffic heterogeneity, while the benefit of a particular Stage II initialization strategy is distribution dependent.
>
> The revised manuscript now describes the new data construction, experimental settings, quantitative results, and scope of the generalization claim. We also clarify that the base-station coordinates are real, whereas the new heterogeneous user-traffic profiles are reproducibly generated and are not presented as measured population data.

### 对应中文

> **回复：** 感谢审稿人指出原始实验地理范围有限的问题。我们使用包含 2,215 个北京真实基站坐标的基站池，新增了两组互补的泛化实验。首先，我们在一片与原西直门设置明显分离的区域中完整评估两阶段框架，该区域候选基站质心与原区域相距 24.20 km，包含 40 个候选基站、130 个用户，并部署 10 台服务器。其用户覆盖面积与原案例接近（1.02 倍），因此该实验专门检验框架迁移到不同真实基站拓扑、且候选基站数量加倍后的表现，而不将其作为空间尺度扩大的证据。Stage I 中 CLS 的覆盖/access 目标值为 2,304.7670，而记录到的最好非 CLS 初始化部署为 6,150.5741，相当于降低 62.53%。Stage II 采用种群规模 50、200 代和三个随机种子，PSP 的平均 HV、IGD 和 Best Q 分别为 1.0116、0.0129 和 0.2678，均为 NS-P、GCP、GDP 和 PSP 四种方法中的最优均值。
>
> 我们还使用另一组真实基站拓扑进行了扩大区域压力测试。三种流量设置的用户覆盖面积为原设置的 2.25-2.88 倍，并以可复现方式生成 sparse、clustered 和 skewed 流量分布。相对于记录到的最好初始化部署，CLS 在 Stage I 中分别降低覆盖/access 目标值 26.63%、34.82% 和 51.54%。全部 36 个 Stage II 方法-流量分布-随机种子组合均完成运行，每种方法返回 50 个已评价解。但是，在这一更具挑战性的设置下，Stage II 初始化方法的相对排名会随流量分布变化，PSP 并非始终最优。该结果说明框架在改变地理位置、扩大空间覆盖和引入流量异质性后仍然适用，同时也表明特定 Stage II 初始化策略的收益具有分布依赖性。
>
> 修改后的稿件补充了新数据的构造方式、实验设置、定量结果和泛化结论的适用范围。我们还明确说明候选基站坐标来自真实数据，而新增的异构用户流量是可复现生成的，不将其描述为实际测量的人口数据。

## 6. Recommended manuscript text

### English text for the main manuscript

> **Geographical Generalization:** To evaluate transferability beyond the original Xizhimen setting, we constructed an additional MEC instance from real base-station coordinates in a geographically separate region of Beijing. The candidate-station centroid is 24.20 km from that of the original instance. The new instance contains 40 candidate stations, 130 reproducibly generated users, and 10 deployed servers, while its coverage-density coefficient of variation increases from 0.2336 to 0.3359. Its user-footprint area is 1.02 times that of the original instance; this case therefore evaluates geographical and station-topology transfer rather than spatial-scale expansion. In Stage I, CLS obtains a coverage/access objective value of 2,304.7670 and reduces the best recorded non-CLS initialization-only value by 62.53%. In Stage II, over three tested random seeds, PSP achieves mean HV, IGD, and Best Q values of 1.0116, 0.0129, and 0.2678, respectively, outperforming NS-P, GCP, and GDP in all three mean metrics. These results indicate that the proposed two-stage framework remains effective after changing the underlying real-station topology and increasing the number of candidate stations.

### 对应中文解释

> **地理泛化：** 为评估框架在原西直门设置之外的迁移能力，我们使用北京另一片区域的真实基站坐标构建了新的 MEC 实例。该实例候选基站质心与原实例相距 24.20 km，包含 40 个候选基站、130 个可复现生成的用户和 10 台部署服务器，其覆盖密度变异系数由 0.2336 增加到 0.3359。用户覆盖面积为原实例的 1.02 倍，因此该案例检验的是地理位置和基站拓扑迁移，而不是空间尺度扩大。Stage I 中 CLS 的覆盖/access 目标值为 2,304.7670，相对于记录到的最好非 CLS 初始化部署降低 62.53%。Stage II 在测试的三个随机种子下，PSP 的平均 HV、IGD 和 Best Q 分别为 1.0116、0.0129 和 0.2678，三个均值指标均优于 NS-P、GCP 和 GDP。结果表明，在更换真实基站拓扑并增加候选基站数量后，所提出的两阶段框架仍然有效。

### Optional text for the response or supplementary material

> To further assess scale and traffic heterogeneity, we expanded the user footprint to 2.25-2.88 times that of the original setting and generated reproducible sparse, clustered, and skewed traffic profiles over a common real-station topology. CLS reduces the best recorded Stage I initialization-only objective by 26.63%, 34.82%, and 51.54%, respectively. All 36 Stage II method-profile-seed combinations completed and returned 50 evaluated solutions per method. The relative ranking of the initialization strategies nevertheless varies across profiles, showing that the framework is portable but that the advantage of a specific Stage II initialization is distribution dependent.

### 对应中文解释

> 为进一步评估规模和流量异质性，我们将用户覆盖面积扩大到原设置的 2.25-2.88 倍，并在同一真实基站拓扑上可复现地生成 sparse、clustered 和 skewed 三种流量分布。CLS 相对于记录到的 Stage I 最好初始化目标值分别降低 26.63%、34.82% 和 51.54%。全部 36 个 Stage II 方法-流量分布-随机种子组合均完成运行，每种方法返回 50 个已评价解；但初始化策略的相对排名会随流量分布变化，说明框架具有可迁移性，而特定 Stage II 初始化策略的优势具有分布依赖性。

## 7. Figure and table captions

### Geography comparison

> **Fig. X. Geographical configurations used for the generalization evaluation.** The original Xizhimen instance is compared with a geographically separate real-station instance and an expanded real-station instance. Circles denote users, triangles denote candidate base stations, and stars denote the servers selected by CLS.

译：**图 X. 泛化评估使用的地理配置。** 对比原西直门实例、另一片真实基站实例和扩大范围的真实基站实例。圆点表示用户，三角形表示候选基站，星形表示 CLS 选择的服务器。

### Heterogeneous traffic

> **Fig. Y. Reproducible heterogeneous traffic profiles over the same expanded real-station topology.** The sparse, clustered, and skewed profiles use the same 40 real candidate stations, 130 users, and 10 selected servers. The user locations and requests are generated with fixed seeds; they are not presented as measured population data.

译：**图 Y. 同一扩大真实基站拓扑上的可复现异构流量分布。** sparse、clustered 和 skewed 三组实验使用相同的 40 个真实候选基站、130 个用户和 10 台部署服务器。用户位置和请求由固定随机种子生成，不作为真实人口测量数据表述。

### Main-candidate result summary

> **Fig. Z. Two-stage performance in the alternate real-station region.** Stage I reports the reduction in the CLS coverage/access objective relative to the best recorded initialization-only placement. Stage II reports the mean and sample standard deviation of HV, IGD, and Best Q over seeds 42, 43, and 44; higher HV and lower IGD/Best Q indicate better performance.

译：**图 Z. 另一真实基站区域中的两阶段性能。** Stage I 展示 CLS 覆盖/access 目标值相对于记录到的最好初始化部署的降幅；Stage II 展示随机种子 42、43 和 44 下 HV、IGD 和 Best Q 的均值与样本标准差，其中 HV 越高越好，IGD 和 Best Q 越低越好。

### Expanded-region result summary

> **Fig. S1. Generalization results in the expanded region.** Stage I reports the reduction in the CLS coverage/access objective relative to the best recorded initialization-only placement. Stage II reports the mean and sample standard deviation of HV, IGD, and Best Q over seeds 42, 43, and 44.

译：**图 S1. 扩大区域中的泛化结果。** Stage I 展示 CLS 覆盖/access 目标值相对于记录到的最好初始化部署的降幅；Stage II 展示随机种子 42、43 和 44 下 HV、IGD 和 Best Q 的均值与样本标准差。

## 8. Reproducibility commands

Generate the expanded-region datasets and Stage I results:

```powershell
$src='<path-to-station-pool.xlsx>'
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
- `output/png/reviewer6_main_candidate_results.png`
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
