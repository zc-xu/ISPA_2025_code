# Reviewer Comment 6: Geographical Generalization

## 1. Reviewer Comment

> In Section V, all experiments are conducted using a dataset collected within approximately a 9 km region around Xizhimen Subway Station in Beijing. However, the manuscript does not discuss the generalization capability of the proposed framework under different geographical distributions, heterogeneous traffic densities, or larger-scale MEC environments.

逐句翻译：

> 在第 V 节中，所有实验均使用在北京西直门地铁站周边约 9 km 范围内采集的数据集。然而，稿件没有讨论所提出框架在不同地理分布、异构流量密度或更大规模 MEC 环境下的泛化能力。

## 2. Added Generalization Experiment

The complete two-stage framework was evaluated on an additional MEC instance constructed from a pool of 2,215 real base-station coordinates in Beijing. The centroid of the new candidate-station topology is 24.20 km from that of the original Xizhimen instance. The number of candidate stations increases from 20 to 40, while the deployment contains 10 selected servers, 130 users, and eight service types.

The new instance also changes the spatial density structure. The mean nearest-neighbor distance between candidate stations decreases from 0.9451 km to 0.4038 km, and the coefficient of variation of user coverage density increases from 0.2336 to 0.3359. The fixed random seeds preserve the workload-generation protocol and make the complete experiment reproducible.

对应中文：

完整的两阶段框架在一个新增 MEC 实例上进行了评估。该实例从 2,215 个北京真实基站坐标中构建，新候选基站拓扑的质心与原西直门实例相距 24.20 km。候选基站数量由 20 增加到 40，部署设置包括 10 台选中服务器、130 个用户和 8 类服务。

新实例同时改变了空间密度结构。候选基站之间的平均最近邻距离由 0.9451 km 降至 0.4038 km，用户覆盖密度的变异系数由 0.2336 增至 0.3359。实验采用固定随机种子并沿用相同的工作负载生成协议，从而保证完整流程可复现。

### 2.1 Experimental settings

| Item | Setting |
|---|---:|
| Real Beijing base-station pool | 2,215 coordinates |
| Candidate stations | 40 |
| Deployed servers | 10 |
| Users | 130 |
| Service types | 8 |
| Distance from original candidate centroid | 24.20 km |
| Coverage radius in Stage I | 1.5 km |
| CLS maximum iterations in Stage I screening | 250 |
| Random initialization-only trials | 30 |
| Stage II population size | 50 |
| Stage II generations | 200 |
| Stage II random seeds | 42, 43, and 44 |
| DQN preference weights | 0.1, 0.3, 0.5, 0.7, and 0.9 |
| DQN training episodes per preference | 320 |

All Stage II population-based methods use the same Stage I server deployment within a run. NS-P, GCP, GDP, and PSP each return 50 service-provisioning solutions. DQN returns five independently trained preference-conditioned solutions. HV and IGD are calculated for the four equally sized population outputs. DQN is included in the common balanced-solution comparison through Best Q, evaluated for every method using the same per-seed normalization bounds and the fixed expression

`Q = 0.5 x normalized cost + 0.5 x normalized delay`.

对应中文：

同一次运行中的所有 Stage II 方法共享相同的 Stage I 服务器部署。NS-P、GCP、GDP 和 PSP 各返回 50 个服务配置解；DQN 返回 5 个分别训练的偏好条件解。HV 和 IGD 用于比较四个规模相同的种群输出。DQN 通过统一的平衡解指标 Best Q 参与比较：每个随机种子下的所有方法使用相同的归一化上下界，并固定采用 `Q = 0.5 x 归一化成本 + 0.5 x 归一化时延`，因此 Best Q 具有一致的评价尺度。

## 3. Verified Results

### 3.1 Stage I server deployment

| Method | Coverage/access objective | Direction |
|---|---:|---|
| Best recorded non-CLS initialization | 6,150.5741 | Lower is better |
| CLS | **2,304.7670** | Lower is better |

CLS reduces the Stage I coverage/access objective by **62.53%** relative to the best recorded non-CLS initialization-only placement.

对应中文：CLS 的 Stage I 覆盖/access 目标值为 2,304.7670，相比记录到的最好非 CLS 初始化部署 6,150.5741 降低 **62.53%**。

### 3.2 Stage II service provisioning

Mean and sample standard deviation over seeds 42, 43, and 44:

