# Overleaf First-Round Text Patches

这些片段用于先处理编辑部和审稿人要求的文字性修改。由于当前本地没有 Overleaf 源码文件，下面内容按“插入位置 + LaTeX 片段”的形式组织。拿到 `.tex` 源文件后，应把这些片段精确合并进原文，而不是整段盲目粘贴。

## 0. 修改标记方式

编辑部要求修改稿必须用 Word Track Changes，或类似方式显示修改；在 LaTeX/Overleaf 中，建议使用显式修订标记。把下面宏加到 preamble，也就是 `\documentclass` 后、`\begin{document}` 前。

```tex
% Revision marking macros for resubmission.
\usepackage[normalem]{ulem}
\usepackage{xcolor}
\newcommand{\rev}[1]{\textcolor{blue}{\uline{#1}}}
\newcommand{\del}[1]{\textcolor{red}{\sout{#1}}}
```

使用方式：

```tex
\rev{This is newly added or substantially revised text.}
\del{This is deleted text.}
```

注意：不要把很长的公式、复杂表格、`\cite{}` 和跨段落内容全部塞进 `\rev{}`。长段落可以只对关键新增句子做 `\rev{}`，或者在段落前后用文字说明“blue underlined text indicates revisions”。

## 1. 符号体系重命名

对应意见：Reviewer 1 comment 2。

建议在 Table I 和模型公式中统一替换：

```tex
% Suggested notation revision
y_{jk}: binary variable indicating whether edge server m_j is deployed at base station b_k.
z_{jw}: binary variable indicating whether service s_w is provisioned on edge server m_j.
a_{ijw}: binary variable indicating whether user u_i is served by service s_w on edge server m_j.
```

可替换原文中关于决策变量的描述：

```tex
\rev{To avoid ambiguity among decision variables, we use three visually distinct binary variables throughout the model. Let $y_{jk}=1$ if edge server $m_j$ is deployed at base station $b_k$, and $y_{jk}=0$ otherwise. Let $z_{jw}=1$ if service $s_w$ is provisioned on edge server $m_j$, and $z_{jw}=0$ otherwise. Finally, let $a_{ijw}=1$ if user $u_i$ is served by service $s_w$ provisioned on edge server $m_j$, and $a_{ijw}=0$ otherwise.}
```

Table I 中建议替换为：

```tex
$y_{jk}$ & Indicator whether server $m_j$ is deployed at base station $b_k$. \\
$z_{jw}$ & Indicator whether server $m_j$ provisions service $s_w$. \\
$a_{ijw}$ & Indicator whether user $u_i$ is served by service $s_w$ on server $m_j$. \\
```

公式中相应替换：

```tex
C_d(m_j)= y_{jk} p_j.
```

```tex
C_p(m_j)= \sum_{s_w\in S} z_{jw} sc_w.
```

```tex
\sum_{s_w\in S} z_{jw} v_w \le V_j,\qquad
\sum_{s_w\in S} z_{jw} \varsigma_w \le \mu_j.
```

```tex
a_{ijw}\left(\frac{R_{iw}^{c}}{\mu_j}+\frac{R_{iw}^{t}}{r_{ij}}\beta_{iw}\right)\le \widehat{D}_i,\quad \forall u_i\in U.
```

```tex
y_{jk},z_{jw},a_{ijw}\in\{0,1\}.
```

## 2. 在 Problem Formulation 后新增：两阶段分解合理性

对应意见：Reviewer 1 comment 3。

插入位置：Section III-D `Problem Formulation` 末尾，进入 Section IV 前。

