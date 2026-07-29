# IEEE IoT-J 审稿意见逐句翻译与修改指导

来源文件：
- 回信文本：`C:\Users\m1870\.codex\attachments\300cc5db-bd6f-4cc3-b394-a6abaae324c8\pasted-text.txt`
- 论文 PDF：本地保存的 MOS2 journal manuscript PDF（私人文件路径不写入公开仓库）
- 代码仓库：`D:\pythonProject`

## 1. 总体结论

这封信的正式结果是：当前稿件不能接收，编辑部建议你们根据意见大幅修改后作为新稿重投。它属于 Reject and Resubmit / 拒稿后鼓励重投，而不是普通 Major Revision。比较积极的信号是：副编辑认可会议扩展稿投期刊的合理性，Reviewer 1 总体正面，Reviewer 2 虽然意见多，但大多可以通过补实验、补指标、补参数解释和补讨论来回应。

我建议：优先按 IEEE IoT-J 重投准备，不建议马上转投。前提是你们愿意补实验，尤其是随机初始化稳定性、Pareto 数值指标、参数敏感性和泛化实验。

## 2. 编辑部与副编辑意见逐句翻译

### 2.1 主编/编辑部邮件

**04-Jun-2026**
译：2026 年 6 月 4 日。

**Paper: IoT-65990-2026 MOS2: A Two-Stage Multi-Objective Framework for Server Deployment and Service Provisioning in Mobile Edge Computing**
译：论文：IoT-65990-2026，MOS2：一种用于移动边缘计算中服务器部署与服务配置的两阶段多目标框架。

**Authors: Dr. Xiaofei Di, Liu, Haiming; Xu, Zecheng; Di, Xiaofei; Su, Jingxin; Che, Xiaoping**
译：作者：邸晓飞博士、刘海明、徐泽成、邸晓飞、苏静鑫、车小平。

**Editor: Dr. Wei Zhang**
译：编辑：张伟博士。

**Dear Dr. Di,**
译：尊敬的邸博士：

**I am writing to you concerning the above referenced manuscript which you submitted to the IEEE Internet of Things Journal.**
译：我写信是关于您提交到 IEEE Internet of Things Journal 的上述稿件。

**Based on the enclosed set of reviews, this manuscript is not acceptable for publication at this time.**
译：根据随信附上的审稿意见，该稿件目前不能被接受发表。

**Please consider the comments of the reviewers and resubmit your reworked manuscript as quickly as you feel is appropriate.**
译：请认真考虑审稿人的意见，并在您认为合适的时候尽快重新提交修改后的稿件。

**Your revised manuscript will receive another peer review as a new submission.**
译：您的修改稿将作为一篇新的投稿再次接受同行评审。

**Be sure to mention the original paper number in your cover letter and the Author Comments field.**
译：请务必在投稿信和作者备注栏中注明原始稿件编号。

**As you revise the manuscript, please use the Track Changes feature of MS Word, or a similar method, to show the changes you have made.**
译：修改稿件时，请使用 MS Word 的修订模式，或类似方法，显示您所做的改动。

**The changes must be underlined or highlighted in the resubmitted manuscript.**
译：重新提交的稿件中，修改内容必须以下划线或高亮方式标出。

**This will expedite the re-review process.**
译：这将加快再次评审的过程。

**Be sure to include a file with a detailed response to the reviews as well.**
译：同时请务必附上一份对审稿意见的详细回复文件。

**You can use the following link to start your resubmission without logging in:**
译：您可以使用以下链接在不登录的情况下开始重新提交。

**If you have any questions regarding the reviews, please contact the Associate Editor: Dr. Wei Zhang wei.zhang@singaporetech.edu.sg.**
译：如果您对审稿意见有任何问题，请联系副编辑张伟博士。

**Any other inquiries should be directed to the Administrative Assistant: Surbhi Tyagi surbhi.tyagi@ieee.org**
译：其他任何问题请联系行政助理 Surbhi Tyagi。

**Thank you for considering IEEE Internet of Things Journal for publication of your work.**
译：感谢您考虑将您的工作发表在 IEEE Internet of Things Journal。

**Sincerely, Dr. Bo Li (IoT-J EiC), Editor-in-Chief, IEEE Internet of Things Journal**
译：此致，Bo Li 博士，IEEE Internet of Things Journal 主编。

### 2.2 副编辑意见

**Associate Editor Comments, if any, are listed below:**
译：如有副编辑意见，列在下方。

