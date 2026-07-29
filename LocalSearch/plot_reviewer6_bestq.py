import argparse
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INPUT = os.path.join(
    PROJECT_ROOT,
    "output",
    "csv",
    "reviewer6_main_candidate_bestq_aggregate.csv",
)
DEFAULT_STEM = "reviewer6_generalization_bestq"
METHODS = ["NS-P", "PSP", "GCP", "GDP", "DQN"]
STYLE = {
    "NS-P": {"facecolor": "white", "edgecolor": "#1683D8", "hatch": "."},
    "PSP": {"facecolor": "white", "edgecolor": "#FF1F1F", "hatch": "++"},
    "GCP": {"facecolor": "white", "edgecolor": "#21B95B", "hatch": "//"},
    "GDP": {"facecolor": "white", "edgecolor": "#C99500", "hatch": "..."},
    "DQN": {"facecolor": "#9467BD", "edgecolor": "#7E57A6", "hatch": None},
}


def plot_bestq(input_path, output_stem):
    frame = pd.read_csv(input_path).set_index("Method").loc[METHODS]
    means = frame["BestQMean"].to_numpy(dtype=float)
    errors = frame["BestQStd"].to_numpy(dtype=float)
    positions = np.arange(len(METHODS))

    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["hatch.linewidth"] = 1.0
    fig, ax = plt.subplots(figsize=(7.0, 4.3))

    for index, method in enumerate(METHODS):
        style = STYLE[method]
        ax.bar(
            positions[index],
            means[index],
            width=0.58,
            facecolor=style["facecolor"],
            edgecolor=style["edgecolor"],
            linewidth=1.25,
            hatch=style["hatch"],
            zorder=3,
        )
    ax.errorbar(
        positions,
        means,
        yerr=errors,
        fmt="none",
        ecolor="#4B5563",
        elinewidth=1.0,
        capsize=3.0,
        capthick=1.0,
        zorder=4,
    )

    for position, mean, error in zip(positions, means, errors):
        ax.text(
            position,
            mean + error + 0.012,
            f"{mean:.3f}",
            ha="center",
            va="bottom",
            fontsize=10,
            color="#222222",
        )

    ax.set_xticks(positions)
    ax.set_xticklabels(METHODS, fontsize=13)
    ax.set_ylabel("Q (normalized)", fontsize=15)
    ax.tick_params(axis="y", labelsize=12)
    ax.set_ylim(0.20, 0.70)
    ax.set_yticks(np.arange(0.20, 0.71, 0.10))
    ax.grid(True, axis="y", linestyle="--", linewidth=0.75, color="#B7B7B7", alpha=0.72, zorder=0)
    for spine in ax.spines.values():
        spine.set_color("#4A4A4A")
        spine.set_linewidth(0.8)

    fig.tight_layout(pad=0.8)
    png_path = os.path.join(PROJECT_ROOT, "output", "png", f"{output_stem}.png")
    pdf_path = os.path.join(PROJECT_ROOT, "output", "pdf", f"{output_stem}.pdf")
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render the Reviewer-6 Best-Q comparison in the paper's bar-chart style."
    )
    parser.add_argument("--input", default=DEFAULT_INPUT)
    parser.add_argument("--output-stem", default=DEFAULT_STEM)
    return parser.parse_args()


def main():
    args = parse_args()
    png_path, pdf_path = plot_bestq(os.path.abspath(args.input), args.output_stem)
    print(f"Saved: {png_path}")
    print(f"Saved: {pdf_path}")


if __name__ == "__main__":
    main()
