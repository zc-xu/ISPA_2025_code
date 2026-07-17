import argparse
import glob
import os
import re
import sys
from collections import OrderedDict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, MaxNLocator
import numpy as np
import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from LocalSearch.experiment_utils import (
    build_stage_context,
    compute_density_for_stations,
    haversine_distance,
    load_input_from_excel,
)
from LocalSearch.real_region_generalization import km_extent, nearest_neighbor_mean


OUT_CSV = os.path.join(PROJECT_ROOT, "output", "csv")
OUT_PNG = os.path.join(PROJECT_ROOT, "output", "png")
OUT_PDF = os.path.join(PROJECT_ROOT, "output", "pdf")

ORIGINAL_DATA = "data/input_data_10_130_8_new.xlsx"
MAIN_CONFIG = "real_sparse_r04_c40_u130_k10_s1"
MAIN_DATA = f"data/real_region/input_data_{MAIN_CONFIG}_8.xlsx"
MAIN_STAGE1_CSV = os.path.join(OUT_CSV, "real_region_stage1_screen_c40_u130_k10.csv")
MAIN_METRIC_GLOB = os.path.join(
    OUT_CSV, "seed_checks", f"pareto_metrics_{MAIN_CONFIG}_seed*.csv"
)

WIDE_RUN = "review6_large_c40_u130_k10"
WIDE_STAGE1_CSV = os.path.join(OUT_CSV, f"real_region_stage1_screen_{WIDE_RUN}.csv")
WIDE_LOG_GLOB = os.path.join(
    PROJECT_ROOT, "output", "logs", "*review6_large_region_stage2_seed*.log"
)
WIDE_DETAIL_FALLBACK = os.path.join(OUT_CSV, "reviewer6_large_region_stage2_detail.csv")

METHODS = ["NS-P", "GCP", "GDP", "PSP"]
METHOD_COLORS = {
    "NS-P": "#1f77b4",
    "GCP": "#2ca02c",
    "GDP": "#ff7f0e",
    "PSP": "#d62728",
}
SCENARIOS = OrderedDict(
    [
        ("sparse", "Sparse"),
        ("clustered", "Clustered"),
        ("skewed", "Skewed"),
    ]
)


def ensure_dirs():
    for path in (OUT_CSV, OUT_PNG, OUT_PDF):
        os.makedirs(path, exist_ok=True)


def scenario_from_config(config):
    for scenario in SCENARIOS:
        if f"_{scenario}_" in config:
            return scenario
    raise ValueError(f"Cannot identify scenario from {config}.")


def parse_wide_logs():
    pattern = re.compile(
        r"^\s*(NS-P|GCP|GDP|PSP)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)"
        r"\s+([0-9.]+)\s+(\d+)\s+(\d+)\s+([0-9.]+)\s+([0-9.]+)"
    )
    marker = "_review6_large_region_stage2_seed"
    rows = []
    for path in sorted(glob.glob(WIDE_LOG_GLOB)):
        filename = os.path.basename(path)
        if marker not in filename:
            continue
        config, seed_text = filename.rsplit(marker, 1)
        seed = int(seed_text.replace(".log", ""))
        with open(path, encoding="utf-8") as source:
            for line in source:
                match = pattern.match(line)
                if not match:
                    continue
                rows.append(
                    {
                        "Config": config,
                        "Scenario": scenario_from_config(config),
                        "Seed": seed,
                        "Method": match.group(1),
                        "HV": float(match.group(2)),
                        "IGD": float(match.group(3)),
                        "Spacing": float(match.group(4)),
                        "BestQ": float(match.group(5)),
                        "BestFrontQ": float(match.group(6)),
                        "ParetoCount": int(match.group(7)),
                        "SolutionCount": int(match.group(8)),
                        "BestCostNorm": float(match.group(9)),
                        "BestDelayNorm": float(match.group(10)),
                    }
                )
    if rows:
        detail = pd.DataFrame(rows)
    elif os.path.exists(WIDE_DETAIL_FALLBACK):
        detail = pd.read_csv(WIDE_DETAIL_FALLBACK)
    else:
        raise FileNotFoundError(
            "No Reviewer 6 Stage-II logs or committed detail table were found."
        )
    expected = len(SCENARIOS) * 3 * len(METHODS)
    if len(detail) != expected:
        raise ValueError(f"Expected {expected} wide-region metric rows, found {len(detail)}.")
    counts = detail.groupby(["Scenario", "Seed"])["Method"].nunique()
    if not (counts == len(METHODS)).all():
        raise ValueError("At least one scenario/seed does not contain all four methods.")
    if set(detail["Seed"]) != {42, 43, 44}:
        raise ValueError("Reviewer 6 Stage-II evidence must contain seeds 42, 43, and 44.")
    if not (detail["SolutionCount"] == 50).all():
        raise ValueError("At least one Reviewer 6 Stage-II run does not contain 50 solutions.")
    if not (detail["ParetoCount"] == 50).all():
        raise ValueError("At least one Reviewer 6 Stage-II run does not contain 50 nondominated solutions.")
    return detail


