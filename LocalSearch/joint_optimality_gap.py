import argparse
import itertools
import os
import random
import sys
import time
from collections import OrderedDict

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.termination import get_termination


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from LocalSearch.experiment_utils import (
    assign_users_to_stations,
    coverage_local_search,
    load_input_from_excel,
)
from LocalSearch.nsga_service_deploy import MyServiceDeployProblem, ServiceRepair, ServiceSampling
from LocalSearch.pareto_batch_metrics import calculate_metrics, nondominated


OUT_DIRS = [
    "data/joint_gap",
    "output/csv",
    "output/excel",
    "output/npz",
    "output/png",
    "output/pdf",
]


def ensure_dirs():
    for rel in OUT_DIRS:
        os.makedirs(os.path.join(PROJECT_ROOT, rel), exist_ok=True)


def farthest_subset(points, n_points):
    centroid = np.mean(points, axis=0)
    start = int(np.argmin(np.linalg.norm(points - centroid, axis=1)))
    selected = [start]
    while len(selected) < n_points:
        remaining = [idx for idx in range(len(points)) if idx not in selected]
        dist_to_selected = []
        for idx in remaining:
            distances = np.linalg.norm(points[idx] - points[selected], axis=1)
            dist_to_selected.append((float(np.min(distances)), idx))
        selected.append(max(dist_to_selected)[1])
    return selected


def build_small_instance(source_config, n_candidates, k, n_users, num_services, seed):
    candidates, users, services = load_input_from_excel(source_config)
    rng = np.random.default_rng(seed)

    candidate_indices = farthest_subset(candidates, n_candidates)
    small_candidates = candidates[candidate_indices]

    user_indices = rng.choice(np.arange(len(users)), size=n_users, replace=False)
    small_users = users[user_indices]
    small_services = (services[user_indices] % num_services).astype(int)

    path = os.path.join(
        PROJECT_ROOT,
        "data",
        "joint_gap",
        f"input_data_joint_gap_c{n_candidates}_u{n_users}_k{k}_s{num_services}_seed{seed}.xlsx",
    )
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame(small_candidates, columns=["lng", "lat"]).to_excel(writer, sheet_name="candidates", index=False)
        pd.DataFrame(small_users, columns=["lng", "lat"]).to_excel(writer, sheet_name="users", index=False)
        pd.DataFrame({"service": small_services}).to_excel(writer, sheet_name="services", index=False)
    return small_candidates, small_users, small_services, path


def service_subsets(num_services, capacity):
    subsets = []
    for size in range(capacity + 1):
        subsets.extend(itertools.combinations(range(num_services), size))
    return subsets


def matrix_from_subsets(choices, k, num_services):
    mat = np.zeros((k, num_services), dtype=int)
    for row, subset in enumerate(choices):
        for svc in subset:
            mat[row, svc] = 1
    return mat


def exact_joint_front(candidate_positions, user_positions, user_services, k, num_services, capacity):
    subsets = service_subsets(num_services, capacity)
    rows = []
    started = time.perf_counter()
    for selected in itertools.combinations(range(len(candidate_positions)), k):
        selected = list(selected)
        servers_pos = candidate_positions[selected]
        assigned = assign_users_to_stations(user_positions, candidate_positions, selected)
        problem = MyServiceDeployProblem(
            k=k,
            servers_pos=servers_pos,
            user_positions=user_positions,
            user_services=user_services,
            assigned_server=assigned,
            num_services=num_services,
        )
        for choices in itertools.product(subsets, repeat=k):
            mat = matrix_from_subsets(choices, k, num_services)
            cost, delay = problem._calc_obj(mat)
            rows.append((cost, delay))
    F = np.asarray(rows, dtype=float)
    front = nondominated(F)
    return F, front, time.perf_counter() - started


