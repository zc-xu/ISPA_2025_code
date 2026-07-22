import fs from "node:fs/promises";
import path from "node:path";

import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";


const ROOT = path.resolve(process.cwd());
const CSV_DIR = path.join(ROOT, "output", "csv");
const OUTPUT_PATH = path.join(ROOT, "output", "excel", "reviewer6_generalization_evidence.xlsx");
const PREVIEW_DIR = path.join(ROOT, "output", "workbook_preview", "reviewer6_generalization_main");

const SOURCES = [
  ["Design", "reviewer6_generalization_design.csv", "DesignTable"],
  ["Stage I", "reviewer6_main_candidate_stage1.csv", "StageITable"],
  ["Stage II Aggregate", "reviewer6_main_candidate_stage2_aggregate.csv", "StageIIAggregateTable"],
  ["Stage II Seeds", "reviewer6_main_candidate_stage2_detail.csv", "StageIISeedTable"],
  ["DQN Weighted", "reviewer6_main_candidate_dqn_weighted.csv", "DQNWeightedTable"],
  ["BestQ Seeds", "reviewer6_main_candidate_bestq_detail.csv", "BestQSeedTable"],
  ["BestQ Aggregate", "reviewer6_main_candidate_bestq_aggregate.csv", "BestQAggregateTable"],
];