**Associate Editor: Zhang, Wei**
译：副编辑：张伟。

**REQUIRED: Comments to Author:**
译：必要项：给作者的意见。

**This is an extended version of a conference paper.**
译：这是一篇会议论文的扩展版本。

**I can see there are quite some new contents for algorithm, experiments, etc., so a submission to a journal is reasonable to me.**
译：我可以看到其中在算法、实验等方面加入了相当多的新内容，因此我认为将其投稿到期刊是合理的。

**We got the comments from two reviewers, both offered detailed comments and overall recommendations, that are not positive enough for an acceptance.**
译：我们收到了两位审稿人的意见，他们都给出了详细评论和总体建议，但这些意见还不足以支持接收。

**I recommend a reject, but meanwhile suggest to offer the authors a chance to revise significantly and re-submit; however the authors can also consider submitting this work to other more suitable journals.**
译：我建议拒稿，但同时建议给作者一次大幅修改并重新提交的机会；不过作者也可以考虑将该工作投到其他更合适的期刊。

**Note that the authors shall feel free to evaluate each reference and only cite those with true and big enough relevance to this study.**
译：请注意，作者可以自行评估每一篇参考文献，只引用那些与本研究真正相关且相关性足够强的文献。

含义：副编辑没有否定论文方向。他明确承认扩展稿合理，但认为目前版本不够接收。最后一句是在提醒你们：Reviewer 2 推荐的文献不必全部机械加入，要有选择地引用。

## 3. Reviewer 1 逐句翻译与修改含义

**This paper investigates the server deployment and service provisioning problem in edge computing environments.**
译：本文研究边缘计算环境中的服务器部署与服务配置问题。

**The authors propose a two-stage framework to decouple this complex problem.**
译：作者提出了一个两阶段框架来解耦这一复杂问题。

**In the first stage, a Coverage-based Local Search (CLS) algorithm (inspired by the K-Median problem) is introduced to minimize deployment and transmission costs.**
译：在第一阶段，作者提出了一种受 K-Median 问题启发的基于覆盖的局部搜索算法 CLS，用于最小化部署成本和传输成本。

**In the second stage, a Pareto-oriented Service Provisioning (PSP) strategy based on NSGA-II is proposed to jointly optimize provisioning cost and service latency.**
译：在第二阶段，作者提出了一种基于 NSGA-II 的面向 Pareto 的服务配置策略 PSP，用于联合优化服务配置成本和服务时延。

**This paper is well-structured.**
译：本文结构良好。

**The proposed framework demonstrates practical value in balancing deployment expenses and user response delays, offering a promising solution for service providers.**
译：所提出的框架在平衡部署开销和用户响应时延方面体现出实际价值，为服务提供商提供了一个有前景的解决方案。

**However, before the manuscript can be recommended for publication, there are a few issues regarding figure clarity, mathematical notations, and methodological justification that need to be addressed.**
译：然而，在推荐发表之前，稿件还需要解决一些问题，主要涉及图示清晰度、数学符号以及方法合理性论证。

**1. Figure 1 in the paper is somewhat cluttered and difficult to follow.**
译：论文中的图 1 有些拥挤，读起来不够清楚。

**Specifically, the regions enclosed by the dashed lines are not clearly explained.**
译：具体来说，虚线圈出的区域没有被清楚解释。

**The authors should refine the visual layout of this figure and provide a more explicit description in both the text and the caption regarding what these dashed areas represent.**
译：作者应改进该图的视觉布局，并在正文和图注中更明确地说明这些虚线区域代表什么。

修改含义：重画 Fig. 1，不只是改 caption。黑色虚线大区域、红色虚线框、覆盖圆、服务器、服务块和用户颜色要分层解释。

**2. There are some conflicts and visual similarities in the defined notations, particularly concerning the decision variables.**
译：定义的符号中存在一些冲突和视觉相似之处，尤其是决策变量。

**For example, x_ijw and x_jw are used to denote different concepts, which may easily confuse the readers.**
译：例如，x_ijw 和 x_jw 被用来表示不同概念，这很容易使读者混淆。

**It is strongly recommended to use completely distinct variable letters to differentiate the decision variables clearly.**
译：强烈建议使用完全不同的变量字母，以清楚区分这些决策变量。

修改含义：不能只解释，要改符号体系。例如服务器部署用 `y_{jk}`，服务配置用 `z_{jw}`，用户分配用 `a_{ijw}` 或 `r_{ijw}`。