| Method | HV, higher is better | IGD, lower is better | Best Q, lower is better |
|---|---:|---:|---:|
| NS-P | 0.9574 +/- 0.0840 | 0.0498 +/- 0.0328 | 0.2953 +/- 0.0584 |
| GCP | 0.9799 +/- 0.0691 | 0.0446 +/- 0.0158 | 0.2800 +/- 0.0447 |
| GDP | 0.9742 +/- 0.0522 | 0.0408 +/- 0.0234 | 0.2733 +/- 0.0380 |
| PSP | **1.0116 +/- 0.0579** | **0.0129 +/- 0.0055** | **0.2678 +/- 0.0503** |
| DQN | -- | -- | 0.5517 +/- 0.1021 |

PSP obtains the highest mean HV and the lowest mean IGD and Best Q. Across the three tested seeds, PSP has the best HV and IGD in every run. Its mean Best Q is 51.45% lower than that of DQN under the common 0.5/0.5 evaluation.

对应中文：PSP 获得最高的平均 HV，以及最低的平均 IGD 和 Best Q。在三个随机种子的每次运行中，PSP 的 HV 和 IGD 均为最好。在统一的 0.5/0.5 评价下，PSP 的平均 Best Q 比 DQN 低 51.45%。

### 3.3 Complete per-seed population results

| Seed | Method | HV | IGD | Best Q |
|---:|---|---:|---:|---:|
| 42 | NS-P | 1.0481 | 0.0193 | 0.2344 |
| 42 | GCP | 1.0478 | 0.0263 | 0.2421 |
| 42 | GDP | 1.0252 | 0.0405 | 0.2385 |
| 42 | PSP | **1.0490** | **0.0192** | **0.2273** |
| 43 | NS-P | 0.8824 | 0.0458 | 0.3509 |
| 43 | GCP | 0.9097 | 0.0534 | 0.3293 |
| 43 | GDP | 0.9208 | 0.0176 | **0.3139** |
| 43 | PSP | **0.9448** | **0.0096** | 0.3241 |
| 44 | NS-P | 0.9417 | 0.0845 | 0.3006 |
| 44 | GCP | 0.9822 | 0.0542 | 0.2687 |
| 44 | GDP | 0.9766 | 0.0643 | 0.2674 |
| 44 | PSP | **1.0408** | **0.0100** | **0.2521** |

### 3.4 DQN balanced solutions under the common metric

For each seed, the table reports the best of the five DQN preference-conditioned outputs after all five are reevaluated using the common 0.5/0.5 Best Q definition.

| Seed | Training preference weight | Cost | Delay | Common Best Q |
|---:|---:|---:|---:|---:|
| 42 | 0.9 | 1,984.6548 | 218.2309 | 0.4388 |
| 43 | 0.5 | 2,115.1869 | 234.7720 | 0.6377 |
| 44 | 0.5 | 2,300.8531 | 232.9600 | 0.5785 |

## 4. Response to the Reviewer

### English

> **Response:** Thank you for highlighting the geographical scope of the original evaluation. We have added an end-to-end generalization experiment using a pool of 2,215 real base-station coordinates in Beijing. The new MEC instance is constructed in a geographically distinct region whose candidate-station centroid is 24.20 km from that of the original Xizhimen instance. It contains 40 candidate stations, twice the original number, together with 10 deployed servers, 130 users, and eight service types. The changed topology also exhibits a more heterogeneous coverage-density distribution: the density coefficient of variation increases from 0.2336 to 0.3359.
>
> In Stage I, CLS obtains a coverage/access objective value of 2,304.7670, compared with 6,150.5741 for the best recorded non-CLS initialization-only placement, corresponding to a 62.53% reduction. In Stage II, we use a population size of 50, 200 generations, and three random seeds. PSP achieves mean HV, IGD, and Best Q values of 1.0116, 0.0129, and 0.2678, respectively, which are the best mean values among NS-P, GCP, GDP, and PSP. PSP also achieves the best HV and IGD in each of the three runs.
>
> We further include the learning-based DQN baseline in the balanced-solution comparison. Five preference-conditioned DQN policies are trained for each seed, and all methods are evaluated using the same per-seed objective bounds and the same equal-weight normalized cost-delay metric. PSP obtains a mean Best Q of 0.2678, compared with 0.5517 for DQN. These results demonstrate that the complete MOS2 framework remains effective after changing the real base-station geography, doubling the candidate-station scale, and increasing spatial density heterogeneity.

### 中文对应翻译

