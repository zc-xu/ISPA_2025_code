import argparse
import os
import random
import sys
from collections import OrderedDict

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from LocalSearch.experiment_configs import EXPERIMENT_CONFIGS, select_configs
from LocalSearch.experiment_utils import (
    COST_PER_KM,
    PENALTY_FACTOR,
    haversine_distance,
    load_input_from_excel,
    resolve_k,
)


STRATEGY_LABELS = OrderedDict(
    [
        ("random", "Random"),
        ("density_topk", "Density"),
        ("distance_sum", "DistSum"),
        ("greedy_marginal", "Greedy"),
        ("density_diverse", "Diverse"),
    ]
)

STRATEGY_COLORS = {
    "random": "#1f77b4",
    "density_topk": "#2ca02c",
    "distance_sum": "#ff7f0e",
    "greedy_marginal": "#9467bd",
    "density_diverse": "#d62728",
}


def ensure_dirs():
    for rel in ("output/csv", "output/excel", "output/pdf", "output/png"):
        os.makedirs(os.path.join(PROJECT_ROOT, rel), exist_ok=True)


def pairwise_user_candidate_distances(user_positions, candidate_positions):
    distances = np.zeros((len(user_positions), len(candidate_positions)), dtype=float)
    for user_idx, user in enumerate(user_positions):
        for cand_idx, candidate in enumerate(candidate_positions):
            distances[user_idx, cand_idx] = haversine_distance(user[0], user[1], candidate[0], candidate[1])
    return distances


def pairwise_candidate_distances(candidate_positions):
    distances = np.zeros((len(candidate_positions), len(candidate_positions)), dtype=float)
    for i, left in enumerate(candidate_positions):
        for j, right in enumerate(candidate_positions):
            if i == j:
                continue
            distances[i, j] = haversine_distance(left[0], left[1], right[0], right[1])
    return distances


def coverage_cost_from_matrix(solution, user_candidate_distances, coverage_radius):
    if not solution:
        return float("inf")
    selected = user_candidate_distances[:, list(solution)]
    min_distances = np.min(selected, axis=1)
    penalties = np.where(min_distances <= coverage_radius, 0.0, min_distances * PENALTY_FACTOR)
    return float(np.sum(penalties) * COST_PER_KM)


def coverage_ratio(solution, user_candidate_distances, coverage_radius):
    selected = user_candidate_distances[:, list(solution)]
    min_distances = np.min(selected, axis=1)
    return float(np.mean(min_distances <= coverage_radius))


def station_densities(user_candidate_distances, coverage_radius):
    return np.sum(user_candidate_distances <= coverage_radius, axis=0).astype(float)


def normalize(values):
    values = np.asarray(values, dtype=float)
    lower = float(np.min(values))
    upper = float(np.max(values))
    if upper - lower <= 1e-12:
        return np.zeros_like(values)
    return (values - lower) / (upper - lower)


def initial_solution(strategy, k, rng, user_candidate_distances, candidate_distances, coverage_radius):
    num_candidates = user_candidate_distances.shape[1]
    all_indices = list(range(num_candidates))

    if strategy == "random":
        return sorted(rng.sample(all_indices, k))

    densities = station_densities(user_candidate_distances, coverage_radius)

    if strategy == "density_topk":
        total_distances = np.sum(user_candidate_distances, axis=0)
        order = sorted(all_indices, key=lambda idx: (-densities[idx], total_distances[idx], idx))
        return sorted(order[:k])

    if strategy == "distance_sum":
        total_distances = np.sum(user_candidate_distances, axis=0)
        order = sorted(all_indices, key=lambda idx: (total_distances[idx], -densities[idx], idx))
        return sorted(order[:k])

    if strategy == "greedy_marginal":
        selected = []
        remaining = set(all_indices)
        for _ in range(k):
            best_idx = None
            best_cost = float("inf")
            for idx in sorted(remaining):
                trial = selected + [idx]
                cost = coverage_cost_from_matrix(trial, user_candidate_distances, coverage_radius)
                if cost < best_cost - 1e-9:
                    best_idx = idx
                    best_cost = cost
            selected.append(best_idx)
            remaining.remove(best_idx)
        return sorted(selected)

    if strategy == "density_diverse":
        selected = []
        remaining = set(all_indices)
        density_score = normalize(densities)
        max_candidate_distance = np.max(candidate_distances) or 1.0
        for _ in range(k):
            best_idx = None
            best_score = -float("inf")
            for idx in sorted(remaining):
                if selected:
                    spread = float(np.min(candidate_distances[idx, selected]) / max_candidate_distance)
                else:
                    spread = 1.0
                score = 0.7 * density_score[idx] + 0.3 * spread
                if score > best_score + 1e-12:
                    best_idx = idx
                    best_score = score
            selected.append(best_idx)
            remaining.remove(best_idx)
        return sorted(selected)

    raise ValueError(f"Unknown initialization strategy: {strategy}")


