import argparse
import contextlib
import io
import os
import random
import sys
from collections import OrderedDict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.indicators.hv import HV
from pymoo.optimize import minimize
from pymoo.termination import get_termination


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

import LocalSearch.compute_delay as compute_delay
import LocalSearch.nsga_service_deploy as nsga_service_deploy
import LocalSearch.service_selection_strategies as service_selection_strategies
from LocalSearch.experiment_configs import EXPERIMENT_CONFIGS, select_configs
from LocalSearch.experiment_utils import build_stage_context
from LocalSearch.nsga_service_deploy import MyServiceDeployProblem, ServiceRepair, ServiceSampling
from LocalSearch.pareto_batch_metrics import igd, nondominated, normalize, spacing


METHOD_NAME = "PSP"


def ensure_dirs():
    for rel in ("output/npz", "output/csv", "output/excel", "output/pdf", "output/png"):
        os.makedirs(os.path.join(PROJECT_ROOT, rel), exist_ok=True)


def set_capacity(capacity):
    capacity = int(capacity)
    compute_delay.SERVICE_CAPACITY_PER_SERVER = capacity
    nsga_service_deploy.SERVICE_CAPACITY_PER_SERVER = capacity
    service_selection_strategies.SERVICE_CAPACITY_PER_SERVER = capacity
    return capacity


