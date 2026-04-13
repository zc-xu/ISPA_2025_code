import os
import numpy as np
np.set_printoptions(threshold=np.inf, linewidth=200)
import random
import matplotlib.pyplot as plt
from pymoo.indicators.hv import HV

# 项目根目录（LocalSearch/ 的上一级）
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ====== pymoo核心类 ====== #
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling
from pymoo.core.repair import Repair
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.termination import get_termination
from pymoo.optimize import minimize

# ====== 引入你已有的compute_delay函数或常量 ====== #
# 假设你的 compute_delay.py 就在同级目录:
from LocalSearch.compute_delay import (
    SERVICE_DEPLOY_COSTS,         # [100, 120, 80, ...] 每类服务的部署费用
    SERVICE_CAPACITY_PER_SERVER,  # 每台服务器最多可部署几个服务
    SERVICE_WORKLOADS,            # 各类服务的计算量
    SERVICE_DATA_SIZES,           # 各类服务对应的数据量
    DEFAULT_CAPACITY,
    DEFAULT_TX_RATE,
    THRESHOLD_DISTANCE,
    COMM_PENALTY_FACTOR,
    haversine_distance
)

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# --- 全局字体设置 (确保与 main.py 风格一致) ---
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False


def visualize_detailed_hybrid_process(server_id, candidate_data):
    """
    绘制 Hybrid-A-1 的详细全流程图 (两张独立竖向柱状图，无标注，统一样式)
    """
    # 1. 数据准备：按总分从高到低排序
    data = sorted(candidate_data, key=lambda x: x['total'], reverse=True)

    ids = [str(d['id']) for d in data]
    cost_parts = [d['cost_part'] for d in data]
    req_parts = [d['req_part'] for d in data]
    totals = [d['total'] for d in data]
    statuses = [d['status'] for d in data]

    # ==========================
    # 🎨 颜色设置区域 (已调亮)
    # ==========================
    # Stage 1: 柔和的浅紫 & 浅橙
    color_cost = '#BB8FCE'  # 浅紫色 (Lighter Purple)
    color_req = '#F8C471'  # 浅橙色 (Lighter Orange)

    # Stage 2: 清新的红、蓝、灰
    status_colors = {
        'Top-N': '#FF7675',  # 浅红色 (Soft Red)
        'Random': '#74B9FF',  # 浅蓝色 (Soft Blue)
        'Discarded': '#E5E7E9'  # 极浅灰 (Very Light Gray) - 这样如果不选中几乎看不见，很干净
    }
    bar_colors = [status_colors[s] for s in statuses]

    x_pos = np.arange(len(data))

    # =========================================================
    # 图表 1: [Stage 1] 评分来源分解 (Score Breakdown)
    # =========================================================
    plt.figure(figsize=(8, 6))
    ax1 = plt.gca()

    # 绘制堆叠柱状图 (竖向)
    # zorder=3 保证柱子在网格线上方
    p1 = ax1.bar(x_pos, cost_parts, color=color_cost, label=r'Cost Score ($\alpha \cdot W_{cost}$)',
                 alpha=0.85, width=0.6, zorder=3, edgecolor='black', linewidth=0.5)
    p2 = ax1.bar(x_pos, req_parts, bottom=cost_parts, color=color_req, label=r'Request Score ($\beta \cdot W_{req}$)',
                 alpha=0.85, width=0.6, zorder=3, edgecolor='black', linewidth=0.5)

    # --- 样式设置 ---
    # X轴
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([f"Service {i}" for i in ids], fontsize=16, rotation=0)

    # Y轴
    plt.yticks(fontsize=16)
    plt.ylabel("Weighted Score", fontname='Arial', fontsize=18)

    # 网格线 (放在最底层)
    ax1.grid(axis='y', linestyle='--', linewidth=0.75, alpha=0.7, zorder=0)

    # 图例 (右上角)
    ax1.legend(loc='upper right', fontsize=14, frameon=True, edgecolor='lightgray', framealpha=1)

    # 保存 Stage 1
    plt.tight_layout()
    filename1 = os.path.join(PROJECT_ROOT, f"output/pdf/hybrid_process_stage1_server_{server_id}.pdf")
    plt.savefig(filename1, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"✅ 生成 Stage 1 图表 (无标注): {filename1}")

    # =========================================================
    # 图表 2: [Stage 2] 选择逻辑 (Selection Logic) - 改为竖向
    # =========================================================
    plt.figure(figsize=(8, 6))
    ax2 = plt.gca()

    # --- 1. 确定三个区域的边界索引 ---
    top_n_count = sum(1 for s in statuses if s == 'Top-N')
    random_count = sum(1 for s in statuses if s == 'Random')
    # 区域分界线: Top-N | Random | Discarded
    boundary_1 = top_n_count - 0.5          # Top-N 与 Random 之间
    boundary_2 = top_n_count + random_count - 0.5  # Random 与 Discarded 之间

    # --- 2. 绘制区域背景色 (zorder=0，在最底层) ---
    ax2.axvspan(-0.5, boundary_1, facecolor='#FF7675', alpha=0.08, zorder=0)
    ax2.axvspan(boundary_1, boundary_2, facecolor='#74B9FF', alpha=0.08, zorder=0)
    ax2.axvspan(boundary_2, len(data) - 0.5, facecolor='#B0B0B0', alpha=0.08, zorder=0)

    # --- 3. 绘制柱状图 ---
    bar_width = 0.6
    for idx_bar in range(len(data)):
        s = statuses[idx_bar]
        if s == 'Discarded':
            # Discarded: 用斜线填充 + 低透明度，视觉上表达"被淘汰"
            ax2.bar(x_pos[idx_bar], totals[idx_bar], color='#E5E7E9',
                    edgecolor='gray', alpha=0.5, width=bar_width, zorder=3,
                    linewidth=0.8, hatch='///')
        else:
            ax2.bar(x_pos[idx_bar], totals[idx_bar], color=bar_colors[idx_bar],
                    edgecolor='black', alpha=0.9, width=bar_width, zorder=3,
                    linewidth=0.5)

    # --- 4. 绘制区域分隔虚线 ---
    ax2.axvline(x=boundary_1, color='gray', linestyle='--', linewidth=1.2, alpha=0.7, zorder=2)
    ax2.axvline(x=boundary_2, color='gray', linestyle='--', linewidth=1.2, alpha=0.7, zorder=2)

    # --- 5. 添加区域标注 (图表顶部) ---
    y_top = ax2.get_ylim()[1] if ax2.get_ylim()[1] > max(totals) * 1.1 else max(totals) * 1.15
    ax2.set_ylim(top=y_top)
    label_y = y_top * 0.95

    ax2.text((0 + boundary_1) / 2 - 0.25, label_y, 'Deterministic',
             fontsize=12, fontweight='bold', color='#D63031',
             ha='center', va='top', zorder=5)
    ax2.text((boundary_1 + boundary_2) / 2, label_y, 'Random Pool',
             fontsize=12, fontweight='bold', color='#0984E3',
             ha='center', va='top', zorder=5)
    if boundary_2 < len(data) - 0.5:
        ax2.text((boundary_2 + len(data) - 0.5) / 2, label_y, 'Discarded',
                 fontsize=12, fontweight='bold', color='#7F8C8D',
                 ha='center', va='top', zorder=5)

    # --- 样式设置 ---
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([f"Service {i}" for i in ids], fontsize=16, rotation=0)
    plt.yticks(fontsize=16)
    plt.ylabel("Total Hybrid Score", fontname='Arial', fontsize=18)

    # 网格线
    ax2.grid(axis='y', linestyle='--', linewidth=0.75, alpha=0.7, zorder=1)

    # 手动构建图例 (右上角)
    legend_patches = [
        mpatches.Patch(color='#FF7675', label='Top-N'),
        mpatches.Patch(color='#74B9FF', label='Random'),
        mpatches.Patch(facecolor='#E5E7E9', edgecolor='gray', label='Discarded', hatch='///'),
    ]
    ax2.legend(handles=legend_patches, loc='upper right', fontsize=14, frameon=True, edgecolor='lightgray', framealpha=1)

    # 保存 Stage 2
    plt.tight_layout()
    filename2 = os.path.join(PROJECT_ROOT, f"output/pdf/hybrid_process_stage2_server_{server_id}.pdf")
    plt.savefig(filename2, format='pdf', bbox_inches='tight')
    plt.close()
    print(f"✅ 生成 Stage 2 图表 (竖版无标注): {filename2}")
