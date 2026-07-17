import fs from "node:fs/promises";
import path from "node:path";

import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";


const ROOT = path.resolve(process.cwd());
const CSV_DIR = path.join(ROOT, "output", "csv");
const OUTPUT_PATH = path.join(ROOT, "output", "excel", "reviewer6_generalization_evidence.xlsx");
const PREVIEW_DIR = path.join(ROOT, "output", "workbook_preview", "reviewer6_generalization");

const SOURCES = [
  ["Design", "reviewer6_generalization_design.csv", "DesignTable"],
  ["Stage I", "reviewer6_large_region_stage1.csv", "StageITable"],
  ["Wide Aggregate", "reviewer6_large_region_stage2_aggregate.csv", "WideAggregateTable"],
  ["Wide Detail", "reviewer6_large_region_stage2_detail.csv", "WideDetailTable"],
  ["Main Aggregate", "reviewer6_main_candidate_stage2_aggregate.csv", "MainAggregateTable"],
  ["Main Detail", "reviewer6_main_candidate_stage2_detail.csv", "MainDetailTable"],
];

const COLORS = {
  navy: "#1F4E78",
  blue: "#4C78A8",
  green: "#59A14F",
  orange: "#F28E2B",
  red: "#C1121F",
  ink: "#1F2937",
  muted: "#5B6573",
  paleBlue: "#EAF2F8",
  paleRed: "#FDECEC",
  paleGray: "#F4F6F8",
  line: "#D7DEE5",
  white: "#FFFFFF",
};


function parseCsv(text) {
  const rows = [];
  let row = [];
  let value = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') {
        value += '"';
        i += 1;
      } else if (char === '"') {
        quoted = false;
      } else {
        value += char;
      }
    } else if (char === '"') {
      quoted = true;
    } else if (char === ",") {
      row.push(value);
      value = "";
    } else if (char === "\n") {
      row.push(value.replace(/\r$/, ""));
      rows.push(row);
      row = [];
      value = "";
    } else {
      value += char;
    }
  }
  if (value.length > 0 || row.length > 0) {
    row.push(value.replace(/\r$/, ""));
    rows.push(row);
  }
  return rows.filter((record) => record.some((cell) => cell !== ""));
}


function coerceRows(rows) {
  return rows.map((row, rowIndex) => row.map((cell) => {
    if (rowIndex === 0 || cell === "") return cell === "" ? null : cell;
    if (/^-?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?$/.test(cell)) return Number(cell);
    return cell;
  }));
}


function columnName(index) {
  let value = index + 1;
  let name = "";
  while (value > 0) {
    const remainder = (value - 1) % 26;
    name = String.fromCharCode(65 + remainder) + name;
    value = Math.floor((value - 1) / 26);
  }
  return name;
}


function styleHeader(range) {
  range.format = {
    fill: COLORS.navy,
    font: { bold: true, color: COLORS.white, size: 10 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: COLORS.navy },
  };
  range.format.rowHeight = 34;
}


function applyColumnFormats(sheet, headers, rowCount) {
  headers.forEach((header, index) => {
    const letter = columnName(index);
    const body = sheet.getRange(`${letter}2:${letter}${rowCount}`);
    const normalized = String(header).toLowerCase();
    if (/users|candidates|servers|seed|count|types|k$|sigma|adjust|pareto/.test(normalized)) {
      body.format.numberFormat = "#,##0";
    } else if (/pct/.test(normalized)) {
      body.format.numberFormat = "0.00";
    } else if (/lng|lat|distance|width|height|area|density|entropy|nnmean/.test(normalized)) {
      body.format.numberFormat = "0.0000";
    } else if (/cost/.test(normalized)) {
      body.format.numberFormat = "#,##0.0000";
    } else if (/hv|igd|spacing|bestq|bestfrontq|norm/.test(normalized)) {
      body.format.numberFormat = "0.0000";
    } else if (/mean|std|advantage/.test(normalized)) {
      body.format.numberFormat = "0.0000";
    }
  });
}


