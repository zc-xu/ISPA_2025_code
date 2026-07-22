from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Polygon
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "figure_candidates"

COLORS = {
    "blue": "#3B7198",
    "blue_fill": "#F2F8FC",
    "purple": "#6C3A73",
    "purple_fill": "#FCF6FC",
    "orange": "#D67C16",
    "orange_fill": "#FFF0D6",
    "green": "#568A4F",
    "green_fill": "#EAF5E5",
    "red": "#B94A42",
    "red_fill": "#FFF4F2",
    "ink": "#1F1F1F",
}


def add_box(ax, xy, width, height, text, edge, fill, fontsize=8.5):
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.018,rounding_size=0.12",
        linewidth=1.45,
        edgecolor=edge,
        facecolor=fill,
        zorder=3,
    )
    ax.add_patch(box)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        ha="center",
        va="center",
        fontsize=fontsize,
        fontweight="semibold",
        linespacing=1.0,
        zorder=4,
    )


def arrow(ax, start, end, color=None, linewidth=1.35, mutation=10):
    patch = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=mutation,
        linewidth=linewidth,
        color=color or COLORS["ink"],
        shrinkA=1,
        shrinkB=1,
        zorder=2,
    )
    ax.add_patch(patch)


def polyline_arrow(ax, points, color=None, linewidth=1.35):
    line_color = color or COLORS["ink"]
    for start, end in zip(points[:-2], points[1:-1]):
        ax.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            color=line_color,
            linewidth=linewidth,
            solid_capstyle="round",
            zorder=1,
        )
    arrow(ax, points[-2], points[-1], color=line_color, linewidth=linewidth)


def build_figure():
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans"],
            "mathtext.fontset": "stixsans",
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )

    # The reference panel is 513 x 253 px (aspect ratio 2.0277:1).
    fig = plt.figure(figsize=(5.13, 2.53), dpi=100, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 10.26)
    ax.set_ylim(0, 5.06)
    ax.axis("off")

    add_box(
        ax,
        (0.20, 4.05),
        1.86,
        0.78,
        "Parent Pop.\n$P_t$",
        COLORS["blue"],
        COLORS["blue_fill"],
    )
    add_box(
        ax,
        (2.75, 4.05),
        1.98,
        0.78,
        "Crossover &\nMutation",
        COLORS["purple"],
        COLORS["purple_fill"],
        fontsize=8.1,
    )
    add_box(
        ax,
        (5.45, 4.05),
        1.82,
        0.78,
        "Offspring\n$Q_t$",
        COLORS["orange"],
        COLORS["orange_fill"],
    )

    diamond_center = (8.70, 3.32)
    diamond_w, diamond_h = 2.86, 1.58
    diamond = Polygon(
        [
            (diamond_center[0], diamond_center[1] + diamond_h / 2),
            (diamond_center[0] + diamond_w / 2, diamond_center[1]),
            (diamond_center[0], diamond_center[1] - diamond_h / 2),
            (diamond_center[0] - diamond_w / 2, diamond_center[1]),
        ],
        closed=True,
        linewidth=1.45,
        edgecolor=COLORS["green"],
        facecolor=COLORS["green_fill"],
        zorder=3,
    )
    ax.add_patch(diamond)
    ax.text(
        diamond_center[0],
        diamond_center[1] + 0.18,
        "Capacity feasible?",
        ha="center",
        va="center",
        fontsize=8.1,
        fontweight="semibold",
        zorder=4,
    )
    ax.text(
        diamond_center[0],
        diamond_center[1] - 0.18,
        r"$\sum_w z_{jw}\leq V_j$, $\forall j$",
        ha="center",
        va="center",
        fontsize=7.4,
        zorder=4,
    )

    add_box(
        ax,
        (0.18, 1.83),
        2.12,
        0.78,
        "Repair:\nDrop Service",
        COLORS["purple"],
        COLORS["purple_fill"],
        fontsize=8.0,
    )

    add_box(
        ax,
        (0.55, 0.17),
        2.05,
        0.82,
        "Merge &\nEvaluate",
        COLORS["blue"],
        COLORS["blue_fill"],
        fontsize=8.1,
    )
    add_box(
        ax,
        (3.61, 0.17),
        2.24,
        0.82,
        "Non-dominated\nSort & Crowding",
        COLORS["purple"],
        COLORS["purple_fill"],
        fontsize=7.8,
    )
    add_box(
        ax,
        (7.15, 0.17),
        2.08,
        0.82,
        "Next Gen.\n$P_{t+1}$",
        COLORS["blue"],
        COLORS["blue_fill"],
        fontsize=8.1,
    )
    ax.text(9.62, 0.56, r"$\cdots$", fontsize=13, ha="center", va="center")

    arrow(ax, (2.06, 4.44), (2.75, 4.44))
    arrow(ax, (4.73, 4.44), (5.45, 4.44))
    polyline_arrow(ax, [(7.27, 4.44), (8.70, 4.44), (8.70, 4.11)])
    ax.text(7.70, 4.23, "binary rounding", fontsize=6.2, ha="center", va="top")

    # Capacity violation goes to repair.
    polyline_arrow(
        ax,
        [(7.27, 3.32), (1.24, 3.32), (1.24, 2.61)],
        color=COLORS["red"],
    )
    ax.text(
        4.15,
        3.46,
        "Violation",
        color=COLORS["red"],
        fontsize=7.0,
        fontweight="semibold",
        ha="center",
    )

    # Feasible and repaired offspring join before evaluation.
    join = (1.58, 1.27)
    polyline_arrow(
        ax,
        [(8.70, 2.53), (8.70, 1.27), (join[0] + 0.12, join[1])],
        color=COLORS["green"],
    )
    ax.text(8.88, 2.10, "Feasible", color=COLORS["green"], fontsize=6.9, fontweight="semibold")
    arrow(ax, (1.24, 1.83), (join[0], join[1] + 0.11), color=COLORS["purple"])

    join_circle = Circle(join, radius=0.12, facecolor="white", edgecolor=COLORS["ink"], linewidth=1.1, zorder=4)
    ax.add_patch(join_circle)
    ax.text(join[0], join[1] - 0.002, "+", ha="center", va="center", fontsize=8.2, fontweight="bold", zorder=5)
    arrow(ax, (join[0], join[1] - 0.12), (join[0], 0.99))

    arrow(ax, (2.60, 0.58), (3.61, 0.58))
    arrow(ax, (5.85, 0.58), (7.15, 0.58))

    return fig


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = build_figure()
    stem = OUTPUT_DIR / "fig2_evolutionary_optimization_panel_compact"
    fig.savefig(stem.with_suffix(".pdf"), facecolor="white", pad_inches=0)
    fig.savefig(stem.with_suffix(".svg"), facecolor="white", pad_inches=0)
    png_path = stem.with_suffix(".png")
    fig.savefig(png_path, facecolor="white", dpi=100, pad_inches=0)
    plt.close(fig)

    with Image.open(png_path) as image:
        if image.size != (513, 253):
            image.resize((513, 253), Image.Resampling.LANCZOS).save(png_path)
    print(stem)


if __name__ == "__main__":
    main()
