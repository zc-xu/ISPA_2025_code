# coverage_local_search.py

import numpy as np
import random
import math


def coverage_compute_cost(solution, user_positions, candidate_positions, coverage_radius=0.009):
    """
    计算在覆盖约束下的总距离:
    - 若某个用户对所有已选基站都超过 coverage_radius, 则返回 inf 表示不可行
    - 否则返回所有用户到其最近可行基站的距离之和
    """
    selected_positions = candidate_positions[solution]  # shape: (k, 2)
    num_users = user_positions.shape[0]

    total_cost = 0.0
    for i in range(num_users):
        # 计算用户 i 到所有选中基站的距离
        dists = np.linalg.norm(user_positions[i] - selected_positions, axis=1)
        # 只保留 <= coverage_radius 的距离
        feasible_dists = dists[dists <= coverage_radius]

        if len(feasible_dists) == 0:
            # 没有任何基站能覆盖用户 i，解不可行
            return float('inf')
        else:
            total_cost += np.min(feasible_dists)

    return total_cost


def coverage_local_search(candidate_positions, user_positions, k, coverage_radius=0.009, max_iter=1000):
    """
    带覆盖约束的局部搜索:
    - 若交换后出现不可行解( cost=inf ), 则不接受该交换
    - 记录每次迭代成功交换时的 cost, coverage 等信息
    """
    num_candidates = candidate_positions.shape[0]
    # 随机选 k 个基站
    current_solution = random.sample(range(num_candidates), k)
    current_cost = coverage_compute_cost(current_solution, user_positions, candidate_positions, coverage_radius)

    improved = True
    iter_count = 0

    # 用于记录每次成功交换后的信息
    iteration_log = []

    while improved and iter_count < max_iter:
        improved = False
        best_swap_cost = current_cost
        best_swap = None

        for i in current_solution:
            for j in range(num_candidates):
                if j in current_solution:
                    continue
                new_solution = current_solution.copy()
                new_solution.remove(i)
                new_solution.append(j)
                new_cost = coverage_compute_cost(new_solution, user_positions, candidate_positions, coverage_radius)

                if new_cost < best_swap_cost:
                    best_swap_cost = new_cost
                    best_swap = (i, j)

        if best_swap is not None:
            current_solution.remove(best_swap[0])
            current_solution.append(best_swap[1])
            current_cost = best_swap_cost
            improved = True

            # 记录日志
            iteration_log.append({
                'iter': iter_count,
                'cost': current_cost,
                'solution': current_solution.copy()
            })

            print(f"Iteration {iter_count}: New cost = {current_cost:.4f}")

        iter_count += 1

    return current_solution, current_cost, iteration_log