###############################################################
#  (1) Problem定义: MyServiceDeployProblem
###############################################################
class MyServiceDeployProblem(Problem):
    """
    我们假设:
    - 已经选定了 k 台服务器 (位置固定, 由局部搜索给出).
    - 每个服务器可以最多部署 SERVICE_CAPACITY_PER_SERVER(=3) 类服务.
    - 共有 8 类服务(索引[0..7])。同一服务可重复部署到多台服务器，但会多次产生部署费用。
    - 用户 -> 'assigned_server[u]' 表示首选服务器(局部搜索结果)；如果该服务器没有部署用户所需服务 => 找最近有该服务的服务器 => 计算通信/延迟.
    - 优化目标:
         f1(Cost)  = 通信成本 + 服务部署成本
         f2(Delay) = 总时延(含计算+通信中继)
    """
    def __init__(self,
                 k,                            # 服务器数
                 servers_pos,                  # shape(k, 2)
                 user_positions,               # shape(m, 2)
                 user_services,                # shape(m,)  => 每个用户的服务类型(0..7)
                 assigned_server,              # shape(m,)  => 每个用户首选服务器
                 num_services=8,               # 默认为8类服务
                 # num_services=16,                # 默认为8类服务
                 **kwargs):

        # n_var = k * 8  (每个服务器8列 => 0/1是否部署服务i)
        n_var = k * num_services
        n_obj = 2   # Cost, Delay
        n_constr = 0

        # 决策变量下界=0, 上界=1 => 我们后面会用 repair+round 做0/1
        xl = np.zeros(n_var)
        xu = np.ones(n_var)

        super().__init__(
            n_var=n_var,
            n_obj=n_obj,
            n_constr=n_constr,
            xl=xl,
            xu=xu,
            **kwargs
        )

        # 存储
        self.k = k
        self.num_services = num_services
        self.servers_pos = servers_pos
        self.user_positions = user_positions
        self.user_services = user_services
        self.assigned_server = assigned_server  # 用户首选服务器

    def _evaluate(self, X, out, *args, **kwargs):
        """
        X: shape (pop_size, n_var)
        out["F"] => shape (pop_size, 2), 分别表示 (cost, delay)
        """
        pop_size = X.shape[0]
        costs = np.zeros(pop_size)
        delays = np.zeros(pop_size)

        for i in range(pop_size):
            # 1) 把个体 X[i] reshape => (k, 8) => 强制0/1
            x_1d = np.round(X[i])  # [0,1]
            indiv = x_1d.reshape((self.k, self.num_services))

            # 2) 计算 (cost, delay)
            c, d = self._calc_obj(indiv)
            costs[i]  = c
            delays[i] = d

        out["F"] = np.column_stack([costs, delays])

    def _calc_obj(self, indiv):
        """给定一个 (k,8) 0/1 矩阵 => 返回 (cost,delay)"""

        # ========== (A) 计算服务部署成本 ========== #
        # 若同一个服务在多个服务器部署, 费用累加
        deploy_cost = 0.0
        for j in range(self.k):
            for svc in range(self.num_services):
                if indiv[j, svc] == 1:
                    deploy_cost += SERVICE_DEPLOY_COSTS[svc]

        # ========== (B) 计算通信成本 + 用户延迟 ========== #
        #   对每个用户:
        #   1) 若其 assigned_server 有这个服务 => 就用 assigned_server
        #   2) 否则找最近有 svc 的服务器 => 计算通信距离 => cost & delay
        total_comm_cost = 0.0
        total_delay = 0.0

        for u, upos in enumerate(self.user_positions):
            svc_type = self.user_services[u]
            prime_srv = self.assigned_server[u]
            dist = haversine_distance(upos[0], upos[1],
                                      self.servers_pos[prime_srv][0],
                                      self.servers_pos[prime_srv][1])

            # 该用户首选服务器是否已部署服务
            if indiv[prime_srv, svc_type] == 1:
                # 直接使用 prime_srv
                # dist = haversine_distance(upos[0], upos[1],
                #                           self.servers_pos[prime_srv][0],
                #                           self.servers_pos[prime_srv][1])
                # comm_cost_u = dist * 1.0  # 你可定义 distance->cost, 1.0表示1元/km
                # 新增逻辑：若 dist <= THRESHOLD => cost=0, 否则 dist*factor
                if dist <= THRESHOLD_DISTANCE:
                    comm_cost_u = 0.0
                else:
                    comm_cost_u = dist * COMM_PENALTY_FACTOR
                delay_u     = self._compute_user_delay_ex(upos, prime_srv, svc_type, indiv)
            else:
                # 找最近拥有 svc_type 的服务器
                best_j, best_dist = self._find_nearest_server_with_service(upos, svc_type, indiv)
                if best_j is None:
                    # 没有任何服务器部署该服务 => 给极大惩罚
                    comm_cost_u = 999999.0 * 0.01
                    delay_u = 999999.0 * 0.01
                    # comm_cost_u = dist * self.k * COMM_PENALTY_FACTOR
                    # delay_u = self._compute_user_delay_ex(upos, prime_srv, svc_type, indiv) * self.k
                else:
                    comm_cost_u = best_dist * 1.0
                    delay_u     = self._compute_user_delay_ex(upos, best_j, svc_type, indiv)
            total_comm_cost += comm_cost_u
            total_delay     += delay_u

        # ========== 最终 cost = 部署cost + 通信cost,   delay = total_delay
        # 这里修改
        cost = deploy_cost + total_comm_cost
        # cost = deploy_cost
        # print("看下deploy_cost的值",deploy_cost)
        # print("看下comm_cost的值", total_comm_cost)
        delay= total_delay
        return cost, delay

    def _find_nearest_server_with_service(self, user_pos, svc_type, indiv):
        """在部署矩阵indiv中找到拥有svc_type服务的服务器中距离最近的那一个"""
        min_dist = 1e9
        best_j   = None
        for j in range(self.k):
            if indiv[j, svc_type] == 1:
                dist = haversine_distance(user_pos[0], user_pos[1],
                                          self.servers_pos[j][0],
                                          self.servers_pos[j][1])
                if dist < min_dist:
                    min_dist = dist
                    best_j = j
        return best_j, min_dist if best_j is not None else (None, None)

    def _compute_user_delay_ex(self, user_pos, srv_idx, svc_type, indiv):
        """
        计算用户 u 在服务器 srv_idx 上执行 svc_type 的延迟(包含计算+通信).
        也可以复用 compute_user_delay() 函数，但这里可能还要考虑 threshold等.
        视需求实现.
        """
        # ====================
        # 1) 计算距离
        dist = haversine_distance(user_pos[0], user_pos[1],
                                  self.servers_pos[srv_idx][0],
                                  self.servers_pos[srv_idx][1])
        # 2) 计算延迟:
        #   计算延迟 = SERVICE_WORKLOADS[svc_type]/DEFAULT_CAPACITY
        #   通信延迟(示例):
        compute_delay = SERVICE_WORKLOADS[svc_type] / DEFAULT_CAPACITY
        if dist <= THRESHOLD_DISTANCE:
            comm_delay = 0.0
        else:
            # 例如: data_size / tx_rate * distance * COMM_PENALTY_FACTOR
            # (可自行修改)
            data_size = SERVICE_DATA_SIZES[svc_type]
            base_time = data_size / DEFAULT_TX_RATE
            comm_delay = base_time * COMM_PENALTY_FACTOR * dist

        # print("compute_delay", compute_delay)
        # print("comm_delay", comm_delay)
        return compute_delay + comm_delay

