# Response to the Editor and Reviewers

**Original manuscript ID:** IoT-65990-2026  
**Manuscript title:** *MOS²: A Two-Stage Multi-Objective Framework for Server Deployment and Service Provisioning in Mobile Edge Computing*

Dear Editor and Reviewers,

Thank you for the careful evaluation and constructive comments. We have revised the manuscript throughout and highlighted all textual changes in blue. The principal revisions include clearer system and algorithm figures, a unified notation system, a technical justification of the two-stage formulation, an explicit capacity-repair procedure, an initialization-sensitivity study for CLS, complete PSP/NSGA-II parameter settings, a mathematical definition of the normalized score, a learning-based DQN baseline, and quantitative Pareto metrics. We also conducted small-scale exact joint-optimization and real-region generalization experiments to support the responses below.

## Response to Reviewer 1

### Comment 1: Clarity of Fig. 1 and the dashed regions

**Response:** Thank you for identifying the ambiguity in Fig. 1. We revised the figure and its accompanying explanation so that each visual element has a unique meaning. The solid black contours partition the topology into interconnected service regions; the black dashed circles represent the coverage areas of individual base stations; the red dotted circles identify base stations equipped with edge servers; the blue bidirectional arrows represent cloud-edge communication; and the red dashed arrows indicate inter-region request forwarding. User colors correspond directly to the colors of the requested service types. The service blocks beside each edge server identify its instantiated services, and the question-mark slot in Area 3 represents the remaining service-provisioning decision under limited capacity. The Area 4 example is also aligned with the figure and identifies its provisioned services as s3 and s6. The caption is kept concise, while the full explanation is provided in the main text.

### Comment 2: Conflicting decision-variable notation

**Response:** We agree that the original use of visually similar variables could cause confusion. The notation has been revised consistently throughout the system model, Table I, constraints, and subsequent formulations:

- y_jk: server m_j is deployed at base station b_k;
- z_jw: service s_w is provisioned on server m_j;
- a_ijw: user u_i is served by service s_w on server m_j.

The binary matrix entry indiv[j,w] used in the PSP implementation is now explicitly identified as the encoded counterpart of z_jw. This removes the former visual conflict among x_jk, x_jw, and x_ijw.

### Comment 3: Rationale and potential optimality loss of the two-stage decomposition

**Response:** The manuscript now explains that the decomposition follows the operational hierarchy of MEC planning. Server deployment is a relatively long-term infrastructure decision governed by budget, coverage, and geographic demand. Service provisioning is subsequently optimized on the selected infrastructure. Stage I passes the selected locations, user assignments, and deployment-related cost to Stage II, thereby preserving the principal cost-latency dependence while reducing the joint combinatorial decision space.

We also conducted an exact small-scale joint-optimization comparison. The instance contains 6 candidate stations, 3 deployed servers, 30 users, 4 service types, and a per-server service capacity of 2. All C(6,3) x [sum from r=0 to 2 of C(4,r)]^3 = 26,620 feasible joint server-service decisions were enumerated to construct an exact Pareto reference. Across random seeds 42, 43, and 44, MOS²-PSP attained the same best normalized weighted quality as the exact joint reference in every run. The mean HV difference was 3.87%, the mean IGD was 0.0382, and exact enumeration required 5.18 times the runtime of MOS² on average even at this reduced scale. These results show that the decomposition retains high-quality cost-delay trade-offs while avoiding the rapidly expanding joint search space encountered in practical MEC instances.

### Comment 4: Constraint checking and handling in PSP

**Response:** Fig. 2, Algorithm 3, and the associated text describe the complete feasibility procedure. After crossover and mutation, every decision entry is rounded to a binary value. For each server m_j, PSP checks whether sum_w z_jw is no greater than V_j. If this capacity is exceeded, selected service entries are randomly deactivated until the constraint is satisfied. Objective evaluation and non-dominated sorting are applied only after repair. PSP therefore uses an explicit repair mechanism rather than a penalty function. The Evolutionary Optimization panel follows this sequence explicitly and uses mathematical subscripts for the population and capacity variables.

### Comment 5: Small labels and ticks in the experimental figures

