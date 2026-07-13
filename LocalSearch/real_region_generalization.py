import argparse
import io
import math
import os
import random
import sys
import zipfile
from collections import OrderedDict

import numpy as np
import pandas as pd

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter, MaxNLocator


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

from LocalSearch.batch_service_experiments import run_nsga_methods
from LocalSearch.cls_initialization_sensitivity import (
    coverage_cost_from_matrix,
    initial_solution,
    pairwise_candidate_distances,
    pairwise_user_candidate_distances,
)
from LocalSearch.experiment_utils import (
    build_stage_context,
    compute_density_for_stations,
    coverage_compute_cost,
    coverage_local_search,
    haversine_distance,
    load_input_from_excel,
)
from LocalSearch.pareto_batch_metrics import run as run_pareto_metrics
from LocalSearch.station_selection_strategies import (
    density_based_selection,
    distance_sum_selection,
    greedy_k_selection,
    random_selection,
)


DATA_DIR = os.path.join(PROJECT_ROOT, "data", "real_region")
RAW_DIR = os.path.join(PROJECT_ROOT, "data", "raw_station_pool")
OUT_CSV_DIR = os.path.join(PROJECT_ROOT, "output", "csv")
OUT_XLSX_DIR = os.path.join(PROJECT_ROOT, "output", "excel")
OUT_PNG_DIR = os.path.join(PROJECT_ROOT, "output", "png")
OUT_PDF_DIR = os.path.join(PROJECT_ROOT, "output", "pdf")

BASE_CONFIG = {
    "data_file": "data/input_data_10_130_8_new.xlsx",
    "target_servers": 10,
    "sigma_min": 16,
    "n2_adjust": -1,
    "users": 130,
}
READ_PASSWORD = ""

LON_NAMES = [
    "lng",
    "lon",
    "longitude",
    "x",
    "经度",
    "东经",
    "bd09_lng",
    "gcj02_lng",
    "wgs84_lng",
    "wgs84_lon",
]
LAT_NAMES = [
    "lat",
    "latitude",
    "y",
    "纬度",
    "北纬",
    "bd09_lat",
    "gcj02_lat",
    "wgs84_lat",
]


def ensure_dirs():
    for path in (DATA_DIR, RAW_DIR, OUT_CSV_DIR, OUT_XLSX_DIR, OUT_PNG_DIR, OUT_PDF_DIR):
        os.makedirs(path, exist_ok=True)


def label_suffix(label):
    if not label:
        return ""
    clean = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in str(label).strip())
    return f"_{clean}" if clean else ""


def label_prefix(label):
    suffix = label_suffix(label)
    return f"{suffix[1:]}_" if suffix else ""


def norm_name(name):
    return str(name).strip().lower().replace(" ", "").replace("_", "")


def candidate_data_files(path):
    if os.path.isfile(path):
        return [path]
    files = []
    for root, _, names in os.walk(path):
        for name in names:
            if os.path.splitext(name)[1].lower() in {".xlsx", ".xls", ".csv", ".txt"}:
                files.append(os.path.join(root, name))
    return sorted(files)


def extract_zip(zip_path, password):
    target = os.path.join(RAW_DIR, os.path.splitext(os.path.basename(zip_path))[0])
    os.makedirs(target, exist_ok=True)
    with zipfile.ZipFile(zip_path) as archive:
        pwd = password.encode("utf-8") if password else None
        archive.extractall(target, pwd=pwd)
    return target


