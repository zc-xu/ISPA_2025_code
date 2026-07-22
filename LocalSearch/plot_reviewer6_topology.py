import argparse
import io
import math
import os
import time

import matplotlib

matplotlib.use("Agg")
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests
from matplotlib.patches import Ellipse
from matplotlib.ticker import MultipleLocator
from PIL import Image


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CONFIG = "real_sparse_r04_c40_u130_k10_s1"
DEFAULT_DATA = os.path.join(
    PROJECT_ROOT,
    "data",
    "real_region",
    f"input_data_{DEFAULT_CONFIG}_8.xlsx",
)
DEFAULT_STAGE1 = os.path.join(
    PROJECT_ROOT,
    "output",
    "csv",
    "real_region_stage1_screen_c40_u130_k10.csv",
)
DEFAULT_STEM = "reviewer6_generalization_topology"
SERVICE_COLORS = [
    "blue",
    "green",
    "red",
    "orange",
    "purple",
    "brown",
    "cyan",
    "magenta",
]


def tile_coordinates(longitude, latitude, zoom):
    scale = 2**zoom
    latitude = np.clip(latitude, -85.05112878, 85.05112878)
    x = (longitude + 180.0) / 360.0 * scale
    latitude_rad = np.deg2rad(latitude)
    y = (1.0 - np.arcsinh(np.tan(latitude_rad)) / np.pi) / 2.0 * scale
    return x, y


def tile_edge(tile_x, tile_y, zoom):
    scale = 2**zoom
    longitude = tile_x / scale * 360.0 - 180.0
    latitude = np.rad2deg(np.arctan(np.sinh(np.pi * (1.0 - 2.0 * tile_y / scale))))
    return longitude, latitude


def download_tile(session, zoom, tile_x, tile_y, cache_dir, retries=3):
    os.makedirs(cache_dir, exist_ok=True)
    path = os.path.join(cache_dir, f"{zoom}_{tile_x}_{tile_y}.png")
    if os.path.exists(path):
        with Image.open(path) as image:
            return image.convert("RGB")

    url = f"https://tile.openstreetmap.org/{zoom}/{tile_x}/{tile_y}.png"
    last_error = None
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=20)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content)).convert("RGB")
            image.save(path)
            time.sleep(0.05)
            return image
        except Exception as exc:
            last_error = exc
            time.sleep(0.5 * (attempt + 1))
    raise RuntimeError(f"Could not download map tile {zoom}/{tile_x}/{tile_y}: {last_error}")


def build_basemap(bounds, zoom, cache_dir):
    min_lon, max_lon, min_lat, max_lat = bounds
    x0_float, y0_float = tile_coordinates(min_lon, max_lat, zoom)
    x1_float, y1_float = tile_coordinates(max_lon, min_lat, zoom)
    x0 = int(math.floor(x0_float))
    x1 = int(math.floor(x1_float))
    y0 = int(math.floor(y0_float))
    y1 = int(math.floor(y1_float))

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "MEC-generalization-research/1.0 (local publication figure)",
        }
    )
    rows = []
    for tile_y in range(y0, y1 + 1):
        tiles = [
            download_tile(session, zoom, tile_x, tile_y, cache_dir)
            for tile_x in range(x0, x1 + 1)
        ]
        row = Image.new("RGB", (256 * len(tiles), 256))
        for index, tile in enumerate(tiles):
            row.paste(tile, (index * 256, 0))
        rows.append(row)

    mosaic = Image.new("RGB", (rows[0].width, 256 * len(rows)))
    for index, row in enumerate(rows):
        mosaic.paste(row, (0, index * 256))

    west, north = tile_edge(x0, y0, zoom)
    east, south = tile_edge(x1 + 1, y1 + 1, zoom)
    return mosaic, (west, east, south, north), (x1 - x0 + 1) * (y1 - y0 + 1)