def load_main_metrics():
    frames = []
    for path in sorted(glob.glob(MAIN_METRIC_GLOB)):
        match = re.search(r"seed(\d+)", os.path.basename(path))
        if not match:
            continue
        frame = pd.read_csv(path)
        frame["Config"] = MAIN_CONFIG
        frame.insert(0, "Seed", int(match.group(1)))
        frame.insert(0, "Scenario", "alternate_sparse")
        frames.append(frame)
    if len(frames) != 3:
        raise ValueError(f"Expected three main-candidate seed files, found {len(frames)}.")
    return pd.concat(frames, ignore_index=True)


def aggregate_metrics(detail):
    grouped = detail.groupby(["Scenario", "Method"], sort=False)
    rows = []
    for (scenario, method), frame in grouped:
        row = {"Scenario": scenario, "Method": method, "Seeds": frame["Seed"].nunique()}
        for metric in ("HV", "IGD", "BestQ"):
            row[f"{metric}Mean"] = float(frame[metric].mean())
            row[f"{metric}Std"] = float(frame[metric].std(ddof=1))
        rows.append(row)
    return pd.DataFrame(rows)


def psp_gap_summary(detail):
    rows = []
    for (scenario, seed), frame in detail.groupby(["Scenario", "Seed"]):
        indexed = frame.set_index("Method")
        psp = indexed.loc["PSP"]
        rows.append(
            {
                "Scenario": scenario,
                "Seed": int(seed),
                "PSPHV": psp["HV"],
                "BestHV": frame["HV"].max(),
                "PSPHVRelativeGapPct": 100.0 * (frame["HV"].max() - psp["HV"]) / frame["HV"].max(),
                "PSPIGD": psp["IGD"],
                "BestIGD": frame["IGD"].min(),
                "PSPIGDAbsoluteGap": psp["IGD"] - frame["IGD"].min(),
                "PSPBestQ": psp["BestQ"],
                "BestBestQ": frame["BestQ"].min(),
                "PSPBestQRelativeGapPct": 100.0 * (psp["BestQ"] - frame["BestQ"].min()) / frame["BestQ"].min(),
            }
        )
    return pd.DataFrame(rows)


def selected_from_stage1(path, config):
    frame = pd.read_csv(path)
    row = frame[frame["Config"] == config]
    if len(row) != 1:
        raise ValueError(f"Expected one Stage-I row for {config}, found {len(row)}.")
    return [int(value) for value in row.iloc[0]["SelectedSolution"].split()]


