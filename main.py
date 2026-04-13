import os
import numpy as np
import random
import math
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.ticker as ticker
import matplotlib.pyplot as plt
from matplotlib import image as mpimg
from matplotlib.patches import Circle
import matplotlib.ticker as mticker

# 项目根目录（main.py 所在目录），确保无论从哪里运行都能找到文件
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# ========== 来自你的新版本 compute_delay.py 的导入 ==========
# 注意：根据你在 compute_delay.py 中定义的函数/常量灵活调整
from LocalSearch.compute_delay import (
    haversine_distance,
    compute_user_delay,
    total_delay,
    total_delay_breakdown,
    DEFAULT_CAPACITY,
    DEFAULT_TX_RATE,
    THRESHOLD_DISTANCE,
    COMM_PENALTY_FACTOR
)

# plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['font.family'] = 'Arial'
plt.rcParams['axes.unicode_minus'] = False

# 全局系数，将 km 转换为费用单位
COST_PER_KM = 20  # 每公里通信代价 20 元
# 惩罚因子，单位：元/km（表示用户超出服务范围时，每增加 1 km 的额外成本）
PENALTY_FACTOR = 10


# ------------------------------
# Haversine公式：计算两个经纬度点之间的距离（单位：km）
def haversine_distance(lon1, lat1, lon2, lat2):
    # 将度转为弧度
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    km = 6371 * c  # 地球半径约6371 km
    return km



def load_input_from_excel(path="data/input_data.xlsx"):
    path = os.path.join(PROJECT_ROOT, path)
    # 加载服务器位置
    df_candidates = pd.read_excel(path, sheet_name="candidates")
    candidate_positions = df_candidates.to_numpy()

    # 加载用户位置
    df_users = pd.read_excel(path, sheet_name="users")
    user_positions = df_users.to_numpy()

    # 加载服务类型
    df_services = pd.read_excel(path, sheet_name="services")
    user_services = df_services.to_numpy().flatten().astype(int)

    return candidate_positions, user_positions, user_services

candidate_positions, user_positions, user_services = load_input_from_excel("data/input_data_10_130_8_new.xlsx")
# 示例写入



# # 为绘图定义颜色：共8种颜色
service_colors = ['blue', 'green', 'red', 'orange', 'purple', 'brown', 'cyan', 'magenta']


# 绘图时新函数：根据用户服务类别上色
def plot_users_with_services(user_positions, user_services, user_size=20):
    for i, pos in enumerate(user_positions):
        plt.scatter(
            pos[0], pos[1],
            color=service_colors[user_services[i] % len(service_colors)],
            s=user_size, alpha=0.7
        )

# 定义16种颜色
# service_colors = [
#     'blue', 'green', 'red', 'orange', 'purple', 'brown', 'cyan', 'magenta',
#     'pink', 'olive', 'teal', 'lime', 'navy', 'gold', 'darkred', 'gray'
# ]
#
# # 用户绘图函数：根据服务类别染色
# def plot_users_with_services(user_positions, user_services, user_size=20):
#     for i, pos in enumerate(user_positions):
#         plt.scatter(
#             pos[0], pos[1],
#             color=service_colors[user_services[i] % len(service_colors)],
#             s=user_size, alpha=0.7
#         )


def compute_density_for_stations(candidate_positions, user_positions, coverage_radius=1, sigma_min=5):
    """
    对每个候选基站，以其为中心，计算服务范围（单位：km）内的用户数量，
    若该数量大于等于 sigma_min，则认为该候选基站满足密度要求。

    参数：
      candidate_positions: ndarray，形状 (n, 2)，候选基站经纬度（单位：度）
      user_positions: ndarray，形状 (m, 2)，用户经纬度（单位：度）
      service_range: 服务范围，单位 km
      sigma_min: 密度阈值，要求该服务范围内至少有 sigma_min 个用户

    返回：
      active_indices: 满足密度要求的候选基站索引列表（N₂）
      densities: 每个候选基站在服务范围内的用户数列表
      N2: 满足密度要求的基站数
    """
    active_indices = []
    densities = []
    for idx, station in enumerate(candidate_positions):
        count = 0
        for user in user_positions:
            d = haversine_distance(station[0], station[1], user[0], user[1])
            if d <= coverage_radius:
                count += 1
        densities.append(count)
        if count >= sigma_min:
            active_indices.append(idx)
    N2 = len(active_indices)
    return active_indices, densities, N2


