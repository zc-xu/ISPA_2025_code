# CLS Initialization Sensitivity Experiment

本文档用于回应审稿意见：

> The proposed CLS algorithm is essentially a local-search-based heuristic for the K-median problem. However, the manuscript does not clearly explain the initialization sensitivity of the algorithm. Since the initial deployment set S in Algorithm 1 is randomly generated, different initializations may lead to significantly different local optima.

## 1. 实验目的

该实验用于说明 Stage I 的 CLS 局部搜索对初始部署集合 `S` 的敏感性。核心问题是：

1. 随机初始化是否会导致结果大幅波动？
2. 使用贪心或密度型初始化是否会明显优于 random？
3. 是否存在某些看似合理的贪心策略反而陷入较差局部最优？

## 2. 对比初始化策略

当前代码实现了 5 类初始化策略，随后都接入同一个 CLS local search。

| Strategy | 含义 | 设计目的 |
|---|---|---|
| `random` | 随机选择 K 个候选站点，重复 50 个随机种子 | 测试原始算法的初始化波动 |
| `density_topk` | 选择覆盖半径内用户密度最高的 K 个候选站点 | 检查密度贪心是否更稳 |
| `distance_sum` | 选择到所有用户总距离最小的 K 个候选站点 | 检查中心性贪心是否更稳 |
| `greedy_marginal` | 逐步加入能最大降低当前传输成本的站点 | 检查单纯边际贪心是否容易陷入局部最优 |
| `density_diverse` | 综合用户密度和站点分散性选点 | 检查密度与空间分散折中是否更稳 |

## 3. 代码入口

新增脚本：

```text
LocalSearch/cls_initialization_sensitivity.py
```

默认可跑单组配置：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\cls_initialization_sensitivity.py --configs 10_130 --random-runs 50
```

本次实验使用所有 `_new` 数据集：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\cls_initialization_sensitivity.py --configs all_new --random-runs 50 --seed 42 --max-iter 200
```