def dataset_description(label, data_path, original_center, original_area, selected, source_type):
    candidates, users, services = load_input_from_excel(data_path)
    candidate_width, candidate_height = km_extent(candidates)
    user_width, user_height = km_extent(users)
    center = np.mean(candidates, axis=0)
    _, densities, _ = compute_density_for_stations(
        candidates, users, coverage_radius=1.5, sigma_min=1
    )
    density = np.asarray(densities, dtype=float)
    user_area = user_width * user_height
    return {
        "Dataset": label,
        "SourceType": source_type,
        "Candidates": len(candidates),
        "Users": len(users),
        "SelectedServers": len(selected),
        "CenterLng": center[0],
        "CenterLat": center[1],
        "CenterDistanceFromOriginalKm": haversine_distance(
            original_center[0], original_center[1], center[0], center[1]
        ),
        "CandidateWidthKm": candidate_width,
        "CandidateHeightKm": candidate_height,
        "UserWidthKm": user_width,
        "UserHeightKm": user_height,
        "UserBBoxAreaKm2": user_area,
        "AreaScaleVsOriginal": user_area / original_area,
        "StationNNMeanKm": nearest_neighbor_mean(candidates),
        "UserNNMeanKm": nearest_neighbor_mean(users),
        "CoverageDensityMean": float(density.mean()),
        "CoverageDensityCV": float(density.std() / density.mean()) if density.mean() else 0.0,
        "ServiceTypes": int(np.max(services) + 1),
        "SelectedSolution": " ".join(map(str, selected)),
        "DataFile": data_path,
    }


def build_design_table():
    original_config = {
        "data_file": ORIGINAL_DATA,
        "target_servers": 10,
        "sigma_min": 16,
        "n2_adjust": -1,
        "users": 130,
    }
    original_context = build_stage_context(original_config, seed=42, max_iter=200, verbose=False)
    original_candidates, original_users, _ = load_input_from_excel(ORIGINAL_DATA)
    original_center = np.mean(original_candidates, axis=0)
    ow, oh = km_extent(original_users)
    original_area = ow * oh

    rows = [
        dataset_description(
            "Original urban (Xizhimen)",
            ORIGINAL_DATA,
            original_center,
            original_area,
            original_context["best_solution"],
            "Original measured experiment data",
        )
    ]
    main_selected = selected_from_stage1(MAIN_STAGE1_CSV, MAIN_CONFIG)
    rows.append(
        dataset_description(
            "Alternate real region",
            MAIN_DATA,
            original_center,
            original_area,
            main_selected,
            "Real stations + reproducible sparse traffic",
        )
    )

    wide_stage1 = pd.read_csv(WIDE_STAGE1_CSV)
    for scenario, title in SCENARIOS.items():
        row = wide_stage1[wide_stage1["Config"].str.contains(f"_{scenario}_")]
        if len(row) != 1:
            raise ValueError(f"Expected one wide-region {scenario} row, found {len(row)}.")
        record = row.iloc[0]
        rows.append(
            dataset_description(
                f"Expanded real region - {title}",
                record["DataFile"],
                original_center,
                original_area,
                [int(value) for value in record["SelectedSolution"].split()],
                f"Real stations + reproducible {scenario} traffic",
            )
        )
    design = pd.DataFrame(rows)
    wide = design[design["Dataset"].str.startswith("Expanded")]
    if (wide["Candidates"] != 40).any() or (wide["AreaScaleVsOriginal"] < 2.0).any():
        raise ValueError("Expanded-region design no longer meets the predeclared scale criteria.")
    return design


def plot_topology_panels(design):
    labels = ["Original urban (Xizhimen)", "Alternate real region", "Expanded real region - Sparse"]
    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.1))
    for ax, label in zip(axes, labels):
        row = design[design["Dataset"] == label].iloc[0]
        candidates, users, _ = load_input_from_excel(row["DataFile"])
        selected = [int(value) for value in row["SelectedSolution"].split()]
        ax.scatter(users[:, 0], users[:, 1], s=16, color="#4C78A8", alpha=0.68, label="Users", zorder=2)
        ax.scatter(candidates[:, 0], candidates[:, 1], s=38, marker="^", color="#9CA3AF", edgecolor="white", linewidth=0.35, label="Candidates", zorder=3)
        ax.scatter(candidates[selected, 0], candidates[selected, 1], s=80, marker="*", color="#C1121F", edgecolor="black", linewidth=0.35, label="Selected servers", zorder=4)
        ax.set_title(label.replace(" - Sparse", ""), fontsize=13, pad=7)
        ax.set_xlabel("longitude", fontsize=12)
        ax.set_ylabel("latitude", fontsize=12)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
        ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.tick_params(axis="both", labelsize=9)
        ax.grid(True, linestyle="--", linewidth=0.65, alpha=0.55, zorder=0)
        ax.set_aspect(1.0 / np.cos(np.deg2rad(np.mean(candidates[:, 1]))))
        ax.text(
            0.02,
            0.02,
            f"{row['Candidates']} candidates; {row['UserWidthKm']:.1f} x {row['UserHeightKm']:.1f} km",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox={"facecolor": "white", "edgecolor": "#D1D5DB", "alpha": 0.90, "pad": 3},
        )
    handles, legend_labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, legend_labels, loc="upper center", ncol=3, fontsize=10, frameon=True)
    fig.tight_layout(rect=(0, 0, 1, 0.90))
    for ext in ("png", "pdf"):
        path = os.path.join(OUT_PNG if ext == "png" else OUT_PDF, f"reviewer6_geography_comparison.{ext}")
        fig.savefig(path, dpi=300 if ext == "png" else None, format=ext, bbox_inches="tight")
    plt.close(fig)


