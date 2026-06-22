# DQN Baseline Reassessment and Learning-Based Alternatives

本文档用于澄清：DQN 在本文服务部署问题中到底是什么、当前结果为什么不适合直接放入论文主 Pareto 图，以及如果仍希望回应审稿人“缺少 learning-based service placement baseline”的意见，后续应选择什么方案。

## 1. 先给结论

1. 当前实现的 DQN **符合 DRL 方向**，但结果形态不好，**不建议直接作为论文主图中的 Pareto curve**。
2. 当前 DQN 图上只有 11 个候选点、6 个非支配点，且分布远离 PSP/NSGA-II 前沿，因此这张图最多说明“普通标量化 DQN 在本文问题上表现较弱”，不能说明 DQN 给出了一条高质量 Pareto curve。
3. 如果要做成与其他方法类似的曲线，应改为 **multi-objective / preference-conditioned learning baseline**，而不是普通 DQN。
4. 最稳妥的短期路线是：正文主图先不放当前 DQN 曲线；若老师坚持 learning-based baseline，则做一个更严谨的 **Preference-Conditioned DRL / Pareto Set Learning inspired baseline**，并用 HV、IGD、Best Q 评价。

## 2. DQN 到底是什么

DQN 是 Deep Q-Network，核心是用神经网络近似动作价值函数：

```text
Q(state, action)
```

它回答的问题是：

```text
在当前 state 下，如果采取 action，后续累计收益大约是多少？
```

普通 DQN 默认处理的是 **单目标决策问题**。也就是说，DQN 每一步需要一个标量 reward，比如 “总成本越低 reward 越高” 或 “delay 越低 reward 越高”。

但本文 Stage II 是多目标优化：

```text
minimize deployment cost
minimize user delay
```

这两个目标天然冲突：为了降低 delay，可能需要部署更多或更贵的服务；为了降低 cost，可能牺牲部分 delay。因此，普通 DQN 不能直接处理 Pareto front，必须先把多目标压成一个标量。

## 3. 落到本文，当前 DQN 是怎么工作的

本文服务部署矩阵可以理解为：

```text
服务器 j 是否部署服务 k
```

假设 10/130 这一组实验中，Stage I 已选出 10 个边缘服务器，Stage II 要决定这些服务器部署哪些服务类型。每台服务器最多部署若干类服务。

当前 DQN 把“生成一个服务部署矩阵”拆成一个序列过程：

| 元素 | 本文含义 |
|---|---|
| State | 当前已经生成到一半的服务部署矩阵、当前服务器编号、当前服务槽编号、该服务器周围用户对不同服务的请求频率、各服务部署成本 |
| Action | 给当前服务器的当前服务槽选择一个服务类型 |
| Transition | 填完一个服务槽后移动到下一个服务槽；填完一台服务器后移动到下一台服务器 |
| Reward | 一个完整部署矩阵生成后，计算 cost 和 delay，再用权重 `lambda` 合成一个标量目标，目标越小 reward 越高 |
| Output | 对某个 `lambda`，输出一个完整服务部署方案，以及该方案对应的 cost-delay 点 |

标量化目标大致是：

```text
Q_lambda = lambda * normalized_cost + (1 - lambda) * normalized_delay
```

其中：

- `lambda` 接近 1：更重视 cost。
- `lambda` 接近 0：更重视 delay。
- `lambda = 0.5`：成本和时延折中。

## 4. 用 10/130 真实结果举例

当前 10/130 下，DQN 用 `lambda=0.0,0.1,...,1.0` 得到了 11 个点：

| lambda | Cost | Delay | 解释 |
|---:|---:|---:|---|
| 0.0 | 2627.47 | 226.84 | 理论上最重视 delay，但并没有得到全局最低 delay |
| 0.5 | 2579.94 | 239.12 | 成本和时延折中点 |
| 1.0 | 2413.28 | 415.92 | 理论上最重视 cost，因此 delay 明显变差 |

对比 PSP 在同一组中的范围：

```text
PSP cost range: 1117.70 - 2529.96
PSP delay range: 149.49 - 377.53
```

这说明当前 DQN 学到的策略质量较弱：

- 它没有找到 PSP 那样低 delay 的点。
- 它也没有找到 PSP 那样低 cost 的点。
- 很多点被 PSP/其他方法支配或明显远离主前沿。

因此，这张 DQN 图不应该解释为“DQN 形成了一条可比曲线”。更合理的结论是：

```text
普通标量化 DQN baseline 在本文静态组合式服务部署问题上表现较弱，说明本文 PSP+NSGA-II 在生成高质量 Pareto 解集方面更合适。
```

但这个结论如果要放论文里，需要非常谨慎，最好放在补充表或单独小节，而不是混在主 Pareto 曲线图里。

## 5. 为什么普通 DQN 不能直接生成一条 Pareto 曲线

NSGA-II / PSP 的工作方式是：

```text
一次运行维护一个种群 population
population 里面有很多候选部署方案
算法通过非支配排序和拥挤距离保留一组折中解
最终自然输出一组 Pareto solutions
```

所以它天然输出一条 Pareto front。

普通 DQN 的工作方式是：

```text
给定一个 reward
学习一个策略 policy
该策略倾向于输出一个最优或近似最优的部署方案
```

也就是说，普通 DQN 通常是：

```text
一个权重 lambda -> 一个策略 -> 一个解点
```

