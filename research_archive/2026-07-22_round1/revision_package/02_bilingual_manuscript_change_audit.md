# 论文逐项修改中英对照审计

## 使用说明

- 对照基线：第一次投稿的 `conference_101719(1).tex`。
- 标记稿：`conference_101719_targeted_revision_marked.tex`，只有实质修改内容显示为蓝色。
- 净稿：`conference_101719_targeted_revision_clean.tex`，源码和 PDF 均不含修改标记。
- 正文只写可独立阅读的技术内容；“为何修改、对应哪条意见、补充实验的详细解释”仅出现在本审计和回信中。

## 1. Fig. 1 的视觉含义与正文解释

**对应意见：** Reviewer 1, Comment 1。

**原图注英文**

> An illustrating example.

**原图注中文**

> 一个说明性示例。

**修改后图注英文**

> MEC system model and service-provisioning scenario.

**修改后图注中文**

> MEC 系统模型与服务配置场景。

**修改后正文英文**

> Server deployment and service provisioning have a significant impact on the profit of mobile network operators. Figure 1 illustrates a scenario with five base stations. The solid black contours partition the topology into interconnected service regions, the black dashed circles denote the coverage areas of individual base stations, and the red dotted circles identify base stations equipped with edge servers. The blue bidirectional arrows represent cloud-edge communication, while the red dashed arrows indicate inter-region request forwarding. Distinct colors represent service types s1-s6, and each user color indicates the corresponding requested service. The service blocks beside an edge server show its instantiated services; the question-mark slot in Area 3 denotes a provisioning decision under limited server capacity.

**修改后正文中文**

> 服务器部署和服务配置会显著影响移动网络运营商的收益。图 1 展示了一个包含五个基站的场景。黑色实线轮廓将拓扑划分为互联的服务区域，黑色虚线圆表示各基站的覆盖区域，红色点线圆表示部署了边缘服务器的基站。蓝色双向箭头表示云边通信，红色虚线箭头表示跨区域请求转发。不同颜色表示服务类型 s1-s6，用户颜色与其请求的服务颜色一一对应。服务器旁的服务色块表示已经配置的服务；Area 3 中的问号槽位表示容量受限条件下仍待决定的服务配置位置。

**图文一致性修正英文**

> For example, the server in Area 4 provisions services s3 and s6; requests for the other service types require inter-area forwarding.

**图文一致性修正中文**

> 例如，Area 4 的服务器配置了服务 s3 和 s6；其他服务类型的请求需要进行跨区域转发。

**修正原因：** 指定的新图中 Area 4 的两个色块对应 s3 和 s6；旧句写成 s2、s3 和 s5，与图不一致，已经从正文删除。

**位置：** 标记稿约 L100-L109，Fig. 1。

## 2. Fig. 1 中服务槽位示例

**原文英文**

> For example, in area 3, the deployed server can only host three service instances, which cannot satisfy all user requests simultaneously. Two services, s2 and s5, have already been provisioned, and the remaining slot must be assigned to one of the candidate services in {s2, s3, s4, s6}.

**修改后英文**

> For example, the server in Area 3 can host three service instances. Two slots are occupied by the illustrated service replicas, while the remaining slot must be assigned from the candidate services shown below the server. Since this choice affects forwarding distance, transmission cost, and service-delivery latency, the provisioning decision considers request frequency and service provisioning cost.

**修改后中文**

> 例如，Area 3 中的服务器最多可容纳三个服务实例。图中已有两个服务副本占用两个槽位，剩余槽位需要从服务器下方给出的候选服务中选择。由于该选择会影响转发距离、传输成本和服务交付时延，因此配置决策同时考虑请求频率和服务配置成本。

**说明：** 保留原图中的开放决策槽位，不把最后一个服务写死；用户颜色与服务颜色保持一致。

## 3. 决策变量体系重构

**对应意见：** Reviewer 1, Comment 2。

**原文英文**

