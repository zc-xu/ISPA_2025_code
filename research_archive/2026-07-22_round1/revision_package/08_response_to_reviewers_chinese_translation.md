# 回信逐条中英对照核对稿

**原稿编号：** IoT-65990-2026  
**论文题目：** *MOS²: A Two-Stage Multi-Objective Framework for Server Deployment and Service Provisioning in Mobile Edge Computing*

> 本文档与 `07_response_to_editor_and_reviewers.docx` 的条目顺序和回复内容一一对应，用于中文核对。Word 中的浅蓝色框直接列出修改后的论文原文；仅用于回信佐证的联合优化和真实区域实验不作为论文正文修改列出。

## 副编辑

### 副编辑意见

**英文建议原文**

> This is an extended version of a conference paper. I can see there are quite some new contents for algorithm, experiments, etc., so a submission to a journal is reasonable to me. We got the comments from two reviewers, both offered detailed comments and overall recommendations, that are not positive enough for an acceptance. I recommend a reject, but meanwhile suggest to offer the authors a chance to revise significantly and re-submit; however the authors can also consider submitting this work to other more suitable journals. Note that the authors shall feel free to evaluate each reference and only cite those with true and big enough relevance to this study.

**建议中文翻译**

这是会议论文的扩展版本。我看到在算法、实验等方面加入了相当多的新内容，因此向期刊投稿是合理的。两位审稿人都给出了详细意见，但总体建议尚不足以支持接收。副编辑建议拒稿，同时给予作者进行大幅修改后重新投稿的机会；作者也可以考虑其他更合适的期刊。作者可自行评估每篇建议文献，只引用与本研究真正且充分相关的工作。

**英文回复**

Thank you for recognizing the journal-level extension and for allowing a substantially revised resubmission. We have addressed every technical and presentation issue raised by the two reviewers. The marked manuscript highlights all changes in blue, and a clean version is provided separately. The revision includes a redesigned system illustration and algorithm flow, a unified notation system, a technical rationale for the two-stage formulation, an explicit feasibility-repair procedure, additional reproducibility details, a CLS initialization-sensitivity study, a DQN baseline, quantitative Pareto metrics, and focused supporting experiments.

We also followed the guidance on references. Each of the six suggested works was evaluated individually. Four directly relevant studies on service deployment/offloading, local search, long-term MEC resource allocation, and online learning were incorporated into the Related Work section. The two FSO-enabled SAGIN task-offloading studies were not cited because their network architecture, link model, and decision variables differ substantially from the terrestrial capacity-constrained service-provisioning problem considered here.

**中文回复**

感谢副编辑认可本稿作为期刊扩展版本的合理性，并给予大幅修改后重新投稿的机会。我们已经逐条处理两位审稿人提出的技术与表达问题。标记稿以蓝色显示全部修改，并另附无标记正式稿。主要修改包括重构系统示意图和算法流程图、统一符号体系、补充两阶段分解的技术依据、明确可行性修复流程、完善复现参数、增加 CLS 初始化敏感性实验、DQN 学习型基线、Pareto 定量指标以及有针对性的补充实验。

我们也遵循了参考文献选择建议，对六篇推荐文献逐篇评估。与服务部署/卸载、局部搜索、长期 MEC 资源分配和在线学习直接相关的四篇文献已纳入 Related Work；另外两篇聚焦 FSO 支持的 SAGIN 任务卸载，其网络架构、链路模型和决策变量与本文的地面 MEC 容量受限服务配置问题差异较大，因此未机械引用。

---

## 审稿人 1

### 意见 1：Clarity of Fig. 1 and the dashed regions

**英文建议原文**

> Figure 1 in the paper is somewhat cluttered and difficult to follow. Specifically, the regions enclosed by the dashed lines are not clearly explained. The authors should refine the visual layout of this figure and provide a more explicit description in both the text and the caption regarding what these dashed areas represent.

**建议中文翻译**

论文中的图 1 有些拥挤，不易理解。尤其是虚线圈出的区域没有得到清楚解释。作者应改进图的视觉布局，并在正文和图注中更明确地说明这些虚线区域代表什么。

**英文回复**

Thank you for identifying the ambiguity in Fig. 1. We revised the illustration and its accompanying explanation so that every visual element has a unique meaning. The solid black contours partition the topology into interconnected service regions; the black dashed circles denote individual base-station coverage areas; the red dotted circles identify base stations equipped with edge servers; blue bidirectional arrows represent cloud-edge communication; and red dashed arrows indicate inter-region request forwarding. User colors correspond to requested service types, and the service blocks beside an edge server identify its instantiated services. The question-mark slot in Area 3 deliberately represents the remaining provisioning decision under limited capacity.

The caption is now a concise one-sentence description, while the main text explains the dashed regions, routing arrows, service colors, instantiated services, and the open service slot in detail.

**中文回复**

感谢审稿人指出图 1 的歧义。我们重新设计了图示及其配套说明，使每一种视觉元素只表达一种含义：黑色实线轮廓划分相互连接的服务区域；黑色虚线圆表示单个基站覆盖范围；红色点线圆标识配置了边缘服务器的基站；蓝色双向箭头表示云边通信；红色虚线箭头表示跨区域请求转发。用户颜色与其请求的服务类型对应，边缘服务器旁的色块表示已实例化服务，Area 3 的问号槽位用于表示容量受限条件下尚待确定的服务配置。

图注已压缩为一句概括性说明，虚线区域、转发箭头、服务颜色、已配置服务和开放槽位的具体含义均在正文中详细解释。

**论文修改后原文**

**位置：** Section I-A, Fig. 1 and the accompanying discussion

> *Fig. 1. MEC system model and service-provisioning scenario.*

> Server deployment and service provisioning have a significant impact on the profit of mobile network operators. Figure 1 illustrates a scenario with five base stations. The solid black contours partition the topology into interconnected service regions, the black dashed circles denote the coverage areas of individual base stations, and the red dotted circles identify base stations equipped with edge servers. The blue bidirectional arrows represent cloud-edge communication, while the red dashed arrows indicate inter-region request forwarding. Distinct colors represent service types $s_1\text{--}s_6$, and each user color indicates the corresponding requested service. The service blocks beside an edge server show its instantiated services; the question-mark slot in Area 3 denotes a provisioning decision under limited server capacity.

> Each service replica serves a user request and generates income. Because an edge server can host only a subset of the service catalog, a request without a local replica is forwarded to another server that provides the requested service, incurring additional transmission cost. For example, the server in Area 4 provisions services $s_3$ and $s_6$; requests for the other service types require inter-area forwarding.

**修改后原文中文翻译**

图 1. MEC 系统模型与服务配置场景。

服务器部署和服务配置对移动网络运营商的收益具有显著影响。图 1 展示了一个包含五个基站的场景。黑色实线轮廓将拓扑划分为相互连接的服务区域，黑色虚线圆表示各基站的覆盖区域，红色点线圆标识配置了边缘服务器的基站。蓝色双向箭头表示云边通信，红色虚线箭头表示跨区域请求转发。不同颜色表示服务类型 $s_1\text{--}s_6$，每个用户的颜色表示其对应的请求服务。边缘服务器旁的服务色块表示其实例化的服务；Area 3 中带问号的槽位表示服务器容量受限条件下尚待确定的配置决策。

