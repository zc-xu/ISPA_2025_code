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
from matplotlib.ticker import FormatStrFormatter, MaxNLocator


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from LocalSearch.batch_service_experiments import METHOD_OUTPUTS, run_nsga_methods
from LocalSearch.experiment_configs import EXPERIMENT_CONFIGS
from LocalSearch.experiment_utils import (
    build_stage_context,
    compute_density_for_stations,
    haversine_distance,
    load_input_from_excel,
)
from LocalSearch.pareto_batch_metrics import METHOD_COLORS, run as run_pareto_metrics


BASE_CONFIG_NAME = "10_130"
GENERALIZATION_DIR = os.path.join(PROJECT_ROOT, "data", "generalization")
OUT_CSV_DIR = os.path.join(PROJECT_ROOT, "output", "csv")
OUT_XLSX_DIR = os.path.join(PROJECT_ROOT, "output", "excel")
OUT_PNG_DIR = os.path.join(PROJECT_ROOT, "output", "png")
OUT_PDF_DIR = os.path.join(PROJECT_ROOT, "output", "pdf")
OUT_NPZ_DIR = os.path.join(PROJECT_ROOT, "output", "npz")


SCENARIOS = OrderedDict(
    [
        (
            "sparse_suburban",
            {
                "config_name": "gen_sparse_suburban_10_130",
                "data_file": "data/generalization/input_data_gen_sparse_suburban_10_130_8.xlsx",
                "description": "Synthetic sparse suburban-like distribution with one main hotspot and dispersed users.",
            },
        ),
        (
            "uniform_large",
            {
                "config_name": "gen_uniform_large_10_130",
                "data_file": "data/generalization/input_data_gen_uniform_large_10_130_8.xlsx",
                "description": "Synthetic large-area uniform distribution with lower spatial concentration.",
            },
        ),
        (
            "clustered_hotspot",
            {
                "config_name": "gen_clustered_hotspot_10_130",
                "data_file": "data/generalization/input_data_gen_clustered_hotspot_10_130_8.xlsx",
                "description": "Synthetic heterogeneous traffic distribution with two strong hotspots.",
            },
        ),
    ]
)

SCENARIO_SEED_OFFSETS = {
    "sparse_suburban": 101,
    "uniform_large": 202,
    "clustered_hotspot": 303,
}

SCENARIO_DISPLAY_NAMES = {
    "Xizhimen real-data baseline": "Xizhimen baseline",
    "sparse_suburban": "Sparse suburban",
    "uniform_large": "Large-area uniform",
    "clustered_hotspot": "Clustered hotspots",
}


def ensure_dirs():
    for path in (GENERALIZATION_DIR, OUT_CSV_DIR, OUT_XLSX_DIR, OUT_PNG_DIR, OUT_PDF_DIR, OUT_NPZ_DIR):
        os.makedirs(path, exist_ok=True)


def sample_services(base_services, n_users, rng, scenario):
    num_services = int(np.max(base_services) + 1)
    counts = np.bincount(base_services.astype(int), minlength=num_services).astype(float)
    base_prob = counts / max(counts.sum(), 1.0)

    if scenario == "clustered_hotspot":
        prob = 0.65 * base_prob
        hot = int(np.argmax(base_prob))
        prob[hot] += 0.25
        prob[(hot + 1) % num_services] += 0.10
        prob = prob / prob.sum()
    elif scenario == "sparse_suburban":
        prob = 0.80 * base_prob + 0.20 / num_services
        prob = prob / prob.sum()
    else:
        prob = base_prob

    return rng.choice(np.arange(num_services), size=n_users, p=prob).astype(int)


def expanded_box(points, factor):
    center = np.mean(points, axis=0)
    span = np.ptp(points, axis=0)
    span = np.maximum(span, np.array([0.01, 0.01]))
    low = center - 0.5 * factor * span
    high = center + 0.5 * factor * span
    return center, low, high