def cls_local_search(initial, user_candidate_distances, coverage_radius, max_iter=200, improve_factor=0.999):
    current_solution = list(initial)
    current_cost = coverage_cost_from_matrix(current_solution, user_candidate_distances, coverage_radius)
    num_candidates = user_candidate_distances.shape[1]
    iteration_log = []

    iter_count = 0
    while iter_count < max_iter:
        improved = False
        current_set = set(current_solution)
        for old_idx in list(current_solution):
            for new_idx in range(num_candidates):
                if new_idx in current_set:
                    continue
                trial = current_solution.copy()
                trial.remove(old_idx)
                trial.append(new_idx)
                trial = sorted(trial)
                trial_cost = coverage_cost_from_matrix(trial, user_candidate_distances, coverage_radius)
                if trial_cost < current_cost * improve_factor:
                    current_solution = trial
                    current_cost = trial_cost
                    improved = True
                    iteration_log.append(
                        {
                            "iter": iter_count,
                            "cost": current_cost,
                            "solution": current_solution.copy(),
                        }
                    )
                    break
            if improved:
                break
        if not improved:
            break
        iter_count += 1

    return current_solution, current_cost, iteration_log


def expand_config_names(names):
    if names == ["all_new"]:
        selected = OrderedDict()
        for name, config in EXPERIMENT_CONFIGS.items():
            if "_new" in config["data_file"]:
                selected[name] = config
        return selected
    return select_configs(names)


def parse_strategies(raw):
    if raw == ["all"]:
        return list(STRATEGY_LABELS.keys())
    unknown = [name for name in raw if name not in STRATEGY_LABELS]
    if unknown:
        raise ValueError(f"Unknown strategy: {', '.join(unknown)}. Known: {', '.join(STRATEGY_LABELS.keys())}")
    return raw


def jaccard(left, right):
    left = set(left)
    right = set(right)
    if not left and not right:
        return 1.0
    return len(left & right) / len(left | right)


