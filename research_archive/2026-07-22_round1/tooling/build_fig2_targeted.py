from __future__ import annotations

from io import BytesIO
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
PROJECT = ROOT / "targeted_revision_original_based"
SOURCE = PROJECT / "algo_0421.pdf"
OUTPUT = PROJECT / "fig2_architecture_targeted.pdf"


def arrow(c: canvas.Canvas, points: list[tuple[float, float]], color=(0.10, 0.10, 0.10)) -> None:
    c.setStrokeColorRGB(*color)
    c.setFillColorRGB(*color)
    c.setLineWidth(1.15)
    path = c.beginPath()
    path.moveTo(*points[0])
    for point in points[1:]:
        path.lineTo(*point)
    c.drawPath(path, stroke=1, fill=0)

    (x0, y0), (x1, y1) = points[-2], points[-1]
    dx, dy = x1 - x0, y1 - y0
    length = max((dx * dx + dy * dy) ** 0.5, 1e-6)
    ux, uy = dx / length, dy / length
    px, py = -uy, ux
    size = 4.0
    wing = 2.2
    c.line(x1, y1, x1 - size * ux + wing * px, y1 - size * uy + wing * py)
    c.line(x1, y1, x1 - size * ux - wing * px, y1 - size * uy - wing * py)


def rounded_box(
    c: canvas.Canvas,
    x: float,
    y: float,
    w: float,
    h: float,
    lines: list[str],
    stroke: tuple[float, float, float],
    fill: tuple[float, float, float],
    font_size: float = 6.4,
) -> None:
    c.setLineWidth(1.0)
    c.setStrokeColorRGB(*stroke)
    c.setFillColorRGB(*fill)
    c.roundRect(x, y, w, h, 4, stroke=1, fill=1)
    c.setFillColorRGB(0.08, 0.08, 0.08)
    c.setFont("Helvetica-Bold", font_size)
    leading = font_size + 1.0
    total = leading * len(lines)
    baseline = y + (h + total) / 2 - leading + 0.7
    for index, line in enumerate(lines):
        c.drawCentredString(x + w / 2, baseline - index * leading, line)


def decision_diamond(c: canvas.Canvas, cx: float, cy: float, w: float, h: float) -> None:
    c.setLineWidth(1.0)
    c.setStrokeColorRGB(0.31, 0.49, 0.27)
    c.setFillColorRGB(0.91, 0.96, 0.89)
    path = c.beginPath()
    path.moveTo(cx, cy + h / 2)
    path.lineTo(cx + w / 2, cy)
    path.lineTo(cx, cy - h / 2)
    path.lineTo(cx - w / 2, cy)
    path.close()
    c.drawPath(path, stroke=1, fill=1)
    c.setFillColorRGB(0.08, 0.08, 0.08)
    c.setFont("Helvetica-Bold", 5.7)
    c.drawCentredString(cx, cy + 5.2, "Capacity")
    c.drawCentredString(cx, cy - 1.8, "feasible?")
    c.setFont("Helvetica", 5.1)
    c.drawCentredString(cx, cy - 8.5, r"sum z_jw <= V_j")


def build_overlay(width: float, height: float) -> BytesIO:
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=(width, height))

    # Replace only the evolutionary-optimization interior. The original panel
    # border, stage header, inter-panel arrows, and the rest of Fig. 2 remain intact.
    c.setFillColorRGB(1, 1, 1)
    c.rect(203.0, 10.0, 262.0, 134.0, stroke=0, fill=1)

    # Correct the Stage-I label without disturbing the surrounding artwork.
    c.setFillColorRGB(1, 1, 1)
    c.rect(294.0, 201.0, 108.0, 22.0, stroke=0, fill=1)
    c.setFillColorRGB(0.05, 0.05, 0.05)
    c.setFont("Helvetica-Bold", 9.3)
    c.drawCentredString(348.0, 208.0, "Candidate BSs")

    blue = (0.22, 0.43, 0.58)
    purple = (0.39, 0.18, 0.42)
    orange = (0.82, 0.48, 0.13)
    red = (0.67, 0.25, 0.24)
    light_blue = (0.94, 0.97, 0.99)
    light_purple = (0.98, 0.95, 0.98)
    light_orange = (1.00, 0.94, 0.84)
    light_red = (1.00, 0.94, 0.94)

    rounded_box(c, 210, 102, 46, 27, ["Parent Pop.", "P_t"], blue, light_blue)
    rounded_box(c, 270, 102, 50, 27, ["Crossover", "& Mutation"], purple, light_purple)
    rounded_box(c, 334, 102, 47, 27, ["Offspring", "Q_t"], orange, light_orange)
    decision_diamond(c, 428, 115.5, 58, 39)

    rounded_box(c, 318, 58, 53, 24, ["Repair:", "Drop Service"], red, light_red, 5.9)
    rounded_box(c, 211, 18, 62, 24, ["Merge &", "Evaluate"], blue, light_blue, 6.0)
    rounded_box(c, 289, 18, 64, 24, ["Non-dominated", "Sort"], purple, light_purple, 5.8)
    rounded_box(c, 370, 18, 58, 24, ["Next Gen.", "P_(t+1)"], blue, light_blue, 5.9)

    arrow(c, [(256, 115.5), (270, 115.5)])
    arrow(c, [(320, 115.5), (334, 115.5)])
    arrow(c, [(381, 115.5), (399, 115.5)])

    # Infeasible offspring are repaired before evaluation.
    arrow(c, [(411, 101.5), (395, 88), (371, 70)])
    c.setFillColorRGB(0.42, 0.15, 0.14)
    c.setFont("Helvetica-Bold", 5.4)
    c.drawString(382, 84, "No")

    # Feasible and repaired offspring join at the same merge/evaluation step.
    arrow(c, [(428, 96), (428, 49), (278, 49), (242, 42)])
    c.setFillColorRGB(0.08, 0.08, 0.08)
    c.setFont("Helvetica-Bold", 5.4)
    c.drawString(431, 87, "Yes")
    arrow(c, [(318, 70), (286, 70), (286, 50), (244, 42)], color=purple)

    arrow(c, [(273, 30), (289, 30)])
    arrow(c, [(353, 30), (370, 30)])

    # Redraw the inter-panel arrow last so its arrowhead cannot be hidden by
    # the white replacement panel.
    c.setStrokeColorRGB(0.05, 0.05, 0.05)
    c.setFillColorRGB(1, 1, 1)
    c.setLineWidth(1.0)
    connector = c.beginPath()
    connector.moveTo(186.0, 79.0)
    connector.lineTo(198.0, 79.0)
    connector.lineTo(198.0, 74.0)
    connector.lineTo(209.0, 84.0)
    connector.lineTo(198.0, 94.0)
    connector.lineTo(198.0, 89.0)
    connector.lineTo(186.0, 89.0)
    connector.close()
    c.drawPath(connector, stroke=1, fill=1)

    c.showPage()
    c.save()
    stream.seek(0)
    return stream


def main() -> None:
    base_reader = PdfReader(str(SOURCE))
    page = base_reader.pages[0]
    width = float(page.mediabox.width)
    height = float(page.mediabox.height)
    overlay = PdfReader(build_overlay(width, height)).pages[0]
    page.merge_page(overlay)

    writer = PdfWriter()
    writer.add_page(page)
    with OUTPUT.open("wb") as handle:
        writer.write(handle)
    print(OUTPUT)


if __name__ == "__main__":
    main()