def clipped_normal(rng, center, scale, low, high, n):
    samples = rng.normal(loc=center, scale=scale, size=(n, 2))
    return np.clip(samples, low, high)


def generate_positions(base_candidates, base_users, n_candidates, n_users, scenario, rng):
    reference = np.vstack([base_candidates, base_users])

    if scenario == "uniform_large":
        center, low, high = expanded_box(reference, factor=2.2)
        candidates = rng.uniform(low=low, high=high, size=(n_candidates, 2))
        users = rng.uniform(low=low, high=high, size=(n_users, 2))
        return candidates, users

    if scenario == "clustered_hotspot":
        center, low, high = expanded_box(reference, factor=1.7)
        span = high - low
        centers = np.array(
            [
                center + np.array([-0.25 * span[0], 0.10 * span[1]]),
                center + np.array([0.24 * span[0], -0.12 * span[1]]),
                center + np.array([0.05 * span[0], 0.28 * span[1]]),
            ]
        )
        candidates = np.vstack(
            [
                rng.uniform(low=low, high=high, size=(max(n_candidates - 6, 0), 2)),
                clipped_normal(rng, centers[0], span * 0.06, low, high, 3),
                clipped_normal(rng, centers[1], span * 0.06, low, high, 3),
            ]
        )[:n_candidates]
        n1 = int(n_users * 0.55)
        n2 = int(n_users * 0.30)
        n3 = n_users - n1 - n2
        users = np.vstack(
            [
                clipped_normal(rng, centers[0], span * 0.08, low, high, n1),
                clipped_normal(rng, centers[1], span * 0.07, low, high, n2),
                rng.uniform(low=low, high=high, size=(n3, 2)),
            ]
        )
        return candidates, users

    center, low, high = expanded_box(reference, factor=2.0)
    span = high - low
    centers = np.array(
        [
            center + np.array([-0.28 * span[0], 0.18 * span[1]]),
            center + np.array([0.22 * span[0], -0.22 * span[1]]),
        ]
    )
    candidates = rng.uniform(low=low, high=high, size=(n_candidates, 2))
    n1 = int(n_users * 0.45)
    n2 = int(n_users * 0.25)
    n3 = n_users - n1 - n2
    users = np.vstack(
        [
            clipped_normal(rng, centers[0], span * 0.10, low, high, n1),
            clipped_normal(rng, centers[1], span * 0.14, low, high, n2),
            rng.uniform(low=low, high=high, size=(n3, 2)),
        ]
    )
    return candidates, users


def choose_density_parameters(candidate_positions, user_positions, target_servers, coverage_radius):
    _, densities, _ = compute_density_for_stations(
        candidate_positions,
        user_positions,
        coverage_radius=coverage_radius,
        sigma_min=1,
    )
    max_density = max(max(densities), 1)
    choices = []
    for sigma in range(1, int(max_density) + 1):
        active = sum(1 for d in densities if d >= sigma)
        choices.append((abs(active - target_servers), -active, sigma, active))
    _, _, sigma_min, n2_raw = min(choices)
    n2_adjust = target_servers - n2_raw
    return int(sigma_min), int(n2_adjust), densities


