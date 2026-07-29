from __future__ import annotations

import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from lxml import etree as ET


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "backups" / "2026-07-19_original_baseline_rebuild" / "stage2_user_template_original.xlsx"
OUTPUT = ROOT / "targeted_revision_original_based" / "stage2_five_method_with_dqn_errorbars.xlsx"

DQN_VALUES = {
    ("Sheet1", "B9"): 0.5770307911,
    ("Sheet1", "V9"): 0.6125035722,
    ("Sheet1", "B26"): 0.4971969240,
    ("Sheet1", "V26"): 0.4840131472,
    ("Sheet1 (2)", "B9"): 0.4051715848,
    ("Sheet1 (2)", "V9"): 0.6125035722,
    ("Sheet1 (2)", "B26"): 0.6077332731,
    ("Sheet1 (2)", "V26"): 0.7077210813,
}

NS = {
    "x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
    "c": "http://schemas.openxmlformats.org/drawingml/2006/chart",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "c15": "http://schemas.microsoft.com/office/drawing/2012/chart",
    "c16": "http://schemas.microsoft.com/office/drawing/2014/chart",
    "c16r2": "http://schemas.microsoft.com/office/drawing/2015/06/chart",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "c14": "http://schemas.microsoft.com/office/drawing/2007/8/2/chart",
    "x14ac": "http://schemas.microsoft.com/office/spreadsheetml/2009/9/ac",
    "xr": "http://schemas.microsoft.com/office/spreadsheetml/2014/revision",
    "xr2": "http://schemas.microsoft.com/office/spreadsheetml/2015/revision2",
    "xr3": "http://schemas.microsoft.com/office/spreadsheetml/2016/revision3",
}

def q(prefix: str, name: str) -> str:
    return f"{{{NS[prefix]}}}{name}"


def column_number(column: str) -> int:
    value = 0
    for char in column:
        value = value * 26 + ord(char) - ord("A") + 1
    return value


def split_address(address: str) -> tuple[str, int]:
    match = re.fullmatch(r"([A-Z]+)(\d+)", address)
    if not match:
        raise ValueError(address)
    return match.group(1), int(match.group(2))


def worksheet_paths(workdir: Path) -> dict[str, Path]:
    workbook = ET.parse(workdir / "xl" / "workbook.xml").getroot()
    relationships = ET.parse(workdir / "xl" / "_rels" / "workbook.xml.rels").getroot()
    rel_targets = {
        item.attrib["Id"]: item.attrib["Target"]
        for item in relationships.findall(q("pr", "Relationship"))
    }
    result: dict[str, Path] = {}
    for sheet in workbook.find(q("x", "sheets")):
        target = rel_targets[sheet.attrib[q("r", "id")]].replace("/", "\\")
        result[sheet.attrib["name"]] = workdir / "xl" / target
    return result


def set_cell(root: ET.Element, address: str, value: str | float, style_source: str) -> None:
    column, row_number = split_address(address)
    sheet_data = root.find(q("x", "sheetData"))
    row = next((item for item in sheet_data.findall(q("x", "row")) if int(item.attrib["r"]) == row_number), None)
    if row is None:
        row = ET.Element(q("x", "row"), {"r": str(row_number)})
        insert_at = next(
            (index for index, item in enumerate(sheet_data) if int(item.attrib["r"]) > row_number),
            len(sheet_data),
        )
        sheet_data.insert(insert_at, row)

    cell = next((item for item in row.findall(q("x", "c")) if item.attrib.get("r") == address), None)
    source = next((item for item in row.findall(q("x", "c")) if item.attrib.get("r") == style_source), None)
    if cell is None:
        cell = ET.Element(q("x", "c"), {"r": address})
        insert_at = next(
            (
                index
                for index, item in enumerate(row.findall(q("x", "c")))
                if column_number(split_address(item.attrib["r"])[0]) > column_number(column)
            ),
            len(row),
        )
        row.insert(insert_at, cell)
    if source is not None and "s" in source.attrib:
        cell.attrib["s"] = source.attrib["s"]

    for child in list(cell):
        cell.remove(child)
    if isinstance(value, str):
        cell.attrib["t"] = "inlineStr"
        inline = ET.SubElement(cell, q("x", "is"))
        ET.SubElement(inline, q("x", "t")).text = value
    else:
        cell.attrib.pop("t", None)
        ET.SubElement(cell, q("x", "v")).text = f"{value:.10f}"


