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
- 用户范围约为：`6.70 km x 8.70 km`
- 覆盖密度变异系数：`0.3359`

与原 `10_130` 数据相比，它不是简单的西直门重复实验，而是从真实基站池重新选择的另一组区域，并且候选基站数量从 20 增加到 40，覆盖密度异质性更强。

## Stage I 结果

| 配置 | 候选基站 | 用户 | 部署服务器 | CLS cost | 最好基线 cost | CLS 优势 |
|---|---:|---:|---:|---:|---:|---:|
| `real_sparse_r04_c40_u130_k10_s1` | 40 | 130 | 10 | 2304.7670 | 6150.5741 | 62.5276% |

Stage I 结论：

CLS 在该真实区域中明显优于随机、密度、距离和贪心初始化基线。这个结果可以支撑“服务器选址阶段具有地理泛化能力”的回应。

## Stage II 结果

论文级参数：

- `pop_size=50`
- `n_gen=200`
- seed 42

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

| 流量分布 | 用户范围 | 密度 CV | Stage I CLS 优势 | Stage II 均值最优方法 |
|---|---:|---:|---:|---|
| Sparse | 13.30 km x 12.40 km | 0.5409 | 26.63% | GDP |
| Clustered | 11.56 km x 11.15 km | 0.5343 | 34.82% | GCP |
| Skewed | 12.63 km x 11.08 km | 0.6001 | 51.54% | GCP |

扩大区域说明：

- CLS 在三种流量分布下均明显优于记录到的最好 Stage I 初始化基线；
- 三种配置均以 `pop_size=50`、`n_gen=200` 和 seed 42/43/44 完成 Stage II；
- 全部方法均产生 50 个有效非支配解，但 PSP 并非在三种扩大区域流量下都最优；
- 该结果适合作为 response letter 或补充材料中的压力测试，用于说明完整流程可迁移，同时诚实限定 Stage II 初始化优势具有分布依赖性。

## 建议写入论文/回复信的方式

推荐主张：

1. 新增一个真实基站泛化实验，使用从北京基站池重新选择的非西直门区域。
2. 该实验采用 40 个候选基站、10 个部署服务器和 130 个用户。
3. Stage I 中 CLS 相比最好初始化基线降低 62.53% 的部署/access cost。
4. Stage II 中 PSP 在 seed 42 下获得最优 HV、IGD 和 BestQ；多 seed 检查中 PSP 的 HV 和 IGD 优势稳定。

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

最终汇总表：

- `output/csv/real_region_final_candidate_summary.csv`
- `output/excel/real_region_final_candidate_summary.xlsx`

多 seed 检查：

- `output/csv/real_region_stage2_c40_sparse_r04_seed_check.csv`
- `output/excel/real_region_stage2_c40_sparse_r04_seed_check.xlsx`