每个服务副本处理一个用户请求并产生收益。由于边缘服务器只能承载服务目录中的一部分服务，若本地没有相应副本，请求将被转发到能够提供该服务的其他服务器，从而产生额外传输成本。例如，Area 4 的服务器配置了服务 $s_3$ 和 $s_6$；对其他服务类型的请求需要跨区域转发。


**证据与数据**

证据图：`response_evidence/fig1_revised.png`（修改后的 Fig. 1）。

---

### 意见 2：Conflicting decision-variable notation

**英文建议原文**

> There are some conflicts and visual similarities in the defined notations, particularly concerning the decision variables. For example, $x_{ijw}$ and $x_{jw}$ are used to denote different concepts, which may easily confuse the readers. It is strongly recommended to use completely distinct variable letters to differentiate the decision variables clearly.

**建议中文翻译**

已定义符号中存在冲突和视觉相似，尤其是决策变量。例如 $x_{ijw}$ 与 $x_{jw}$ 表示不同概念，容易使读者混淆。强烈建议使用完全不同的字母清楚区分这些决策变量。

**英文回复**

We agree that the original notation could cause confusion. The decision variables have been renamed consistently throughout the system model, Table I, constraints, objective functions, and algorithm descriptions: $y_{jk}$ denotes server deployment, $z_{jw}$ denotes service provisioning, and $a_{ijw}$ denotes user-service-server association. The implementation entry $\mathrm{indiv}[j,w]$ is explicitly defined as the encoded counterpart of $z_{jw}$. This revision removes the former visual conflict among $x_{jk}$, $x_{jw}$, and $x_{ijw}$ and also eliminates the inconsistent use of $w_j$ for server $m_j$.

**中文回复**

我们同意原符号体系容易造成混淆。系统模型、Table I、约束、目标函数和算法描述中的决策变量已统一重命名：$y_{jk}$ 表示服务器部署，$z_{jw}$ 表示服务配置，$a_{ijw}$ 表示用户-服务-服务器关联。实现中的矩阵项 $\mathrm{indiv}[j,w]$ 也明确说明为 $z_{jw}$ 的编码对应项。这样消除了 $x_{jk}$、$x_{jw}$ 和 $x_{ijw}$ 之间的视觉冲突，同时修正了将服务器 $m_j$ 误写为 $w_j$ 的不一致。

**论文修改后原文**

**位置：** Section III-A and Section IV-B

> Equation (7) defines the server-deployment variable $y_{jk}$, service-provisioning variable $z_{jw}$, and user-service association variable $a_{ijw}$.

> A service-provisioning scheme is encoded by a binary matrix $\mathrm{indiv}\in\{0,1\}^{k\times|\mathcal{S}|}$. Each row corresponds to a deployed server and each column to a service type. The entry $\mathrm{indiv}[j,w]$ is the encoded counterpart of $z_{jw}$: it equals 1 when service $s_w$ is provisioned on server $m_j$, and 0 otherwise.

**修改后原文中文翻译**

公式 (7) 分别定义服务器部署变量 $y_{jk}$、服务配置变量 $z_{jw}$ 和用户-服务关联变量 $a_{ijw}$。

服务配置方案编码为二进制矩阵 $\mathrm{indiv}\in\{0,1\}^{k\times|\mathcal{S}|}$。每一行对应一台已部署服务器，每一列对应一种服务类型。矩阵项 $\mathrm{indiv}[j,w]$ 是 $z_{jw}$ 的编码对应项：当服务 $s_w$ 配置在服务器 $m_j$ 上时取 1，否则取 0。


**证据与数据**

| 决策含义 | 修改后变量 | 定义 |
|---|---|---|
| 服务器部署 | $y_{jk}$ | $m_j$ 是否部署在 $b_k$ |
| 服务配置 | $z_{jw}$ | $m_j$ 是否配置 $s_w$ |
| 用户关联 | $a_{ijw}$ | $u_i$ 是否由 $m_j$ 上的 $s_w$ 服务 |

---

### 意见 3：Rationale and potential optimality loss of the two-stage decomposition

**英文建议原文**

> The authors transform the highly intertwined server deployment and service provisioning problem into two relatively independent stages. While this decoupling effectively reduces computational complexity, it raises the question of whether this transformation leads to a loss of global optimality. The authors should add a discussion justifying this two-stage decomposition and, if possible, comment on or analyze the potential performance gap compared to a joint optimization approach.

**建议中文翻译**

作者将高度耦合的服务器部署与服务配置问题转化为两个相对独立的阶段。虽然这种解耦降低了计算复杂度，但也引出了是否损失全局最优性的问题。作者应说明两阶段分解的合理性，并在可能的情况下分析其相对联合优化方法的性能差距。

**英文回复**

Thank you for raising this important point. The revised manuscript explains that the decomposition follows the operational hierarchy of MEC planning. Server deployment is a relatively long-term infrastructure decision governed by budget, coverage, and geographic demand, whereas service instances are provisioned after physical server locations are known. Stage I passes the selected locations, user assignments, and deployment-related cost to Stage II, thereby preserving the principal cost-latency dependence while substantially reducing the combinatorial decision space.

We further conducted a response-only exact small-scale joint-optimization experiment. The instance contains 6 candidate stations, 3 deployed servers, 30 users, 4 service types, and a per-server service capacity of 2. All $\binom{6}{3}\times\left[\sum_{r=0}^{2}\binom{4}{r}\right]^3=26{,}620$ feasible joint server-service decisions were enumerated to construct an exact Pareto reference. Across seeds 42, 43, and 44, MOS²-PSP attained the same best normalized weighted quality as the exact joint reference in every run. The mean HV gap was 3.87%, the mean IGD was 0.0382, and exact enumeration required 5.18 times the MOS² runtime on average even at this reduced scale.

The near-identical balanced cost-delay quality and the steep growth of exhaustive search show that decomposition is not merely a computational convenience, but is necessary for tractable optimization at the larger MEC scales studied in the manuscript. MOS² preserves the decisive deployment-to-provisioning dependencies while matching the exact solver's best balanced solution in every tested seed, using only about one-fifth of its runtime and avoiding enumeration and storage of the full joint decision space.

**中文回复**

感谢审稿人提出这一关键问题。修改稿说明，两阶段分解遵循 MEC 规划的实际决策层级：服务器部署是受预算、覆盖和地理需求约束的长期基础设施决策，服务实例则在物理服务器位置确定后进行配置。Stage I 将已选位置、用户分配和部署相关成本传递给 Stage II，因此在显著缩小组合决策空间的同时保留主要的成本-时延联系。

我们还进行了仅用于回信佐证的小规模精确联合优化实验。实例包含 6 个候选基站、3 台部署服务器、30 个用户、4 类服务，每台服务器服务容量为 2。通过枚举全部 $\binom{6}{3}\times\left[\sum_{r=0}^{2}\binom{4}{r}\right]^3=26{,}620$ 个可行联合决策，构造精确 Pareto 参考。在种子 42、43 和 44 下，MOS²-PSP 每次都取得与精确联合参考相同的最佳归一化加权质量；平均 HV 差距为 3.87%，平均 IGD 为 0.0382，而精确枚举即使在该小规模下平均也需要 MOS² 的 5.18 倍运行时间。