def run_mos2_psp(candidate_positions, user_positions, user_services, k, num_services, capacity, seed, max_iter, pop_size, n_gen):
    random.seed(seed)
    np.random.seed(seed)
    started = time.perf_counter()
    selected, stage1_cost, _ = coverage_local_search(
        candidate_positions,
        user_positions,
        k,
        coverage_radius=1.5,
        max_iter=max_iter,
        verbose=False,
    )
    servers_pos = candidate_positions[selected]
    assigned = assign_users_to_stations(user_positions, candidate_positions, selected)
    problem = MyServiceDeployProblem(
        k=k,
        servers_pos=servers_pos,
        user_positions=user_positions,
        user_services=user_services,
        assigned_server=assigned,
        num_services=num_services,
    )
    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=ServiceSampling(
            "hybrid-A-1",
            deterministic_anchor_size=min(2, capacity),
            visualize_hybrid_process=False,
            capacity_per_server=capacity,
        ),
        repair=ServiceRepair(capacity_per_server=capacity),
        eliminate_duplicates=True,
    )
    res = minimize(
        problem,
        algorithm,
        get_termination("n_gen", n_gen),
        seed=seed,
        save_history=False,
        verbose=False,
    )
    elapsed = time.perf_counter() - started
    F = np.asarray(res.F, dtype=float)
    return F, selected, stage1_cost, elapsed


def save_npz(config_name, exact_front, mos2_f):
    npz_dir = os.path.join(PROJECT_ROOT, "output", "npz")
    exact_path = os.path.join(npz_dir, f"res_joint_exact_{config_name}.npz")
    mos2_path = os.path.join(npz_dir, f"res_mos2_psp_{config_name}.npz")
    np.savez(exact_path, F=exact_front)
    np.savez(mos2_path, F=mos2_f)
    return exact_path, mos2_path


def plot_front(config_name, norm_data):
    colors = {"Joint-Exact": "#4C566A", "MOS2-PSP": "#D62728"}
    markers = {"Joint-Exact": "o", "MOS2-PSP": "D"}
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(6.8, 5.3))
    for method, data in norm_data.items():
        ax.scatter(
            data[:, 0],
            data[:, 1],
            label=method,
            color=colors.get(method, "#333333"),
            marker=markers.get(method, "o"),
            s=58 if method == "MOS2-PSP" else 34,
            alpha=0.82,
            edgecolors="white",
            linewidths=0.35,
            zorder=3,
        )
    ax.set_xlabel("cost", fontsize=22)
    ax.set_ylabel("delay", fontsize=22)
    ax.tick_params(axis="both", labelsize=19)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.75, alpha=0.75, zorder=0)
    ax.legend(fontsize=17, frameon=True, edgecolor="lightgray")
    ax.set_xlim(-0.04, 1.04)
    ax.set_ylim(-0.04, 1.04)
    fig.tight_layout()
    png = os.path.join(PROJECT_ROOT, "output", "png", f"joint_gap_front_{config_name}.png")
    pdf = os.path.join(PROJECT_ROOT, "output", "pdf", f"joint_gap_front_{config_name}.pdf")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return png, pdf