**3. The authors transform the highly intertwined server deployment and service provisioning problem into two relatively independent stages.**
译：作者将高度耦合的服务器部署和服务配置问题转化为两个相对独立的阶段。

**While this decoupling effectively reduces computational complexity, it raises the question of whether this transformation leads to a loss of global optimality.**
译：虽然这种解耦有效降低了计算复杂度，但也引出了一个问题：这种转化是否会导致全局最优性的损失。

**The authors should add a discussion justifying this two-stage decomposition and, if possible, comment on or analyze the potential performance gap compared to a joint optimization approach.**
译：作者应增加一段讨论来说明两阶段分解的合理性，并且如果可能的话，应评论或分析其相对于联合优化方法可能产生的性能差距。

修改含义：这是 Reviewer 1 最重要的技术意见。要补一节 “Rationale and optimality-gap discussion”，最好再补小规模联合优化对比实验。

**4. The PSP strategy was proposed for the service provisioning stage, the logic surrounding the constraint check step is somewhat vague and unclear.**
译：作者为服务配置阶段提出了 PSP 策略，但约束检查步骤周围的逻辑有些模糊、不清楚。

**The authors need to adjust this part of the diagram and elaborate in the corresponding text on exactly how the constraints are verified and handled during the algorithm's execution (e.g., whether penalty functions or repair mechanisms are used).**
译：作者需要调整图中的这一部分，并在相应正文中详细说明算法执行过程中约束是如何被验证和处理的，例如使用惩罚函数还是修复机制。

修改含义：你们代码里实际用了 repair 机制，不是 penalty。论文 Fig. 2 和 Algorithm 3 需要明确写：容量超限时随机或按规则删除服务，直到满足 `sum_w z_{jw} <= V_j`。

**5. The font sizes for the X-axis and Y-axis labels/ticks in all experimental figures are too small.**
译：所有实验图中 X 轴和 Y 轴标签/刻度的字号太小。

**Please enlarge them to ensure they are easily readable.**
译：请放大字号，以确保它们容易阅读。

修改含义：重导出所有实验图。建议单栏图宽 3.4 in 时 label 8-9 pt，tick 7-8 pt；双栏图宽 7 in 时 label 10-11 pt，tick 9-10 pt。

**There are several typos in this paper. A thorough proofreading is required.**
译：本文存在若干拼写或排版错误，需要进行全面校对。

**Some specific examples include: page 5: s2 , s3 and s5. -> s2 , s3, and s5**
译：具体例子包括：第 5 页，`s2 , s3 and s5.` 应改为 `s2, s3, and s5`。

**page 12: U the set of -> U is the set of**
译：第 12 页，`U the set of` 应改为 `U is the set of`。

修改含义：必须全文英文润色。PDF 第 1-2 页已经能看到重复句，例如 “To clarify this problem” 连续出现。

## 4. Reviewer 2 逐句翻译与修改含义

**This manuscript investigates the joint optimization problem of server deployment and service provisioning in mobile edge computing systems.**
译：本文研究移动边缘计算系统中服务器部署和服务配置的联合优化问题。

**To address the trade-off between deployment cost and service latency, the authors propose a two-stage multi-objective optimization framework termed MOS², where a Coverage-based Local Search algorithm is designed for server deployment and a Pareto-oriented Service Provisioning strategy based on NSGA-II is developed for service provisioning.**
译：为了解决部署成本和服务时延之间的权衡，作者提出了一个名为 MOS² 的两阶段多目标优化框架，其中为服务器部署设计了 CLS 算法，并为服务配置开发了基于 NSGA-II 的 PSP 策略。

**The topic is relevant and has potential practical significance for MEC resource management.**
译：该主题具有相关性，并且对 MEC 资源管理具有潜在实践意义。

**However, several technical and experimental issues still need to be further clarified and strengthened before the manuscript can be considered for publication.**
译：然而，在该稿件被考虑发表之前，仍有若干技术和实验问题需要进一步澄清和加强。

**1. The proposed CLS algorithm is essentially a local-search-based heuristic for the K-median problem.**
译：所提出的 CLS 算法本质上是 K-median 问题的一种基于局部搜索的启发式算法。

**However, the manuscript does not clearly explain the initialization sensitivity of the algorithm.**
译：然而，稿件没有清楚解释该算法对初始化的敏感性。