sigma_min = 5
grid_size = 0.01
# 这里改检测密度函数的阈值
active_indices, densities, N2 = compute_density_for_stations(candidate_positions, user_positions, coverage_radius=1.5,
                                                             sigma_min=16)
# 基站10，用户300.密度阈值sigma_min设为30时，K值为9，不合适，这里加1变成10方便比较;基站10，用户180，sigma_min为22，k能取到10,正好;基站10，用户100，sigma_min为12，k能取到10,正好;
# 基站10,用户150，sigma_min为18，减1,k能取10;基站10,用户160，sigma_min为20，k能取10;基站10,用户200，sigma_min为24，加1,k能取10;基站10,用户210，sigma_min为24，减1,k能取10;
# 基站10,用户130，sigma_min为16，减1,k能取10;
# 基站5,用户130，sigma_min为15，减1,k能取5;
# 基站15,用户130，sigma_min为17，k能取15;
# 基站20,用户130，sigma_min为17，k能取15;
# N2=N2+1
# 基站20，用户180.密度阈值sigma_min设为22时，K值为21，不合适，这里减1变成20方便比较;基站20,用户300，sigma_min为29，减1,k能取20
# 基站20，用户150.密度阈值sigma_min设为20时，K值为19,不合适，加1变成20；基站20，用户130.密度阈值sigma_min设为18时，K值为20；基站20，用户100.密度阈值sigma_min设为12时，K值为20
N2=N2-1

print("各候选基站的用户密度:", densities)
print("满足密度要求的区域数 N2 =", N2)


# ==================== 计算K ====================
C_max = 20000  # 总预算（元）
C_max = 40000  # 总预算（元）
price = 1000  # 每个基站部署成本（元）
N1 = C_max // price
K = min(N1, N2)
print("N1 =", N1, "   最终选择的 K =", K)


# ============== 3. 修改后的覆盖约束计算与局部搜索（采用实际距离计算） ==============
def haversine_distance(lon1, lat1, lon2, lat2):
    # 将度转换为弧度
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    km = 6371 * c
    return km


# 新计算函数，若某个用户对所有选中基站的距离均超过服务范围，依然加入计算，只是加入了惩罚因子增加了通讯成本
def coverage_compute_cost(solution, user_positions, candidate_positions, coverage_radius=1):
    """
    计算在覆盖约束下的总通信成本:
    - 对于每个用户，计算其到选中基站的最小距离（单位：km）
    - 如果最小距离小于等于 coverage_radius，则认为该用户得到“全覆盖”，通信成本为 0
    - 如果最小距离大于 coverage_radius，则通信成本为 (min_distance) * PENALTY_FACTOR
    - 最终结果乘以 COST_PER_KM，将通信成本换算为费用（元）
    """
    selected_positions = candidate_positions[solution]
    total_cost = 0.0
    num_users = user_positions.shape[0]
    for i in range(num_users):
        user_lon, user_lat = user_positions[i]
        distances = []
        for (lon, lat) in selected_positions:
            d = haversine_distance(user_lon, user_lat, lon, lat)
            distances.append(d)
        distances = np.array(distances)
        min_distance = np.min(distances)
        if min_distance <= coverage_radius:
            cost_for_user = 0  # 在服务范围内，认为通信成本为0
        else:
            # cost_for_user = (min_distance - coverage_radius) * PENALTY_FACTOR
            cost_for_user = min_distance * PENALTY_FACTOR
        total_cost += cost_for_user
    return total_cost * COST_PER_KM


def check_full_coverage(solution, user_positions, candidate_positions, coverage_radius=1):
    """
    检查给定的 solution 是否能使所有用户在候选基站服务范围内。
    若有任一用户到该 solution 中基站的最小距离大于 coverage_radius，则认为不全覆盖，返回 False，否则返回 True。
    """
    for user in user_positions:
        distances = [haversine_distance(user[0], user[1], candidate_positions[j][0], candidate_positions[j][1])
                     for j in solution]
        if np.min(distances) > coverage_radius:
            return False
    return True



