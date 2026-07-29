# 原稿与修改稿全部差异中英对照审计

## 1. 审计范围与覆盖方式

- 原稿：conference_101719_first_submission.tex。
- 标记稿：conference_101719_targeted_revision_marked.tex。
- 净稿：conference_101719_targeted_revision_clean.tex。
- 自动提取结果：标记稿共有 69 段蓝色内容，包括 44 个 rev 命令、23 个 revision 环境和 2 个整表 revcolor 区块。
- 原稿与净稿的逐行比较产生 76 个差异块，其中既包括正文实质修改，也包括图片替换、LaTeX 冲突消除和版面调整。
- 为避免把同一句话拆成多个难以阅读的小项，正文将相邻且属于同一技术目的的修改合并为 26 个审计项；附录 A 将 69 段蓝色标记逐条映射到这些审计项，附录 B 将 76 个源文件差异块逐条映射到审计项或结构性修改项。

下文中的“原稿无此内容”表示该段为新增内容；中文部分解释的是修改后英文在论文中的实际含义，而不是对回复文字进行翻译。

## A01. 作者序号后缀

**覆盖：** 蓝色 B01-B02；差异 H04-H05；标记稿 L69、L75。

**原稿英文**

> 4rd Jingxin Su; 5rd Xiaoping Che.

**修改后英文**

> 4th Jingxin Su; 5th Xiaoping Che.

**中文含义**

> 第四作者 Jingxin Su；第五作者 Xiaoping Che。

**修改原因**

> 修正英文序数词后缀。4 和 5 均应使用 th，而不是 rd。

## A02. 引言中的语法与研究目标

**覆盖：** 蓝色 B03-B04；差异 H06-H07；标记稿 L95、L97。

**原稿英文**

> The emergence of new applications and the growing demand for portable services has introduced significant computational and communication burdens.

> We aim to strike an optimal balance between cost and latency, enable efficient deployment of edge servers and services, while enhancing network performance, optimizing resource allocation, and ultimately reducing the operational cost of edge servers.

**修改后英文**

> The emergence of new applications and the growing demand for portable services have introduced significant computational and communication burdens.

> We aim to balance cost and latency while enabling efficient deployment of edge servers and services, enhancing network performance, improving resource allocation, and reducing edge-server operating cost.

**修改后中文**

> 新型应用的出现以及对便携式服务不断增长的需求带来了显著的计算和通信负担。

> 本文旨在平衡成本与时延，同时实现边缘服务器和服务的高效部署，提升网络性能，改善资源分配，并降低边缘服务器的运营成本。

**修改原因**

> 第一处修正并列主语的主谓一致；第二处消除原句中 aim to、enable 与 while enhancing 之间不平行的语法结构，使研究目标更简洁、正式。

## A03. Fig. 1 图注、视觉语义与服务配置示例

**覆盖：** 蓝色 B05-B07；差异 H08-H11；标记稿 L100-L115。

**原稿英文**

> An illustrating example.

> Server deployment and service provisioning significant impact on the profit of mobile network operators. To clarify this problem, we use a scenario involving five base stations to illustrate how to choose the placement locations for servers and services.

> For example, in area 3, the deployed server can only host three service instances. Two services, s2 and s5, have already been provisioned, and the remaining slot must be assigned to one of the candidate services in {s2, s3, s4, s6}.

**修改后英文**

> MEC system model and service-provisioning scenario.

> Server deployment and service provisioning have a significant impact on the profit of mobile network operators. Figure 1 illustrates a scenario with five base stations. The solid black contours partition the topology into interconnected service regions, the black dashed circles denote the coverage areas of individual base stations, and the red dotted circles identify base stations equipped with edge servers. The blue bidirectional arrows represent cloud-edge communication, while the red dashed arrows indicate inter-region request forwarding. Distinct colors represent service types s1-s6, and each user color indicates the corresponding requested service. The service blocks beside an edge server show its instantiated services; the question-mark slot in Area 3 denotes a provisioning decision under limited server capacity.

> Each service replica serves a user request and generates income. Because an edge server can host only a subset of the service catalog, a request without a local replica is forwarded to another server that provides the requested service, incurring additional transmission cost. For example, the server in Area 4 provisions services s3 and s6; requests for the other service types require inter-area forwarding.

> Designing an effective service provisioning strategy under constrained server capacity while jointly optimizing provisioning cost and users' delay remains a significant challenge. For example, the server in Area 3 can host three service instances. Two slots are occupied by the illustrated service replicas, while the remaining slot must be assigned from the candidate services shown below the server. Since this choice affects forwarding distance, transmission cost, and service-delivery latency, the provisioning decision considers request frequency and service provisioning cost.

**修改后中文**

> MEC 系统模型与服务配置场景。

> 服务器部署与服务配置会显著影响移动网络运营商的收益。图 1 展示了一个包含五个基站的场景。黑色实线轮廓把拓扑划分为相互连接的服务区域，黑色虚线圆表示单个基站的覆盖范围，红色点线圆标识配置了边缘服务器的基站。蓝色双向箭头表示云边通信，红色虚线箭头表示跨区域请求转发。不同颜色表示服务类型 s1-s6，用户的颜色表示其请求的对应服务。边缘服务器旁的服务色块表示已经实例化的服务；Area 3 中的问号槽位表示容量受限条件下尚待决定的服务配置。

> 每个服务副本处理一个用户请求并产生收益。由于边缘服务器只能容纳服务目录中的一部分服务，本地没有副本的请求需要转发到提供该服务的其他服务器，从而产生额外传输成本。例如，Area 4 的服务器配置了 s3 和 s6，其他服务类型的请求需要跨区域转发。

> 在容量受限条件下设计有效的服务配置策略，并联合优化配置成本与用户时延，仍是一项重要挑战。Area 3 的服务器可容纳三个服务实例，图中已有两个槽位被占用，剩余槽位需要从服务器下方展示的候选服务中选择。由于该选择会影响转发距离、传输成本和服务交付时延，因此决策同时考虑请求频率和服务配置成本。

**修改原因**

> 新图保留了开放服务决策槽位，因此正文不再写死具体候选集合；服务色块、用户颜色、跨区转发和云边通信均与图中符号一一对应。图注缩短为一句，仅说明图的性质，详细解释置于正文。