> Here, we introduce a binary variable x_jk, where x_jk = 1 if an edge server m_j is deployed at base station b_k, and 0 otherwise.

> Let x_jw be a binary variable, where x_jw = 1 if an instance of service s_w is deployed on edge server w_j, and x_jw = 0 otherwise. Furthermore, let x_ijw be a binary variable indicating whether user u_i is served by service s_w deployed on server w_j.

**原文中文**

> 原稿分别使用 x_jk、x_jw 和 x_ijw 表示服务器部署、服务配置和用户服务关联，三个符号外观相近，而且正文把服务器 m_j 误写为 w_j。

**修改后英文**

> Let y_jk be a binary server-deployment variable, where y_jk = 1 if edge server m_j is deployed at base station b_k, and y_jk = 0 otherwise.

> Let z_jw be a binary service-provisioning variable, where z_jw = 1 if an instance of s_w is provisioned on edge server m_j, and z_jw = 0 otherwise. Furthermore, let a_ijw be a binary association variable, where a_ijw = 1 if user u_i is served by service s_w on server m_j, and a_ijw = 0 otherwise.

**修改后中文**

> y_jk 专用于服务器部署，z_jw 专用于服务配置，a_ijw 专用于用户与服务器上服务的关联。三个决策变量使用完全不同的字母，并统一把服务器写为 m_j。

**同步修改范围：** Table I、成本模型、时延模型、约束 (5)-(7)、P1/P2/P3 的说明及算法正文。

**位置：** 标记稿约 L164-L310。

## 4. PSP 编码矩阵与数学变量的对应关系

**原稿状态：** 原稿直接使用 `indiv[j,w]`，没有说明它与系统模型中的服务配置变量之间的关系。

**修改后英文**

> A service-provisioning scheme is encoded by a binary matrix indiv in {0,1}^{k x |S|}. Each row corresponds to a deployed server and each column to a service type. The entry indiv[j,w] is the encoded counterpart of z_jw: it equals 1 when service s_w is provisioned on server m_j, and 0 otherwise.

**修改后中文**

> 服务配置方案编码为一个 k x |S| 的二进制矩阵 indiv。每一行对应一台已部署服务器，每一列对应一种服务。indiv[j,w] 是数学变量 z_jw 在算法编码中的对应项：为 1 表示在 m_j 上配置 s_w，为 0 表示未配置。

**位置：** 标记稿约 L564。

## 5. 两阶段分解的技术合理性

**对应意见：** Reviewer 1, Comment 3。

**原文英文**

> To solve this problem, we use a decomposition that separates it into two sequential stages. The first stage focuses on servers, determining where edge servers should be deployed. The second stage addresses providing services, i.e., deciding the provisioning locations of services across the selected servers.

**原文中文**

> 为求解该问题，我们将其拆分为两个连续阶段。第一阶段确定边缘服务器部署位置，第二阶段确定服务在已选服务器上的配置位置。

**新增正文英文**

> The decomposition follows the operational hierarchy of MEC planning. Server deployment is a long-term infrastructure decision governed by budget, coverage, and geographic demand, whereas service instances are provisioned after the physical server locations are known. Stage 1 therefore resolves the spatial variables that determine deployment and transmission costs, and Stage 2 optimizes service instances and user associations on the selected infrastructure. Passing the selected locations, user assignments, and Stage-I cost to Stage 2 preserves the cost-latency dependence while substantially reducing the decision space of the service-provisioning search.

**新增正文中文**

> 该分解遵循 MEC 规划的实际决策层级。服务器部署属于受预算、覆盖和地理需求支配的长期基础设施决策，而服务实例需要在物理服务器位置确定后进行配置。因此，Stage 1 先求解决定部署成本和传输成本的空间变量，Stage 2 再在选定基础设施上优化服务实例和用户关联。Stage 1 将已选位置、用户分配和阶段成本传递给 Stage 2，在显著缩小服务配置搜索空间的同时保留主要的成本-时延联系。