def coverage_local_search(candidate_positions, user_positions, k, coverage_radius=1, max_iter=2000):
    num_candidates = candidate_positions.shape[0]
    current_solution = random.sample(range(num_candidates), k)
    current_cost = coverage_compute_cost(current_solution, user_positions, candidate_positions, coverage_radius)
    # print("局部搜索随机cost", current_cost)

    iter_count = 0
    iteration_log = []

    while iter_count < max_iter:
        improved = False

        for i in current_solution:
            for j in range(num_candidates):
                if j in current_solution:
                    continue
                new_solution = current_solution.copy()
                new_solution.remove(i)
                new_solution.append(j)
                new_cost = coverage_compute_cost(new_solution, user_positions, candidate_positions, coverage_radius)

                # 稍微改进一点点就接受，立即跳出
                if new_cost < current_cost * 0.999:
                    current_solution = new_solution
                    current_cost = new_cost
                    improved = True
                    iteration_log.append({
                        'iter': iter_count,
                        'cost': current_cost,
                        'solution': current_solution.copy()
                    })
                    print(f"Iteration {iter_count}: New cost = {current_cost:.4f}")
                    break
            if improved:
                break

        if not improved:
            break  # 没有任何改进就结束
        iter_count += 1

    return current_solution, current_cost, iteration_log

def assign_users_to_stations(user_positions, candidate_positions, solution):
    """
    对每个用户，根据局部搜索得到的基站方案 solution，
    分配到最近的基站，返回一个列表 assignment，其长度与用户数相同，
    assignment[i] 表示第 i 个用户在过滤后的基站数组（candidate_positions[solution]）中的索引。
    """
    assignment = []
    selected_positions = candidate_positions[solution]
    for user in user_positions:
        distances = [haversine_distance(user[0], user[1], station[0], station[1])
                     for station in selected_positions]
        # 选择最小距离对应的局部索引（0到len(solution)-1）
        idx = int(np.argmin(distances))
        assignment.append(idx)
    return assignment


