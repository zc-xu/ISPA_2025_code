import math
import numpy as np

###################
# 服务部署相关参数
###################
# 每类服务都可有不同部署成本
# SERVICE_DEPLOY_COSTS = [145, 90, 185, 100, 65, 240, 80, 170,
#                         50, 195, 225, 135, 210, 160, 120, 110]
# SERVICE_DEPLOY_COSTS = [100, 120, 80, 150, 90, 200, 50, 110,
#                         145, 90, 185, 100, 65, 240, 80, 170]  # 8类服务对应的部署费用--初始设置
# SERVICE_DEPLOY_COSTS = [100, 120, 80, 150, 90, 200, 50, 110]  # 8类服务对应的部署费用--初始设置
# SERVICE_DEPLOY_COSTS = [10, 20, 80, 100, 30, 200, 50, 110] ##New test --8类服务使用的
SERVICE_DEPLOY_COSTS = [10, 20, 80, 100, 30, 200, 50, 110,] ##New test
# SERVICE_DEPLOY_COSTS = [100, 120, 100, 150, 100, 100, 100, 110]  # 8类服务对应的部署费用--初始设置-changed
# SERVICE_DEPLOY_COSTS = [90, 80, 70, 120, 100, 170, 80, 100]  # 8类服务对应的部署费用
SERVICE_CAPACITY_PER_SERVER = 4  # 每台服务器最多部署多少类服务

########################
# 1. 服务类型相关参数 #
########################

# 假设我们有 8 类服务，对应 8 个不同的 workload 和 data_size
# 这里仅做示例，你可根据实际实验需求自行修改数值
SERVICE_WORKLOADS = [2.0, 3.0, 5.0, 7.0, 4.5, 6.0, 10.0, 1.5]   # 每类服务的计算资源需求 -- 初始设置 --8类服务使用的
# SERVICE_WORKLOADS = [10.0, 15.0, 25.0, 35.0, 20.5, 30.0, 50.0, 6.5]   # 每类服务的计算资源需求 --50
# 打乱后的计算资源需求（单位工作量）
# SERVICE_WORKLOADS = [2.0, 3.0, 5.0, 7.0, 4.5, 6.0, 10.0, 1.5,
#                      6.0, 11.0, 4.5, 9.0, 7.0, 2.0, 8.0, 4.0]


SERVICE_DATA_SIZES = [2.0, 15.0, 4.0, 6.0, 3.0, 8.0, 10.0, 1.0]  # 每类服务对应的数据量(MB) --测试调整1 最优加权值（归一化）=0.2706
# SERVICE_DATA_SIZES = [2.0, 5.0, 4.0, 6.0, 3.0, 8.0, 10.0, 1.0]  # 每类服务对应的数据量(MB) --初始设置
# SERVICE_DATA_SIZES = [1.0, 2.5, 2.0, 3.0, 1.5, 4.0, 5.0, 0.5]  # 每类服务对应的数据量(MB) --50
# 打乱后的数据大小（单位：MB）
# SERVICE_DATA_SIZES = [2.0, 5.0, 4.0, 6.0, 3.0, 8.0, 10.0, 1.0,
#                       6.0, 7.0, 2.0, 10.0, 3.5, 5.0, 1.5, 8.0]

########################
# 2. 全局固定参数（可调）#
########################
DEFAULT_CAPACITY = 10.0      # 服务器计算能力（任务量/秒）
DEFAULT_TX_RATE  = 20.0      # 传输速率（MB/s）
THRESHOLD_DISTANCE = 1.5     # 判断是否在同一区域（km）
# THRESHOLD_DISTANCE = 1.0     # 判断是否在同一区域（km）
COMM_PENALTY_FACTOR = 5.0    # 超出 coverage 时每 km 的额外惩罚系数

########################
# 工具函数：地理距离  #
########################
def haversine_distance(lon1, lat1, lon2, lat2):
    """
    计算两点之间的地理距离（km）
    """
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371.0 * c