def run_config(config_name, config, strategies, random_runs, seed, coverage_radius, max_iter, improve_factor):
    candidate_positions, user_positions, _ = load_input_from_excel(config["data_file"])
    k, n2_raw, active_indices, densities = resolve_k(
        candidate_positions,
        user_positions,
        sigma_min=config["sigma_min"],
        n2_adjust=config["n2_adjust"],
        coverage_radius=coverage_radius,
        target_servers=config["target_servers"],
    )
    user_candidate_distances = pairwise_user_candidate_distances(user_positions, candidate_positions)
    candidate_distances = pairwise_candidate_distances(candidate_positions)

    rows = []
    for strategy in strategies:
        runs = random_runs if strategy == "random" else 1
        for run_id in range(runs):
            run_seed = seed + run_id if strategy == "random" else seed
            rng = random.Random(run_seed)
            init = initial_solution(strategy, k, rng, user_candidate_distances, candidate_distances, coverage_radius)
            init_cost = coverage_cost_from_matrix(init, user_candidate_distances, coverage_radius)
            final_solution, final_cost, log = cls_local_search(
                init,
                user_candidate_distances,
                coverage_radius,
                max_iter=max_iter,
                improve_factor=improve_factor,
            )
            rows.append(
                {
                    "Config": config_name,
                    "DataFile": config["data_file"],
                    "Strategy": strategy,
                    "StrategyLabel": STRATEGY_LABELS[strategy],
                    "RunID": run_id,
                    "Seed": run_seed,
                    "K": k,
                    "N2Raw": n2_raw,
                    "Users": len(user_positions),
                    "Candidates": len(candidate_positions),
                    "InitialCost": init_cost,
                    "FinalCost": final_cost,
                    "ImprovementPct": 100.0 * (init_cost - final_cost) / max(init_cost, 1e-12),
                    "Iterations": len(log),
                    "InitialCoverage": coverage_ratio(init, user_candidate_distances, coverage_radius),
                    "FinalCoverage": coverage_ratio(final_solution, user_candidate_distances, coverage_radius),
                    "InitialSolution": " ".join(map(str, init)),
                    "FinalSolution": " ".join(map(str, sorted(final_solution))),
                }
            )

    frame = pd.DataFrame(rows)
    best_cost = frame["FinalCost"].min()
    best_solutions = [
        set(map(int, value.split()))
        for value in frame.loc[np.isclose(frame["FinalCost"], best_cost), "FinalSolution"].tolist()
    ]
    frame["FinalGapPct"] = 100.0 * (frame["FinalCost"] - best_cost) / max(best_cost, 1e-12)
    frame["JaccardToBest"] = frame["FinalSolution"].apply(
        lambda value: max(jaccard(map(int, value.split()), solution) for solution in best_solutions)
    )
    return frame


def summarize(results):
    rows = []
    for (config, strategy), group in results.groupby(["Config", "Strategy"], sort=False):
        final = group["FinalCost"].to_numpy(dtype=float)
        final_mean = float(np.mean(final))
        final_std = float(np.std(final, ddof=1)) if len(final) > 1 else 0.0
        final_cv = 100.0 * final_std / final_mean if abs(final_mean) > 1e-12 else 0.0
        rows.append(
            {
                "Config": config,
                "Strategy": strategy,
                "StrategyLabel": group["StrategyLabel"].iloc[0],
                "Runs": len(group),
                "InitialMean": group["InitialCost"].mean(),
                "FinalMean": final_mean,
                "FinalStd": final_std,
                "FinalMin": np.min(final),
                "FinalMax": np.max(final),
                "FinalCVPct": final_cv,
                "MeanGapPct": group["FinalGapPct"].mean(),
                "BestGapPct": group["FinalGapPct"].min(),
                "MeanIterations": group["Iterations"].mean(),
                "MeanImprovementPct": group["ImprovementPct"].mean(),
                "MeanFinalCoverage": group["FinalCoverage"].mean(),
                "MeanJaccardToBest": group["JaccardToBest"].mean(),
            }
        )
    return pd.DataFrame(rows)


def save_outputs(results, summary):
    paper_table = make_paper_table(summary)
    detail_csv = os.path.join(PROJECT_ROOT, "output", "csv", "cls_init_sensitivity_detail.csv")
    summary_csv = os.path.join(PROJECT_ROOT, "output", "csv", "cls_init_sensitivity_summary.csv")
    paper_csv = os.path.join(PROJECT_ROOT, "output", "csv", "cls_init_sensitivity_paper_table.csv")
    detail_xlsx = os.path.join(PROJECT_ROOT, "output", "excel", "cls_init_sensitivity_detail.xlsx")
    summary_xlsx = os.path.join(PROJECT_ROOT, "output", "excel", "cls_init_sensitivity_summary.xlsx")
    paper_xlsx = os.path.join(PROJECT_ROOT, "output", "excel", "cls_init_sensitivity_paper_table.xlsx")
    results.to_csv(detail_csv, index=False)
    summary.to_csv(summary_csv, index=False)
    paper_table.to_csv(paper_csv, index=False)
    results.to_excel(detail_xlsx, index=False)
    summary.to_excel(summary_xlsx, index=False)
    paper_table.to_excel(paper_xlsx, index=False)
    return detail_csv, summary_csv, paper_csv, detail_xlsx, summary_xlsx, paper_xlsx


