# 真实基站地理泛化实验报告

## 实验目标

本实验用于验证 MOS2 完整两阶段框架在更换真实基站地理区域、扩大候选基站规模并改变空间密度结构后能否保持有效。

## 数据与实例

- 北京真实基站坐标池：2,215 个去重坐标。
- 实验配置：`real_sparse_r04_c40_u130_k10_s1`。
- 输入文件：`data/real_region/input_data_real_sparse_r04_c40_u130_k10_s1_8.xlsx`。
- 候选基站：40 个；原西直门实例为 20 个。
- 部署服务器：10 台。
- 用户：130 个。
- 服务类型：8 类。
- 新旧候选基站质心距离：24.2044 km。
- 候选基站平均最近邻距离：由 0.9451 km 变为 0.4038 km。
- 用户覆盖密度变异系数：由 0.2336 增至 0.3359。

该实例同时体现了地理位置变化、真实基站拓扑变化、候选基站数量扩大和覆盖密度异质性增强。

## Stage I：服务器放置

实验参数：

- 覆盖半径：1.5 km。
- CLS 最大迭代数：250。
- 随机初始化基线试验：30 次。
- 数据生成及 Stage I 派生随机种子：4060，基础种子为 42。

完整结果：

| 策略 | 覆盖/access 目标值 |
|---|---:|
| CLS | **2,304.7670** |
| Random 30 次均值 | 13,540.5175 |
| Random 30 次最好值 | 6,150.5741 |
| Density | 22,206.4751 |
| Distance-sum | 28,513.3397 |
| Greedy | 28,513.3397 |
| Density-diverse | 19,031.7959 |

记录到的最好非 CLS 初始化部署为 Random 的最好值 6,150.5741。CLS 将目标值降至 2,304.7670，降幅为 **62.5276%**。

这里的 Stage I 目标用于衡量固定服务器数量下的覆盖/access 代价，数值越低越好。它与 Stage II 的部署成本和用户时延目标相互独立。

## Stage II：服务配置

共同参数：

- 种群规模：50。
- 进化代数：200。
- 随机种子：42、43、44。
- 四种种群方法：NS-P、GCP、GDP、PSP。
- 同一次运行中的四种方法共享相同的 Stage I 服务器部署。

三种子均值和样本标准差：

| 方法 | HV，越高越好 | IGD，越低越好 | Best Q，越低越好 |
|---|---:|---:|---:|
| NS-P | 0.9574 +/- 0.0840 | 0.0498 +/- 0.0328 | 0.2953 +/- 0.0584 |
| GCP | 0.9799 +/- 0.0691 | 0.0446 +/- 0.0158 | 0.2800 +/- 0.0447 |
| GDP | 0.9742 +/- 0.0522 | 0.0408 +/- 0.0234 | 0.2733 +/- 0.0380 |
| PSP | **1.0116 +/- 0.0579** | **0.0129 +/- 0.0055** | **0.2678 +/- 0.0503** |

逐种子结果：

| Seed | 方法 | HV | IGD | Best Q |
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

PSP 的平均 HV 最高，平均 IGD 和平均 Best Q 最低；并且在三个随机种子下，每次都获得最优 HV 和 IGD。

## DQN 对比

DQN 在每个随机种子下分别训练 5 个偏好条件策略，偏好权重为 0.1、0.3、0.5、0.7 和 0.9，每个策略训练 320 个 episode。每个 DQN 输出均使用与对应种子四种种群方法相同的 cost/delay 归一化上下界，并统一按下式重新评价：

`Best Q = 0.5 x normalized cost + 0.5 x normalized delay`。

每个种子的 DQN 最好平衡解：

| Seed | 产生该解的训练权重 | Cost | Delay | 统一 Best Q |
|---:|---:|---:|---:|---:|
| 42 | 0.9 | 1,984.6548 | 218.2309 | 0.4388 |
| 43 | 0.5 | 2,115.1869 | 234.7720 | 0.6377 |
| 44 | 0.5 | 2,300.8531 | 232.9600 | 0.5785 |
| 均值 +/- 样本标准差 | - | - | - | **0.5517 +/- 0.1021** |

PSP 的平均 Best Q 为 0.2678，比 DQN 的 0.5517 低 **51.45%**。

DQN 每个种子返回 5 个偏好解，而四种种群方法各返回 50 个解。因此 HV 和 IGD 用于四种等规模种群输出之间的比较，DQN 通过采用完全相同定义的 Best Q 参与平衡解比较，避免输出解集规模差异影响结论。

## 结论

1. 更换真实基站地理区域并将候选基站数量由 20 增至 40 后，CLS 在 Stage I 中仍将最好非 CLS 初始化目标值降低 62.53%。
2. PSP 在 Stage II 的三个随机种子上每次都获得最好 HV 和 IGD，三个核心指标的平均值也均为四种种群方法中的最好结果。
3. 加入学习型 DQN 后，PSP 的统一平均 Best Q 仍明显更低。
4. 完整两阶段框架在不同真实基站拓扑、更大的候选基站规模和更高的空间密度异质性下保持有效。

## 复现与产物

代码：

- `LocalSearch/real_region_generalization.py`
- `LocalSearch/run_real_region_stage2.py`
- `LocalSearch/dqn_service_baseline.py`
- `LocalSearch/reviewer6_generalization_summary.py`
- `LocalSearch/plot_reviewer6_topology.py`
- `LocalSearch/plot_reviewer6_bestq.py`
- `LocalSearch/build_reviewer6_paper_workbook.mjs`

汇总数据：

- `output/csv/reviewer6_generalization_design.csv`
- `output/csv/reviewer6_main_candidate_stage1.csv`
- `output/csv/reviewer6_main_candidate_stage2_detail.csv`
- `output/csv/reviewer6_main_candidate_stage2_aggregate.csv`
- `output/csv/reviewer6_main_candidate_dqn_weighted.csv`
- `output/csv/reviewer6_main_candidate_bestq_detail.csv`
- `output/csv/reviewer6_main_candidate_bestq_aggregate.csv`
- `output/excel/reviewer6_generalization_paper_style.xlsx`

图：

- `output/png/reviewer6_generalization_topology.png`
- `output/pdf/reviewer6_generalization_topology.pdf`
- `output/png/reviewer6_generalization_bestq.png`
- `output/pdf/reviewer6_generalization_bestq.pdf`

复现命令见 `reviewer6_geographical_generalization_response.md` 第 7 节。
