import argparse
import contextlib
import os
import shutil
import sys

import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from LocalSearch.batch_service_experiments import run_nsga_methods
from LocalSearch.experiment_utils import build_stage_context
from LocalSearch.pareto_batch_metrics import run as run_pareto_metrics
from LocalSearch.real_region_generalization import rank_stage2


OUT_CSV_DIR = os.path.join(PROJECT_ROOT, "output", "csv")
OUT_XLSX_DIR = os.path.join(PROJECT_ROOT, "output", "excel")
OUT_LOG_DIR = os.path.join(PROJECT_ROOT, "output", "logs")
OUT_NPZ_SEED_DIR = os.path.join(PROJECT_ROOT, "output", "npz", "seed_checks")


def ensure_dirs():
    for path in (OUT_CSV_DIR, OUT_XLSX_DIR, OUT_LOG_DIR, OUT_NPZ_SEED_DIR):
        os.makedirs(path, exist_ok=True)


def archive_npz_results(paths, seed):
    archived = []
    for path in paths:
        stem, ext = os.path.splitext(os.path.basename(path))
        target = os.path.join(OUT_NPZ_SEED_DIR, f"{stem}_seed{seed}{ext}")
        shutil.copy2(path, target)
        archived.append(target)
    return archived


def load_screen(path):
    if not os.path.isabs(path):
        path = os.path.join(PROJECT_ROOT, path)
    frame = pd.read_csv(path)
    required = {"Config", "DataFile", "TargetServers", "SigmaMin", "N2Adjust", "Users"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Stage-I screen file is missing required columns: {sorted(missing)}")
    return frame


def select_rows(frame, args):
    if args.configs:
        selected = frame[frame["Config"].isin(args.configs)].copy()
        missing = [name for name in args.configs if name not in set(selected["Config"])]
        if missing:
            raise ValueError(f"Configs not found in screen file: {missing}")
        return selected
    metric = "CLSAdvantagePct" if "CLSAdvantagePct" in frame.columns else "CLSCost"
    ascending = metric == "CLSCost"
    return frame.sort_values(metric, ascending=ascending).head(args.top).copy()


def run(args):
    ensure_dirs()
    screen = load_screen(args.screen_csv)
    selected = select_rows(screen, args)
    rows = []
    metric_rows = []
    for _, row in selected.iterrows():
        config_name = row["Config"]
        print(f"[stage2] {config_name}", flush=True)
        config = {
            "data_file": row["DataFile"],
            "target_servers": int(row["TargetServers"]),
            "sigma_min": int(row["SigmaMin"]),
            "n2_adjust": int(row["N2Adjust"]),
            "series": "real_region",
            "users": int(row["Users"]),
        }
        context = build_stage_context(config)
        log_path = os.path.join(OUT_LOG_DIR, f"{config_name}_{args.output_prefix}.log")
        with open(log_path, "w", encoding="utf-8") as log:
            with contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
                result_paths = run_nsga_methods(
                    config_name=config_name,
                    context=context,
                    pop_size=args.pop_size,
                    n_gen=args.n_gen,
                    seed=args.seed,
                    visualize_hybrid_process=False,
                )
                if args.archive_npz:
                    for path in archive_npz_results(result_paths, args.seed):
                        print("Archived:", path)
                metrics = run_pareto_metrics(config_name=config_name, alpha=args.metric_alpha)
        metrics = metrics.copy()
        metrics.insert(0, "Seed", int(args.seed))
        metrics.insert(0, "ConfigName", config_name)
        metric_rows.append(metrics)
        ranking = rank_stage2(metrics)
        ranking["Config"] = config_name
        if "CLSCost" in row:
            ranking["CLSCost"] = float(row["CLSCost"])
        if "CLSAdvantagePct" in row:
            ranking["CLSAdvantagePct"] = float(row["CLSAdvantagePct"])
        rows.append(ranking)

    result = pd.DataFrame(rows)
    leading = ["Config", "CLSCost", "CLSAdvantagePct"]
    ordered_cols = [col for col in leading if col in result.columns] + [
        col for col in result.columns if col not in leading
    ]
    result = result[ordered_cols]
    csv_path = os.path.join(OUT_CSV_DIR, f"{args.output_prefix}.csv")
    xlsx_path = os.path.join(OUT_XLSX_DIR, f"{args.output_prefix}.xlsx")
    result.to_csv(csv_path, index=False)
    result.to_excel(xlsx_path, index=False)
    metric_detail = pd.concat(metric_rows, ignore_index=True)
    metric_csv_path = os.path.join(OUT_CSV_DIR, f"{args.output_prefix}_metrics.csv")
    metric_xlsx_path = os.path.join(OUT_XLSX_DIR, f"{args.output_prefix}_metrics.xlsx")
    metric_detail.to_csv(metric_csv_path, index=False)
    metric_detail.to_excel(metric_xlsx_path, index=False)
    print("Saved:", csv_path)
    print("Saved:", xlsx_path)
    print("Saved:", metric_csv_path)
    print("Saved:", metric_xlsx_path)
    print(result.to_string(index=False, float_format=lambda value: f"{value:.4f}"))


def main():
    parser = argparse.ArgumentParser(description="Run Stage-II verification from a real-region Stage-I screen file.")
    parser.add_argument("--screen-csv", default=os.path.join("output", "csv", "real_region_stage1_screen.csv"))
    parser.add_argument("--configs", nargs="+", default=None)
    parser.add_argument("--top", type=int, default=6)
    parser.add_argument("--pop-size", type=int, default=50)
    parser.add_argument("--n-gen", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--metric-alpha", type=float, default=0.5)
    parser.add_argument("--output-prefix", default="real_region_stage2_from_screen")
    parser.add_argument("--archive-npz", action="store_true")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