def parse_varpi_values(values, capacity):
    cap = int(capacity)
    parsed = []
    for value in values:
        token = str(value).strip()
        if token.lower() in {"vj", "v_j", "cap", "capacity"}:
            varpi = cap
        elif token.lower() in {"half", "vj/2", "v_j/2"}:
            varpi = max(1, cap // 2)
        else:
            varpi = int(token)
        varpi = max(0, min(cap, varpi))
        if varpi not in parsed:
            parsed.append(varpi)
    return parsed


def varpi_label(varpi, capacity):
    cap = int(capacity)
    half = max(1, cap // 2)
    if varpi == half:
        return f"Vj/2={varpi}"
    if varpi == cap:
        return f"Vj={cap}"
    return str(varpi)


def run_one(config_name, context, capacity, varpi, seed, pop_size, n_gen, verbose):
    set_capacity(capacity)
    random.seed(seed)
    np.random.seed(seed)

    problem = MyServiceDeployProblem(
        k=context["k"],
        servers_pos=context["servers_pos"],
        user_positions=context["user_positions"],
        user_services=context["user_services"],
        assigned_server=context["assigned_server"],
    )
    algorithm = NSGA2(
        pop_size=pop_size,
        sampling=ServiceSampling(
            "hybrid-A-1",
            deterministic_anchor_size=varpi,
            visualize_hybrid_process=False,
            capacity_per_server=capacity,
        ),
        repair=ServiceRepair(capacity_per_server=capacity),
        eliminate_duplicates=True,
    )

    runner = lambda: minimize(
        problem,
        algorithm,
        get_termination("n_gen", n_gen),
        seed=seed,
        save_history=False,
        verbose=False,
    )
    if verbose:
        res = runner()
    else:
        with contextlib.redirect_stdout(io.StringIO()):
            res = runner()

    F = np.asarray(res.F, dtype=float)
    X = np.asarray(res.X)
    if F.ndim == 1:
        F = F.reshape(1, -1)

    npz_path = os.path.join(
        PROJECT_ROOT,
        "output",
        "npz",
        f"res_hybrid_anchor_cap{capacity}_varpi{varpi}_{config_name}_seed{seed}.npz",
    )
    np.savez(npz_path, X=X, F=F, config=config_name, capacity=capacity, varpi=varpi, seed=seed)
    return F, npz_path


def calculate_detail_metrics(results, alpha=0.5, ref_point=(1.1, 1.1)):
    by_config = OrderedDict()
    for item in results:
        by_config.setdefault((item["Capacity"], item["Config"]), []).append(item)

    rows = []
    beta = 1.0 - alpha
    hv_indicator = HV(ref_point=np.asarray(ref_point, dtype=float))

    for (capacity, config_name), items in by_config.items():
        all_raw = np.vstack([item["F"] for item in items])
        lower = np.min(all_raw, axis=0)
        upper = np.max(all_raw, axis=0)

        fronts = []
        norm_f_by_item = []
        for item in items:
            F_norm = normalize(item["F"], lower, upper)
            front = nondominated(F_norm)
            fronts.append(front)
            norm_f_by_item.append(F_norm)
        reference_front = nondominated(np.vstack(fronts))

        for item, F_norm, front in zip(items, norm_f_by_item, fronts):
            weighted = alpha * F_norm[:, 0] + beta * F_norm[:, 1]
            front_weighted = alpha * front[:, 0] + beta * front[:, 1] if len(front) else np.array([np.nan])
            rows.append(
                {
                    "Config": item["Config"],
                    "Capacity": item["Capacity"],
                    "CapacityLabel": f"Vj={item['Capacity']}",
                    "Varpi": item["Varpi"],
                    "VarpiLabel": varpi_label(item["Varpi"], item["Capacity"]),
                    "VarpiRatio": float(item["Varpi"] / item["Capacity"]) if item["Capacity"] else np.nan,
                    "IsHalfCapacity": bool(item["Varpi"] == max(1, item["Capacity"] // 2)),
                    "Seed": item["Seed"],
                    "HV": float(hv_indicator.do(front)) if len(front) else np.nan,
                    "IGD": igd(front, reference_front),
                    "Spacing": spacing(front),
                    "BestQ": float(np.min(weighted)),
                    "BestFrontQ": float(np.min(front_weighted)),
                    "ParetoCount": int(len(front)),
                    "SolutionCount": int(len(F_norm)),
                    "BestCostNorm": float(np.min(F_norm[:, 0])),
                    "BestDelayNorm": float(np.min(F_norm[:, 1])),
                    "RawBestCost": float(np.min(item["F"][:, 0])),
                    "RawBestDelay": float(np.min(item["F"][:, 1])),
                    "NpzPath": item["NpzPath"],
                }
            )

    return pd.DataFrame(rows)


def summarize_metrics(detail):
    grouped = (
        detail.groupby(["Capacity", "CapacityLabel", "Config", "Varpi", "VarpiLabel", "VarpiRatio", "IsHalfCapacity"], as_index=False)
        .agg(
            HV_mean=("HV", "mean"),
            HV_std=("HV", "std"),
            IGD_mean=("IGD", "mean"),
            IGD_std=("IGD", "std"),
            BestQ_mean=("BestQ", "mean"),
            BestQ_std=("BestQ", "std"),
            BestCostNorm_mean=("BestCostNorm", "mean"),
            BestDelayNorm_mean=("BestDelayNorm", "mean"),
            ParetoCount_mean=("ParetoCount", "mean"),
            Runs=("Seed", "count"),
        )
        .sort_values(["Capacity", "Config", "Varpi"])
    )

    ranked_parts = []
    for (capacity, config_name), part in grouped.groupby(["Capacity", "Config"], sort=False):
        part = part.copy()
        part["HV_rank"] = part["HV_mean"].rank(method="min", ascending=False)
        part["IGD_rank"] = part["IGD_mean"].rank(method="min", ascending=True)
        part["BestQ_rank"] = part["BestQ_mean"].rank(method="min", ascending=True)
        part["MeanRank"] = part[["HV_rank", "IGD_rank", "BestQ_rank"]].mean(axis=1)
        part["ConfigBestByMeanRank"] = part["MeanRank"] == part["MeanRank"].min()
        ranked_parts.append(part)

    return pd.concat(ranked_parts, ignore_index=True)


def save_tables(detail, summary):
    csv_detail = os.path.join(PROJECT_ROOT, "output", "csv", "hybrid_anchor_capacity_sensitivity_detail.csv")
    csv_summary = os.path.join(PROJECT_ROOT, "output", "csv", "hybrid_anchor_capacity_sensitivity_summary.csv")
    csv_paper = os.path.join(PROJECT_ROOT, "output", "csv", "hybrid_anchor_capacity_sensitivity_paper_table.csv")
    csv_series = os.path.join(PROJECT_ROOT, "output", "csv", "hybrid_anchor_capacity_sensitivity_series_rank.csv")
    xlsx_detail = os.path.join(PROJECT_ROOT, "output", "excel", "hybrid_anchor_capacity_sensitivity_detail.xlsx")
    xlsx_summary = os.path.join(PROJECT_ROOT, "output", "excel", "hybrid_anchor_capacity_sensitivity_summary.xlsx")

    detail.to_csv(csv_detail, index=False)
    summary.to_csv(csv_summary, index=False)
    summary.to_excel(xlsx_summary, index=False)
    detail.to_excel(xlsx_detail, index=False)

    paper_cols = [
        "Config",
        "CapacityLabel",
        "VarpiLabel",
        "VarpiRatio",
        "IsHalfCapacity",
        "HV_mean",
        "IGD_mean",
        "BestQ_mean",
        "MeanRank",
        "ConfigBestByMeanRank",
        "Runs",
    ]
    summary[paper_cols].to_csv(csv_paper, index=False)
    calculate_series_rank(summary).to_csv(csv_series, index=False)
    return csv_detail, csv_summary, csv_paper, csv_series, xlsx_detail, xlsx_summary


def calculate_series_rank(summary):
    config_sets = OrderedDict(
        [
            ("K=10", ["10_130", "10_150", "10_180"]),
            ("M=130", ["5_130", "10_130", "15_130", "20_130"]),
            ("All", sorted(summary["Config"].unique())),
        ]
    )
    rows = []
    for series, configs in config_sets.items():
        part = summary[summary["Config"].isin(configs)]
        if part.empty:
            continue
        for (capacity, capacity_label, varpi, label, is_half), group in part.groupby(
            ["Capacity", "CapacityLabel", "Varpi", "VarpiLabel", "IsHalfCapacity"], sort=True
        ):
            rows.append(
                {
                    "Series": series,
                    "Capacity": capacity,
                    "CapacityLabel": capacity_label,
                    "Varpi": varpi,
                    "VarpiLabel": label,
                    "IsHalfCapacity": is_half,
                    "MeanRank": float(group["MeanRank"].mean()),
                    "RankStd": float(group["MeanRank"].std()) if len(group) > 1 else 0.0,
                    "ConfigCount": int(group["Config"].nunique()),
                }
            )
    return pd.DataFrame(rows).sort_values(["Capacity", "Series", "Varpi"])


def plot_config(summary, capacity, config_name):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False

    part = summary[(summary["Capacity"] == capacity) & (summary["Config"] == config_name)].sort_values("Varpi")
    labels = part["VarpiLabel"].tolist()
    x = np.arange(len(part))

    metric_specs = [
        ("HV_mean", "HV_std", "HV ↑", "#A3BEFA", "#2E4780"),
        ("IGD_mean", "IGD_std", "IGD ↓", "#F0986E", "#804126"),
        ("BestQ_mean", "BestQ_std", "Best Q ↓", "#A3D576", "#386411"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.6))
    for ax, (mean_col, std_col, ylabel, fill, edge) in zip(axes, metric_specs):
        y = part[mean_col].to_numpy(dtype=float)
        yerr = part[std_col].fillna(0.0).to_numpy(dtype=float)
        ax.errorbar(
            x,
            y,
            yerr=yerr,
            color=edge,
            marker="o",
            markerfacecolor=fill,
            markeredgecolor=edge,
            linewidth=1.2,
            capsize=3,
            zorder=3,
        )
        ax.set_xticks(x)
        ax.set_xticklabels(labels, fontsize=12)
        ax.set_xlabel(r"$\varpi_j$", fontsize=14)
        ax.set_ylabel(ylabel, fontsize=14)
        ax.tick_params(axis="y", labelsize=12)
        ax.grid(True, axis="y", linestyle="--", linewidth=0.75, alpha=0.72, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)

    fig.tight_layout()
    pdf_path = os.path.join(PROJECT_ROOT, "output", "pdf", f"hybrid_anchor_capacity_sensitivity_cap{capacity}_{config_name}.pdf")
    png_path = os.path.join(PROJECT_ROOT, "output", "png", f"hybrid_anchor_capacity_sensitivity_cap{capacity}_{config_name}.png")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return pdf_path, png_path


def plot_mean_rank(summary):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False

    rank_df = (
        summary.groupby(["Capacity", "CapacityLabel", "Varpi", "VarpiLabel", "IsHalfCapacity"], as_index=False)
        .agg(MeanRank=("MeanRank", "mean"), MeanRankStd=("MeanRank", "std"))
        .sort_values(["Capacity", "Varpi"])
    )
    rank_df["XLabel"] = rank_df["CapacityLabel"] + "\n" + rank_df["VarpiLabel"]
    fig, ax = plt.subplots(figsize=(9.2, 4.2))
    colors = ["#F0986E" if is_half else "#A3BEFA" for is_half in rank_df["IsHalfCapacity"]]
    edges = ["#804126" if is_half else "#2E4780" for is_half in rank_df["IsHalfCapacity"]]
    bars = ax.bar(
        np.arange(len(rank_df)),
        rank_df["MeanRank"],
        yerr=rank_df["MeanRankStd"].fillna(0.0),
        color=colors,
        edgecolor=edges,
        linewidth=1.0,
        capsize=3,
        width=0.55,
        zorder=3,
    )
    ax.set_xticks(np.arange(len(rank_df)))
    ax.set_xticklabels(rank_df["XLabel"], fontsize=11)
    ax.set_xlabel(r"Capacity $V_j$ and anchor size $\varpi_j$", fontsize=15)
    ax.set_ylabel("Mean rank across metrics ↓", fontsize=15)
    ax.tick_params(axis="y", labelsize=13)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.75, alpha=0.72, zorder=0)
    for bar, value in zip(bars, rank_df["MeanRank"]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=11,
            color="#1F2430",
        )
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    pdf_path = os.path.join(PROJECT_ROOT, "output", "pdf", "hybrid_anchor_capacity_sensitivity_mean_rank.pdf")
    png_path = os.path.join(PROJECT_ROOT, "output", "png", "hybrid_anchor_capacity_sensitivity_mean_rank.png")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return pdf_path, png_path


def plot_series_rank(summary):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False

    rank_df = calculate_series_rank(summary)
    series_order = [series for series in ["K=10", "M=130", "All"] if series in set(rank_df["Series"])]
    varpi_order = rank_df[["Capacity", "CapacityLabel", "Varpi", "VarpiLabel"]].drop_duplicates().sort_values(["Capacity", "Varpi"])
    labels = (varpi_order["CapacityLabel"] + "\n" + varpi_order["VarpiLabel"]).tolist()
    key_labels = list(zip(varpi_order["Capacity"], varpi_order["Varpi"]))
    x = np.arange(len(labels))
    width = min(0.24, 0.72 / max(len(series_order), 1))
    colors = {
        "K=10": ("#A3BEFA", "#2E4780"),
        "M=130": ("#F0986E", "#804126"),
        "All": ("#A3D576", "#386411"),
    }

    fig, ax = plt.subplots(figsize=(7.4, 4.2))
    for i, series in enumerate(series_order):
        part = rank_df[rank_df["Series"] == series].set_index(["Capacity", "Varpi"]).loc[key_labels].reset_index()
        offset = (i - (len(series_order) - 1) / 2) * width
        fill, edge = colors.get(series, ("#C5CAD3", "#464C55"))
        bars = ax.bar(
            x + offset,
            part["MeanRank"],
            yerr=part["RankStd"].fillna(0.0),
            width=width,
            color=fill,
            edgecolor=edge,
            linewidth=1.0,
            capsize=3,
            label=series,
            zorder=3,
        )
        for bar, value in zip(bars, part["MeanRank"]):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value,
                f"{value:.2f}",
                ha="center",
                va="bottom",
                fontsize=8.5,
                color="#1F2430",
            )

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_xlabel(r"Capacity $V_j$ and anchor size $\varpi_j$", fontsize=15)
    ax.set_ylabel("Mean rank across metrics ↓", fontsize=15)
    ax.tick_params(axis="y", labelsize=13)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.75, alpha=0.72, zorder=0)
    ax.legend(loc="upper right", fontsize=11, frameon=True, edgecolor="lightgray", framealpha=1)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    fig.tight_layout()
    pdf_path = os.path.join(PROJECT_ROOT, "output", "pdf", "hybrid_anchor_capacity_sensitivity_series_rank.pdf")
    png_path = os.path.join(PROJECT_ROOT, "output", "png", "hybrid_anchor_capacity_sensitivity_series_rank.png")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return pdf_path, png_path


def run(args):
    ensure_dirs()
    configs = select_configs(args.configs)
    results = []

    print("Testing capacities V_j:", ", ".join(map(str, args.capacities)))
    print("Seeds:", ", ".join(map(str, args.seeds)))

    contexts = {}
    for config_name, config in configs.items():
        print(f"\n=== Build Stage-I context: {config_name} ===")
        contexts[config_name] = build_stage_context(
            config,
            seed=args.stage1_seed,
            coverage_radius=args.coverage_radius,
            max_iter=args.stage1_iter,
            verbose=args.verbose_stage1,
        )
        context = contexts[config_name]
        print(f"[{config_name}] data={config['data_file']}, K={context['k']}, selected={context['best_solution']}, stage1_cost={context['best_cost']:.4f}")

    for capacity in args.capacities:
        set_capacity(capacity)
        varpi_values = parse_varpi_values(args.varpi_values, capacity)
        print(f"\n=== Capacity V_j={capacity}; testing varpi_j values: {', '.join(map(str, varpi_values))} ===")
        for config_name, context in contexts.items():
            for varpi in varpi_values:
                for seed in args.seeds:
                    print(f"[{config_name}] V_j={capacity}, varpi_j={varpi_label(varpi, capacity)}, seed={seed}")
                    F, npz_path = run_one(
                        config_name=config_name,
                        context=context,
                        capacity=capacity,
                        varpi=varpi,
                        seed=seed,
                        pop_size=args.pop_size,
                        n_gen=args.n_gen,
                        verbose=args.verbose_nsga,
                    )
                    results.append(
                        {
                            "Config": config_name,
                            "Capacity": capacity,
                            "Varpi": varpi,
                            "Seed": seed,
                            "F": F,
                            "NpzPath": npz_path,
                        }
                    )

    detail = calculate_detail_metrics(results, alpha=args.metric_alpha)
    summary = summarize_metrics(detail)
    table_paths = save_tables(detail, summary)

    figure_paths = []
    for capacity in args.capacities:
        for config_name in configs:
            figure_paths.extend(plot_config(summary, capacity, config_name))
    figure_paths.extend(plot_mean_rank(summary))
    figure_paths.extend(plot_series_rank(summary))

    print("\nSummary:")
    print(
        summary[
            [
                "Config",
                "CapacityLabel",
                "VarpiLabel",
                "IsHalfCapacity",
                "HV_mean",
                "IGD_mean",
                "BestQ_mean",
                "MeanRank",
                "ConfigBestByMeanRank",
                "Runs",
            ]
        ].to_string(index=False, float_format=lambda x: f"{x:.4f}")
    )
    print("\nSaved tables:")
    for path in table_paths:
        print(path)
    print("\nSaved figures:")
    for path in figure_paths:
        print(path)
    return detail, summary


def main():
    parser = argparse.ArgumentParser(description="Run sensitivity experiments for hybrid-A-1 deterministic anchor size.")
    parser.add_argument(
        "--configs",
        nargs="+",
        default=["10_130"],
        help="Config names to run, or all. Known: " + ", ".join(EXPERIMENT_CONFIGS.keys()),
    )
    parser.add_argument(
        "--varpi-values",
        nargs="+",
        default=["1", "half", "Vj"],
        help="Anchor sizes to test. Use half/Vj/Cap tokens for capacity-relative values.",
    )
    parser.add_argument("--capacities", nargs="+", type=int, default=[4], help="Capacity values V_j to test.")
    parser.add_argument("--seeds", nargs="+", type=int, default=[42, 43, 44])
    parser.add_argument("--stage1-seed", type=int, default=42)
    parser.add_argument("--coverage-radius", type=float, default=1.5)
    parser.add_argument("--stage1-iter", type=int, default=200)
    parser.add_argument("--pop-size", type=int, default=50)
    parser.add_argument("--n-gen", type=int, default=200)
    parser.add_argument("--metric-alpha", type=float, default=0.5)
    parser.add_argument("--verbose-stage1", action="store_true")
    parser.add_argument("--verbose-nsga", action="store_true")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