近乎一致的成本-时延平衡质量与穷举搜索负担的陡增表明，两阶段分解并非单纯为了计算方便，而是使本文较大规模 MEC 配置可求解的必要设计。MOS² 在保留部署与服务配置关键依赖关系的同时，在全部测试种子下均取得与精确求解器相同的最佳平衡解，运行时间仅约为后者的五分之一，并避免枚举和存储完整联合决策空间。

**论文修改后原文**

**位置：** Section III-D, decomposition rationale

> The decomposition follows the operational hierarchy of MEC planning. Server deployment is a long-term infrastructure decision governed by budget, coverage, and geographic demand, whereas service instances are provisioned after the physical server locations are known. Stage 1 therefore resolves the spatial variables that determine deployment and transmission costs, and Stage 2 optimizes service instances and user associations on the selected infrastructure. Passing the selected locations, user assignments, and Stage-I cost to Stage 2 preserves the cost-latency dependence while substantially reducing the decision space of the service-provisioning search.

**修改后原文中文翻译**

该分解遵循 MEC 规划的实际决策层级。服务器部署是受预算、覆盖范围和地理需求约束的长期基础设施决策，而服务实例则在物理服务器位置确定后进行配置。因此，Stage 1 求解决定部署成本和传输成本的空间变量，Stage 2 在选定基础设施上优化服务实例和用户关联。将选定位置、用户分配和 Stage-I 成本传递至 Stage 2，可在大幅缩小服务配置搜索决策空间的同时保留成本-时延依赖关系。


**证据与数据**

证据图：`response_evidence/joint_exact_vs_mos2_seed42.png`。

| 种子 | HV 差距 | IGD | Best Q 差距 | Joint/MOS² 运行时间 |
|---|---|---|---|---|
| 42 | 6.45% | 0.0289 | 0.0000 | 4.99x |
| 43 | 4.18% | 0.0199 | 0.0000 | 5.15x |
| 44 | 0.98% | 0.0660 | 0.0000 | 5.40x |
| Mean | 3.87% | 0.0382 | 0.0000 | 5.18x |

---

### 意见 4：Constraint checking and handling in PSP

**英文建议原文**

> The PSP strategy was proposed for the service provisioning stage, the logic surrounding the constraint check step is somewhat vague and unclear. The authors need to adjust this part of the diagram and elaborate in the corresponding text on exactly how the constraints are verified and handled during the algorithm's execution (e.g., whether penalty functions or repair mechanisms are used).

**建议中文翻译**

PSP 用于服务配置阶段，但约束检查步骤周围的逻辑较为模糊。作者需要调整图中这一部分，并在正文中说明算法执行期间如何验证和处理约束，例如使用惩罚函数还是修复机制。

**英文回复**

Fig. 2, Algorithm 3, and the associated text now describe the complete feasibility procedure. After crossover and mutation, each decision entry is rounded to a binary value. For every server $m_j$, PSP checks whether $\sum_w z_{jw}\leq V_j$. If capacity is exceeded, selected service entries are randomly deactivated until feasibility is restored. Objective evaluation and non-dominated sorting are performed only after repair. PSP therefore enforces capacity through an explicit repair mechanism rather than a penalty function. The redesigned Evolutionary Optimization panel presents the same sequence and uses proper mathematical subscripts for the population and capacity variables.

**中文回复**

Fig. 2、Algorithm 3 及相应正文现已完整描述可行性处理流程。交叉和变异后，先将每个决策项二值化；随后对每台服务器 $m_j$ 检查 $\sum_w z_{jw}\leq V_j$。若容量超限，则随机关闭已选服务项，直到恢复可行。只有修复后的个体才进入目标评价和非支配排序。因此 PSP 使用的是显式修复机制，而不是惩罚函数。重绘后的 Evolutionary Optimization 面板按同一顺序展示流程，并使用规范的种群和容量数学下标。

**论文修改后原文**

**位置：** Section IV and Algorithm 3

> *Fig. 2. Overall architecture of MOS².*

> Given the fixed server locations, PSP constructs a hybrid initial population and applies NSGA-II to optimize provisioning cost and access delay. Crossover and mutation produce each offspring, whose entries are first rounded to binary values. For every server $m_j$, PSP then checks $\sum_w z_{jw}\leq V_j$. If the capacity is exceeded, selected service entries are randomly deactivated until feasibility is restored. Only capacity-feasible offspring are evaluated and passed to non-dominated sorting; thus, feasibility is enforced by repair rather than by a penalty function. The evolutionary process returns a set of provisioning schemes representing different cost-delay trade-offs.

> After crossover and mutation, every encoded entry is rounded to 0 or 1. If $\sum_w\mathrm{indiv}[j,w]>V_j$ for any server $m_j$, selected entries in that row are randomly set to 0 until the capacity constraint is satisfied. Objective evaluation and non-dominated sorting are then performed on the repaired feasible individual.

**修改后原文中文翻译**

图 2. MOS² 的总体架构。

在服务器位置固定后，PSP 构造混合初始种群，并应用 NSGA-II 优化服务配置成本和访问时延。交叉与变异产生子代后，首先将其各编码项舍入为二进制值。随后，PSP 对每台服务器 $m_j$ 检查 $\sum_w z_{jw}\leq V_j$。若容量超限，则随机停用已选服务项，直至恢复可行性。只有满足容量约束的子代才进入目标评估和非支配排序；因此，可行性通过修复而非惩罚函数来保证。进化过程最终返回一组表示不同成本-时延权衡的服务配置方案。

交叉和变异后，每个编码项都被舍入为 0 或 1。若任一服务器 $m_j$ 满足 $\sum_w\mathrm{indiv}[j,w]>V_j$，则随机将该行中的已选项置为 0，直至满足容量约束；随后才对修复后的可行个体进行目标评估和非支配排序。


**证据与数据**

证据图：`response_evidence/fig2_evolution_panel.png`（重绘的进化优化流程）。

---

### 意见 5：Readability of axes, labels, and ticks

**英文建议原文**

> The font sizes for the X-axis and Y-axis labels/ticks in all experimental figures are too small. Please enlarge them to ensure they are easily readable.

**建议中文翻译**

所有实验图中 X 轴和 Y 轴标签及刻度字号过小。请放大这些文字以确保易于阅读。

**英文回复**

We re-exported the experimental figures with consistent multi-panel dimensions, larger axis labels and tick labels, improved panel spacing, and concise captions. The Stage-I scale and convergence results, Stage-II scalar comparisons, hybrid-initialization illustration, Pareto fronts, and CLS sensitivity figure were all visually checked at the final IEEE column widths. Redundant shared legends and auxiliary annotations were removed where they reduced usable plotting area.

**中文回复**

我们重新导出了全部实验图，统一多子图尺寸，增大坐标轴标题和刻度文字，改善子图间距，并将图注压缩为简洁说明。Stage I 规模与收敛结果、Stage II 标量比较、混合初始化示意图、Pareto 前沿和 CLS 敏感性图均按最终 IEEE 栏宽进行了视觉检查；对于挤占绘图区的重复图例和辅助标注进行了精简。

**证据与数据**

代表性重导出图：`response_evidence/stage1_scale.png`、`response_evidence/stage2_fixed_users_dqn.png`。

---

### 意见 6：Typographical and language errors

**英文建议原文**

