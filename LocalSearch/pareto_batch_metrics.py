import argparse
import os
from collections import OrderedDict

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from pymoo.indicators.hv import HV


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

METHOD_FILES = OrderedDict(
    [
        ("NS-P", "res_random.npz"),
        ("GCP", "res_greedy_cost.npz"),
        ("GDP", "res_greedy_request.npz"),
        ("PSP", "res_hybrid-A-1.npz"),
    ]
)

METHOD_COLORS = {
    "NS-P": "#1f77b4",
    "GCP": "#2ca02c",
    "GDP": "#ff7f0e",
    "PSP": "#d62728",
}

METHOD_MARKERS = {
    "NS-P": "o",
    "GCP": "s",
    "GDP": "^",
    "PSP": "D",
}


def ensure_dirs():
    for rel in ("output/csv", "output/excel", "output/pdf", "output/png"):
        os.makedirs(os.path.join(PROJECT_ROOT, rel), exist_ok=True)


def normalize(values, lower, upper):
    denom = np.maximum(upper - lower, 1e-12)
    return (values - lower) / denom


def pareto_mask(points):
    points = np.asarray(points, dtype=float)
    mask = np.ones(points.shape[0], dtype=bool)
    for i, point in enumerate(points):
        if not mask[i]:
            continue
        dominated = np.all(points <= point, axis=1) & np.any(points < point, axis=1)
        if np.any(dominated):
            mask[i] = False
    return mask


def nondominated(points):
    points = np.asarray(points, dtype=float)
    if len(points) == 0:
        return points
    return points[pareto_mask(points)]


def igd(front, reference_front):
    if len(front) == 0 or len(reference_front) == 0:
        return np.nan
    distances = []
    for ref in reference_front:
        distances.append(np.min(np.linalg.norm(front - ref, axis=1)))
    return float(np.mean(distances))


def spacing(front):
    if len(front) < 2:
        return 0.0
    nearest = []
    for i, point in enumerate(front):
        others = np.delete(front, i, axis=0)
        nearest.append(np.min(np.linalg.norm(others - point, axis=1)))
    nearest = np.asarray(nearest, dtype=float)
    return float(np.sqrt(np.mean((nearest - np.mean(nearest)) ** 2)))


def load_npz_group(config_name):
    npz_dir = os.path.join(PROJECT_ROOT, "output", "npz")
    files = OrderedDict()
    for method, filename in METHOD_FILES.items():
        stem, ext = os.path.splitext(filename)
        candidates = [os.path.join(npz_dir, f"{stem}_{config_name}{ext}")]
        if config_name == "10_130":
            candidates.append(os.path.join(npz_dir, filename))
        for path in candidates:
            if os.path.exists(path):
                files[method] = path
                break

    data = OrderedDict()
    for method, path in files.items():
        arr = np.load(path)
        if "F" not in arr:
            continue
        F = np.asarray(arr["F"], dtype=float)
        if F.ndim == 1:
            F = F.reshape(1, -1)
        if F.shape[1] != 2:
            raise ValueError(f"{path} must contain a two-column F array.")
        data[method] = F

    if not data:
        raise FileNotFoundError(f"No usable npz result files found in {npz_dir}.")
    return data


def calculate_metrics(data, alpha=0.5, ref_point=(1.1, 1.1)):
    all_raw = np.vstack(list(data.values()))
    lower = np.min(all_raw, axis=0)
    upper = np.max(all_raw, axis=0)

    norm_data = OrderedDict()
    fronts = OrderedDict()
    for method, F in data.items():
        F_norm = normalize(F, lower, upper)
        norm_data[method] = F_norm
        fronts[method] = nondominated(F_norm)

    reference_front = nondominated(np.vstack(list(fronts.values())))
    hv_indicator = HV(ref_point=np.asarray(ref_point, dtype=float))

    rows = []
    beta = 1.0 - alpha
    for method, F_norm in norm_data.items():
        front = fronts[method]
        weighted = alpha * F_norm[:, 0] + beta * F_norm[:, 1]
        front_weighted = alpha * front[:, 0] + beta * front[:, 1] if len(front) else np.array([np.nan])
        rows.append(
            {
                "Config": "",
                "Method": method,
                "HV": float(hv_indicator.do(front)) if len(front) else np.nan,
                "IGD": igd(front, reference_front),
                "Spacing": spacing(front),
                "BestQ": float(np.min(weighted)),
                "BestFrontQ": float(np.min(front_weighted)),
                "ParetoCount": int(len(front)),
                "SolutionCount": int(len(F_norm)),
                "BestCostNorm": float(np.min(F_norm[:, 0])),
                "BestDelayNorm": float(np.min(F_norm[:, 1])),
            }
        )

    metrics = pd.DataFrame(rows)
    return metrics, norm_data, fronts, reference_front, lower, upper