## A04. 论文结构说明的时态与措辞

**覆盖：** 蓝色 B08-B09；差异 H12；标记稿 L128。

**原稿英文**

> In Section III, we modeled the problem. In Section V, we illustrate the comparative experimental evaluation results.

**修改后英文**

> In Section III, we model the problem. In Section V, we present the comparative experimental results.

**修改后中文**

> 第 III 节建立问题模型；第 V 节给出对比实验结果。

**修改原因**

> 论文结构说明统一使用一般现在时，并删除 comparative、experimental、evaluation、results 之间的冗余堆叠。

## A05. 学习型与长期优化相关工作及新增文献

**覆盖：** 蓝色 B10、B66-B69；差异 H13、H76；标记稿 L148-L150、L968-L974。

**原稿英文**

> 原稿无此段，也未列出对应的四篇参考文献。

**修改后英文**

> Optimization and learning methods also address complementary MEC resource-management objectives. Feng et al. [33] jointly optimized latency-aware service deployment and peer offloading over multiple timescales. Kato et al. [34] applied breakout local search to transmission- and processing-aware task offloading in a multi-tier cloud environment. Jing et al. [35] studied long-term max-min fairness for task splitting and resource allocation in integrated multi-RAT/MEC networks, while Jing et al. [36] used online mini-batch learning for dynamic energy-cost conservation in distributed edge clouds. These studies address dynamic offloading, fairness, or energy management; the present work focuses on interpretable server planning and capacity-constrained multi-objective service provisioning under a common cost-latency model.

**修改后中文**

> 优化与学习方法也从互补角度研究 MEC 资源管理。Feng 等人 [33] 在多个时间尺度上联合优化时延感知的服务部署与对等卸载。Kato 等人 [34] 使用突破局部搜索解决多层云环境中同时考虑传输与处理的任务卸载。Jing 等人 [35] 研究集成多 RAT/MEC 网络中任务拆分与资源分配的长期最大最小公平性，另一项 Jing 等人的工作 [36] 使用在线小批量学习降低分布式边缘云的动态能源成本。这些研究分别关注动态卸载、公平性或能源管理；本文则在统一成本-时延模型下研究可解释的服务器规划和容量受限多目标服务配置。

**修改原因**

> 补充服务部署/卸载联合优化、局部搜索式卸载、长期 MEC 公平资源分配和学习型能源管理四类相关工作，并准确界定其与本文服务器规划、容量约束和多目标服务配置问题的差异。新增 [33]-[36] 四条完整参考文献。

## A06. 系统架构形容词

**覆盖：** 蓝色 B11；差异 H14；标记稿 L157。

**原稿英文**

> a hierarchy network architecture

**修改后英文**

> a hierarchical network architecture

**修改后中文**

> 分层网络架构。

**修改原因**

> hierarchy 是名词，修饰 network architecture 时应使用形容词 hierarchical。

## A07. 服务器部署与服务配置决策变量

**覆盖：** 蓝色 B12-B13；差异 H15-H16；标记稿 L162-L170。

**原稿英文**

> We introduce a binary variable x_jk, where x_jk = 1 if an edge server m_j is deployed at base station b_k.

> Let x_jw be a binary variable indicating service deployment, and let x_ijw indicate whether user u_i is served by service s_w deployed on server w_j.

**修改后英文**

> Let y_jk be a binary server-deployment variable, where y_jk=1 if edge server m_j is deployed at base station b_k, and y_jk=0 otherwise.

> Let z_jw be a binary service-provisioning variable, where z_jw=1 if an instance of s_w is provisioned on edge server m_j, and z_jw=0 otherwise. Furthermore, let a_ijw be a binary association variable, where a_ijw=1 if user u_i is served by service s_w on server m_j, and a_ijw=0 otherwise.

**修改后中文**

> y_jk 专门表示服务器 m_j 是否部署在基站 b_k；z_jw 专门表示服务器 m_j 是否配置服务 s_w；a_ijw 专门表示用户 u_i 是否由服务器 m_j 上的服务 s_w 提供服务。

**修改原因**

> 用不同字母区分物理部署、服务配置和用户关联，消除原稿中多个 x 变量外观相近及服务器符号 w_j/m_j 混用的问题。

## A08. Table I 符号表同步

**覆盖：** 蓝色 B14-B24；差异 H17-H19；标记稿 L247-L259。

| 原稿 | 修改后英文 | 中文含义 |
|---|---|---|
| x_ij | a_ij: Indicator whether user u_i is served by m_j. | 用户 u_i 是否由服务器 m_j 服务。 |
| x_jk | y_jk: Indicator whether server m_j is deployed at base station b_k. | 服务器 m_j 是否部署在基站 b_k。 |
| x_ijw | a_ijw: Indicator whether user u_i is served by s_w on m_j. | 用户 u_i 是否由服务器 m_j 上的服务 s_w 服务。 |
| x_jw | z_jw: Indicator whether server m_j provisions service s_w. | 服务器 m_j 是否配置服务 s_w。 |
| beta_iw: hops between user u_i and server s_w | beta_iw: Number of hops between user u_i and server m_j providing s_w. | 用户 u_i 与提供服务 s_w 的服务器 m_j 之间的跳数。 |

**修改原因**

> 符号表与正文、目标函数和约束统一，修正“server s_w”把服务误写成服务器的语义错误。

## A09. 计算时延与通信时延模型说明

**覆盖：** 蓝色 B25-B26；差异 H20-H21；标记稿 L272-L279。

**修改后英文**

> In this system, user latency occurs during both computation and communication. We define D_p(m_j) as the computational latency associated with user requests processed by edge server m_j. This latency depends on the resource requirements of the requested services and the computing capabilities of the servers, and is given by D_p(m_j)=sum_i a_ijw R^c_iw / mu_j.

> Communication latency refers to data transmission between users and edge servers when a requested service is provisioned outside the user's region. The maximum transmission rate is r_ij=B_ij log2(1+gamma g_ij/N), and the communication latency is D_c(m_j)=sum_i a_ijw(R^t_iw/r_ij) beta_iw.

**修改后中文**