def write_dataset(path, candidate_positions, user_positions, user_services):
    full_path = path if os.path.isabs(path) else os.path.join(PROJECT_ROOT, path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with pd.ExcelWriter(full_path) as writer:
        pd.DataFrame(candidate_positions, columns=["lng", "lat"]).to_excel(writer, sheet_name="candidates", index=False)
        pd.DataFrame(user_positions, columns=["lng", "lat"]).to_excel(writer, sheet_name="users", index=False)
        pd.DataFrame({"svc_type": user_services.astype(int)}).to_excel(writer, sheet_name="services", index=False)
    return full_path


def create_synthetic_config(scenario, seed, coverage_radius, force=False):
    if scenario not in SCENARIOS:
        known = ", ".join(SCENARIOS.keys())
        raise ValueError(f"Unknown scenario: {scenario}. Known: {known}")

    base_cfg = EXPERIMENT_CONFIGS[BASE_CONFIG_NAME]
    base_candidates, base_users, base_services = load_input_from_excel(base_cfg["data_file"])
    spec = SCENARIOS[scenario]
    full_path = os.path.join(PROJECT_ROOT, spec["data_file"])
    rng = np.random.default_rng(seed + SCENARIO_SEED_OFFSETS[scenario])

    if force or not os.path.exists(full_path):
        candidates, users = generate_positions(
            base_candidates=base_candidates,
            base_users=base_users,
            n_candidates=len(base_candidates),
            n_users=base_cfg["users"],
            scenario=scenario,
            rng=rng,
        )
        services = sample_services(base_services, len(users), rng, scenario)
        write_dataset(spec["data_file"], candidates, users, services)

    candidates, users, services = load_input_from_excel(spec["data_file"])
    sigma_min, n2_adjust, densities = choose_density_parameters(
        candidates,
        users,
        target_servers=base_cfg["target_servers"],
        coverage_radius=coverage_radius,
    )

    cfg = {
        "data_file": spec["data_file"],
        "target_servers": base_cfg["target_servers"],
        "sigma_min": sigma_min,
        "n2_adjust": n2_adjust,
        "series": "generalization",
        "users": len(users),
        "description": spec["description"],
    }
    return spec["config_name"], cfg, densities


def result_files_exist(config_name):
    for output_stem in METHOD_OUTPUTS.values():
        path = os.path.join(OUT_NPZ_DIR, f"{output_stem}_{config_name}.npz")
        if not os.path.exists(path):
            return False
    return True


def km_extent(points):
    lon_min, lat_min = np.min(points, axis=0)
    lon_max, lat_max = np.max(points, axis=0)
    width = haversine_distance(lon_min, lat_min, lon_max, lat_min)
    height = haversine_distance(lon_min, lat_min, lon_min, lat_max)
    return width, height


def nearest_neighbor_mean(points):
    if len(points) < 2:
        return 0.0
    distances = []
    for i, point in enumerate(points):
        others = np.delete(points, i, axis=0)
        distances.append(
            min(haversine_distance(point[0], point[1], other[0], other[1]) for other in others)
        )
    return float(np.mean(distances))


def service_entropy(services):
    counts = np.bincount(services.astype(int))
    prob = counts[counts > 0] / counts.sum()
    return float(-np.sum(prob * np.log(prob)))


def describe_context(config_name, config, context, densities, scenario_label):
    all_points = np.vstack([context["candidate_positions"], context["user_positions"]])
    width_km, height_km = km_extent(all_points)
    density_arr = np.asarray(densities, dtype=float)
    density_mean = float(np.mean(density_arr))
    density_std = float(np.std(density_arr))
    density_cv = density_std / density_mean if density_mean > 0 else 0.0
    row = {
        "Config": config_name,
        "Scenario": scenario_label,
        "DataFile": config["data_file"],
        "Users": int(len(context["user_positions"])),
        "Candidates": int(len(context["candidate_positions"])),
        "TargetServers": int(config["target_servers"]),
        "ResolvedK": int(context["k"]),
        "SigmaMin": int(config["sigma_min"]),
        "N2Adjust": int(config["n2_adjust"]),
        "Stage1Cost": float(context["best_cost"]),
        "BBoxWidthKm": float(width_km),
        "BBoxHeightKm": float(height_km),
        "UserNNMeanKm": nearest_neighbor_mean(context["user_positions"]),
        "StationDensityMean": density_mean,
        "StationDensityStd": density_std,
        "StationDensityCV": float(density_cv),
        "ServiceEntropy": service_entropy(context["user_services"]),
    }
    return row


def plot_topology(config_name, context, scenario_label):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False

    candidates = context["candidate_positions"]
    users = context["user_positions"]
    selected = context["servers_pos"]

    fig, ax = plt.subplots(figsize=(6.8, 5.2))
    ax.scatter(users[:, 0], users[:, 1], s=24, color="#4C78A8", alpha=0.72, label="Users", zorder=2)
    ax.scatter(candidates[:, 0], candidates[:, 1], s=52, marker="^", color="#9CA3AF", edgecolor="white", linewidth=0.4, label="Candidates", zorder=3)
    ax.scatter(selected[:, 0], selected[:, 1], s=100, marker="*", color="#C1121F", edgecolor="black", linewidth=0.4, label="Selected servers", zorder=4)
    ax.set_xlabel("longitude", fontsize=16)
    ax.set_ylabel("latitude", fontsize=16)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    ax.tick_params(axis="both", labelsize=12)
    ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.55, zorder=0)
    ax.legend(fontsize=11, frameon=True, edgecolor="lightgray")
    ax.set_title(SCENARIO_DISPLAY_NAMES.get(scenario_label, scenario_label), fontsize=14, pad=8)
    fig.tight_layout()

    png_path = os.path.join(OUT_PNG_DIR, f"generalization_topology_{config_name}.png")
    pdf_path = os.path.join(OUT_PDF_DIR, f"generalization_topology_{config_name}.pdf")
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def plot_metric_summary(all_metrics):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False

    metrics = ["HV", "IGD", "BestQ"]
    ylabels = ["HV (higher better)", "IGD (lower better)", "Best Q (lower better)"]
    scenarios = list(OrderedDict.fromkeys(all_metrics["Scenario"].tolist()))
    scenario_labels = [SCENARIO_DISPLAY_NAMES.get(item, item) for item in scenarios]
    methods = list(OrderedDict.fromkeys(all_metrics["Method"].tolist()))

    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.1))
    width = 0.18
    x = np.arange(len(scenarios))

    for ax, metric, ylabel in zip(axes, metrics, ylabels):
        for idx, method in enumerate(methods):
            vals = []
            for scenario in scenarios:
                match = all_metrics[(all_metrics["Scenario"] == scenario) & (all_metrics["Method"] == method)]
                vals.append(float(match[metric].iloc[0]) if not match.empty else np.nan)
            offset = (idx - (len(methods) - 1) / 2.0) * width
            ax.bar(
                x + offset,
                vals,
                width=width,
                label=method if metric == metrics[0] else None,
                color=METHOD_COLORS.get(method, "#4B5563"),
                edgecolor="black",
                linewidth=0.35,
                zorder=3,
            )
        ax.set_xticks(x)
        ax.set_xticklabels(scenario_labels, fontsize=10, rotation=18, ha="right")
        ax.set_ylabel(ylabel, fontsize=12)
        ax.tick_params(axis="y", labelsize=10)
        ax.grid(True, axis="y", linestyle="--", linewidth=0.7, alpha=0.65, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.02),
        fontsize=10,
        frameon=True,
        edgecolor="lightgray",
        ncol=len(methods),
    )
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    png_path = os.path.join(OUT_PNG_DIR, "generalization_pareto_metrics_summary.png")
    pdf_path = os.path.join(OUT_PDF_DIR, "generalization_pareto_metrics_summary.pdf")
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def build_run_plan(args):
    plan = OrderedDict()
    if args.include_baseline:
        plan[BASE_CONFIG_NAME] = ("Xizhimen real-data baseline", EXPERIMENT_CONFIGS[BASE_CONFIG_NAME], None)
    for scenario in args.scenarios:
        config_name, cfg, densities = create_synthetic_config(
            scenario=scenario,
            seed=args.seed,
            coverage_radius=args.coverage_radius,
            force=args.regenerate_data,
        )
        plan[config_name] = (scenario, cfg, densities)
    return plan