def read_table(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in {".xlsx", ".xls"}:
        try:
            return pd.read_excel(path)
        except Exception as original_exc:
            try:
                import msoffcrypto

                with open(path, "rb") as source:
                    office = msoffcrypto.OfficeFile(source)
                    if not office.is_encrypted():
                        raise original_exc
                    decrypted = io.BytesIO()
                    office.load_key(password=READ_PASSWORD)
                    office.decrypt(decrypted)
                    decrypted.seek(0)
                    return pd.read_excel(decrypted)
            except Exception:
                raise original_exc
    for encoding in ("utf-8-sig", "gbk", "utf-8"):
        try:
            return pd.read_csv(path, encoding=encoding)
        except Exception:
            continue
    return pd.read_csv(path)


def find_coordinate_columns(frame):
    normalized = {norm_name(col): col for col in frame.columns}
    lon_col = None
    lat_col = None
    for name in LON_NAMES:
        key = norm_name(name)
        if key in normalized:
            lon_col = normalized[key]
            break
    for name in LAT_NAMES:
        key = norm_name(name)
        if key in normalized:
            lat_col = normalized[key]
            break
    if lon_col is not None and lat_col is not None:
        return lon_col, lat_col

    numeric_cols = []
    for col in frame.columns:
        values = pd.to_numeric(frame[col], errors="coerce")
        valid = values.dropna()
        if len(valid) >= max(10, len(frame) * 0.2):
            numeric_cols.append((col, valid))

    lon_candidates = []
    lat_candidates = []
    for col, values in numeric_cols:
        lon_share = ((values >= 70) & (values <= 140)).mean()
        lat_share = ((values >= 15) & (values <= 55)).mean()
        if lon_share > 0.8:
            lon_candidates.append(col)
        if lat_share > 0.8:
            lat_candidates.append(col)

    for lon in lon_candidates:
        for lat in lat_candidates:
            if lon != lat:
                return lon, lat
    raise ValueError("Could not detect longitude/latitude columns.")


def load_station_pool(source, password=""):
    global READ_PASSWORD
    READ_PASSWORD = password
    if source is None:
        return load_existing_candidate_pool()
    source = os.path.abspath(source)
    ext = os.path.splitext(source)[1].lower()
    if ext == ".zip":
        source = extract_zip(source, password=password)
    elif ext in {".rar", ".7z"}:
        raise ValueError("RAR/7z station pools need to be extracted first, or install a 7z command-line tool.")

    frames = []
    errors = []
    for path in candidate_data_files(source):
        try:
            frame = read_table(path)
            lon_col, lat_col = find_coordinate_columns(frame)
            coords = pd.DataFrame(
                {
                    "lng": pd.to_numeric(frame[lon_col], errors="coerce"),
                    "lat": pd.to_numeric(frame[lat_col], errors="coerce"),
                    "SourceFile": os.path.relpath(path, PROJECT_ROOT) if path.startswith(PROJECT_ROOT) else path,
                }
            )
            frames.append(coords)
        except Exception as exc:
            errors.append((path, str(exc)))
    if not frames:
        detail = "\n".join(f"{path}: {err}" for path, err in errors[:8])
        raise ValueError(f"No readable station coordinate table found.\n{detail}")

    pool = pd.concat(frames, ignore_index=True)
    pool = pool.dropna(subset=["lng", "lat"])
    pool = pool[(pool["lng"].between(115.0, 118.0)) & (pool["lat"].between(39.0, 41.5))]
    pool = pool.drop_duplicates(subset=["lng", "lat"]).reset_index(drop=True)
    if len(pool) < 50:
        raise ValueError(f"Only {len(pool)} Beijing-area station coordinates were found; too few for region search.")
    return pool


def load_existing_candidate_pool():
    rows = []
    data_dir = os.path.join(PROJECT_ROOT, "data")
    for name in os.listdir(data_dir):
        if not name.startswith("input_data_") or not name.endswith(".xlsx"):
            continue
        path = os.path.join(data_dir, name)
        try:
            candidates, _, _ = load_input_from_excel(path)
        except Exception:
            continue
        for lon, lat in candidates:
            rows.append({"lng": float(lon), "lat": float(lat), "SourceFile": os.path.join("data", name)})
    pool = pd.DataFrame(rows).drop_duplicates(subset=["lng", "lat"]).reset_index(drop=True)
    if len(pool) < 20:
        raise ValueError("Existing input_data files do not provide enough unique candidate stations.")
    return pool


def pairwise_station_distances_km(points):
    n = len(points)
    distances = np.zeros((n, n), dtype=float)
    for i in range(n):
        for j in range(i + 1, n):
            d = haversine_distance(points[i, 0], points[i, 1], points[j, 0], points[j, 1])
            distances[i, j] = d
            distances[j, i] = d
    return distances


def km_extent(points):
    lon_min, lat_min = np.min(points, axis=0)
    lon_max, lat_max = np.max(points, axis=0)
    width = haversine_distance(lon_min, lat_min, lon_max, lat_min)
    height = haversine_distance(lon_min, lat_min, lon_min, lat_max)
    return width, height


def nearest_neighbor_mean(points):
    if len(points) < 2:
        return 0.0
    distances = pairwise_station_distances_km(points)
    distances[distances == 0] = np.nan
    return float(np.nanmean(np.nanmin(distances, axis=1)))


def pick_region_candidates(pool, candidate_count, max_regions, min_radius_km, min_center_distance_km):
    points = pool[["lng", "lat"]].to_numpy(dtype=float)
    station_distances = pairwise_station_distances_km(points)
    centers = []
    for center_idx in range(len(points)):
        order = np.argsort(station_distances[center_idx])
        selected = order[:candidate_count]
        radius = float(station_distances[center_idx, selected[-1]])
        if radius < min_radius_km:
            continue
        width, height = km_extent(points[selected])
        nn_mean = nearest_neighbor_mean(points[selected])
        density = candidate_count / max(math.pi * radius * radius, 1e-12)
        centers.append(
            {
                "CenterIndex": int(center_idx),
                "CenterLng": float(points[center_idx, 0]),
                "CenterLat": float(points[center_idx, 1]),
                "SelectedIndices": selected.tolist(),
                "StationRadiusKm": radius,
                "StationWidthKm": width,
                "StationHeightKm": height,
                "StationNNMeanKm": nn_mean,
                "StationDensityPerKm2": density,
            }
        )

    centers.sort(key=lambda row: (-row["StationRadiusKm"], -row["StationNNMeanKm"]))
    chosen = []
    for row in centers:
        far_enough = True
        for prev in chosen:
            d = haversine_distance(row["CenterLng"], row["CenterLat"], prev["CenterLng"], prev["CenterLat"])
            if d < min_center_distance_km:
                far_enough = False
                break
        if far_enough:
            chosen.append(row)
        if len(chosen) >= max_regions:
            break
    return chosen


def km_offsets_to_lonlat(anchor, dx_km, dy_km):
    lon, lat = anchor
    lat_offset = dy_km / 111.0
    lon_offset = dx_km / max(111.0 * math.cos(math.radians(lat)), 1e-6)
    return lon + lon_offset, lat + lat_offset


def generate_users(candidates, n_users, rng, mode):
    lon_min, lat_min = np.min(candidates, axis=0)
    lon_max, lat_max = np.max(candidates, axis=0)
    width_km, height_km = km_extent(candidates)
    expand_lon = (max(width_km, 1.0) * 0.12) / max(111.0 * math.cos(math.radians(np.mean(candidates[:, 1]))), 1e-6)
    expand_lat = (max(height_km, 1.0) * 0.12) / 111.0

    if mode == "sparse":
        anchor_share = 0.55
        spread_km = 1.20
        uniform_expand = 1.0
    elif mode == "skewed":
        anchor_share = 0.88
        spread_km = 0.45
        uniform_expand = 0.90
    elif mode == "clustered":
        anchor_share = 0.82
        spread_km = 0.55
        uniform_expand = 0.45
    else:
        anchor_share = 0.65
        spread_km = 0.85
        uniform_expand = 0.70

    anchor_count = int(n_users * anchor_share)
    uniform_count = n_users - anchor_count
    users = []

    anchor_indices = rng.integers(0, len(candidates), size=anchor_count)
    for idx in anchor_indices:
        angle = rng.uniform(0, 2 * math.pi)
        radius = abs(rng.normal(0.0, spread_km))
        dx = radius * math.cos(angle)
        dy = radius * math.sin(angle)
        users.append(km_offsets_to_lonlat(candidates[idx], dx, dy))

    low = np.array([lon_min - expand_lon * uniform_expand, lat_min - expand_lat * uniform_expand])
    high = np.array([lon_max + expand_lon * uniform_expand, lat_max + expand_lat * uniform_expand])
    uniform_users = rng.uniform(low=low, high=high, size=(uniform_count, 2))
    users.extend(map(tuple, uniform_users))
    return np.asarray(users, dtype=float)


def sample_services(base_services, n_users, rng, mode):
    num_services = int(np.max(base_services) + 1)
    counts = np.bincount(base_services.astype(int), minlength=num_services).astype(float)
    prob = counts / max(counts.sum(), 1.0)
    if mode == "clustered":
        hot = int(np.argmax(prob))
        prob = prob * 0.70
        prob[hot] += 0.20
        prob[(hot + 1) % num_services] += 0.10
        prob = prob / prob.sum()
    elif mode == "skewed":
        hot = int(np.argmax(prob))
        second = int(np.argsort(prob)[-2]) if num_services > 1 else hot
        prob = prob * 0.55
        prob[hot] += 0.30
        prob[second] += 0.15
        prob = prob / prob.sum()
    elif mode == "sparse":
        prob = prob * 0.85 + 0.15 / num_services
        prob = prob / prob.sum()
    return rng.choice(np.arange(num_services), size=n_users, p=prob).astype(int)


def choose_density_parameters(candidate_positions, user_positions, target_servers, coverage_radius):
    _, densities, _ = compute_density_for_stations(
        candidate_positions,
        user_positions,
        coverage_radius=coverage_radius,
        sigma_min=1,
    )
    max_density = max(max(densities), 1)
    choices = []
    for sigma in range(1, int(max_density) + 1):
        active = sum(1 for value in densities if value >= sigma)
        choices.append((abs(active - target_servers), abs((target_servers - active)), sigma, active))
    _, _, sigma_min, n2_raw = min(choices)
    return int(sigma_min), int(target_servers - n2_raw), densities


def write_dataset(config_name, candidates, users, services):
    rel_path = os.path.join("data", "real_region", f"input_data_{config_name}_8.xlsx")
    full_path = os.path.join(PROJECT_ROOT, rel_path)
    with pd.ExcelWriter(full_path) as writer:
        pd.DataFrame(candidates, columns=["lng", "lat"]).to_excel(writer, sheet_name="candidates", index=False)
        pd.DataFrame(users, columns=["lng", "lat"]).to_excel(writer, sheet_name="users", index=False)
        pd.DataFrame({"svc_type": services.astype(int)}).to_excel(writer, sheet_name="services", index=False)
    return rel_path


def evaluate_stage1(config_name, config, seed, coverage_radius, max_iter, random_trials):
    random.seed(seed)
    np.random.seed(seed)
    candidates, users, _ = load_input_from_excel(config["data_file"])
    context = build_stage_context(config, seed=seed, coverage_radius=coverage_radius, max_iter=max_iter, verbose=False)
    k = context["k"]

    baseline_rows = []
    random_costs = []
    for trial in range(random_trials):
        random.seed(seed + trial)
        solution = random_selection(candidates, users, k)
        cost = coverage_compute_cost(solution, users, candidates, coverage_radius)
        random_costs.append(cost)
    baseline_rows.append(("RandomMean", float(np.mean(random_costs))))
    baseline_rows.append(("RandomBest", float(np.min(random_costs))))

    for label, func in [
        ("Density", lambda: density_based_selection(candidates, users, k, coverage_radius)),
        ("DistSum", lambda: distance_sum_selection(candidates, users, k)),
        ("Greedy", lambda: greedy_k_selection(users, candidates, k)),
    ]:
        solution = func()
        baseline_rows.append((label, coverage_compute_cost(solution, users, candidates, coverage_radius)))

    baseline_costs = dict(baseline_rows)
    best_baseline = min(baseline_costs.values())
    cls_cost = float(context["best_cost"])
    cls_advantage = 100.0 * (best_baseline - cls_cost) / max(best_baseline, 1e-12)

    user_candidate_distances = pairwise_user_candidate_distances(users, candidates)
    candidate_distances = pairwise_candidate_distances(candidates)
    rng = random.Random(seed)
    init = initial_solution("density_diverse", k, rng, user_candidate_distances, candidate_distances, coverage_radius)
    diverse_init_cost = coverage_cost_from_matrix(init, user_candidate_distances, coverage_radius)

    return {
        "Config": config_name,
        "DataFile": config["data_file"],
        "Users": len(users),
        "Candidates": len(candidates),
        "TargetServers": config["target_servers"],
        "ResolvedK": k,
        "SigmaMin": config["sigma_min"],
        "N2Adjust": config["n2_adjust"],
        "N2Raw": context["n2_raw"],
        "CLSCost": cls_cost,
        "RandomMeanCost": baseline_costs["RandomMean"],
        "RandomBestCost": baseline_costs["RandomBest"],
        "DensityCost": baseline_costs["Density"],
        "DistSumCost": baseline_costs["DistSum"],
        "GreedyCost": baseline_costs["Greedy"],
        "DiverseInitCost": diverse_init_cost,
        "BestBaselineCost": best_baseline,
        "CLSAdvantagePct": cls_advantage,
        "SelectedSolution": " ".join(map(str, sorted(context["best_solution"]))),
    }, context


def service_entropy(services):
    counts = np.bincount(services.astype(int))
    prob = counts[counts > 0] / counts.sum()
    return float(-np.sum(prob * np.log(prob)))


def describe_dataset(config_name, scenario, center_row, candidates, users, services, densities, stage1_row):
    all_points = np.vstack([candidates, users])
    width, height = km_extent(all_points)
    density_arr = np.asarray(densities, dtype=float)
    return {
        "Config": config_name,
        "Scenario": scenario,
        "CenterLng": center_row["CenterLng"],
        "CenterLat": center_row["CenterLat"],
        "StationRadiusKm": center_row["StationRadiusKm"],
        "StationWidthKm": center_row["StationWidthKm"],
        "StationHeightKm": center_row["StationHeightKm"],
        "StationNNMeanKm": center_row["StationNNMeanKm"],
        "StationDensityPerKm2": center_row["StationDensityPerKm2"],
        "BBoxWidthKm": width,
        "BBoxHeightKm": height,
        "UserNNMeanKm": nearest_neighbor_mean(users),
        "StationCoverageDensityMean": float(np.mean(density_arr)),
        "StationCoverageDensityCV": float(np.std(density_arr) / np.mean(density_arr)) if np.mean(density_arr) else 0.0,
        "ServiceEntropy": service_entropy(services),
        "CLSCost": stage1_row["CLSCost"],
        "CLSAdvantagePct": stage1_row["CLSAdvantagePct"],
    }


def plot_topology(config_name, scenario, candidates, users, selected_indices=None):
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(6.8, 5.2))
    ax.scatter(users[:, 0], users[:, 1], s=22, color="#4C78A8", alpha=0.70, label="Users", zorder=2)
    ax.scatter(candidates[:, 0], candidates[:, 1], s=54, marker="^", color="#9CA3AF", edgecolor="white", linewidth=0.4, label="Candidates", zorder=3)
    if selected_indices:
        selected = candidates[list(selected_indices)]
        ax.scatter(selected[:, 0], selected[:, 1], s=104, marker="*", color="#C1121F", edgecolor="black", linewidth=0.4, label="Selected servers", zorder=4)
    ax.set_xlabel("longitude", fontsize=16)
    ax.set_ylabel("latitude", fontsize=16)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=6))
    ax.xaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    ax.yaxis.set_major_formatter(FormatStrFormatter("%.3f"))
    ax.tick_params(axis="both", labelsize=12)
    ax.grid(True, linestyle="--", linewidth=0.7, alpha=0.55, zorder=0)
    ax.legend(fontsize=11, frameon=True, edgecolor="lightgray")
    ax.set_title(scenario, fontsize=14, pad=8)
    fig.tight_layout()
    png_path = os.path.join(OUT_PNG_DIR, f"real_region_topology_{config_name}.png")
    pdf_path = os.path.join(OUT_PDF_DIR, f"real_region_topology_{config_name}.pdf")
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def rank_stage2(metrics):
    row = metrics.set_index("Method")
    if "PSP" not in row.index:
        return {"PSPStage2Score": 0, "PSPBestHV": False, "PSPBestIGD": False, "PSPBestQ": False}
    hv_best = row.loc["PSP", "HV"] >= row["HV"].max() - 1e-12
    igd_best = row.loc["PSP", "IGD"] <= row["IGD"].min() + 1e-12
    bestq_best = row.loc["PSP", "BestQ"] <= row["BestQ"].min() + 1e-12
    return {
        "PSPStage2Score": int(hv_best) + int(igd_best) + int(bestq_best),
        "PSPBestHV": bool(hv_best),
        "PSPBestIGD": bool(igd_best),
        "PSPBestQ": bool(bestq_best),
        "PSPHV": float(row.loc["PSP", "HV"]),
        "PSPIGD": float(row.loc["PSP", "IGD"]),
        "PSPBestQValue": float(row.loc["PSP", "BestQ"]),
    }