> 用户时延由计算和通信两部分构成。D_p(m_j) 表示边缘服务器 m_j 处理用户请求产生的计算时延，它取决于服务的计算资源需求和服务器算力。通信时延发生在所请求服务不位于用户本地区域时；最大传输速率由带宽、发射功率、噪声和信道增益确定，beta_iw 表示跨服务器转发带来的逐跳时延影响。

**修改原因**

> 在保留原始信道模型的前提下，将时延项与新的 a_ijw、m_j、s_w 决策变量体系对齐，并澄清计算时延与跨区域通信时延各自的物理含义。

## A10. 约束 (5)-(7) 与 QoS 解释

**覆盖：** 蓝色 B27-B30；差异 H22-H24；标记稿 L304-L310。

**修改后英文**

> sum_w z_jw v_w <= V_j, and sum_w z_jw varsigma_w <= mu_j.

> a_ijw(R^c_iw/mu_j + (R^t_iw/r_ij)beta_iw) <= D_i-tilde.

> y_jk, z_jw, a_ijw are binary variables.

> Equation (4) limits total server-deployment cost to budget C_max. Equation (5) enforces the storage and computing capacities of each edge server. Equation (6) provides latency-oriented QoS by requiring the end-to-end latency of a served request to remain below the user's tolerable bound. For reliability-critical applications, latency compliance can be complemented by packet-loss, link-availability, and service-interruption constraints. Equation (7) defines the three binary decision variables.

**修改后中文**

> 式 (5) 分别限制每台服务器上已配置服务的存储和计算资源总量；式 (6) 要求已服务请求的端到端时延不超过用户可容忍上限；式 (7) 规定服务器部署、服务配置和用户服务关联变量均为二进制变量。对于可靠性关键型应用，可进一步加入丢包率、链路可用性和服务中断约束。

**修改原因**

> 约束中的变量与 A07 统一，并明确当前 QoS 是时延导向的；可靠性指标被作为自然扩展进行中性说明，没有改写本文现有优化目标。

## A11. 两阶段分解的技术合理性

**覆盖：** 蓝色 B31；差异 H25；标记稿 L318-L320。

**原稿英文**

> 原稿只说明将问题分成服务器部署和服务配置两个顺序阶段，没有解释该分解与 MEC 实际规划流程的关系。

**修改后英文**

> The decomposition follows the operational hierarchy of MEC planning. Server deployment is a long-term infrastructure decision governed by budget, coverage, and geographic demand, whereas service instances are provisioned after the physical server locations are known. Stage 1 therefore resolves the spatial variables that determine deployment and transmission costs, and Stage 2 optimizes service instances and user associations on the selected infrastructure. Passing the selected locations, user assignments, and Stage-I cost to Stage 2 preserves the cost-latency dependence while substantially reducing the decision space of the service-provisioning search.

**修改后中文**

> 该分解遵循 MEC 规划的实际决策层级。服务器部署是受预算、覆盖和地理需求约束的长期基础设施决策，而服务实例在物理服务器位置确定后进行配置。Stage 1 先求解决定部署成本与传输成本的空间变量，Stage 2 再在选定基础设施上优化服务实例和用户关联。Stage 1 将已选位置、用户分配和阶段成本传递给 Stage 2，从而在显著缩小服务配置搜索空间的同时保留成本与时延之间的联系。

**修改原因**

> 回答为什么可以采用两阶段求解，同时避免在论文正文中使用针对审稿人的对话式表述。

## A12. 架构图图注与章节标题

**覆盖：** 蓝色 B32-B33；差异 H26-H28；标记稿 L344、L348。

**原稿英文**

> The overall architecture of MOS2.

> algorithm design

**修改后英文**

> Overall architecture of MOS2.

> Algorithm Design

**修改后中文**

> MOS2 的总体架构。

> 算法设计。

**修改原因**

> 图注保持一句话，并统一章节标题的首字母大写格式。

## A13. Stage II 容量检查和修复流程

**覆盖：** 蓝色 B34；差异 H29；标记稿 L363-L366。

**修改后英文**

> Given the fixed server locations, PSP constructs a hybrid initial population and applies NSGA-II to optimize provisioning cost and access delay. Crossover and mutation produce each offspring, whose entries are first rounded to binary values. For every server m_j, PSP then checks sum_w z_jw <= V_j. If the capacity is exceeded, selected service entries are randomly deactivated until feasibility is restored. Only capacity-feasible offspring are evaluated and passed to non-dominated sorting; thus, feasibility is enforced by repair rather than by a penalty function. The evolutionary process returns a set of provisioning schemes representing different cost-delay trade-offs.

**修改后中文**

> 固定服务器位置后，PSP 构造混合初始种群并利用 NSGA-II 优化配置成本和访问时延。交叉与变异生成子代后，先将变量二值化，再逐台服务器检查容量；若超限，则随机关闭已选服务，直至恢复可行。只有容量可行的子代才进入目标计算和非支配排序，最终得到反映不同成本-时延折中的配置方案集合。

**修改原因**

> 将“生成、二值化、容量检查、修复、评价和排序”的实际执行顺序完整写清，并与 Algorithm 3 以及重绘的进化优化面板一致。

## A14. Algorithm 1 随机初始化的显式命名

**覆盖：** 蓝色 B35；差异 H30；标记稿 L379。

**原稿英文**

> S <- Select(M,k).

**修改后英文**

> S <- RandomSelect(M,k).

**中文含义**

> 从候选集合 M 中随机选择 k 个位置，构成初始部署集合 S。

**修改原因**

> 明确 Algorithm 1 的默认初始化确实是随机选择，为后续初始化敏感性实验提供无歧义的算法定义。

## A15. CLS 的设施选址形式与服务器数量确定

**覆盖：** 蓝色 B36-B37；差异 H31；标记稿 L413-L416。

**修改后英文**

> We reformulate server deployment as a facility-location problem in which candidate base stations are potential server sites and users are demand points with heterogeneous service requirements. The deployment budget C_max gives the upper bound K^c=floor(C_max/min_j{p_j}) on the number of deployable servers. For each candidate base station b_k, we compute the user density sigma_k within a circular coverage region of radius r. Let K^r denote the number of candidate sites whose local density reaches threshold sigma_min. The target server count is then k=min{K^c,K^r}, reflecting both budget feasibility and the spatial distribution of demand.

**修改后中文**