> There are several typos in this paper. A thorough proofreading is required. Some specific examples include: page 5: s2 , s3 and s5. -> s2 , s3, and s5; page 12: U the set of -> U is the set of.

**建议中文翻译**

论文中存在若干拼写或排版错误，需要全面校对。具体例子包括：第 5 页的 s2 , s3 and s5. 应改为 s2, s3, and s5；第 12 页的 U the set of 应改为 U is the set of。

**英文回复**

The manuscript has been proofread throughout. The two examples identified by the reviewer were corrected. We also corrected ordinal suffixes in the author affiliations, subject-verb agreement in the Introduction, the phrase 'hierarchy network architecture,' repeated introductory wording, inconsistent server symbols, punctuation in service lists, and grammatical issues in the system-model and algorithm descriptions. The marked and clean manuscripts were both compiled and visually inspected after proofreading.

**中文回复**

我们已对全文进行校对并修正审稿人指出的两处问题。此外，还修正了作者序号后缀、引言中的主谓一致、hierarchy network architecture 的词性错误、重复的引导语、服务器符号不一致、服务列表标点以及系统模型和算法描述中的语法问题。校对后，标记稿和无标记稿均重新编译并进行了视觉检查。

**论文修改后原文**

**位置：** Sections I and III, representative corrected passages

> In this paper, we consider a hierarchical network architecture comprising the cloud data center, edge servers, and mobile end users, as illustrated in Figure 1.

> At the user layer, the set of mobile users is denoted by $\mathcal{U}=\{u_i\}$, where $u_i$ represents the i-th user.

**修改后原文中文翻译**

本文考虑由云数据中心、边缘服务器和移动终端用户构成的分层网络架构，如图 1 所示。

在用户层，移动用户集合记为 $\mathcal{U}=\{u_i\}$，其中 $u_i$ 表示第 i 个用户。


**证据与数据**

| 原文 | 修改后 |
|---|---|
| s2 , s3 and s5 | s2, s3, and s5 |
| U the set of | U is the set of |
| 4rd / 5rd | 4th / 5th |
| hierarchy network architecture | hierarchical network architecture |

---

## 审稿人 2

### 意见 1：Initialization sensitivity of CLS

**英文建议原文**

> The proposed CLS algorithm is essentially a local-search-based heuristic for the K-median problem. However, the manuscript does not clearly explain the initialization sensitivity of the algorithm. Since the initial deployment set S in Algorithm 1 is randomly generated, different initializations may lead to significantly different local optima.

**建议中文翻译**

CLS 本质上是 K-median 问题的局部搜索启发式方法，但稿件没有清楚解释其初始化敏感性。由于 Algorithm 1 的初始部署集合 S 随机生成，不同初始化可能导致显著不同的局部最优解。

**英文回复**

We added a 50-run initialization-sensitivity study comparing Random, Density, Distance-Sum, marginal Greedy, and Diverse initializations. For each server/user configuration, the reported gap is the percentage difference between the final CLS cost and the best final cost observed under the same configuration.

With 130 users and 5, 10, 15, or 20 deployed servers, Random reached the same best final cost as the specialized initialization strategies in three of the four configurations and showed only a small 2.10% mean gap in the remaining case. More importantly, in the complementary 10-server/150-user stress case, Random obtained a 1.27% mean gap, whereas marginal Greedy deteriorated to 15.88%. Thus, handcrafted initialization provides no consistent optimization advantage, and a deterministic greedy preference can even steer CLS toward a markedly poorer local optimum. We therefore retain Random initialization because it matches the dedicated strategies in most tested settings while remaining more robust to initialization bias.

**中文回复**

我们增加了 50 次重复的初始化敏感性实验，比较 Random、Density、Distance-Sum、marginal Greedy 和 Diverse 五种初始化。对每个服务器/用户配置，gap 定义为最终 CLS 成本相对同一配置下观测到的最佳最终成本的百分比差。

在固定 130 个用户、服务器数为 5、10、15 和 20 时，Random 在四组中的三组都与专门设计的初始化策略达到相同最佳最终成本，在其余一组中也仅有 2.10% 的较小平均 gap。更重要的是，在补充的 10 台服务器/150 个用户压力情形中，Random 的平均 gap 为 1.27%，而 marginal Greedy 显著恶化至 15.88%。因此，手工设计的初始化并未带来稳定一致的优化优势，确定性的贪心偏好在特定情况下反而可能将 CLS 引向明显较差的局部最优。本文据此保留 Random 初始化：它在多数测试设置下与专门策略效果一致，同时对初始化偏置更稳健。

**论文修改后原文**

**位置：** Section V-B, Stage-I initialization-sensitivity analysis

> To examine the effect of the initial deployment set in Algorithm 1, we compare Random, Density, DistSum, marginal Greedy, and Diverse initialization over 50 runs. For each configuration, the reported gap is the percentage difference between the final cost and the best final cost observed under the same server/user setting. As shown in Fig. 9, the five strategies reach the same best final cost in nearly all fixed-130-user cases; the only nonzero entry is the 2.10% mean gap of Random at 10 servers. Under the 10-server/150-user setting, Random obtains a 1.27% mean gap, whereas marginal Greedy reaches 15.88%. These results show that CLS is generally stable across initializations and that random initialization avoids a systematic preference for a poorer local optimum.

> *Fig. 9. Initialization sensitivity of CLS under two server/user settings.*

**修改后原文中文翻译**

为考察 Algorithm 1 中初始部署集合的影响，我们在 50 次运行中比较 Random、Density、DistSum、marginal Greedy 和 Diverse 五种初始化。对于每种配置，所报告的 gap 是最终成本相对于同一服务器/用户设置下观测到的最佳最终成本的百分比差值。如 Fig. 9 所示，在固定 130 个用户的几乎所有情形中，五种策略均达到相同的最佳最终成本；唯一的非零项是 10 台服务器时 Random 的 2.10% 平均 gap。在 10 台服务器/150 个用户的设置下，Random 的平均 gap 为 1.27%，而 marginal Greedy 达到 15.88%。这些结果表明 CLS 对初始化总体稳定，且随机初始化可避免对较差局部最优形成系统性偏好。

图 9. 两种服务器/用户设置下 CLS 的初始化敏感性。


**证据与数据**

证据图：`response_evidence/cls_initialization_sensitivity.png`。

---

### 意见 2：Reliability-related QoS metrics

**英文建议原文**

> In Eq. (6), the QoS constraint only constrains the end-to-end latency upper bound $D_i$. However, packet loss, reliability, and service interruption probability are not considered. Since MEC systems for latency-sensitive applications usually require reliability guarantees, the manuscript is suggested to discuss the impact of ignoring reliability-related QoS metrics.

**建议中文翻译**

公式 (6) 的 QoS 约束只限制端到端时延上界 $D_i$，没有考虑丢包率、可靠性和服务中断概率。由于时延敏感型 MEC 应用通常需要可靠性保障，建议讨论忽略可靠性相关 QoS 指标的影响。

**英文回复**

Equation (6) retains end-to-end latency as the primary QoS requirement because the present optimization focuses on the cost-latency trade-off. The accompanying model discussion now clarifies that, for reliability-critical applications, latency compliance can be complemented by packet-loss, link-availability, and service-interruption constraints so that low-latency solutions are not selected when continuity is insufficient. The Conclusion also identifies reliability-aware QoS constraints as a direct extension of the framework.

