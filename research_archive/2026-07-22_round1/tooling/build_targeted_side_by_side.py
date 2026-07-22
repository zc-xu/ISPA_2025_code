from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_PDF = (
    ROOT
    / "revision_package"
    / "manuscript"
    / "conference_101719_first_submission.pdf"
)
REVISED_PDF = (
    ROOT
    / "revision_package"
    / "manuscript"
    / "conference_101719_targeted_revision_marked.pdf"
)
OUT_DIR = ROOT / "revision_package"
RENDER_DIR = ROOT / "tmp" / "targeted_comparison"
OUT_PDF = OUT_DIR / "04_original_vs_revised_marked_side_by_side.pdf"
PDFTOPPM = Path(os.environ.get("PDFTOPPM", shutil.which("pdftoppm") or "pdftoppm"))


# Each revised page is paired with the original page containing the closest
# corresponding section. Repeated original pages are intentional because the
# revised manuscript contains two additional pages.
PAGE_MAP = [
    (1, 1, "Title, abstract, and introduction / 标题、摘要与引言"),
    (2, 2, "Fig. 1 and motivation / 图1与研究动机"),
    (2, 3, "Contributions and related work / 贡献与相关工作"),
    (3, 4, "Related work and system model / 相关工作与系统模型"),
    (4, 5, "Notation and latency model / 符号与时延模型"),
    (5, 6, "Problem formulation and decomposition / 问题建模与两阶段分解"),
    (7, 7, "Architecture and CLS / 总体架构与CLS"),
    (8, 8, "CLS and PSP algorithms / CLS与PSP算法"),
    (9, 9, "Stage-II fixed-server comparison and PSP / Stage-II固定服务器对比与PSP"),
    (10, 10, "Hybrid initialization and settings / 混合初始化与实验设置"),
    (11, 11, "Stage-II fixed-user and Pareto figures / Stage-II固定用户与Pareto图"),
    (11, 12, "Baselines, sensitivity, and results / 基线、敏感性与实验结果"),
    (12, 13, "Conclusion and references / 结论与参考文献"),
    (12, 14, "References / 参考文献"),
]


def render_page(pdf: Path, page: int, prefix: str) -> Path:
    stem = RENDER_DIR / f"{prefix}_p{page:02d}"
    output = stem.with_suffix(".png")
    if not output.exists() or output.stat().st_mtime < pdf.stat().st_mtime:
        subprocess.run(
            [
                str(PDFTOPPM),
                "-png",
                "-r",
                "140",
                "-f",
                str(page),
                "-l",
                str(page),
                "-singlefile",
                str(pdf),
                str(stem),
            ],
            check=True,
        )
    return output


def fit_page(image: Image.Image, width: int, height: int) -> Image.Image:
    scale = min(width / image.width, height / image.height)
    size = (round(image.width * scale), round(image.height * scale))
    return image.resize(size, Image.Resampling.LANCZOS)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RENDER_DIR.mkdir(parents=True, exist_ok=True)

    regular = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 18)
    bold = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 23)
    title_font = ImageFont.truetype(r"C:\Windows\Fonts\msyhbd.ttc", 25)

    canvas_width, canvas_height = 2400, 1600
    margin, gap, header_height = 54, 46, 122
    page_width = (canvas_width - 2 * margin - gap) // 2
    page_height = canvas_height - header_height - margin
    spreads: list[Image.Image] = []

    for index, (old_page, new_page, section) in enumerate(PAGE_MAP, start=1):
        old = Image.open(render_page(ORIGINAL_PDF, old_page, "original")).convert("RGB")
        revised = Image.open(render_page(REVISED_PDF, new_page, "revised")).convert("RGB")
        old_fit = fit_page(old, page_width, page_height)
        revised_fit = fit_page(revised, page_width, page_height)

        canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
        draw = ImageDraw.Draw(canvas)
        draw.text(
            (canvas_width // 2, 20),
            f"{index:02d}. {section}",
            fill="#202020",
            font=title_font,
            anchor="ma",
        )
        draw.text(
            (margin + page_width // 2, 68),
            f"Original submission p.{old_page} / 第一次投稿",
            fill="#1F4E79",
            font=bold,
            anchor="ma",
        )
        draw.text(
            (margin + page_width + gap + page_width // 2, 68),
            f"Revised marked p.{new_page} / 修改标记稿",
            fill="#8A1C1C",
            font=bold,
            anchor="ma",
        )
        draw.text(
            (canvas_width // 2, 99),
            "Complete English-Chinese text mapping: 06_complete_original_vs_revised_bilingual_audit.md",
            fill="#555555",
            font=regular,
            anchor="ma",
        )

        old_x = margin + (page_width - old_fit.width) // 2
        revised_x = margin + page_width + gap + (page_width - revised_fit.width) // 2
        old_y = header_height + (page_height - old_fit.height) // 2
        revised_y = header_height + (page_height - revised_fit.height) // 2
        canvas.paste(old_fit, (old_x, old_y))
        canvas.paste(revised_fit, (revised_x, revised_y))
        draw.line(
            (canvas_width // 2, header_height, canvas_width // 2, canvas_height - margin),
            fill="#B0B0B0",
            width=2,
        )
        spreads.append(canvas)

    first, *rest = spreads
    first.save(
        OUT_PDF,
        "PDF",
        resolution=140.0,
        save_all=True,
        append_images=rest,
    )
    print(OUT_PDF)


if __name__ == "__main__":
    main()
