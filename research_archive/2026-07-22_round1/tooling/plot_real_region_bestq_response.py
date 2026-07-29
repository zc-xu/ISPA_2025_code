from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "revision_package" / "response_evidence"
INPUT = EVIDENCE / "real_region_bestq_aggregate.csv"
OUTPUT_PNG = EVIDENCE / "real_region_bestq.png"
OUTPUT_PDF = EVIDENCE / "real_region_bestq.pdf"

METHODS = ["NS-P", "PSP", "GCP", "GDP", "DQN"]
COLORS = {
    "NS-P": "#56A9E8",
    "PSP": "#FF5A5F",
    "GCP": "#33B864",
    "GDP": "#E5A92B",
    "DQN": "#8A6CC2",
}
HATCHES = {
    "NS-P": "..",
    "PSP": "xx",
    "GCP": "///",
    "GDP": "...",
    "DQN": "\\\\",
}


def load_rows() -> dict[str, tuple[float, float]]:
    with INPUT.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    values = {
        row["Method"]: (float(row["BestQMean"]), float(row["BestQStd"]))
        for row in rows
    }
    missing = [method for method in METHODS if method not in values]
    if missing:
        raise ValueError(f"Missing methods in {INPUT}: {missing}")
    return values


def main() -> None:
    values = load_rows()
    means = np.array([values[method][0] for method in METHODS])
    stds = np.array([values[method][1] for method in METHODS])
    x = np.arange(len(METHODS))

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "Times", "DejaVu Serif"],
            "font.size": 11,
            "axes.labelsize": 12,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "hatch.linewidth": 1.0,
        }
    )

    fig, ax = plt.subplots(figsize=(6.0, 3.9), constrained_layout=True)
    bars = []
    for idx, method in enumerate(METHODS):
        bar = ax.bar(
            x[idx],
            means[idx],
            width=0.56,
            facecolor="white",
            edgecolor=COLORS[method],
            linewidth=1.25,
            hatch=HATCHES[method],
            zorder=3,
        )
        bars.append(bar[0])

    ax.errorbar(
        x,
        means,
        yerr=stds,
        fmt="none",
        ecolor="#4B5563",
        elinewidth=1.0,
        capsize=3,
        capthick=1.0,
        zorder=4,
    )
    for idx, value in enumerate(means):
        ax.text(
            x[idx],
            value + stds[idx] + 0.012,
            f"{value:.3f}",
            ha="center",
            va="bottom",
            fontsize=9.5,
            color="#30343B",
        )

    ax.set_xticks(x, METHODS)
    ax.set_ylabel(r"$Q$ (normalized)")
    ax.set_ylim(0.20, 0.70)
    ax.grid(axis="y", linestyle="--", linewidth=0.6, color="#C8CCD2", alpha=0.85, zorder=0)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#5B6168")
    ax.spines["bottom"].set_color("#5B6168")
    ax.tick_params(direction="out", length=3.5, width=0.8)

    metadata = {"Creator": "MOS2 reproducible response-figure pipeline"}
    fig.savefig(OUTPUT_PNG, dpi=300, facecolor="white", bbox_inches="tight", metadata=metadata)
    fig.savefig(OUTPUT_PDF, facecolor="white", bbox_inches="tight", metadata=metadata)
    plt.close(fig)
    print(OUTPUT_PNG)
    print(OUTPUT_PDF)


if __name__ == "__main__":
    main()