def make_paper_table(summary):
    rows = []
    for config, group in summary.groupby("Config", sort=False):
        indexed = group.set_index("Strategy")
        random_row = indexed.loc["random"] if "random" in indexed.index else None
        deterministic = group[group["Strategy"] != "random"].copy()
        best_gap = float(group["MeanGapPct"].min())
        worst_gap = float(group["MeanGapPct"].max())
        best_det = deterministic.loc[deterministic["MeanGapPct"].idxmin(), "StrategyLabel"] if not deterministic.empty else ""
        greedy_gap = float(indexed.loc["greedy_marginal", "MeanGapPct"]) if "greedy_marginal" in indexed.index else np.nan
        rows.append(
            {
                "Config": config,
                "RandomMeanGapPct": float(random_row["MeanGapPct"]) if random_row is not None else np.nan,
                "RandomCVPct": float(random_row["FinalCVPct"]) if random_row is not None else np.nan,
                "BestDeterministicInit": best_det,
                "BestObservedGapPct": best_gap,
                "WorstGapPct": worst_gap,
                "GreedyGapPct": greedy_gap,
            }
        )
    return pd.DataFrame(rows)


def plot_config_boxplots(results):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False
    paths = []
    for config, group in results.groupby("Config", sort=False):
        strategies = [strategy for strategy in STRATEGY_LABELS if strategy in set(group["Strategy"])]
        data = [group.loc[group["Strategy"] == strategy, "FinalGapPct"].to_numpy(dtype=float) for strategy in strategies]
        labels = [STRATEGY_LABELS[strategy] for strategy in strategies]
        colors = [STRATEGY_COLORS[strategy] for strategy in strategies]

        fig, ax = plt.subplots(figsize=(6.5, 3.8), constrained_layout=True)
        box = ax.boxplot(data, patch_artist=True, labels=labels, showmeans=True, widths=0.55)
        for patch, color in zip(box["boxes"], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.58)
            patch.set_edgecolor("black")
        for median in box["medians"]:
            median.set_color("black")
            median.set_linewidth(1.2)

        for idx, values in enumerate(data, start=1):
            jitter = np.linspace(-0.06, 0.06, len(values)) if len(values) > 1 else np.array([0.0])
            ax.scatter(
                np.full(len(values), idx) + jitter,
                values,
                s=28,
                color=colors[idx - 1],
                edgecolors="white",
                linewidths=0.35,
                zorder=3,
            )

        ax.set_xlabel("Initialization", fontsize=11)
        ax.set_ylabel("Gap to best final cost (%)", fontsize=11)
        ax.tick_params(axis="both", labelsize=10)
        ax.grid(True, axis="y", linestyle="--", linewidth=0.75, alpha=0.72, zorder=0)
        ax.set_title(config, fontsize=12)
        max_gap = max(float(np.max(values)) if len(values) else 0.0 for values in data)
        ax.set_ylim(bottom=-0.2, top=max(1.0, max_gap * 1.18 + 0.2))

        pdf_path = os.path.join(PROJECT_ROOT, "output", "pdf", f"cls_init_sensitivity_{config}.pdf")
        png_path = os.path.join(PROJECT_ROOT, "output", "png", f"cls_init_sensitivity_{config}.png")
        fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
        fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
        plt.close(fig)
        paths.append(pdf_path)
    return paths