# ============== 4. 绘图函数：绘制最终解 ==============
def plot_final_solution(k, best_solution, best_cost, coverage_radius, feasible):

    plt.figure(figsize=(8, 7))
    # === 加载背景图 ===
    bg_img = mpimg.imread(os.path.join(PROJECT_ROOT, "assets/background.jpg"))
    min_lon = np.min(np.concatenate((candidate_positions[:, 0], user_positions[:, 0]))) - 0.005
    max_lon = np.max(np.concatenate((candidate_positions[:, 0], user_positions[:, 0]))) + 0.005
    min_lat = np.min(np.concatenate((candidate_positions[:, 1], user_positions[:, 1]))) - 0.005
    max_lat = np.max(np.concatenate((candidate_positions[:, 1], user_positions[:, 1]))) + 0.005
    plt.imshow(bg_img, extent=[min_lon, max_lon, min_lat, max_lat], aspect='auto', zorder=0, alpha=0.6)

    # 标题，可根据需要修改
    # title_text = "Distribution Map"
    # plt.title(title_text, fontsize=16)  # 标题字体加大

    # X/Y 轴标签 & 刻度
    # plt.xlabel("纬度", fontsize=14)
    # plt.ylabel("经度", fontsize=14)
    # plt.tick_params(axis='both', which='major', labelsize=12)  # X/Y 轴刻度字体
    plt.xticks(rotation=0, ha='right', fontsize=16)
    plt.yticks(rotation=0, fontsize=16)
    plt.xlabel("Longitude", fontname='Arial', fontsize=17)
    plt.ylabel("Latitude", fontname='Arial', fontsize=17)
    plt.grid(True, axis='y', linestyle='--', linewidth=0.75)

    # plt.grid(True)

    # ---------- 绘制候选基站 ----------
    # 思路：先画“未被选中”的灰色基站和黑色标号，然后单独画被选中的
    for i, pos in enumerate(candidate_positions):
        if i not in best_solution:
            # 未选中的基站用灰色圆点 + 黑色小字体
            plt.scatter(pos[0], pos[1], c='gray', s=40, alpha=0.6)  # 候选基站略微大一点
            plt.text(pos[0], pos[1], str(i), fontsize=9, color='black', alpha=0.7)
    # 再在后面画“被选中的基站”
    selected_positions = candidate_positions[best_solution] if best_solution is not None else []
    for idx_sol in best_solution:
        bx, by = candidate_positions[idx_sol]
        # 用红色五角星表示选中基站, 大小加大
        plt.scatter(bx, by, c='red', marker='*', s=240)
        # 红色标号
        plt.text(bx + 0.0005, by + 0.0005, str(idx_sol), fontsize=12, color='red')

    # ---------- 绘制用户 ----------
    # 绘制用户（使用你的 plot_users_with_services）
    # 让用户点的大小也更大一些 s=40
    plot_users_with_services(user_positions, user_services, user_size=50)

    # ----- “哑元”散点：图例显示不同用户类别 -----
    num_classes = 8
    for cls_idx in range(num_classes):
        # plt.scatter([], [], color=service_colors[cls_idx], label=f"s {cls_idx}")
        plt.scatter([], [], color=service_colors[cls_idx], label=f"$s_{{{cls_idx}}}$")

    # ---------- 画覆盖圆 ----------
    ax = plt.gca()
    # 让 X 轴、Y 轴都以 0.01 为刻度间隔
    ax.xaxis.set_major_locator(mticker.MultipleLocator(0.02))
    ax.yaxis.set_major_locator(mticker.MultipleLocator(0.02))

    plot_radius = coverage_radius / 111.0
    if best_solution is not None:
        for idx_sol in best_solution:
            bx, by = candidate_positions[idx_sol]
            circle = Circle((bx, by), plot_radius, fill=False,
                            edgecolor='red', linestyle='--', alpha=0.5)
            ax.add_patch(circle)

    # ---------- 若可行，连线用户 -> 最近基站 ----------
    if feasible and best_solution is not None:
        for i in range(user_positions.shape[0]):
            ux, uy = user_positions[i]
            dists = np.array([
                haversine_distance(ux, uy, candidate_positions[j][0], candidate_positions[j][1])
                for j in best_solution
            ])
            assigned_index = np.argmin(dists)
            bx, by = candidate_positions[best_solution[assigned_index]]
            plt.plot([ux, bx], [uy, by], c='gray', alpha=0.4, linewidth=0.5)

    # plt.legend(loc='upper left', ncol=2)
    # plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05), ncol=8, fontsize=12)
    plt.legend(
        loc='upper center',
        bbox_to_anchor=(0.5, 1.0),
        ncol=8,
        fontsize=10,
        handletextpad=0.3,
        columnspacing=0.8,
        borderaxespad=0.2
    )

    plt.subplots_adjust(top=0.88)

    # 调整显示范围
    all_lons = np.concatenate((candidate_positions[:, 0], user_positions[:, 0]))
    all_lats = np.concatenate((candidate_positions[:, 1], user_positions[:, 1]))
    plt.xlim(np.min(all_lons) - 0.005, np.max(all_lons) + 0.005)
    plt.ylim(np.min(all_lats) - 0.005, np.max(all_lats) + 0.005)

    # 避免科学计数
    plt.ticklabel_format(useOffset=False, style='plain')
    # plt.savefig(os.path.join(PROJECT_ROOT, 'output/pdf/trace_data.pdf'), format='pdf', bbox_inches='tight')
    plt.show()