###############################################################
#  (2) Repair: 确保每台服务器 <= 4个服务
###############################################################
class ServiceRepair(Repair):
    def _do(self, problem, X, **kwargs):
        """
        X: shape (pop_size, n_var)
        """
        pop_size, n_var = X.shape
        k = problem.k
        num_svc = problem.num_services

        for i in range(pop_size):
            # 强制0/1
            X[i] = np.round(X[i])

            mat = X[i].reshape((k, num_svc))
            for j in range(k):
                while np.sum(mat[j]) > SERVICE_CAPACITY_PER_SERVER:
                    ones_idx = np.where(mat[j] == 1)[0]
                    drop_col = random.choice(ones_idx)
                    mat[j, drop_col] = 0
            X[i] = mat.flatten()

        return X


class ServiceSampling(Sampling):
    def __init__(self, mode="random"):
        super().__init__()
        self.mode = mode

    def _do(self, problem, n_samples, **kwargs):
        k = problem.k
        num_svc = problem.num_services
        n_var = k * num_svc
        cap = SERVICE_CAPACITY_PER_SERVER
        from LocalSearch.service_selection_strategies import (
            greedy_service_deployment_by_cost,
            greedy_service_deployment_by_request
        )

        def perturb(mat):
            new_mat = np.copy(mat)
            for j in range(k):
                # replace_count = random.randint(1,2)
                # replace_count = random.randint(3, 4)#最佳
                replace_count = random.randint(2, 4)
                # replace_count = 1
                # replace_count = 4
                for _ in range(replace_count):
                    ones = np.where(new_mat[j] == 1)[0]
                    zeros = np.where(new_mat[j] == 0)[0]
                    if len(ones) > 0 and len(zeros) > 0:
                        drop = random.choice(ones)
                        add = random.choice(zeros)
                        new_mat[j, drop] = 0
                        new_mat[j, add] = 1
            return new_mat

        def perturb_random(mat):
            new_mat = np.copy(mat)
            for j in range(k):
                replace_count = random.randint(1, 2)
                # replace_count = random.randint(2, 4)
                # replace_count = 1##刚才的
                # replace_count = 4
                # replace_count = (0,1)
                for _ in range(replace_count):
                    ones = np.where(new_mat[j] == 1)[0]
                    zeros = np.where(new_mat[j] == 0)[0]
                    if len(ones) > 0 and len(zeros) > 0:
                        drop = random.choice(ones)
                        add = random.choice(zeros)
                        new_mat[j, drop] = 0
                        new_mat[j, add] = 1
            return new_mat

        def perturb_new(mat):
            new_mat = np.copy(mat)
            for j in range(k):
                # replace_count = random.randint(1, 2)
                # replace_count = random.randint(2, 3)
                replace_count = 1 ##所有的基准
                # replace_count = 4
                for _ in range(replace_count):
                    ones = np.where(new_mat[j] == 1)[0]
                    zeros = np.where(new_mat[j] == 0)[0]
                    if len(ones) > 0 and len(zeros) > 0:
                        drop = random.choice(ones)
                        add = random.choice(zeros)
                        new_mat[j, drop] = 0
                        new_mat[j, add] = 1
            return new_mat

        def perturb_cost(mat):
            new_mat = np.copy(mat)
            for j in range(k):
                # replace_count = random.randint(2, 4)
                replace_count = random.randint(1, 2)##刚才效果还可以的
                # replace_count = 4
                # replace_count = 1
                for _ in range(replace_count):
                    ones = np.where(new_mat[j] == 1)[0]
                    zeros = np.where(new_mat[j] == 0)[0]
                    if len(ones) > 0 and len(zeros) > 0:
                        drop = random.choice(ones)
                        add = random.choice(zeros)
                        new_mat[j, drop] = 0
                        new_mat[j, add] = 1
            return new_mat

        def expand_population(base_mat):
            X = np.zeros((n_samples, n_var))
            for i in range(n_samples):
                if i == 0:
                    mat = base_mat
                    print("\n🔍 初始解（第一个个体）:\n", mat)  # ✅ 打印基础部署矩阵
                else:
                    mat = perturb(base_mat)
                    # print("\n🔍 随机策略其余解:\n", mat)
                X[i] = mat.flatten()
            return X

        def expand_population_random(base_mat):
            X = np.zeros((n_samples, n_var))
            for i in range(n_samples):
                if i == 0:
                    mat = base_mat
                    print("\n🔍 初始解（第一个个体）:\n", mat)  # ✅ 打印基础部署矩阵
                else:
                    mat = perturb_random(base_mat)
                    # print("\n🔍 随机策略其余解:\n", mat)
                X[i] = mat.flatten()
            return X

        def expand_population_new(base_mat):
            X = np.zeros((n_samples, n_var))
            for i in range(n_samples):
                if i == 0:
                    mat = base_mat
                    print("\n🔍 初始解（第一个个体）:\n", mat)  # ✅ 打印基础部署矩阵
                else:
                    mat = perturb_new(base_mat)
                    # print("\n🔍 混合策略其余解:\n", mat)
                X[i] = mat.flatten()
            return X

        def expand_population_cost(base_mat):
            X = np.zeros((n_samples, n_var))
            for i in range(n_samples):
                if i == 0:
                    mat = base_mat
                    print("\n🔍 初始解（第一个个体）:\n", mat)  # ✅ 打印基础部署矩阵
                else:
                    mat = perturb_cost(base_mat)
                    # print("\n🔍 混合策略其余解:\n", mat)
                X[i] = mat.flatten()
            return X

        def expand_population_hybrid_mixed(base_mat, n_samples, k, num_svc):
            """
            一半解使用 base_mat + perturb_new，另一半使用随机策略 + perturb
            """
            assert n_samples % 2 == 0, "n_samples 应为偶数"
            half = n_samples // 2
            n_var = k * num_svc
            X = np.zeros((n_samples, n_var))

            # 混合策略部分
            for i in range(half):
                if i == 0:
                    mat = base_mat
                    print("\n🔍 混合策略第一个个体:\n", mat)
                else:
                    mat = perturb_new(base_mat)
                    print(f"\n🔍 混合策略个体 {i}：\n", mat)
                X[i] = mat.flatten()

            # 随机策略部分
            for i in range(half, n_samples):
                mat = np.zeros((k, num_svc), dtype=int)
                for j in range(k):
                    svc_indices = np.random.permutation(num_svc)
                    selected = svc_indices[:SERVICE_CAPACITY_PER_SERVER]
                    mat[j, selected] = 1
                mat = perturb(mat)
                print(f"\n🔍 随机策略个体 {i}：\n", mat)
                X[i] = mat.flatten()

            return X


        if self.mode == "random":
            base_mat = np.zeros((k, num_svc), dtype=int)
            anchor_services = []
            for j in range(k):
                svc_indices = np.random.permutation(num_svc)
                selected = svc_indices[:cap]
                base_mat[j, selected] = 1
                anchor_services.append(selected[0])  # 保留第一个服务作为 anchor
            # return expand_population_with_anchor(base_mat, anchor_services)
            # return expand_population(base_mat)
            return expand_population_random(base_mat)


        elif self.mode == "hybrid":
            cost_mat, _, _, _ = greedy_service_deployment_by_cost(
                problem.servers_pos, problem.user_positions,
                problem.user_services, problem.assigned_server
            )
            req_mat, _, _, _ = greedy_service_deployment_by_request(
                problem.servers_pos, problem.user_positions,
                problem.user_services, problem.assigned_server
            )

            from LocalSearch.service_selection_strategies import compute_objectives

            alpha = 0.5
            beta = 0.5

            base_mat = np.zeros((k, num_svc), dtype=int)
            mat_r_list = []
            mat_w_list = []
            cost_r_list = []
            delay_r_list = []
            cost_w_list = []
            delay_w_list = []

            # ========== Step 1: 收集所有 cost/delay ==========
            for j in range(k):
                # 构建 cost_order 和 request_order
                cost_order = sorted([idx for idx, val in enumerate(cost_mat[j]) if val == 1],
                                    key=lambda x: SERVICE_DEPLOY_COSTS[x])
                cost_weight = {svc: max(SERVICE_CAPACITY_PER_SERVER - rank, 1)
                               for rank, svc in enumerate(cost_order)}

                freq = {svc: 0 for svc in range(num_svc)}
                user_indices = [u for u, srv in enumerate(problem.assigned_server) if srv == j]
                for u in user_indices:
                    freq[problem.user_services[u]] += 1
                request_order = sorted([idx for idx, val in enumerate(req_mat[j]) if val == 1],
                                       key=lambda x: -freq[x])
                request_weight = {svc: max(SERVICE_CAPACITY_PER_SERVER - rank, 1)
                                  for rank, svc in enumerate(request_order)}

                # 合并并构建随机和权重策略
                merged_set = set(cost_order) | set(request_order)
                merged_list = list(merged_set)

                random_selected = merged_list.copy()
                if len(random_selected) > cap:
                    random_selected = random.sample(random_selected, cap)
                mat_r = np.zeros((k, num_svc), dtype=int)
                for svc in random_selected:
                    mat_r[j, svc] = 1

                score_dict = {}
                for svc in merged_set:
                    cw = cost_weight.get(svc, 0)
                    rw = request_weight.get(svc, 0)
                    score = alpha * cw + beta * rw
                    score_dict[svc] = score
                sorted_services = sorted(score_dict.items(), key=lambda x: -x[1])
                weight_selected = [svc for svc, _ in sorted_services[:cap]]
                mat_w = np.zeros((k, num_svc), dtype=int)
                for svc in weight_selected:
                    mat_w[j, svc] = 1

                # 计算 cost & delay
                cost_r, delay_r = compute_objectives(mat_r, problem.servers_pos,
                                                     problem.user_positions,
                                                     problem.user_services,
                                                     problem.assigned_server)
                cost_w, delay_w = compute_objectives(mat_w, problem.servers_pos,
                                                     problem.user_positions,
                                                     problem.user_services,
                                                     problem.assigned_server)

                mat_r_list.append(mat_r)
                mat_w_list.append(mat_w)
                cost_r_list.append(cost_r)
                delay_r_list.append(delay_r)
                cost_w_list.append(cost_w)
                delay_w_list.append(delay_w)

            # ========== Step 2: 全局归一化范围 ==========
            cost_all = cost_r_list + cost_w_list
            delay_all = delay_r_list + delay_w_list
            cost_min, cost_max = min(cost_all), max(cost_all)
            delay_min, delay_max = min(delay_all), max(delay_all)

            def norm(v, vmin, vmax):
                return (v - vmin) / (vmax - vmin + 1e-6)

            # ========== Step 3: 比较并选择 ==========
            for j in range(k):
                cost_r = cost_r_list[j]
                delay_r = delay_r_list[j]
                cost_w = cost_w_list[j]
                delay_w = delay_w_list[j]

                score_r = alpha * norm(cost_r, cost_min, cost_max) + beta * norm(delay_r, delay_min, delay_max)
                score_w = alpha * norm(cost_w, cost_min, cost_max) + beta * norm(delay_w, delay_min, delay_max)

                print(f"\n🔍 Server {j} 比较两种策略（归一化后加权）:")
                print(f"  随机策略 -> RawCost: {cost_r:.2f}, RawDelay: {delay_r:.2f}, Score: {score_r:.4f}")
                print(f"  权重策略 -> RawCost: {cost_w:.2f}, RawDelay: {delay_w:.2f}, Score: {score_w:.4f}")
                print(f"  ✅ 选择策略: {'权重策略' if score_w < score_r else '随机策略'}")

                base_mat[j] = mat_w_list[j][j] if score_w < score_r else mat_r_list[j][j]

            return expand_population_new(base_mat)

        # 2. 混合策略
        elif self.mode == "hybrid-A":
            cost_mat, _, _, _ = greedy_service_deployment_by_cost(
                problem.servers_pos, problem.user_positions,
                problem.user_services, problem.assigned_server
            )
            req_mat, _, _, _ = greedy_service_deployment_by_request(
                problem.servers_pos, problem.user_positions,
                problem.user_services, problem.assigned_server
            )
            #1.随机在Merge之后的数组里drop掉超容量的
            #2.按照权重做法去drop掉超出容量限制的数量
            alpha = 0.5  # 成本占比
            beta = 0.5  # 请求频率占比

            base_mat = np.zeros((k, num_svc), dtype=int)
            for j in range(k):

                # 获取 cost_order
                cost_order = sorted(
                    [idx for idx, val in enumerate(cost_mat[j]) if val == 1],
                    key=lambda x: SERVICE_DEPLOY_COSTS[x]
                )
                cost_weight = {}
                for rank, svc in enumerate(cost_order):
                    cost_weight[svc] = max(SERVICE_CAPACITY_PER_SERVER - rank, 1)

                # 获取 request_order
                freq = {svc: 0 for svc in range(num_svc)}
                user_indices = [u for u, srv in enumerate(problem.assigned_server) if srv == j]
                for u in user_indices:
                    freq[problem.user_services[u]] += 1
                request_order = sorted(
                    [idx for idx, val in enumerate(req_mat[j]) if val == 1],
                    key=lambda x: -freq[x]
                )
                request_weight = {}
                for rank, svc in enumerate(request_order):
                    request_weight[svc] = max(SERVICE_CAPACITY_PER_SERVER - rank, 1)

                # 合并并打分
                merged_set = set(cost_order) | set(request_order)
                score_dict = {}
                for svc in merged_set:
                    cw = cost_weight.get(svc, 0)
                    rw = request_weight.get(svc, 0)
                    score = alpha * cw + beta * rw
                    score_dict[svc] = score

                # 最终选择前 cap 个分数最高的服务
                sorted_services = sorted(score_dict.items(), key=lambda x: -x[1])
                selected_services = [svc for svc, _ in sorted_services[:SERVICE_CAPACITY_PER_SERVER]]

                for svc in selected_services:
                    base_mat[j, svc] = 1


            return expand_population_new(base_mat)
            # return expand_population(base_mat)


        elif self.mode == "hybrid-A-1":

            # ... (这部分代码保持不变，获取 cost_mat 和 req_mat) ...

            cost_mat, _, _, _ = greedy_service_deployment_by_cost(

                problem.servers_pos, problem.user_positions,

                problem.user_services, problem.assigned_server

            )

            req_mat, _, _, _ = greedy_service_deployment_by_request(

                problem.servers_pos, problem.user_positions,

                problem.user_services, problem.assigned_server

            )

            alpha = 0.5;
            beta = 0.5

            base_mat = np.zeros((k, num_svc), dtype=int)

            for j in range(k):

                # --- 1. 计算权重 (保持不变) ---

                cost_order = sorted([idx for idx, val in enumerate(cost_mat[j]) if val == 1],

                                    key=lambda x: SERVICE_DEPLOY_COSTS[x])

                cost_weight = {svc: max(SERVICE_CAPACITY_PER_SERVER - rank, 1) for rank, svc in enumerate(cost_order)}

                freq = {svc: 0 for svc in range(num_svc)}

                user_indices = [u for u, srv in enumerate(problem.assigned_server) if srv == j]

                for u in user_indices: freq[problem.user_services[u]] += 1

                request_order = sorted([idx for idx, val in enumerate(req_mat[j]) if val == 1],

                                       key=lambda x: -freq[x])

                request_weight = {svc: max(SERVICE_CAPACITY_PER_SERVER - rank, 1) for rank, svc in
                                  enumerate(request_order)}

                # --- 2. 详细数据收集 (修改部分) ---

                merged_set = set(cost_order) | set(request_order)

                # 临时列表，用于后续排序和绘图

                candidates_list = []

                for svc in merged_set:
                    cw = cost_weight.get(svc, 0)

                    rw = request_weight.get(svc, 0)

                    cost_part = alpha * cw

                    req_part = beta * rw

                    total_score = cost_part + req_part

                    candidates_list.append({

                        'id': svc,

                        'cost_part': cost_part,

                        'req_part': req_part,

                        'total': total_score,

                        'status': 'Discarded'  # 默认状态

                    })

                # --- 3. 选择逻辑 ---

                cap = SERVICE_CAPACITY_PER_SERVER

                keep_top_n = 2

                random_pick_n = cap - keep_top_n

                # 按总分排序

                candidates_list.sort(key=lambda x: x['total'], reverse=True)

                # 选 Top-N

                top_n_candidates = candidates_list[:keep_top_n]

                for c in top_n_candidates:
                    c['status'] = 'Top-N'

                # 选 Random

                remaining = candidates_list[keep_top_n:]

                if len(remaining) >= random_pick_n:

                    random_candidates = random.sample(remaining, random_pick_n)

                else:

                    random_candidates = remaining

                for c in random_candidates:
                    c['status'] = 'Random'

                # 最终选中列表

                selected_ids = [c['id'] for c in top_n_candidates + random_candidates]

                # 写入 base_mat

                for svc in selected_ids:
                    base_mat[j, svc] = 1

                # ==========================================

                # 🔥 [新钩子] 详细可视化：Server 0

                # ==========================================

                if j == 2:
                    print(f"\n📊 正在生成 Server {j} 的详细流程图...")

                    visualize_detailed_hybrid_process(j, candidates_list)

                # ==========================================

            return expand_population_new(base_mat)



            return expand_population_new(base_mat)

        elif self.mode == "hybrid-B":
            cost_mat, _, _, _ = greedy_service_deployment_by_cost(
                problem.servers_pos, problem.user_positions,
                problem.user_services, problem.assigned_server
            )
            req_mat, _, _, _ = greedy_service_deployment_by_request(
                problem.servers_pos, problem.user_positions,
                problem.user_services, problem.assigned_server
            )
            #1.随机在Merge之后的数组里drop掉超容量的
            #2.按照权重做法去drop掉超出容量限制的数量
            alpha = 0.5  # 成本占比
            beta = 0.5  # 请求频率占比

            base_mat = np.zeros((k, num_svc), dtype=int)
            for j in range(k):
                cost_order = sorted(
                    [idx for idx, val in enumerate(cost_mat[j]) if val == 1],
                    key=lambda x: SERVICE_DEPLOY_COSTS[x]
                )
                freq = {svc: 0 for svc in range(num_svc)}
                user_indices = [u for u, srv in enumerate(problem.assigned_server) if srv == j]
                for u in user_indices:
                    freq[problem.user_services[u]] += 1
                request_order = sorted(
                    [idx for idx, val in enumerate(req_mat[j]) if val == 1],
                    key=lambda x: -freq[x]
                )
                merged = []
                seen = set()
                for idx in cost_order + request_order:
                    if idx not in seen:
                        merged.append(idx)
                        seen.add(idx)
                # print(merged)

                if len(merged) > cap:
                    drop_count = len(merged) - cap
                    drop_items = random.sample(merged, drop_count)  # 不重复随机选
                    for d in drop_items:
                        merged.remove(d)
                # while len(merged) > cap:
                #     # candidates = merged[-2:] if len(merged) >= 2 else merged[-1:]
                #     # print(candidates)
                #     drop = random.choice()
                #     merged.remove(drop)
                for idx in merged:
                    base_mat[j, idx] = 1
            return expand_population_new(base_mat)
            # return expand_population(base_mat)

        elif self.mode == "hybrid-C":
            cost_mat, _, _, _ = greedy_service_deployment_by_cost(
                problem.servers_pos, problem.user_positions,
                problem.user_services, problem.assigned_server
            )
            req_mat, _, _, _ = greedy_service_deployment_by_request(
                problem.servers_pos, problem.user_positions,
                problem.user_services, problem.assigned_server
            )

            from LocalSearch.service_selection_strategies import compute_objectives

            alpha = 0.5
            beta = 0.5

            base_mat = np.zeros((k, num_svc), dtype=int)
            mat_r_list = []
            mat_w_list = []
            cost_r_list = []
            delay_r_list = []
            cost_w_list = []
            delay_w_list = []

            # ========== Step 1: 收集所有 cost/delay ==========
            for j in range(k):
                # 构建 cost_order 和 request_order
                cost_order = sorted([idx for idx, val in enumerate(cost_mat[j]) if val == 1],
                                    key=lambda x: SERVICE_DEPLOY_COSTS[x])
                cost_weight = {svc: max(SERVICE_CAPACITY_PER_SERVER - rank, 1)
                               for rank, svc in enumerate(cost_order)}

                freq = {svc: 0 for svc in range(num_svc)}
                user_indices = [u for u, srv in enumerate(problem.assigned_server) if srv == j]
                for u in user_indices:
                    freq[problem.user_services[u]] += 1
                request_order = sorted([idx for idx, val in enumerate(req_mat[j]) if val == 1],
                                       key=lambda x: -freq[x])
                request_weight = {svc: max(SERVICE_CAPACITY_PER_SERVER - rank, 1)
                                  for rank, svc in enumerate(request_order)}

                # 合并并构建随机和权重策略
                merged_set = set(cost_order) | set(request_order)
                merged_list = list(merged_set)

                random_selected = merged_list.copy()
                if len(random_selected) > cap:
                    random_selected = random.sample(random_selected, cap)
                mat_r = np.zeros((k, num_svc), dtype=int)
                for svc in random_selected:
                    mat_r[j, svc] = 1

                score_dict = {}
                for svc in merged_set:
                    cw = cost_weight.get(svc, 0)
                    rw = request_weight.get(svc, 0)
                    score = alpha * cw + beta * rw
                    score_dict[svc] = score
                sorted_services = sorted(score_dict.items(), key=lambda x: -x[1])
                weight_selected = [svc for svc, _ in sorted_services[:cap]]
                mat_w = np.zeros((k, num_svc), dtype=int)
                for svc in weight_selected:
                    mat_w[j, svc] = 1

                # 计算 cost & delay
                cost_r, delay_r = compute_objectives(mat_r, problem.servers_pos,
                                                     problem.user_positions,
                                                     problem.user_services,
                                                     problem.assigned_server)
                cost_w, delay_w = compute_objectives(mat_w, problem.servers_pos,
                                                     problem.user_positions,
                                                     problem.user_services,
                                                     problem.assigned_server)

                mat_r_list.append(mat_r)
                mat_w_list.append(mat_w)
                cost_r_list.append(cost_r)
                delay_r_list.append(delay_r)
                cost_w_list.append(cost_w)
                delay_w_list.append(delay_w)

            # ========== Step 2: 全局归一化范围 ==========
            cost_all = cost_r_list + cost_w_list
            delay_all = delay_r_list + delay_w_list
            cost_min, cost_max = min(cost_all), max(cost_all)
            delay_min, delay_max = min(delay_all), max(delay_all)

            def norm(v, vmin, vmax):
                return (v - vmin) / (vmax - vmin + 1e-6)

            # ========== Step 3: 比较并选择 ==========
            for j in range(k):
                cost_r = cost_r_list[j]
                delay_r = delay_r_list[j]
                cost_w = cost_w_list[j]
                delay_w = delay_w_list[j]

                score_r = alpha * norm(cost_r, cost_min, cost_max) + beta * norm(delay_r, delay_min, delay_max)
                score_w = alpha * norm(cost_w, cost_min, cost_max) + beta * norm(delay_w, delay_min, delay_max)

                print(f"\n🔍 Server {j} 比较两种策略（归一化后加权）:")
                print(f"  随机策略 -> RawCost: {cost_r:.2f}, RawDelay: {delay_r:.2f}, Score: {score_r:.4f}")
                print(f"  权重策略 -> RawCost: {cost_w:.2f}, RawDelay: {delay_w:.2f}, Score: {score_w:.4f}")
                print(f"  ✅ 选择策略: {'权重策略' if score_w < score_r else '随机策略'}")

                base_mat[j] = mat_w_list[j][j] if score_w < score_r else mat_r_list[j][j]

            # return expand_population_new(base_mat)
            return expand_population_hybrid_mixed(base_mat, n_samples, k, num_svc)

        # elif self.mode == "hybrid-C":
        #     cost_mat, _, _, _ = greedy_service_deployment_by_cost(
        #         problem.servers_pos, problem.user_positions,
        #         problem.user_services, problem.assigned_server
        #     )
        #     req_mat, _, _, _ = greedy_service_deployment_by_request(
        #         problem.servers_pos, problem.user_positions,
        #         problem.user_services, problem.assigned_server
        #     )
        #
        #     from LocalSearch.service_selection_strategies import compute_objectives
        #
        #     alpha = 0.5  # cost占比
        #     beta = 0.5  # request占比
        #     # alpha = 0.3  # cost占比
        #     # beta = 0.7  # request占比
        #
        #     base_mat = np.zeros((k, num_svc), dtype=int)
        #     print("初始随机")
        #     print(base_mat)
        #     anchor_services = []
        #
        #     for j in range(k):
        #         # === 准备 cost_order 和 request_order ===
        #         cost_order = sorted(
        #             [idx for idx, val in enumerate(cost_mat[j]) if val == 1],
        #             key=lambda x: SERVICE_DEPLOY_COSTS[x]
        #         )
        #         cost_weight = {svc: max(SERVICE_CAPACITY_PER_SERVER - rank, 1) for rank, svc in enumerate(cost_order)}
        #
        #         freq = {svc: 0 for svc in range(num_svc)}
        #         user_indices = [u for u, srv in enumerate(problem.assigned_server) if srv == j]
        #         for u in user_indices:
        #             freq[problem.user_services[u]] += 1
        #         request_order = sorted(
        #             [idx for idx, val in enumerate(req_mat[j]) if val == 1],
        #             key=lambda x: -freq[x]
        #         )
        #         request_weight = {svc: max(SERVICE_CAPACITY_PER_SERVER - rank, 1) for rank, svc in
        #                           enumerate(request_order)}
        #
        #         # === 生成 merged 集合 ===
        #         merged_set = set(cost_order) | set(request_order)
        #         merged_list = list(merged_set)
        #
        #         # (A) 随机删除策略
        #         random_selected = merged_list.copy()
        #         if len(random_selected) > cap:
        #             random_selected = random.sample(random_selected, cap)
        #         mat_r = np.zeros((k, num_svc), dtype=int)
        #         for svc in random_selected:
        #             mat_r[j, svc] = 1
        #
        #         # (B) 权重删除策略（根据 score）
        #         score_dict = {}
        #         for svc in merged_set:
        #             cw = cost_weight.get(svc, 0)
        #             rw = request_weight.get(svc, 0)
        #             score = alpha * cw + beta * rw
        #             score_dict[svc] = score
        #         sorted_services = sorted(score_dict.items(), key=lambda x: -x[1])
        #         weight_selected = [svc for svc, _ in sorted_services[:cap]]
        #         mat_w = np.zeros((k, num_svc), dtype=int)
        #         for svc in weight_selected:
        #             mat_w[j, svc] = 1
        #
        #         # # === 替换 base_mat[j] 选择更优方案 ===
        #         # cost_r, delay_r = compute_objectives(mat_r, problem.servers_pos, problem.user_positions,
        #         #                                      problem.user_services, problem.assigned_server)
        #         # cost_w, delay_w = compute_objectives(mat_w, problem.servers_pos, problem.user_positions,
        #         #                                      problem.user_services, problem.assigned_server)
        #         # #加黄的和绿的的做法,看看结果
        #         #
        #         # score_r = 0.5 * cost_r + 0.5 * delay_r
        #         # score_w = 0.5 * cost_w + 0.5 * delay_w
        #         #
        #         # print(f"\n🔍 Server {j} 比较两种策略：")
        #         # print(f"  随机删除策略服务列表: {sorted(random_selected)}")
        #         # print(f"  权重删除策略服务列表: {sorted(weight_selected)}")
        #         # print(f"  随机策略 -> Cost: {cost_r:.2f}, Delay: {delay_r:.2f}, Score: {score_r:.2f}")
        #         # print(f"  权重策略 -> Cost: {cost_w:.2f}, Delay: {delay_w:.2f}, Score: {score_w:.2f}")
        #         # print(f"  ✅ 选择策略: {'权重策略' if score_w < score_r else '随机策略'}")
        #         #
        #         # base_mat[j] = mat_w[j] if score_w < score_r else mat_r[j]
        #
        #         # === 替换 base_mat[j] 选择更优方案（归一化 + 加权） ===
        #         cost_r, delay_r = compute_objectives(mat_r, problem.servers_pos, problem.user_positions,
        #                                              problem.user_services, problem.assigned_server)
        #         cost_w, delay_w = compute_objectives(mat_w, problem.servers_pos, problem.user_positions,
        #                                              problem.user_services, problem.assigned_server)
        #
        #         # 最小-最大归一化（避免相差数量级造成偏差）
        #         cost_min = min(cost_r, cost_w)
        #         cost_max = max(cost_r, cost_w)
        #         delay_min = min(delay_r, delay_w)
        #         delay_max = max(delay_r, delay_w)
        #
        #         # 避免除以 0
        #         def norm(v, vmin, vmax):
        #             return (v - vmin) / (vmax - vmin + 1e-6)
        #
        #         norm_cost_r = norm(cost_r, cost_min, cost_max)
        #         norm_delay_r = norm(delay_r, delay_min, delay_max)
        #         norm_cost_w = norm(cost_w, cost_min, cost_max)
        #         norm_delay_w = norm(delay_w, delay_min, delay_max)
        #
        #         score_r = alpha * norm_cost_r + beta * norm_delay_r
        #         score_w = alpha * norm_cost_w + beta * norm_delay_w
        #
        #         print(f"\n🔍 Server {j} 比较两种策略（归一化后加权）:")
        #         print(f"  随机策略 -> RawCost: {cost_r:.2f}, RawDelay: {delay_r:.2f}, Score: {score_r:.4f}")
        #         print(f"  权重策略 -> RawCost: {cost_w:.2f}, RawDelay: {delay_w:.2f}, Score: {score_w:.4f}")
        #         print(f"  ✅ 选择策略: {'权重策略' if score_w < score_r else '随机策略'}")
        #
        #         base_mat[j] = mat_w[j] if score_w < score_r else mat_r[j]


            # return expand_population_new(base_mat)

            # return expand_population_hybrid_mixed(base_mat, n_samples, k, num_svc)



        # 3. 贪心成本策略
        elif self.mode == "greedy_cost":
            base_mat, _, _, _ = greedy_service_deployment_by_cost(
                problem.servers_pos, problem.user_positions,
                problem.user_services, problem.assigned_server
            )
            anchor_services = []
            for j in range(k):
                candidates = [idx for idx, val in enumerate(base_mat[j]) if val == 1]
                anchor = candidates[0] if candidates else random.randint(0, num_svc - 1)
                anchor_services.append(anchor)
            return expand_population_cost(base_mat)
            # return expand_population_with_anchor(base_mat, anchor_services)

        # 4. 贪心请求策略
        elif self.mode == "greedy_request":
            base_mat, _, _, _ = greedy_service_deployment_by_request(
                problem.servers_pos, problem.user_positions,
                problem.user_services, problem.assigned_server
            )
            anchor_services = []
            for j in range(k):
                candidates = [idx for idx, val in enumerate(base_mat[j]) if val == 1]
                anchor = candidates[0] if candidates else random.randint(0, num_svc - 1)
                anchor_services.append(anchor)
            return expand_population(base_mat)
            # return expand_population_with_anchor(base_mat, anchor_services)

        else:
            raise ValueError(f"Unsupported sampling mode: {self.mode}")