def plot_summary_bars(summary):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False
    configs = summary["Config"].drop_duplicates().tolist()
    strategies = [strategy for strategy in STRATEGY_LABELS if strategy in set(summary["Strategy"])]
    matrix = np.zeros((len(strategies), len(configs)), dtype=float)
    for row, strategy in enumerate(strategies):
        subset = summary[summary["Strategy"] == strategy].set_index("Config")
        for col, config in enumerate(configs):
            matrix[row, col] = subset.loc[config, "MeanGapPct"] if config in subset.index else np.nan

    fig, ax = plt.subplots(figsize=(8.2, 3.5), constrained_layout=True)
    vmax = max(float(np.nanmax(matrix)), 1.0)
    image = ax.imshow(matrix, cmap="YlOrRd", vmin=0.0, vmax=vmax, aspect="auto")

    ax.set_xticks(np.arange(len(configs)))
    ax.set_xticklabels(configs, rotation=20, ha="right", fontsize=10)
    ax.set_yticks(np.arange(len(strategies)))
    ax.set_yticklabels([STRATEGY_LABELS[strategy] for strategy in strategies], fontsize=10)
    ax.set_xlabel("Dataset configuration", fontsize=11)
    ax.set_ylabel("Initialization", fontsize=11)

    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            value = matrix[row, col]
            label = f"{value:.2f}"
            text_color = "white" if value > vmax * 0.55 else "black"
            ax.text(col, row, label, ha="center", va="center", fontsize=9, color=text_color)

    ax.set_xticks(np.arange(-0.5, len(configs), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(strategies), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    cbar = fig.colorbar(image, ax=ax, fraction=0.035, pad=0.02)
    cbar.ax.set_ylabel("Mean gap to best final cost (%)", fontsize=10)
    cbar.ax.tick_params(labelsize=9)

    pdf_path = os.path.join(PROJECT_ROOT, "output", "pdf", "cls_init_sensitivity_summary.pdf")
    png_path = os.path.join(PROJECT_ROOT, "output", "png", "cls_init_sensitivity_summary.png")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return pdf_path


def plot_fixed_130_heatmap(summary):
    configs = [config for config in ["5_130", "10_130", "15_130", "20_130"] if config in set(summary["Config"])]
    strategies = [strategy for strategy in STRATEGY_LABELS if strategy in set(summary["Strategy"])]
    if not configs:
        return None

    matrix = np.zeros((len(strategies), len(configs)), dtype=float)
    for row, strategy in enumerate(strategies):
        subset = summary[summary["Strategy"] == strategy].set_index("Config")
        for col, config in enumerate(configs):
            matrix[row, col] = subset.loc[config, "MeanGapPct"] if config in subset.index else np.nan

    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(6.4, 3.4), constrained_layout=True)
    vmax = max(float(np.nanmax(matrix)), 1.0)
    image = ax.imshow(matrix, cmap="YlOrRd", vmin=0.0, vmax=vmax, aspect="auto")

    ax.set_xticks(np.arange(len(configs)))
    ax.set_xticklabels(configs, rotation=18, ha="right", fontsize=10)
    ax.set_yticks(np.arange(len(strategies)))
    ax.set_yticklabels([STRATEGY_LABELS[strategy] for strategy in strategies], fontsize=10)
    ax.set_xlabel("Server scale with 130 users", fontsize=11)
    ax.set_ylabel("Initialization", fontsize=11)

    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            value = matrix[row, col]
            ax.text(col, row, f"{value:.2f}", ha="center", va="center", fontsize=9, color="black")

    ax.set_xticks(np.arange(-0.5, len(configs), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(strategies), 1), minor=True)
    ax.grid(which="minor", color="white", linestyle="-", linewidth=1.2)
    ax.tick_params(which="minor", bottom=False, left=False)
    for spine in ax.spines.values():
        spine.set_visible(False)

    cbar = fig.colorbar(image, ax=ax, fraction=0.045, pad=0.02)
    cbar.ax.set_ylabel("Mean gap to best final cost (%)", fontsize=10)
    cbar.ax.tick_params(labelsize=9)

    pdf_path = os.path.join(PROJECT_ROOT, "output", "pdf", "cls_init_sensitivity_130_heatmap.pdf")
    png_path = os.path.join(PROJECT_ROOT, "output", "png", "cls_init_sensitivity_130_heatmap.png")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return pdf_path


def plot_random_greedy_case(summary, config_name="10_150"):
    group = summary[summary["Config"] == config_name].set_index("Strategy")
    required = ["random", "greedy_marginal"]
    if not all(strategy in group.index for strategy in required):
        return None

    labels = [STRATEGY_LABELS[strategy] for strategy in required]
    values = [float(group.loc[strategy, "MeanGapPct"]) for strategy in required]
    colors = [STRATEGY_COLORS[strategy] for strategy in required]

    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(3.6, 3.2), constrained_layout=True)
    bars = ax.bar(
        np.arange(len(labels)),
        values,
        color=colors,
        edgecolor="black",
        linewidth=0.5,
        width=0.55,
        zorder=3,
    )
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + max(values) * 0.03,
            f"{value:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Mean gap to best final cost (%)", fontsize=10)
    ax.set_title(config_name, fontsize=11)
    ax.set_ylim(0, max(values) * 1.22 + 0.4)
    ax.tick_params(axis="y", labelsize=9)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.75, alpha=0.72, zorder=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)

    pdf_path = os.path.join(PROJECT_ROOT, "output", "pdf", f"cls_init_random_vs_greedy_{config_name}.pdf")
    png_path = os.path.join(PROJECT_ROOT, "output", "png", f"cls_init_random_vs_greedy_{config_name}.png")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return pdf_path