**中文回复**

公式 (6) 保留端到端时延作为主要 QoS 要求，因为本文优化聚焦成本-时延权衡。模型部分现已说明，对于可靠性关键型应用，可在时延约束之外补充丢包率、链路可用性和服务中断约束，以避免选择连续性不足的低时延方案。结论中也将可靠性感知 QoS 约束列为框架的直接扩展方向。

**论文修改后原文**

**位置：** Section III-C and Conclusion

> Equation (6) provides latency-oriented QoS by requiring the end-to-end latency of a served request to remain below the user's tolerable bound $\widetilde{D_i}$. For reliability-critical applications, latency compliance can be complemented by packet-loss, link-availability, and service-interruption constraints, preventing a low-latency solution from being selected when service continuity is insufficient.

> Future work will extend the framework with reliability-aware QoS constraints for packet loss, link availability, and service interruption, together with learning-based demand prediction and multi-domain coordination.

**修改后原文中文翻译**

公式 (6) 通过要求已服务请求的端到端时延不超过用户可容忍上界 $\widetilde{D_i}$，提供面向时延的 QoS 保障。对于可靠性关键型应用，可在时延约束之外补充丢包率、链路可用性和服务中断约束，避免在服务连续性不足时选取低时延方案。

未来工作将通过面向丢包、链路可用性和服务中断的可靠性感知 QoS 约束扩展该框架，并进一步研究基于学习的需求预测和多域协同。


---

### 意见 3：PSP/NSGA-II hyperparameters

**英文建议原文**

> The proposed PSP algorithm relies on NSGA-II for multi-objective optimization. Nevertheless, the manuscript lacks a detailed explanation of several key hyperparameters, such as population size $N$, mutation probability, crossover probability, and maximum generation number $G$.

**建议中文翻译**

PSP 依赖 NSGA-II 进行多目标优化，但稿件缺少对关键超参数的详细说明，例如种群规模 $N$、变异概率、交叉概率和最大迭代代数 $G$。

**英文回复**

A complete parameter table has been added. The experiments use $N=50$, $G=200$, simulated binary crossover with $p_c=0.9,\ \eta_c=15$, polynomial mutation with $p_m=\frac{1}{k|\mathcal{S}|},\ \eta_m=20$, hybrid-score weights $\alpha=\beta=0.5$, per-server service capacity $V_j=4$, and anchor ratio $\rho=0.5$. The revised algorithm text also states the non-dominated rank and crowding-distance selection rule and the explicit capacity-repair procedure.

**中文回复**

修改稿增加了完整参数表。实验采用 $N=50$、$G=200$；模拟二进制交叉参数为 $p_c=0.9,\ \eta_c=15$；多项式变异参数为 $p_m=\frac{1}{k|\mathcal{S}|},\ \eta_m=20$；混合评分权重为 $\alpha=\beta=0.5$；单服务器服务容量为 $V_j=4$；锚点比例为 $\rho=0.5$。算法正文同时说明了非支配等级、拥挤距离选择规则以及显式容量修复流程。

**论文修改后原文**

**位置：** Section V-A and Table II

> The evolutionary settings used for PSP are summarized in Table II. The deterministic anchor size is defined proportionally as $\varpi_j=\lceil\rho V_j\rceil,\ \rho=0.5$. Hence, for the experimental capacity $V_j=4$, two slots retain the highest-scoring services and two slots preserve stochastic exploration. This equal allocation provides an interpretable exploitation-exploration balance and applies directly to servers with different capacities.

**修改后原文中文翻译**

PSP 使用的进化参数汇总于 Table II。确定性锚点大小按比例定义为 $\varpi_j=\lceil\rho V_j\rceil,\ \rho=0.5$。因此，在实验容量 $V_j=4$ 下，两个槽位保留评分最高的服务，另外两个槽位保留随机探索。该等比例分配形成可解释的利用-探索平衡，并可直接适用于不同容量的服务器。


**证据与数据**

| 参数 | 设置 |
|---|---|
| 种群规模 | $N=50$ |
| 最大迭代代数 | $G=200$ |
| SBX 交叉 | $p_c=0.9,\ \eta_c=15$ |
| 多项式变异 | $p_m=\frac{1}{k|\mathcal{S}|},\ \eta_m=20$ |
| 混合评分权重 | $\alpha=\beta=0.5$ |
| 服务容量 | $V_j=4$ |
| 锚点比例 | $\rho=0.5$ |

---

### 意见 4：Definition and normalization of Q

**英文建议原文**

> In Fig. 5 and Fig. 7, the performance metric $Q$ (normalized) is presented, but its exact normalization process and mathematical definition are not sufficiently described.

**建议中文翻译**

Fig. 5 和 Fig. 7 展示了 $Q$ (normalized)，但其确切归一化过程和数学定义描述不充分。

**英文回复**

The revised manuscript defines min-max normalization over the pooled solutions of all compared methods within each server/user configuration using $\widehat{C}=\frac{C-C_{\min}}{C_{\max}-C_{\min}}$ and $\widehat{D}=\frac{D-D_{\min}}{D_{\max}-D_{\min}}$. The scalar evaluation score is $Q=\lambda\widehat{C}+(1-\lambda)\widehat{D},\ \lambda=0.5$. Lower $Q$ denotes a better balanced cost-delay solution. The text further clarifies that $Q$ is applied only after multi-objective optimization for scalar comparison and is not an objective used to generate the Pareto population.

**中文回复**

修改稿明确规定：在每个服务器/用户配置内，将全部对比方法的解合并后进行 min-max 归一化，采用 $\widehat{C}=\frac{C-C_{\min}}{C_{\max}-C_{\min}}$ 和 $\widehat{D}=\frac{D-D_{\min}}{D_{\max}-D_{\min}}$；随后按 $Q=\lambda\widehat{C}+(1-\lambda)\widehat{D},\ \lambda=0.5$ 计算标量评价分数。$Q$ 越低表示成本与时延的平衡解越好。正文还说明 $Q$ 只在多目标优化之后用于标量比较，并不是生成 Pareto 种群的优化目标。

**论文修改后原文**

**位置：** Section V-A, normalization and scalar evaluation

> For each server/user configuration, cost and delay are normalized over the pooled solutions of the compared methods as

$$\widehat{C}=\frac{C-C_{\min}}{C_{\max}-C_{\min}}$$

$$\widehat{D}=\frac{D-D_{\min}}{D_{\max}-D_{\min}}$$

> and the scalar evaluation score is

$$Q=\lambda\widehat{C}+(1-\lambda)\widehat{D},\ \lambda=0.5$$

> Lower $Q$ indicates a better balanced solution. Hypervolume (HV) measures the dominated objective-space volume relative to the reference point $(1.1,1.1)$ and is maximized, whereas inverted generational distance (IGD) measures the mean distance from the common non-dominated reference front to a method's front and is minimized.

**修改后原文中文翻译**

对于每种服务器/用户配置，在所有对比方法的合并解集上对成本和时延进行如下归一化：

$$\widehat{C}=\frac{C-C_{\min}}{C_{\max}-C_{\min}}$$
成本的 min-max 归一化公式。

