# service_selection_strategies.py

import numpy as np
import random

# 引入 NSGA-II 中用到的常量和函数（假设 compute_delay.py 中已定义）
from compute_delay import (
    SERVICE_DEPLOY_COSTS,         # 例如 [100, 120, 80, ...]
    SERVICE_CAPACITY_PER_SERVER,  # 每台服务器最多可部署的服务数（如 3）
    SERVICE_WORKLOADS,            # 各类服务的计算量
    SERVICE_DATA_SIZES,           # 各类服务对应的数据量
    DEFAULT_CAPACITY,
    DEFAULT_TX_RATE,
    THRESHOLD_DISTANCE,
    COMM_PENALTY_FACTOR,
    haversine_distance
)

# --------------------------
# 辅助函数：计算部署矩阵的总体目标（成本与延迟）
# --------------------------
def compute_objectives(deployment, servers_pos, user_positions, user_services, assigned_server):
    """
    输入:
       deployment: (k, 8) 0/1 部署矩阵
       servers_pos: (k,2) 服务器位置
       user_positions: (m,2)
       user_services: (m,) 每个用户携带的服务类型
       assigned_server: (m,) 用户首选服务器索引
    输出:
       cost, delay, 其中 cost = 部署成本 + 通信成本，delay 为用户总延迟
    """
    k, num_services = deployment.shape

    # （A）计算部署成本: 累加每个服务器上部署的服务成本
    deploy_cost = 0.0
    for j in range(k):
        for svc in range(num_services):
            if deployment[j, svc] == 1:
                deploy_cost += SERVICE_DEPLOY_COSTS[svc]

    # （B）计算每个用户的通信成本及延迟
    total_comm_cost = 0.0
    total_delay = 0.0
    for u, upos in enumerate(user_positions):
        svc_type = user_services[u]
        prime_srv = assigned_server[u]
        dist = haversine_distance(upos[0], upos[1],
                                  servers_pos[prime_srv][0],
                                  servers_pos[prime_srv][1])
        if deployment[prime_srv, svc_type] == 1:
            # 如果首选服务器部署了该服务
            dist = haversine_distance(upos[0], upos[1],
                                      servers_pos[prime_srv][0],
                                      servers_pos[prime_srv][1])
            if dist <= THRESHOLD_DISTANCE:
                comm_cost_u = 0.0
            else:
                comm_cost_u = dist * COMM_PENALTY_FACTOR
            delay_u = compute_user_delay_ex(upos, prime_srv, svc_type, servers_pos)
        else:
            # 否则，寻找部署该服务的最近服务器
            best_j, best_dist = find_nearest_server_with_service(upos, svc_type, deployment, servers_pos)
            if best_j is None:
                # comm_cost_u = 999999.0
                comm_cost_u = dist * k * COMM_PENALTY_FACTOR
                # delay_u = 999999.0
                delay_u = compute_user_delay_ex(upos, prime_srv, svc_type, servers_pos) * k
            else:
                comm_cost_u = best_dist * 1.0
                delay_u = compute_user_delay_ex(upos, best_j, svc_type, servers_pos)
        total_comm_cost += comm_cost_u
        total_delay += delay_u

    cost = deploy_cost + total_comm_cost
    # cost = deploy_cost
    delay = total_delay
    return cost, delay

def compute_user_delay_ex(user_pos, srv_idx, svc_type, servers_pos):
    """
    根据用户与服务器之间的距离计算用户延迟：包含计算延迟与通信延迟
    """
    dist = haversine_distance(user_pos[0], user_pos[1],
                              servers_pos[srv_idx][0],
                              servers_pos[srv_idx][1])
    compute_delay = SERVICE_WORKLOADS[svc_type] / DEFAULT_CAPACITY
    if dist <= THRESHOLD_DISTANCE:
        comm_delay = 0.0
    else:
        data_size = SERVICE_DATA_SIZES[svc_type]
        base_time = data_size / DEFAULT_TX_RATE
        comm_delay = base_time * COMM_PENALTY_FACTOR * dist
    return compute_delay + comm_delay

def find_nearest_server_with_service(user_pos, svc_type, deployment, servers_pos):
    """
    在部署矩阵中找到部署了 svc_type 服务的、与用户位置最近的服务器，
    返回 (服务器索引, 距离)；若没有则返回 (None, None)
    """
    min_dist = 1e9
    best_j = None
    for j in range(deployment.shape[0]):
        if deployment[j, svc_type] == 1:
            dist = haversine_distance(user_pos[0], user_pos[1],
                                      servers_pos[j][0],
                                      servers_pos[j][1])
            if dist < min_dist:
                min_dist = dist
                best_j = j
    if best_j is None:
        return None, None
    else:
        return best_j, min_dist

# --------------------------
# 策略1：随机服务部署
# --------------------------
def random_service_deployment(servers_pos, user_positions, user_services, assigned_server):
    """
    为每个服务器随机生成一组 0/1 部署方案，确保每台服务器中 1 的个数不超过 SERVICE_CAPACITY_PER_SERVER。
    返回：(部署矩阵, cost, delay, weighted_value)
    """
    k = len(servers_pos)
    # num_services = 8
    num_services = len(SERVICE_DEPLOY_COSTS)
    deployment = np.random.randint(0, 2, size=(k, num_services))
    for j in range(k):
        ones = np.where(deployment[j] == 1)[0]
        while ones.size > SERVICE_CAPACITY_PER_SERVER:
            drop = random.choice(ones)
            deployment[j, drop] = 0
            ones = np.where(deployment[j] == 1)[0]
    cost, delay = compute_objectives(deployment, servers_pos, user_positions, user_services, assigned_server)
    weighted = 0.5 * cost + 0.5 * delay
    return deployment, cost, delay, weighted

