# MOS2 Revision Progress Mapping

本文档用于向导师汇报当前返修进展，并把审稿意见与当前保留的代码修改逐条对应起来。当前版本保留可复现性、批量实验入口、Pareto 指标、CLS 初始化敏感性、混合锚点参数化、地理泛化、小规模联合优化对比，以及 Stage II 的 DQN 学习型基线。

## 0. 当前结论

1. 当前 Stage II 对比方法为：`NS-P`、`GCP`、`GDP`、`PSP`、`DQN`。
2. DQN 作为学习型 baseline 纳入可复现实验，但只以独立偏好点、指标表和控制变量柱状图展示，不把五个点连接成连续 Pareto curve。
3. 已保留数据集配置表、批量运行入口、Pareto 指标计算和统一风格图表生成，方便后续切换不同规模数据集复现实验。
4. 主展示指标建议保留 `HV`、`IGD`、`Best Q`；`Spacing` 仅保留在 CSV 中作为可追溯指标，不作为主图指标。

> 2026-07-14 更新：本文件后文若仍出现“DQN 未纳入”的旧状态描述，以本节和 `dqn_stage2_baseline_report.md` 为准。SPEA2 仍不纳入，因为它不是 learning-based service placement 方法。

## 1. 审稿意见与当前修改结果总表

| 审稿意见 | 审稿人真正关心的问题 | 当前保留修改 | 支撑文件/结果 | 下一步建议 |
|---|---|---|---|---|
| Stage II 对比实验不够充分。 | 审稿人希望看到 learning-based service placement baseline 和定量评价。 | 已加入可复现 DQN，完成七组控制变量实验；五个偏好结果作为独立点和柱状图展示，不连接成连续 Pareto curve。 | `LocalSearch/dqn_service_baseline.py`；`LocalSearch/plot_dqn_control_results.py`；`docs/revision/03_experiment_baselines/dqn_stage2_baseline_report.md`。 | 正文补充 DQN 建模、训练预算和结果边界；SPEA2 不纳入。 |
| CLS 初始化敏感性解释不足。 | Algorithm 1 的初始部署集合 `S` 随机生成，审稿人担心不同初值导致不同局部最优。 | 已新增 CLS 初始化敏感性实验，对比 random、density、distance-sum、greedy、density-diverse 五类初值。主图改为固定 130 用户规模 heatmap；另提供 `10_150` Random vs Greedy 辅助图。 | `LocalSearch/cls_initialization_sensitivity.py`；`output/pdf/cls_init_sensitivity_130_heatmap.pdf`；`output/pdf/cls_init_random_vs_greedy_10_150.pdf`；`output/csv/cls_init_sensitivity_all_data_scan.csv`。 | 正文主结论写 CLS 对初始化整体不敏感；辅助结论写单纯 Greedy 不一定更好。不要写 Random 普遍优于所有初始化。 |
| 缺少 Pareto front 定量指标。 | 原稿主要依赖散点图和加权 Q，缺少通用指标。 | 已新增 `HV`、`IGD`、`Best Q`，并生成 CSV、Excel、PDF、PNG。 | `LocalSearch/pareto_batch_metrics.py`；`output/pdf/pareto_metrics_10_130.pdf`。 | 正文说明指标方向：`HV` 越高越好；`IGD`、`Best Q` 越低越好。 |
| 多规模实验数据对应关系不清楚。 | 代码仓库里 Excel 较多，难以判断哪个文件对应哪组论文实验。 | 已新增显式配置清单，列出 7 组候选实验配置、用户规模、服务器规模、`sigma_min` 和 `n2_adjust`。 | `LocalSearch/experiment_configs.py`；`output/csv/experiment_config_manifest.csv`。 | 后续如需完整复现实验，可直接用 `--configs all` 或指定配置名。 |
| 两阶段分解合理性不足。 | 审稿人担心先服务器部署、再服务部署会牺牲全局最优性。 | 新增小规模 Joint-Exact 对比。6 candidates/30 users/3 servers/4 services 的三个种子中，Best Q gap 均为 0，平均 HV gap 为 3.87%，联合穷举平均约慢 5.85 倍。 | `LocalSearch/joint_optimality_gap.py`；`output/csv/joint_gap_summary_c6_u30_k3_s4_seeds42_44.csv`。 | 写入正文与 response；明确这是小规模经验差距，不是理论最优性保证。 |
| `varpi_j` 选择依据不足。 | 确定性 anchor 大小看似任意，缺少与容量 `V_j` 的关系。 | 将 `varpi_j` 和 `V_j` 参数化，并完成 144 次容量敏感性运行。保留 `varpi_j=ceil(0.5V_j)` 作为 exploitation/exploration 的比例式默认折中。 | `LocalSearch/hybrid_anchor_sensitivity.py`；`docs/revision/03_experiment_baselines/hybrid_anchor_sensitivity.md`。 | 不声称半容量稳定最优；实验可放 response 或补充材料。 |
| 地理和流量泛化不足。 | 原稿只在西直门附近数据上验证。 | 新增三组合成分布和真实北京稀疏区域实例。最终真实候选为 40 candidates/130 users/10 servers，Stage I CLS 优势 62.53%；Stage II 多种子下 PSP 的 HV/IGD 优势稳定。 | `LocalSearch/generalization_experiments.py`；`LocalSearch/real_region_generalization.py`；`LocalSearch/run_real_region_stage2.py`。 | 正文使用真实区域结果；合成结果谨慎放 response/补充材料。 |
| 变量定义和符号不统一。 | 公式可读性和模型可信度受影响。 | 已统一服务部署、关联和容量相关符号，并补充归一化 cost/delay 和 Q 定义。 | `D:\NDM\conference_101719.tex`。 | 后续编译后检查公式编号、表格和正文引用。 |
| QoS/reliability 讨论不足。 | 实际 MEC 场景还涉及丢包、中断、链路可用性等可靠性因素。 | 已加入 reliability-aware QoS 讨论，作为模型可扩展约束和未来工作。 | `D:\NDM\conference_101719.tex`。 | 当前不扩展实验，避免返修工作量失控。 |
| 图示解释不足。 | Fig. 1/Fig. 2 对服务器区域、服务路径和流程机制说明不够。 | 已修改 caption；图本身等待 Visio 源文件后再统一重画。 | `D:\NDM\conference_101719.tex`。 | 拿到 Visio 后简化路径、突出 Stage I/Stage II、保持论文图风格一致。 |