def save_metrics(config_name, metrics):
    metrics = metrics.copy()
    metrics["Config"] = config_name

    csv_path = os.path.join(PROJECT_ROOT, "output", "csv", f"pareto_metrics_{config_name}.csv")
    xlsx_path = os.path.join(PROJECT_ROOT, "output", "excel", f"pareto_metrics_{config_name}.xlsx")
    metrics.to_csv(csv_path, index=False)
    metrics.to_excel(xlsx_path, index=False)
    return csv_path, xlsx_path


def plot_pareto_front(config_name, norm_data, fronts):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False

    fig, ax = plt.subplots(figsize=(7, 5.5))
    for method, F in norm_data.items():
        ax.scatter(
            F[:, 0],
            F[:, 1],
            label=method,
            color=METHOD_COLORS.get(method, "#333333"),
            marker=METHOD_MARKERS.get(method, "o"),
            s=76,
            alpha=0.82,
            edgecolors="white",
            linewidths=0.35,
            zorder=3,
        )

    ax.set_xlabel("cost", fontsize=24, fontname="Arial")
    ax.set_ylabel("delay", fontsize=24, fontname="Arial")
    ax.tick_params(axis="both", labelsize=23)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.75, alpha=0.75, zorder=0)
    legend_fontsize = 17 if len(norm_data) >= 5 else 19
    ax.legend(fontsize=legend_fontsize, frameon=True, edgecolor="lightgray", framealpha=1)
    ax.set_xlim(-0.04, 1.04)
    ax.set_ylim(-0.04, 1.04)
    fig.tight_layout()

    out_path = os.path.join(PROJECT_ROOT, "output", "pdf", f"pareto_front_{config_name}.pdf")
    png_path = os.path.join(PROJECT_ROOT, "output", "png", f"pareto_front_{config_name}.png")
    fig.savefig(out_path, format="pdf", bbox_inches="tight")
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def plot_metric_bars(config_name, metrics):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False

    metric_names = ["HV", "IGD", "BestQ"]
    ylabels = ["HV", "IGD", "Best Q"]
    methods = metrics["Method"].tolist()
    colors = [METHOD_COLORS.get(method, "#333333") for method in methods]

    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.6))
    for ax, metric, ylabel in zip(axes.ravel(), metric_names, ylabels):
        values = metrics[metric].to_numpy(dtype=float)
        ax.bar(np.arange(len(methods)), values, color=colors, edgecolor="black", linewidth=0.45, width=0.58, zorder=3)
        ax.set_xticks(np.arange(len(methods)))
        ax.set_xticklabels(methods, fontsize=13)
        ax.set_ylabel(ylabel, fontsize=15, fontname="Arial")
        ax.tick_params(axis="y", labelsize=13)
        ax.grid(True, axis="y", linestyle="--", linewidth=0.75, alpha=0.72, zorder=0)
        for spine in ("top", "right"):
            ax.spines[spine].set_visible(False)

    fig.tight_layout()
    out_path = os.path.join(PROJECT_ROOT, "output", "pdf", f"pareto_metrics_{config_name}.pdf")
    png_path = os.path.join(PROJECT_ROOT, "output", "png", f"pareto_metrics_{config_name}.png")
    fig.savefig(out_path, format="pdf", bbox_inches="tight")
    fig.savefig(png_path, format="png", dpi=300, bbox_inches="tight")
    plt.close(fig)
    return out_path


def run(config_name="10_130", alpha=0.5):
    ensure_dirs()
    data = load_npz_group(config_name=config_name)
    metrics, norm_data, fronts, reference_front, lower, upper = calculate_metrics(data, alpha=alpha)
    csv_path, xlsx_path = save_metrics(config_name, metrics)
    front_path = plot_pareto_front(config_name, norm_data, fronts)
    metrics_path = plot_metric_bars(config_name, metrics)

    print("Config:", config_name)
    print("Normalization lower:", lower)
    print("Normalization upper:", upper)
    print(metrics.to_string(index=False, float_format=lambda x: f"{x:.4f}"))
    print("Saved:", csv_path)
    print("Saved:", xlsx_path)
    print("Saved:", front_path)
    print("Saved:", metrics_path)
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Calculate Pareto quality metrics for saved service deployment results.")
    parser.add_argument("--config", default="10_130", help="Configuration name used in output file names.")
    parser.add_argument("--alpha", type=float, default=0.5, help="Weight for normalized cost in BestQ.")
    args = parser.parse_args()
    run(config_name=args.config, alpha=args.alpha)


if __name__ == "__main__":
    main()