**Response:** We revised the experimental presentation using consistent multi-panel dimensions, typography, axis labels, and concise captions. The two CLS initialization panels are combined into a compact one-column figure with additional separation between the panels. The Stage-II scalar comparisons use five consistently formatted bars for NS-P, PSP, GCP, GDP, and DQN; redundant shared legends and auxiliary annotations were removed to improve legibility. The four original Pareto datasets are retained in a full-width four-panel layout.

### Comment 6: Typographical and language errors

**Response:** The manuscript has been proofread throughout. In particular, punctuation in service lists has been corrected, the sentence defining the user set has been completed, ordinal suffixes in the author affiliations have been corrected, repeated introductory wording has been removed, variable names have been made consistent, and grammatical errors in the system-model and algorithm descriptions have been corrected.

## Response to Reviewer 2

### Comment 1: Initialization sensitivity of CLS

**Response:** We added a 50-run initialization-sensitivity study comparing Random, Density, Distance-Sum, marginal Greedy, and Diverse initializations. For each server/user configuration, the reported gap is the percentage difference between the final CLS cost and the best final cost observed for that configuration. With 130 users and 5, 10, 15, or 20 deployed servers, all five initializers reached the same best final cost except Random at 10 servers, whose mean gap was 2.10%. In the separate 10-server/150-user case, Random obtained a 1.27% mean gap, whereas marginal Greedy obtained 15.88%. The results indicate that CLS is generally stable across the tested initializations and that random initialization avoids imposing a systematic preference that can lead to a poorer local optimum.

### Comment 2: Reliability-related QoS metrics

**Response:** Equation (6) retains the end-to-end latency requirement as the primary QoS constraint because the present optimization focuses on the cost-latency trade-off. The accompanying text now explains that, for reliability-critical applications, latency compliance can be complemented by packet-loss, link-availability, and service-interruption constraints so that a low-latency solution is not selected when service continuity is insufficient. Reliability-aware QoS extensions are also identified as a future research direction.

### Comment 3: PSP/NSGA-II hyperparameters

**Response:** A complete parameter table has been added. The experiments use a population size of N=50, a maximum of G=200 generations, simulated binary crossover with p_c=0.9 and eta_c=15, polynomial mutation with p_m=1/(k|S|) and eta_m=20, hybrid-score weights alpha=beta=0.5, service capacity V_j=4, and anchor ratio rho=0.5.

### Comment 4: Definition and normalization of Q

**Response:** The manuscript now defines the normalization over the pooled solutions of all compared methods for each server/user configuration as C_hat=(C-C_min)/(C_max-C_min) and D_hat=(D-D_min)/(D_max-D_min), followed by Q=lambda C_hat+(1-lambda)D_hat, with lambda=0.5.

Lower Q denotes a better balanced cost-delay solution. The text also clarifies that Q is applied after multi-objective optimization for scalar comparison and is not an objective used to generate the Pareto population.

### Comment 5: Rationale for selecting varpi_j

**Response:** The deterministic anchor size is now defined proportionally as varpi_j=ceil(rho V_j), with rho=0.5.

This assigns half of each server's capacity to the highest-ranked deterministic services and reserves the remaining half for stochastic selection from lower-ranked candidates. The rule gives a direct exploitation-exploration interpretation and scales with heterogeneous capacities. In the reported experiments, V_j=4, so varpi_j=2; for a capacity of 8, the same rule gives varpi_j=4.

### Comment 6: Generalization to different geographical distributions and larger MEC settings

**Response:** We conducted a complete two-stage experiment in a different real Beijing region using a pool of 2,215 deduplicated base-station coordinates. The test instance contains 40 candidate base stations, 10 deployed servers, 130 users, and 8 service types. Relative to the original setting, this instance changes the geographic topology, doubles the number of candidate stations, and increases the heterogeneity of the coverage-density distribution.

In Stage I, CLS obtained a cost of 2,304.7670, whereas the best non-CLS result was 6,150.5741, corresponding to a 62.53% reduction. In Stage II, three independent seeds produced the following mean results:

| Method | HV (higher is better) | IGD (lower is better) | Best Q (lower is better) |
|---|---:|---:|---:|
| NS-P | 0.9574 | 0.0498 | 0.2953 |
| GCP | 0.9799 | 0.0446 | 0.2800 |
| GDP | 0.9742 | 0.0408 | 0.2733 |
| PSP | **1.0116** | **0.0129** | **0.2678** |