> 将服务器部署重述为设施选址问题：候选基站是潜在服务器位置，用户是具有异构服务需求的需求点。预算 C_max 给出可部署服务器数量上限 K^c；覆盖半径内达到密度阈值的候选站数量给出 K^r；最终取 k=min{K^c,K^r}，同时反映预算可行性与需求的空间分布。

**修改原因**

> 明确 CLS 与 K-median/设施选址问题的联系，并给出 k 的预算约束与密度约束来源。

## A16. Algorithm 3 输入参数与逐行容量修复

**覆盖：** 蓝色 B38-B40；差异 H35-H37；标记稿 L496、L506、L515。

**原稿英文**

> Algorithm 3 的输入未列出 varpi_j；修复步骤仅写为 Repair X to satisfy capacity constraint V_j。

**修改后英文**

> The input list includes varpi_j.

> For each row j, randomly deactivate selected entries while sum_w X_jw > V_j.

> Round and reshape X'; repair each violating row as above; evaluate X'.

**修改后中文**

> Algorithm 3 将确定性锚点大小 varpi_j 列为输入。对矩阵的每一行逐台检查服务器容量，只要已选服务数超过 V_j，就随机关闭已选项；对子代 X' 先取整和重塑，再按相同步骤修复并评价。

**修改原因**

> 将原来笼统的“repair”改成可复现的逐行操作，并补齐算法实际依赖的初始化参数。

## A17. Stage I 与第一组 Stage II 图注

**覆盖：** 蓝色 B41-B43；差异 H38-H44；标记稿 L540、L548、L555。

| 修改后英文图注 | 中文 |
|---|---|
| Stage-I server-deployment performance under different server and user scales. | 不同服务器和用户规模下的 Stage-I 服务器部署性能。 |
| Stage-I cost analysis under varying server counts and CLS iterations. | 不同服务器数量和 CLS 迭代过程下的 Stage-I 成本分析。 |
| Service-provisioning performance with 10 deployed servers and increasing user populations. | 固定部署 10 台服务器、逐步增加用户数量时的服务配置性能。 |

**修改原因**

> 将冗长解释移出图注，图注仅说明图的对象和控制变量；同时使用重新组合的清晰 PDF 替换原先分散的子图代码。

## A18. PSP 编码矩阵、成本函数与容量修复

**覆盖：** 蓝色 B44-B45；差异 H45-H50；标记稿 L562-L574。

**修改后英文**

> A service-provisioning scheme is encoded by a binary matrix indiv in {0,1}^{k x |S|}. Each row corresponds to a deployed server and each column to a service type. The entry indiv[j,w] is the encoded counterpart of z_jw: it equals 1 when service s_w is provisioned on server m_j, and 0 otherwise. The provisioning cost on m_j is C_p(m_j)=sum_w indiv[j,w]sc_w, and each row satisfies sum_w indiv[j,w] <= V_j.

> After crossover and mutation, every encoded entry is rounded to 0 or 1. If the row sum exceeds V_j, selected entries in that row are randomly set to 0 until the capacity constraint is satisfied. Objective evaluation and non-dominated sorting are then performed on the repaired feasible individual.

**修改后中文**

> 服务配置方案编码为 k×|S| 的二进制矩阵 indiv，每行对应一台已部署服务器，每列对应一种服务。indiv[j,w] 是数学变量 z_jw 的算法编码：1 表示在 m_j 上配置 s_w，0 表示未配置。服务器 m_j 的配置成本是该行已选服务成本之和，每行已选服务数量不得超过 V_j。

> 交叉和变异后，所有元素先取为 0 或 1。若某行超过容量，则随机将该行已选项置 0，直到满足容量约束；之后才进行目标评价和非支配排序。

**修改原因**

> 建立算法编码与数学模型之间的一一对应关系，并消除原稿成本公式中对服务器索引重复求和的问题。

## A19. 混合初始化、混合评分与示意图

**覆盖：** 蓝色 B46-B48；差异 H51-H56；标记稿 L576-L609。

**修改后英文**

> PSP uses a hybrid initialization before the NSGA-II evolutionary loop. For each server, it constructs one ranking that favors low provisioning cost and another that favors services requested frequently by locally assigned users. The two rankings are fused by a hybrid score. High-scoring services form a deterministic anchor set, and the remaining capacity is filled by stochastic sampling from lower-ranked candidates.

> Let alpha and beta balance provisioning cost and local demand, with alpha+beta=1. Let varpi_j denote the deterministic anchor size on edge server m_j. The hybrid score is H_j(s_w)=alpha w_cost,j(s_w)+beta w_req,j(s_w). We set varpi_j=ceil(rho V_j) with rho=0.5, reserving half of the capacity for high-ranked deterministic services and half for stochastic selection from the remaining candidates.

> Figure 7 illustrates the construction for Server 0. Panel (a) decomposes each candidate's hybrid score into cost- and request-oriented components, and panel (b) shows the deterministic anchor, stochastic fill, and discarded candidates under the capacity limit.

**修改后中文**

> PSP 在 NSGA-II 进化前使用混合初始化。每台服务器分别建立偏好低配置成本和偏好高本地请求频率的两个排序，再通过混合评分融合。高分服务构成确定性锚点，其余容量从较低排名候选中随机填充。

> alpha 与 beta 平衡配置成本和本地需求，且二者之和为 1。varpi_j 表示服务器 m_j 上确定性锚点的大小，混合评分为 H_j(s_w)=alpha w_cost,j(s_w)+beta w_req,j(s_w)。设置 varpi_j=ceil(rho V_j)，rho=0.5，即一半容量用于保留高分确定性服务，另一半用于随机探索。

> 图 7 以 Server 0 为例：子图 (a) 展示成本分量和请求分量如何构成混合评分，子图 (b) 展示容量限制下的确定性锚点、随机填充和被舍弃候选。

**修改原因**

> 将原稿含糊的“cost and delay greedy”改为代码实际使用的配置成本与本地请求频率评分，并给 varpi_j 提供随容量缩放且可解释的比例定义。

## A20. NSGA-II 种群更新、Q 的用途与输入集合

**覆盖：** 蓝色 B49-B51；差异 H57-H58；标记稿 L613-L660。

**修改后英文**