$$\widehat{D}=\frac{D-D_{\min}}{D_{\max}-D_{\min}}$$
时延的 min-max 归一化公式。

随后，标量评价分数定义为：

$$Q=\lambda\widehat{C}+(1-\lambda)\widehat{D},\ \lambda=0.5$$
成本与时延等权的标量评价分数。

$Q$ 越低表示成本与时延的平衡解越好。Hypervolume (HV) 衡量相对于参考点 $(1.1,1.1)$ 的支配目标空间体积，越大越好；Inverted Generational Distance (IGD) 衡量公共非支配参考前沿到某方法前沿的平均距离，越小越好。


---

### 意见 5：Rationale for selecting the deterministic anchor size

**英文建议原文**

> The proposed hybrid initialization mechanism in Algorithm 2 introduces the parameter $\varpi_j$ to control the deterministic anchor size. However, the rationale behind selecting $\varpi_j$ is unclear.

**建议中文翻译**

Algorithm 2 的混合初始化机制引入 $\varpi_j$ 控制确定性锚点大小，但稿件没有解释选择 $\varpi_j$ 的依据。

**英文回复**

The deterministic anchor is now defined proportionally as $\varpi_j=\lceil\rho V_j\rceil,\ \rho=0.5$. This rule assigns half of each server's capacity to the highest-ranked deterministic services and reserves the remaining half for stochastic selection from lower-ranked candidates. It therefore provides an interpretable exploitation-exploration balance and scales automatically with heterogeneous server capacities. In the reported experiments, $V_j=4$ gives $\varpi_j=2$; a capacity of 8 gives $\varpi_j=4$.

**中文回复**

确定性锚点现按比例定义为 $\varpi_j=\lceil\rho V_j\rceil,\ \rho=0.5$。该规则将每台服务器一半容量用于保留最高评分的确定性服务，另一半容量用于从较低排名候选中随机选择，从而形成可解释的利用-探索折中，并可随异构服务器容量自动缩放。本文实验中 $V_j=4$ 对应 $\varpi_j=2$；当容量为 8 时，对应 $\varpi_j=4$。

**论文修改后原文**

**位置：** Section IV-B and Section V-A

> PSP uses a hybrid initialization before the NSGA-II evolutionary loop. For each server, it constructs one ranking that favors low provisioning cost and another that favors services requested frequently by locally assigned users. The two rankings are fused by a hybrid score. High-scoring services form a deterministic anchor set, and the remaining capacity is filled by stochastic sampling from lower-ranked candidates. The resulting base configuration combines exploitation of high-quality candidates with exploration of alternative service combinations.

> Let $\alpha,\beta\in[0,1],\ \alpha+\beta=1$ balance provisioning cost and local demand. Let $\varpi_j$ ($0<\varpi_j\leq V_j$) denote the deterministic anchor size on edge server $m_j$. The hybrid score of candidate service $s_w$ is

$$H_j(s_w)=\alpha w_{\mathrm{cost},j}(s_w)+\beta w_{\mathrm{req},j}(s_w)$$

> where $w_{\mathrm{cost},j}$ and $w_{\mathrm{req},j}$ are descending rank scores derived from provisioning cost and the request frequency of users assigned to $m_j$, respectively. We set $\varpi_j=\lceil\rho V_j\rceil,\ \rho=0.5$, reserving half of the capacity for high-ranked deterministic services and half for stochastic selection from the remaining candidates.

**修改后原文中文翻译**

PSP 在 NSGA-II 进化循环之前采用混合初始化。对于每台服务器，分别构造偏向低配置成本的排序和偏向本地分配用户高频请求服务的排序，并通过混合评分融合。高评分服务构成确定性锚点集合，剩余容量则从低排名候选中随机采样填充。由此得到的基础配置同时利用高质量候选并探索替代服务组合。

令 $\alpha,\beta\in[0,1],\ \alpha+\beta=1$ 用于平衡配置成本与本地需求。令 $\varpi_j$（$0<\varpi_j\leq V_j$）表示边缘服务器 $m_j$ 上的确定性锚点大小。候选服务 $s_w$ 的混合评分为：

$$H_j(s_w)=\alpha w_{\mathrm{cost},j}(s_w)+\beta w_{\mathrm{req},j}(s_w)$$
候选服务的混合评分公式。

其中，$w_{\mathrm{cost},j}$ 和 $w_{\mathrm{req},j}$ 分别是由配置成本及分配到 $m_j$ 的用户请求频率得到的降序排名分数。本文设置 $\varpi_j=\lceil\rho V_j\rceil,\ \rho=0.5$，将一半容量用于高排名确定性服务，另一半用于从其余候选中随机选择。


**证据与数据**

证据图：`response_evidence/hybrid_initialization.png`。

---

### 意见 6：Generalization to different geographical distributions and larger MEC settings

**英文建议原文**

> In Section V, all experiments are conducted using a dataset collected within approximately a 9 km region around Xizhimen Subway Station in Beijing. However, the manuscript does not discuss the generalization capability of the proposed framework under different geographical distributions, heterogeneous traffic densities, or larger-scale MEC environments.

**建议中文翻译**

Section V 的实验均使用北京西直门地铁站周边约 9 km 区域的数据，但稿件没有讨论框架在不同地理分布、异构流量密度或更大规模 MEC 环境下的泛化能力。

**英文回复**

We conducted an additional complete two-stage experiment in a different real Beijing region using a pool of 2,215 deduplicated base-station coordinates. The evaluated instance contains 40 candidate base stations, 10 deployed servers, 130 users, and 8 service types. It changes the real base-station topology, doubles the candidate set relative to the primary experiment, and exhibits a more heterogeneous coverage-density structure.

In Stage I, CLS obtained a cost of 2,304.7670, compared with 6,150.5741 for the best non-CLS initialization-only result, a 62.53% reduction. In Stage II, the three-seed means for PSP were $\mathrm{HV}=1.0116$, $\mathrm{IGD}=0.0129$, and Best $Q=0.2678$. PSP achieved the best HV and IGD in each seed and the best mean values of all three metrics. The DQN baseline obtained mean Best $Q=0.5517$, whereas PSP obtained 0.2678, corresponding to a 51.45% reduction. These results demonstrate that the complete framework remains effective under a different real deployment topology, a larger candidate set, and heterogeneous spatial demand.

**中文回复**

我们使用 2,215 个去重后的北京真实基站坐标，在不同真实区域完成了一组从 Stage I 到 Stage II 的完整实验。测试实例包含 40 个候选基站、10 台部署服务器、130 个用户和 8 类服务。相对于主实验，该实例改变了真实基站拓扑，将候选基站数量扩大一倍，并呈现更异构的覆盖密度结构。

Stage I 中，CLS 的成本为 2,304.7670，最佳非 CLS 初始化结果为 6,150.5741，下降 62.53%。Stage II 的三种子平均结果中，PSP 的结果为 $\mathrm{HV}=1.0116$、$\mathrm{IGD}=0.0129$ 和 Best $Q=0.2678$；PSP 在每个种子下都取得最佳 HV 和 IGD，并取得三项指标的最佳均值。DQN 的平均结果为 Best $Q=0.5517$，PSP 为 0.2678，下降 51.45%。结果表明，完整框架在不同真实部署拓扑、更大的候选集合和异构空间需求下仍保持有效。

**证据与数据**

