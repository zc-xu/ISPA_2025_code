# MOS2 Revision Progress Mapping

本文档用于向导师汇报当前返修进展，并把审稿意见与当前保留的代码修改逐条对应起来。当前版本只保留可复现性、批量实验入口、Pareto 指标统计和原有 Stage II 初始化策略对比；额外 baseline 暂不进入主实验流程。

## 0. 当前结论

1. 当前代码中只保留原有 Stage II 对比方法：`NS-P`、`GCP`、`GDP`、`PSP`。
2. 额外 baseline 先不放入主动实验流程，避免在结果不稳定或解释不足时影响论文主线。
3. 已保留数据集配置表、批量运行入口、Pareto 指标计算和统一风格图表生成，方便后续切换不同规模数据集复现实验。
4. 主展示指标建议保留 `HV`、`IGD`、`Best Q`；`Spacing` 仅保留在 CSV 中作为可追溯指标，不作为主图指标。

## 1. 审稿意见与当前修改结果总表

| 审稿意见 | 审稿人真正关心的问题 | 当前保留修改 | 支撑文件/结果 | 下一步建议 |
|---|---|---|---|---|
| Stage II 对比实验不够充分。 | 审稿人希望看到更强、更可解释的对比和定量评价。 | 当前先保留原有四类方法，并新增批量入口和 Pareto 指标，保证已有实验可复现、可扩展。 | `LocalSearch/batch_service_experiments.py`；`LocalSearch/pareto_batch_metrics.py`；`output/csv/pareto_metrics_10_130.csv`。 | learning-based baseline 暂缓，等确定建模方式后再单独加入。 |
| CLS 初始化敏感性解释不足。 | Algorithm 1 的初始部署集合 `S` 随机生成，审稿人担心不同初值导致不同局部最优。 | 已新增 CLS 初始化敏感性实验，对比 random、density、distance-sum、greedy、density-diverse 五类初值。主图改为固定 130 用户规模 heatmap；另提供 `10_150` Random vs Greedy 辅助图。 | `LocalSearch/cls_initialization_sensitivity.py`；`output/pdf/cls_init_sensitivity_130_heatmap.pdf`；`output/pdf/cls_init_random_vs_greedy_10_150.pdf`；`output/csv/cls_init_sensitivity_all_data_scan.csv`。 | 正文主结论写 CLS 对初始化整体不敏感；辅助结论写单纯 Greedy 不一定更好。不要写 Random 普遍优于所有初始化。 |
| 缺少 Pareto front 定量指标。 | 原稿主要依赖散点图和加权 Q，缺少通用指标。 | 已新增 `HV`、`IGD`、`Best Q`，并生成 CSV、Excel、PDF、PNG。 | `LocalSearch/pareto_batch_metrics.py`；`output/pdf/pareto_metrics_10_130.pdf`。 | 正文说明指标方向：`HV` 越高越好；`IGD`、`Best Q` 越低越好。 |
| 多规模实验数据对应关系不清楚。 | 代码仓库里 Excel 较多，难以判断哪个文件对应哪组论文实验。 | 已新增显式配置清单，列出 7 组候选实验配置、用户规模、服务器规模、`sigma_min` 和 `n2_adjust`。 | `LocalSearch/experiment_configs.py`；`output/csv/experiment_config_manifest.csv`。 | 后续如需完整复现实验，可直接用 `--configs all` 或指定配置名。 |
| 两阶段分解合理性不足。 | 审稿人担心先服务器部署、再服务部署会牺牲全局最优性。 | 已在论文文字修改中补充两阶段分解理由：基础设施部署和服务配置属于不同时间尺度，分解能降低搜索空间并提高可解释性。 | `D:\NDM\conference_101719.tex`。 | 如版面允许，可补充运行时间或复杂度说明。 |
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

> 我们先撤掉了临时额外 baseline，只保留原有 Stage II 对比方法和可复现性增强。现在代码已经整理出统一实验配置、批量运行入口、Pareto 指标统计脚本和 CLS 初始化敏感性实验。对于审稿人质疑 CLS 随机初始化敏感的问题，我们比较了 random、density、distance-sum、greedy 和 density-diverse 五类初值；结果显示多数数据集最终收敛到同一成本，random 在 10/130、10/150、10/180 中平均 gap 分别约为 2.10%、1.27%、2.40%，说明 CLS 对初始化整体较稳。同时，10/150 中单纯边际贪心差 15.88%，说明贪心初始化不一定更好，可能陷入较差局部最优。所有新增 PDF 图已渲染检查，未发现坐标轴、图例或标签裁切。

## 6. 后续待办

1. 确认是否完整重跑 7 组配置。
2. 将 10/130 的 Pareto 指标结果写入论文实验分析。
3. 将 CLS 初始化敏感性实验作为新增消融/鲁棒性实验写入论文。
4. 拿到 Visio 源文件后修改 Fig. 1/Fig. 2。
5. 后续如果需要 learning-based baseline，再单独设计更可解释的多目标学习方法。
