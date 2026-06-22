import argparse
import os
import random
import sys
from collections import OrderedDict

import numpy as np
import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from pymoo.algorithms.moo.nsga2 import NSGA2
from pymoo.optimize import minimize
from pymoo.termination import get_termination

from LocalSearch.experiment_configs import EXPERIMENT_CONFIGS, select_configs
from LocalSearch.experiment_utils import build_stage_context, load_input_from_excel
from LocalSearch.nsga_service_deploy import MyServiceDeployProblem, ServiceRepair, ServiceSampling
from LocalSearch.pareto_batch_metrics import run as run_pareto_metrics


METHOD_OUTPUTS = OrderedDict(
    [
        ("random", "res_random"),
        ("greedy_cost", "res_greedy_cost"),
        ("greedy_request", "res_greedy_request"),
        ("hybrid-A-1", "res_hybrid-A-1"),
    ]
)


def ensure_dirs():
    for rel in ("output/npz", "output/csv", "output/excel", "output/pdf"):
        os.makedirs(os.path.join(PROJECT_ROOT, rel), exist_ok=True)


def write_config_manifest():
    rows = []
    for name, cfg in EXPERIMENT_CONFIGS.items():
        candidate_positions, user_positions, user_services = load_input_from_excel(cfg["data_file"])
        rows.append(
            {
                "Config": name,
                "DataFile": cfg["data_file"],
                "TargetServers": cfg["target_servers"],
                "Users": len(user_positions),
                "Candidates": len(candidate_positions),
                "ServiceTypes": int(np.max(user_services) + 1),
                "SigmaMin": cfg["sigma_min"],
                "N2Adjust": cfg["n2_adjust"],
                "Series": cfg["series"],
            }
        )
    path = os.path.join(PROJECT_ROOT, "output", "csv", "experiment_config_manifest.csv")
    pd.DataFrame(rows).to_csv(path, index=False)
    return path


def run_nsga_methods(config_name, context, pop_size=50, n_gen=200, seed=42):
    result_paths = []
    for offset, (mode, output_stem) in enumerate(METHOD_OUTPUTS.items()):
        method_seed = seed
        random.seed(method_seed)
        np.random.seed(method_seed)

        print(f"[{config_name}] Running NSGA-II initialization mode: {mode}")
        algorithm = NSGA2(
            pop_size=pop_size,
            sampling=ServiceSampling(mode),
            repair=ServiceRepair(),
            eliminate_duplicates=True,
        )
        problem = MyServiceDeployProblem(
            k=context["k"],
            servers_pos=context["servers_pos"],
            user_positions=context["user_positions"],
            user_services=context["user_services"],
            assigned_server=context["assigned_server"],
        )
        res = minimize(
            problem,
            algorithm,
            get_termination("n_gen", n_gen),
            seed=method_seed,
            save_history=True,
            verbose=False,
        )

        path = os.path.join(PROJECT_ROOT, "output", "npz", f"{output_stem}_{config_name}.npz")
        np.savez(path, X=res.X, F=res.F)
        print(f"[{config_name}] Saved {path}")
        result_paths.append(path)
    return result_paths


def run_config(config_name, config, args):
    print(f"\n=== Config {config_name} ===")
    context = build_stage_context(
        config,
        seed=args.seed,
        coverage_radius=args.coverage_radius,
        max_iter=args.stage1_iter,
        verbose=args.verbose_stage1,
    )
    print(
        f"[{config_name}] data={config['data_file']}, K={context['k']}, "
        f"N2_raw={context['n2_raw']}, selected={context['best_solution']}, "
        f"stage1_cost={context['best_cost']:.4f}"
    )

    if not args.skip_nsga:
        run_nsga_methods(
            config_name,
            context,
            pop_size=args.pop_size,
            n_gen=args.n_gen,
            seed=args.seed,
        )

    if not args.skip_metrics:
        run_pareto_metrics(config_name=config_name, alpha=args.metric_alpha)


def main():
    parser = argparse.ArgumentParser(description="Run reproducible batch experiments for MOS2 service deployment.")
    parser.add_argument(
        "--configs",
        nargs="+",
        default=["10_130"],
        help="Config names to run, or all. Known: " + ", ".join(EXPERIMENT_CONFIGS.keys()),
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--coverage-radius", type=float, default=1.5)
    parser.add_argument("--stage1-iter", type=int, default=200)
    parser.add_argument("--pop-size", type=int, default=50)
    parser.add_argument("--n-gen", type=int, default=200)
    parser.add_argument("--metric-alpha", type=float, default=0.5)
    parser.add_argument("--skip-nsga", action="store_true")
    parser.add_argument("--skip-metrics", action="store_true")
    parser.add_argument("--verbose-stage1", action="store_true")
    args = parser.parse_args()

    ensure_dirs()
    manifest_path = write_config_manifest()
    print(f"Saved manifest: {manifest_path}")

    for config_name, config in select_configs(args.configs).items():
        run_config(config_name, config, args)


if __name__ == "__main__":
    main()
