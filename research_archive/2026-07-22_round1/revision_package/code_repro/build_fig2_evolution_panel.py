from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "outputs" / "figure_candidates"


COLORS = {
    "blue": (0.24, 0.45, 0.61),
    "blue_fill": (0.95, 0.98, 1.00),
    "purple": (0.42, 0.22, 0.45),
    "purple_fill": (0.99, 0.96, 0.99),
    "orange": (0.86, 0.51, 0.12),
    "orange_fill": (1.00, 0.94, 0.84),
    "green": (0.35, 0.55, 0.31),
    "green_fill": (0.92, 0.97, 0.90),
    "red": (0.72, 0.28, 0.25),
    "red_fill": (1.00, 0.95, 0.94),
    "gray": (0.15, 0.15, 0.15),
}


def add_box(ax, xy, width, height, text, edge, fill, fontsize=10.5):
    box = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.025,rounding_size=0.11",
        linewidth=1.7,
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
        linespacing=1.12,
        zorder=4,
    )


def add_arrow(ax, start, end, connectionstyle="arc3", color=None, linewidth=1.6):
    arrow = FancyArrowPatch(
        start,
        end,
        arrowstyle="-|>",
        mutation_scale=13,
        linewidth=linewidth,
        color=color or COLORS["gray"],
        connectionstyle=connectionstyle,
        shrinkA=2,
        shrinkB=2,
        zorder=2,
    )
    ax.add_patch(arrow)


def add_polyline_arrow(ax, points, color=None, linewidth=1.6):
    line_color = color or COLORS["gray"]
    for start, end in zip(points[:-2], points[1:-1]):
        ax.plot(
            [start[0], end[0]],
            [start[1], end[1]],
            color=line_color,
            linewidth=linewidth,
            solid_capstyle="round",
            zorder=1,
        )
    add_arrow(ax, points[-2], points[-1], color=line_color, linewidth=linewidth)


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
    fig, ax = plt.subplots(figsize=(13.6, 4.45))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    add_box(
        ax,
        (0.35, 3.05),
        1.65,
        0.92,
        "Parent Population\n$P_t$",
        COLORS["blue"],
        COLORS["blue_fill"],
    )
    add_box(
        ax,
        (2.55, 3.05),
        1.85,
        0.92,
        "Crossover &\nMutation",
        COLORS["purple"],
        COLORS["purple_fill"],
    )
    add_box(
        ax,
        (4.95, 3.05),
        1.55,
        0.92,
        "Offspring\n$Q_t$",
        COLORS["orange"],
        COLORS["orange_fill"],
    )
    add_box(
        ax,
        (7.05, 3.05),
        1.70,
        0.92,
        "Binary\nRounding",
        COLORS["orange"],
        COLORS["orange_fill"],
    )

    cx, cy, dw, dh = 10.75, 3.51, 2.55, 1.60
    diamond = Polygon(
        [
            (cx, cy + dh / 2),
            (cx + dw / 2, cy),
            (cx, cy - dh / 2),
            (cx - dw / 2, cy),
        ],
        closed=True,
        linewidth=1.7,
        edgecolor=COLORS["green"],
        facecolor=COLORS["green_fill"],
        zorder=3,
    )
    ax.add_patch(diamond)
    ax.text(
        cx,
        cy + 0.18,
        "Capacity feasible?",
        ha="center",
        va="center",
        fontsize=10.3,
        fontweight="semibold",
        zorder=4,
    )
    ax.text(
        cx,
        cy - 0.20,
        r"$\sum_w z_{jw}\leq V_j$, for every $j$",
        ha="center",
        va="center",
        fontsize=9.2,
        zorder=4,
    )

    add_box(
        ax,
        (8.35, 1.55),
        2.55,
        1.03,
        "Repair Capacity\nRandomly deactivate selected services",
        COLORS["red"],
        COLORS["red_fill"],
        fontsize=9.25,
    )
    add_box(
        ax,
        (11.55, 1.55),
        2.05,
        1.03,
        "Evaluate\nCost and Delay",
        COLORS["blue"],
        COLORS["blue_fill"],
        fontsize=10.0,
    )
    add_box(
        ax,
        (7.95, 0.15),
        2.05,
        0.88,
        "Merge\n$P_t \cup Q_t$",
        COLORS["blue"],
        COLORS["blue_fill"],
        fontsize=10.0,
    )
    add_box(
        ax,
        (4.65, 0.15),
        2.45,
        0.88,
        "Non-dominated Sort\n& Crowding",
        COLORS["purple"],
        COLORS["purple_fill"],
        fontsize=9.7,
    )
    add_box(
        ax,
        (1.75, 0.15),
        2.05,
        0.88,
        "Next Generation\n$P_{t+1}$",
        COLORS["blue"],
        COLORS["blue_fill"],
        fontsize=9.8,
    )

    add_arrow(ax, (2.00, 3.51), (2.55, 3.51))
    add_arrow(ax, (4.40, 3.51), (4.95, 3.51))
    add_arrow(ax, (6.50, 3.51), (7.05, 3.51))
    add_arrow(ax, (8.75, 3.51), (9.48, 3.51))

    add_polyline_arrow(
        ax,
        [(10.25, 2.96), (9.62, 2.70), (9.62, 2.58)],
        color=COLORS["red"],
    )
    ax.text(9.72, 2.76, "No", color=COLORS["red"], fontsize=9.3, fontweight="semibold")
    add_arrow(ax, (10.90, 2.73), (12.25, 2.58), color=COLORS["green"])
    ax.text(11.36, 2.82, "Yes", color=COLORS["green"], fontsize=9.3, fontweight="semibold")
    add_arrow(ax, (10.90, 2.07), (11.55, 2.07), color=COLORS["red"])

    add_polyline_arrow(ax, [(12.58, 1.55), (12.58, 0.92), (10.00, 0.59)])
    add_arrow(ax, (7.95, 0.59), (7.10, 0.59))
    add_arrow(ax, (4.65, 0.59), (3.80, 0.59))

    add_polyline_arrow(
        ax,
        [(1.75, 0.59), (0.55, 0.59), (0.55, 2.75), (0.86, 3.05)],
        color=COLORS["blue"],
    )

    fig.subplots_adjust(left=0.01, right=0.99, top=0.98, bottom=0.03)
    return fig


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    fig = build_figure()
    outputs = [
        OUTPUT_DIR / "fig2_evolutionary_optimization_panel.pdf",
        OUTPUT_DIR / "fig2_evolutionary_optimization_panel.svg",
        OUTPUT_DIR / "fig2_evolutionary_optimization_panel.png",
    ]
    for output in outputs:
        kwargs = {"bbox_inches": "tight", "facecolor": "white", "pad_inches": 0.04}
        if output.suffix == ".png":
            kwargs["dpi"] = 450
        fig.savefig(output, **kwargs)
        print(f"Saved {output}")
    plt.close(fig)


if __name__ == "__main__":
    main()