def plot_stage1_screen(stage1_df, run_label=None):
    top = stage1_df.sort_values("CLSAdvantagePct", ascending=False).head(12)
    labels = top["Config"].tolist()
    values = top["CLSAdvantagePct"].to_numpy(dtype=float)
    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(8.2, 3.8))
    ax.bar(np.arange(len(labels)), values, color="#C1121F", edgecolor="black", linewidth=0.45, zorder=3)
    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=25, ha="right", fontsize=9)
    ax.set_ylabel("CLS advantage over best baseline (%)", fontsize=11)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.7, alpha=0.65, zorder=0)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    fig.tight_layout()
    suffix = label_suffix(run_label)
    png_path = os.path.join(OUT_PNG_DIR, f"real_region_stage1_screen_top{suffix}.png")
    pdf_path = os.path.join(OUT_PDF_DIR, f"real_region_stage1_screen_top{suffix}.pdf")
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path


def run_search(args):
    ensure_dirs()
    pool = load_station_pool(args.station_pool, password=args.password)
    suffix = label_suffix(args.run_label)
    pool_csv = os.path.join(OUT_CSV_DIR, f"real_region_station_pool_loaded{suffix}.csv")
    pool.to_csv(pool_csv, index=False)

    _, _, base_services = load_input_from_excel(BASE_CONFIG["data_file"])
    regions = pick_region_candidates(
        pool,
        candidate_count=args.candidate_count,
        max_regions=args.max_regions,
        min_radius_km=args.min_station_radius,
        min_center_distance_km=args.min_center_distance,
    )
    if not regions:
        raise ValueError("No region candidates met the radius and spacing filters.")

    stage1_rows = []
    dataset_rows = []
    config_contexts = {}
    config_defs = {}
    rng_master = np.random.default_rng(args.seed)

    for region_rank, region in enumerate(regions):
        candidates = pool.iloc[region["SelectedIndices"]][["lng", "lat"]].to_numpy(dtype=float)
        for mode in args.user_modes:
            for repeat in range(args.repeats):
                mode_offsets = {"sparse": 1, "mixed": 2, "clustered": 3, "skewed": 4}
                seed = int(args.seed + region_rank * 1000 + repeat * 17 + mode_offsets[mode])
                rng = np.random.default_rng(seed)
                users = generate_users(candidates, args.users, rng, mode=mode)
                services = sample_services(base_services, args.users, rng, mode=mode)
                sigma_min, n2_adjust, densities = choose_density_parameters(
                    candidates,
                    users,
                    target_servers=args.target_servers,
                    coverage_radius=args.coverage_radius,
                )
                config_name = (
                    f"real_{label_prefix(args.run_label)}{mode}_r{region_rank:02d}_c{args.candidate_count}"
                    f"_u{args.users}_k{args.target_servers}_s{repeat}"
                )
                rel_path = write_dataset(config_name, candidates, users, services)
                config = {
                    "data_file": rel_path,
                    "target_servers": args.target_servers,
                    "sigma_min": sigma_min,
                    "n2_adjust": n2_adjust,
                    "series": "real_region",
                    "users": args.users,
                }
                try:
                    stage1_row, context = evaluate_stage1(
                        config_name,
                        config,
                        seed=seed,
                        coverage_radius=args.coverage_radius,
                        max_iter=args.stage1_iter,
                        random_trials=args.random_trials,
                    )
                except Exception as exc:
                    print(f"[skip] {config_name}: {exc}")
                    continue
                stage1_rows.append(stage1_row)
                dataset_rows.append(describe_dataset(config_name, mode, region, candidates, users, services, densities, stage1_row))
                config_contexts[config_name] = context
                config_defs[config_name] = config
                selected = [int(value) for value in stage1_row["SelectedSolution"].split()]
                plot_topology(config_name, mode, candidates, users, selected_indices=selected)

    stage1_df = pd.DataFrame(stage1_rows)
    dataset_df = pd.DataFrame(dataset_rows)
    if stage1_df.empty:
        raise ValueError("No valid generated datasets were produced.")

    stage1_csv = os.path.join(OUT_CSV_DIR, f"real_region_stage1_screen{suffix}.csv")
    dataset_csv = os.path.join(OUT_CSV_DIR, f"real_region_dataset_summary{suffix}.csv")
    stage1_xlsx = os.path.join(OUT_XLSX_DIR, f"real_region_stage1_screen{suffix}.xlsx")
    dataset_xlsx = os.path.join(OUT_XLSX_DIR, f"real_region_dataset_summary{suffix}.xlsx")
    stage1_df.to_csv(stage1_csv, index=False)
    dataset_df.to_csv(dataset_csv, index=False)
    stage1_df.to_excel(stage1_xlsx, index=False)
    dataset_df.to_excel(dataset_xlsx, index=False)
    plot_stage1_screen(stage1_df, run_label=args.run_label)

    metric_rows = []
    if not args.skip_stage2:
        selected_configs = stage1_df.sort_values("CLSAdvantagePct", ascending=False)["Config"].head(args.stage2_top).tolist()
        for config_name in selected_configs:
            print(f"\n=== Stage II for {config_name} ===")
            context = config_contexts[config_name]
            run_nsga_methods(
                config_name=config_name,
                context=context,
                pop_size=args.pop_size,
                n_gen=args.n_gen,
                seed=args.seed,
                visualize_hybrid_process=False,
            )
            metrics = run_pareto_metrics(config_name=config_name, alpha=args.metric_alpha)
            ranking = rank_stage2(metrics)
            ranking["Config"] = config_name
            metric_rows.append(ranking)

    if metric_rows:
        metric_df = pd.DataFrame(metric_rows)
        combined = stage1_df.merge(metric_df, on="Config", how="left")
        metric_csv = os.path.join(OUT_CSV_DIR, f"real_region_stage2_screen{suffix}.csv")
        metric_xlsx = os.path.join(OUT_XLSX_DIR, f"real_region_stage2_screen{suffix}.xlsx")
        combined.to_csv(metric_csv, index=False)
        combined.to_excel(metric_xlsx, index=False)
        print("Saved:", metric_csv)
        print("Saved:", metric_xlsx)

    print("Saved:", pool_csv)
    print("Saved:", stage1_csv)
    print("Saved:", dataset_csv)
    print("Saved:", stage1_xlsx)
    print("Saved:", dataset_xlsx)
    print("\n=== Top Stage-I candidates ===")
    cols = ["Config", "Users", "Candidates", "ResolvedK", "CLSCost", "BestBaselineCost", "CLSAdvantagePct"]
    print(stage1_df.sort_values("CLSAdvantagePct", ascending=False)[cols].head(10).to_string(index=False, float_format=lambda value: f"{value:.4f}"))