def main():
    parser = argparse.ArgumentParser(description="Run CLS initialization sensitivity experiments for Stage I.")
    parser.add_argument(
        "--configs",
        nargs="+",
        default=["10_130"],
        help="Config names, all, or all_new. Known: " + ", ".join(EXPERIMENT_CONFIGS.keys()),
    )
    parser.add_argument(
        "--strategies",
        nargs="+",
        default=["all"],
        help="Initialization strategies, or all. Known: " + ", ".join(STRATEGY_LABELS.keys()),
    )
    parser.add_argument("--random-runs", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--coverage-radius", type=float, default=1.5)
    parser.add_argument("--max-iter", type=int, default=200)
    parser.add_argument("--improve-factor", type=float, default=0.999)
    args = parser.parse_args()

    ensure_dirs()
    configs = expand_config_names(args.configs)
    strategies = parse_strategies(args.strategies)

    all_results = []
    for config_name, config in configs.items():
        print(f"Running CLS initialization sensitivity: {config_name}")
        frame = run_config(
            config_name=config_name,
            config=config,
            strategies=strategies,
            random_runs=args.random_runs,
            seed=args.seed,
            coverage_radius=args.coverage_radius,
            max_iter=args.max_iter,
            improve_factor=args.improve_factor,
        )
        all_results.append(frame)

    results = pd.concat(all_results, ignore_index=True)
    summary = summarize(results)
    detail_csv, summary_csv, paper_csv, detail_xlsx, summary_xlsx, paper_xlsx = save_outputs(results, summary)
    config_plot_paths = plot_config_boxplots(results)
    summary_plot_path = plot_summary_bars(summary)
    fixed_130_path = plot_fixed_130_heatmap(summary)
    random_greedy_path = plot_random_greedy_case(summary, config_name="10_150")

    print("\n=== CLS Initialization Sensitivity Summary ===")
    cols = ["Config", "StrategyLabel", "Runs", "FinalMean", "FinalStd", "FinalCVPct", "MeanGapPct", "MeanIterations"]
    print(summary[cols].to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("Saved:", detail_csv)
    print("Saved:", summary_csv)
    print("Saved:", paper_csv)
    print("Saved:", detail_xlsx)
    print("Saved:", summary_xlsx)
    print("Saved:", paper_xlsx)
    for path in config_plot_paths:
        print("Saved:", path)
    print("Saved:", summary_plot_path)
    if fixed_130_path:
        print("Saved:", fixed_130_path)
    if random_greedy_path:
        print("Saved:", random_greedy_path)


if __name__ == "__main__":
    main()