def plot_traffic_panels(design):
    expanded = design[design["Dataset"].str.startswith("Expanded")].copy()
    all_points = []
    datasets = []
    for scenario, title in SCENARIOS.items():
        row = expanded[expanded["Dataset"] == f"Expanded real region - {title}"].iloc[0]
        candidates, users, _ = load_input_from_excel(row["DataFile"])
        selected = [int(value) for value in row["SelectedSolution"].split()]
        datasets.append((scenario, title, row, candidates, users, selected))
        all_points.append(np.vstack([candidates, users]))
    combined = np.vstack(all_points)
    xmin, ymin = combined.min(axis=0)
    xmax, ymax = combined.max(axis=0)
    xpad = (xmax - xmin) * 0.04
    ypad = (ymax - ymin) * 0.04

    fig, axes = plt.subplots(1, 3, figsize=(12.2, 4.0), sharex=True, sharey=True)
    for ax, (_, title, row, candidates, users, selected) in zip(axes, datasets):
        ax.scatter(users[:, 0], users[:, 1], s=17, color="#4C78A8", alpha=0.68, label="Users", zorder=2)
        ax.scatter(candidates[:, 0], candidates[:, 1], s=38, marker="^", color="#9CA3AF", edgecolor="white", linewidth=0.35, label="Candidates", zorder=3)
        ax.scatter(candidates[selected, 0], candidates[selected, 1], s=80, marker="*", color="#C1121F", edgecolor="black", linewidth=0.35, label="Selected servers", zorder=4)
        ax.set_xlim(xmin - xpad, xmax + xpad)
        ax.set_ylim(ymin - ypad, ymax + ypad)
        ax.set_title(f"{title}\nDensity CV = {row['CoverageDensityCV']:.3f}", fontsize=12.5, pad=6)
        ax.set_xlabel("longitude", fontsize=12)
        ax.set_ylabel("latitude", fontsize=12)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
        ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.tick_params(axis="both", labelsize=9)
        ax.grid(True, linestyle="--", linewidth=0.65, alpha=0.55, zorder=0)
        ax.set_aspect(1.0 / np.cos(np.deg2rad(np.mean(candidates[:, 1]))))
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, fontsize=10, frameon=True)
    fig.tight_layout(rect=(0, 0, 1, 0.88))
    for ext in ("png", "pdf"):
        path = os.path.join(OUT_PNG if ext == "png" else OUT_PDF, f"reviewer6_heterogeneous_traffic.{ext}")
        fig.savefig(path, dpi=300 if ext == "png" else None, format=ext, bbox_inches="tight")
    plt.close(fig)


