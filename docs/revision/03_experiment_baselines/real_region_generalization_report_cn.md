# 真实基站区域泛化实验汇报

完整的 Reviewer 2 Comment 6 实验设计、三随机种子结果、英文回复和正文文字见 `reviewer6_geographical_generalization_response.md`。本文件保留正文候选的简要汇报，最新扩大区域压力测试结果以该详细文档和 `reviewer6_*` 输出文件为准。

## 目标

针对审稿意见 6，需要说明 MOS2 框架不仅适用于原稿中西直门附近的实验区域，也能在不同地理分布、异构流量密度或更大 MEC 环境下工作。

本次实验使用原始北京基站数据：

- 原始文件：北京基站池 Excel（本地路径不写入公开仓库）
- 读取方式：通过命令行参数 `--password` 或环境变量 `MEC_STATION_POOL_PASSWORD` 提供密码
- 成功读取并去重后的北京基站坐标数：2215

## 新增代码

1. `LocalSearch/real_region_generalization.py`
   - 直接读取加密 Excel；
   - 自动识别经纬度列；
   - 从真实基站池中按“以某个中心点向外扩散”的方式选候选基站；
   - 生成 sparse、clustered、mixed、skewed 用户分布；
   - 批量运行 Stage I，并生成地理分布图。

2. `LocalSearch/run_real_region_stage2.py`
   - 从 Stage I 筛选结果中指定配置；
   - 用统一的 `pop_size=50, n_gen=200` 运行 Stage II；
   - 生成 Pareto 图、指标图、CSV 和 Excel。

## 最终推荐主候选

建议主用配置：

`real_sparse_r04_c40_u130_k10_s1`

这个配置的含义：

- 真实基站候选数：40
- 部署服务器数：10
- 用户数：130
- 服务类型数：8
- 用户分布：sparse
- 区域中心坐标约为：`116.0938, 40.1078`
- 与原西直门候选基站质心距离：`24.20 km`
- 用户范围约为：`6.70 km x 8.70 km`
- 用户覆盖面积相对原实验：`1.0172` 倍
- 覆盖密度变异系数：`0.3359`

与原 `10_130` 数据相比，它不是简单的西直门重复实验，而是从真实基站池重新选择的另一组区域，并且候选基站数量从 20 增加到 40，覆盖密度异质性更强。它的用户覆盖面积仅为原实验的 `1.02` 倍，所以主候选用于证明地理位置和真实基站拓扑迁移，不能单独用来证明空间尺度扩大。基站坐标来自真实数据，用户位置和请求由固定随机种子生成，不能表述为实测人口或运营商流量。

## Stage I 结果

实验设置为覆盖半径 `1.5 km`、CLS 最大迭代数 `250`、30 次随机初始化基线试验。该配置的生成与 Stage I 派生随机种子为 `4060`（基础种子为 42）。

| 配置 | 候选基站 | 用户 | 部署服务器 | CLS cost | 最好基线 cost | CLS 优势 |
|---|---:|---:|---:|---:|---:|---:|
| `real_sparse_r04_c40_u130_k10_s1` | 40 | 130 | 10 | 2304.7670 | 6150.5741 | 62.5276% |

完整 Stage I 审计值：

| 部署结果 | 覆盖/access 目标值 |
|---|---:|
| CLS 局部搜索结果 | **2304.7670** |
| Random 30 次均值 | 13540.5175 |
| Random 30 次最好值 | **6150.5741** |
| Density 初始化 | 22206.4751 |
| Distance-sum 初始化 | 28513.3397 |
| Greedy 初始化 | 28513.3397 |
| Density-diverse 初始化（补充审计） | 19031.7959 |

`CLSCost` 的定义是：固定 `K=10` 时，用户距最近所选服务器不超过 `1.5 km` 则贡献 0，否则按 `20 x 10 x 距离` 累加。它是代码定义的 Stage I 覆盖/access 目标值，不是 Stage II 的完整 cost-delay 目标。

Stage I 结论：

CLS 在该真实区域中明显优于记录到的随机、密度、距离、贪心和 density-diverse 初始化部署。这个结果可以支撑“服务器选址阶段具有地理泛化能力”的回应。

## Stage II 结果

论文级参数：

- `pop_size=50`
- `n_gen=200`
- seeds 42、43、44

seed 42 的完整单次结果：

| 方法 | HV | IGD | Spacing | BestQ |
|---|---:|---:|---:|---:|
| NS-P | 1.0481 | 0.0193 | 0.0101 | 0.2344 |
| GCP | 1.0478 | 0.0263 | 0.0081 | 0.2421 |
| GDP | 1.0252 | 0.0405 | 0.0042 | 0.2385 |
| PSP | 1.0490 | 0.0192 | 0.0075 | 0.2273 |

指标含义：

- HV 越高越好；
- IGD 越低越好；
- BestQ 越低越好；
- Spacing 越低表示解分布更均匀，但不作为主要胜负指标。

Stage II seed 42 结论：

PSP 同时取得最优 HV、IGD 和 BestQ。

三个种子的均值和样本标准差：