**Since the initial deployment set S in Algorithm 1 is randomly generated, different initializations may lead to significantly different local optima.**
译：由于 Algorithm 1 中初始部署集合 S 是随机生成的，不同初始化可能导致显著不同的局部最优解。

***1.要向他证明 我们在初始化时 随机或贪心或其他策略 生成的结果 是不是没区别 证明初始种群对策略的生成是不敏感的 证明random是好或与其他的没区别 /// 证明贪心或其他策略会不会陷入局部最优解等缺陷***

修改含义：需要做多随机种子稳定性实验。代码中 `coverage_local_search` 在 `main.py:218` 随机采样初始解，正好对应这个问题。

**2. In Eq. (6), the QoS constraint only constrains the end-to-end latency upper bound D_i.**
译：在公式 (6) 中，QoS 约束只限制了端到端时延上界。

**However, packet loss, reliability, and service interruption probability are not considered.**
译：然而，文中没有考虑丢包率、可靠性和服务中断概率。

***2.暂时列到future work***

**Since MEC systems for latency-sensitive applications usually require reliability guarantees, the manuscript is suggested to discuss the impact of ignoring reliability-related QoS metrics.**
译：由于面向时延敏感应用的 MEC 系统通常需要可靠性保障，建议论文讨论忽略可靠性相关 QoS 指标的影响。

修改含义：不一定要把可靠性建模进主问题，但至少要加 “Reliability-related QoS discussion”。如果能加一个扩展约束更好。

**3. The proposed PSP algorithm relies on NSGA-II for multi-objective optimization.**
译：所提出的 PSP 算法依赖 NSGA-II 进行多目标优化。

**Nevertheless, the manuscript lacks a detailed explanation of several key hyperparameters, such as population size N, mutation probability, crossover probability, and maximum generation number G.**
译：然而，稿件缺少对若干关键超参数的详细解释，例如种群规模 N、变异概率、交叉概率以及最大迭代代数 G。

修改含义：必须加超参数表。代码中 `nsga_service_deploy.py:1375` 使用 `pop_size=50`，`nsga_service_deploy.py:1389` 使用 `n_gen=200`，但论文没有清楚列出来。

**4. In Fig. 5 and Fig. 7, the performance metric Q (normalized) is presented, but its exact normalization process and mathematical definition are not sufficiently described.**
译：在图 5 和图 7 中展示了性能指标 `Q (normalized)`，但其确切的归一化过程和数学定义描述不充分。

修改含义：要新增公式。建议定义全局 min-max 归一化：`Q = lambda * C_norm + (1-lambda) * D_norm`，并说明 min/max 是在同一实验组所有算法上统一计算。

**5. The proposed hybrid initialization mechanism in Algorithm 2 introduces the parameter varpi_j to control the deterministic anchor size.**
译：Algorithm 2 中提出的混合初始化机制引入了参数 `varpi_j`，用于控制确定性锚点集合的大小。

**However, the rationale behind selecting varpi_j is unclear.**
译：然而，选择 `varpi_j` 的理由不清楚。

***5.测几下，然后说通过实验得出这个v的设置最好***

修改含义：代码中 `keep_top_n = 2` 位于 `nsga_service_deploy.py:817`，需要把它对应到论文的 `varpi_j`，并做敏感性实验，例如 `varpi_j = 1, 2, 3, V_j`。

**6. In Section V, all experiments are conducted using a dataset collected within approximately a 9 km region around Xizhimen Subway Station in Beijing.**
译：在第 V 节中，所有实验都使用了北京西直门地铁站周边约 9 km 区域内采集的数据集。

**However, the manuscript does not discuss the generalization capability of the proposed framework under different geographical distributions, heterogeneous traffic densities, or larger-scale MEC environments.**
译：然而，稿件没有讨论所提出框架在不同地理分布、异构流量密度或更大规模 MEC 环境下的泛化能力。

6.选择人口少 稀疏的位置做一下 比如昌平某区域 说明一下分布特点 比如选10server  用户分布的时候与原版做出差异化 比如有的密集有的稀疏 选出这一组 从stage1-2 都做一下 出一组结果 展示 看一下  如果效果非常好 就都做全了放进论文里 否则只放response里先试试

修改含义：要补泛化实验。代码仓库已有多组 xlsx：10/20/30/40 个候选基站、100-300 用户，可整理成规模泛化；还建议生成 synthetic clustered/uniform/skewed 分布。

