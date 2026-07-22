# Stage II DQN Baseline: Implementation and Verified Results

## Purpose

The DQN experiment adds a learning-based service-provisioning baseline to Stage II. DQN is implemented as a transparent scalarized deep-reinforcement-learning method. Its preference-conditioned outputs are reported as independent solutions rather than being connected into a continuous Pareto curve.

## Mapping DQN to the Service-Provisioning Problem

For `K` selected edge servers and eight service types, DQN constructs a binary service-deployment matrix of size `K x 8`.

| Element | Definition |
|---|---|
| State | Current server, current service slot, services already selected on the current server, local request distribution, normalized deployment costs, global request distribution, and preference weight |
| Action | Select one of eight service types or skip the current slot |
| Transition | Move to the next service slot and then to the next server |
| Capacity | At most four selected services per server, consistent with `SERVICE_CAPACITY_PER_SERVER=4` |
| Reward | Request-coverage and deployment-cost shaping reward plus a terminal normalized cost-delay reward |
| Output | Binary service-deployment matrix evaluated by `MyServiceDeployProblem._calc_obj()` |

For preference weight `lambda`, policy training minimizes

`Q_lambda = lambda x normalized cost + (1 - lambda) x normalized delay`.

Five preferences are used: 0.1, 0.3, 0.5, 0.7, and 0.9. Each preference trains a separate policy for 320 episodes. The implementation uses a NumPy multilayer Q-network, replay buffer, target network, epsilon-greedy exploration, and deterministic random seeds.

## Controlled-Configuration Results

The four evolutionary values below reproduce the original paper workbook. DQN is added as the fifth method and is evaluated from its saved seed-42 objective outputs. Lower Best Q is better.

| Config | NS-P | PSP | GCP | GDP | DQN |
|---|---:|---:|---:|---:|---:|
| 10_100 | 0.2975 | **0.2686** | 0.2996 | 0.2748 | 0.5770 |
| 10_130 | 0.3894 | **0.3282** | 0.3550 | 0.3363 | 0.6125 |
| 10_150 | 0.3023 | **0.2749** | 0.2868 | 0.2847 | 0.4972 |
| 10_180 | 0.2976 | **0.2774** | 0.2955 | 0.2896 | 0.4840 |
| 5_130 | 0.2150 | **0.1945** | 0.2304 | 0.2393 | 0.4052 |
| 15_130 | 0.3072 | **0.2646** | 0.2729 | 0.2980 | 0.6077 |
| 20_130 | 0.3196 | **0.2864** | 0.2980 | 0.3049 | 0.7077 |

PSP has the lowest Best Q in all seven distinct configurations. Relative to the strongest non-PSP evolutionary initialization in each configuration, PSP reduces Best Q by 2.26%--9.53%, with a mean reduction of 4.11%. DQN has the largest Best Q throughout.

For the representative 10-server/130-user case, the equally sized evolutionary populations obtain the following Pareto metrics:

| Method | HV (higher is better) | IGD (lower is better) | Best Q (lower is better) |
|---|---:|---:|---:|
| NS-P | 0.8191 | 0.0785 | 0.3894 |
| GCP | 0.8596 | 0.0492 | 0.3550 |
| GDP | 0.8945 | 0.0326 | 0.3363 |
| PSP | **0.9470** | **0.0016** | **0.3282** |
| DQN | -- | -- | 0.6125 |

HV and IGD are not assigned to DQN in the manuscript because its five independently trained preference-conditioned outputs are not a population with the same cardinality and density as the 50-solution evolutionary sets. DQN participates through the common Best-Q comparison.

## Geographical-Generalization Result

The DQN baseline was also run on `real_sparse_r04_c40_u130_k10_s1`, which contains 40 real candidate stations, 10 deployed servers, 130 users, and eight service types in a region whose candidate centroid is 24.20 km from that of the original Xizhimen instance.

For cross-method Best Q comparison, every DQN output is reevaluated using the exact seed-specific normalization bounds of the four population methods and the fixed expression

`Best Q = 0.5 x normalized cost + 0.5 x normalized delay`.

This separates the preference used to train a DQN policy from the metric used to compare methods.

| Seed | Best DQN preference | Cost | Delay | Common Best Q |
|---:|---:|---:|---:|---:|
| 42 | 0.9 | 1,984.6548 | 218.2309 | 0.4388 |
| 43 | 0.5 | 2,115.1869 | 234.7720 | 0.6377 |
| 44 | 0.5 | 2,300.8531 | 232.9600 | 0.5785 |
| Mean +/- sample std | - | - | - | **0.5517 +/- 0.1021** |