> **回复：** 感谢审稿人指出原始实验地理范围方面的问题。我们使用包含 2,215 个北京真实基站坐标的基站池，新增了一组端到端泛化实验。新的 MEC 实例位于一个不同的地理区域，其候选基站质心与原西直门实例相距 24.20 km。该实例包含 40 个候选基站，是原实例的两倍，同时设置 10 台部署服务器、130 个用户和 8 类服务。新拓扑还呈现出更强的覆盖密度异质性，其密度变异系数由 0.2336 增至 0.3359。
>
> 在 Stage I 中，CLS 的覆盖/access 目标值为 2,304.7670，而记录到的最好非 CLS 初始化部署为 6,150.5741，相当于降低 62.53%。Stage II 采用种群规模 50、200 代和三个随机种子。PSP 的平均 HV、IGD 和 Best Q 分别为 1.0116、0.0129 和 0.2678，均为 NS-P、GCP、GDP 和 PSP 四种方法中的最优均值；而且 PSP 在三次运行中每次都获得最优的 HV 和 IGD。
>
> 我们还将学习型 DQN 基线纳入平衡解比较。每个随机种子分别训练 5 个偏好条件 DQN 策略，所有方法均使用相同的逐种子目标上下界和相同的等权归一化成本-时延指标进行评价。PSP 的平均 Best Q 为 0.2678，而 DQN 为 0.5517。结果表明，在更换真实基站地理区域、将候选基站规模扩大一倍并提高空间密度异质性后，完整的 MOS2 框架仍保持有效。

## 5. Text Added to Section V

### English manuscript text

> **Geographical Generalization:** To evaluate the framework beyond the original Xizhimen setting, we construct an additional MEC instance from a pool of 2,215 real base-station coordinates in Beijing. The candidate-station centroid of the new instance is 24.20 km from that of the original instance. It contains 40 candidate stations, 10 deployed servers, 130 users, and eight service types. Compared with the original instance, the candidate-station count is doubled and the coefficient of variation of user coverage density increases from 0.2336 to 0.3359, yielding a distinct and more heterogeneous spatial topology.
>
> CLS obtains a Stage-I coverage/access objective value of 2,304.7670, reducing the best recorded non-CLS initialization-only value of 6,150.5741 by 62.53%. For Stage II, Table X reports the mean and sample standard deviation over seeds 42, 43, and 44 using a population size of 50 and 200 generations. PSP achieves an HV of 1.0116 +/- 0.0579, an IGD of 0.0129 +/- 0.0055, and a Best Q of 0.2678 +/- 0.0503, giving the best mean value for all three metrics among the four population-based methods. Under the same equal-weight normalized cost-delay evaluation, DQN obtains a Best Q of 0.5517 +/- 0.1021. The complete two-stage framework therefore preserves its effectiveness under a different real base-station geography, a doubled candidate-station scale, and increased spatial density heterogeneity.

### 中文解释

> **地理泛化：** 为评估框架在原西直门设置之外的表现，我们从 2,215 个北京真实基站坐标中构建了一个新的 MEC 实例。新实例的候选基站质心与原实例相距 24.20 km，包含 40 个候选基站、10 台部署服务器、130 个用户和 8 类服务。与原实例相比，候选基站数量扩大一倍，用户覆盖密度变异系数由 0.2336 增至 0.3359，从而形成不同且异质性更强的空间拓扑。
>
> CLS 的 Stage I 覆盖/access 目标值为 2,304.7670，相比记录到的最好非 CLS 初始化值 6,150.5741 降低 62.53%。Stage II 采用种群规模 50、200 代，并在随机种子 42、43 和 44 上报告均值及样本标准差。PSP 的 HV、IGD 和 Best Q 分别为 1.0116 +/- 0.0579、0.0129 +/- 0.0055 和 0.2678 +/- 0.0503，在四种种群方法中三个指标的均值均为最好。在相同的等权归一化成本-时延评价下，DQN 的 Best Q 为 0.5517 +/- 0.1021。因此，在更换真实基站地理区域、将候选基站规模扩大一倍并提高空间密度异质性后，完整两阶段框架仍保持有效。

## 6. Figure and Table Captions

### Geography figure

> **Fig. X. Stage-I deployment in the new real-station region.** User markers are colored by the eight requested service types, gray circles denote unselected candidate stations, red stars denote the ten servers selected by CLS, dashed circles show the 1.5-km coverage radius, and gray segments show nearest-server assignments. The candidate-station centroid is 24.20 km from that of the original Xizhimen instance, and the candidate set contains 40 stations.

