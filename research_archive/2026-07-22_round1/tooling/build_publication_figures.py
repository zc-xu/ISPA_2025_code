from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[1]
PROJECT = Path(__file__).resolve().parents[3]
OUT = ROOT / "revision_package" / "figures"

METHODS_STAGE1 = ["CLS", "RD", "DBD", "DSD", "GKD"]
STAGE1_COLORS = ["#F28E5B", "#79B473", "#6FA8DC", "#F2C14E", "#A67BC5"]
STAGE1_HATCHES = ["..", "....", "////", "....", "\\\\"]
STAGE1_VALUES = {
    "10/180": [4368.5810, 18477.1883, 16525.8861, 24679.8230, 19654.1285],
    "20/180": [309.1278, 3399.2539, 9404.7827, 23456.3853, 21155.7435],
    "10/300": [19641.0931, 50883.3984, 62409.6870, 58749.2674, 58749.2674],
    "20/300": [4291.5943, 22812.0878, 24189.3530, 68837.6756, 60406.8891],
}

SERVER_COUNTS = [8, 9, 10, 11, 12, 20]
NORMALIZED_TOTAL_COST = [0.5500, 0.5202, 0.4956, 0.4980, 0.5207, 0.7773]

# Recovered from the vector path in the first-submission Fig. 4(b). The final
# point agrees with the source workbook value (4368.581) to plotting precision.
CONVERGENCE_COST = [
    13220.328,
    12759.260,
    12081.101,
    11060.709,
    8055.592,
    7855.299,
    7645.973,
    7624.180,
    7610.703,
    7516.363,
    7083.087,
    6196.750,
    5552.571,
    5491.350,
    5291.057,
    4382.210,
    4368.581,
]

PARETO_METHODS = ["NS-P", "GCP", "GDP", "PSP"]
PARETO_COLORS = {"NS-P": "#2F6FDB", "GCP": "#2B9B49", "GDP": "#F0A124", "PSP": "#E64646"}
PARETO_MARKERS = {"NS-P": "o", "GCP": "s", "GDP": "^", "PSP": "D"}


def set_style() -> None:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "axes.linewidth": 0.75,
        }
    )


def style_axis(ax: plt.Axes, tick_size: float = 7.5) -> None:
    ax.tick_params(axis="both", labelsize=tick_size, width=0.75, length=2.7)
    ax.grid(axis="y", color="#C9C9C9", linestyle="--", linewidth=0.55, alpha=0.85, zorder=0)
    for spine in ax.spines.values():
        spine.set_linewidth(0.75)


def standard_error(values: np.ndarray) -> float:
    return float(np.std(values, ddof=1) / np.sqrt(values.size))


