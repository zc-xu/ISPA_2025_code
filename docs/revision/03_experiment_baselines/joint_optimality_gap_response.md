# Two-stage decomposition and optimality-gap response

## Reviewer concern

The reviewer questions whether decomposing the joint server deployment and service provisioning problem into two stages may cause a loss of global optimality. This is a valid concern because the proposed MOS2 framework first optimizes server deployment and then optimizes service provisioning on the selected servers.

## Recommended handling

This item can be mainly addressed in the response letter. To avoid making the manuscript look abrupt, the paper can include only a short discussion paragraph, while the detailed small-scale comparison can be reported in the response letter as supporting evidence.

The safest wording is:

- Do not claim that the two-stage decomposition is globally optimal.
- Acknowledge that strict global optimality is not guaranteed after decomposition.
- Explain that the decomposition is designed to control computational complexity.
- Use the small-scale joint experiment to show that the empirical gap is limited while the computational saving is clear.

## Small-scale joint optimization experiment

Implemented script:

`LocalSearch/joint_optimality_gap.py`

The experiment constructs tractable small-scale instances from the existing `10_130` data:

- candidate stations: 6
- deployed servers: 3
- users: 30
- service types: 4
- service capacity per server: 2
- Stage-II setting for MOS2-PSP: `pop_size=50`, `n_gen=200`

For this reduced problem, the joint optimization can be enumerated exactly:

\[
\binom{6}{3}\left(\sum_{r=0}^{2}\binom{4}{r}\right)^3
=20\times 11^3=26620
\]

feasible joint server-service decisions.

Thus, `Joint-Exact` is a small-scale exact Pareto reference, not just another heuristic.

## Commands

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\joint_optimality_gap.py --seed 42 --n-candidates 6 --k 3 --n-users 30 --num-services 4 --capacity 2 --pop-size 50 --n-gen 200
.\LocalSearch\Scripts\python.exe .\LocalSearch\joint_optimality_gap.py --seed 43 --n-candidates 6 --k 3 --n-users 30 --num-services 4 --capacity 2 --pop-size 50 --n-gen 200
.\LocalSearch\Scripts\python.exe .\LocalSearch\joint_optimality_gap.py --seed 44 --n-candidates 6 --k 3 --n-users 30 --num-services 4 --capacity 2 --pop-size 50 --n-gen 200
```

## Results

| Seed | HV gap of MOS2 vs Joint-Exact | IGD gap | BestQ gap | Runtime ratio: Joint/MOS2 |
|---:|---:|---:|---:|---:|
| 42 | 6.4466% | 0.0289 | 0.0000 | 5.5817 |
| 43 | 4.1811% | 0.0199 | 0.0000 | 5.8895 |
| 44 | 0.9836% | 0.0660 | 0.0000 | 6.0928 |
| Mean | 3.8704% | 0.0382 | 0.0000 | 5.8547 |

Interpretation:

- MOS2-PSP obtains the same normalized BestQ as the exact joint Pareto reference in all three seeds.
- The average HV gap is about 3.87%.
- Exact joint enumeration is about 5.85 times slower even in this very small instance.
- For larger instances, exact or near-exact joint optimization becomes much less practical because the joint decision space grows combinatorially.

## Response-letter wording

**English draft**

Thank you for pointing out the potential optimality issue caused by the two-stage decomposition. We agree that the proposed decomposition does not provide a strict global optimality guarantee for the original fully joint server deployment and service provisioning problem. The motivation for this design is to reduce the combinatorial search space by first determining the geographic server deployment structure and then optimizing service provisioning on the selected servers.

To assess the possible performance loss, we conducted an additional small-scale joint-optimization comparison. In this experiment, we used a tractable instance with 6 candidate stations, 3 deployed servers, 30 users, 4 service types, and a service capacity of 2 per server. For this reduced instance, all feasible joint server-service decisions can be enumerated exactly, giving a Joint-Exact Pareto reference with 26,620 feasible solutions. We then compared MOS2-PSP with this exact joint reference under three random seeds.

The results show that MOS2-PSP achieves the same normalized best weighted quality as the Joint-Exact reference in all three seeds. The average HV gap is 3.87%, while exact joint enumeration is approximately 5.85 times slower even at this small scale. These results indicate that although the two-stage decomposition may sacrifice strict global optimality, the empirical performance gap is limited in the tested small-scale cases, whereas the reduction in computational burden is substantial. Therefore, the decomposition offers a practical trade-off between solution quality and computational complexity for larger MEC scenarios.

**中文解释**

这段回应的逻辑是：

1. 先承认两阶段分解不是严格全局最优，这样不会被审稿人抓住“过度声称”。
2. 说明分解的目的不是证明数学最优，而是降低联合组合空间。
3. 用小规模精确枚举实验说明：MOS2 和 Joint-Exact 的 BestQ 没有差距，HV 平均差距约 3.87%，但 Joint-Exact 在很小规模下已经慢约 5.85 倍。
4. 最终结论是“性能损失有限，复杂度收益明显”，而不是“完全没有性能损失”。

## Optional manuscript sentence

If this needs to enter the manuscript, use only a concise paragraph rather than a full new experiment section:

**English manuscript text**

Although the two-stage decomposition does not guarantee strict global optimality for the original fully joint problem, it substantially reduces the combinatorial search space by separating geographic server deployment from service provisioning. A small-scale exact joint-optimization check further indicates that the resulting empirical optimality gap is limited, while the computational burden of joint enumeration increases rapidly with the number of candidate stations, deployed servers, and service types.

**中文解释**

这段正文只做原则性解释，不放太多实验细节，不会显得突兀。如果老师希望“正文一定要回应”，可以把这段放在算法复杂度或实验设置之后。

## Generated files

Summary files:

- `output/csv/joint_gap_summary_c6_u30_k3_s4_seeds42_44.csv`
- `output/csv/joint_gap_metrics_c6_u30_k3_s4_seeds42_44.csv`
- `output/excel/joint_gap_c6_u30_k3_s4_seeds42_44.xlsx`

Representative figures:

- `output/png/joint_gap_front_joint_gap_c6_u30_k3_s4_seed42.png`
- `output/png/joint_gap_metrics_joint_gap_c6_u30_k3_s4_seed42.png`

Exploratory result not recommended as main evidence:

- `joint_gap_c8_u40_k3_s4_seed42` had an HV gap of about 27.92%, so it is useful only as a reminder that the gap can increase with instance difficulty. The recommended response evidence is the more controlled `c6_u30_k3_s4` setting above.