########################
# 3. 单个用户延迟计算  #
########################
def compute_user_delay(user_position,
                       server_position,
                       user_service_type,
                       capacity=DEFAULT_CAPACITY,
                       tx_rate=DEFAULT_TX_RATE,
                       threshold=THRESHOLD_DISTANCE,
                       comm_penalty_factor=COMM_PENALTY_FACTOR):
    """
    计算单个用户在给定服务器上的总延迟（计算延迟 + 通信延迟）
    - 计算延迟 = SERVICE_WORKLOADS[user_service_type] / capacity
    - 通信延迟:
        如果距离 <= threshold => 0
        否则 => (SERVICE_DATA_SIZES[user_service_type] / tx_rate) * [ comm_penalty_factor * (distance - threshold) ]
        （或自行定义成 distance * comm_penalty_factor，看你想用哪种方式）
    """
    # 1) 获取该用户所需的计算量 & 数据量
    workload  = SERVICE_WORKLOADS[user_service_type]
    data_size = SERVICE_DATA_SIZES[user_service_type]

    # 2) 计算延迟
    compute_delay = workload / capacity

    # 3) 通信延迟
    distance = haversine_distance(user_position[0], user_position[1],
                                  server_position[0], server_position[1])
    if distance <= threshold:
        comm_delay = 0.0
    else:
        # 这里采用距离超出 threshold 的部分进行加权，也可以改成 distance 整体乘惩罚因子
        dist_exceed = distance - threshold
        # 通信时间基本量:
        base_comm_time = data_size / tx_rate  # 仅根据带宽计算的时间
        # 将超出距离乘以 comm_penalty_factor
        comm_delay = base_comm_time * comm_penalty_factor * distance###注释没改，注意这里的计算方式是distance * comm_penalty_factor
        # 如果想简化，就直接:
        # comm_delay = base_comm_time * comm_penalty_factor * dist_exceed\


    return compute_delay + comm_delay

########################
# 4. Breakdown: 逐用户  #
########################
def total_delay_breakdown(users,
                          servers,
                          assignment,
                          user_service_types,
                          capacity=DEFAULT_CAPACITY,
                          tx_rate=DEFAULT_TX_RATE,
                          threshold=THRESHOLD_DISTANCE,
                          comm_penalty_factor=COMM_PENALTY_FACTOR):
    """
    返回:
      - total_compute: 所有用户计算延迟之和
      - total_comm:    所有用户通信延迟之和
      - total_delay:   上面两者之和
      - breakdown:     list，每个用户 (compute_delay, comm_delay)
    参数:
      users: ndarray, shape (num_users, 2)  # (lon, lat)
      servers: ndarray, shape (num_servers, 2)
      assignment: list/array, 每个用户分配到的服务器索引
      user_service_types: list/array, 每个用户的服务类型[0..7]
    """
    total_compute = 0.0
    total_comm    = 0.0
    breakdown     = []

    for i, user_pos in enumerate(users):
        srv_idx = assignment[i]
        srv_pos = servers[srv_idx]
        svc_type = user_service_types[i]

        # === 计算延迟 ===
        workload  = SERVICE_WORKLOADS[svc_type]
        compute_delay = workload / capacity

        # === 通信延迟 ===
        distance = haversine_distance(user_pos[0], user_pos[1], srv_pos[0], srv_pos[1])
        if distance <= threshold:
            comm_delay = 0.0
        else:
            dist_exceed = distance - threshold
            data_size = SERVICE_DATA_SIZES[svc_type]
            base_comm_time = data_size / tx_rate
            # comm_delay = base_comm_time * (1.0 + comm_penalty_factor * dist_exceed)
            # 或者简单写成:
            comm_delay = base_comm_time * comm_penalty_factor * distance

        total_compute += compute_delay
        total_comm    += comm_delay
        breakdown.append((compute_delay, comm_delay))

    return total_compute, total_comm, (total_compute + total_comm), breakdown

########################
# 5. 合并计算总延迟    #
########################
def total_delay(users,
                servers,
                assignment,
                user_service_types,
                capacity=DEFAULT_CAPACITY,
                tx_rate=DEFAULT_TX_RATE,
                threshold=THRESHOLD_DISTANCE,
                comm_penalty_factor=COMM_PENALTY_FACTOR):
    """
    计算所有用户的总延迟（累加），并返回:
      - overall_delay: float，总延迟之和
      - delays_list:   list, 每个用户的总延迟
    参数:
      users: ndarray, 每个元素 (lon, lat)
      servers: ndarray, 每个元素 (lon, lat)
      assignment: 为每个用户指定使用哪个服务器
      user_service_types: 为每个用户指定其服务类型[0..7]
    """
    delays_list = []
    for i, user_pos in enumerate(users):
        srv_idx = assignment[i]
        srv_pos = servers[srv_idx]
        svc_type = user_service_types[i]

        single_delay = compute_user_delay(
            user_position=user_pos,
            server_position=srv_pos,
            user_service_type=svc_type,
            capacity=capacity,
            tx_rate=tx_rate,
            threshold=threshold,
            comm_penalty_factor=comm_penalty_factor
        )
        delays_list.append(single_delay)

    overall_delay = sum(delays_list)
    return overall_delay, delays_list