**7. The comparison baselines in Stage II mainly include heuristic initialization strategies (GCP, GDP) and standard NSGA-II initialization.**
译：Stage II 的对比基线主要包括启发式初始化策略 GCP、GDP 和标准 NSGA-II 初始化。

**However, the manuscript does not compare against recent learning-based service placement methods, such as deep reinforcement learning or graph neural network based approaches.**
译：然而，稿件没有与近期基于学习的服务放置方法进行比较，例如深度强化学习或图神经网络方法。

***DQN再设计一下 做不成曲线***

修改含义：最好补一个 learning-based baseline。若时间不足，至少在 Related Work 和实验讨论中解释为什么未纳入，并补一个轻量 DRL/learning-inspired baseline 更稳。

**8. In Fig. 8, the Pareto fronts of different algorithms are illustrated, but no quantitative Pareto evaluation metrics (e.g., Hypervolume, IGD, Spacing, or Spread) are provided.**
译：在图 8 中展示了不同算法的 Pareto 前沿，但没有提供定量 Pareto 评价指标，例如 Hypervolume、IGD、Spacing 或 Spread。

**Relying only on visual comparison may not be sufficiently rigorous.**
译：仅依靠视觉比较可能不够严谨。

修改含义：必须加表格。代码 `compare_results.py:59` 已经计算 HV，可扩展 IGD、Spacing、Spread。现有 `.npz` 的一次读取结果显示 PSP 的 HV=0.9470、IGD=0.0016、bestQ=0.3282，优于 NS-P/GCP/GDP。

**9. The following works are closely related to MEC and server placement, and thus should not be overlooked.**
译：以下工作与 MEC 和服务器放置密切相关，因此不应被忽略。

**[1] Latency-Aware Service Deployment and Peer Offloading: A Long-Term Optimization Framework for Satellite Edge Computing.**
译：[1] 面向卫星边缘计算的时延感知服务部署与对等卸载：一种长期优化框架。

**[2] Latency-Aware Task Offloading in Multi-Tier SAGIN With FSO-Enabled Mobile Edge Computing.**
译：[2] 支持 FSO 的移动边缘计算多层 SAGIN 中的时延感知任务卸载。

**[3] Novel Breakout Local Search for Offloading Tasks in Multi-Tiered Cloud Environment Considering Transmission and Processing.**
译：[3] 考虑传输与处理的多层云环境任务卸载新型突破局部搜索方法。

**[4] Long-Term Max-Min Fairness Guarantee Mechanism for Integrated Multi-RAT and MEC Networks.**
译：[4] 集成多 RAT 与 MEC 网络中的长期最大最小公平性保障机制。

**[5] Dynamic Energy Cost Conservation for Distributed Edge Clouds Utilizing Online Mini-Batch Learning.**
译：[5] 利用在线小批量学习实现分布式边缘云的动态能源成本节约。

**[6] Mobile Edge Computing Offloading for Static Users in a Free Space Optical Communications-Enabled Satellite-Air-Ground Integrated Network.**
译：[6] 支持自由空间光通信的空天地一体化网络中面向静态用户的移动边缘计算卸载。

修改含义：逐篇判断相关性。最应考虑引用 [1]、[3]、[4]；[2] 和 [6] 更偏 SAGIN/FSO/卸载，若问题设置差异大，可以在回复中说明只简要讨论；[5] 偏能源成本和在线学习，也可作为相关工作补充。

## 5. 逐条修改建议和具体操作

### AE 意见

修改目标：让编辑看到这是认真重投，不是简单修小问题。

建议操作：
1. Cover letter 第一段写明：This is a substantially revised resubmission of IoT-65990-2026.
2. Response letter 开头列出主要改动：新增稳定性实验、Pareto 指标表、参数表、泛化实验、符号重构、图 1/2 重画、语言校对。
3. 对参考文献的回应要有选择：感谢审稿人，已补充真正相关文献；对不完全匹配的文献说明差异，而不是全部硬塞。

### R1-1 Fig. 1 不清楚

论文现状：PDF 第 2 页 Fig. 1 信息密度过高，黑色虚线、红色虚线、覆盖圈和服务块混在一起，caption 只有 “An illustrating example”。

