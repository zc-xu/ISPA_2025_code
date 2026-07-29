import math
import os
import random

import numpy as np
import pandas as pd


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COST_PER_KM = 20
PENALTY_FACTOR = 10


def load_input_from_excel(path):
    full_path = path if os.path.isabs(path) else os.path.join(PROJECT_ROOT, path)
    candidate_positions = pd.read_excel(full_path, sheet_name="candidates").to_numpy()
    user_positions = pd.read_excel(full_path, sheet_name="users").to_numpy()
    user_services = pd.read_excel(full_path, sheet_name="services").to_numpy().flatten().astype(int)
    return candidate_positions, user_positions, user_services


def haversine_distance(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return 6371.0 * c


def compute_density_for_stations(candidate_positions, user_positions, coverage_radius=1.5, sigma_min=5):
    active_indices = []
    densities = []
    for idx, station in enumerate(candidate_positions):
        count = 0
        for user in user_positions:
            d = haversine_distance(station[0], station[1], user[0], user[1])
            if d <= coverage_radius:
                count += 1
        densities.append(count)
        if count >= sigma_min:
            active_indices.append(idx)
    return active_indices, densities, len(active_indices)


def resolve_k(candidate_positions, user_positions, sigma_min, n2_adjust=0, coverage_radius=1.5, target_servers=None):
    active_indices, densities, n2_raw = compute_density_for_stations(
        candidate_positions,
        user_positions,
        coverage_radius=coverage_radius,
        sigma_min=sigma_min,
    )
    k = n2_raw + n2_adjust
    if target_servers is not None and k != target_servers:
        raise ValueError(
            f"Resolved K={k}, but target_servers={target_servers}. "
            f"Check sigma_min={sigma_min} and n2_adjust={n2_adjust}."
        )
    return k, n2_raw, active_indices, densities


def coverage_compute_cost(solution, user_positions, candidate_positions, coverage_radius=1.5):
    selected_positions = candidate_positions[solution]
    total_cost = 0.0
    for user_lon, user_lat in user_positions:
        distances = [
            haversine_distance(user_lon, user_lat, lon, lat)
            for lon, lat in selected_positions
        ]
        min_distance = np.min(distances)
        if min_distance <= coverage_radius:
            cost_for_user = 0.0
        else:
            cost_for_user = min_distance * PENALTY_FACTOR
        total_cost += cost_for_user
    return total_cost * COST_PER_KM


def coverage_local_search(candidate_positions, user_positions, k, coverage_radius=1.5, max_iter=200, verbose=False):
    num_candidates = candidate_positions.shape[0]
    current_solution = random.sample(range(num_candidates), k)
    current_cost = coverage_compute_cost(current_solution, user_positions, candidate_positions, coverage_radius)

    iter_count = 0
    iteration_log = []
    while iter_count < max_iter:
        improved = False
        for old_idx in current_solution:
            for new_idx in range(num_candidates):
                if new_idx in current_solution:
                    continue
                new_solution = current_solution.copy()
                new_solution.remove(old_idx)
                new_solution.append(new_idx)
                new_cost = coverage_compute_cost(new_solution, user_positions, candidate_positions, coverage_radius)

                if new_cost < current_cost * 0.999:
                    current_solution = new_solution
                    current_cost = new_cost
                    improved = True
                    iteration_log.append(
                        {
                            "iter": iter_count,
                            "cost": current_cost,
                            "solution": current_solution.copy(),
                        }
                    )
                    if verbose:
                        print(f"Iteration {iter_count}: New cost = {current_cost:.4f}")
                    break
            if improved:
                break
        if not improved:
            break
        iter_count += 1

    return current_solution, current_cost, iteration_log


def assign_users_to_stations(user_positions, candidate_positions, solution):
    assignment = []
    selected_positions = candidate_positions[solution]
    for user in user_positions:
        distances = [
            haversine_distance(user[0], user[1], station[0], station[1])
            for station in selected_positions
        ]
        assignment.append(int(np.argmin(distances)))
    return assignment


def build_stage_context(config, seed=42, coverage_radius=1.5, max_iter=200, verbose=False):
    random.seed(seed)
    np.random.seed(seed)
    candidate_positions, user_positions, user_services = load_input_from_excel(config["data_file"])
    k, n2_raw, active_indices, densities = resolve_k(
        candidate_positions,
        user_positions,
        sigma_min=config["sigma_min"],
        n2_adjust=config["n2_adjust"],
        coverage_radius=coverage_radius,
        target_servers=config["target_servers"],
    )
    best_solution, best_cost, iteration_log = coverage_local_search(
        candidate_positions,
        user_positions,
        k,
        coverage_radius=coverage_radius,
        max_iter=max_iter,
        verbose=verbose,
    )
    servers_pos = candidate_positions[best_solution]
    assigned_server = assign_users_to_stations(user_positions, candidate_positions, best_solution)
    return {
        "candidate_positions": candidate_positions,
        "user_positions": user_positions,
        "user_services": user_services,
        "k": k,
        "n2_raw": n2_raw,
        "active_indices": active_indices,
        "densities": densities,
        "best_solution": best_solution,
        "best_cost": best_cost,
        "iteration_log": iteration_log,
        "servers_pos": servers_pos,
        "assigned_server": assigned_server,
    }