证据图：`response_evidence/real_region_topology.png`、`response_evidence/real_region_bestq.png`。

| Method | HV mean ± std | IGD mean ± std | Best Q mean ± std |
|---|---|---|---|
| NS-P | 0.9574 ± 0.0840 | 0.0498 ± 0.0328 | 0.2953 ± 0.0584 |
| GCP | 0.9799 ± 0.0691 | 0.0446 ± 0.0158 | 0.2800 ± 0.0447 |
| GDP | 0.9742 ± 0.0522 | 0.0408 ± 0.0234 | 0.2733 ± 0.0380 |
| PSP | 1.0116 ± 0.0579 | 0.0129 ± 0.0055 | 0.2678 ± 0.0503 |

| Method | Best Q mean | Std. |
|---|---|---|
| NS-P | 0.2953 | 0.0584 |
| GCP | 0.2800 | 0.0447 |
| GDP | 0.2733 | 0.0380 |
| PSP | 0.2678 | 0.0503 |
| DQN | 0.5517 | 0.1021 |

---

### 意见 7：Learning-based service-placement baseline

**英文建议原文**

> The comparison baselines in Stage II mainly include heuristic initialization strategies (GCP, GDP) and standard NSGA-II initialization. However, the manuscript does not compare against recent learning-based service placement methods, such as deep reinforcement learning or graph neural network based approaches.

**建议中文翻译**

Stage II 的基线主要包括 GCP、GDP 等启发式初始化和标准 NSGA-II 初始化，但没有与近期基于学习的服务放置方法比较，例如深度强化学习或图神经网络方法。

**英文回复**

We included a Deep Q-Network provisioning baseline. Stage-II provisioning is represented as a sequence of server-slot decisions in which the Q-network selects a service type or an empty action from demand, deployment-cost, current-selection, and cost-delay preference information. The resulting service matrix is evaluated by exactly the same cost and delay functions as the other methods. The implementation uses one hidden layer with 64 units and trains for 320 episodes for each preference weight in $\{0.1,0.3,0.5,0.7,0.9\}$; the learning rate is $7\times10^{-4}$, the discount factor is 0.98, the mini-batch size is 64, and the replay capacity is 12,000.

Across both primary Stage-II experiment series, PSP attained the lowest normalized $Q$ in every reported case. In the representative 10-server/130-user setting, PSP achieved $Q=0.3282$, compared with $Q=0.6125$ for DQN. Because DQN returns preference-conditioned deployment points rather than an evolutionary population, it is compared through the common scalar $Q$ measure and is not presented as a Pareto curve.

**中文回复**

我们引入了 Deep Q-Network 服务配置基线。Stage II 被表示为一系列服务器槽位决策，Q 网络依据需求、配置成本、当前已选服务和成本-时延偏好，为每个槽位选择一种服务或空动作。输出的服务配置矩阵采用与其他方法完全相同的成本和时延函数进行评价。实现使用一个含 64 个单元的隐藏层，并对每个偏好权重 $\{0.1,0.3,0.5,0.7,0.9\}$ 训练 320 个 episode；学习率为 $7\times10^{-4}$，折扣因子 0.98，mini-batch 为 64，经验回放容量为 12,000。

在两组主要 Stage II 实验中，PSP 在所有展示配置下都取得最低归一化 $Q$。以 10 台服务器/130 个用户为例，PSP 的结果为 $Q=0.3282$，DQN 为 $Q=0.6125$。由于 DQN 返回的是偏好条件化部署点，而不是进化算法种群，因此通过统一标量指标 $Q$ 进行比较，不将其画成 Pareto 曲线。

**论文修改后原文**

**位置：** Section V-A and Section V-B

> Deep Q-Network Provision (DQN): A Q-network sequentially selects a service or an empty action for each server slot using demand, deployment cost, and a cost-delay preference. The resulting deployment is evaluated by the same objectives as the other methods.

> We evaluate Stage II under two complementary configurations: (i) 10 deployed servers with 100, 130, 150, and 180 users, and (ii) 130 users with 5, 10, 15, and 20 deployed servers. Figures 5 and 7 report the minimum normalized score $Q$ obtained by each method. PSP achieves the lowest $Q$ in every reported case across both experimental series. Its hybrid initialization consistently improves upon random NS-P and the single-criterion GCP and GDP initializations; PSP also achieves lower $Q$ than DQN across all tested scales.

**修改后原文中文翻译**

Deep Q-Network Provision (DQN)：Q 网络根据需求、部署成本和成本-时延偏好，依次为每个服务器槽位选择一种服务或空动作；所得部署方案使用与其他方法相同的目标函数进行评价。

我们在两组互补配置下评估 Stage II：(i) 固定部署 10 台服务器，用户数为 100、130、150 和 180；(ii) 固定 130 个用户，部署服务器数为 5、10、15 和 20。Figures 5 和 7 给出各方法获得的最小归一化分数 $Q$。在两组实验的全部配置中，PSP 均取得最低 $Q$。其混合初始化始终优于随机 NS-P 以及单准则 GCP 和 GDP 初始化；在所有测试规模下，PSP 的 $Q$ 也均低于 DQN。


**证据与数据**

证据图：`response_evidence/stage2_fixed_servers_dqn.png`、`response_evidence/stage2_fixed_users_dqn.png`。

| 系列 | 服务器/用户 | PSP Q | DQN Q | PSP 相对降低 |
|---|---|---|---|---|
| Fixed 10 servers | 10/100 | 0.2686 | 0.5770 | 53.5% |
| Fixed 10 servers | 10/130 | 0.3282 | 0.6125 | 46.4% |
| Fixed 10 servers | 10/150 | 0.2749 | 0.4972 | 44.7% |
| Fixed 10 servers | 10/180 | 0.2774 | 0.4840 | 42.7% |
| Fixed 130 users | 5/130 | 0.1945 | 0.4052 | 52.0% |
| Fixed 130 users | 10/130 | 0.3282 | 0.6125 | 46.4% |
| Fixed 130 users | 15/130 | 0.2646 | 0.6077 | 56.5% |
| Fixed 130 users | 20/130 | 0.2864 | 0.7077 | 59.5% |

---

### 意见 8：Quantitative Pareto metrics

**英文建议原文**

> In Fig. 8, the Pareto fronts of different algorithms are illustrated, but no quantitative Pareto evaluation metrics (e.g., Hypervolume, IGD, Spacing, or Spread) are provided. Relying only on visual comparison may not be sufficiently rigorous.

**建议中文翻译**

Fig. 8 展示了不同算法的 Pareto 前沿，但没有提供 Hypervolume、IGD、Spacing 或 Spread 等定量 Pareto 指标。仅依靠视觉比较可能不够严谨。

**英文回复**

We added Hypervolume (HV) and Inverted Generational Distance (IGD), together with Best $Q$, for the representative 10-server/130-user configuration. HV measures dominated objective-space volume relative to the common reference point $(1.1,1.1)$ and is maximized; IGD measures the mean distance from the common non-dominated reference front to a method's front and is minimized. PSP achieved $\mathrm{HV}=0.9470$, $\mathrm{IGD}=0.0016$, and Best $Q=0.3282$, outperforming NS-P, GCP, and GDP on all three measures.