建议修改：
1. 重画 Fig. 1 成两栏或两子图：`(a) server deployment and coverage regions`，`(b) service provisioning and routing example`。
2. 黑色虚线只表示 geographical service areas，红色虚线只表示 edge-server-hosted area，不要让两种虚线承担多个含义。
3. 图注写清：base station、deployed edge server、coverage region、service replica、unserved request、inter-server routing 分别是什么。
4. 正文删除重复的 “To clarify this problem”，把例子分成 deployment challenge 和 provisioning challenge 两段。

### R1-2 符号冲突

论文现状：Table I 和模型中同时使用 `x_{jk}`、`x_{jw}`、`x_{ijw}`，视觉相似；正文还出现 `wj` 这类应为 `m_j` 的错误。

建议修改：
1. 服务器部署变量改为 `y_{jk}`：`y_{jk}=1` 表示服务器 `m_j` 部署在基站 `b_k`。
2. 服务配置变量改为 `z_{jw}`：`z_{jw}=1` 表示服务 `s_w` 配置在服务器 `m_j`。
3. 用户服务分配变量改为 `a_{ijw}` 或 `r_{ijw}`：表示用户 `u_i` 是否由服务器 `m_j` 上的服务 `s_w` 服务。
4. Algorithm 2/3 中的 `indiv[j,w]` 保留为编码矩阵，但在算法前明确 `indiv[j,w]` is the encoded counterpart of `z_{jw}`。
5. 全文替换公式 (1)-(13)、Table I、问题 P1/P2/P3 的变量。

### R1-3 两阶段分解是否损失全局最优

论文现状：模型直接从 P1 拆到 P2/P3，但缺少全局最优性讨论。

建议修改：
1. 在 Section IV 前或 Section III-D 后新增小节：`Justification of the two-stage decomposition`。
2. 写清楚：完整联合问题包含服务器位置、服务配置、用户分配，变量空间约为 `C(|M|,k) * 2^{k|S|}`，直接联合优化不可扩展。
3. 给出“可接受损失”的论证：Stage I 固定的是强空间约束，主要决定覆盖和传输距离；Stage II 在固定位置上优化服务配置，目标是降低剩余成本和时延。
4. 最好补一个小规模联合优化 baseline：例如候选基站 5-8、服务 4、用户 30-50，用穷举或 MILP/NSGA-II 联合编码求近似联合解，对比 MOS2 的 cost/delay/HV gap。
5. 如果来不及做精确联合优化，至少做 “joint-coded NSGA-II small scale” 作为近似联合优化对照。

代码依据：
- Stage I 随机局部搜索在 `D:\pythonProject\main.py:218`。
- Stage II 编码在 `D:\pythonProject\LocalSearch\nsga_service_deploy.py:185`。

### R1-4 PSP 约束检查不清楚

论文现状：Fig. 2 中 Constraint Check/Repair 箭头表达不够清楚；Algorithm 3 写了 repair 但文字还不够具体。

代码依据：
- `ServiceRepair` 在 `D:\pythonProject\LocalSearch\nsga_service_deploy.py:360`。
- 它将个体 round 成 0/1，然后当某服务器服务数超过 `SERVICE_CAPACITY_PER_SERVER` 时随机删除 1，直到容量满足。

建议修改：
1. Fig. 2 把 “Constraint Check” 改成明确流程：Round -> Capacity Check -> Repair by dropping excess services -> Evaluate。
2. 文中写明不是 penalty function，而是 repair mechanism。
3. Algorithm 3 第 5/12 行补一句：if `sum_w z_{jw} > V_j`, iteratively set selected active entries to 0 until feasible。
4. 最好说明删除策略：当前代码是 random drop；论文若说 “randomly removes excess services”，代码和论文一致。若想更强，可以改为 “drop lowest hybrid-score services”，但这需要同步改代码。

### R1-5 图字号太小

建议修改：
1. 所有实验图统一 `plt.rcParams`：字体 Arial，label 10-12 pt，tick 9-10 pt，legend 8-10 pt。
2. Fig. 5/7 多子图建议导出为双栏宽度，单个子图避免过窄。
3. Fig. 8 的坐标轴文字在 PDF 渲染中出现嵌入字体乱码风险，重新导出并检查 PDF。

代码依据：
- Fig. 5/7/8 相关绘图在 `D:\pythonProject\LocalSearch\compare_results.py:104` 附近和 `nsga_service_deploy.py` 可视化部分。

### R2-1 CLS 初始化敏感性

论文现状：Algorithm 1 第一行随机选择初始部署集合，但没有多次运行统计。

