import argparse
import os
import random
import sys
from collections import OrderedDict

import numpy as np
import pandas as pd
from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.termination import get_termination


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from LocalSearch.experiment_configs import EXPERIMENT_CONFIGS
from LocalSearch.experiment_utils import build_stage_context
from LocalSearch.nsga_service_deploy import MyServiceDeployProblem, ServiceRepair, ServiceSampling
from LocalSearch.pareto_batch_metrics import calculate_metrics


METHODS = OrderedDict(
    [
        ("random", "NS-P"),
        ("greedy_cost", "GCP"),
        ("greedy_request", "GDP"),
        ("hybrid-A-1", "PSP"),
    ]
)

DATA_VARIANTS = {
    "10_150": [
        ("new", "data/input_data_10_150_8_new.xlsx"),
        ("legacy", "data/input_data_10_150_8.xlsx"),
    ],
    "10_180": [
        ("new", "data/input_data_10_180_8_new.xlsx"),
        ("legacy", "data/input_data_10_180_8.xlsx"),
    ],
}


def run_scenario(config_name, variant, data_file, seed, pop_size, n_gen, reset_per_method):
    config = dict(EXPERIMENT_CONFIGS[config_name])
    config["data_file"] = data_file
    context = build_stage_context(config, seed=seed, coverage_radius=1.5, max_iter=200, verbose=False)

    raw = OrderedDict()
    protocol = "reset_per_method" if reset_per_method else "submitted"
    output_dir = os.path.join(
        PROJECT_ROOT,
        "output",
        "npz",
        "paper_protocol_audit",
        f"seed{seed}",
        protocol,
    )
    os.makedirs(output_dir, exist_ok=True)

    for mode, method in METHODS.items():
        if reset_per_method:
            random.seed(seed)
            np.random.seed(seed)
        problem = MyServiceDeployProblem(
            k=context["k"],
            servers_pos=context["servers_pos"],
            user_positions=context["user_positions"],
            user_services=context["user_services"],
            assigned_server=context["assigned_server"],
        )
        # This constructor intentionally matches the submitted-paper code. The
        # current explicit SBX/PM settings belong to the later revision audit.
        algorithm = NSGA2(
            pop_size=pop_size,
            sampling=ServiceSampling(mode, visualize_hybrid_process=False),
            repair=ServiceRepair(),
            eliminate_duplicates=True,
        )
        result = minimize(
            problem,
            algorithm,
            get_termination("n_gen", n_gen),
            seed=seed,
            save_history=False,
            verbose=False,
        )
        raw[method] = np.asarray(result.F, dtype=float)
        stem = f"{config_name}_{variant}_{method.replace('-', '').lower()}"
        np.savez(
            os.path.join(output_dir, f"{stem}.npz"),
            X=result.X,
            F=result.F,
            seed=np.asarray([seed]),
        )

    metrics, _, _, _, lower, upper = calculate_metrics(raw, alpha=0.5)
    metrics["Config"] = config_name
    metrics["Variant"] = variant
    metrics["Seed"] = seed
    metrics["Protocol"] = protocol
    metrics["DataFile"] = data_file
    metrics["Stage1Solution"] = " ".join(str(value) for value in context["best_solution"])
    metrics["Stage1Cost"] = context["best_cost"]
    metrics["NormalizationLowerCost"] = lower[0]
    metrics["NormalizationLowerDelay"] = lower[1]
    metrics["NormalizationUpperCost"] = upper[0]
    metrics["NormalizationUpperDelay"] = upper[1]
    return metrics


def scenario_variants(config_name, include_data_variants):
    if include_data_variants and config_name in DATA_VARIANTS:
        return DATA_VARIANTS[config_name]
    config = EXPERIMENT_CONFIGS[config_name]
    return [("configured", config["data_file"])]


def main():
    parser = argparse.ArgumentParser(
        description="Reproduce the submitted-paper Stage-II protocol without overwriting current results."
    )
    parser.add_argument("--configs", nargs="+", default=["all"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[42])
    parser.add_argument("--pop-size", type=int, default=50)
    parser.add_argument("--n-gen", type=int, default=200)
    parser.add_argument("--include-data-variants", action="store_true")
    parser.add_argument(
        "--reset-per-method",
        action="store_true",
        help="Use the later batch-runner convention instead of the submitted-paper random-state sequence.",
    )
    args = parser.parse_args()

    config_names = list(EXPERIMENT_CONFIGS) if args.configs == ["all"] else args.configs
    unknown = [name for name in config_names if name not in EXPERIMENT_CONFIGS]
    if unknown:
        raise ValueError(f"Unknown configuration(s): {', '.join(unknown)}")

    frames = []
    for seed in args.seeds:
        for config_name in config_names:
            for variant, data_file in scenario_variants(config_name, args.include_data_variants):
                print(f"Running {config_name}/{variant}, seed={seed}")
                frames.append(
                    run_scenario(
                        config_name,
                        variant,
                        data_file,
                        seed,
                        args.pop_size,
                        args.n_gen,
                        args.reset_per_method,
                    )
                )

    results = pd.concat(frames, ignore_index=True)
    archive_path = os.path.join(
        PROJECT_ROOT, "data", "paper_archive", "stage2_bestq_original_paper.csv"
    )
    archived = pd.read_csv(archive_path)[["Config", "Method", "BestQ"]].rename(
        columns={"BestQ": "ArchivedBestQ"}
    )
    results = results.merge(archived, on=["Config", "Method"], how="left")
    results["BestQAbsError"] = (results["BestQ"] - results["ArchivedBestQ"]).abs()

    csv_dir = os.path.join(PROJECT_ROOT, "output", "csv")
    os.makedirs(csv_dir, exist_ok=True)
    protocol = "reset_per_method" if args.reset_per_method else "submitted"
    detail_path = os.path.join(csv_dir, f"original_stage2_protocol_audit_{protocol}_detail.csv")
    summary_path = os.path.join(csv_dir, f"original_stage2_protocol_audit_{protocol}_summary.csv")
    results.to_csv(detail_path, index=False)
    summary = (
        results.groupby(["Config", "Variant", "Seed", "DataFile"], as_index=False)
        .agg(
            MeanAbsoluteError=("BestQAbsError", "mean"),
            MaxAbsoluteError=("BestQAbsError", "max"),
        )
    )
    psp = results.loc[
        results["Method"] == "PSP",
        ["Config", "Variant", "Seed", "DataFile", "BestQ"],
    ].rename(columns={"BestQ": "PSPBestQ"})
    summary = summary.merge(
        psp,
        on=["Config", "Variant", "Seed", "DataFile"],
        how="left",
    ).sort_values(["Config", "MeanAbsoluteError"])
    summary.to_csv(summary_path, index=False)
    print(summary.to_string(index=False))
    print(f"Saved {detail_path}")
    print(f"Saved {summary_path}")


if __name__ == "__main__":
    main()