###############################################################
#  (4) NSGA-II 主流程
###############################################################
def run_nsga_service_deploy(servers_pos,
                            user_positions,
                            user_services,
                            assigned_server,
                            k,
                            pop_size=30,
                            n_gen=100,
                            seed=42):
    """
    传入:
      - servers_pos: shape(k,2), 服务器位置(已固定)
      - user_positions: shape(m,2)
      - user_services: shape(m,)
      - assigned_server: shape(m,), 局部搜索后的首选服务器
      - k: 服务器数
    返回:
      - result: pymoo求解之后的结果对象
    """
    # 1) 构造 problem
    problem = MyServiceDeployProblem(
        k=k,
        servers_pos=servers_pos,
        user_positions=user_positions,
        user_services=user_services,
        assigned_server=assigned_server
    )

    # 2) 构造NSGA2 算法
    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=ServiceSampling(),   # 我们自定义的 0/1 sampling
        repair=ServiceRepair(),       # 我们自定义的修复(保证行中<=4个1)
        eliminate_duplicates=True
    )

    # 3) 定义终止条件: 迭代n_gen代
    termination = get_termination("n_gen", n_gen)

    # 4) 执行优化
    res = minimize(
        problem,
        algorithm,
        termination,
        seed=seed,
        save_history=True,
        verbose=True
    )

    return res