```tex
\subsection{Rationale for the Two-Stage Decomposition}

\rev{The original joint optimization problem couples three types of decisions: server deployment, service provisioning, and user-service association. Solving these decisions simultaneously is computationally prohibitive because the search space grows combinatorially with both the number of candidate base stations and the number of service types. For example, selecting $k$ deployed servers from $|\mathcal{M}|$ candidates already introduces $\binom{|\mathcal{M}|}{k}$ possible deployment patterns, while service provisioning over the selected servers further introduces $2^{k|S|}$ binary configurations before considering user association. Therefore, a direct joint search is difficult to scale to city-level MEC scenarios.}

\rev{The proposed decomposition follows the physical hierarchy of MEC resource planning. The first stage determines the spatial server layout, which mainly affects deployment cost, coverage, and distance-dependent transmission cost. Once server locations are fixed, the second stage optimizes service provisioning and user-perceived latency under the capacity constraints of the deployed servers. This design reduces the search space while preserving the dominant coupling between geographic coverage and service availability.}

\rev{We note that the two-stage decomposition may not always guarantee the same solution as a fully joint optimizer, since early deployment decisions constrain the feasible service-provisioning space. To address this concern, the revised manuscript discusses the possible optimality gap and evaluates the decomposition empirically through additional small-scale joint-optimization comparisons. These results help quantify the trade-off between solution quality and computational tractability.}
```

最后一句涉及新增实验。如果暂时还没跑 joint baseline，可先改为：

```tex
\rev{We note that the two-stage decomposition may not always guarantee the same solution as a fully joint optimizer, since early deployment decisions constrain the feasible service-provisioning space. In the revised discussion, we explicitly analyze this trade-off and identify the decomposition as a tractability-oriented design choice for large-scale MEC deployment.}
```

## 3. 在 Eq. (6) 后新增：QoS 可靠性讨论

对应意见：Reviewer 2 comment 2。

插入位置：QoS 延迟约束 Eq. (6) 解释之后。

```tex
\rev{The QoS constraint in Eq. (6) focuses on the latency-bounded requirement, which is the primary performance metric considered in this study. We acknowledge that latency-sensitive MEC applications may also require reliability-related QoS guarantees, such as packet loss probability, service interruption probability, and link availability. These metrics are not explicitly optimized in the current formulation because the available dataset mainly contains geographic base-station and user-request information rather than packet-level link traces.}

\rev{Nevertheless, the proposed framework can be extended to incorporate reliability constraints. For instance, one may impose $P_{ij}^{\mathrm{loss}}\le \epsilon_i$ or $R_{ij}\ge R_i^{\min}$ for the link between user $u_i$ and server $m_j$, or add a service interruption constraint $P_i^{\mathrm{int}}\le \eta_i$ for each user request. These constraints can be checked together with the latency and capacity constraints during service provisioning. We leave the joint modeling of latency, reliability, and interruption-aware service migration as future work.}
```

## 4. 替换 PSP 约束处理说明

对应意见：Reviewer 1 comment 4。

插入位置：Section IV-B `Pareto-based Service Provisioning - PSP` 中 Eq. (13) 后。

```tex
\rev{The capacity constraint in Eq. (13) is handled by a repair mechanism rather than by a penalty function. After crossover and mutation, each offspring is first rounded and reshaped into a binary service-provisioning matrix. Then, for every server $m_j$, the algorithm checks whether $\sum_{s_w\in S} z_{jw}>V_j$. If the capacity limit is violated, active service entries are iteratively removed until the constraint is satisfied. The repaired individual is then evaluated by the two objective functions. In this way, every individual entering the non-dominated sorting stage is capacity-feasible.}
```

如果代码保持当前随机删除策略，可加：

```tex
\rev{In our implementation, excess active entries are randomly removed during repair, which preserves population diversity while guaranteeing feasibility.}
```

如果后续把代码改成删除低 hybrid-score 服务，则改为：

```tex
\rev{In our implementation, excess active entries with lower hybrid scores are removed first, so the repair step preserves high-priority services while guaranteeing feasibility.}
```

## 5. 增加 Algorithm 2 中 `\varpi_j` 的依据

对应意见：Reviewer 2 comment 5。

插入位置：Algorithm 2 解释 `Top-N` 和随机填充之后。

```tex
\rev{The parameter $\varpi_j$ controls the deterministic anchor size on server $m_j$. In the experiments, we set $\varpi_j=\lceil \rho V_j\rceil$ with $\rho=0.5$, meaning that approximately half of the service capacity is reserved for high-score deterministic services and the remaining capacity is filled stochastically. This setting balances exploitation and exploration: the deterministic anchor preserves high-quality service candidates, whereas random filling maintains population diversity and reduces premature convergence to local optima.}
```

