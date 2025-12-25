import matplotlib.pyplot as plt
import networkx as nx

# 创建图
G = nx.erdos_renyi_graph(10, 0.3)  # 随机生成一个包含10个节点的图

# 设置节点颜色
node_colors = ['yellow' if i == 4 else 'blue' for i in range(len(G.nodes))]  # 假设v是第4个节点

# 获取节点v的邻居
neighbors = list(G.neighbors(4))

# 绘制图
plt.figure(figsize=(10, 8))
pos = nx.spring_layout(G)  # 选择一种布局方式
nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=500, font_size=12, font_weight='bold', edge_color='gray')

# 绘制子图采样框
# 将v和其邻居的坐标提取出来
subgraph_nodes = [4] + neighbors
subgraph_pos = {node: pos[node] for node in subgraph_nodes}
subgraph_x = [subgraph_pos[node][0] for node in subgraph_nodes]
subgraph_y = [subgraph_pos[node][1] for node in subgraph_nodes]

# 使用阴影框突出显示子图区域
min_x, max_x = min(subgraph_x) - 0.1, max(subgraph_x) + 0.1
min_y, max_y = min(subgraph_y) - 0.1, max(subgraph_y) + 0.1
plt.gca().add_patch(plt.Rectangle((min_x, min_y), max_x - min_x, max_y - min_y, linewidth=2, edgecolor='red', facecolor='none'))

# 添加文本标注
plt.text(min_x + 0.05, min_y + 0.05, 'Subgraph Sampling', fontsize=12, color='red')

# 添加Transformer聚合模块示意
# 结构编码
plt.text(min_x + 0.3, min_y + 0.2, 'Structural Encoding', fontsize=12, color='blue')
# 边/关系编码
plt.text(min_x + 0.3, min_y + 0.1, 'Edge/Relation Encoding', fontsize=12, color='blue')
# 多头注意力
plt.text(min_x + 0.3, min_y + 0.0, 'Multi-Head Attention', fontsize=12, color='blue')
# 非线性变换
plt.text(min_x + 0.3, min_y - 0.1, 'Non-linear Transformation', fontsize=12, color='blue')

# 添加更新节点嵌入部分
plt.text(max_x + 0.2, max_y - 0.2, 'Updated Node Embeddings', fontsize=12, color='green')

# 绘制聚合后的最终节点嵌入
plt.scatter([max_x + 0.3], [max_y - 0.2], color='green', s=300, zorder=5)  # 更新后的节点嵌入

# 连接框之间的箭头
plt.arrow(min_x + 0.15, min_y + 0.2, 0.15, 0, head_width=0.05, head_length=0.1, fc='blue', ec='blue')
plt.arrow(min_x + 0.15, min_y + 0.1, 0.15, 0, head_width=0.05, head_length=0.1, fc='blue', ec='blue')
plt.arrow(min_x + 0.15, min_y + 0.0, 0.15, 0, head_width=0.05, head_length=0.1, fc='blue', ec='blue')
plt.arrow(min_x + 0.15, min_y - 0.1, 0.15, 0, head_width=0.05, head_length=0.1, fc='blue', ec='blue')

# 显示图形
plt.title('Transformer-based Node Aggregation')
plt.show()