**位置：** 标记稿约 L299-L301。

**回信中的补充证据：** 6 个候选站、3 台服务器、30 个用户、4 类服务、容量 2 的小规模实例；精确枚举 26,620 个联合可行解。三组种子中 MOS²-PSP 的 Best Q 均与精确联合参考一致，平均 HV 差异为 3.87%，精确枚举平均耗时为 MOS² 的 5.18 倍。该实验只写入回信，不写入正文。

## 6. PSP 容量检查与修复机制

**对应意见：** Reviewer 1, Comment 4。

**原稿英文**

> Repair X to satisfy capacity constraint V_j.

**原稿中文**

> 修复 X 以满足容量约束 V_j。

**修改后正文英文**

> Given the fixed server locations, PSP constructs a hybrid initial population and applies NSGA-II to optimize provisioning cost and access delay. Crossover and mutation produce each offspring, whose entries are first rounded to binary values. For every server m_j, PSP then checks sum_w z_jw <= V_j. If the capacity is exceeded, selected service entries are randomly deactivated until feasibility is restored. Only capacity-feasible offspring are evaluated and passed to non-dominated sorting; thus, feasibility is enforced by repair rather than by a penalty function.

**修改后中文**

> 在服务器位置固定后，PSP 构造混合初始种群并使用 NSGA-II 优化配置成本和访问时延。交叉与变异生成子代后，首先把变量取整为二进制值；随后对每台服务器检查服务数量是否超过 V_j。若超限，则随机关闭已选服务项，直到恢复可行性。只有修复后的容量可行解才进入目标计算和非支配排序。因此本文采用显式修复机制，而不是惩罚函数。

**图与算法：** Algorithm 3 和正文同步给出“二进制取整 -> 容量检查 -> 超限修复 -> 目标计算 -> 非支配排序”。独立 `Evolutionary Optimization` 面板已按同一顺序重画，待作者贴回 Visio 后替换整幅 Fig. 2。

**位置：** 标记稿约 L343-L346、L495-L516、L574。

## 7. 实验图可读性与图注

**对应意见：** Reviewer 1, Comment 5。

**处理结果：** Stage-I 规模对比、Stage-I 成本与收敛、Stage-II 两组柱形图、混合初始化和 CLS 初始化敏感性图采用清晰的统一排版；Pareto fronts 恢复为第一次投稿所用的四幅原始数据 PDF，并保持四子图全宽组合。

**修改后英文图注**

> Stage-I server-deployment performance under different server and user scales.

> Stage-I cost analysis under varying server counts and CLS iterations.

> Service-provisioning performance with 10 deployed servers and increasing user populations.

> Hybrid initialization for candidate services on Server 0.

> Service-provisioning performance with 130 users and increasing numbers of deployed edge servers.

> Pareto fronts for Stage-II service provisioning with 130 users.

> Initialization sensitivity of CLS under two server/user settings.

**对应中文**

> 不同服务器和用户规模下的 Stage-I 服务器部署性能。

> 不同服务器数量与 CLS 迭代过程下的 Stage-I 成本分析。

> 固定部署 10 台服务器、逐步增加用户数量时的服务配置性能。

> Server 0 上候选服务的混合初始化过程。

> 固定 130 个用户、逐步增加部署服务器数量时的服务配置性能。

> 130 个用户条件下 Stage-II 服务配置的 Pareto 前沿。

> 两种服务器/用户设置下 CLS 的初始化敏感性。

**说明：** 图注只说明“这是什么图”；结果解释全部放在对应正文段落中。Stage-II 两组柱形图包含 NS-P、PSP、GCP、GDP 和 DQN 五种方法。柱顶数值和误差棒均已移除：旧误差棒是 Excel 对同一图中五种算法数值横向计算的标准误，并非多次独立运行的不确定性，不能作为论文统计误差棒使用。

## 8. CLS 初始化敏感性实验