PSP obtains a common Best Q of **0.2678 +/- 0.0503**, which is 51.45% lower than DQN. HV and IGD are reported for NS-P, GCP, GDP, and PSP because these four methods each return 50 solutions; DQN participates in this experiment through the equal-definition balanced-solution comparison.

## Response to the Learning-Based-Baseline Comment

### English

> Thank you for pointing out the absence of a learning-based service-placement baseline. We have added a DQN baseline to the Stage II evaluation. DQN constructs the service-deployment matrix sequentially. Its state contains the current server and service slot, services selected on the current server, local and global request distributions, deployment costs, and a cost-delay preference weight; each action selects one service type or skips the slot. The terminal matrix is evaluated using exactly the same cost and delay functions as the other methods. Separate policies are trained for five preference weights under a fixed training budget, and their outputs are reported as independent solutions.
>
> DQN was included in both controlled scale sweeps. With 10 deployed servers and 100, 130, 150, and 180 users, its Best-Q values are 0.5770, 0.6125, 0.4972, and 0.4840, respectively. With 130 users and 5, 10, 15, and 20 deployed servers, the corresponding values are 0.4052, 0.6125, 0.6077, and 0.7077. PSP achieves the lowest Best Q in every panel and reduces Best Q by 2.26%--9.53% relative to the strongest alternative evolutionary initialization. In the representative 10-server/130-user case, PSP obtains HV=0.9470, IGD=0.0016, and Best Q=0.3282, whereas DQN obtains Best Q=0.6125. The same learning baseline was also included in the new real-station generalization instance, where PSP obtains a mean Best Q of 0.2678 compared with 0.5517 for DQN.

### 中文对应翻译

> 感谢审稿人指出缺少学习型服务放置基线。我们在 Stage II 评估中加入了 DQN 基线。DQN 以序列方式构建服务部署矩阵：状态包含当前服务器、当前服务槽、当前服务器已选择的服务、本地与全局请求分布、部署成本以及成本-时延偏好权重；动作是选择一种服务或跳过当前服务槽。最终部署矩阵与其他方法使用完全相同的成本和时延函数进行评价。实验在固定训练预算下分别训练 5 个偏好权重对应的策略，并将其输出作为独立解报告。
>
> DQN 已加入两条控制变量实验。固定 10 台服务器时，100、130、150、180 个用户的 DQN Best Q 分别为 0.5770、0.6125、0.4972、0.4840；固定 130 个用户时，5、10、15、20 台服务器的对应数值为 0.4052、0.6125、0.6077、0.7077。PSP 在每个面板中均取得最低 Best Q，相较每个配置中最强的其他进化初始化方法降低 2.26%--9.53%。在 10 台服务器、130 个用户的代表性实验中，PSP 的 HV、IGD 和 Best Q 分别为 0.9470、0.0016 和 0.3282，DQN 的 Best Q 为 0.6125。真实基站泛化实例中，PSP 的平均 Best Q 为 0.2678，DQN 为 0.5517。

## Reproducibility

Run the seven controlled configurations:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\dqn_service_baseline.py `
  --configs all --weights 0.1 0.3 0.5 0.7 0.9 `
  --episodes 320 --dqn-seeds 42
```

Run the geographical instance with seed-specific reference bounds:

```powershell
.\LocalSearch\Scripts\python.exe .\LocalSearch\dqn_service_baseline.py `
  --screen-csv output\csv\real_region_stage1_screen_c40_u130_k10.csv `
  --configs real_sparse_r04_c40_u130_k10_s1 `
  --weights 0.1 0.3 0.5 0.7 0.9 `
  --episodes 320 --dqn-seeds 42 43 44 `
  --stage-seed 42 --stage1-iter 200 `
  --reference-by-seed --evaluation-alpha 0.5
```

Primary outputs:

- `output/npz/res_dqn_<config>.npz`
- `output/npz/seed_checks/res_dqn_<config>_seed<seed>.npz`
- `output/csv/dqn_summary_<config>.csv`
- `output/csv/dqn_training_<config>.csv`
- `output/csv/reviewer6_main_candidate_dqn_weighted.csv`
- `output/csv/reviewer6_main_candidate_bestq_detail.csv`
- `output/csv/reviewer6_main_candidate_bestq_aggregate.csv`
- `data/paper_archive/stage2_bestq_original_paper.csv`
- `output/csv/stage2_bestq_original_with_dqn.csv`
- `output/csv/stage2_bestq_original_with_dqn_validation.csv`