def plot_metrics(config_name, metrics):
    colors = ["#4C566A" if m == "Joint-Exact" else "#D62728" for m in metrics["Method"]]
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False
    fig, axes = plt.subplots(1, 3, figsize=(9.2, 3.4))
    for ax, metric, ylabel in zip(axes, ["HV", "IGD", "BestQ"], ["HV", "IGD", "Best Q"]):
        values = metrics[metric].to_numpy(dtype=float)
        ax.bar(np.arange(len(values)), values, color=colors, edgecolor="black", linewidth=0.45, width=0.56, zorder=3)
        ax.set_xticks(np.arange(len(values)))
        ax.set_xticklabels(metrics["Method"], fontsize=11)
        ax.set_ylabel(ylabel, fontsize=14)
        ax.tick_params(axis="y", labelsize=12)
        ax.grid(True, axis="y", linestyle="--", linewidth=0.75, alpha=0.72, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    fig.tight_layout()
    png = os.path.join(PROJECT_ROOT, "output", "png", f"joint_gap_metrics_{config_name}.png")
    pdf = os.path.join(PROJECT_ROOT, "output", "pdf", f"joint_gap_metrics_{config_name}.pdf")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return png, pdf


def run(args):
    ensure_dirs()
    config_name = f"joint_gap_c{args.n_candidates}_u{args.n_users}_k{args.k}_s{args.num_services}_seed{args.seed}"
    candidates, users, services, data_path = build_small_instance(
        args.source_config,
        args.n_candidates,
        args.k,
        args.n_users,
        args.num_services,
        args.seed,
    )
    exact_all, exact_front, exact_time = exact_joint_front(
        candidates,
        users,
        services,
        args.k,
        args.num_services,
        args.capacity,
    )
    mos2_f, selected, stage1_cost, mos2_time = run_mos2_psp(
        candidates,
        users,
        services,
        args.k,
        args.num_services,
        args.capacity,
        args.seed,
        args.stage1_iter,
        args.pop_size,
        args.n_gen,
    )
    save_npz(config_name, exact_front, mos2_f)

    data = OrderedDict([("Joint-Exact", exact_front), ("MOS2-PSP", mos2_f)])
    metrics, norm_data, fronts, _, lower, upper = calculate_metrics(data, alpha=args.metric_alpha)
    runtime = pd.DataFrame(
        [
            {
                "Config": config_name,
                "Method": "Joint-Exact",
                "RuntimeSec": exact_time,
                "RawSolutionCount": len(exact_all),
                "ParetoCount": len(exact_front),
                "SelectedServers": "",
                "Stage1Cost": np.nan,
            },
            {
                "Config": config_name,
                "Method": "MOS2-PSP",
                "RuntimeSec": mos2_time,
                "RawSolutionCount": len(mos2_f),
                "ParetoCount": int(metrics.loc[metrics["Method"] == "MOS2-PSP", "ParetoCount"].iloc[0]),
                "SelectedServers": " ".join(map(str, sorted(selected))),
                "Stage1Cost": stage1_cost,
            },
        ]
    )
    metrics["Config"] = config_name
    merged = metrics.merge(runtime, on=["Config", "Method"], how="left")

    joint = merged[merged["Method"] == "Joint-Exact"].iloc[0]
    mos2 = merged[merged["Method"] == "MOS2-PSP"].iloc[0]
    gap = pd.DataFrame(
        [
            {
                "Config": config_name,
                "HVGapPct": 100.0 * (joint["HV"] - mos2["HV"]) / max(joint["HV"], 1e-12),
                "IGDGap": mos2["IGD"] - joint["IGD"],
                "BestQGap": mos2["BestQ"] - joint["BestQ"],
                "RuntimeRatioJointOverMOS2": joint["RuntimeSec"] / max(mos2["RuntimeSec"], 1e-12),
                "NormalizationLowerCost": lower[0],
                "NormalizationLowerDelay": lower[1],
                "NormalizationUpperCost": upper[0],
                "NormalizationUpperDelay": upper[1],
            }
        ]
    )

    csv_path = os.path.join(PROJECT_ROOT, "output", "csv", f"joint_gap_metrics_{config_name}.csv")
    xlsx_path = os.path.join(PROJECT_ROOT, "output", "excel", f"joint_gap_metrics_{config_name}.xlsx")
    gap_csv = os.path.join(PROJECT_ROOT, "output", "csv", f"joint_gap_summary_{config_name}.csv")
    merged.to_csv(csv_path, index=False)
    gap.to_csv(gap_csv, index=False)
    with pd.ExcelWriter(xlsx_path) as writer:
        merged.to_excel(writer, sheet_name="metrics", index=False)
        gap.to_excel(writer, sheet_name="gap", index=False)

    front_png, front_pdf = plot_front(config_name, norm_data)
    metric_png, metric_pdf = plot_metrics(config_name, metrics)

    print("Config:", config_name)
    print("Data:", data_path)
    print(merged.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print(gap.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("Saved:", csv_path)
    print("Saved:", xlsx_path)
    print("Saved:", gap_csv)
    print("Saved:", front_png)
    print("Saved:", front_pdf)
    print("Saved:", metric_png)
    print("Saved:", metric_pdf)


def main():
    parser = argparse.ArgumentParser(description="Small-scale joint optimization gap experiment for MOS2.")
    parser.add_argument("--source-config", default="data/input_data_10_130_8_new.xlsx")
    parser.add_argument("--n-candidates", type=int, default=8)
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--n-users", type=int, default=40)
    parser.add_argument("--num-services", type=int, default=4)
    parser.add_argument("--capacity", type=int, default=2)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--stage1-iter", type=int, default=200)
    parser.add_argument("--pop-size", type=int, default=50)
    parser.add_argument("--n-gen", type=int, default=200)
    parser.add_argument("--metric-alpha", type=float, default=0.5)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