def run_experiments(args):
    ensure_dirs()
    plan = build_run_plan(args)

    stage_rows = []
    metric_frames = []
    generated_topology = []

    for config_name, (scenario_label, config, precomputed_densities) in plan.items():
        print(f"\n=== Generalization config: {config_name} ({scenario_label}) ===")
        context = build_stage_context(
            config,
            seed=args.seed,
            coverage_radius=args.coverage_radius,
            max_iter=args.stage1_iter,
            verbose=False,
        )
        if precomputed_densities is None:
            _, precomputed_densities, _ = compute_density_for_stations(
                context["candidate_positions"],
                context["user_positions"],
                coverage_radius=args.coverage_radius,
                sigma_min=config["sigma_min"],
            )
        stage_rows.append(describe_context(config_name, config, context, precomputed_densities, scenario_label))
        generated_topology.append(plot_topology(config_name, context, scenario_label))

        if args.skip_nsga:
            print(f"[{config_name}] Skip NSGA-II runs.")
        elif result_files_exist(config_name) and args.reuse_npz and not args.force_nsga:
            print(f"[{config_name}] Reusing existing NSGA-II result npz files.")
        else:
            run_nsga_methods(
                config_name=config_name,
                context=context,
                pop_size=args.pop_size,
                n_gen=args.n_gen,
                seed=args.seed,
                visualize_hybrid_process=False,
            )

        if not args.skip_metrics:
            metrics = run_pareto_metrics(config_name=config_name, alpha=args.metric_alpha)
            metrics = metrics.copy()
            metrics["Scenario"] = scenario_label
            metric_frames.append(metrics)

    stage_df = pd.DataFrame(stage_rows)
    stage_csv = os.path.join(OUT_CSV_DIR, "generalization_stage1_summary.csv")
    stage_xlsx = os.path.join(OUT_XLSX_DIR, "generalization_stage1_summary.xlsx")
    stage_df.to_csv(stage_csv, index=False)
    stage_df.to_excel(stage_xlsx, index=False)
    print(f"Saved: {stage_csv}")
    print(f"Saved: {stage_xlsx}")

    if metric_frames:
        all_metrics = pd.concat(metric_frames, ignore_index=True)
        metric_csv = os.path.join(OUT_CSV_DIR, "generalization_pareto_metrics_summary.csv")
        metric_xlsx = os.path.join(OUT_XLSX_DIR, "generalization_pareto_metrics_summary.xlsx")
        all_metrics.to_csv(metric_csv, index=False)
        all_metrics.to_excel(metric_xlsx, index=False)
        summary_png, summary_pdf = plot_metric_summary(all_metrics)
        print(f"Saved: {metric_csv}")
        print(f"Saved: {metric_xlsx}")
        print(f"Saved: {summary_png}")
        print(f"Saved: {summary_pdf}")

    for png_path, pdf_path in generated_topology:
        print(f"Saved: {png_path}")
        print(f"Saved: {pdf_path}")


def main():
    parser = argparse.ArgumentParser(description="Run scale and geography generalization checks for MOS2.")
    parser.add_argument("--scenarios", nargs="+", default=["sparse_suburban"], choices=list(SCENARIOS.keys()))
    parser.add_argument("--include-baseline", action="store_true", default=True)
    parser.add_argument("--no-baseline", dest="include_baseline", action="store_false")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--coverage-radius", type=float, default=1.5)
    parser.add_argument("--stage1-iter", type=int, default=200)
    parser.add_argument("--pop-size", type=int, default=40)
    parser.add_argument("--n-gen", type=int, default=100)
    parser.add_argument("--metric-alpha", type=float, default=0.5)
    parser.add_argument("--reuse-npz", action="store_true", default=True)
    parser.add_argument("--force-nsga", action="store_true")
    parser.add_argument("--regenerate-data", action="store_true")
    parser.add_argument("--skip-nsga", action="store_true")
    parser.add_argument("--skip-metrics", action="store_true")
    args = parser.parse_args()
    run_experiments(args)


if __name__ == "__main__":
    main()
