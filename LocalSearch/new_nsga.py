import numpy as np
import random
import matplotlib.pyplot as plt

# ====== pymoo核心类 ====== #
from pymoo.core.problem import Problem
from pymoo.core.sampling import Sampling
from pymoo.core.repair import Repair
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.termination import get_termination
from pymoo.optimize import minimize

# ====== 引入你已有的compute_delay函数或常量 ====== #
# 假设你的 compute_delay.py 就在同级目录:
from compute_delay import (
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

from service_selection_strategies import (
    greedy_service_deployment_by_cost,
    greedy_service_deployment_by_request
)

class MixedServiceSampling(Sampling):
    def __init__(self, predefined=None):
        super().__init__()
        self.predefined = predefined

    def _do(self, problem, n_samples, **kwargs):
        k = problem.k
        num_svc = problem.num_services
        n_var = k * num_svc

        init = self.predefined if self.predefined is not None else np.empty((0, n_var))
        n_remain = n_samples - len(init)

        if n_remain > 0:
            rand_part = np.random.randint(0, 2, size=(n_remain, n_var)).astype(float)
            full_init = np.vstack([init, rand_part])
        else:
            indices = np.random.choice(len(init), size=n_samples, replace=False)
            full_init = init[indices]

        return full_init

def generate_initial_population_by_strategies(servers_pos, user_positions, user_services, assigned_server, k, num_services=8, num_each=10):
    initial_population = []
    for _ in range(num_each):
        indiv, *_ = greedy_service_deployment_by_cost(servers_pos, user_positions, user_services, assigned_server)
        initial_population.append(indiv.flatten())
    for _ in range(num_each):
        indiv, *_ = greedy_service_deployment_by_request(servers_pos, user_positions, user_services, assigned_server)
        initial_population.append(indiv.flatten())
    return np.array(initial_population)


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

            # 该用户首选服务器是否已部署服务
            if indiv[prime_srv, svc_type] == 1:
                # 直接使用 prime_srv
                dist = haversine_distance(upos[0], upos[1],
                                          self.servers_pos[prime_srv][0],
                                          self.servers_pos[prime_srv][1])
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
                    comm_cost_u = 999999.0
                    delay_u = 999999.0
                else:
                    comm_cost_u = best_dist * 1.0
                    delay_u     = self._compute_user_delay_ex(upos, best_j, svc_type, indiv)
            total_comm_cost += comm_cost_u
            total_delay     += delay_u

        # ========== 最终 cost = 部署cost + 通信cost,   delay = total_delay
        cost = deploy_cost + total_comm_cost
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

###############################################################
#  (3) Sampling: 初始种群 (0/1) + 修复
###############################################################
class ServiceSampling(Sampling):
    def _do(self, problem, n_samples, **kwargs):
        k = problem.k
        num_svc = problem.num_services
        n_var = k * num_svc

        # 初步随机 0/1
        X = np.random.randint(0,2,size=(n_samples,n_var)).astype(float)
        return X


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
                            seed=42,
                            init_pop=None):
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
        sampling=MixedServiceSampling(predefined=init_pop),
        # sampling=ServiceSampling(),   # 我们自定义的 0/1 sampling
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


from service_selection_strategies import (
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
        compare_station_selection_methods
    )

    random.seed(42)
    # Suppose we do coverage_local_search => best_sol
        # 先假定 k = N2
    k_val = N2
    best_sol, best_cost, _ = coverage_local_search(
        candidate_positions,
        user_positions,
        k_val,
        coverage_radius=1.5,
        max_iter=200
    )
    # 选中服务器位置:
    selected_positions = candidate_positions[best_sol]  # shape(k,2)

    # 为每个用户分配 nearest from best_sol
    assignment = assign_users_to_stations(user_positions, candidate_positions, best_sol)

    print(f"局部搜索后服务器: {best_sol}, cost= {best_cost}")
    print("用户首选服务器(assignment):", assignment[:10], "...")

    # 生成贪心混合初始解集
    init_pop = generate_initial_population_by_strategies(
        selected_positions,
        user_positions,
        user_services,
        assignment,
        k=len(best_sol),
        num_services=8,
        num_each=15
    )

    # ========== 2) 在 NSGA-II 中只优化服务部署  ========== #
    res = run_nsga_service_deploy(
        servers_pos=selected_positions,  # shape(k,2)
        user_positions=user_positions,
        user_services=user_services,
        assigned_server=assignment,
        k=len(best_sol),
        pop_size=30,
        n_gen=200,
        # n_gen=1000,
        seed=42,
        # initial_population = init_pop
        init_pop = init_pop
    )

    # ========== 3) 分析/输出结果 ========== #
    analyze_nsga_result(res, k=len(best_sol), num_svc=8)

    # 2) 分别使用三种对比策略
    dep_rand, cost_rand, delay_rand, weighted_rand = random_service_deployment(selected_positions, user_positions,
                                                                               user_services, assignment)
    print("\n随机部署策略：")
    print("部署矩阵：\n", dep_rand)
    print("Cost = {:.2f}, Delay = {:.2f}, Weighted = {:.2f}".format(cost_rand, delay_rand, weighted_rand))

    dep_cost, cost_cost, delay_cost, weighted_cost = greedy_service_deployment_by_cost(selected_positions,
                                                                                       user_positions, user_services,
                                                                                       assignment)
    print("\n基于成本贪心部署策略：")
    print("部署矩阵：\n", dep_cost)
    print("Cost = {:.2f}, Delay = {:.2f}, Weighted = {:.2f}".format(cost_cost, delay_cost, weighted_cost))

    dep_req, cost_req, delay_req, weighted_req = greedy_service_deployment_by_request(selected_positions,
                                                                                      user_positions, user_services,
                                                                                      assignment)
    print("\n基于请求贪心部署策略：")
    print("部署矩阵：\n", dep_req)
    print("Cost = {:.2f}, Delay = {:.2f}, Weighted = {:.2f}".format(cost_req, delay_req, weighted_req))