**对应意见：** Reviewer 2, Comment 1。

**原稿状态：** Algorithm 1 随机生成初始集合 S，但没有初始化敏感性结果。

**新增正文英文**

> To examine the effect of the initial deployment set in Algorithm 1, we compare Random, Density, DistSum, marginal Greedy, and Diverse initialization over 50 runs. For each configuration, the reported gap is the percentage difference between the final cost and the best final cost observed under the same server/user setting. As shown in Fig. 9, the five strategies reach the same best final cost in nearly all fixed-130-user cases; the only nonzero entry is the 2.10% mean gap of Random at 10 servers. Under the 10-server/150-user setting, Random obtains a 1.27% mean gap, whereas marginal Greedy reaches 15.88%. These results show that CLS is generally stable across initializations and that random initialization avoids a systematic preference for a poorer local optimum.

**新增正文中文**

> 为考察 Algorithm 1 中初始部署集合的影响，我们在 50 次运行中比较 Random、Density、DistSum、marginal Greedy 和 Diverse 五种初始化。每个配置的 gap 定义为最终成本与该服务器/用户设置下观察到的最佳最终成本之间的百分比差。在固定 130 个用户的实验中，五种策略在几乎所有设置下都达到相同最佳最终成本，唯一的非零项是 10 台服务器时 Random 的 2.10% 平均差距。在 10 台服务器、150 个用户的设置下，Random 的平均差距为 1.27%，marginal Greedy 为 15.88%。结果表明 CLS 对测试的初始化方式总体稳定，随机初始化也避免了确定性偏好导致较差局部最优的风险。

**位置：** 标记稿约 L847-L856，Fig. 9。

## 9. 可靠性 QoS 的定位

**对应意见：** Reviewer 2, Comment 2。

**原稿英文**

> Equation (6) ensures QoS for each user by requiring that the total latency incurred when accessing the requested service does not exceed the maximum tolerable delay.

**修改后英文**

> Equation (6) provides latency-oriented QoS by requiring the end-to-end latency of a served request to remain below the user's tolerable bound. For reliability-critical applications, latency compliance can be complemented by packet-loss, link-availability, and service-interruption constraints, preventing a low-latency solution from being selected when service continuity is insufficient.

**修改后中文**

> Equation (6) 通过要求已服务请求的端到端时延不超过用户可容忍上限，提供面向时延的 QoS 约束。对于可靠性关键型应用，可进一步加入丢包率、链路可用性和服务中断约束，避免在服务连续性不足时仍选择表面上低时延的解。

**结论新增英文**

> Future work will extend the framework with reliability-aware QoS constraints for packet loss, link availability, and service interruption, together with learning-based demand prediction and multi-domain coordination.

**结论新增中文**

> 后续研究将通过丢包率、链路可用性和服务中断等可靠性感知 QoS 约束扩展该框架，并研究基于学习的需求预测和多域协同。

## 10. NSGA-II/PSP 参数说明

**对应意见：** Reviewer 2, Comment 3。

**原稿状态：** 未集中给出 N、G、交叉概率、变异概率和分布指数。

**新增表格英文**

> Population size N = 50; maximum generations G = 200; SBX crossover p_c = 0.9, eta_c = 15; polynomial mutation p_m = 1/(k|S|), eta_m = 20; hybrid-score weights alpha = beta = 0.5; service capacity V_j = 4; anchor ratio rho = 0.5.

**新增表格中文**

> 种群规模 N=50；最大进化代数 G=200；SBX 交叉概率 0.9、分布指数 15；多项式变异概率 1/(k|S|)、分布指数 20；混合评分权重 alpha=beta=0.5；服务容量 V_j=4；锚点比例 rho=0.5。

**位置：** Table II，标记稿约 L771-L804。

## 11. 归一化指标 Q 的数学定义

**对应意见：** Reviewer 2, Comment 4。