> Each generation merges the parent and offspring populations and retains N individuals according to non-dominated rank and crowding distance. At generation G, PSP returns the non-dominated capacity-feasible provisioning schemes found by the search.

> The normalized score Q is applied after optimization to select one balanced solution for scalar comparison; it is not an objective used to generate the Pareto population.

> Let M be the set of deployed servers obtained from Stage 1, U the set of user positions, S the service catalog, and k=|M| the number of deployed servers.

**修改后中文**

> 每一代合并父代和子代，并依据非支配等级与拥挤距离保留 N 个个体；达到第 G 代后，PSP 返回搜索到的容量可行非支配配置方案。归一化分数 Q 只在优化结束后用于选择一个平衡解进行标量比较，并不参与 Pareto 种群生成。M、U、S 和 k 分别表示 Stage 1 得到的已部署服务器集合、用户位置集合、服务目录和服务器数量。

**修改原因**

> 澄清 PSP 输出的是 Pareto 解集，而 Q 是后处理评价指标；同时让算法输入符号自包含。

## A21. 混合初始化、固定用户和 Pareto 图注

**覆盖：** 蓝色 B52-B54；差异 H59-H65；标记稿 L686、L748、L763。

| 修改后英文图注 | 中文 |
|---|---|
| Hybrid initialization for candidate services on Server 0. | Server 0 上候选服务的混合初始化。 |
| Service-provisioning performance with 130 users and increasing numbers of deployed edge servers. | 固定 130 个用户、逐步增加部署服务器数量时的服务配置性能。 |
| Pareto fronts for Stage-II service provisioning with 130 users. | 130 个用户条件下 Stage-II 服务配置的 Pareto 前沿。 |

**修改原因**

> 图注只说明图的内容，所有指标解释和结果分析均移到正文；对应图件以清晰的组合 PDF 替换原来的多段子图代码。

## A22. PSP 参数、varpi_j 比例、Q、HV 与 IGD

**覆盖：** 蓝色 B55-B56；差异 H66；标记稿 L777-L811。

**原稿状态**

> 原稿没有集中列出进化参数，也没有给出 Q 的归一化公式、权重以及 HV/IGD 定义。

**修改后英文**

> The deterministic anchor size is defined proportionally as varpi_j=ceil(rho V_j) with rho=0.5. Hence, for V_j=4, two slots retain the highest-scoring services and two slots preserve stochastic exploration.

> C-hat=(C-C_min)/(C_max-C_min), D-hat=(D-D_min)/(D_max-D_min), and Q=lambda C-hat+(1-lambda)D-hat with lambda=0.5. Lower Q indicates a better balanced solution.

> Hypervolume (HV) measures the dominated objective-space volume relative to the reference point (1.1,1.1) and is maximized, whereas inverted generational distance (IGD) measures the mean distance from the common non-dominated reference front to a method's front and is minimized.

> Table II reports N=50, G=200, SBX p_c=0.9 and eta_c=15, polynomial mutation p_m=1/(k|S|) and eta_m=20, alpha=beta=0.5, V_j=4, and rho=0.5.

**修改后中文**

> 确定性锚点大小按 varpi_j=ceil(rho V_j) 设置，rho=0.5。实验中 V_j=4，因此两个槽位保留最高评分服务，另两个槽位用于随机探索。

> 成本和时延在同一配置下按所有对比方法的合并解集进行 min-max 归一化，Q 使用等权重 0.5。Q 越低表示成本与时延的综合平衡越好。HV 衡量相对于参考点的支配空间体积，越高越好；IGD 衡量方法前沿与公共非支配参考前沿之间的距离，越低越好。

> Table II 集中列出种群规模、代数、交叉与变异参数、混合评分权重、服务器服务容量和锚点比例。

**修改原因**

> 补齐实验可复现所需的参数和评价定义，并解释 varpi_j=V_j/2 的利用-探索含义。

## A23. 对比基线与简化后的 DQN 介绍

**覆盖：** 蓝色 B57-B60；差异 H67-H70；标记稿 L831-L848。

**原稿英文**

> In stage I, we introduced four baselines in comparison with our proposed CLS algorithm.

> In stage II, we introduced three baselines in comparison with our proposed PSP algorithm.

> NS-P uses random service provisioning strategies. 原稿无 DQN 基线。

**修改后英文**

> In Stage I, CLS is compared with four baseline methods.

> In Stage II, PSP is compared with four baseline strategies.

> NSGA-II Provision (NS-P): The initial population is generated randomly.

> Deep Q-Network Provision (DQN): A Q-network sequentially selects a service or an empty action for each server slot using demand, deployment cost, and a cost-delay preference. The resulting deployment is evaluated by the same objectives as the other methods.

**修改后中文**

> Stage I 将 CLS 与四种基线方法进行比较；Stage II 将 PSP 与四种基线策略进行比较。NS-P 随机生成初始种群。DQN 使用 Q 网络依次为每个服务器槽位选择服务或空动作，决策依据包括需求、配置成本和成本-时延偏好；所得部署方案采用与其他方法相同的目标进行评价。

**修改原因**

> 使用中性、可直接投稿的表述，不写“新增第五种方法”等修改过程。DQN 只保留方法核心，长度与其他基线接近，网络结构和训练细节留在复现材料中。

## A24. CLS 初始化敏感性实验

**覆盖：** 蓝色 B61-B62；差异 H71；标记稿 L853-L860。

**原稿状态**

> Algorithm 1 随机生成初始集合 S，但原稿没有初始化敏感性实验。

**修改后英文**

> To examine the effect of the initial deployment set in Algorithm 1, we compare Random, Density, DistSum, marginal Greedy, and Diverse initialization over 50 runs. For each configuration, the reported gap is the percentage difference between the final cost and the best final cost observed under the same server/user setting. The five strategies reach the same best final cost in nearly all fixed-130-user cases; the only nonzero entry is the 2.10% mean gap of Random at 10 servers. Under the 10-server/150-user setting, Random obtains a 1.27% mean gap, whereas marginal Greedy reaches 15.88%. These results show that CLS is generally stable across initializations and that random initialization avoids a systematic preference for a poorer local optimum.

> Initialization sensitivity of CLS under two server/user settings.

**修改后中文**

