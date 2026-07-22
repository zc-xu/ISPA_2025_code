import argparse
import glob
import os
import re
import sys
from collections import OrderedDict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FormatStrFormatter, MaxNLocator
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
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
MAIN_DQN_CSV = os.path.join(OUT_CSV, f"dqn_summary_{MAIN_CONFIG}.csv")

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
    "DQN": "#9467bd",
}
METHOD_MARKERS = {"NS-P": "o", "GCP": "s", "GDP": "^", "PSP": "D", "DQN": "P"}
PDF_METADATA = {
    "Creator": "MOS2 reproducible experiment pipeline",
    "CreationDate": None,
    "ModDate": None,
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


def load_dqn_bestq():
    frame = pd.read_csv(MAIN_DQN_CSV)
    required = {
        "Config",
        "Weight",
        "Seed",
        "Cost",
        "Delay",
        "EvaluationAlpha",
        "EvaluationBestQ",
    }
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(
            "DQN summary must be regenerated with fixed-alpha evaluation; "
            f"missing columns: {sorted(missing)}"
        )
    frame = frame[frame["Config"] == MAIN_CONFIG].copy()
    if set(frame["Seed"].astype(int)) != {42, 43, 44}:
        raise ValueError("DQN evidence must contain seeds 42, 43, and 44.")
    if not np.allclose(frame["EvaluationAlpha"].to_numpy(dtype=float), 0.5):
        raise ValueError("DQN cross-method evaluation must use alpha=0.5.")
    weight_counts = frame.groupby("Seed")["Weight"].nunique()
    if not (weight_counts == 5).all():
        raise ValueError("Each DQN seed must contain five preference-weight solutions.")

    best_indices = frame.groupby("Seed")["EvaluationBestQ"].idxmin()
    best = frame.loc[best_indices].sort_values("Seed").copy()
    best.insert(3, "Method", "DQN")
    best.rename(columns={"EvaluationBestQ": "BestQ"}, inplace=True)
    return frame.sort_values(["Seed", "Weight"]), best


def aggregate_bestq(main_detail, dqn_best):
    base = main_detail[["Seed", "Method", "BestQ"]].copy()
    learned = dqn_best[["Seed", "Method", "BestQ"]].copy()
    detail = pd.concat([base, learned], ignore_index=True)
    rows = []
    for method, frame in detail.groupby("Method", sort=False):
        rows.append(
            {
                "Method": method,
                "Seeds": int(frame["Seed"].nunique()),
                "BestQMean": float(frame["BestQ"].mean()),
                "BestQStd": float(frame["BestQ"].std(ddof=1)),
            }
        )
    aggregate = pd.DataFrame(rows).set_index("Method").loc[METHODS + ["DQN"]].reset_index()
    return detail, aggregate


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
    return pd.DataFrame(rows)


def user_density_surface(users, grid_size=140, bandwidth_km=0.75):
    center = np.mean(users, axis=0)
    cos_lat = np.cos(np.deg2rad(center[1]))
    x = (users[:, 0] - center[0]) * 111.0 * cos_lat
    y = (users[:, 1] - center[1]) * 111.0
    pad = 0.8
    gx = np.linspace(x.min() - pad, x.max() + pad, grid_size)
    gy = np.linspace(y.min() - pad, y.max() + pad, grid_size)
    xx, yy = np.meshgrid(gx, gy)
    distances = (xx[..., None] - x) ** 2 + (yy[..., None] - y) ** 2
    density = np.exp(-distances / (2.0 * bandwidth_km**2)).sum(axis=2)
    longitude = center[0] + xx / (111.0 * cos_lat)
    latitude = center[1] + yy / 111.0
    return longitude, latitude, density


def plot_topology_panels(design):
    labels = ["Original urban (Xizhimen)", "Alternate real region"]
    panel_titles = ["(a) Original Xizhimen region", "(b) New real-station region"]
    datasets = []
    max_density = 0.0
    for label in labels:
        row = design[design["Dataset"] == label].iloc[0]
        candidates, users, _ = load_input_from_excel(row["DataFile"])
        selected = [int(value) for value in row["SelectedSolution"].split()]
        longitude, latitude, density = user_density_surface(users)
        max_density = max(max_density, float(density.max()))
        datasets.append((row, candidates, users, selected, longitude, latitude, density))

    plt.rcParams["font.family"] = "Arial"
    fig, axes = plt.subplots(1, 2, figsize=(9.4, 4.4))
    fig.subplots_adjust(left=0.08, right=0.87, bottom=0.14, top=0.80, wspace=0.30)
    levels = np.linspace(0.0, max_density, 13)
    contour = None
    for ax, title, dataset in zip(axes, panel_titles, datasets):
        row, candidates, users, selected, longitude, latitude, density = dataset
        contour = ax.contourf(
            longitude,
            latitude,
            density,
            levels=levels,
            cmap="YlGnBu",
            alpha=0.92,
            antialiased=True,
            zorder=1,
        )
        ax.scatter(
            users[:, 0],
            users[:, 1],
            s=8,
            color="#111827",
            alpha=0.24,
            linewidth=0,
            zorder=2,
        )
        ax.scatter(
            candidates[:, 0],
            candidates[:, 1],
            s=38,
            marker="^",
            facecolor="white",
            edgecolor="#374151",
            linewidth=0.75,
            zorder=3,
        )
        ax.scatter(
            candidates[selected, 0],
            candidates[selected, 1],
            s=92,
            marker="*",
            color="#d62728",
            edgecolor="black",
            linewidth=0.45,
            zorder=4,
        )
        ax.set_title(title, fontsize=12.5, pad=7)
        ax.set_xlabel("Longitude", fontsize=11)
        ax.set_ylabel("Latitude", fontsize=11)
        ax.xaxis.set_major_locator(MaxNLocator(nbins=5))
        ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
        ax.xaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.yaxis.set_major_formatter(FormatStrFormatter("%.2f"))
        ax.tick_params(axis="both", labelsize=9)
        ax.set_aspect(1.0 / np.cos(np.deg2rad(np.mean(candidates[:, 1]))))
        ax.text(
            0.02,
            0.02,
            f"{int(row['Candidates'])} candidate stations; {int(row['Users'])} users",
            transform=ax.transAxes,
            fontsize=8.5,
            bbox={"facecolor": "white", "edgecolor": "#D1D5DB", "alpha": 0.92, "pad": 3},
            zorder=5,
        )
    legend_handles = [
        Line2D([0], [0], marker=".", color="none", markerfacecolor="#111827", markersize=7, label="Users"),
        Line2D([0], [0], marker="^", color="none", markerfacecolor="white", markeredgecolor="#374151", markersize=7, label="Candidate stations"),
        Line2D([0], [0], marker="*", color="none", markerfacecolor="#d62728", markeredgecolor="black", markersize=10, label="CLS-selected servers"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="upper center",
        bbox_to_anchor=(0.47, 0.98),
        ncol=3,
        fontsize=9.5,
        frameon=True,
    )
    colorbar_axis = fig.add_axes([0.895, 0.18, 0.018, 0.58])
    colorbar = fig.colorbar(contour, cax=colorbar_axis)
    colorbar.set_label("Estimated user density", fontsize=10)
    colorbar.ax.tick_params(labelsize=8.5)
    for ext in ("png", "pdf"):
        path = os.path.join(
            OUT_PNG if ext == "png" else OUT_PDF,
            f"reviewer6_geography_comparison.{ext}",
        )
        fig.savefig(
            path,
            dpi=300 if ext == "png" else None,
            format=ext,
            bbox_inches="tight",
            metadata=PDF_METADATA if ext == "pdf" else None,
        )
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
        fig.savefig(
            path,
            dpi=300 if ext == "png" else None,
            format=ext,
            bbox_inches="tight",
            metadata=PDF_METADATA if ext == "pdf" else None,
        )
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
        fig.savefig(
            path,
            dpi=300 if ext == "png" else None,
            format=ext,
            bbox_inches="tight",
            metadata=PDF_METADATA if ext == "pdf" else None,
        )
    plt.close(fig)


def zoom_point_range(ax, frame, metric, methods, ylabel, title):
    ordered = frame.set_index("Method").loc[methods]
    means = ordered[f"{metric}Mean"].to_numpy(dtype=float)
    errors = ordered[f"{metric}Std"].to_numpy(dtype=float)
    x = np.arange(len(methods))
    for index, method in enumerate(methods):
        ax.errorbar(
            x[index],
            means[index],
            yerr=errors[index],
            fmt=METHOD_MARKERS[method],
            markersize=8.5 if method == "PSP" else 7.5,
            color=METHOD_COLORS[method],
            markeredgecolor="black",
            markeredgewidth=0.45,
            ecolor=METHOD_COLORS[method],
            elinewidth=1.5,
            capsize=4,
            capthick=1.2,
            zorder=4,
        )
    lower = float(np.min(means - errors))
    upper = float(np.max(means + errors))
    span = max(upper - lower, 1e-4)
    ax.set_ylim(lower - 0.12 * span, upper + 0.16 * span)
    ax.set_xticks(x, methods)
    ax.set_ylabel(ylabel, fontsize=10.5)
    ax.set_title(title, fontsize=12.5, pad=7)


def plot_main_candidate_summary(stage1, aggregate, bestq_aggregate):
    selected = stage1[stage1["Config"] == MAIN_CONFIG]
    if len(selected) != 1:
        raise ValueError(f"Expected one main Stage-I row for {MAIN_CONFIG}, found {len(selected)}.")

    plt.rcParams["font.family"] = "Arial"
    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7.2), constrained_layout=True)
    row = selected.iloc[0]
    baseline = float(row["BestBaselineCost"])
    cls_cost = float(row["CLSCost"])
    improvement = float(row["CLSAdvantagePct"])
    labels = ["Best initialization", "CLS"]
    values = [baseline, cls_cost]
    colors = ["#9CA3AF", METHOD_COLORS["PSP"]]
    bars = axes[0, 0].barh(
        np.arange(2),
        values,
        height=0.52,
        color=colors,
        edgecolor="black",
        linewidth=0.45,
        zorder=3,
    )
    axes[0, 0].invert_yaxis()
    axes[0, 0].set_yticks(np.arange(2), labels)
    axes[0, 0].set_xlim(0.0, baseline * 1.20)
    axes[0, 0].set_xlabel("Coverage/access objective (lower is better)", fontsize=10.5)
    axes[0, 0].set_title("(a) Stage I deployment", fontsize=12.5, pad=7)
    for bar, value in zip(bars, values):
        axes[0, 0].text(
            value + baseline * 0.025,
            bar.get_y() + bar.get_height() / 2.0,
            f"{value:,.1f}",
            va="center",
            fontsize=9.5,
            fontweight="bold" if value == cls_cost else "normal",
        )
    axes[0, 0].text(
        0.97,
        0.92,
        f"{improvement:.1f}% lower",
        transform=axes[0, 0].transAxes,
        ha="right",
        va="top",
        color=METHOD_COLORS["PSP"],
        fontsize=10.5,
        fontweight="bold",
    )

    zoom_point_range(
        axes[0, 1],
        aggregate,
        "HV",
        METHODS,
        "HV (higher is better)",
        "(b) Stage II hypervolume",
    )
    zoom_point_range(
        axes[1, 0],
        aggregate,
        "IGD",
        METHODS,
        "IGD (lower is better)",
        "(c) Stage II convergence",
    )
    zoom_point_range(
        axes[1, 1],
        bestq_aggregate,
        "BestQ",
        METHODS + ["DQN"],
        "Best Q (lower is better)",
        "(d) Stage II balanced solution",
    )

    inset = inset_axes(axes[1, 1], width="45%", height="43%", loc="upper left", borderpad=0.9)
    zoom_point_range(inset, bestq_aggregate, "BestQ", METHODS, "", "Evolutionary methods")
    inset.set_title("Evolutionary methods", fontsize=8.5, pad=3)
    inset.tick_params(axis="both", labelsize=7)
    inset.set_xticklabels(METHODS, rotation=0, ha="center")
    inset.grid(True, axis="y", linestyle="--", linewidth=0.45, alpha=0.55, zorder=0)
    for spine in ("top", "right"):
        inset.spines[spine].set_visible(False)

    for ax in axes.flat:
        ax.tick_params(axis="both", labelsize=9.5)
        ax.grid(True, axis="y", linestyle="--", linewidth=0.65, alpha=0.60, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)
    for ext in ("png", "pdf"):
        path = os.path.join(
            OUT_PNG if ext == "png" else OUT_PDF,
            f"reviewer6_main_candidate_results.{ext}",
        )
        fig.savefig(
            path,
            dpi=300 if ext == "png" else None,
            format=ext,
            bbox_inches="tight",
            metadata=PDF_METADATA if ext == "pdf" else None,
        )
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description="Summarize the Reviewer 6 geographic generalization evidence.")
    parser.parse_args()
    ensure_dirs()
    main_detail = load_main_metrics()
    main_aggregate = aggregate_metrics(main_detail)
    main_detail_output = main_detail[
        ["Scenario", "Seed", "Config", "Method", "HV", "IGD", "BestQ"]
    ].copy()
    dqn_weighted, dqn_best = load_dqn_bestq()
    bestq_detail, bestq_aggregate = aggregate_bestq(main_detail, dqn_best)
    design = build_design_table()
    stage1 = pd.read_csv(MAIN_STAGE1_CSV)
    stage1 = stage1[stage1["Config"] == MAIN_CONFIG].copy()
    if len(stage1) != 1:
        raise ValueError(f"Expected one Stage-I record for {MAIN_CONFIG}, found {len(stage1)}.")

    outputs = {
        "reviewer6_generalization_design.csv": design,
        "reviewer6_main_candidate_stage1.csv": stage1,
        "reviewer6_main_candidate_stage2_detail.csv": main_detail_output,
        "reviewer6_main_candidate_stage2_aggregate.csv": main_aggregate,
        "reviewer6_main_candidate_dqn_weighted.csv": dqn_weighted,
        "reviewer6_main_candidate_bestq_detail.csv": bestq_detail,
        "reviewer6_main_candidate_bestq_aggregate.csv": bestq_aggregate,
    }
    for filename, frame in outputs.items():
        frame.to_csv(os.path.join(OUT_CSV, filename), index=False)

    plot_topology_panels(design)
    plot_main_candidate_summary(stage1, main_aggregate, bestq_aggregate)

    print(
        design[
            [
                "Dataset",
                "Candidates",
                "Users",
                "CenterDistanceFromOriginalKm",
                "CoverageDensityCV",
            ]
        ].to_string(index=False, float_format=lambda value: f"{value:.4f}")
    )
    print("\nMain-candidate Stage I:")
    print(stage1[["Config", "CLSCost", "BestBaselineCost", "CLSAdvantagePct"]].to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nMain-candidate Stage II aggregate:")
    print(main_aggregate.to_string(index=False, float_format=lambda value: f"{value:.4f}"))
    print("\nBestQ aggregate including DQN:")
    print(bestq_aggregate.to_string(index=False, float_format=lambda value: f"{value:.4f}"))


if __name__ == "__main__":
    main()