const COLORS = {
  navy: "#1F4E78",
  blue: "#4C78A8",
  green: "#59A14F",
  orange: "#F28E2B",
  purple: "#9467BD",
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
  sheet.getRange("A1").values = [["Reviewer Comment 6: Geographical Generalization Evidence"]];
  sheet.getRange("A1:N1").format = {
    fill: COLORS.navy,
    font: { bold: true, color: COLORS.white, size: 17 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
  sheet.getRange("A1:N1").format.rowHeight = 36;
  sheet.getRange("A2:N2").merge();
  sheet.getRange("A2").values = [["A geographically distinct real-station instance evaluated end to end with Stage I, Stage II, and the DQN learning baseline."]];
  sheet.getRange("A2:N2").format = {
    fill: COLORS.paleBlue,
    font: { color: COLORS.muted, italic: true, size: 10 },
    verticalAlignment: "center",
  };
  sheet.getRange("A2:N2").format.rowHeight = 26;

  sheet.getRange("A4:B4").values = [["Evidence item", "Value"]];
  styleHeader(sheet.getRange("A4:B4"));
  sheet.getRange("A5:A10").values = [
    ["New-region centroid shift (km)"],
    ["Candidate stations in new instance"],
    ["Candidate-station scale vs. original (x)"],
    ["New-region coverage-density CV"],
    ["Stage I CLS objective reduction (%)"],
    ["Stage II random seeds"],
  ];
  sheet.getRange("B5:B10").formulas = [
    ["='Design'!H3"],
    ["='Design'!C3"],
    ["='Design'!C3/'Design'!C2"],
    ["='Design'!R3"],
    ["='Stage I'!R2"],
    ["='Stage II Aggregate'!C2"],
  ];
  sheet.getRange("B5").format.numberFormat = "0.00";
  sheet.getRange("B6").format.numberFormat = "#,##0";
  sheet.getRange("B7:B9").format.numberFormat = "0.0000";
  sheet.getRange("B10").format.numberFormat = "#,##0";
  sheet.getRange("A5:B10").format = {
    font: { color: COLORS.ink, size: 10 },
    borders: { insideHorizontal: { style: "thin", color: COLORS.line } },
    verticalAlignment: "center",
  };
  sheet.getRange("B5:B10").format.fill = "#F8FAFC";
  sheet.getRange("B5:B10").format.font = { bold: true, color: COLORS.navy };

  sheet.getRange("C4:F4").merge();
  sheet.getRange("C4").values = [["Verified conclusion"]];
  styleHeader(sheet.getRange("C4:F4"));
  const notes = [
    "The new real-station topology is 24.20 km from the original Xizhimen centroid and doubles the candidate count from 20 to 40.",
    "CLS reduces the best recorded non-CLS Stage I objective from 6,150.5741 to 2,304.7670, a reduction of 62.53%.",
    "Across seeds 42, 43, and 44, PSP has the best mean HV, IGD, and Best Q among the four population methods.",
    "Under the common equal-weight evaluation, PSP Best Q is 0.2678 and DQN Best Q is 0.5517.",
  ];
  notes.forEach((note, index) => {
    const row = 5 + index;
    sheet.getRange(`C${row}:F${row}`).merge();
    sheet.getRange(`C${row}`).values = [[note]];
    sheet.getRange(`C${row}:F${row}`).format = {
      fill: index === 3 ? "#F2EAFE" : COLORS.paleGray,
      font: { color: COLORS.ink, size: 9 },
      wrapText: true,
      verticalAlignment: "center",
      borders: { bottom: { style: "thin", color: COLORS.line } },
    };
    sheet.getRange(`C${row}:F${row}`).format.rowHeight = 42;
  });

  sheet.getRange("G4:I4").values = [["Instance", "Best non-CLS", "CLS"]];
  styleHeader(sheet.getRange("G4:I4"));
  sheet.getRange("G5:I5").formulas = [[
    "=\"New region\"",
    "='Stage I'!Q2",
    "='Stage I'!J2",
  ]];
  sheet.getRange("H5:I5").format.numberFormat = "#,##0.0";

  sheet.getRange("A13:H13").values = [["Method", "HV mean", "HV std", "IGD mean", "IGD std", "Best Q mean", "Best Q std", "Seeds"]];
  styleHeader(sheet.getRange("A13:H13"));
  for (let index = 0; index < 4; index += 1) {
    const targetRow = 14 + index;
    const sourceRow = 2 + index;
    sheet.getRange(`A${targetRow}:H${targetRow}`).formulas = [[
      `='Stage II Aggregate'!B${sourceRow}`,
      `='Stage II Aggregate'!D${sourceRow}`,
      `='Stage II Aggregate'!E${sourceRow}`,
      `='Stage II Aggregate'!F${sourceRow}`,
      `='Stage II Aggregate'!G${sourceRow}`,
      `='Stage II Aggregate'!H${sourceRow}`,
      `='Stage II Aggregate'!I${sourceRow}`,
      `='Stage II Aggregate'!C${sourceRow}`,
    ]];
  }
  sheet.getRange("B14:G17").format.numberFormat = "0.0000";
  sheet.getRange("H14:H17").format.numberFormat = "#,##0";
  sheet.getRange("A14:H17").format = {
    font: { color: COLORS.ink, size: 10 },
    borders: { insideHorizontal: { style: "thin", color: COLORS.line } },
  };
  sheet.getRange("A17:H17").format = {
    fill: COLORS.paleRed,
    font: { bold: true, color: "#8E111B", size: 10 },
    borders: { top: { style: "thin", color: COLORS.red } },
  };

  sheet.getRange("A20:D20").values = [["Method", "Best Q mean", "Best Q std", "Seeds"]];
  styleHeader(sheet.getRange("A20:D20"));
  for (let index = 0; index < 5; index += 1) {
    const targetRow = 21 + index;
    const sourceRow = 2 + index;
    sheet.getRange(`A${targetRow}:D${targetRow}`).formulas = [[
      `='BestQ Aggregate'!A${sourceRow}`,
      `='BestQ Aggregate'!C${sourceRow}`,
      `='BestQ Aggregate'!D${sourceRow}`,
      `='BestQ Aggregate'!B${sourceRow}`,
    ]];
  }
  sheet.getRange("B21:C25").format.numberFormat = "0.0000";
  sheet.getRange("D21:D25").format.numberFormat = "#,##0";
  sheet.getRange("A21:D25").format = {
    font: { color: COLORS.ink, size: 10 },
    borders: { insideHorizontal: { style: "thin", color: COLORS.line } },
  };
  sheet.getRange("A24:D24").format = {
    fill: COLORS.paleRed,
    font: { bold: true, color: "#8E111B", size: 10 },
  };
  sheet.getRange("A25:D25").format = {
    fill: "#F2EAFE",
    font: { bold: true, color: COLORS.purple, size: 10 },
  };

  sheet.getRange("G20:L20").values = [["Metric", "NS-P", "GCP", "GDP", "PSP", "DQN"]];
  styleHeader(sheet.getRange("G20:L20"));
  sheet.getRange("G21:L21").formulas = [[
    "=\"Best Q\"",
    "='BestQ Aggregate'!C2",
    "='BestQ Aggregate'!C3",
    "='BestQ Aggregate'!C4",
    "='BestQ Aggregate'!C5",
    "='BestQ Aggregate'!C6",
  ]];
  sheet.getRange("H21:L21").format.numberFormat = "0.0000";

  sheet.getRange("A28:F28").merge();
  sheet.getRange("A28").values = [["Metric directions and interpretation"]];
  styleHeader(sheet.getRange("A28:F28"));
  sheet.getRange("A29:F32").values = [
    ["HV: higher is better; it measures the objective-space volume dominated by the obtained Pareto set.", null, null, null, null, null],
    ["IGD: lower is better; it measures the average distance from a common reference front to the obtained Pareto set.", null, null, null, null, null],
    ["Best Q: lower is better; every method uses the same per-seed bounds and Q = 0.5 x normalized cost + 0.5 x normalized delay.", null, null, null, null, null],
    ["All aggregate values report mean and sample standard deviation over seeds 42, 43, and 44.", null, null, null, null, null],
  ];
  for (let row = 29; row <= 32; row += 1) {
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
  sheet.getRange("G:G").format.columnWidth = 18;
  sheet.getRange("H:N").format.columnWidth = 12;

  const stageChart = sheet.charts.add("bar", sheet.getRange("G4:I5"));
  stageChart.title = "Stage I coverage/access objective";
  stageChart.titleTextStyle.fontSize = 12;
  stageChart.hasLegend = true;
  stageChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
  stageChart.yAxis = { numberFormatCode: "#,##0", min: 0 };
  stageChart.setPosition("I7", "N18");
  const stageSeries = stageChart.series.items;
  if (stageSeries[0]) stageSeries[0].fill = COLORS.muted;
  if (stageSeries[1]) stageSeries[1].fill = COLORS.red;

  const bestQChart = sheet.charts.add("bar", sheet.getRange("G20:L21"));
  bestQChart.title = "Stage II mean Best Q (lower is better)";
  bestQChart.titleTextStyle.fontSize = 12;
  bestQChart.hasLegend = true;
  bestQChart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
  bestQChart.yAxis = { numberFormatCode: "0.00", min: 0 };
  bestQChart.setPosition("G23", "N36");
  const bestQColors = [COLORS.blue, COLORS.green, COLORS.orange, COLORS.red, COLORS.purple];
  bestQChart.series.items.forEach((series, index) => {
    if (bestQColors[index]) series.fill = bestQColors[index];
  });
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
    range: "Overview!A1:N36",
    include: "values,formulas",
    tableMaxRows: 36,
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
    ["Overview", "A1:N36"],
    ["Design", "A1:U3"],
    ["Stage I", "A1:S2"],
    ["Stage II Aggregate", "A1:I5"],
    ["Stage II Seeds", "A1:G13"],
    ["DQN Weighted", "A1:M16"],
    ["BestQ Seeds", "A1:C16"],
    ["BestQ Aggregate", "A1:D6"],
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