> 为考察 Algorithm 1 初始部署集合的影响，在 50 次运行中比较 Random、Density、DistSum、marginal Greedy 和 Diverse 五种初始化。gap 表示最终成本相对同一配置下最佳最终成本的百分比差。在固定 130 个用户时，五种策略在几乎全部配置中达到相同最佳成本，唯一非零项是 10 台服务器时 Random 的 2.10%。在 10 台服务器、150 个用户时，Random 的平均差距为 1.27%，marginal Greedy 为 15.88%。结果表明 CLS 对初始化总体稳定，随机初始化也避免了确定性策略系统性偏向较差局部最优。

> 两种服务器/用户设置下 CLS 的初始化敏感性。

**修改原因**

> 直接回答 CLS 是否受随机初始集合影响，并用多种确定性和随机策略、重复运行以及统一 gap 定义提供证据。

## A25. Stage II 两组实验、Pareto 指标与 DQN 结果

**覆盖：** 蓝色 B63-B64；差异 H72-H74；标记稿 L876-L897。

**修改后英文**

> We evaluate Stage II under two complementary configurations: (i) 10 deployed servers with 100, 130, 150, and 180 users, and (ii) 130 users with 5, 10, 15, and 20 deployed servers. Figures 5 and 7 report the minimum normalized score Q obtained by each method. PSP achieves the lowest Q in every reported case across both experimental series. Its hybrid initialization consistently improves upon random NS-P and the single-criterion GCP and GDP initializations; PSP also achieves lower Q than DQN across all tested scales.

> Figure 8 compares the cost-delay fronts generated by the four NSGA-II-based provisioning strategies with 130 users. For the 10-server setting, PSP attains the largest HV (0.9470), the smallest IGD (0.0016), and the smallest Q (0.3282). DQN produces a limited set of scalarized solutions rather than a population-based Pareto front; it is therefore compared through Q and is not included in the HV/IGD comparison.

**修改后中文**

> Stage II 包含两组互补配置：固定 10 台服务器，将用户数设为 100、130、150 和 180；固定 130 个用户，将服务器数设为 5、10、15 和 20。两组图报告各方法得到的最小归一化 Q，PSP 在所有展示配置中均取得最低 Q。其混合初始化优于随机 NS-P 以及单一准则 GCP 和 GDP；在全部测试规模下，PSP 的 Q 也均低于 DQN。

> 固定 130 个用户的图比较四种基于 NSGA-II 的方法产生的成本-时延前沿。在 10 台服务器时，PSP 的 HV 最大，为 0.9470；IGD 最小，为 0.0016；Q 最小，为 0.3282。DQN 生成的是有限个标量化解，而不是种群型 Pareto 前沿，因此 DQN 通过 Q 比较，不纳入 HV/IGD 对比。

**修改原因**

> 用统一指标解释两组柱形结果，并为 Pareto 曲线补充数值证据。DQN 不被伪装成连续 Pareto 曲线，比较边界在正文中明确。

**修改后表格数据**

| Method | HV 越高越好 | IGD 越低越好 | Best Q 越低越好 |
|---|---:|---:|---:|
| NS-P | 0.8191 | 0.0785 | 0.3894 |
| GCP | 0.8596 | 0.0492 | 0.3550 |
| GDP | 0.8945 | 0.0326 | 0.3363 |
| PSP | **0.9470** | **0.0016** | **0.3282** |
| DQN | -- | -- | 0.6125 |

## A26. 结论中的后续研究范围

**覆盖：** 蓝色 B65；差异 H75；标记稿 L911。

**原稿英文**

> Future work will explore joint learning-based optimization for content popularity and mobility pattern estimation, and further extend the framework to handle federated scenarios with multi-domain coordination.

**修改后英文**

> Future work will extend the framework with reliability-aware QoS constraints for packet loss, link availability, and service interruption, together with learning-based demand prediction and multi-domain coordination.

**修改后中文**

> 后续研究将通过丢包率、链路可用性和服务中断等可靠性感知 QoS 约束扩展该框架，并研究基于学习的需求预测和多域协同。

**修改原因**

> 与正文对 QoS 范围的说明保持一致，同时保留学习型需求预测和多域协同这两个原有研究方向。

## 2. 非蓝色但与原稿不同的结构、图片和排版修改

### S01. LaTeX 宏包冲突消除

**差异：** H01-H03。

- 删除同时加载的 algorithmic 和 algpseudocode，保留稿件实际使用的算法环境，避免命令重定义冲突。
- 删除第二次重复加载的 amsmath。
- 将重复的 usepackage[bookmarks=false]{hyperref} 改为 hypersetup{bookmarks=false}，避免重复加载 hyperref。
- 这些修改不改变论文内容，只保证本地与 Overleaf 可稳定编译。

### S02. Fig. 1 资源替换和无外框裁切

**差异：** H08-H09。

- 原资源 figure1_0422.pdf 替换为作者指定 Visio 页面导出的 figure1_user_selected_no_outer_border.pdf。
- 只裁掉导出页面最外围 1.5 pt 黑色边框，未裁剪图中区域轮廓、基站覆盖圈、服务色块、用户、箭头或文字。
- LaTeX 仍使用 1.0 columnwidth，保持原稿左侧单栏大小。
- 移除图前后的负 vspace，避免图注和正文间距过紧。

### S03. Algorithm 2 混合评分下标一致性

**差异：** H33-H34。

- H(s_w) 改为 H_j(s_w)，排序语句同步使用 H_j。
- 该修改与正文中服务器相关的 w_cost,j 和 w_req,j 一致，表示同一服务在不同服务器上可因本地请求不同而获得不同评分。

### S04. Algorithm 2 输出行格式

**差异：** H32。

- 删除 KwOut 行末不必要的强制换行符，仅消除 algorithm2e 环境的版面异常，不改变算法含义。

### S05. 实验图件组合与浮动位置

**差异：** H38-H44、H59-H65。

