import numpy as np
import matplotlib.pyplot as plt
from pymoo.indicators.hv import HV
import matplotlib
import pandas as pd
plt.rcParams['font.family'] = 'Arial'
# matplotlib.rcParams['font.sans-serif'] = ['SimHei']
matplotlib.rcParams['axes.unicode_minus'] = False

def normalize(F, global_min=None, global_max=None):
    """归一化到 [0, 1] 区间"""
    if global_min is None:
        global_min = np.min(F, axis=0)
    if global_max is None:
        global_max = np.max(F, axis=0)
    return (F - global_min) / (global_max - global_min)

def compare_four_saved_results_normalized(a=0.5, b=0.5, save_excel=True):
    files = {
        "NS-P": "res_random.npz",
        # "hybrid": "res_hybrid.npz",
        # "hybrid-A": "res_hybrid-A.npz",

        # "hybrid-B": "res_hybrid-B.npz",
        # "hybrid-C": "res_hybrid-C.npz",
        "GCP": "res_greedy_cost.npz",
        "GDP": "res_greedy_request.npz",
        "PSP": "res_hybrid-A-1.npz",
    }

    colors = {
        "NS-P": "blue",
        # "hybrid": "red",
        # "hybrid-A":"pink",

        # "hybrid-B": "black",
        # "hybrid-C": "purple",
        "GCP": "green",
        "GDP": "orange",
        "PSP": "red",
    }

    raw_data = {}
    for label, file in files.items():
        res = np.load(file)
        raw_data[label] = res["F"]

    # 全局 min-max（用于归一化和反归一化）
    all_F = np.vstack(list(raw_data.values()))
    global_min = np.min(all_F, axis=0)
    global_max = np.max(all_F, axis=0)

    # HV 计算参考点
    ref_point = np.array([1.1, 1.1])
    hv = HV(ref_point=ref_point)

    norm_data = {}
    print("\n📐 Hypervolume（归一化后）& 最优加权值:")

    # Excel writer 初始化
    if save_excel:
        writer = pd.ExcelWriter("nsga2_normalized_results20.xlsx", engine='xlsxwriter')

    for label, F in raw_data.items():
        F_norm = normalize(F, global_min, global_max)
        norm_data[label] = F_norm

        # 归一化后指标
        hv_val = hv.do(F_norm)
        weighted = a * F_norm[:, 0] + b * F_norm[:, 1]
        best_weighted = np.min(weighted)

        # 原始指标下的加权值
        weighted_raw = a * F[:, 0] + b * F[:, 1]
        best_weighted_raw = np.min(weighted_raw)

        print(f" - {label}：HV={hv_val:.4f}, 最优加权值（归一化）={best_weighted:.4f}，最优加权值（原始）={best_weighted_raw:.4f}")

        # 保存至 Excel
        if save_excel:
            df = pd.DataFrame({
                "原始 Cost": F[:, 0],
                "原始 Delay": F[:, 1],
                "归一化 Cost": F_norm[:, 0],
                "归一化 Delay": F_norm[:, 1],
                f"加权值({a}*C+{b}*D)_归一化": weighted,
                f"加权值({a}*C+{b}*D)_原始": weighted_raw
            })
            df.to_excel(writer, sheet_name=label, index=False)

    if save_excel:
        writer.close()
        print("✅ 已保存结果至 nsga2_normalized_results10.xlsx")

    # 绘图
    plt.figure(figsize=(7, 5.5))
    for label, F in norm_data.items():
        plt.scatter(F[:, 0], F[:, 1], label=label, alpha=0.8, s=80, c=colors[label])

    plt.xticks(rotation=0, ha='right', fontsize=23)
    plt.yticks(rotation=0, fontsize=23)
    plt.xlabel("cost", fontname='Arial', fontsize=24)
    plt.ylabel("delay", fontname='Arial', fontsize=24)

    # plt.xlabel("归一化 Cost")
    # plt.ylabel("归一化 Delay")
    # plt.title("四种初始化策略（归一化后）的 NSGA-II 解集对比")
    plt.legend(fontsize=23)
    plt.grid(True, axis='y', linestyle='--', linewidth=0.75)
    plt.tight_layout()
    plt.savefig('nsga_data_10_130_new2.pdf', format='pdf', bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    compare_four_saved_results_normalized()