最终复跑命令：

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\cls_initialization_sensitivity.py --configs all_new --random-runs 50 --seed 42 --max-iter 200
```

`all_new` 当前包括：

- `10_130`
- `10_150`
- `10_180`
- `5_130`
- `15_130`
- `20_130`

## 4. 输出文件

| 文件 | 内容 |
|---|---|
| `output/csv/cls_init_sensitivity_detail.csv` | 每次运行的初始成本、最终成本、迭代次数、覆盖率和最终站点集合 |
| `output/csv/cls_init_sensitivity_summary.csv` | 按配置和初始化策略聚合后的均值、标准差、CV、gap 和迭代次数 |
| `output/csv/cls_init_sensitivity_paper_table.csv` | 论文表格用的精简结果 |
| `output/excel/cls_init_sensitivity_detail.xlsx` | Excel 版详细结果 |
| `output/excel/cls_init_sensitivity_summary.xlsx` | Excel 版汇总结果 |
| `output/excel/cls_init_sensitivity_paper_table.xlsx` | Excel 版论文精简结果 |
| `output/pdf/cls_init_sensitivity_<config>.pdf` | 每个配置下不同初始化 final gap 的箱线图 |
| `output/pdf/cls_init_sensitivity_summary.pdf` | 各配置相对最优最终成本平均 gap 的数值热力图 |
| `output/pdf/cls_init_sensitivity_130_heatmap.pdf` | 仅固定 130 用户规模的初始化敏感性热力图 |
| `output/pdf/cls_init_random_vs_greedy_10_150.pdf` | `10_150` 下 Random 与 Greedy 的辅助对比图 |
| `output/csv/cls_init_sensitivity_all_data_scan.csv` | 对 `data` 目录所有 Excel 的额外扫描结果 |

## 5. 主要结果

| Config | Random mean gap | Random CV | 其他启发式结果 | 结论 |
|---|---:|---:|---|---|
| `10_130` | 2.10% | 4.53% | Density/DistSum/Greedy/Diverse 均达到最优 | CLS 对初始化较稳，random 只略差 |
| `10_150` | 1.27% | 2.56% | Density/DistSum/Diverse 达到最优，Greedy 差 15.88% | 单纯边际贪心可能陷入较差局部最优 |
| `10_180` | 2.40% | 5.88% | Density/DistSum/Greedy/Diverse 均达到最优 | CLS 对初始化较稳，random 波动有限 |
| `5_130` | 0.00% | 0.00% | 所有初始化均达到同一最终成本 | 初始化不敏感 |
| `15_130` | 0.00% | 0.00% | 所有初始化均达到同一最终成本 | 初始化不敏感 |
| `20_130` | 0.00% | 0.00% | 所有初始化均达到同一最终成本 | 初始化不敏感 |

## 6. 论文中建议怎么写

建议不要说“random 初始化绝对无影响”，而是更严谨地说：

> To evaluate the initialization sensitivity of CLS, we compared random initialization with four deterministic initialization strategies, including density-based, distance-sum-based, greedy marginal, and density-diversity initialization. All initialization strategies were followed by the same CLS improvement procedure. Results on six representative datasets show that CLS is generally robust to initialization. In four datasets, all tested initializations converge to the same final transmission cost. In the remaining fixed-server cases, random initialization yields only small average gaps, while density-based and distance-sum-based initializations converge to the best observed result. Moreover, the marginal greedy initialization performs worse in one case, suggesting that a purely greedy initialization may be trapped in a poorer local optimum.

中文解释：

> 我们比较了随机初始化和四种确定性初始化策略，并让它们都经过同一个 CLS 局部搜索过程。实验表明，CLS 对初始化整体不敏感：在多数数据集上，不同初始化最终收敛到相同传输成本；在用户数变化的若干规模中，随机初始化的平均 gap 较小，而密度型和距离型初始化可达到最佳观测结果。同时，单纯边际贪心在 10/150 中出现明显较差结果，说明贪心初始化并不必然更优，甚至可能落入较差局部最优。

## 7. 推荐给论文的实验呈现方式

优先放：

1. `cls_init_sensitivity_130_heatmap.pdf`，只展示固定 130 用户规模下的初始化敏感性，和原文“固定用户数 130，改变服务器数量”的实验设置一致。
2. 一张表，列出 `Random mean gap`、`Random CV` 和最差贪心 case。
3. `cls_init_random_vs_greedy_10_150.pdf` 可以作为辅助图，用来说明单纯边际贪心不一定更好。

不建议把所有单配置箱线图都放正文，可以放补充材料或内部汇报。

## 7.1 关于 Random vs Greedy 辅助图的严谨性

只放 Random 和 Greedy 的 `10_150` 柱状图有一定选择性展示风险，因此不建议把它作为唯一证据。更稳妥的用法是：

1. 主证据使用 `cls_init_sensitivity_130_heatmap.pdf`，说明固定 130 用户规模下 CLS 对初始化整体不敏感。
2. `10_150` 的 Random vs Greedy 图只作为辅助反例，说明“专门设计的贪心初始化也可能陷入较差局部最优”。
3. 完整策略结果仍保留在 `cls_init_sensitivity_summary.csv` 和 `cls_init_sensitivity_paper_table.csv` 中。

我额外扫描了 `data` 目录下所有 Excel 文件，结果保存在 `output/csv/cls_init_sensitivity_all_data_scan.csv`。扫描中没有发现“Random gap 为 0 而其他四种策略明显更差”的案例；更常见的现象是 Density/DistSum/Diverse 也达到 0 gap，而 Greedy 在若干数据集上出现较大 gap。因此论文中不能写“Random 普遍优于所有初始化”，只能写“Random 简单且总体稳定；单纯 Greedy 不一定更优”。

## 8. 图形质量验证

已使用 Poppler 将以下 PDF 渲染为 PNG 进行视觉和边界检查：

- `output/pdf/cls_init_sensitivity_130_heatmap.pdf`
- `output/pdf/cls_init_random_vs_greedy_10_150.pdf`
- `output/pdf/cls_init_sensitivity_summary.pdf`
- `output/pdf/cls_init_sensitivity_10_130.pdf`
- `output/pdf/cls_init_sensitivity_10_150.pdf`
- `output/pdf/cls_init_sensitivity_10_180.pdf`
- `output/pdf/cls_init_sensitivity_5_130.pdf`
- `output/pdf/cls_init_sensitivity_15_130.pdf`
- `output/pdf/cls_init_sensitivity_20_130.pdf`

检查结果：所有渲染图均完整显示，坐标轴、图例、标题和标签未裁切；自动边界检查结果均为 `ok`。