如果想让它有“曲线”，只能人为扫很多个权重：

```text
lambda=0.0 -> 一个点
lambda=0.1 -> 一个点
...
lambda=1.0 -> 一个点
```

这些点不是同一次多目标搜索自然形成的 Pareto front，而是多个单目标训练结果拼出来的近似前沿。由于训练不稳定、动作空间大、奖励稀疏、问题是静态组合优化而非连续交互环境，这些点经常分布稀疏、不平滑，甚至被其他方法支配。

这就是当前图中 DQN “不像曲线”的原因。

## 6. 如果想做成与其他方法类似的曲线，应怎么做

### 方案 A：Preference-Conditioned DQN / MORL-DQN

把 `lambda` 作为 state 的一部分输入网络：

```text
state' = [state, lambda]
```

训练时每个 episode 随机采样不同 `lambda`，使同一个网络学会：

```text
不同偏好 lambda 下，应该生成不同部署方案
```

推理时扫很多个 `lambda`，例如 0.00 到 1.00 共 51 个权重，再对输出点做非支配筛选。这样比“每个 lambda 单独训练一个普通 DQN”更像 preference-conditioned policy，也更接近 multi-objective RL。

优点：

- 仍然是 DRL，能回应审稿意见。
- 可以输出更多点，图形上更接近一条前沿。
- 改造当前 DQN 的成本中等。

缺点：

- 仍可能不如 PSP。
- 训练稳定性需要验证。
- 严格来说仍是 approximate Pareto front，不是 NSGA-II 那种原生 Pareto 搜索。

### 方案 B：Pareto Set Learning inspired baseline

这是更对口的多目标学习方法。思想是学习一个偏好条件生成器：

```text
preference lambda + problem features -> service deployment matrix
```

推理时输入不同 `lambda`，直接生成一组不同偏好的服务部署方案，形成近似 Pareto set。

优点：

- 概念上最适合“学习型方法 + Pareto curve”。
- 可解释性比普通 DQN 更好：输入偏好，输出对应折中方案。
- 文献上有 Pareto Set Learning for Neural Multi-Objective Combinatorial Optimization 作为支撑。

缺点：

- 需要训练数据或强化学习式训练。
- 如果用 PSP 结果当训练标签，会有“学生模型模仿本文方法”的风险，不适合做完全公平 baseline。
- 实现比普通 DQN 更复杂。

### 方案 C：GNN-based constructive policy

把用户、服务器、服务建成图，用 GNN 编码，再输出服务部署决策。

优点：

- 最贴近审稿人举例中的 GNN。
- 对 MEC 场景有解释空间：服务器-用户-服务天然是图结构。

缺点：

- 实现成本最高。
- 需要 PyTorch/PyG/DGL 等框架。
- 如果时间紧，容易出现复现难、调参难、结果不稳定的问题。

### 方案 D：只放单点 DQN，不画成曲线

选择一个公平的偏好，例如 `lambda=0.5`，只报告 DQN 在折中目标上的结果：

```text
DQN(lambda=0.5) vs PSP best-Q solution
```

优点：

- 严谨，不伪装成 Pareto curve。
- 实现和解释简单。
- 可以作为“学习型 baseline 的代表性比较”回应审稿人。

缺点：

- 视觉上不像其他 Pareto 曲线。
- 可能不如“完整学习型前沿”有说服力。

## 7. 当前建议

不建议把当前 DQN 虚线曲线直接放进正文主图。

建议优先顺序：

1. **短期稳妥版**：DQN 只作为 representative learning-based baseline，放 `lambda=0.5` 或多权重点的指标表，不在主 Pareto 图里连成曲线。
2. **中期增强版**：实现 Preference-Conditioned DQN，扫 51 个偏好权重，生成更密集的 approximate Pareto front，再判断是否可放主图。
3. **更强但更重版**：做 Pareto Set Learning inspired baseline 或 GNN policy，但需要更长开发和调参时间。

## 8. 给导师汇报时建议怎么说

可以这样说：

> DQN 属于 DRL，但普通标量化 DQN 一次训练只对应一个偏好权重，因此不能天然输出完整 Pareto front。当前 10/130 实验中，DQN 点分布稀疏且明显弱于 PSP，不建议直接作为主图曲线。更严谨的做法是，要么把 DQN 作为单点/表格型 learning baseline，要么进一步实现 preference-conditioned DQN 或 Pareto set learning 方法来生成近似 Pareto front。

## 9. 文献支撑

可用于说明“普通 DQN/DRL 可做服务放置 baseline”的文献：

- Liu et al., Deep Reinforcement Learning based Approach for Online Service Placement and Computation Resource Allocation in Edge Computing, IEEE TMC, 2023.
- Lu et al., A Dynamic Service Placement Based on Deep Reinforcement Learning in Mobile Edge Computing, Network, 2022.
- Hao et al., Deep Reinforcement Learning for Edge Service Placement in Softwarized Industrial Cyber-Physical System.

可用于说明“要学习整条 Pareto front，需要 multi-objective / preference-conditioned learning”的文献：

- Lin et al., Pareto Set Learning for Neural Multi-Objective Combinatorial Optimization, ICLR, 2022.
- Liu et al., Pareto Set Learning for Multi-Objective Reinforcement Learning, AAAI, 2025.
- Van Moffaert and Nowe, Multi-Objective Reinforcement Learning using Sets of Pareto Dominating Policies, JMLR, 2014.