def build_stage1_scale_figure() -> Path:
    fig, axes = plt.subplots(1, 4, figsize=(7.05, 1.92))
    panel_labels = list(STAGE1_VALUES)
    x = np.arange(len(METHODS_STAGE1))

    for panel, (ax, label) in enumerate(zip(axes, panel_labels)):
        values = np.asarray(STAGE1_VALUES[label], dtype=float) / 1000.0
        err = standard_error(values)
        for idx, value in enumerate(values):
            ax.bar(
                idx,
                value,
                width=0.64,
                facecolor="white",
                edgecolor=STAGE1_COLORS[idx],
                linewidth=1.0,
                hatch=STAGE1_HATCHES[idx],
                yerr=err,
                capsize=2.0,
                error_kw={"elinewidth": 0.65, "ecolor": "#555555", "capthick": 0.65},
                zorder=3,
            )
        style_axis(ax, 7.3)
        ax.set_xticks(x)
        ax.set_xticklabels(METHODS_STAGE1, fontsize=7.2)
        ax.set_xlabel(f"({chr(97 + panel)}) $k/|U|={label}$.", fontsize=8.2, labelpad=4.0)
        if panel == 0:
            ax.set_ylabel(r"total cost ($\times 10^3$)", fontsize=8.4)
        ax.set_ylim(bottom=0)

    fig.subplots_adjust(left=0.070, right=0.995, top=0.97, bottom=0.28, wspace=0.28)
    path = OUT / "stage1_scale_comparison_readable.pdf"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def build_stage1_cost_figure() -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(3.45, 1.72))

    ax = axes[0]
    values = np.asarray(NORMALIZED_TOTAL_COST, dtype=float)
    err = standard_error(values)
    x = np.arange(len(SERVER_COUNTS))
    ax.bar(
        x,
        values,
        width=0.58,
        color="#82BCE8",
        edgecolor="#397EAE",
        linewidth=0.75,
        yerr=err,
        capsize=1.8,
        error_kw={"elinewidth": 0.6, "ecolor": "#666666", "capthick": 0.6},
        zorder=3,
    )
    ax.plot(x, values, color="#E64B35", linewidth=0.9, linestyle=":", marker="o", markersize=2.0, zorder=4)
    style_axis(ax, 7.0)
    ax.set_xticks(x)
    ax.set_xticklabels(SERVER_COUNTS)
    ax.set_xlabel("(a) Number of edge servers.", fontsize=7.7, labelpad=3.8)
    ax.set_ylabel("total cost (normalized)", fontsize=7.6)
    ax.set_ylim(0, 1.0)

    ax = axes[1]
    iterations = np.arange(len(CONVERGENCE_COST))
    ax.plot(
        iterations,
        np.asarray(CONVERGENCE_COST) / 1000.0,
        color="#2F7EE6",
        marker="^",
        markersize=3.0,
        linewidth=1.0,
        zorder=3,
    )
    style_axis(ax, 7.0)
    ax.set_xlabel("(b) Convergence behavior.", fontsize=7.7, labelpad=3.8)
    ax.set_ylabel(r"transmission cost ($\times 10^3$)", fontsize=7.6)
    ax.set_xlim(-0.5, len(iterations) - 0.5)

    fig.subplots_adjust(left=0.13, right=0.995, top=0.96, bottom=0.29, wspace=0.38)
    path = OUT / "stage1_cost_analysis_readable.pdf"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def build_hybrid_figure() -> Path:
    labels = ["Service 0", "Service 1", "Service 6", "Service 4", "Service 2"]
    cost = np.asarray([2.0, 1.5, 0.5, 1.0, 0.0])
    request = np.asarray([1.5, 1.0, 2.0, 0.0, 0.5])
    x = np.arange(len(labels))

    fig, axes = plt.subplots(1, 2, figsize=(3.45, 1.62))
    ax = axes[0]
    ax.bar(x, cost, width=0.58, color="#B88AD4", edgecolor="#76518D", linewidth=0.6, label="Cost score")
    ax.bar(
        x,
        request,
        width=0.58,
        bottom=cost,
        color="#F2C879",
        edgecolor="#B78B3E",
        linewidth=0.6,
        label="Request score",
    )
    style_axis(ax, 6.7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=6.2)
    ax.set_ylabel("weighted score", fontsize=7.4)
    ax.legend(frameon=True, fontsize=5.7, loc="upper right", borderpad=0.25, handlelength=1.1)
    ax.set_xlabel("(a) Hybrid score breakdown.", fontsize=7.5, labelpad=3.8)

    ax = axes[1]
    totals = cost + request
    colors = ["#F17070", "#F17070", "#70A9E8", "#70A9E8", "#D9D9D9"]
    hatches = ["", "", "", "", "////"]
    for idx, value in enumerate(totals):
        ax.bar(
            idx,
            value,
            width=0.58,
            color=colors[idx],
            edgecolor="#777777",
            linewidth=0.55,
            hatch=hatches[idx],
            zorder=3,
        )
    ax.axvspan(-0.5, 1.5, color="#FDEAEA", alpha=0.65, zorder=0)
    ax.axvspan(1.5, 3.5, color="#EAF3FD", alpha=0.65, zorder=0)
    style_axis(ax, 6.7)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=6.2)
    ax.set_ylabel("total hybrid score", fontsize=7.4)
    ax.set_ylim(0, 4.0)
    ax.set_xlabel("(b) Selection logic.", fontsize=7.5, labelpad=3.8)
    legend = [
        Patch(facecolor="#F17070", edgecolor="#777777", label="Top-$N$"),
        Patch(facecolor="#70A9E8", edgecolor="#777777", label="Random"),
        Patch(facecolor="#D9D9D9", edgecolor="#777777", hatch="////", label="Discarded"),
    ]
    ax.legend(
        handles=legend,
        frameon=True,
        fontsize=5.3,
        loc="upper right",
        borderpad=0.25,
        handlelength=1.1,
    )

    fig.subplots_adjust(left=0.12, right=0.995, top=0.94, bottom=0.34, wspace=0.36)
    path = OUT / "hybrid_initialization_readable.pdf"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def pareto_files(config: str) -> dict[str, Path]:
    suffix = "" if config == "10_130" else f"_{config}"
    return {
        "NS-P": PROJECT / "output" / "npz" / f"res_random{suffix}.npz",
        "GCP": PROJECT / "output" / "npz" / f"res_greedy_cost{suffix}.npz",
        "GDP": PROJECT / "output" / "npz" / f"res_greedy_request{suffix}.npz",
        "PSP": PROJECT / "output" / "npz" / f"res_hybrid-A-1{suffix}.npz",
    }


def build_pareto_figure() -> Path:
    configs = ["5_130", "10_130", "15_130", "20_130"]
    fig, axes = plt.subplots(1, 4, figsize=(7.05, 1.88))
    for panel, (ax, config) in enumerate(zip(axes, configs)):
        raw = {method: np.load(path)["F"] for method, path in pareto_files(config).items()}
        pooled = np.vstack([raw[method] for method in PARETO_METHODS])
        low = pooled.min(axis=0)
        high = pooled.max(axis=0)
        span = np.where(high > low, high - low, 1.0)
        for method in PARETO_METHODS:
            normalized = (raw[method] - low) / span
            ax.scatter(
                normalized[:, 0],
                normalized[:, 1],
                s=8.5,
                marker=PARETO_MARKERS[method],
                facecolor=PARETO_COLORS[method],
                edgecolor="none",
                alpha=0.82,
                label=method,
                zorder=3,
            )
        style_axis(ax, 7.3)
        ax.set_xlim(-0.03, 1.05)
        ax.set_ylim(-0.03, 1.05)
        ax.set_xlabel("cost", fontsize=8.3, labelpad=1.5)
        ax.text(
            0.5,
            -0.31,
            f"({chr(97 + panel)}) # edge servers ({config.split('_')[0]}).",
            transform=ax.transAxes,
            ha="center",
            va="top",
            fontsize=8.1,
        )
        if panel == 0:
            ax.set_ylabel("delay", fontsize=8.4)
        ax.set_xticks([0.0, 0.5, 1.0])
        ax.set_yticks([0.0, 0.5, 1.0])

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(0.5, 1.03), ncol=4, frameon=False, fontsize=8.2)
    fig.subplots_adjust(left=0.070, right=0.995, top=0.83, bottom=0.31, wspace=0.28)
    path = OUT / "stage2_pareto_fronts_readable.pdf"
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    set_style()
    for path in (
        build_stage1_scale_figure(),
        build_stage1_cost_figure(),
        build_hybrid_figure(),
        build_pareto_figure(),
    ):
        print(f"Saved {path}")


if __name__ == "__main__":
    main()
