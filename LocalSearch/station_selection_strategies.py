# station_selection_strategies.py

import numpy as np
import random
import math

#############################
#  需要用到的一些外部函数或常量
#############################

# 视情况而定，你可以在这里再定义 coverage_compute_cost,
# 或者从你的 main.py / compute_delay.py 中 import。
# 为避免循环引用，这里直接贴出来：
PENALTY_FACTOR = 10
COST_PER_KM = 20

def haversine_distance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371.0 * c

def coverage_compute_cost(solution, user_positions, candidate_positions, coverage_radius=1.5):
    """
    从 main.py 中复制过来的版本:
    计算在覆盖约束下的总通信成本:
    - 对于每个用户, 计算其到选中基站的最小距离
    - 若 min_dist <= coverage_radius => 通信成本=0
      否则 => (min_dist)*PENALTY_FACTOR
    - 最后乘以 COST_PER_KM
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
        min_distance = min(distances)
        if min_distance <= coverage_radius:
            cost_for_user = 0.0
        else:
            cost_for_user = min_distance * PENALTY_FACTOR
        total_cost += cost_for_user
    return total_cost * COST_PER_KM


#############################
#       三种选取策略
#############################

def random_selection(candidate_positions, user_positions, k):
    """
    1) 随机从 candidate_positions 中选 k 个基站
    返回: solution(list), 表示所选基站索引
    """
    num_candidates = candidate_positions.shape[0]
    selected = random.sample(range(num_candidates), k)
    return selected

def density_based_selection(candidate_positions, user_positions, k, coverage_radius=1.5):
    """
    2) 基于用户密度的贪心策略:
       - 先统计每个基站在 coverage_radius 范围内包含多少用户
       - 然后选取密度最高的前 k 个基站
    """
    num_candidates = candidate_positions.shape[0]
    densities = []
    for idx in range(num_candidates):
        station = candidate_positions[idx]
        count = 0
        for user in user_positions:
            d = haversine_distance(station[0], station[1], user[0], user[1])
            if d <= coverage_radius:
                count += 1
        densities.append((idx, count))
    # 按照 count 从大到小排序
    densities.sort(key=lambda x: x[1], reverse=True)
    selected = [item[0] for item in densities[:k]]
    return selected

def distance_sum_selection(candidate_positions, user_positions, k):
    """
    3) 基于“总距离”贪心策略:
       - 对每个基站, 计算其与所有用户的距离之和(或者是加权之和)
       - 排序后选出总距离最小的前 k (因为希望该基站离用户越近越好)
         也可以反过来: 先算总距离, 排序后选  k  "最小"即可
    """
    num_candidates = candidate_positions.shape[0]
    dist_sums = []
    for idx in range(num_candidates):
        station = candidate_positions[idx]
        sum_dist = 0.0
        for user in user_positions:
            sum_dist += haversine_distance(station[0], station[1], user[0], user[1])
        dist_sums.append((idx, sum_dist))

    # 按距离和从小到大排序, 取前k
    dist_sums.sort(key=lambda x: x[1])
    selected = [item[0] for item in dist_sums[:k]]
    return selected


def greedy_k_selection(user_positions, candidate_positions, k):
    """
    贪心算法：每次选择一个点，直到选够k个设施
    """
    selected_facilities = []  # 已选设施
    remaining_candidates = np.arange(len(candidate_positions))  # 使用 NumPy 数组的索引来表示剩余候选设施

    for _ in range(k):
        # 计算每个候选设施到所有用户的总距离
        facility_distances = []
        for facility_idx in remaining_candidates:
            facility = candidate_positions[facility_idx]
            total_distance = 0
            for user in user_positions:
                total_distance += np.linalg.norm(np.array(facility) - np.array(user))  # 欧几里得距离
            facility_distances.append((facility_idx, total_distance))

        # 选择那个能最大程度减少总距离的设施
        best_facility_idx, min_distance = min(facility_distances, key=lambda x: x[1])

        # 更新选择的设施
        selected_facilities.append(best_facility_idx)

        # 从剩余候选设施中移除已选择的设施
        remaining_candidates = remaining_candidates[remaining_candidates != best_facility_idx]  # 使用索引过滤

    return selected_facilities