PSP achieved the best HV and IGD in each of the three seeds and the best mean value for all three metrics. The DQN baseline obtained a mean Best Q of 0.5517, while PSP obtained 0.2678, a reduction of 51.45%. The complete framework therefore remains effective under a different real base-station topology, a larger candidate set, and a more heterogeneous spatial-density structure.

### Comment 7: Learning-based service-placement baseline

**Response:** We added a Deep Q-Network provisioning baseline. Stage-II provisioning is represented as a sequence of server-slot decisions. The state contains the current server and slot, already selected services, local and global request frequencies, normalized service costs, and a cost-delay preference weight. An action selects one of eight service types or leaves the slot empty. The reward combines normalized request gain and service cost and includes a terminal cost-delay quality term and a penalty for globally missing service types. A one-hidden-layer Q-network with 64 units is trained for 320 episodes for each preference weight in {0.1, 0.3, 0.5, 0.7, 0.9}. The learning rate is 7 x 10^-4, the discount factor is 0.98, the mini-batch size is 64, the replay capacity is 12,000, the target network is synchronized every 20 episodes, and the exploration rate decays from 1.0 to 0.05. Its output is evaluated by the same cost and delay functions used for all other methods.

Across both primary Stage-II experiment series, PSP attained the lowest normalized Q in every reported case. For the representative 10-server/130-user case, PSP achieved Q=0.3282, compared with Q=0.6125 for DQN.

### Comment 8: Quantitative Pareto metrics

**Response:** We added Hypervolume (HV) and Inverted Generational Distance (IGD), together with Best Q, for the representative 10-server/130-user setting. HV is maximized and IGD is minimized. The results are:

| Method | HV | IGD | Best Q |
|---|---:|---:|---:|
| NS-P | 0.8191 | 0.0785 | 0.3894 |
| GCP | 0.8596 | 0.0492 | 0.3550 |
| GDP | 0.8945 | 0.0326 | 0.3363 |
| PSP | **0.9470** | **0.0016** | **0.3282** |
| DQN | -- | -- | 0.6125 |

DQN produces a limited set of scalarized solutions rather than a population-based Pareto front. It is therefore compared through the common scalar quality measure Q and is not included in the HV/IGD comparison.

### Comment 9: Suggested references

**Response:** We evaluated the six suggested works individually, following the Associate Editor's guidance to retain references with direct relevance to the present problem. We added and discussed the following four studies:

1. C. Feng, M. Yang, Z. Jing, T. Q. S. Quek, and M. Mei, “Latency-Aware Service Deployment and Peer Offloading: A Long-Term Optimization Framework for Satellite Edge Computing,” *IEEE Internet of Things Journal*, vol. 13, no. 1, pp. 405-417, 2026.
2. M. Kato, T. K. Rodrigues, and S. Verma, “Novel Breakout Local Search for Offloading Tasks in Multi-Tiered Cloud Environment Considering Transmission and Processing,” in *Proc. 2025 9th IEEE International Conference on Network Intelligence and Digital Content (IC-NIDC)*, 2025, pp. 269-274.
3. Z. Jing, Q. Yang, M. Qin, J. Li, and K. S. Kwak, “Long-Term Max-Min Fairness Guarantee Mechanism for Integrated Multi-RAT and MEC Networks,” *IEEE Transactions on Vehicular Technology*, vol. 70, no. 3, pp. 2478-2492, 2021.
4. Z. Jing, X. Wang, Q. Yang, M. Mei, and Y. Wu, “Dynamic Energy Cost Conservation for Distributed Edge Clouds Utilizing Online Mini-Batch Learning,” in *Proc. IEEE PIMRC*, 2023, pp. 1-6.

These works respectively contribute service-deployment/offloading co-optimization, local-search-based task offloading, long-term MEC resource fairness, and learning-based energy management, and therefore provide useful methodological context for the present framework. The two remaining suggested studies focus specifically on FSO-enabled SAGIN task offloading. Because their network architecture, link model, and decision variables differ substantially from the capacity-constrained terrestrial MEC service-provisioning problem considered here, they were not included in the revised related-work discussion.

We appreciate the reviewers' comments, which have helped improve the clarity, reproducibility, and experimental support of the manuscript.

Sincerely,  
The Authors