- Stage-I 规模图、Stage-I 成本/收敛图、两组 Stage-II 五方法柱形图和混合初始化图改用预先组合的清晰 PDF。
- Stage-II 两组柱形图包含 NS-P、PSP、GCP、GDP 和 DQN；方法名称已直接写在横轴，因而删除冗余共享图例，并使图体尺寸与 Stage-I 多面板图一致。不使用把五个算法横向离散程度误作实验方差的误差棒。
- CLS 初始化敏感性双图增加了面板间距；Random 的重复运行标准误与确定性 Greedy 的零标准误原本会形成单侧可见误差棒，为避免不必要的视觉不对称，图中统一只展示均值。
- Pareto fronts 保留第一次投稿所用的四幅原始数据 PDF。
- figure* 使用 [!t] 以减少跨栏图漂移；少量 vspace 从 -10 pt 调整为 -7 pt 或删除，避免图注挤压正文。

### S06. 紧凑型 Evolutionary Optimization 面板

- 新面板按用户给出的参考图精确输出为 513×253 像素，宽高比约 2.028:1。
- 流程为 Parent Population -> Crossover & Mutation -> Offspring -> Capacity Check；超限进入 Repair: Drop Service，可行解与修复解汇合后依次进入 Merge & Evaluate、Non-dominated Sort & Crowding、Next Generation。
- 数学量使用正常上下标：P_t、Q_t、P_{t+1} 和 sum_w z_jw <= V_j。
- 面板没有外围边框，提供 PDF、SVG 和 PNG，供作者手工替换 Fig. 2 中对应区域；整幅 Fig. 2 原稿仍保留，便于回退。

## 附录 A：69 段蓝色标记的逐条覆盖映射

| 蓝色编号 | 标记稿位置 | 类型 | 本文审计项 |
|---:|---:|---|---|
| B01 | L69 | rev | A01 作者 4th |
| B02 | L75 | rev | A01 作者 5th |
| B03 | L95 | rev | A02 have introduced |
| B04 | L97 | rev | A02 研究目标 |
| B05 | L101 | rev | A03 Fig. 1 图注 |
| B06 | L106-L109 | revision | A03 Fig. 1 视觉解释 |
| B07 | L113-L115 | revision | A03 服务槽位示例 |
| B08 | L128 | rev | A04 model |
| B09 | L128 | rev | A04 present the comparative experimental results |
| B10 | L148-L150 | revision | A05 学习型相关工作 |
| B11 | L157 | rev | A06 hierarchical |
| B12 | L162-L164 | revision | A07 服务器部署变量 |
| B13 | L168-L170 | revision | A07 服务配置变量 |
| B14 | L247 | rev | A08 a_ij |
| B15 | L247 | rev | A08 a_ij 含义 |
| B16 | L248 | rev | A08 y_jk |
| B17 | L248 | rev | A08 y_jk 含义第一行 |
| B18 | L249 | rev | A08 y_jk 含义第二行 |
| B19 | L250 | rev | A08 a_ijw |
| B20 | L250 | rev | A08 a_ijw 含义 |
| B21 | L251 | rev | A08 z_jw |
| B22 | L251 | rev | A08 z_jw 含义 |
| B23 | L259 | rev | A08 beta_iw |
| B24 | L259 | rev | A08 beta_iw 含义 |
| B25 | L272-L274 | revision | A09 计算时延 |
| B26 | L277-L279 | revision | A09 通信时延 |
| B27 | L304 | rev | A10 容量约束 |
| B28 | L305 | rev | A10 时延约束 |
| B29 | L306 | rev | A10 二进制变量 |
| B30 | L308-L310 | revision | A10 约束解释与 QoS |
| B31 | L318-L320 | revision | A11 两阶段分解 |
| B32 | L344 | rev | A12 架构图图注 |
| B33 | L348 | rev | A12 Algorithm Design 标题 |
| B34 | L363-L366 | revision | A13 Stage II 流程 |
| B35 | L379 | rev | A14 RandomSelect |
| B36 | L413-L415 | revision | A15 CLS 设施选址说明 |
| B37 | L416 | rev | A15 Algorithm 1 引用 |
| B38 | L496 | rev | A16 varpi_j 输入 |
| B39 | L506 | rev | A16 初始个体修复 |
| B40 | L515 | rev | A16 子代修复 |
| B41 | L540 | rev | A17 Stage-I 规模图注 |
| B42 | L548 | rev | A17 Stage-I 成本图注 |
| B43 | L555 | rev | A17 固定服务器图注 |
| B44 | L562-L571 | revision | A18 编码矩阵与成本 |
| B45 | L572-L574 | revision | A18 容量修复 |
| B46 | L576-L578 | revision | A19 混合初始化概述 |
| B47 | L580-L589 | revision | A19 混合评分与比例锚点 |
| B48 | L607-L609 | revision | A19 混合初始化示意图说明 |
| B49 | L613-L615 | revision | A20 种群更新 |
| B50 | L616-L618 | revision | A20 Q 的用途 |
| B51 | L658-L660 | revision | A20 输入集合 |
| B52 | L686 | rev | A21 混合初始化图注 |
| B53 | L748 | rev | A21 固定用户图注 |
| B54 | L763 | rev | A21 Pareto 图注 |
| B55 | L777-L792 | revision | A22 参数、Q、HV、IGD |
| B56 | L796-L811 | revcolor | A22 参数表 |
| B57 | L831 | rev | A23 Stage I 基线引导句 |
| B58 | L840-L842 | revision | A23 Stage II 基线引导句 |
| B59 | L845 | rev | A23 NS-P |
| B60 | L848 | rev | A23 DQN |
| B61 | L853-L855 | revision | A24 CLS 初始化实验 |
| B62 | L860 | rev | A24 CLS 初始化图注 |
| B63 | L876-L880 | revision | A25 Stage II 结果 |
| B64 | L884-L897 | revcolor | A25 Pareto 指标表 |
| B65 | L911 | rev | A26 Future work |
| B66 | L968 | rev | A05 参考文献 [33] |
| B67 | L970 | rev | A05 参考文献 [34] |
| B68 | L972 | rev | A05 参考文献 [35] |
| B69 | L974 | rev | A05 参考文献 [36] |

## 附录 B：76 个原稿—净稿差异块覆盖映射