def load_instance(data_path, stage1_path, config):
    candidates = pd.read_excel(data_path, sheet_name="candidates").to_numpy(dtype=float)
    users = pd.read_excel(data_path, sheet_name="users").to_numpy(dtype=float)
    services = (
        pd.read_excel(data_path, sheet_name="services")
        .to_numpy()
        .reshape(-1)
        .astype(int)
    )
    stage1 = pd.read_csv(stage1_path)
    selected_row = stage1[stage1["Config"] == config]
    if len(selected_row) != 1:
        raise ValueError(f"Expected one Stage-I row for {config}, found {len(selected_row)}.")
    selected = [int(value) for value in selected_row.iloc[0]["SelectedSolution"].split()]
    return candidates, users, services, selected


def nearest_assignments(users, candidates, selected):
    selected_positions = candidates[selected]
    mean_latitude = np.mean(np.vstack([users, selected_positions])[:, 1])
    longitude_scale = math.cos(math.radians(mean_latitude))
    user_xy = np.column_stack([users[:, 0] * longitude_scale, users[:, 1]])
    server_xy = np.column_stack(
        [selected_positions[:, 0] * longitude_scale, selected_positions[:, 1]]
    )
    squared_distance = np.sum((user_xy[:, None, :] - server_xy[None, :, :]) ** 2, axis=2)
    return np.argmin(squared_distance, axis=1)