# --------------------------
# 策略2：基于服务部署成本贪心策略
# --------------------------
def greedy_service_deployment_by_cost(servers_pos, user_positions, user_services, assigned_server):
    """
    对每个服务器，统计分配到该服务器的用户请求所携带的服务类型（去重后）。
    按照每个服务的部署成本 SERVICE_DEPLOY_COSTS 从低到高排序，
    然后选取最便宜的 SERVICE_CAPACITY_PER_SERVER 个服务进行部署。
    返回：(部署矩阵, cost, delay, weighted_value)
    """
    k = len(servers_pos)
    # num_services = 8
    num_services = len(SERVICE_DEPLOY_COSTS)
    deployment = np.zeros((k, num_services), dtype=int)
    for j in range(k):
        user_indices = [u for u, srv in enumerate(assigned_server) if srv == j]
        requested = set()
        for u in user_indices:
            requested.add(user_services[u])
        requested = list(requested)
        requested.sort(key=lambda svc: SERVICE_DEPLOY_COSTS[svc])
        selected = requested[:SERVICE_CAPACITY_PER_SERVER]
        for svc in selected:
            deployment[j, svc] = 1
    cost, delay = compute_objectives(deployment, servers_pos, user_positions, user_services, assigned_server)
    weighted = 0.5 * cost + 0.5 * delay
    return deployment, cost, delay, weighted

# --------------------------
# 策略3：基于用户请求数的贪心策略
# --------------------------
def greedy_service_deployment_by_request(servers_pos, user_positions, user_services, assigned_server):
    """
    对每个服务器，统计分配到该服务器的用户请求中各服务类型的出现次数，
    选择出现次数最多的 SERVICE_CAPACITY_PER_SERVER 个服务进行部署。
    返回：(部署矩阵, cost, delay, weighted_value)
    """
    k = len(servers_pos)
    # num_services = 8
    num_services = len(SERVICE_DEPLOY_COSTS)
    deployment = np.zeros((k, num_services), dtype=int)
    for j in range(k):
        user_indices = [u for u, srv in enumerate(assigned_server) if srv == j]
        freq = {svc: 0 for svc in range(num_services)}
        for u in user_indices:
            svc = user_services[u]
            freq[svc] += 1
        sorted_services = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        # print(sorted_services)
        selected = [svc for svc, count in sorted_services if count > 0][:SERVICE_CAPACITY_PER_SERVER]
        for svc in selected:
            deployment[j, svc] = 1
    cost, delay = compute_objectives(deployment, servers_pos, user_positions, user_services, assigned_server)
    weighted = 0.5 * cost + 0.5 * delay

    return deployment, cost, delay, weighted

# --------------------------
# 主函数示例 (调用示例)
# --------------------------
# if __name__ == "__main__":
#     # 下面的 main 函数示例中假定用户已有输入数据
#     # 示例数据来自 main 模块中的局部搜索与分配结果（替换为你自己的数据）
#     from main import (
#         candidate_positions,
#         user_positions,
#         user_services,
#         coverage_local_search,
#         assign_users_to_stations,
#         N2,
#         compare_station_selection_methods
#     )
#
#     random.seed(42)
#     # 假定 k = N2, 使用局部搜索确定服务器位置
#     k_val = N2
#     best_sol, best_cost, _ = coverage_local_search(
#         candidate_positions,
#         user_positions,
#         k_val,
#         coverage_radius=1.5,
#         max_iter=200
#     )
#     selected_positions = candidate_positions[best_sol]  # shape (k,2)
#
#     # 为每个用户确定首选服务器（局部搜索后的分配）
#     assignment = assign_users_to_stations(user_positions, candidate_positions, best_sol)
#
#     print(f"局部搜索后服务器: {best_sol}, cost = {best_cost}")
#     print("用户首选服务器(assignment):", assignment[:10], "...")
#
#     # 1) 使用 NSGA-II 仅优化服务部署
#     res = run_nsga_service_deploy(
#         servers_pos=selected_positions,
#         user_positions=user_positions,
#         user_services=user_services,
#         assigned_server=assignment,
#         k=len(best_sol),
#         pop_size=30,
#         n_gen=50,
#         seed=42
#     )
#
#     # 2) 分别使用三种对比策略
#     dep_rand, cost_rand, delay_rand, weighted_rand = random_service_deployment(selected_positions, user_positions, user_services, assignment)
#     print("\n随机部署策略：")
#     print("部署矩阵：\n", dep_rand)
#     print("Cost = {:.2f}, Delay = {:.2f}, Weighted = {:.2f}".format(cost_rand, delay_rand, weighted_rand))
#
#     dep_cost, cost_cost, delay_cost, weighted_cost = greedy_service_deployment_by_cost(selected_positions, user_positions, user_services, assignment)
#     print("\n基于成本贪心部署策略：")
#     print("部署矩阵：\n", dep_cost)
#     print("Cost = {:.2f}, Delay = {:.2f}, Weighted = {:.2f}".format(cost_cost, delay_cost, weighted_cost))
#
#     dep_req, cost_req, delay_req, weighted_req = greedy_service_deployment_by_request(selected_positions, user_positions, user_services, assignment)
#     print("\n基于请求贪心部署策略：")
#     print("部署矩阵：\n", dep_req)
#     print("Cost = {:.2f}, Delay = {:.2f}, Weighted = {:.2f}".format(cost_req, delay_req, weighted_req))
#
#     # 此外还会调用 NSGA-II 的结果分析函数 analyze_nsga_result 对 NSGA-II 求解后的 Pareto 解进行分析。