## 2. 当前代码保留内容

| 文件 | 用途 |
|---|---|
| `LocalSearch/experiment_configs.py` | 统一管理不同实验规模的数据文件、目标服务器数和参数修正。 |
| `LocalSearch/experiment_utils.py` | 提供无副作用的数据读取、Stage I 上下文构造、用户分配等复用工具。 |
| `LocalSearch/batch_service_experiments.py` | 批量运行入口，可按配置名重跑 Stage I + Stage II。 |
| `LocalSearch/pareto_batch_metrics.py` | 读取结果文件，计算 Pareto 指标，生成 CSV/Excel/PDF/PNG。 |
| `LocalSearch/cls_initialization_sensitivity.py` | 对比不同 CLS 初始化策略，输出初始化敏感性表格和图。 |
| `LocalSearch/hybrid_anchor_sensitivity.py` | 测试不同 `V_j`、`varpi_j`、配置和随机种子。 |
| `LocalSearch/generalization_experiments.py` | 生成并运行三类可复现合成地理分布。 |
| `LocalSearch/real_region_generalization.py` | 从真实北京基站池筛选不同区域并运行 Stage I。 |
| `LocalSearch/run_real_region_stage2.py` | 对保存的真实区域候选运行 Stage II。 |
| `LocalSearch/joint_optimality_gap.py` | 小规模 Joint-Exact 与 MOS2-PSP 对比。 |
| `LocalSearch/dqn_service_baseline.py` | 可复现 DQN 学习型服务放置 baseline。 |
| `LocalSearch/plot_dqn_control_results.py` | 生成 paper-aligned 与 full-rerun 两套 DQN 控制变量图。 |

## 3. 当前可用命令

生成 10/130 指标和图：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\pareto_batch_metrics.py --config 10_130
```

生成 5/130 指标和图：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\pareto_batch_metrics.py --config 5_130
```

重跑 10/130 的原有四类 Stage II 方法：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\batch_service_experiments.py --configs 10_130
```

查看可选配置：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\batch_service_experiments.py --help
```

运行 CLS 初始化敏感性实验：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\cls_initialization_sensitivity.py --configs all_new --random-runs 50 --seed 42 --max-iter 200
```

运行混合锚点容量敏感性实验：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\hybrid_anchor_sensitivity.py --configs 10_130 10_150 10_180 5_130 15_130 20_130 --capacities 4 8 --varpi-values 1 half 3 Vj --seeds 42 43 44 --pop-size 50 --n-gen 200
```

使用已保存结果汇总合成泛化实验：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\generalization_experiments.py --scenarios sparse_suburban uniform_large clustered_hotspot --skip-nsga
```

运行一个小规模 Joint-Exact 对比：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\joint_optimality_gap.py --n-candidates 6 --k 3 --n-users 30 --num-services 4 --capacity 4 --seed 42
```

## 4. 当前 10/130 指标结果

| Method | HV ↑ | IGD ↓ | Best Q ↓ |
|---|---:|---:|---:|
| NS-P | 0.8191 | 0.0785 | 0.3894 |
| GCP | 0.8596 | 0.0492 | 0.3550 |
| GDP | 0.8945 | 0.0326 | 0.3363 |
| PSP | 0.9470 | 0.0016 | 0.3282 |

结论：在 10/130 representative case 中，PSP 在当前三个主指标上均优于原有对比方法。

## 5. 当前建议给导师的说法

可以这样汇报：

> 当前代码保留统一实验配置、批量运行入口、Pareto 指标统计、CLS 初始化敏感性和 DQN 学习型 baseline。DQN 在七组控制变量配置下均按五个偏好权重训练；10/130 中 PSP 的 HV/IGD/BestQ 为 0.9582/0.0016/0.3185，DQN 为 0.3382/0.4048/0.5974，表明标准标量化 DQN 在声明预算下弱于 PSP。图中 DQN 只显示独立点或柱，不连接成连续 Pareto 曲线。CLS 初始化实验则显示多数数据集最终结果接近，同时单纯贪心在 10/150 中可能陷入较差局部最优。

## 6. 后续待办

1. 将小规模 Joint-Exact 结果和两阶段合理性讨论写入正文与 response。
2. 将真实稀疏区域泛化结果写入正文，合成结果作为补充证据。
3. 将 10/130 Pareto 指标和 CLS 初始化敏感性结果写入实验分析。
4. 保留比例式 `varpi_j` 解释，但不声称半容量是实验最优。
5. 拿到 Visio 源文件后修改 Fig. 1/Fig. 2，并统一原稿图字号。
6. 将已完成的 DQN 建模、训练预算和结果写入正文及 response；SPEA2 不纳入，后续仅在需要完整学习型 Pareto set 时再考虑 preference-conditioned MORL。