def main():
    parser = argparse.ArgumentParser(description="Search real-station geographic regions for generalization experiments.")
    parser.add_argument("--station-pool", default=None, help="Station pool file, directory, or zip. If omitted, uses existing input_data candidates as a dry run.")
    parser.add_argument("--password", default=os.environ.get("MEC_STATION_POOL_PASSWORD", ""))
    parser.add_argument("--candidate-count", type=int, default=20)
    parser.add_argument("--target-servers", type=int, default=10)
    parser.add_argument("--users", type=int, default=130)
    parser.add_argument("--user-modes", nargs="+", default=["sparse", "mixed", "clustered"], choices=["sparse", "mixed", "clustered", "skewed"])
    parser.add_argument("--repeats", type=int, default=2)
    parser.add_argument("--max-regions", type=int, default=8)
    parser.add_argument("--min-station-radius", type=float, default=3.0)
    parser.add_argument("--min-center-distance", type=float, default=5.0)
    parser.add_argument("--coverage-radius", type=float, default=1.5)
    parser.add_argument("--stage1-iter", type=int, default=250)
    parser.add_argument("--random-trials", type=int, default=30)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-stage2", action="store_true")
    parser.add_argument("--stage2-top", type=int, default=4)
    parser.add_argument("--pop-size", type=int, default=40)
    parser.add_argument("--n-gen", type=int, default=100)
    parser.add_argument("--metric-alpha", type=float, default=0.5)
    parser.add_argument("--run-label", default=None, help="Optional suffix for summary CSV/XLSX/figure outputs.")
    args = parser.parse_args()
    run_search(args)


if __name__ == "__main__":
    main()