**原稿状态：** 图中使用 `Q (normalized)`，正文没有给出完整归一化公式和权重。

**新增英文**

> For each server/user configuration, cost and delay are normalized over the pooled solutions of the compared methods as C-hat = (C-C_min)/(C_max-C_min) and D-hat = (D-D_min)/(D_max-D_min), and the scalar evaluation score is Q = lambda C-hat + (1-lambda) D-hat, lambda = 0.5. Lower Q indicates a better balanced solution.

**新增中文**

> 对每个服务器/用户配置，将所有对比方法的候选解合并后分别计算成本和时延的最小值与最大值，并进行 min-max 归一化。随后使用 Q=lambda*C-hat+(1-lambda)*D-hat，且 lambda=0.5。Q 越低表示成本与时延的综合平衡越好。

**额外澄清英文**

> The normalized score Q is applied after optimization to select one balanced solution for scalar comparison; it is not an objective used to generate the Pareto population.

**额外澄清中文**

> Q 只在多目标优化完成后用于选择一个平衡解并进行标量比较，不参与 Pareto 种群的生成。

## 12. 参数 varpi_j 的比例式解释

**对应意见：** Reviewer 2, Comment 5。

**原稿英文**

> Let varpi_j (0 < varpi_j <= V_j) be the size of the deterministic anchor set selected for edge server m_j.

**修改后英文**

> We set varpi_j = ceil(rho V_j) with rho = 0.5, reserving half of the capacity for high-ranked deterministic services and half for stochastic selection from the remaining candidates.

> The deterministic anchor size is defined proportionally as varpi_j = ceil(rho V_j) with rho = 0.5. Hence, for the experimental capacity V_j = 4, two slots retain the highest-scoring services and two slots preserve stochastic exploration. This equal allocation provides an interpretable exploitation-exploration balance and applies directly to servers with different capacities.

**修改后中文**

> 将确定性锚点大小定义为 varpi_j=ceil(rho*V_j)，其中 rho=0.5。也就是把一半容量分配给评分最高的确定性服务，另一半保留给随机探索。实验中 V_j=4，因此 varpi_j=2；若 V_j=8，则 varpi_j=4。该定义会随容量自动缩放，并具有明确的利用-探索折中含义。

**位置：** 标记稿约 L583-L588、L771。

## 13. DQN 学习型基线

**对应意见：** Reviewer 2, Comment 7。

**原稿状态：** Stage II 只有 NS-P、GCP、GDP 三个基线，没有学习型方法。

**正文英文**

> NSGA-II Provision (NS-P): The initial population is generated randomly.

> Deep Q-Network Provision (DQN): A Q-network sequentially selects a service or an empty action for each server slot using demand, deployment cost, and a cost-delay preference. The resulting deployment is evaluated by the same objectives as the other methods.

**正文中文**

> NS-P 的初始种群采用随机方式生成。

> DQN 使用 Q 网络依次为每个服务器槽位选择一种服务或空动作，决策依据为需求、部署成本和成本-时延偏好；所得部署方案使用与其他方法相同的目标函数进行评价。

**说明：** 网络结构、奖励函数和训练超参数保留在回信与复现材料中，不在实验部分展开，以保持与其他基线相近的介绍长度。

**结果英文**

> PSP also achieves lower Q than DQN across all tested scales.

**结果中文**

> 在全部测试规模下，PSP 的 Q 均低于 DQN。由于 Q 越低越好，该句明确表示 PSP 优于 DQN，而不是把 “higher score” 误读为 DQN 更好。

两组主实验共有 8 个面板，对应 7 个唯一配置；PSP 在全部图示场景中均取得最低 Q，其中 10 servers/130 users 时 PSP=0.3282，DQN=0.6125。

## 14. Pareto 数值指标

**对应意见：** Reviewer 2, Comment 8。

**原稿状态：** 只展示 Pareto fronts，没有 HV、IGD 等数值指标。

**新增英文**

