from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "outputs" / "revision_package" / "figures" / "figure1_user_selected.pdf"
OUTPUT = ROOT / "outputs" / "figure_candidates" / "figure1_user_selected_no_outer_border.pdf"


def main() -> None:
    reader = PdfReader(SOURCE)
    if len(reader.pages) != 1:
        raise ValueError(f"Expected a one-page Fig. 1 PDF, found {len(reader.pages)} pages")

    page = reader.pages[0]
    box = page.mediabox
    inset = 1.5  # points; removes the exported page-border stroke without touching content
    cropped = RectangleObject(
        [
            float(box.left) + inset,
            float(box.bottom) + inset,
            float(box.right) - inset,
            float(box.top) - inset,
        ]
    )
    page.mediabox = cropped
    page.cropbox = cropped

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    writer = PdfWriter()
    writer.add_page(page)
    with OUTPUT.open("wb") as stream:
        writer.write(stream)
    print(OUTPUT)


if __name__ == "__main__":
    main()
