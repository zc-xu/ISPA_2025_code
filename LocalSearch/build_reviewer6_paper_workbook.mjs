import fs from "node:fs/promises";
import path from "node:path";

import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";


const ROOT = path.resolve(process.cwd());
const TEMPLATE_PATH = "C:/Users/m1870/Desktop/ISPA_2025_9月材料/change_color_小论文实验二-user.xlsx";
const CSV_DIR = path.join(ROOT, "output", "csv");
const OUTPUT_PATH = path.join(ROOT, "output", "excel", "reviewer6_generalization_paper_style.xlsx");
const PREVIEW_DIR = path.join(ROOT, "output", "workbook_preview", "reviewer6_paper_final");
const METHODS = ["NS-P", "PSP", "GCP", "GDP", "DQN"];
const SEEDS = [42, 43, 44];
const COLORS = {
  navy: "#1F4E78",
  blue: "#1683D8",
  red: "#FF1F1F",
  green: "#21B95B",
  gold: "#C99500",
  purple: "#9467BD",
  ink: "#202020",
  muted: "#5B6573",
  light: "#F4F6F8",
  line: "#D5D9DE",
  white: "#FFFFFF",
};


function parseCsv(text) {
  const rows = [];
  let row = [];
  let value = "";
  let quoted = false;
  for (let index = 0; index < text.length; index += 1) {
    const char = text[index];
    if (quoted) {
      if (char === '"' && text[index + 1] === '"') {
        value += '"';
        index += 1;
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
  if (row.length > 0 || value.length > 0) {
    row.push(value.replace(/\r$/, ""));
    rows.push(row);
  }
  return rows.filter((record) => record.some((cell) => cell !== ""));
}


function toObjects(rows) {
  const headers = rows[0];
  return rows.slice(1).map((row) => Object.fromEntries(headers.map((header, index) => [header, row[index] ?? ""])));
}


async function readCsv(filename) {
  const text = await fs.readFile(path.join(CSV_DIR, filename), "utf8");
  return toObjects(parseCsv(text));
}


function asNumber(value) {
  const number = Number(value);
  if (!Number.isFinite(number)) throw new Error(`Expected a finite number, received ${value}.`);
  return number;
}


function valueBy(frame, method, seed, field) {
  const row = frame.find((item) => item.Method === method && Number(item.Seed) === seed);
  if (!row) return null;
  return row[field] === "" ? null : asNumber(row[field]);
}


function clearTables(sheet) {
  for (const table of [...sheet.tables.items]) table.delete();
}


function styleTitle(sheet, range, text) {
  sheet.getRange(range).merge();
  const cell = sheet.getRange(range.split(":")[0]);
  cell.values = [[text]];
  sheet.getRange(range).format = {
    fill: COLORS.navy,
    font: { bold: true, color: COLORS.white, size: 16 },
    verticalAlignment: "center",
    horizontalAlignment: "left",
  };
  sheet.getRange(range).format.rowHeight = 34;
}


function styleHeader(range) {
  range.format = {
    fill: COLORS.navy,
    font: { bold: true, color: COLORS.white, size: 10 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: COLORS.navy },
  };
  range.format.rowHeight = 28;
}


function styleBody(range) {
  range.format = {
    font: { color: COLORS.ink, size: 10 },
    verticalAlignment: "center",
    borders: {
      insideHorizontal: { style: "thin", color: COLORS.line },
      bottom: { style: "thin", color: COLORS.line },
    },
  };
}


const [stage1Rows, designRows, populationRows, bestQRows] = await Promise.all([
  readCsv("reviewer6_main_candidate_stage1.csv"),
  readCsv("reviewer6_generalization_design.csv"),
  readCsv("reviewer6_main_candidate_stage2_detail.csv"),
  readCsv("reviewer6_main_candidate_bestq_detail.csv"),
]);
const stage1 = stage1Rows[0];
const design = designRows.find((row) => row.Dataset === "Alternate real region");
if (!stage1 || !design) throw new Error("Reviewer-6 source rows are incomplete.");

const source = await FileBlob.load(TEMPLATE_PATH);
const workbook = await SpreadsheetFile.importXlsx(source);
const generalization = workbook.worksheets.getItem("Sheet1 (2)");
const seedResults = workbook.worksheets.getItem("Sheet1");
const figures = workbook.worksheets.getItem("Sheet2");

const templateChart = generalization.charts.items.find((chart) =>
  chart.series.items.some((series) => series.formula.includes("$B$10:$E$10")),
);
if (!templateChart) throw new Error("The reference bar chart was not found in the template.");

let archivedChartIndex = 0;
for (const chart of [...generalization.charts.items]) {
  if (chart !== templateChart && !chart.series.items.some((series) => series.formula.includes("$B$10:$E$10"))) {
    const startRow = 100 + archivedChartIndex * 20;
    chart.setPosition(`AZ${startRow}`, `BH${startRow + 16}`);
    archivedChartIndex += 1;
  }
}
clearTables(generalization);
generalization.getRange("A1:AE60").clear({ applyTo: "all" });
generalization.name = "Generalization";
generalization.showGridLines = false;

seedResults.deleteAllDrawings();
clearTables(seedResults);
seedResults.getRange("A1:AE60").clear({ applyTo: "all" });
seedResults.name = "Seed Results";
seedResults.showGridLines = false;

figures.deleteAllDrawings();
clearTables(figures);
figures.getRange("A1:AE60").clear({ applyTo: "all" });
figures.name = "Figure Files";
figures.showGridLines = false;

styleTitle(seedResults, "A1:P1", "Geographical Generalization: Seed-Level Results");
seedResults.getRange("A2:P2").merge();
seedResults.getRange("A2").values = [["Alternate real-station region; three independent seeds (42, 43, and 44)."]];
seedResults.getRange("A2:P2").format = {
  fill: "#EAF2F8",
  font: { italic: true, color: COLORS.muted, size: 10 },
  verticalAlignment: "center",
};
seedResults.getRange("A3:P3").values = [[
  "Method",
  "Best Q (42)", "Best Q (43)", "Best Q (44)", "Best Q mean", "Best Q SD",
  "HV (42)", "HV (43)", "HV (44)", "HV mean", "HV SD",
  "IGD (42)", "IGD (43)", "IGD (44)", "IGD mean", "IGD SD",
]];
styleHeader(seedResults.getRange("A3:P3"));

METHODS.forEach((method, methodIndex) => {
  const row = 4 + methodIndex;
  const bestQValues = SEEDS.map((seed) => valueBy(bestQRows, method, seed, "BestQ"));
  const hvValues = SEEDS.map((seed) => valueBy(populationRows, method, seed, "HV"));
  const igdValues = SEEDS.map((seed) => valueBy(populationRows, method, seed, "IGD"));
  seedResults.getRange(`A${row}:D${row}`).values = [[method, ...bestQValues]];
  seedResults.getRange(`E${row}`).formulas = [[`=AVERAGE(B${row}:D${row})`]];
  seedResults.getRange(`F${row}`).formulas = [[`=STDEV.S(B${row}:D${row})`]];
  if (method !== "DQN") {
    seedResults.getRange(`G${row}:I${row}`).values = [[...hvValues]];
    seedResults.getRange(`J${row}`).formulas = [[`=AVERAGE(G${row}:I${row})`]];
    seedResults.getRange(`K${row}`).formulas = [[`=STDEV.S(G${row}:I${row})`]];
    seedResults.getRange(`L${row}:N${row}`).values = [[...igdValues]];
    seedResults.getRange(`O${row}`).formulas = [[`=AVERAGE(L${row}:N${row})`]];
    seedResults.getRange(`P${row}`).formulas = [[`=STDEV.S(L${row}:N${row})`]];
  } else {
    seedResults.getRange(`G${row}:P${row}`).values = [[null, null, null, null, null, null, null, null, null, null]];
  }
});
styleBody(seedResults.getRange("A4:P8"));
seedResults.getRange("B4:P8").format.numberFormat = "0.0000";
seedResults.getRange("A4:A8").format.font = { bold: true, color: COLORS.ink };
seedResults.getRange("A3:P8").format.columnWidth = 13;
seedResults.getRange("A:A").format.columnWidth = 12;
seedResults.freezePanes.freezeRows(3);

styleTitle(generalization, "A1:P1", "Geographical Generalization: End-to-End Results");
generalization.getRange("A2:P2").merge();
generalization.getRange("A2").values = [[
  "A geographically distinct real-station instance with 40 candidate stations, 10 deployed servers, 130 users, and eight service types.",
]];
generalization.getRange("A2:P2").format = {
  fill: "#EAF2F8",
  font: { italic: true, color: COLORS.muted, size: 10 },
  verticalAlignment: "center",
};

generalization.getRange("A4:F4").merge();
generalization.getRange("A4").values = [["Stage II common Best Q (lower is better)"]];
generalization.getRange("A4:F4").format = {
  fill: COLORS.light,
  font: { bold: true, color: COLORS.ink, size: 11 },
  horizontalAlignment: "left",
  verticalAlignment: "center",
};
generalization.getRange("A5:A7").values = [["Method"], ["Mean"], ["SD"]];
generalization.getRange("B5:F5").values = [[...METHODS]];
for (let index = 0; index < METHODS.length; index += 1) {
  const sourceRow = 4 + index;
  const column = String.fromCharCode(66 + index);
  generalization.getRange(`${column}6`).formulas = [[`='Seed Results'!E${sourceRow}`]];
  generalization.getRange(`${column}7`).formulas = [[`='Seed Results'!F${sourceRow}`]];
}
styleHeader(generalization.getRange("A5:F5"));
styleBody(generalization.getRange("A6:F7"));
generalization.getRange("B6:F7").format.numberFormat = "0.0000";
generalization.getRange("A4:F7").format.columnWidth = 13;
generalization.getRange("A:A").format.columnWidth = 12;

const series = templateChart.series.items[0];
series.categoryFormula = "'Generalization'!$B$5:$F$5";
series.formula = "'Generalization'!$B$6:$F$6";
series.fill = { type: "solid", color: COLORS.purple };
series.stroke = { color: "#7E57A6", style: "solid", weight: 1.0 };
series.valuesFormatCode = "0.000";
templateChart.setPosition("H3", "P19");
templateChart.yAxis = {
  min: 0.20,
  max: 0.70,
  majorUnit: 0.10,
  numberFormatCode: "0.0",
};

generalization.getRange("A10:F10").values = [["Metric", ...METHODS]];
styleHeader(generalization.getRange("A10:F10"));
generalization.getRange("A11:A16").values = [
  ["Best Q mean"],
  ["Best Q SD"],
  ["HV mean"],
  ["HV SD"],
  ["IGD mean"],
  ["IGD SD"],
];
METHODS.forEach((method, index) => {
  const sourceRow = 4 + index;
  const column = String.fromCharCode(66 + index);
  generalization.getRange(`${column}11:${column}12`).formulas = [[
    `='Seed Results'!E${sourceRow}`,
  ], [
    `='Seed Results'!F${sourceRow}`,
  ]];
  if (method !== "DQN") {
    generalization.getRange(`${column}13:${column}16`).formulas = [[
      `='Seed Results'!J${sourceRow}`,
    ], [
      `='Seed Results'!K${sourceRow}`,
    ], [
      `='Seed Results'!O${sourceRow}`,
    ], [
      `='Seed Results'!P${sourceRow}`,
    ]];
  } else {
    generalization.getRange(`${column}13:${column}16`).values = [["N/A"], ["N/A"], ["N/A"], ["N/A"]];
  }
});
styleBody(generalization.getRange("A11:F16"));
generalization.getRange("B11:F16").format.numberFormat = "0.0000";
generalization.getRange("A11:A16").format.font = { bold: true, color: COLORS.ink };
generalization.getRange("C11:C16").format.fill = "#FFF1F1";
generalization.getRange("F11:F16").format.fill = "#F4EEFA";
generalization.getRange("A10:F16").format.columnWidth = 13;
generalization.getRange("A:A").format.columnWidth = 25;

generalization.getRange("A20:B20").values = [["Stage I evidence", "Value"]];
styleHeader(generalization.getRange("A20:B20"));
generalization.getRange("A21:A27").values = [
  ["Candidate stations"],
  ["Deployed servers"],
  ["Users"],
  ["Centroid shift (km)"],
  ["CLS objective"],
  ["Best non-CLS objective"],
  ["CLS reduction"],
];
generalization.getRange("B21:B26").values = [[
  asNumber(design.Candidates),
], [
  asNumber(design.SelectedServers),
], [
  asNumber(design.Users),
], [
  asNumber(design.CenterDistanceFromOriginalKm),
], [
  asNumber(stage1.CLSCost),
], [
  asNumber(stage1.BestBaselineCost),
]];
generalization.getRange("B27").formulas = [["=(B26-B25)/B26"]];
styleBody(generalization.getRange("A21:B27"));
generalization.getRange("B21:B23").format.numberFormat = "#,##0";
generalization.getRange("B24").format.numberFormat = "0.00";
generalization.getRange("B25:B26").format.numberFormat = "#,##0.0000";
generalization.getRange("B27").format.numberFormat = "0.00%";
generalization.getRange("B:B").format.columnWidth = 15;

generalization.getRange("D20:P22").merge();
generalization.getRange("D20").values = [[
  "HV (higher is better) and IGD (lower is better) are reported for the four 50-solution population methods. DQN is compared through the common equal-weight Best Q because it yields five scalarized policy solutions per seed.",
]];
generalization.getRange("D20:P22").format = {
  fill: COLORS.light,
  font: { color: COLORS.muted, size: 9 },
  wrapText: true,
  verticalAlignment: "center",
};
generalization.getRange("D20:P22").format.rowHeight = 24;
generalization.getRange("A29:P29").merge();
generalization.getRange("A29").values = [[
  `Input: ${stage1.DataFile} | Stage-I selection: ${stage1.SelectedSolution} | Stage-II seeds: ${SEEDS.join(", ")}`,
]];
generalization.getRange("A29:P29").format = {
  font: { color: COLORS.muted, italic: true, size: 8 },
  wrapText: true,
};

styleTitle(figures, "A1:F1", "Publication Figure Files");
figures.getRange("A2:F2").merge();
figures.getRange("A2").values = [[
  "The topology figure uses the Stage-I deployment and service-aware user distribution; the performance figure reports mean +/- SD over seeds 42, 43, and 44.",
]];
figures.getRange("A2:F2").format = {
  fill: "#EAF2F8",
  font: { italic: true, color: COLORS.muted, size: 10 },
  verticalAlignment: "center",
};
figures.getRange("A4:F4").values = [["Figure", "PNG", "PDF", "Contents", "Statistical basis", "Use"]];
styleHeader(figures.getRange("A4:F4"));
figures.getRange("A5:F6").values = [[
  "Geographical topology",
  "output/png/reviewer6_generalization_topology.png",
  "output/pdf/reviewer6_generalization_topology.pdf",
  "Users, eight service types, candidates, CLS-selected servers, coverage circles, and assignments",
  "Stage-I result for real_sparse_r04_c40_u130_k10_s1",
  "Manuscript/response figure",
], [
  "Stage-II Best Q",
  "output/png/reviewer6_generalization_bestq.png",
  "output/pdf/reviewer6_generalization_bestq.pdf",
  "NS-P, PSP, GCP, GDP, and DQN with paper-consistent colors and patterns",
  "Mean +/- SD over seeds 42, 43, and 44",
  "Manuscript/response figure",
]];
styleBody(figures.getRange("A5:F6"));
figures.getRange("A5:F6").format.wrapText = true;
figures.getRange("A:A").format.columnWidth = 24;
figures.getRange("B:C").format.columnWidth = 52;
figures.getRange("D:D").format.columnWidth = 62;
figures.getRange("E:E").format.columnWidth = 40;
figures.getRange("F:F").format.columnWidth = 28;
figures.getRange("A5:F6").format.rowHeight = 52;

await fs.mkdir(path.dirname(OUTPUT_PATH), { recursive: true });
await fs.mkdir(PREVIEW_DIR, { recursive: true });

const keyInspection = await workbook.inspect({
  kind: "table",
  range: "Generalization!A1:P29",
  include: "values,formulas",
  tableMaxRows: 31,
  tableMaxCols: 16,
  maxChars: 12000,
});
console.log(keyInspection.ndjson);

const errorInspection = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 200 },
  summary: "final formula error scan",
  maxChars: 6000,
});
console.log(errorInspection.ndjson);

const previews = [
  ["Generalization", "A1:P30", 1.10],
  ["Seed Results", "A1:P9", 1.15],
  ["Figure Files", "A1:F7", 1.05],
];
for (const [sheetName, range, scale] of previews) {
  const preview = await workbook.render({ sheetName, range, scale, format: "png" });
  await fs.writeFile(
    path.join(PREVIEW_DIR, `${sheetName.replace(/\s+/g, "_")}.png`),
    new Uint8Array(await preview.arrayBuffer()),
  );
}

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(OUTPUT_PATH);
console.log(JSON.stringify({ output: OUTPUT_PATH, previews: PREVIEW_DIR }, null, 2));