> Hypervolume (HV) measures the dominated objective-space volume relative to the reference point (1.1,1.1) and is maximized, whereas inverted generational distance (IGD) measures the mean distance from the common non-dominated reference front to a method's front and is minimized.

**新增中文**

> HV 衡量相对于参考点 (1.1,1.1) 的支配目标空间体积，越高越好；IGD 衡量公共非支配参考前沿到某方法前沿的平均距离，越低越好。

**10 servers/130 users 数值：**

| Method | HV | IGD | Best Q |
|---|---:|---:|---:|
| NS-P | 0.8191 | 0.0785 | 0.3894 |
| GCP | 0.8596 | 0.0492 | 0.3550 |
| GDP | 0.8945 | 0.0326 | 0.3363 |
| PSP | **0.9470** | **0.0016** | **0.3282** |
| DQN | -- | -- | 0.6125 |

**正文英文说明：**

> DQN produces a limited set of scalarized solutions rather than a population-based Pareto front; it is therefore compared through Q and is not included in the HV/IGD comparison.

**正文中文说明：**

> DQN 生成的是有限个标量化解，而不是种群型 Pareto 前沿，因此通过 Q 参与比较，不纳入 HV/IGD 对比。

## 15. 地理泛化实验

**对应意见：** Reviewer 2, Comment 6。

**处理方式：** 详细实验只进入回信，不进入论文正文。

**回信英文结论**

> We conducted a complete two-stage experiment in a different real Beijing region using a pool of 2,215 deduplicated base-station coordinates. The test instance contains 40 candidate base stations, 10 deployed servers, 130 users, and 8 service types. In Stage I, CLS reduced the objective from the best non-CLS value of 6,150.5741 to 2,304.7670, a reduction of 62.53%. In Stage II, PSP achieved the best mean HV (1.0116), IGD (0.0129), and Best Q (0.2678) over three seeds. DQN obtained a mean Best Q of 0.5517, while PSP reduced it by 51.45%.

**回信中文解释**

> 使用 2,215 个去重真实北京基站坐标构造新的区域实例，配置为 40 个候选基站、10 台部署服务器、130 个用户和 8 类服务。Stage I 中 CLS 相对最好非 CLS 结果降低 62.53%；Stage II 三个种子的平均 HV、IGD 和 Best Q 均由 PSP 取得最优，且 PSP 的平均 Best Q 比 DQN 低 51.45%。

## 16. 建议文献

**对应意见：** Reviewer 2, Comment 9 和 AE 的选择性引用要求。

**新增正文英文**

> Optimization and learning methods also address complementary MEC resource-management objectives. Feng et al. jointly optimized latency-aware service deployment and peer offloading over multiple timescales. Kato et al. applied breakout local search to transmission- and processing-aware task offloading in a multi-tier cloud environment. Jing et al. studied long-term max-min fairness for task splitting and resource allocation in integrated multi-RAT/MEC networks, while Jing et al. used online mini-batch learning for dynamic energy-cost conservation in distributed edge clouds. These studies address dynamic offloading, fairness, or energy management; the present work focuses on interpretable server planning and capacity-constrained multi-objective service provisioning under a common cost-latency model.

**新增正文中文**

> 优化与学习方法也从互补角度研究 MEC 资源管理。Feng 等人在多个时间尺度上联合优化时延感知服务部署与对等卸载。Kato 等人采用突破局部搜索处理多层云环境中同时考虑传输与处理的任务卸载。Jing 等人研究集成多 RAT/MEC 网络中任务拆分与资源分配的长期最大最小公平性；另一项 Jing 等人的工作采用在线小批量学习降低分布式边缘云的动态能源成本。这些研究分别关注动态卸载、公平性或能源管理，而本文重点研究统一成本-时延模型下可解释的服务器规划和容量受限多目标服务配置。