建议实验：
1. 对每个数据集运行 CLS 30 次或 50 次，随机种子 `0-29`。
2. 记录 final transmission cost、total delay、iteration number、coverage ratio。
3. 表格报告 mean/std/min/max，图中可用 boxplot 或 error bar。
4. 文字说明：虽然初始解随机，但 CLS 在不同种子下方差较小；如果方差不小，则采用 multi-start CLS，选择最优结果。

代码改造方向：
- 把 `main.py:218` 的 `coverage_local_search` 包一层 `run_multistart_cls(seeds, ...)`。
- 当前 `main.py:610` 只固定 `random.seed(42)`，不足以回应审稿人。

### R2-2 QoS 可靠性指标

建议修改：
1. 在模型部分公式 (6) 后增加讨论：本文主要关注 latency-constrained QoS，packet loss/reliability/interruption probability 可通过约束扩展。
2. 可加入扩展约束，例如 `P_i^{loss} <= epsilon_i` 或 `R_i >= R_i^{min}`，但说明本稿实验聚焦时延和成本。
3. 在 Limitations 中承认：未来将结合链路可靠性、服务迁移失败和节点故障概率。
4. 如果要更主动，可以模拟可靠性：把链路可靠性设为距离或跳数的递减函数，报告 MOS2 在可靠性阈值下的可行率。

### R2-3 NSGA-II 超参数

论文现状：没有表格说明 `N, G, mutation probability, crossover probability`。

代码依据：
- `NSGA2` 在 `D:\pythonProject\LocalSearch\nsga_service_deploy.py:1221` 和 `:1374`。
- 当前批量实验使用 `pop_size=50`，`n_gen=200`，`seed=42`。

建议修改：
1. 新增 Table II 或 Table III：population size `N=50`，generations `G=200`，repair strategy，sampling modes，capacity `V_j=4`，`alpha=0.5`，`beta=0.5`，`varpi_j=2`。
2. 查明 pymoo NSGA2 默认 crossover/mutation 参数；若论文里写默认值，代码要显式设置，避免审稿人追问。
3. 做参数敏感性：`N={30,50,80}`，`G={100,200,300}`，mutation/crossover 可选 2-3 组，报告 PSP 稳定性。

### R2-4 Q(normalized) 定义

代码依据：
- `compare_results.py:14` 定义 min-max normalize。
- `compare_results.py:73-75` 计算 `weighted = a * F_norm[:,0] + b * F_norm[:,1]`。

建议论文新增公式：
1. `\hat{C} = (C-C_min)/(C_max-C_min)`。
2. `\hat{D} = (D-D_min)/(D_max-D_min)`。
3. `Q = \lambda \hat{C} + (1-\lambda)\hat{D}`。
4. 说明本文使用 `\lambda=0.5`，并在所有比较算法的结果上统一归一化。

### R2-5 varpi_j 选择依据

代码依据：
- `alpha=0.5, beta=0.5` 在 `D:\pythonProject\LocalSearch\nsga_service_deploy.py:752`。
- `keep_top_n = 2` 在 `D:\pythonProject\LocalSearch\nsga_service_deploy.py:817`。
- `SERVICE_CAPACITY_PER_SERVER = 4` 在 `D:\pythonProject\LocalSearch\compute_delay.py:17`。

建议修改：
1. 将 `varpi_j` 定义为 `ceil(rho V_j)`，例如 `rho=0.5`，所以 `V_j=4` 时 `varpi_j=2`。
2. 解释含义：一半容量保留确定性高质量服务，一半容量用于随机探索，平衡 exploitation/exploration。
3. 做敏感性实验：`rho={0.25,0.5,0.75,1.0}` 或 `varpi_j={1,2,3,4}`。

### R2-6 泛化能力

代码依据：
- 数据集中已有 `input_data_5_130_8_new.xlsx`、`input_data_10_100_8.xlsx`、`input_data_10_300_8.xlsx`、`input_data_20_300_8.xlsx` 等。
- `main.py:69` 当前硬编码读取 `input_data_10_130_8_new.xlsx`。

建议实验：
1. 规模泛化：候选基站 10/20/30/40，用户 100/130/180/300。
2. 密度泛化：uniform、clustered、hotspot-skewed 三类 synthetic user distribution。
3. 地理泛化：如果没有其他城市真实数据，使用西直门坐标范围内的合成分布，并明确这不是新城市实测。
4. 报告 CLS 成本、PSP Q、HV、运行时间随规模变化。