# ============== 5. 多 K 对比实验 ==============
def multi_k_experiment(k_values, coverage_radius=1):
    results = []
    for k in k_values:
        best_solution, best_cost, iteration_log = coverage_local_search(
            candidate_positions, user_positions, k, coverage_radius=coverage_radius, max_iter=300
        )

        # 检查是否全覆盖（即所有用户至少有一个基站在覆盖半径内）
        full_coverage = check_full_coverage(best_solution, user_positions, candidate_positions, coverage_radius)
        if not full_coverage:
            print(f"警告：对于 K={k} 的解，部分用户不在全覆盖范围内！")
        # 这个If不会是以前做的，不会输出，但是注释掉会改变代码结构导致不能执行，先这样放着
        if best_cost == float('inf'):
            print(f"\nK={k} 时无法覆盖所有用户, 不可行.")
        else:
            import matplotlib.pyplot as plt
            import matplotlib.ticker as ticker

            if iteration_log:
                iters = [item['iter'] for item in iteration_log]
                costs = [item['cost'] for item in iteration_log]

                fig, ax = plt.subplots()
                ax.plot(iters, costs, marker='^', linestyle='-', color='#1f77ff', markersize=10)

                ax.set_xlabel("# of iterations", fontname='Arial', fontsize=17)
                ax.set_ylabel(r"transmission cost", fontname='Arial', fontsize=17)
                ax.tick_params(axis='both', labelsize=16)

                # 设置 y 轴科学计数法为 ×10³，并手动添加标签
                formatter = ticker.ScalarFormatter(useMathText=True)
                formatter.set_scientific(True)
                formatter.set_powerlimits((3, 3))
                ax.yaxis.set_major_formatter(formatter)

                # 隐藏默认 ×10³ 显示
                ax.yaxis.get_offset_text().set_visible(False)

                # 添加竖直的 ×10³ 到 y 轴 label 后面
                ax.annotate(r'$\times 10^3$',
                            xy=(0, 1), xycoords='axes fraction',
                            xytext=(-25, 10), textcoords='offset points',
                            rotation=90, fontsize=15, va='bottom')

                ax.grid(True, axis='y', linestyle='--', linewidth=0.75)
                plt.savefig(os.path.join(PROJECT_ROOT, 'output/pdf/iteration_data.pdf'), format='pdf', bbox_inches='tight')
                plt.show()

            # if iteration_log:
            #     iters = [item['iter'] for item in iteration_log]
            #     costs = [item['cost'] for item in iteration_log]
            #     plt.figure()
            #     plt.plot(iters, costs, marker='^', linestyle='-', color='#1f77ff', markersize=10)
            #     # plt.plot(iters, costs, marker='o', linestyle='-')
            #     # plt.title(f"Local Search Optimization Process (K={k}, Coverage Radius={coverage_radius} km)")
            #     # plt.title(f"Local Search Optimization Process")
            #     # plt.xlabel("# of iterations")
            #     # plt.ylabel("Communication Cost")
            #     plt.xticks(rotation=0, ha='right', fontsize=16)
            #     plt.yticks(rotation=0, fontsize=16)
            #     plt.xlabel("# of iterations", fontname='Arial', fontsize=17)
            #     plt.ylabel("transmission cost", fontname='Arial', fontsize=17)
            #     # 设置 y 轴刻度为以千为单位
            #     plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x / 1000)}×10³'))
            #     # plt.grid(True)
            #     plt.grid(True, axis='y', linestyle='--', linewidth=0.75)
            #     plt.show()
            else:
                print(f"\nK={k} 可行，但局部搜索没有进行任何有效交换。")

            # 自动分配用户到最近基站，并计算延迟
            assignment = assign_users_to_stations(user_positions, candidate_positions, best_solution)

            # 调用新的 total_delay_breakdown，其中增加了 user_services
            total_compute_delay, total_comm_delay, total_delay_value, breakdown = total_delay_breakdown(
                user_positions,
                candidate_positions[best_solution],
                assignment,
                user_service_types=user_services,  # <-- 传入用户服务类型
                capacity=DEFAULT_CAPACITY,
                tx_rate=DEFAULT_TX_RATE,
                threshold=THRESHOLD_DISTANCE,
                comm_penalty_factor=COMM_PENALTY_FACTOR
            )
            print(
                f"K={k} 下，总计算延迟: {total_compute_delay:.4f} 秒, 总通信延迟: {total_comm_delay:.4f} 秒, 总延迟: {total_delay_value:.4f} 秒")
        feasible = (best_cost != float('inf'))
        deploy_cost = k * 1000  # 假设每个基站部署成本 1000 元
        total_cost = float('inf')
        if feasible:
            total_cost = 0.4*deploy_cost + 0.6*best_cost
        results.append({
            'K': k,
            'Feasible': feasible,
            'DeployCost': deploy_cost,
            'CommCost': best_cost if feasible else None,
            'TotalCost': total_cost if feasible else None,
            'ComputeDelay': total_compute_delay,
            'CommDelay': total_comm_delay,
            'TotalDelay': total_delay_value,
            'Solution': best_solution,
            'Assignment': assignment
        })
        # 绘制最终解图，不论是否可行
        plot_final_solution(k, best_solution, best_cost, coverage_radius, feasible)
    # 对所有可行结果归一化，使用平滑参数 c
    feasible_results = [r for r in results if r['Feasible']]
    c = 1  # 平滑参数，可以根据需要调整
    if feasible_results:
        deploy_costs = np.array([r['DeployCost'] for r in feasible_results])
        comm_costs = np.array([r['CommCost'] for r in feasible_results])
        max_deploy = deploy_costs.max()
        max_comm = comm_costs.max()
        for idx, r in enumerate(feasible_results):
            norm_deploy = (r['DeployCost'] + c) / (max_deploy + c)
            norm_comm = (r['CommCost'] + c) / (max_comm + c)
            r['NormDeployCost'] = norm_deploy
            r['NormCommCost'] = norm_comm
            r['WeightedTotalCost'] = 0.77 * norm_deploy + 0.23 * norm_comm
    # 打印结果表
    print("\n=== 多 K 对比实验结果 ===")
    print(
        "K | Feasible | DeployCost | CommCost | TotalCost | ComputeDelay | CommDelay | TotalDelay | NormDeploy | NormComm | WeightedTotal")
    for r in results:
        if r['Feasible']:
            norm_deploy = r.get('NormDeployCost', 0)
            norm_comm = r.get('NormCommCost', 0)
            weighted = r.get('WeightedTotalCost', 0)
            print(
                f"{r['K']} | Yes      | {r['DeployCost']}       | {r['CommCost']:.4f} | {r['TotalCost']:.4f} | {r['ComputeDelay']:.4f} | {r['CommDelay']:.4f} | {r['TotalDelay']:.4f} | {norm_deploy:.4f} | {norm_comm:.4f} | {weighted:.4f}")
        else:
            print(
                f"{r['K']} | No       | {r['DeployCost']}       |  --      |  --         |  --      |  --      |  --         |  --     |  --     |  --")
    return results