如果当前 `V_j=4`，可写：

```tex
\rev{Since each server can provision at most $V_j=4$ services in our setting, this gives $\varpi_j=2$.}
```

## 6. 增加 NSGA-II 超参数表

对应意见：Reviewer 2 comment 3。

插入位置：Section V-A `Basic Setting`，实验平台描述后。

```tex
\begin{table}[t]
\centering
\caption{\rev{Main parameters used in the PSP algorithm.}}
\label{tab:psp_parameters}
\begin{tabular}{l l}
\hline
\textbf{Parameter} & \textbf{Value} \\
\hline
Population size $N$ & 50 \\
Maximum generations $G$ & 200 \\
Service capacity per server $V_j$ & 4 \\
Hybrid weights $(\alpha,\beta)$ & $(0.5,0.5)$ \\
Anchor ratio $\rho$ & 0.5 \\
Anchor size $\varpi_j$ & $\lceil \rho V_j\rceil$ \\
Encoding & Binary service-provisioning matrix \\
Constraint handling & Repair mechanism \\
Selection & Non-dominated sorting with crowding distance \\
\hline
\end{tabular}
\end{table}
```

注意：crossover probability、mutation probability 需要和代码最终设置一致。当前代码使用 pymoo 默认 NSGA2 配置，建议后续在代码里显式设置，再把具体值补进表中。

## 7. 增加 `Q(normalized)` 定义

对应意见：Reviewer 2 comment 4。

插入位置：Section V-B Stage II 实验结果之前，Fig. 5/Fig. 7 解释之前。

```tex
\rev{To compare algorithms whose raw cost and delay have different numerical scales, we report a normalized weighted metric $Q$. For each experimental group, the raw provisioning cost $C$ and delay $D$ are normalized using the global minimum and maximum values among all compared algorithms:}

\begin{equation}
\widehat{C}=\frac{C-C_{\min}}{C_{\max}-C_{\min}},\qquad
\widehat{D}=\frac{D-D_{\min}}{D_{\max}-D_{\min}}.
\end{equation}

\rev{The normalized weighted metric is then computed as}

\begin{equation}
Q=\lambda \widehat{C}+(1-\lambda)\widehat{D},
\end{equation}

\rev{where $\lambda\in[0,1]$ controls the relative preference between cost and delay. Unless otherwise specified, we set $\lambda=0.5$ to give equal importance to both objectives. A smaller $Q$ indicates a better cost-delay trade-off.}
```

## 8. 增加 Pareto 定量指标描述

对应意见：Reviewer 2 comment 8。

插入位置：Fig. 8 解释之前或之后。

```tex
\rev{In addition to the visual Pareto fronts in Fig.~\ref{fig:pareto_front}, we further evaluate the obtained non-dominated solutions using quantitative Pareto metrics, including Hypervolume (HV), Inverted Generational Distance (IGD), and Spacing. HV measures the dominated objective-space volume with respect to a reference point, and a larger HV indicates better convergence and diversity. IGD measures the average distance from a reference Pareto set to the obtained solution set, and a smaller IGD indicates better approximation quality. Spacing reflects the uniformity of the obtained solutions along the Pareto front.}
```

表格模板：

```tex
\begin{table}[t]
\centering
\caption{\rev{Quantitative Pareto-front evaluation under the fixed-user setting.}}
\label{tab:pareto_metrics}
\begin{tabular}{l c c c c}
\hline
\textbf{Method} & \textbf{HV}$\uparrow$ & \textbf{IGD}$\downarrow$ & \textbf{Spacing}$\downarrow$ & \textbf{Best }$Q\downarrow$ \\
\hline
NS-P & TBD & TBD & TBD & TBD \\
GCP & TBD & TBD & TBD & TBD \\
GDP & TBD & TBD & TBD & TBD \\
PSP & TBD & TBD & TBD & TBD \\
\hline
\end{tabular}
\end{table}
```

已有一次本地读取 `.npz` 的参考结果：

```text
NS-P: HV=0.8191, IGD=0.0785, Spacing=0.0137, bestQ=0.3894
GCP:  HV=0.8596, IGD=0.0492, Spacing=0.0104, bestQ=0.3550
GDP:  HV=0.8945, IGD=0.0326, Spacing=0.0060, bestQ=0.3363
PSP:  HV=0.9470, IGD=0.0016, Spacing=0.0145, bestQ=0.3282
```

