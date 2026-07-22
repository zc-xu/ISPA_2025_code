# 投稿正文过程性措辞审计

## 审计对象

- 源码：`manuscript/conference_101719_targeted_revision_clean.tex`
- 编译结果：`manuscript/conference_101719_targeted_revision_clean.pdf`
- 页数：14 页
- 方法：对最终 clean PDF 的实际可见文本进行全文提取与关键词扫描，并人工检查 Fig. 1、Fig. 2、Stage-II 两组柱图、Pareto 图、DQN 基线段和 Stage-II 结果段。

## 已消除的修改过程语言

### 1. Stage-II 图注

不采用：

> DQN is included as the fifth method.

中文含义：

> DQN 被加入为第五种方法。

原因：该句描述修稿动作，不能作为独立投稿论文的图注。

最终英文：

> Service-provisioning performance with 10 deployed servers and increasing user populations.

> Service-provisioning performance with 130 users and increasing numbers of deployed edge servers.

最终中文：

> 固定部署 10 台服务器、逐步增加用户数量时的服务配置性能。

> 固定 130 个用户、逐步增加部署服务器数量时的服务配置性能。

### 2. Stage-II 基线引入

最终英文：

> In Stage II, PSP is compared with four baseline strategies:

最终中文：

> 在 Stage II 中，PSP 与四种基线策略进行比较。

说明：正文以比较关系介绍方法，不使用“新增”“第五根柱”“为回应审稿人加入”等过程性表达。

### 3. DQN 方法说明

最终英文：

> Deep Q-Network Provision (DQN): A Q-network sequentially selects a service or an empty action for each server slot using demand, deployment cost, and a cost-delay preference. The resulting deployment is evaluated by the same objectives as the other methods.

最终中文：

> DQN 使用 Q 网络依次为每个服务器槽位选择一种服务或空动作，决策依据为需求、部署成本和成本-时延偏好；所得部署方案使用与其他方法相同的目标函数进行评价。

说明：正文不再展开奖励公式、网络层数、训练回合和经验池等实现参数，详细信息保留在回信与复现材料中。

### 4. Stage-II 结果段

最终英文：

> We evaluate Stage II under two complementary configurations: (i) 10 deployed servers with 100, 130, 150, and 180 users, and (ii) 130 users with 5, 10, 15, and 20 deployed servers. Figures 5 and 7 report the minimum normalized score Q obtained by each method. PSP achieves the lowest Q in every reported case across both experimental series. Its hybrid initialization consistently improves upon random NS-P and the single-criterion GCP and GDP initializations; PSP also achieves lower Q than DQN across all tested scales.

最终中文：

> Stage II 采用两组互补配置进行评价：固定 10 台服务器并改变用户数量，以及固定 130 个用户并改变服务器数量。图 5 和图 7 报告各方法取得的最小归一化 Q；PSP 在两组实验的每个图示场景中均取得最低 Q。其混合初始化优于随机 NS-P 以及单一准则 GCP 和 GDP；在全部测试规模下，PSP 的 Q 也均低于 DQN。

说明：该段只陈述实验设计和结果，不讨论“本轮新增了 DQN”或“为了回复意见而重跑”。

### 5. Fig. 1 图文一致性

最终英文：

> The blue bidirectional arrows represent cloud-edge communication, while the red dashed arrows indicate inter-region request forwarding.

> For example, the server in Area 4 provisions services s3 and s6; requests for the other service types require inter-area forwarding.

最终中文：

> 蓝色双向箭头表示云边通信，红色虚线箭头表示跨区域请求转发。

> 例如，Area 4 的服务器配置了服务 s3 和 s6；其他服务类型的请求需要跨区域转发。

说明：删除了与新图不一致的旧句 `s2, s3, and s5`，并删除了重复段落。

## 全文零命中检查

| 检索词 | 最终 clean PDF 命中数 |
|---|---:|
| `DQN is included` | 0 |
| `included as the fifth` | 0 |
| `fifth method` | 0 |
| `fifth baseline` | 0 |
| `was added` | 0 |
| `we added` | 0 |
| `we revised` | 0 |
| `in this revision` | 0 |
| `revised version` | 0 |
| `current version` | 0 |
| `modified version` | 0 |
| `reviewer` | 0 |
| `response to` | 0 |
| `as requested` | 0 |
| `This description matches` | 0 |
| `AI-generated` | 0 |
| `ChatGPT` | 0 |

## 图注检查

所有新增或改写图注均为一句话，只说明图的主题；实验现象、指标方向和方法比较均放在正文中。Stage-II 柱图不再显示冗余方法图例、柱顶数值或误差棒；Fig. 9 两个面板之间增加了间距，并统一去除了只在随机策略上可见的误差棒。正文和图注均未保留与这些排版调整有关的过程性说明。

## 最终机器与视觉核验

- 标记稿和净稿均由 Tectonic 编译成功，均为 14 页。
- 净稿中的 revision、rev、revcolor 和 showrevisions 命令命中数为 0。
- 净稿实际引用 16 个图件，缺失图件数为 0。
- Stage-I 多面板图页面尺寸为 511.38×135.35 pt，两组 Stage-II 图分别为 517.65×137.98 pt 和 517.65×136.94 pt，视觉占幅已经统一。
- Fig. 1 已按单栏宽度重新渲染检查，最外围导出黑框已消失，图中内容未被裁切。
- 独立 Evolutionary Optimization 面板的 PNG 尺寸为 513×253；PDF、SVG 和 PNG 的宽高比一致。
- 最新左右对照 PDF 已重新生成，并在页眉中指向完整审计文档 06_complete_original_vs_revised_bilingual_audit.md。