| 差异编号 | 原稿行 | 净稿行 | 归类 |
|---:|---:|---:|---|
| H01 | O7-O8 | R7-R6 | S01 删除冲突算法包 |
| H02 | O15 | R13-R12 | S01 删除重复 amsmath |
| H03 | O24 | R21 | S01 hyperref 改为 hypersetup |
| H04 | O61 | R58 | A01 第四作者序号 |
| H05 | O67 | R64 | A01 第五作者序号 |
| H06 | O87 | R84 | A02 主谓一致 |
| H07 | O89 | R86 | A02 研究目标 |
| H08 | O92-O94 | R89-R90 | S02 Fig. 1 资源与 A03 图注 |
| H09 | O96 | R92-R91 | S02 删除 Fig. 1 后负间距 |
| H10 | O100-O105 | R95-R98 | A03 Fig. 1 视觉解释 |
| H11 | O109 | R102-R104 | A03 服务槽位示例 |
| H12 | O122 | R117 | A04 论文结构 |
| H13 | O142-O141 | R137-R140 | A05 相关工作 |
| H14 | O147 | R146 | A06 hierarchical |
| H15 | O152 | R151-R153 | A07 服务器部署变量 |
| H16 | O156 | R157-R159 | A07 服务配置与关联变量 |
| H17 | O233-O234 | R236-R237 | A08 a_ij 与 y_jk |
| H18 | O236-O237 | R239-R240 | A08 a_ijw 与 z_jw |
| H19 | O245 | R248 | A08 beta_iw |
| H20 | O258 | R261-R263 | A09 计算时延 |
| H21 | O261 | R266-R268 | A09 通信时延 |
| H22 | O286-O288 | R293-R295 | A10 约束公式 |
| H23 | O290-O289 | R297-R299 | A10 新约束解释 |
| H24 | O291 | R301-R300 | A10 删除旧约束解释 |
| H25 | O297-O296 | R306-R309 | A11 两阶段分解 |
| H26 | O320-O321 | R333 | A12 架构图图注与 S05 间距 |
| H27 | O323 | R335-R334 | S05 删除架构图后负间距 |
| H28 | O326 | R337 | A12 章节标题 |
| H29 | O341-O342 | R352-R355 | A13 Stage II 流程 |
| H30 | O355 | R368 | A14 RandomSelect |
| H31 | O389-O390 | R402-R405 | A15 CLS 说明 |
| H32 | O401 | R416 | S04 Algorithm 2 输出格式 |
| H33 | O410 | R425 | S03 H_j 评分 |
| H34 | O412 | R427 | S03 H_j 排序 |
| H35 | O470 | R485 | A16 varpi_j 输入 |
| H36 | O480 | R495 | A16 初始个体容量修复 |
| H37 | O489 | R504 | A16 子代容量修复 |
| H38 | O513-O522 | R528-R529 | A17 Stage-I 规模图与 S05 组合图 |
| H39 | O524 | R531 | S05 Stage-I 规模图间距 |
| H40 | O529-O535 | R536-R537 | A17 Stage-I 成本图与 S05 组合图 |
| H41 | O537 | R539 | S05 Stage-I 成本图间距 |
| H42 | O539 | R541 | S05 跨栏图浮动位置 |
| H43 | O541-O558 | R543-R544 | A17 固定服务器图与 S05 五方法组合图 |
| H44 | O560 | R546-R545 | S05 删除固定服务器图后负间距 |
| H45 | O566 | R551-R552 | A18 编码矩阵 |
| H46 | O568 | R554 | A18 配置成本公式 |
| H47 | O570 | R556 | A18 容量约束引导句 |
| H48 | O574 | R560-R559 | A18 删除旧笼统修复句 |
| H49 | O576-O580 | R561-R567 | A18 修复与 A19 混合初始化 |
| H50 | O582-O581 | R569 | A19 定义前版面衔接 |
| H51 | O583 | R571 | A19 混合评分定义 |
| H52 | O585 | R573-R574 | A19 H_j 公式 |
| H53 | O587 | R576 | A19 评分分量 |
| H54 | O589-O588 | R578 | A19 定义后版面衔接 |
| H55 | O597 | R587 | A19 H_j 引用与 S03 下标 |
| H56 | O606 | R596-R598 | A19 混合初始化图说明 |
| H57 | O610 | R602-R607 | A20 种群更新和 Q 用途 |
| H58 | O650-O653 | R647-R649 | A20 输入集合 |
| H59 | O678-O684 | R674-R675 | A21 混合初始化图与 S05 组合图 |
| H60 | O686 | R677 | S05 混合初始化图间距 |
| H61 | O743 | R734 | S05 固定用户跨栏图位置 |
| H62 | O745-O762 | R736-R737 | A21 固定用户图与 S05 五方法组合图 |
| H63 | O764 | R739-R738 | S05 删除固定用户图后负间距 |
| H64 | O778-O779 | R752 | A21 Pareto 图注与 S05 间距 |
| H65 | O781 | R754 | S05 Pareto 图后间距 |
| H66 | O792-O791 | R765-R800 | A22 参数、Q、HV、IGD 与参数表 |
| H67 | O811 | R820 | A23 Stage I 基线引导句 |
| H68 | O820 | R829-R831 | A23 Stage II 基线引导句 |
| H69 | O823 | R834 | A23 NS-P |
| H70 | O826-O825 | R837 | A23 DQN |
| H71 | O830-O829 | R842-R851 | A24 CLS 初始化实验 |
| H72 | O843-O847 | R865-R864 | A25 删除旧枚举式实验引导 |
| H73 | O849 | R866 | A25 两组 Q 结果 |
| H74 | O851 | R868-R886 | A25 Pareto 结果与指标表 |
| H75 | O865 | R900 | A26 Future work |
| H76 | O922-O921 | R956-R964 | A05 新增参考文献 |

## 3. 当前图件和文件位置

| 内容 | 文件 |
|---|---|
| 513×253 紧凑进化优化面板 PDF | figures/fig2_evolutionary_optimization_panel_compact.pdf |
| 可编辑矢量版本 | figures/fig2_evolutionary_optimization_panel_compact.svg |
| 精确尺寸预览 | figures/fig2_evolutionary_optimization_panel_compact.png |
| 无外围黑框 Fig. 1 | figures/figure1_user_selected_no_outer_border.pdf |
| 蓝色标记稿 | manuscript/conference_101719_targeted_revision_marked.tex/.pdf |
| 正式净稿 | manuscript/conference_101719_targeted_revision_clean.tex/.pdf |

本审计文档用于作者核对；论文正文和净稿中不包含“新增、修改后、审稿人要求、第五种方法”等过程性语言。