def identify_chart(cat_formula: str) -> tuple[str, str, str, str] | None:
    sheet = "Sheet1 (2)" if "Sheet1 (2)" in cat_formula else "Sheet1" if "Sheet1" in cat_formula else None
    if sheet is None:
        return None
    match = re.search(r"\$([BV])\$(9|26):\$[A-Z]+\$(?:9|26)", cat_formula)
    if not match:
        return None
    start_col, row = match.groups()
    key = f"{start_col}{row}"
    end_col = "F" if start_col == "B" else "Z"
    value_row = "10" if row == "9" else "27"
    return sheet, key, end_col, value_row


def replace_formula_range(formula: str, end_col: str, value_row: str, categories: bool) -> str:
    row = "9" if value_row == "10" else "26"
    start_col = "B" if end_col == "F" else "V"
    target_row = row if categories else value_row
    return re.sub(
        rf"\${start_col}\${target_row}:\$[A-Z]+\${target_row}",
        rf"${start_col}${target_row}:${end_col}${target_row}",
        formula,
    )


def reset_cache(cache: ET.Element, values: list[str]) -> None:
    point_count = cache.find(q("c", "ptCount"))
    if point_count is None:
        point_count = ET.SubElement(cache, q("c", "ptCount"))
    point_count.attrib["val"] = str(len(values))
    for point in list(cache.findall(q("c", "pt"))):
        cache.remove(point)
    for index, value in enumerate(values):
        point = ET.SubElement(cache, q("c", "pt"), {"idx": str(index)})
        ET.SubElement(point, q("c", "v")).text = value


def dqn_data_point() -> ET.Element:
    point = ET.Element(q("c", "dPt"))
    ET.SubElement(point, q("c", "idx"), {"val": "4"})
    ET.SubElement(point, q("c", "invertIfNegative"), {"val": "0"})
    ET.SubElement(point, q("c", "bubble3D"), {"val": "0"})
    properties = ET.SubElement(point, q("c", "spPr"))
    pattern = ET.SubElement(properties, q("a", "pattFill"), {"prst": "ltDnDiag"})
    foreground = ET.SubElement(pattern, q("a", "fgClr"))
    ET.SubElement(foreground, q("a", "srgbClr"), {"val": "8A6CC2"})
    background = ET.SubElement(pattern, q("a", "bgClr"))
    ET.SubElement(background, q("a", "schemeClr"), {"val": "bg1"})
    line = ET.SubElement(properties, q("a", "ln"))
    solid = ET.SubElement(line, q("a", "solidFill"))
    ET.SubElement(solid, q("a", "srgbClr"), {"val": "8A6CC2"})
    ET.SubElement(properties, q("a", "effectLst"))
    return point