# 导入刚刚我们实现的策略函数
from LocalSearch.station_selection_strategies import (
    random_selection,
    density_based_selection,
    distance_sum_selection,
    # coverage_compute_cost,
    greedy_k_selection
)


def compare_station_selection_methods(k, coverage_radius=1.5):
    """
    对比四种方法(随机选取/基于用户密度/基于距离和/贪心选择)在给定K值下的性能:
      1) 选出的基站方案 => coverage_compute_cost => 赋值 => total_delay_breakdown => plot
    """
    print(f"\n=== 对比四种基站选取方法 (K={k}) ===")

    # ============ 1) Random Selection ============
    sol_random = random_selection(candidate_positions, user_positions, k)
    cost_random = coverage_compute_cost(sol_random, user_positions, candidate_positions, coverage_radius)
    assignment_random = assign_users_to_stations(user_positions, candidate_positions, sol_random)
    tcomp_random, tcomm_random, tdelay_random, bdown_random = total_delay_breakdown(
        user_positions,
        candidate_positions[sol_random],
        assignment_random,
        user_service_types=user_services,
        capacity=DEFAULT_CAPACITY,
        tx_rate=DEFAULT_TX_RATE,
        threshold=THRESHOLD_DISTANCE,
        comm_penalty_factor=COMM_PENALTY_FACTOR
    )
    plot_final_solution(k, sol_random, cost_random, coverage_radius, feasible=True)
    print(f"[Random] CommCost={cost_random:.4f}, ComputeDelay={tcomp_random:.4f}, CommDelay={tcomm_random:.4f}, TotalDelay={tdelay_random:.4f}")

    # ============ 2) Density-based Selection ============
    sol_density = density_based_selection(candidate_positions, user_positions, k, coverage_radius=coverage_radius)
    cost_density = coverage_compute_cost(sol_density, user_positions, candidate_positions, coverage_radius)
    assignment_density = assign_users_to_stations(user_positions, candidate_positions, sol_density)
    tcomp_density, tcomm_density, tdelay_density, bdown_density = total_delay_breakdown(
        user_positions,
        candidate_positions[sol_density],
        assignment_density,
        user_service_types=user_services,
        capacity=DEFAULT_CAPACITY,
        tx_rate=DEFAULT_TX_RATE,
        threshold=THRESHOLD_DISTANCE,
        comm_penalty_factor=COMM_PENALTY_FACTOR
    )
    plot_final_solution(k, sol_density, cost_density, coverage_radius, feasible=True)
    print(f"[Density] CommCost={cost_density:.4f}, ComputeDelay={tcomp_density:.4f}, CommDelay={tcomm_density:.4f}, TotalDelay={tdelay_density:.4f}")

    # ============ 3) Distance-sum Selection ============
    sol_dist = distance_sum_selection(candidate_positions, user_positions, k)
    cost_dist = coverage_compute_cost(sol_dist, user_positions, candidate_positions, coverage_radius)
    assignment_dist = assign_users_to_stations(user_positions, candidate_positions, sol_dist)
    tcomp_dist, tcomm_dist, tdelay_dist, bdown_dist = total_delay_breakdown(
        user_positions,
        candidate_positions[sol_dist],
        assignment_dist,
        user_service_types=user_services,
        capacity=DEFAULT_CAPACITY,
        tx_rate=DEFAULT_TX_RATE,
        threshold=THRESHOLD_DISTANCE,
        comm_penalty_factor=COMM_PENALTY_FACTOR
    )
    plot_final_solution(k, sol_dist, cost_dist, coverage_radius, feasible=True)
    print(f"[DistSum] CommCost={cost_dist:.4f}, ComputeDelay={tcomp_dist:.4f}, CommDelay={tcomm_dist:.4f}, TotalDelay={tdelay_dist:.4f}")

    # ============ 4) Greedy K Selection ============
    sol_greedy = greedy_k_selection(user_positions, candidate_positions, k)
    cost_greedy = coverage_compute_cost(sol_greedy, user_positions, candidate_positions, coverage_radius)
    assignment_greedy = assign_users_to_stations(user_positions, candidate_positions, sol_greedy)
    tcomp_greedy, tcomm_greedy, tdelay_greedy, bdown_greedy = total_delay_breakdown(
        user_positions,
        candidate_positions[sol_greedy],
        assignment_greedy,
        user_service_types=user_services,
        capacity=DEFAULT_CAPACITY,
        tx_rate=DEFAULT_TX_RATE,
        threshold=THRESHOLD_DISTANCE,
        comm_penalty_factor=COMM_PENALTY_FACTOR
    )
    plot_final_solution(k, sol_greedy, cost_greedy, coverage_radius, feasible=True)
    print(f"[Greedy] CommCost={cost_greedy:.4f}, ComputeDelay={tcomp_greedy:.4f}, CommDelay={tcomm_greedy:.4f}, TotalDelay={tdelay_greedy:.4f}")



# ============== 7. 主函数 ==============
if __name__ == "__main__":
    random.seed(42)  # 固定随机种子

    # (A) 多 K 对比实验：比较不同 K 值的结果
    # k_candidates = [8, 9, 10, 11, 12, 20]
    # k_candidates = [N2 - 2, N2 - 1, N2, N2 + 1, N2 + 2,N1]
    k_candidates = [N2]
    multi_k_results = multi_k_experiment(k_candidates, coverage_radius=1.5)
    # multi_k_results = multi_k_experiment(k_candidates, coverage_radius=1.0)#调小了

    # compare_station_selection_methods(K, coverage_radius=1.5)

    # final_pop 里保存最后一代个体(部署策略)及其 cost, delay
    # 你可进行非支配解提取, 画pareto front, 也可以多代记录

    # (B) 记录局部搜索迭代过程 + 最终解可视化 ( K=10)
    # iteration_record_experiment(k=10, coverage_radius=2)

    # best_solution = nsga2(N2, user_positions, candidate_positions, coverage_radius=1.5)

    # print("优化后的基站配置方案：", best_solution)