代码操作：
- 把 `main.py:69` 的硬编码数据文件改成函数参数或命令行参数。
- 不要再用 `main.py:148` 的 `N2=N2-1` 手工修正；要么给出统一规则，要么在实验配置表中固定 k。

### R2-7 学习型 baseline

建议优先级：
1. 最佳方案：实现一个轻量 DRL service placement baseline，例如状态为 server remaining capacity + request distribution，动作为为每个 server 选服务，reward 为 `-Q`。
2. 中等方案：实现 learning-guided heuristic，例如用请求频率、服务成本、距离收益训练一个简单 ranking model。
3. 最低方案：在 Related Work 中补足 DRL/GNN 服务放置文献，并解释本文聚焦启发式可解释多目标优化，学习型方法作为未来工作。但仅解释不如补 baseline 有说服力。

### R2-8 Pareto 定量指标

代码依据：
- `compare_results.py` 已经计算 HV，但论文没展示。
- 我只读现有 `.npz` 计算了一次，结果为：
  - NS-P：HV=0.8191，IGD=0.0785，Spacing=0.0137，bestQ=0.3894
  - GCP：HV=0.8596，IGD=0.0492，Spacing=0.0104，bestQ=0.3550
  - GDP：HV=0.8945，IGD=0.0326，Spacing=0.0060，bestQ=0.3363
  - PSP：HV=0.9470，IGD=0.0016，Spacing=0.0145，bestQ=0.3282

建议修改：
1. 新增 Pareto Metric Table，至少报告 HV、IGD、Spacing。
2. 对 Fig. 8 的每个 edge server 数量都计算一组指标，不只 10/130 这一组。
3. 如果加 Spread，注意 Spread 越低通常分布越均匀；HV 越高越好，IGD 越低越好。

### R2-9 参考文献

建议修改：
1. Related Work 拆成 Server Deployment、Service Provisioning、Learning-based MEC Placement/Offloading。
2. 对 [1]、[3]、[4] 优先补充并说明与本文差异。
3. 对 [2]、[6] 可作为 SAGIN/FSO 场景的相关扩展，不要强行说它们直接解决本文问题。
4. 对 [5] 可放在 energy-aware/online learning MEC 管理背景里。

## 6. 建议的修改顺序

第一轮先做不用跑大量实验的修改：
1. 重写符号体系和 Table I。
2. 重画 Fig. 1、Fig. 2。
3. 增加两阶段分解合理性讨论。
4. 增加 NSGA-II 参数表和 Q(normalized) 公式。
5. 增加约束 repair 机制说明。

第二轮补关键实验：
1. CLS 多随机种子稳定性实验。
2. PSP 参数敏感性：`N/G/varpi_j/alpha-beta`。
3. Pareto 指标表：HV、IGD、Spacing、Spread。
4. 多规模/多密度泛化实验。

第三轮增强说服力：
1. 小规模 joint optimization 对照，回应全局最优性损失。
2. 至少一个 learning-based 或 learning-guided baseline，回应 Reviewer 2 第 7 条。
3. 全文英文润色和图表重导出。

## 7. Response letter 写法建议

整体策略：不要辩解，采用 “感谢 + 已修改 + 新增内容位置 + 结果说明”。

示例：

**Response to R1-3:**
Thank you for pointing out the need to justify the two-stage decomposition. We have added a new subsection titled "Justification of the Two-Stage Decomposition" in Section III-D. In addition, we conducted a small-scale comparison against a joint optimization baseline to quantify the possible optimality gap. The results show that MOS2 achieves comparable cost-delay trade-offs while reducing the search complexity substantially.

**Response to R2-8:**
Thank you for this valuable suggestion. We agree that visual comparison alone is insufficient for evaluating Pareto fronts. We have added quantitative Pareto metrics, including Hypervolume, IGD, Spacing, and Spread, in Table X. The results consistently show that PSP obtains the highest Hypervolume and the lowest IGD under most configurations.

## 8. 我对当前稿件的判断

这篇稿件现在的主要问题不是方向不行，而是“证据链还不够闭合”。Reviewer 1 要的是解释清楚，Reviewer 2 要的是实验更硬。代码仓库里已经有不少可用基础，比如多组数据文件、NSGA-II 结果、HV 计算、repair 机制和混合初始化逻辑。下一步的重点不是推倒重做，而是把代码中的真实机制规范化、参数化、批量化，然后把实验结果以审稿人认可的形式写进论文。