这些数值需要确认对应哪个实验配置后再正式写进论文。

## 9. Fig. 1 图注替换建议

对应意见：Reviewer 1 comment 1。

```tex
\caption{\rev{Illustrative example of server deployment and service provisioning in MEC. The dashed black regions denote geographical service areas associated with base stations. The red dashed regions indicate areas where edge servers are deployed. Colored blocks represent different service types, and users with the same color request the corresponding service. If a requested service is unavailable on the nearest edge server, the request is forwarded to another server that provisions the service, incurring additional transmission cost and latency.}}
```

正文中 Fig. 1 前后的解释建议替换为：

```tex
\rev{Fig.~1 illustrates the coupling between server deployment and service provisioning. The dashed black regions represent geographical service areas, while the red dashed regions highlight the areas where edge servers are deployed. Deploying more servers can improve coverage and reduce transmission distance, but it also increases deployment cost. Conversely, deploying too few servers may leave some users far from available edge resources.}

\rev{Service provisioning introduces another layer of decision making. Even if a user is covered by a nearby edge server, the requested service may not be provisioned locally because of limited server capacity. In that case, the request must be routed to another server hosting the service, increasing transmission cost and user-perceived latency. Therefore, server deployment and service provisioning must be jointly considered, while still requiring a scalable solution for practical MEC systems.}
```

## 10. Fig. 2 图注替换建议

对应意见：Reviewer 1 comment 4。

```tex
\caption{\rev{Overall architecture of MOS$^2$. Stage 1 determines the number and locations of deployed edge servers using budget and user-density constraints followed by CLS-based local search. Stage 2 performs PSP-based service provisioning. Each offspring generated by crossover and mutation is rounded, checked against the per-server capacity constraint, repaired if necessary, and then evaluated before non-dominated sorting and Pareto selection.}}
```

## 11. Related Work 中补 learning-based 讨论

对应意见：Reviewer 2 comment 7 and 9。

插入位置：Section II Related Work 末尾，或者新增小节 `Learning-based MEC Resource Management`。

```tex
\rev{Recent studies have also explored learning-based resource management for MEC, including deep reinforcement learning, graph-based learning, and online learning approaches. These methods are effective in dynamic environments where service demands, user mobility, or network states evolve over time. However, they often require extensive training data and may provide limited interpretability for deployment decisions. In contrast, our work focuses on a tractable and explainable two-stage optimization framework that explicitly models deployment cost, transmission cost, service provisioning cost, and latency. The learning-based methods are complementary to our framework and can be incorporated in future work as predictive modules for traffic demand or candidate ranking.}
```

需要配合补引用。Reviewer 2 给的文献建议中，优先考虑引用与本文最接近的服务器部署、服务部署、局部搜索和 MEC 资源管理工作。

## 12. Conclusion 增补局限性与未来工作

```tex
\rev{Although MOS$^2$ improves the scalability of joint server-service optimization, the two-stage decomposition may introduce a bounded performance gap compared with a fully joint optimizer in small-scale cases. In addition, this work mainly considers latency-bounded QoS, while reliability-related metrics such as packet loss and service interruption probability are not explicitly optimized. Future work will extend the framework by incorporating reliability-aware constraints, learning-based demand prediction, and joint optimization under dynamic user mobility.}
```

## 13. 第一轮修改优先级

建议先按以下顺序改 Overleaf：

1. 加修订标记宏。
2. 改符号体系：`x_{jk}, x_{jw}, x_{ijw}` 改为 `y_{jk}, z_{jw}, a_{ijw}`。
3. 加两阶段分解合理性小节。
4. 加 QoS 可靠性讨论。
5. 加 PSP repair 机制说明。
6. 加 `\varpi_j` 选择依据。
7. 加 NSGA-II 参数表。
8. 加 `Q(normalized)` 定义。
9. 加 Pareto 定量指标说明和表格模板。
10. 更新 Fig. 1/Fig. 2 caption 和正文解释。
