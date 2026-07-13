import argparse
import os
import sys
from collections import OrderedDict

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from LocalSearch.pareto_batch_metrics import METHOD_COLORS, calculate_metrics, load_npz_group


FIXED_SERVERS = OrderedDict(
    [("10_100", "100"), ("10_130", "130"), ("10_150", "150"), ("10_180", "180")]
)
FIXED_USERS = OrderedDict(
    [("5_130", "5"), ("10_130", "10"), ("15_130", "15"), ("20_130", "20")]
)
METHODS = ["NS-P", "PSP", "GCP", "GDP", "DQN"]


def compute_tables(alpha=0.5):
    paper_rows = []
    rerun_rows = []
    for config_name in OrderedDict.fromkeys([*FIXED_SERVERS, *FIXED_USERS]):
        data = load_npz_group(config_name)
        if "DQN" not in data:
            raise FileNotFoundError(f"DQN result is missing for {config_name}.")

        original = OrderedDict((name, values) for name, values in data.items() if name != "DQN")
        original_metrics, _, _, _, lower, upper = calculate_metrics(original, alpha=alpha)
        for row in original_metrics.to_dict("records"):
            paper_rows.append(
                {
                    "Config": config_name,
                    "Method": row["Method"],
                    "BestQ": row["BestQ"],
                    "Source": "original-four-method normalization",
                }
            )

        dqn_norm = (data["DQN"] - lower) / np.maximum(upper - lower, 1e-12)
        dqn_q = alpha * dqn_norm[:, 0] + (1.0 - alpha) * dqn_norm[:, 1]
        paper_rows.append(
            {
                "Config": config_name,
                "Method": "DQN",
                "BestQ": float(np.min(dqn_q)),
                "Source": "DQN evaluated with original-four-method bounds",
            }
        )

        full_metrics, _, _, _, _, _ = calculate_metrics(data, alpha=alpha)
        for row in full_metrics.to_dict("records"):
            rerun_rows.append(
                {
                    "Config": config_name,
                    "Method": row["Method"],
                    "BestQ": row["BestQ"],
                    "Source": "five-method joint normalization",
                }
            )
    return pd.DataFrame(paper_rows), pd.DataFrame(rerun_rows)


def plot_grouped(table, configs, xlabel, stem):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(8.2, 5.4))
    x = np.arange(len(configs))
    width = 0.15
    offsets = (np.arange(len(METHODS)) - (len(METHODS) - 1) / 2) * width
    for offset, method in zip(offsets, METHODS):
        values = []
        for config_name in configs:
            row = table[(table["Config"] == config_name) & (table["Method"] == method)]
            if len(row) != 1:
                raise ValueError(f"Expected one {method} value for {config_name}, found {len(row)}.")
            values.append(float(row.iloc[0]["BestQ"]))
        ax.bar(
            x + offset,
            values,
            width=width,
            color=METHOD_COLORS[method],
            edgecolor="black",
            linewidth=0.45,
            label=method,
            zorder=3,
        )

    ax.set_xticks(x)
    ax.set_xticklabels(list(configs.values()), fontsize=17)
    ax.set_xlabel(xlabel, fontsize=20)
    ax.set_ylabel("Best Q", fontsize=20)
    ax.tick_params(axis="y", labelsize=17)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.75, alpha=0.72, zorder=0)
    ax.legend(ncol=5, fontsize=13, loc="upper center", bbox_to_anchor=(0.5, 1.14), frameon=True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    png = os.path.join(PROJECT_ROOT, "output", "png", f"{stem}.png")
    pdf = os.path.join(PROJECT_ROOT, "output", "pdf", f"{stem}.pdf")
    fig.savefig(png, dpi=300, bbox_inches="tight")
    fig.savefig(pdf, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return png, pdf


def main():
    parser = argparse.ArgumentParser(description="Plot controlled-variable BestQ comparisons with DQN.")
    parser.add_argument("--alpha", type=float, default=0.5)
    args = parser.parse_args()
    for rel in ("output/csv", "output/png", "output/pdf"):
        os.makedirs(os.path.join(PROJECT_ROOT, rel), exist_ok=True)

    paper, rerun = compute_tables(alpha=args.alpha)
    paper_path = os.path.join(PROJECT_ROOT, "output", "csv", "dqn_control_bestq_paper_aligned.csv")
    rerun_path = os.path.join(PROJECT_ROOT, "output", "csv", "dqn_control_bestq_full_rerun.csv")
    paper.to_csv(paper_path, index=False)
    rerun.to_csv(rerun_path, index=False)

    for label, table in (("paper_aligned", paper), ("full_rerun", rerun)):
        plot_grouped(
            table,
            FIXED_SERVERS,
            "Number of users",
            f"dqn_fixed_servers_{label}",
        )
        plot_grouped(
            table,
            FIXED_USERS,
            "Number of servers",
            f"dqn_fixed_users_{label}",
        )
    print(f"Saved {paper_path}")
    print(f"Saved {rerun_path}")


if __name__ == "__main__":
    main()