def plot_result_summary(stage1, aggregate):
    fig, axes = plt.subplots(2, 2, figsize=(10.8, 7.4))
    scenario_labels = list(SCENARIOS.values())
    stage_values = []
    for scenario in SCENARIOS:
        row = stage1[stage1["Config"].str.contains(f"_{scenario}_")].iloc[0]
        stage_values.append(float(row["CLSAdvantagePct"]))
    stage_bars = axes[0, 0].bar(np.arange(3), stage_values, color=["#4C78A8", "#59A14F", "#F28E2B"], edgecolor="black", linewidth=0.45, zorder=3)
    axes[0, 0].bar_label(stage_bars, fmt="%.1f%%", padding=3, fontsize=9)
    axes[0, 0].set_xticks(np.arange(3), scenario_labels)
    axes[0, 0].set_ylabel("CLS improvement (%)", fontsize=12)
    axes[0, 0].set_title("Stage I", fontsize=13)

    for ax, metric, ylabel in zip(
        axes.flat[1:],
        ("HV", "IGD", "BestQ"),
        ("HV (higher is better)", "IGD (lower is better)", "Best Q (lower is better)"),
    ):
        x = np.arange(3)
        width = 0.19
        for index, method in enumerate(METHODS):
            values = []
            errors = []
            for scenario in SCENARIOS:
                row = aggregate[(aggregate["Scenario"] == scenario) & (aggregate["Method"] == method)].iloc[0]
                values.append(row[f"{metric}Mean"])
                errors.append(row[f"{metric}Std"])
            offset = (index - 1.5) * width
            ax.bar(x + offset, values, width=width, yerr=errors, capsize=2, color=METHOD_COLORS[method], edgecolor="black", linewidth=0.4, label=method, zorder=3)
        ax.set_xticks(x, scenario_labels)
        ax.set_ylabel(ylabel, fontsize=11)
        ax.set_title(f"Stage II: {metric}", fontsize=13)
    for ax in axes.flat:
        ax.tick_params(axis="both", labelsize=10)
        ax.grid(True, axis="y", linestyle="--", linewidth=0.65, alpha=0.60, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    handles, labels = axes[0, 1].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=4, fontsize=10, frameon=True)
    fig.tight_layout(rect=(0, 0, 1, 0.94))
    for ext in ("png", "pdf"):
        path = os.path.join(OUT_PNG if ext == "png" else OUT_PDF, f"reviewer6_large_region_results.{ext}")
        fig.savefig(path, dpi=300 if ext == "png" else None, format=ext, bbox_inches="tight")
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Summarize Reviewer 2 Comment 6 generalization evidence.")
    parser.parse_args()
    ensure_dirs()
    wide_detail = parse_wide_logs()
    wide_aggregate = aggregate_metrics(wide_detail)
    psp_gaps = psp_gap_summary(wide_detail)
    main_detail = load_main_metrics()
    main_aggregate = aggregate_metrics(main_detail)
    design = build_design_table()
    stage1 = pd.read_csv(WIDE_STAGE1_CSV)
    stage1.insert(
        1,
        "Scenario",
        [
            next(title for key, title in SCENARIOS.items() if f"_{key}_" in config)
            for config in stage1["Config"]
        ],
    )

    outputs = {
        "reviewer6_generalization_design.csv": design,
        "reviewer6_large_region_stage1.csv": stage1,
        "reviewer6_large_region_stage2_detail.csv": wide_detail,
        "reviewer6_large_region_stage2_aggregate.csv": wide_aggregate,
        "reviewer6_large_region_psp_gaps.csv": psp_gaps,
        "reviewer6_main_candidate_stage2_detail.csv": main_detail,
        "reviewer6_main_candidate_stage2_aggregate.csv": main_aggregate,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(OUT_CSV, filename), index=False)

    plot_topology_panels(design)
    plot_traffic_panels(design)
    plot_result_summary(stage1, wide_aggregate)

    print(design[["Dataset", "Candidates", "Users", "CenterDistanceFromOriginalKm", "UserWidthKm", "UserHeightKm", "AreaScaleVsOriginal", "CoverageDensityCV"]].to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nWide-region Stage I:")
    print(stage1[["Config", "CLSCost", "BestBaselineCost", "CLSAdvantagePct"]].to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nMain-candidate Stage II aggregate:")
    print(main_aggregate.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nWide-region Stage II aggregate:")
    print(wide_aggregate.to_string(index=False, float_format=lambda value: f"{value:.4f}"))


if __name__ == "__main__":
    main()
