from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "output" / "csv" / "stage2_bestq_original_with_dqn.csv"
PNG_DIR = ROOT / "output" / "png"
PDF_DIR = ROOT / "output" / "pdf"

METHODS = ["NS-P", "PSP", "GCP", "GDP", "DQN"]
COLORS = {
    "NS-P": "#70B7E6",
    "PSP": "#F05A5A",
    "GCP": "#42B96B",
    "GDP": "#E6B94D",
    "DQN": "#8A6CC2",
}
HATCHES = {"NS-P": "..", "PSP": "xx", "GCP": "///", "GDP": "...", "DQN": "\\\\"}

FIXED_SERVERS = OrderedDict(
    [("10_100", "100"), ("10_130", "130"), ("10_150", "150"), ("10_180", "180")]
)
FIXED_USERS = OrderedDict(
    [("5_130", "5"), ("10_130", "10"), ("15_130", "15"), ("20_130", "20")]
)


def load_values() -> dict[str, dict[str, float]]:
    table = pd.read_csv(CSV_PATH)
    values: dict[str, dict[str, float]] = {}
    for config, group in table.groupby("Config"):
        values[config] = {row.Method: float(row.BestQ) for row in group.itertuples()}
    missing = [
        f"{config}/{method}"
        for config in [*FIXED_SERVERS, *FIXED_USERS]
        for method in METHODS
        if config not in values or method not in values[config]
    ]
    if missing:
        raise ValueError(f"Missing values: {', '.join(missing)}")
    return values


def add_break_marks(ax_top, ax_bottom) -> None:
    size = 0.014
    kwargs_top = dict(transform=ax_top.transAxes, color="#333333", clip_on=False, linewidth=0.9)
    kwargs_bottom = dict(transform=ax_bottom.transAxes, color="#333333", clip_on=False, linewidth=0.9)
    ax_top.plot((-size, +size), (-size, +size), **kwargs_top)
    ax_top.plot((1 - size, 1 + size), (-size, +size), **kwargs_top)
    ax_bottom.plot((-size, +size), (1 - size, 1 + size), **kwargs_bottom)
    ax_bottom.plot((1 - size, 1 + size), (1 - size, 1 + size), **kwargs_bottom)


def draw_panel(ax_top, ax_bottom, config: str, values: dict[str, dict[str, float]]) -> None:
    y = np.array([values[config][method] for method in METHODS])
    x = np.arange(len(METHODS))
    original = y[:4]
    standard_error = float(np.std(y, ddof=1) / np.sqrt(len(y)))
    bottom_low = max(0.0, float(original.min()) - standard_error - 0.012)
    bottom_high = float(original.max()) + standard_error + 0.012
    top_low = float(y[4]) - standard_error - 0.018
    top_high = float(y[4]) + standard_error + 0.018

    for axis in (ax_top, ax_bottom):
        for idx, method in enumerate(METHODS):
            axis.bar(
                x[idx],
                y[idx],
                width=0.62,
                facecolor="white",
                edgecolor=COLORS[method],
                linewidth=1.2,
                hatch=HATCHES[method],
                yerr=standard_error,
                capsize=2.4,
                error_kw={"elinewidth": 0.85, "ecolor": "#444444", "capthick": 0.85},
                zorder=3,
            )
        axis.set_xlim(-0.65, len(METHODS) - 0.35)
        axis.grid(axis="y", color="#C8C8C8", linestyle="--", linewidth=0.65, alpha=0.8, zorder=0)
        axis.tick_params(axis="both", labelsize=8, width=0.8, length=3)
        for spine in axis.spines.values():
            spine.set_linewidth(0.8)

    ax_bottom.set_ylim(bottom_low, bottom_high)
    ax_top.set_ylim(top_low, top_high)
    ax_top.spines["bottom"].set_visible(False)
    ax_bottom.spines["top"].set_visible(False)
    ax_top.tick_params(axis="x", bottom=False, labelbottom=False)
    ax_bottom.set_xticks(x)
    ax_bottom.set_xticklabels(METHODS, fontsize=8)
    add_break_marks(ax_top, ax_bottom)

    for idx in range(4):
        ax_bottom.text(
            x[idx],
            y[idx] + standard_error + 0.0025,
            f"{y[idx]:.3f}",
            ha="center",
            va="bottom",
            fontsize=6.7,
            color="#222222",
        )
    ax_top.text(
        x[4],
        y[4] + standard_error + 0.0035,
        f"{y[4]:.3f}",
        ha="center",
        va="bottom",
        fontsize=6.7,
        color="#222222",
    )


def plot_sweep(configs: OrderedDict[str, str], stem: str, descriptor: str, values) -> tuple[Path, Path]:
    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "axes.unicode_minus": False,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
    fig = plt.figure(figsize=(12.2, 3.25))
    outer = fig.add_gridspec(1, 4, wspace=0.27)
    for panel_index, (config, label) in enumerate(configs.items()):
        inner = outer[panel_index].subgridspec(2, 1, height_ratios=[1.0, 2.45], hspace=0.05)
        ax_top = fig.add_subplot(inner[0])
        ax_bottom = fig.add_subplot(inner[1], sharex=ax_top)
        draw_panel(ax_top, ax_bottom, config, values)
        panel_letter = chr(ord("a") + panel_index)
        ax_bottom.text(
            0.5,
            -0.30,
            f"({panel_letter}) # {descriptor} ({label}).",
            transform=ax_bottom.transAxes,
            ha="center",
            va="top",
            fontsize=10.5,
        )
        if panel_index == 0:
            ax_bottom.set_ylabel("Q (normalized)", fontsize=10.5)
            ax_top.set_ylabel("", fontsize=10.5)

    legend = [
        Patch(facecolor="white", edgecolor=COLORS[m], hatch=HATCHES[m], linewidth=1.1, label=m)
        for m in METHODS
    ]
    fig.legend(
        handles=legend,
        loc="upper center",
        bbox_to_anchor=(0.5, 1.01),
        ncol=5,
        frameon=False,
        fontsize=9.5,
        handlelength=1.8,
    )
    fig.subplots_adjust(left=0.070, right=0.995, top=0.82, bottom=0.25)
    png_path = PNG_DIR / f"{stem}.png"
    pdf_path = PDF_DIR / f"{stem}.pdf"
    fig.savefig(png_path, dpi=400, bbox_inches="tight", facecolor="white")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return png_path, pdf_path


def main() -> None:
    PNG_DIR.mkdir(parents=True, exist_ok=True)
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    values = load_values()
    generated = [
        plot_sweep(
            FIXED_SERVERS,
            "stage2_fixed_servers_with_dqn_errorbars",
            "users",
            values,
        ),
        plot_sweep(
            FIXED_USERS,
            "stage2_fixed_users_with_dqn_errorbars",
            "edge servers",
            values,
        ),
    ]
    for paths in generated:
        for path in paths:
            print(f"Saved {path}")


if __name__ == "__main__":
    main()
