# Hybrid Initialization Anchor Sensitivity

本文档对应审稿意见：

> The proposed hybrid initialization mechanism in Algorithm 2 introduces the parameter varpi_j to control the deterministic anchor size. However, the rationale behind selecting varpi_j is unclear.

## 1. 重新核对后的参数含义

代码中有两个容易混淆的概念：

- 服务类型数量：当前主要实验数据均为 8 类服务，用户服务类型范围为 `0..7`。
- 单台服务器最多部署服务数量：`SERVICE_CAPACITY_PER_SERVER`，对应论文中的 `V_j`。

当前生效代码：

```python
SERVICE_CAPACITY_PER_SERVER = 4
```

但为了验证“按容量取一半”的设置是否合理，本次重新做了容量敏感性实验：

```text
V_j = 4 and V_j = 8
```

其中：

```text
varpi_j = V_j / 2
```

对应：

- `V_j = 4` 时，`varpi_j = 2`；
- `V_j = 8` 时，`varpi_j = 4`。

## 2. 代码修改

`LocalSearch/nsga_service_deploy.py` 中 `ServiceSampling(mode="hybrid-A-1")` 已支持显式传入：

```python
ServiceSampling(
    "hybrid-A-1",
    deterministic_anchor_size=varpi,
    capacity_per_server=capacity,
    visualize_hybrid_process=False,
)
```

`ServiceRepair` 也支持同一容量参数，确保 NSGA-II 个体修复时使用相同的 `V_j`。

新增实验脚本：

```text
LocalSearch/hybrid_anchor_sensitivity.py
```

## 3. 复现实验命令

本次正式运行命令：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\hybrid_anchor_sensitivity.py `
  --configs 10_130 10_150 10_180 5_130 15_130 20_130 `
  --capacities 4 8 `
  --varpi-values 1 half 3 Vj `
  --seeds 42 43 44 `
  --pop-size 50 `
  --n-gen 200
```

实验规模：

- 6 个数据配置；
- 2 个容量设置：`V_j=4` 和 `V_j=8`；
- 每个容量下 4 个锚点设置；
- 3 个 NSGA-II 随机种子；
- 共 144 次 NSGA-II 运行。

Stage I 服务器部署位置固定，只测试 Stage II hybrid 初始化参数变化。

## 4. 输出文件

表格：

- `output/csv/hybrid_anchor_capacity_sensitivity_detail.csv`
- `output/csv/hybrid_anchor_capacity_sensitivity_summary.csv`
- `output/csv/hybrid_anchor_capacity_sensitivity_paper_table.csv`
- `output/csv/hybrid_anchor_capacity_sensitivity_series_rank.csv`
- `output/excel/hybrid_anchor_capacity_sensitivity_detail.xlsx`
- `output/excel/hybrid_anchor_capacity_sensitivity_summary.xlsx`

图：

- `output/pdf/hybrid_anchor_capacity_sensitivity_cap4_<config>.pdf`
- `output/png/hybrid_anchor_capacity_sensitivity_cap4_<config>.png`
- `output/pdf/hybrid_anchor_capacity_sensitivity_cap8_<config>.pdf`
- `output/png/hybrid_anchor_capacity_sensitivity_cap8_<config>.png`
- `output/pdf/hybrid_anchor_capacity_sensitivity_mean_rank.pdf`
- `output/png/hybrid_anchor_capacity_sensitivity_mean_rank.png`
- `output/pdf/hybrid_anchor_capacity_sensitivity_series_rank.pdf`
- `output/png/hybrid_anchor_capacity_sensitivity_series_rank.png`

逐次运行结果：

- `output/npz/res_hybrid_anchor_cap<capacity>_varpi<value>_<config>_seed<seed>.npz`

## 5. 指标方向

- `HV`: 越高越好；
- `IGD`: 越低越好；
- `Best Q`: 越低越好；
- `MeanRank`: 对 HV、IGD、Best Q 的平均秩，越低越好。

## 6. 主要结果

### 6.1 按实验线汇总

| Capacity | Experiment line | Best setting | Mean rank |
|---:|---|---|---:|
| `V_j=4` | Fixed server number, `K=10` | `varpi_j = 3` | 1.22 |
| `V_j=4` | Fixed user number, `M=130` | `varpi_j = V_j = 4` | 2.25 |
| `V_j=4` | All six configs | `varpi_j = V_j = 4` | 2.11 |
| `V_j=8` | Fixed server number, `K=10` | `varpi_j = 3` and `V_j=8` tie | 2.33 |
| `V_j=8` | Fixed user number, `M=130` | `varpi_j = V_j = 8` | 1.42 |
| `V_j=8` | All six configs | `varpi_j = V_j = 8` | 1.67 |

### 6.2 半容量设置的表现

| Capacity | Half setting | Overall mean rank | Interpretation |
|---:|---|---:|---|
| `V_j=4` | `varpi_j=2` | 2.83 | Not best overall; best or tied only in `5_130` and `20_130`. |
| `V_j=8` | `varpi_j=4` | 2.28 | Competitive in some cases, best in `10_150` and tied in `20_130`, but not best overall. |

## 7. 结论

当前实验不能严谨支撑“不同容量设置下取一半总是最好”。

更准确的结论是：

1. `varpi_j` 的选择确实会影响 hybrid initialization 的初始种群质量和最终 Pareto 结果，因此审稿人的质疑需要回应。
2. `varpi_j = V_j/2` 是一种可解释的折中设置：一半服务槽由确定性高分服务引导，另一半服务槽保留随机探索。
3. 但实验上，半容量设置不是稳定最优。尤其在 `V_j=4` 的固定服务器数实验线中，`varpi_j=3` 明显更好；在 `V_j=8` 中，`varpi_j=V_j` 或其他设置在多数组合上更强。
4. 当 `V_j=8` 且总服务类型也为 8 时，容量约束接近放开，`varpi_j` 的含义会弱化，因为服务器最多可以部署全部 8 类服务。这一点需要在解释实验时说明。

## 8. 建议写法

不建议写：

> The sensitivity experiment shows that `varpi_j = V_j/2` is optimal.

建议改成：

> The deterministic anchor size `varpi_j` controls the balance between deterministic guidance and randomized diversity in the hybrid initialization. We set `varpi_j = V_j/2` as a conservative default so that half of the service slots are guided by the cost-request hybrid score, while the remaining slots preserve stochastic exploration. To examine this choice, we conduct a sensitivity analysis under `V_j=4` and `V_j=8`. The results show that the best value of `varpi_j` may vary across capacities and workload scales, while the half-capacity setting remains competitive in several cases. This suggests that `varpi_j` is a tunable initialization parameter rather than a universally optimal constant.

中文含义：

> 我们不能声称“一半最好”，但可以说“一半是为了平衡确定性引导和随机探索的保守默认值”。敏感性实验表明最优 `varpi_j` 随容量和规模变化，因此它是可调参数，而不是普适最优常数。

## 9. 下一步建议

如果老师坚持论文里要有非常强的参数依据，有两种选择：

1. 保留 `varpi_j=V_j/2`，但把它写成可解释的默认折中，并报告敏感性实验，不说它最优。
2. 如果想追求实验指标最好，应按具体容量选择更优值，例如当前结果中 `V_j=4` 更偏向 `varpi_j=3` 或 `V_j`，`V_j=8` 更偏向 `V_j`。但这样会让算法看起来像按实验调参，解释性反而不如半容量默认值。

当前更推荐第 1 种：保留半容量作为默认设置，诚实补充敏感性实验，避免过度声称最优。