def patch_chart(path: Path) -> bool:
    tree = ET.parse(path)
    root = tree.getroot()
    changed = False
    for series in root.findall(".//c:ser", NS):
        cat_ref = series.find("c:cat/c:strRef", NS)
        val_ref = series.find("c:val/c:numRef", NS)
        if cat_ref is None or val_ref is None:
            continue
        cat_formula = cat_ref.find(q("c", "f"))
        val_formula = val_ref.find(q("c", "f"))
        if cat_formula is None or val_formula is None or not cat_formula.text:
            continue
        identity = identify_chart(cat_formula.text)
        if identity is None:
            continue
        sheet, key, end_col, value_row = identity
        dqn_value = DQN_VALUES[(sheet, key)]

        cat_formula.text = replace_formula_range(cat_formula.text, end_col, value_row, categories=True)
        val_formula.text = replace_formula_range(val_formula.text, end_col, value_row, categories=False)
        for full_ref in series.findall(".//c15:sqref", NS):
            if full_ref.text:
                full_ref.text = replace_formula_range(
                    full_ref.text,
                    end_col,
                    value_row,
                    categories=(f"${'9' if value_row == '10' else '26'}" in full_ref.text),
                )

        string_cache = cat_ref.find(q("c", "strCache"))
        number_cache = val_ref.find(q("c", "numCache"))
        if string_cache is not None:
            labels = [point.find(q("c", "v")).text for point in string_cache.findall(q("c", "pt"))[:4]]
            reset_cache(string_cache, [*labels, "DQN"])
        if number_cache is not None:
            values = [point.find(q("c", "v")).text for point in number_cache.findall(q("c", "pt"))[:4]]
            reset_cache(number_cache, [*values, f"{dqn_value:.10f}"])

        for existing in list(series.findall(q("c", "dPt"))):
            index = existing.find(q("c", "idx"))
            if index is not None and index.attrib.get("val") == "4":
                series.remove(existing)
        error_bars = series.find(q("c", "errBars"))
        insert_at = list(series).index(error_bars) if error_bars is not None else len(series)
        series.insert(insert_at, dqn_data_point())
        changed = True

    if changed:
        tree.write(path, encoding="utf-8", xml_declaration=True)
    return changed


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="stage2_ooxml_", dir=ROOT / "tmp") as temp_dir:
        workdir = Path(temp_dir)
        with zipfile.ZipFile(SOURCE) as archive:
            archive.extractall(workdir)

        sheets = worksheet_paths(workdir)
        for sheet_name in ("Sheet1", "Sheet1 (2)"):
            tree = ET.parse(sheets[sheet_name])
            root = tree.getroot()
            values = {
                "Sheet1": {"F10": DQN_VALUES[(sheet_name, "B9")], "Z10": DQN_VALUES[(sheet_name, "V9")], "F27": DQN_VALUES[(sheet_name, "B26")], "Z27": DQN_VALUES[(sheet_name, "V26")]},
                "Sheet1 (2)": {"F10": DQN_VALUES[(sheet_name, "B9")], "Z10": DQN_VALUES[(sheet_name, "V9")], "F27": DQN_VALUES[(sheet_name, "B26")], "Z27": DQN_VALUES[(sheet_name, "V26")]},
            }[sheet_name]
            for label_cell in ("F9", "Z9", "F26", "Z26"):
                source_column = "E" if label_cell.startswith("F") else "Y"
                source_cell = f"{source_column}{split_address(label_cell)[1]}"
                set_cell(root, label_cell, "DQN", source_cell)
            for value_cell, value in values.items():
                source_column = "E" if value_cell.startswith("F") else "Y"
                source_cell = f"{source_column}{split_address(value_cell)[1]}"
                set_cell(root, value_cell, value, source_cell)
            tree.write(sheets[sheet_name], encoding="utf-8", xml_declaration=True)

        changed_charts = 0
        for chart in (workdir / "xl" / "charts").glob("chart*.xml"):
            changed_charts += int(patch_chart(chart))
        if changed_charts != 8:
            raise RuntimeError(f"Expected 8 Stage-II charts, patched {changed_charts}")

        temp_output = OUTPUT.with_suffix(".tmp.xlsx")
        with zipfile.ZipFile(temp_output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for item in workdir.rglob("*"):
                if item.is_file():
                    archive.write(item, item.relative_to(workdir).as_posix())
        shutil.move(temp_output, OUTPUT)
    print(OUTPUT)


if __name__ == "__main__":
    main()