| 方法 | HV | IGD | BestQ |
|---|---:|---:|---:|
| NS-P | 0.9574 +/- 0.0840 | 0.0498 +/- 0.0328 | 0.2953 +/- 0.0584 |
| GCP | 0.9799 +/- 0.0691 | 0.0446 +/- 0.0158 | 0.2800 +/- 0.0447 |
| GDP | 0.9742 +/- 0.0522 | 0.0408 +/- 0.0234 | 0.2733 +/- 0.0380 |
| **PSP** | **1.0116 +/- 0.0579** | **0.0129 +/- 0.0055** | **0.2678 +/- 0.0503** |

相对各指标中最强的其他方法均值，PSP 的 HV 提高 `3.23%`，IGD 降低 `68.28%`，BestQ 降低 `1.99%`。由于仅有三个种子，这属于描述性稳定性检查，不是统计显著性检验。

## 多 seed 检查

固定 Stage I 服务器部署不变，只改变 Stage II NSGA-II 随机种子：

| Seed | PSP 是否 best HV | PSP 是否 best IGD | PSP 是否 best BestQ | 得分 |
|---:|---:|---:|---:|---:|
| 42 | 是 | 是 | 是 | 3 |
| 43 | 是 | 是 | 否 | 2 |
| 44 | 是 | 是 | 是 | 3 |

更稳妥的表述：

PSP 在 3 个种子中均取得最优 HV 和 IGD，在 2 个种子中取得最优 BestQ。因此可以说 PSP 在该真实区域中表现出更好的 Pareto 覆盖和收敛质量，但不要写成“所有随机种子下所有指标都绝对最优”。

## 扩大区域压力测试

为了直接回应“不同流量密度和更大 MEC 环境”，在同一组 40 个真实候选基站上构建 sparse、clustered 和 skewed 三种可复现用户流量。区域参考中心约为 `116.0321, 39.9929`，候选基站半径为 11.84 km，用户覆盖面积约为原实验的 2.25--2.88 倍。

| 流量分布 | 用户范围 | 密度 CV | CLS 目标值 | 最好基线 | CLS 优势 | Stage II 均值最优方法 |
|---|---:|---:|---:|---:|---:|---|
| Sparse | 13.30 km x 12.40 km | 0.5409 | 23479.4626 | 32001.1812 | 26.63% | GDP |
| Clustered | 11.56 km x 11.15 km | 0.5343 | 7859.9883 | 12058.5490 | 34.82% | GCP |
| Skewed | 12.63 km x 11.08 km | 0.6001 | 4924.3671 | 10162.4348 | 51.54% | GCP |

扩大区域说明：

- CLS 在三种流量分布下均明显优于记录到的最好 Stage I 初始化基线；
- 三种配置均以 `pop_size=50`、`n_gen=200` 和 seed 42/43/44 完成 Stage II；
- 全部 36 个方法-流量分布-随机种子组合均完成运行，每种方法返回 50 个已评价解；这些解在各自方法输出内均为非支配解，但解的数量本身不能证明质量更优；
- PSP 并非在三种扩大区域流量下都最优；
- 该结果适合作为 response letter 或补充材料中的压力测试，用于说明完整流程可迁移，同时诚实限定 Stage II 初始化优势具有分布依赖性。

## 建议写入论文/回复信的方式

推荐主张：

1. 新增一个真实基站泛化实验，使用从北京基站池重新选择的非西直门区域。
2. 该实验采用 40 个候选基站、10 个部署服务器和 130 个用户。
3. Stage I 中 CLS 相比记录到的最好初始化部署降低 62.53% 的覆盖/access 目标值。
4. Stage II 中 PSP 的三个种子平均 HV、IGD 和 BestQ 均为最优；在各个种子上，PSP 的 HV 和 IGD 均最优，BestQ 在两个种子中最优。

不建议主张：

- 不要说“所有地理区域下都最优”；
- 不要说“所有随机种子下所有指标都最优”；
- 不要把 lightweight 30/60 的结果当主证据；
- 不要把 wide-only 结果作为主图，因为其 Stage II 稳定性不足。

## 已检查图表

主候选图：

- `output/png/real_region_topology_real_sparse_r04_c40_u130_k10_s1.png`
- `output/png/pareto_front_real_sparse_r04_c40_u130_k10_s1.png`
- `output/png/pareto_metrics_real_sparse_r04_c40_u130_k10_s1.png`

审稿意见 6 最终组图：

- `output/png/reviewer6_geography_comparison.png`
- `output/png/reviewer6_heterogeneous_traffic.png`
- `output/png/reviewer6_main_candidate_results.png`
- `output/png/reviewer6_large_region_results.png`
- 对应矢量 PDF 位于 `output/pdf/`

最终数据表：

- `output/csv/reviewer6_generalization_design.csv`
- `output/csv/reviewer6_main_candidate_stage2_detail.csv`
- `output/csv/reviewer6_main_candidate_stage2_aggregate.csv`
- `output/csv/reviewer6_large_region_stage1.csv`
- `output/csv/reviewer6_large_region_stage2_detail.csv`
- `output/csv/reviewer6_large_region_stage2_aggregate.csv`
- `output/excel/reviewer6_generalization_evidence.xlsx`