#####################
# 4) 可视化帕累托前沿
#####################
def plot_pareto_front(result, title="NSGA-II Pareto Front"):
    all_F = result.F  # shape (pop_size, 2)
    pareto_F = np.array([s.F for s in result.opt])

    plt.figure(figsize=(7,5))
    plt.scatter(all_F[:,0], all_F[:,1], c="lightgray", label="All Solutions")
    plt.scatter(pareto_F[:,0], pareto_F[:,1], c="red", marker="o", s=60, label="Pareto Front")
    plt.xlabel("Cost")
    plt.ylabel("Delay")
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()

###############################################################
#  (5) 后处理: 分析结果
###############################################################
def analyze_nsga_result(result, k, num_svc=8, a=0.5, b=0.5):
    """
    result: pymoo返回的结果
    k: 服务器数
    num_svc: 每台服务器的服务列数(默认8)
    a,b: 对f1(Cost), f2(Delay)做加权 =>  weighted_value = a * cost + b * delay

    打印/可视化 Pareto 前沿, 并查看各个解的部署方案
    """
    # result.X => 最后一代存档(或整体种群)
    # result.F => 对应的 (Cost, Delay)

    # 这里获取最终的非支配解(帕累托前沿)
    opt_solutions = result.opt
    print(f"共找到 {len(opt_solutions)} 个非支配解(Pareto)")
    plot_pareto_front(result)

    for idx, sol in enumerate(opt_solutions):
        x = sol.X
        f = sol.F
        # f[0] = cost, f[1] = delay   (nsga中定义的两个目标)
        cost_val  = f[0]
        delay_val = f[1]

        # 额外计算 a*cost + b*delay
        combined_val = a * cost_val + b * delay_val

        # 强制0/1
        x = np.round(x)
        indiv = x.reshape((k, num_svc))

        # 打印一下
        print(f"\n--- Pareto解 {idx+1} ---")
        print(f"Cost = {cost_val:.4f}, Delay = {delay_val:.4f}")
        print(f"加权结果( a={a}, b={b} ): {combined_val:.4f}")

        # 也可以print部署矩阵
        print("部署矩阵:")
        for j in range(k):
            # 哪些服务=1?
            deployed_svcs = np.where(indiv[j] == 1)[0]
            print(f"  Server {j} => 服务 {deployed_svcs.tolist()}")