async function addDataSheet(workbook, name, filename, tableName) {
  const text = await fs.readFile(path.join(CSV_DIR, filename), "utf8");
  const rows = coerceRows(parseCsv(text));
  const sheet = workbook.worksheets.add(name);
  const lastCol = columnName(rows[0].length - 1);
  const rangeAddress = `A1:${lastCol}${rows.length}`;
  sheet.getRange(rangeAddress).values = rows;
  sheet.showGridLines = false;
  sheet.freezePanes.freezeRows(1);
  styleHeader(sheet.getRange(`A1:${lastCol}1`));
  sheet.getRange(`A2:${lastCol}${rows.length}`).format = {
    font: { color: COLORS.ink, size: 9 },
    verticalAlignment: "center",
    borders: { insideHorizontal: { style: "thin", color: "#E6EBF0" } },
  };
  sheet.getRange(rangeAddress).format.columnWidth = 13;
  applyColumnFormats(sheet, rows[0], rows.length);
  const table = sheet.tables.add(rangeAddress, true, tableName);
  table.style = "TableStyleMedium2";

  rows[0].forEach((header, index) => {
    const letter = columnName(index);
    const normalized = String(header).toLowerCase();
    if (/config/.test(normalized)) sheet.getRange(`${letter}:${letter}`).format.columnWidth = 58;
    if (/datafile|sourcefile/.test(normalized)) {
      sheet.getRange(`${letter}:${letter}`).format.columnWidth = 68;
      sheet.getRange(`${letter}2:${letter}${rows.length}`).format.wrapText = true;
    }
    if (/selectedsolution/.test(normalized)) {
      sheet.getRange(`${letter}:${letter}`).format.columnWidth = 34;
      sheet.getRange(`${letter}2:${letter}${rows.length}`).format.wrapText = true;
    }
    if (/dataset|sourcetype/.test(normalized)) sheet.getRange(`${letter}:${letter}`).format.columnWidth = 30;
    if (/scenario|method/.test(normalized)) sheet.getRange(`${letter}:${letter}`).format.columnWidth = 14;
  });
  return { sheet, rows, rangeAddress };
}


