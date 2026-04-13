# 导入所需库
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# 从CSV文件中读取数据
try:
    df = pd.read_csv("D:/NDM/customer_data.csv", encoding='gbk')
except UnicodeDecodeError:
    try:
        df = pd.read_csv("D:/NDM/customer_data.csv", encoding='gb2312')
    except UnicodeDecodeError:
        df = pd.read_csv("D:/NDM/customer_data.csv", encoding='latin1')

# 删除'id'列
df = df.drop(columns=['ID'], axis=1)

# 拆分数据集
X = df[['年龄', '收入', '信用卡', '首次购买', '所在地区']]
y = df['购买产品']

clf = DecisionTreeClassifier(max_depth=10, random_state=42)
clf.fit(X, y)

print(f"树的实际深度: {clf.tree_.max_depth}")
print(f"叶子节点数: {clf.tree_.n_leaves}")
print(f"总节点数: {clf.tree_.node_count}")

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'STSong']
plt.rcParams['axes.unicode_minus'] = False

# 获取决策树信息
tree = clf.tree_
feature_names = X.columns.tolist()


# 先计算每个节点下的叶子节点数量
def count_leaves(node_id):
    """计算节点下的叶子节点数量"""
    if tree.feature[node_id] == -2:  # 叶子节点
        return 1
    left = tree.children_left[node_id]
    right = tree.children_right[node_id]
    left_leaves = count_leaves(left) if left != -1 else 0
    right_leaves = count_leaves(right) if right != -1 else 0
    return left_leaves + right_leaves


# 计算所有节点的叶子数量
leaf_counts = {}


def precompute_leaf_counts(node_id=0):
    leaf_counts[node_id] = count_leaves(node_id)
    if tree.feature[node_id] != -2:
        left = tree.children_left[node_id]
        right = tree.children_right[node_id]
        if left != -1:
            precompute_leaf_counts(left)
        if right != -1:
            precompute_leaf_counts(right)


precompute_leaf_counts()

# 根据叶子节点数量动态调整画布大小
total_leaves = leaf_counts[0]
leaf_spacing = 3.0  # 每个叶子节点的水平间距
canvas_width = max(total_leaves * leaf_spacing, 60)

fig, ax = plt.subplots(figsize=(canvas_width, 32))
ax.axis('off')


def get_node_text(node_id):
    """获取节点显示文本"""
    if tree.feature[node_id] != -2:  # 不是叶子节点
        feature_name = feature_names[tree.feature[node_id]]
        threshold = tree.threshold[node_id]
        return f"{feature_name}\n<= {threshold:.0f}"
    else:  # 叶子节点
        value = tree.value[node_id][0]
        if value[1] > value[0]:
            return "是"
        else:
            return "否"


def draw_node(ax, x, y, text, is_leaf=False):
    """绘制节点"""
    if is_leaf:
        box = FancyBboxPatch((x - 0.8, y - 0.5), 1.6, 1.0,
                             boxstyle="round,pad=0.05",
                             facecolor='#2E5F8C',
                             edgecolor='black',
                             linewidth=1.5)
    else:
        box = mpatches.Circle((x, y), 1.0,
                              facecolor='#2E5F8C',
                              edgecolor='black',
                              linewidth=1.5)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center',
            fontsize=7, color='white', weight='bold')


def draw_edge(ax, x1, y1, x2, y2, label):
    """绘制边和标签"""
    ax.plot([x1, x2], [y1, y2], 'k-', linewidth=1.5)
    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
    ax.text(mid_x, mid_y, label, ha='center', va='bottom',
            fontsize=6, weight='bold')


def plot_tree_custom(node_id=0, x=None, y=30, level=0):
    """递归绘制决策树 - 基于叶子节点数量动态分配空间"""
    if x is None:
        x = canvas_width / 2

    # 获取当前节点的叶子数量
    num_leaves = leaf_counts[node_id]

    if tree.feature[node_id] == -2:  # 叶子节点
        draw_node(ax, x, y, get_node_text(node_id), is_leaf=True)
        return

    draw_node(ax, x, y, get_node_text(node_id), is_leaf=False)

    left_child = tree.children_left[node_id]
    right_child = tree.children_right[node_id]

    new_y = y - 4.5

    if left_child != -1 and right_child != -1:
        # 根据左右子树的叶子数量分配空间
        left_leaves = leaf_counts[left_child]
        right_leaves = leaf_counts[right_child]

        # 计算左右子树应该占用的宽度
        total_width = num_leaves * leaf_spacing
        left_width = (left_leaves / num_leaves) * total_width
        right_width = (right_leaves / num_leaves) * total_width

        # 计算左右子节点的x坐标
        left_x = x - right_width / 2
        right_x = x + left_width / 2

        draw_edge(ax, x, y - 0.4, left_x, new_y + 0.4, "是")
        plot_tree_custom(left_child, left_x, new_y, level + 1)

        draw_edge(ax, x, y - 0.4, right_x, new_y + 0.4, "否")
        plot_tree_custom(right_child, right_x, new_y, level + 1)
    elif left_child != -1:
        left_x = x
        draw_edge(ax, x, y - 0.4, left_x, new_y + 0.4, "是")
        plot_tree_custom(left_child, left_x, new_y, level + 1)
    elif right_child != -1:
        right_x = x
        draw_edge(ax, x, y - 0.4, right_x, new_y + 0.4, "否")
        plot_tree_custom(right_child, right_x, new_y, level + 1)


# 绘制树
plot_tree_custom()

# 设置坐标轴范围
ax.set_xlim(-2, canvas_width + 2)
ax.set_ylim(-2, 32)

plt.tight_layout()
plt.savefig('output/custom_tree_depth6.png', dpi=300, bbox_inches='tight')
print("\n图片已保存为 output/custom_tree_depth6.png")
plt.show()