def plot_topology(
    candidates,
    users,
    services,
    selected,
    coverage_radius_km,
    output_stem,
    zoom=14,
    use_basemap=True,
):
    selected_positions = candidates[selected]
    mean_latitude = float(np.mean(np.vstack([candidates, users])[:, 1]))
    latitude_radius = coverage_radius_km / 111.0
    longitude_radius = coverage_radius_km / (111.0 * math.cos(math.radians(mean_latitude)))

    min_lon = min(np.min(candidates[:, 0]), np.min(users[:, 0]), np.min(selected_positions[:, 0] - longitude_radius))
    max_lon = max(np.max(candidates[:, 0]), np.max(users[:, 0]), np.max(selected_positions[:, 0] + longitude_radius))
    min_lat = min(np.min(candidates[:, 1]), np.min(users[:, 1]), np.min(selected_positions[:, 1] - latitude_radius))
    max_lat = max(np.max(candidates[:, 1]), np.max(users[:, 1]), np.max(selected_positions[:, 1] + latitude_radius))
    longitude_pad = max(0.002, 0.025 * (max_lon - min_lon))
    latitude_pad = max(0.002, 0.025 * (max_lat - min_lat))
    bounds = (
        min_lon - longitude_pad,
        max_lon + longitude_pad,
        min_lat - latitude_pad,
        max_lat + latitude_pad,
    )

    plt.rcParams["font.family"] = "Arial"
    plt.rcParams["axes.unicode_minus"] = False
    fig, ax = plt.subplots(figsize=(8.0, 7.3))
    tile_count = 0
    if use_basemap:
        cache_dir = os.path.join(PROJECT_ROOT, "output", "map_cache", "osm")
        basemap, extent, tile_count = build_basemap(bounds, zoom, cache_dir)
        ax.imshow(basemap, extent=extent, aspect="auto", alpha=0.68, zorder=0)

    assignments = nearest_assignments(users, candidates, selected)
    for user_index, selected_index in enumerate(assignments):
        ux, uy = users[user_index]
        sx, sy = selected_positions[selected_index]
        ax.plot([ux, sx], [uy, sy], color="#8A8A8A", alpha=0.34, linewidth=0.45, zorder=1)

    unselected = [index for index in range(len(candidates)) if index not in set(selected)]
    label_effect = [path_effects.withStroke(linewidth=2.0, foreground="white", alpha=0.88)]
    for index in unselected:
        longitude, latitude = candidates[index]
        ax.scatter(longitude, latitude, color="gray", s=38, alpha=0.62, zorder=2)
        ax.text(
            longitude + 0.00022,
            latitude + 0.00022,
            str(index),
            fontsize=8.5,
            color="#343434",
            alpha=0.82,
            path_effects=label_effect,
            zorder=5,
        )

    for service_type, color in enumerate(SERVICE_COLORS):
        mask = services == service_type
        ax.scatter(
            users[mask, 0],
            users[mask, 1],
            color=color,
            s=48,
            alpha=0.72,
            label=rf"$s_{{{service_type}}}$",
            zorder=3,
        )

    for index in selected:
        longitude, latitude = candidates[index]
        ax.scatter(longitude, latitude, color="red", marker="*", s=250, zorder=6)
        ax.text(
            longitude + 0.00055,
            latitude + 0.00055,
            str(index),
            fontsize=12,
            color="red",
            path_effects=label_effect,
            zorder=7,
        )
        circle = Ellipse(
            (longitude, latitude),
            width=2.0 * longitude_radius,
            height=2.0 * latitude_radius,
            fill=False,
            edgecolor="red",
            linestyle="--",
            linewidth=1.0,
            alpha=0.52,
            zorder=4,
        )
        ax.add_patch(circle)

    ax.set_xlim(bounds[0], bounds[1])
    ax.set_ylim(bounds[2], bounds[3])
    ax.set_aspect(1.0 / math.cos(math.radians(mean_latitude)))
    ax.xaxis.set_major_locator(MultipleLocator(0.02))
    ax.yaxis.set_major_locator(MultipleLocator(0.02))
    ax.ticklabel_format(useOffset=False, style="plain")
    ax.tick_params(axis="both", labelsize=15)
    ax.set_xlabel("Longitude", fontsize=17)
    ax.set_ylabel("Latitude", fontsize=17)
    ax.grid(True, axis="y", linestyle="--", linewidth=0.75, color="#8A8A8A", alpha=0.65, zorder=1)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, 0.995),
        ncol=8,
        fontsize=10,
        handletextpad=0.3,
        columnspacing=0.8,
        borderaxespad=0.2,
        frameon=True,
    )
    if use_basemap:
        ax.text(
            0.995,
            0.008,
            "© OpenStreetMap contributors",
            transform=ax.transAxes,
            ha="right",
            va="bottom",
            fontsize=7,
            color="#4B5563",
            path_effects=label_effect,
            zorder=8,
        )

    fig.subplots_adjust(left=0.13, right=0.98, bottom=0.11, top=0.98)
    png_path = os.path.join(PROJECT_ROOT, "output", "png", f"{output_stem}.png")
    pdf_path = os.path.join(PROJECT_ROOT, "output", "pdf", f"{output_stem}.pdf")
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    fig.savefig(png_path, dpi=300, bbox_inches="tight")
    fig.savefig(pdf_path, format="pdf", bbox_inches="tight")
    plt.close(fig)
    return png_path, pdf_path, tile_count


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render the Reviewer-6 real-region topology in the paper's Stage-I map style."
    )
    parser.add_argument("--data", default=DEFAULT_DATA)
    parser.add_argument("--stage1-csv", default=DEFAULT_STAGE1)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--coverage-radius", type=float, default=1.5)
    parser.add_argument("--zoom", type=int, default=14)
    parser.add_argument("--output-stem", default=DEFAULT_STEM)
    parser.add_argument("--no-basemap", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    candidates, users, services, selected = load_instance(
        os.path.abspath(args.data),
        os.path.abspath(args.stage1_csv),
        args.config,
    )
    png_path, pdf_path, tile_count = plot_topology(
        candidates,
        users,
        services,
        selected,
        coverage_radius_km=args.coverage_radius,
        output_stem=args.output_stem,
        zoom=args.zoom,
        use_basemap=not args.no_basemap,
    )
    print(f"Config: {args.config}")
    print(f"Candidates/users/selected: {len(candidates)}/{len(users)}/{len(selected)}")
    print(f"Selected indices: {' '.join(map(str, selected))}")
    print(f"Map tiles used: {tile_count}")
    print(f"Saved: {png_path}")
    print(f"Saved: {pdf_path}")


if __name__ == "__main__":
    main()
