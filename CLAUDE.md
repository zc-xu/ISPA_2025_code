# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a research codebase for **MEC (Mobile Edge Computing) base station deployment optimization**. The project implements and compares algorithms for selecting optimal base station locations to minimize communication cost and latency for geo-distributed users. The geographic data is centered on Beijing (longitude ~116.3–116.4, latitude ~39.93–40.01).

## Project Structure

```
D:\pythonProject\
├── main.py                          # Primary experiment runner
├── data/                            # All input xlsx data files
│   └── input_data_*.xlsx
├── output/                          # All generated outputs
│   ├── pdf/                         # PDF plots (iteration, nsga, hybrid process)
│   ├── npz/                         # NSGA-II Pareto front result files
│   └── excel/                       # NSGA-II normalized result spreadsheets
├── assets/
│   └── background.jpg               # Map background image for plots
├── LocalSearch/                     # Algorithm code package (also contains venv)
│   ├── __init__.py
│   ├── compute_delay.py
│   ├── nsga_service_deploy.py
│   ├── new_nsga.py
│   ├── service_selection_strategies.py
│   ├── station_selection_strategies.py
│   ├── coverage_local_search.py
│   ├── compare_results.py
│   ├── generate_user.py
│   └── [venv: Include/, Lib/, Scripts/, share/]
├── misc/                            # Unrelated utility scripts
│   ├── jueceshu.py                  # Decision tree visualization
│   ├── new.py                       # NetworkX graph demo
│   └── js.py                        # JavaScript snippet
└── lu-visio/                        # Visio diagram files
```

## Running the Code

The project uses a Python 3.8 virtual environment located at `LocalSearch/`. Activate it before running. **All scripts should be run from the project root directory.**

```bash
# Windows
LocalSearch\Scripts\activate

# Run the main optimization experiment
python main.py

# Run the NSGA-II service deployment experiment
python -m LocalSearch.nsga_service_deploy

# Run the comparison of saved results (Pareto front plots)
python -m LocalSearch.compare_results
```

There are no automated tests. Scripts are run directly and produce plots (PDF/PNG) and console output. All outputs go to `output/` subdirectories.

## Architecture

**Root level** (`main.py`) — the primary experiment runner. It:
1. Loads candidate base station positions and user positions from `data/input_data_*.xlsx`
2. Computes K (number of stations to deploy) from budget constraints and density filtering
3. Runs `coverage_local_search` to find the cost-minimizing station subset
4. Compares results against baseline strategies (random, density-based, distance-sum, greedy)
5. Visualizes results and saves plots to `output/pdf/`

**`LocalSearch/` package** — contains the main algorithm modules:

| File | Purpose |
|------|---------|
| `compute_delay.py` | Central constants and delay calculations. Defines `SERVICE_DEPLOY_COSTS`, `SERVICE_WORKLOADS`, `SERVICE_DATA_SIZES`, `haversine_distance`, `compute_user_delay`, `total_delay_breakdown` |
| `nsga_service_deploy.py` | NSGA-II bi-objective optimization (deploy cost vs. latency) for service-to-server assignment using pymoo. Saves results to `output/npz/` |
| `new_nsga.py` | Alternative NSGA-II implementation with greedy-seeded initial population |
| `service_selection_strategies.py` | Strategy implementations: `compute_objectives`, `greedy_service_deployment_by_cost`, `greedy_service_deployment_by_request` |
| `station_selection_strategies.py` | Baseline station selection: `random_selection`, `density_based_selection`, `distance_sum_selection`, `greedy_k_selection` |
| `coverage_local_search.py` | Standalone local search using Euclidean distance (older version; `main.py` reimplements this with haversine) |
| `compare_results.py` | Loads `.npz` from `output/npz/` and plots normalized Pareto fronts with hypervolume metrics. Saves to `output/pdf/` and `output/excel/` |
| `generate_user.py` | Utility to generate random user position arrays for new test cases |

## Key Data Flow

```
data/input_data_*.xlsx
  ├─ sheet "candidates" → candidate base station (lon, lat) positions
  ├─ sheet "users"      → user (lon, lat) positions  
  └─ sheet "services"   → user service type integers [0..7]
          ↓
  main.py: density filtering → K calculation → local search → assignment → delay breakdown
          ↓
  output/pdf/         ← iteration plots, distribution maps
  output/npz/         ← NSGA-II Pareto front data
  output/excel/       ← normalized result spreadsheets
```

## Important Implementation Details

- **Import convention**: All imports use package-qualified paths (`from LocalSearch.compute_delay import ...`). All scripts are run from the project root.
- **Coordinate convention**: all positions are `[longitude, latitude]` (x=lon, y=lat). Haversine is called as `haversine_distance(lon1, lat1, lon2, lat2)`.
- **`haversine_distance` is duplicated**: it is defined in `compute_delay.py` (canonical), `main.py` (local copy), `station_selection_strategies.py` (local copy), and `coverage_local_search.py` (Euclidean, not haversine). The root `main.py` imports from `compute_delay` but then redefines the function locally — the local definition is what is actually used.
- **K computation**: K = min(N1, N2) where N1 = budget/price and N2 = number of candidate stations meeting user-density threshold. There are hardcoded ±1 adjustments (`N2 = N2 - 1`) tuned per dataset in comments.
- **Result files**: NSGA-II saves Pareto front data as `.npz` files to `output/npz/` which `compare_results.py` loads for comparison plots.
- **Background image**: `plot_final_solution` in `main.py` loads from `assets/background.jpg`.
- **8 service types**: all experiments use `num_services=8`. Constants arrays in `compute_delay.py` are length-8; there are commented-out 16-service variants.

## Dependencies

Key packages (installed in `LocalSearch/` venv, Python 3.8):
- `numpy`, `pandas`, `matplotlib` — core numerics and plotting
- `pymoo==0.6.1.2` — NSGA-II multi-objective optimization
- `openpyxl` / `xlrd` — reading `.xlsx` input files
- `scikit-learn` — used in `misc/jueceshu.py` (decision tree, unrelated to main experiments)
- `folium` — used for map visualizations (heatmap scripts)
- `scipy`, `networkx` — present but minor usage