from LocalSearch.service_selection_strategies import (
    random_service_deployment,
    greedy_service_deployment_by_cost,
    greedy_service_deployment_by_request
)


###############################################################
# 主函数示例 (可以在你自己的 main.py 里调用)
###############################################################
if __name__ == "__main__":
    # ========== 你可在这里导入 main.py 里生成的输入数据: ==========

    # 1) 服务器位置 (k个索引)
    #    - 先运行局部搜索 => best_solution
    #    - best_solution 是 [idx1, idx2, ... idxK]
    #    - selected_positions = candidate_positions[best_solution]
    # 2) user_positions, user_services, assigned_server

    # 这里仅做示例:
    from main import (
        candidate_positions,
        user_positions,
        user_services,
        coverage_local_search,
        assign_users_to_stations,
        N2,
        compare_station_selection_methods,
        load_input_from_excel
    )

    random.seed(42)##原本有个这个 不知道有没有用
    # random.seed(20)
    # Suppose we do coverage_local_search => best_sol
        # 先假定 k = N2
    k_val = N2
    best_sol, best_cost, _ = coverage_local_search(
        candidate_positions,
        user_positions,
        k_val,
        coverage_radius=1.5,
        # coverage_radius=1.0,
        max_iter=200
    )
    # 选中服务器位置:
    selected_positions = candidate_positions[best_sol]  # shape(k,2)

    # 为每个用户分配 nearest from best_sol
    assignment = assign_users_to_stations(user_positions, candidate_positions, best_sol)

    print(f"局部搜索后服务器: {best_sol}, cost= {best_cost}")
    print("用户首选服务器(assignment):", assignment[:10], "...")

    strategies = {
        "random": os.path.join(PROJECT_ROOT, "output/npz/res_random.npz"),
        "greedy_cost": os.path.join(PROJECT_ROOT, "output/npz/res_greedy_cost.npz"),
        "greedy_request": os.path.join(PROJECT_ROOT, "output/npz/res_greedy_request.npz"),
        "hybrid-A-1": os.path.join(PROJECT_ROOT, "output/npz/res_hybrid-A-1.npz"),
        # "hybrid": os.path.join(PROJECT_ROOT, "output/npz/res_hybrid.npz"),
        # "hybrid-A": os.path.join(PROJECT_ROOT, "output/npz/res_hybrid-A.npz"),
        # "hybrid-B": os.path.join(PROJECT_ROOT, "output/npz/res_hybrid-B.npz"),
        # "hybrid-C": os.path.join(PROJECT_ROOT, "output/npz/res_hybrid-C.npz"),
    }

    for mode, filename in strategies.items():
        print(f"\n🚀 正在运行初始化策略：{mode}")
        algorithm = NSGA2(
            pop_size=50,
            # pop_size=60,
            # pop_size=20,
            sampling=ServiceSampling(mode),
            repair=ServiceRepair(),
            eliminate_duplicates=True
        )
        problem = MyServiceDeployProblem(
            k=len(best_sol),
            servers_pos=selected_positions,
            user_positions=user_positions,
            user_services=user_services,
            assigned_server=assignment
        )
        termination = get_termination("n_gen", 200)
        res = minimize(
            problem,
            algorithm,
            termination,
            seed=42,
            # seed=20,
            save_history=True,
            verbose=False
        )
        np.savez(filename, X=res.X, F=res.F)
        print(f"✅ 已保存：{filename}")