译：**图 X. 新真实基站区域中的 Stage I 部署。** 用户标记按 8 类请求服务着色，灰色圆点表示未选候选基站，红色星形表示 CLS 选中的 10 台服务器，红色虚线圆表示 1.5 km 覆盖半径，灰色连线表示用户到最近服务器的归属关系。该候选基站集合包含 40 个基站，其质心与原西直门实例相距 24.20 km。

### Performance figure

> **Fig. Y. Common balanced-solution performance in the new real-station region.** Bars and error bars report the mean and sample standard deviation of Best Q over seeds 42, 43, and 44 for NS-P, PSP, GCP, GDP, and DQN. Lower Best Q indicates a better normalized cost-delay trade-off.

译：**图 Y. 新真实基站区域中的统一平衡解性能。** 柱形和误差棒分别给出 NS-P、PSP、GCP、GDP 和 DQN 在随机种子 42、43 和 44 下 Best Q 的均值与样本标准差。Best Q 越低，表示归一化成本-时延折中越好。

### Stage II table

> **Table X. Stage-II performance in the new real-station region.** Values are mean +/- sample standard deviation over three random seeds. HV and IGD compare population-based outputs of equal size. Best Q uses the same per-seed normalization bounds and equal cost-delay weights for every method.

译：**表 X. 新真实基站区域中的 Stage II 性能。** 数值为三个随机种子下的均值 +/- 样本标准差。HV 和 IGD 比较规模相同的种群输出；Best Q 对所有方法使用相同的逐种子归一化上下界以及相同的成本-时延等权设置。

## 7. Reproducibility Files

### Code

- `LocalSearch/real_region_generalization.py`: constructs real-station MEC instances and runs Stage I screening.
- `LocalSearch/run_real_region_stage2.py`: runs NS-P, GCP, GDP, and PSP with separate seed-level NPZ archives.
- `LocalSearch/dqn_service_baseline.py`: trains and evaluates the DQN baseline with fixed-alpha cross-method Best Q.
- `LocalSearch/reviewer6_generalization_summary.py`: validates and consolidates the evidence CSV files.
- `LocalSearch/plot_reviewer6_topology.py`: renders the service-aware geographical topology and Stage-I deployment.
- `LocalSearch/plot_reviewer6_bestq.py`: renders the five-method Best-Q comparison with sample-standard-deviation error bars.
- `LocalSearch/build_reviewer6_paper_workbook.mjs`: applies the paper chart template and creates the auditable evidence workbook.

### Data and tables

- `data/real_region/input_data_real_sparse_r04_c40_u130_k10_s1_8.xlsx`
- `output/csv/reviewer6_generalization_design.csv`
- `output/csv/reviewer6_main_candidate_stage1.csv`
- `output/csv/reviewer6_main_candidate_stage2_detail.csv`
- `output/csv/reviewer6_main_candidate_stage2_aggregate.csv`
- `output/csv/reviewer6_main_candidate_dqn_weighted.csv`
- `output/csv/reviewer6_main_candidate_bestq_detail.csv`
- `output/csv/reviewer6_main_candidate_bestq_aggregate.csv`
- `output/excel/reviewer6_generalization_paper_style.xlsx`

### Figures

- `output/png/reviewer6_generalization_topology.png`
- `output/pdf/reviewer6_generalization_topology.pdf`
- `output/png/reviewer6_generalization_bestq.png`
- `output/pdf/reviewer6_generalization_bestq.pdf`

### Reproduction commands

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\run_real_region_stage2.py `
  --screen-csv output\csv\real_region_stage1_screen_c40_u130_k10.csv `
  --configs real_sparse_r04_c40_u130_k10_s1 `
  --pop-size 50 --n-gen 200 --seed 42 `
  --output-prefix reviewer6_main_stage2_seed42_refresh --archive-npz
```

Repeat the command with seeds 43 and 44 and the corresponding output prefixes.

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\dqn_service_baseline.py `
  --screen-csv output\csv\real_region_stage1_screen_c40_u130_k10.csv `
  --configs real_sparse_r04_c40_u130_k10_s1 `
  --weights 0.1 0.3 0.5 0.7 0.9 `
  --episodes 320 --dqn-seeds 42 43 44 `
  --stage-seed 42 --stage1-iter 200 `
  --reference-by-seed --evaluation-alpha 0.5

.\LocalSearch\Scripts\python.exe .\LocalSearch\reviewer6_generalization_summary.py
.\LocalSearch\Scripts\python.exe .\LocalSearch\plot_reviewer6_topology.py
.\LocalSearch\Scripts\python.exe .\LocalSearch\plot_reviewer6_bestq.py
node .\LocalSearch\build_reviewer6_paper_workbook.mjs
```