**实际新增文献：** Reviewer 推荐列表中的 [1]、[3]、[4] 和 [5]。其中 [1] 对应服务部署与卸载联合优化，[3] 对应局部搜索式任务卸载，[4] 对应 MEC 长期公平资源分配，[5] 对应学习型动态能源管理。列表中的 [2] 和 [6] 均专门面向 FSO-enabled SAGIN 任务卸载，其网络架构、链路模型和决策变量与本文的地面 MEC 容量受限服务配置差异较大，因此不强行引入。

## 17. 保留并恢复的原始信道模型

**范围说明：** 审稿意见没有要求删除信道模型，因此最终稿保留第一次投稿的带宽、发射功率、噪声和信道增益形式，不使用任何“原模型不受数据支持”之类表述。

**最终英文**

> We define the maximum transmission rate as r_ij = B_ij log2(1 + gamma g_ij/N), where B_ij denotes the channel bandwidth, gamma is the transmission power of the user device, N is the noise power, and g_ij is the channel gain between u_i and m_j. The channel gain is modeled as g_ij = 127 + 30 log(tau(u_i -> m_j)).

**最终中文**

> 最大传输速率保留为 r_ij=B_ij log2(1+gamma*g_ij/N)，其中 B_ij 为信道带宽，gamma 为用户设备发射功率，N 为噪声功率，g_ij 为用户与边缘服务器之间的信道增益；信道增益仍采用 g_ij=127+30 log(tau(u_i->m_j))。

## 18. 标题页与语言校对

**对应意见：** Reviewer 1 的全文校对要求。

**标题页原文与修改**

> 4rd Jingxin Su -> 4th Jingxin Su  
> 5rd Xiaoping Che -> 5th Xiaoping Che

**中文说明**

> 将第四作者和第五作者序数中的错误后缀 `rd` 分别改为正确的 `th`。

**正文原文与修改**

> has introduced -> have introduced  
> we modeled the problem -> we model the problem  
> we illustrate the comparative experimental evaluation results -> we present the comparative experimental results  
> a hierarchy network architecture -> a hierarchical network architecture

**中文说明**

> 分别修正并列主语的主谓一致、论文结构说明中的时态、冗余实验表述和形容词形式。标记稿只对改动词组标蓝。

## 19. 投稿正文过程性措辞审计

**删除的非出版化表述示例**

> DQN is included as the fifth method.

> DQN 被加入为第五种方法。

该类句子描述的是修改过程，而不是可独立阅读的科研内容，已从正文和图注删除。最终正文只保留中性表述：

> In Stage II, PSP is compared with four baseline strategies.

> 在 Stage II 中，PSP 与四种基线策略进行比较。

两组图注分别为：

> Service-provisioning performance with 10 deployed servers and increasing user populations.

> Service-provisioning performance with 130 users and increasing numbers of deployed edge servers.

**全文扫描：** 对最终 14 页 clean PDF 搜索 `fifth method`、`was added`、`we added`、`we revised`、`in this revision`、`current version`、`modified version`、`reviewer`、`response to`、`as requested`、`AI-generated` 和 `ChatGPT`，命中数均为 0。完整结果见 `05_publication_language_audit.md`。

## 20. 最终文件关系

| 文件 | 用途 |
|---|---|
| `conference_101719_targeted_revision_marked.tex/.pdf` | 蓝色标记修改位置，供作者与审稿人核对 |
| `conference_101719_targeted_revision_clean.tex/.pdf` | 不含修改标记的正式净稿 |
| `01_response_to_reviewers_initial_draft.md` | 逐条回信初稿 |
| `02_bilingual_manuscript_change_audit.md` | 原文、改文和中文含义逐项审计 |
| `03_remaining_manual_checklist.md` | 投稿前仍需作者确认的事项 |
| `05_publication_language_audit.md` | 最终 PDF 的过程性措辞与图注审计 |
| `spreadsheets/stage2_five_method_results_editable.xlsx` | 两组五方法数据、八张可编辑原生柱图和公式核验页 |