function buildOverview(workbook) {
  const sheet = workbook.worksheets.getItem("Overview");
  sheet.showGridLines = false;
  sheet.getRange("A1:N1").merge();
  sheet.getRange("A1").values = [["Reviewer 2 Comment 6: Geographical Generalization Evidence"]];
  sheet.getRange("A1:N1").format = {
    fill: COLORS.navy,
    font: { bold: true, color: COLORS.white, size: 17 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
  sheet.getRange("A1:N1").format.rowHeight = 36;
  sheet.getRange("A2:N2").merge();
  sheet.getRange("A2").values = [["Real Beijing base-station topology; reproducible sparse, clustered, and skewed traffic profiles; Stage I and Stage II evaluated end to end."]];
  sheet.getRange("A2:N2").format = {
    fill: COLORS.paleBlue,
    font: { color: COLORS.muted, italic: true, size: 10 },
    verticalAlignment: "center",
  };
  sheet.getRange("A2:N2").format.rowHeight = 26;

  sheet.getRange("A4:B4").values = [["Evidence item", "Value"]];
  styleHeader(sheet.getRange("A4:B4"));
  sheet.getRange("A5:A10").values = [
    ["Alternate-region center shift (km)"],
    ["Expanded area scale, minimum (x)"],
    ["Expanded area scale, maximum (x)"],
    ["Expanded Stage I CLS gain, minimum (%)"],
    ["Expanded Stage I CLS gain, maximum (%)"],
    ["Seeds per Stage II scenario"],
  ];
  sheet.getRange("B5:B10").formulas = [
    ["='Design'!H3"],
    ["=MIN('Design'!N4:N6)"],
    ["=MAX('Design'!N4:N6)"],
    ["=MIN('Stage I'!S2:S4)"],
    ["=MAX('Stage I'!S2:S4)"],
    ["='Wide Aggregate'!C2"],
  ];
  sheet.getRange("B5:B9").format.numberFormat = "0.00";
  sheet.getRange("B10").format.numberFormat = "#,##0";
  sheet.getRange("A5:B10").format = {
    font: { color: COLORS.ink, size: 10 },
    borders: { insideHorizontal: { style: "thin", color: COLORS.line } },
    verticalAlignment: "center",
  };
  sheet.getRange("B5:B10").format.fill = "#F8FAFC";
  sheet.getRange("B5:B10").format.font = { bold: true, color: COLORS.navy };

  sheet.getRange("C4:F4").merge();
  sheet.getRange("C4").values = [["Recommended use in the revision"]];
  styleHeader(sheet.getRange("C4:F4"));
  const notes = [
    "Main paper: use the alternate real region, where PSP has the best mean HV, IGD, and Best Q across three seeds.",
    "Response or supplement: use the expanded-region stress test to demonstrate end-to-end portability and expose distribution-dependent Stage II behavior.",
    "Evidence boundary: base-station coordinates are real; sparse, clustered, and skewed user traffic profiles are reproducibly generated.",
    "Claim boundary: the experiment supports geographical applicability, not universal superiority of PSP under every traffic distribution.",
  ];
  notes.forEach((note, index) => {
    const row = 5 + index;
    sheet.getRange(`C${row}:F${row}`).merge();
    sheet.getRange(`C${row}`).values = [[note]];
    sheet.getRange(`C${row}:F${row}`).format = {
      fill: index === 3 ? COLORS.paleRed : COLORS.paleGray,
      font: { color: COLORS.ink, size: 9 },
      wrapText: true,
      verticalAlignment: "center",
      borders: { bottom: { style: "thin", color: COLORS.line } },
    };
    sheet.getRange(`C${row}:F${row}`).format.rowHeight = 42;
  });

  sheet.getRange("A13:B13").values = [["Traffic profile", "CLS gain (%)"]];
  styleHeader(sheet.getRange("A13:B13"));
  for (let index = 0; index < 3; index += 1) {
    const targetRow = 14 + index;
    const sourceRow = 2 + index;
    sheet.getRange(`A${targetRow}:B${targetRow}`).formulas = [[
      `='Stage I'!B${sourceRow}`,
      `='Stage I'!S${sourceRow}`,
    ]];
  }
  sheet.getRange("B14:B16").format.numberFormat = "0.0";

  sheet.getRange("A20:E20").values = [["Method", "HV mean", "IGD mean", "Best Q mean", "Seeds"]];
  styleHeader(sheet.getRange("A20:E20"));
  for (let index = 0; index < 4; index += 1) {
    const targetRow = 21 + index;
    const sourceRow = 2 + index;
    sheet.getRange(`A${targetRow}:E${targetRow}`).formulas = [[
      `='Main Aggregate'!B${sourceRow}`,
      `='Main Aggregate'!D${sourceRow}`,
      `='Main Aggregate'!F${sourceRow}`,
      `='Main Aggregate'!H${sourceRow}`,
      `='Main Aggregate'!C${sourceRow}`,
    ]];
  }
  sheet.getRange("B21:D24").format.numberFormat = "0.0000";
  sheet.getRange("E21:E24").format.numberFormat = "#,##0";
  sheet.getRange("A21:E24").format = {
    font: { color: COLORS.ink, size: 10 },
    borders: { insideHorizontal: { style: "thin", color: COLORS.line } },
  };
  sheet.getRange("A24:E24").format = {
    fill: COLORS.paleRed,
    font: { bold: true, color: "#8E111B", size: 10 },
    borders: { top: { style: "thin", color: COLORS.red } },
  };

  sheet.getRange("A27:F27").merge();
  sheet.getRange("A27").values = [["Metric directions and interpretation"]];
  styleHeader(sheet.getRange("A27:F27"));
  sheet.getRange("A28:F31").values = [
    ["HV: higher is better; it measures the objective-space volume dominated by the obtained Pareto set.", null, null, null, null, null],
    ["IGD: lower is better; it measures the average distance from a common reference front to the obtained Pareto set.", null, null, null, null, null],
    ["Best Q: lower is better; Q is the equal-weight normalized cost-delay scalar used only as a representative compromise indicator.", null, null, null, null, null],
    ["All Stage II aggregates report mean and sample standard deviation over seeds 42, 43, and 44.", null, null, null, null, null],
  ];
  for (let row = 28; row <= 31; row += 1) {
    sheet.getRange(`A${row}:F${row}`).merge();
    sheet.getRange(`A${row}:F${row}`).format = {
      fill: row % 2 === 0 ? "#FFFFFF" : COLORS.paleGray,
      font: { color: COLORS.ink, size: 9 },
      wrapText: true,
      verticalAlignment: "center",
      borders: { bottom: { style: "thin", color: "#E6EBF0" } },
    };
    sheet.getRange(`A${row}:F${row}`).format.rowHeight = 30;
  }

  sheet.getRange("A:A").format.columnWidth = 34;
  sheet.getRange("B:B").format.columnWidth = 16;
  sheet.getRange("C:F").format.columnWidth = 16;
  sheet.getRange("G:N").format.columnWidth = 12;

  const stageChart = sheet.charts.add("bar", sheet.getRange("A13:B16"));
  stageChart.title = "Expanded region: Stage I CLS improvement (%)";
  stageChart.titleTextStyle.fontSize = 12;
  stageChart.hasLegend = false;
  stageChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
  stageChart.yAxis = { numberFormatCode: "0.0", min: 0 };
  stageChart.setPosition("G4", "N17");

  const hvChart = sheet.charts.add("bar", sheet.getRange("A20:B24"));
  hvChart.title = "Alternate region: mean hypervolume (3 seeds)";
  hvChart.titleTextStyle.fontSize = 12;
  hvChart.hasLegend = false;
  hvChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
  hvChart.yAxis = { numberFormatCode: "0.00", min: 0 };
  hvChart.setPosition("G19", "N32");
  return sheet;
}


async function main() {
  await fs.mkdir(path.dirname(OUTPUT_PATH), { recursive: true });
  await fs.mkdir(PREVIEW_DIR, { recursive: true });

  const workbook = Workbook.create();
  workbook.worksheets.add("Overview");
  const loaded = [];
  for (const [name, filename, tableName] of SOURCES) {
    loaded.push(await addDataSheet(workbook, name, filename, tableName));
  }
  const overview = buildOverview(workbook);

  const overviewCheck = await workbook.inspect({
    kind: "table",
    range: "Overview!A1:N31",
    include: "values,formulas",
    tableMaxRows: 31,
    tableMaxCols: 14,
    maxChars: 7000,
  });
  console.log("OVERVIEW_INSPECT");
  console.log(overviewCheck.ndjson);

  const errorScan = await workbook.inspect({
    kind: "match",
    searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
    options: { useRegex: true, maxResults: 300 },
    summary: "Reviewer 6 workbook formula error scan",
  });
  console.log("FORMULA_ERROR_SCAN");
  console.log(errorScan.ndjson);

  const renderRanges = new Map([
    ["Overview", "A1:N32"],
    ["Design", "A1:U6"],
    ["Stage I", "A1:T4"],
    ["Wide Aggregate", "A1:I13"],
    ["Wide Detail", "A1:M37"],
    ["Main Aggregate", "A1:I5"],
    ["Main Detail", "A1:M13"],
  ]);
  for (const [sheetName, range] of renderRanges.entries()) {
    const preview = await workbook.render({ sheetName, range, scale: 1.2, format: "png" });
    const filename = `${sheetName.toLowerCase().replaceAll(" ", "_")}.png`;
    await fs.writeFile(path.join(PREVIEW_DIR, filename), new Uint8Array(await preview.arrayBuffer()));
  }

  const output = await SpreadsheetFile.exportXlsx(workbook);
  await output.save(OUTPUT_PATH);
  console.log(`SAVED ${OUTPUT_PATH}`);
  console.log(`PREVIEWS ${PREVIEW_DIR}`);
  console.log(`SHEETS ${loaded.length + 1}`);
}


await main();