DQN provides a limited set of preference-conditioned solutions rather than an equal-cardinality population-based Pareto front. It is therefore evaluated through the common Best $Q$ measure, while HV and IGD are reported for the four population-based strategies.

**中文回复**

我们在代表性的 10 台服务器/130 个用户配置下增加了 Hypervolume (HV)、Inverted Generational Distance (IGD) 和 Best $Q$。HV 衡量相对于公共参考点 $(1.1,1.1)$ 的支配目标空间体积，越高越好；IGD 衡量公共非支配参考前沿到方法前沿的平均距离，越低越好。PSP 的结果为 $\mathrm{HV}=0.9470$、$\mathrm{IGD}=0.0016$ 和 Best $Q=0.3282$，三项均优于 NS-P、GCP 和 GDP。

DQN 输出有限个偏好条件化解，不是等规模的种群型 Pareto 前沿，因此使用统一 Best $Q$ 比较；HV 和 IGD 则用于四种种群型策略。

**论文修改后原文**

**位置：** Section V-A and Section V-B

> Lower $Q$ indicates a better balanced solution. Hypervolume (HV) measures the dominated objective-space volume relative to the reference point $(1.1,1.1)$ and is maximized, whereas inverted generational distance (IGD) measures the mean distance from the common non-dominated reference front to a method's front and is minimized.

> Figure 8 compares the cost-delay fronts generated by the four NSGA-II-based provisioning strategies with 130 users. Table III gives the numerical results for the 10-server setting. PSP attains the largest HV (0.9470), the smallest IGD (0.0016), and the smallest $Q$ (0.3282), confirming both broader objective-space coverage and closer convergence to the common reference front. DQN produces a limited set of scalarized solutions rather than a population-based Pareto front; it is therefore compared through $Q$ and is not included in the HV/IGD comparison.

**修改后原文中文翻译**

$Q$ 越低表示成本与时延的平衡解越好。Hypervolume (HV) 衡量相对于参考点 $(1.1,1.1)$ 的支配目标空间体积，越大越好；Inverted Generational Distance (IGD) 衡量公共非支配参考前沿到某方法前沿的平均距离，越小越好。

Figure 8 比较了 130 个用户下四种基于 NSGA-II 的服务配置策略所生成的成本-时延前沿。Table III 给出 10 台服务器设置下的数值结果。PSP 取得最大 HV (0.9470)、最小 IGD (0.0016) 和最小 $Q$ (0.3282)，表明其目标空间覆盖更广且更接近公共参考前沿。DQN 产生的是有限个标量化解，而不是种群型 Pareto 前沿，因此仅通过 $Q$ 比较，不纳入 HV/IGD 对比。


**证据与数据**

证据图：`response_evidence/pareto_10_130.png`。

| Method | HV | IGD | Best Q |
|---|---|---|---|
| NS-P | 0.8191 | 0.0785 | 0.3894 |
| GCP | 0.8596 | 0.0492 | 0.3550 |
| GDP | 0.8945 | 0.0326 | 0.3363 |
| PSP | 0.9470 | 0.0016 | 0.3282 |
| DQN | N/A | N/A | 0.6125 |

---

### 意见 9：Suggested references

**英文建议原文**

> The following works are closely related to MEC and server placement, and thus should not be overlooked. [1] Latency-Aware Service Deployment and Peer Offloading: A Long-Term Optimization Framework for Satellite Edge Computing. [2] Latency-Aware Task Offloading in Multi-Tier SAGIN With FSO-Enabled Mobile Edge Computing. [3] Novel Breakout Local Search for Offloading Tasks in Multi-Tiered Cloud Environment Considering Transmission and Processing. [4] Long-Term Max-Min Fairness Guarantee Mechanism for Integrated Multi-RAT and MEC Networks. [5] Dynamic Energy Cost Conservation for Distributed Edge Clouds Utilizing Online Mini-Batch Learning. [6] Mobile Edge Computing Offloading for Static Users in a Free Space Optical Communications-Enabled Satellite-Air-Ground Integrated Network.

**建议中文翻译**

审稿人列出六篇与 MEC、服务器放置、任务卸载、长期资源管理和在线学习相关的工作，并建议不要忽略。

**英文回复**

Following the Associate Editor's guidance, we evaluated the six works individually and incorporated four studies with direct methodological relevance: Feng et al. on latency-aware service deployment and peer offloading; Kato et al. on breakout local search for transmission- and processing-aware offloading; Jing et al. on long-term max-min fairness in integrated multi-RAT/MEC networks; and Jing et al. on online mini-batch learning for dynamic energy-cost conservation in distributed edge clouds. The Related Work section now explains how these studies complement the present focus on interpretable server planning and capacity-constrained multi-objective service provisioning.

The two remaining studies specifically address task offloading in FSO-enabled satellite-air-ground integrated networks. Their network architecture, optical-link assumptions, and decision variables differ substantially from the terrestrial MEC service-provisioning model considered here; consequently, they were not included solely to increase the citation count.

**中文回复**

根据副编辑的指导，我们逐篇评估六篇文献，并引入其中四篇与方法直接相关的研究：Feng 等人的时延感知服务部署与对等卸载；Kato 等人的传输/处理感知突破局部搜索卸载；Jing 等人的集成多 RAT/MEC 长期最大最小公平性；以及另一项 Jing 等人关于分布式边缘云动态能源成本的在线小批量学习。Related Work 现已说明这些研究如何从动态卸载、局部搜索、公平性和学习型能源管理角度补充本文的可解释服务器规划与容量受限多目标服务配置。

其余两篇专门研究 FSO 支持的空天地一体化网络任务卸载，其网络架构、光链路假设和决策变量与本文地面 MEC 服务配置模型差异较大，因此没有仅为增加引用数量而纳入。

**论文修改后原文**

**位置：** Section II-C, Related Work

> Optimization and learning methods also address complementary MEC resource-management objectives. Feng et al. [33] jointly optimized latency-aware service deployment and peer offloading over multiple timescales. Kato et al. [34] applied breakout local search to transmission- and processing-aware task offloading in a multi-tier cloud environment. Jing et al. [35] studied long-term max-min fairness for task splitting and resource allocation in integrated multi-RAT/MEC networks, while Jing et al. [36] used online mini-batch learning for dynamic energy-cost conservation in distributed edge clouds. These studies address dynamic offloading, fairness, or energy management; the present work focuses on interpretable server planning and capacity-constrained multi-objective service provisioning under a common cost-latency model.

**修改后原文中文翻译**

优化与学习方法也从互补角度研究 MEC 资源管理目标。Feng 等人 [33] 在多时间尺度下联合优化时延感知服务部署和对等卸载。Kato 等人 [34] 将突破局部搜索用于多层云环境中同时考虑传输和处理的任务卸载。Jing 等人 [35] 研究集成多 RAT/MEC 网络中任务拆分和资源分配的长期最大最小公平性；另一项 Jing 等人的工作 [36] 使用在线小批量学习实现分布式边缘云的动态能源成本节约。这些研究侧重动态卸载、公平性或能源管理；本文则聚焦共同成本-时延模型下可解释的服务器规划与容量受限多目标服务配置。


**证据与数据**

已引用建议文献 [1]、[3]、[4]、[5]；建议文献 [2]、[6] 因专门面向 FSO-SAGIN 任务卸载而未纳入。

---
