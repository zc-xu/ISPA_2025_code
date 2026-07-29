import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "D:/EdgeComputing_journal/outputs/revision_package/spreadsheets";
const previewDir = "D:/EdgeComputing_journal/tmp/spreadsheet_stage2_final/previews";
const outputPath = path.join(outputDir, "stage2_five_method_results_editable.xlsx");

const methods = ["NS-P", "PSP", "GCP", "GDP", "DQN"];
const colors = {
  "NS-P": "#64B5F6",
  PSP: "#FF5A5F",
  GCP: "#39B96B",
  GDP: "#F2B84B",
  DQN: "#9B72CF",
};

const fixedServers = [
  ["10 servers / 100 users", 0.2975, 0.2686, 0.2996, 0.2748, 0.5770307911],
  ["10 servers / 130 users", 0.3894, 0.3282, 0.3550, 0.3363, 0.6125035722],
  ["10 servers / 150 users", 0.3023, 0.2749, 0.2868, 0.2847, 0.4971969240],
  ["10 servers / 180 users", 0.2976, 0.2774, 0.2955, 0.2896, 0.4840131472],
];

const fixedUsers = [
  ["5 servers / 130 users", 0.2150, 0.1945, 0.2304, 0.2393, 0.4051715848],
  ["10 servers / 130 users", 0.3894, 0.3282, 0.3550, 0.3363, 0.6125035722],
  ["15 servers / 130 users", 0.3072, 0.2646, 0.2729, 0.2980, 0.6077332731],
  ["20 servers / 130 users", 0.3196, 0.2864, 0.2980, 0.3049, 0.7077210813],
];

const axisBoundsFixedServers = [
  [0.20, 0.62],
  [0.30, 0.65],
  [0.25, 0.53],
  [0.25, 0.52],
];

const axisBoundsFixedUsers = [
  [0.18, 0.43],
  [0.30, 0.65],
  [0.25, 0.65],
  [0.27, 0.73],
];

function styleTitle(sheet, rangeAddress, text) {
  const range = sheet.getRange(rangeAddress);
  range.merge();
  range.values = [[text]];
  range.format = {
    fill: "#1F4E78",
    font: { bold: true, color: "#FFFFFF", size: 16 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  range.format.rowHeight = 28;
}

function styleMethodHeader(sheet, rangeAddress) {
  const header = sheet.getRange(rangeAddress);
  header.format = {
    font: { bold: true, color: "#FFFFFF" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "outside", style: "thin", color: "#A6A6A6" },
  };
  methods.forEach((method, index) => {
    const cell = sheet.getCell(2, index + 1);
    cell.format.fill = colors[method];
    if (method === "GDP") cell.format.font = { bold: true, color: "#1F1F1F" };
  });
}

function addExperimentSheet(workbook, name, title, rows, axisBounds) {
  const sheet = workbook.worksheets.add(name);
  sheet.showGridLines = false;
  sheet.freezePanes.freezeRows(3);
  styleTitle(sheet, "A1:F1", title);

  sheet.getRange("A3:F7").values = [
    ["Configuration", ...methods],
    ...rows,
  ];
  styleMethodHeader(sheet, "A3:F3");
  sheet.getRange("A4:A7").format = {
    fill: "#EAF2F8",
    font: { bold: true, color: "#1F1F1F" },
    horizontalAlignment: "left",
  };
  sheet.getRange("B4:F7").format = {
    numberFormat: "0.0000",
    horizontalAlignment: "center",
    borders: {
      insideHorizontal: { style: "thin", color: "#D9E2F3" },
      insideVertical: { style: "thin", color: "#D9E2F3" },
      bottom: { style: "thin", color: "#A6A6A6" },
    },
  };
  sheet.getRange("A3:F7").format.borders = {
    outside: { style: "thin", color: "#7F8C8D" },
    insideHorizontal: { style: "thin", color: "#D9E2F3" },
    insideVertical: { style: "thin", color: "#D9E2F3" },
  };
  sheet.getRange("A:A").format.columnWidth = 25;
  sheet.getRange("B:F").format.columnWidth = 12;

  rows.forEach((row, index) => {
    const sourceRow = index + 4;
    const chart = sheet.charts.add("bar", {
      chartType: "bar",
      title: row[0],
      hasLegend: true,
    });
    chart.title = row[0];
    chart.titleTextStyle.fontSize = 11;
    chart.hasLegend = true;
    chart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 9 } };
    chart.yAxis = {
      numberFormatCode: "0.00",
      min: axisBounds[index][0],
      max: axisBounds[index][1],
      textStyle: { fontSize: 9 },
    };
    methods.forEach((method, seriesIndex) => {
      const series = chart.series.add(method);
      const valueColumn = String.fromCharCode("B".charCodeAt(0) + seriesIndex);
      series.categoryFormula = `'${name}'!$A$${sourceRow}`;
      series.formula = `'${name}'!$${valueColumn}$${sourceRow}`;
      series.fill = colors[method];
    });

    const topRow = index < 2 ? 9 : 28;
    const leftCol = index % 2 === 0 ? "A" : "J";
    const rightCol = index % 2 === 0 ? "H" : "Q";
    chart.setPosition(`${leftCol}${topRow}`, `${rightCol}${topRow + 17}`);
  });

  sheet.getRange("A52:F54").values = [
    ["Figure note", null, null, null, null, null],
    ["The editable charts use the same five-method values as the manuscript figures.", null, null, null, null, null],
    ["No uncertainty bars are shown because the archived values do not contain per-method repeated-run distributions.", null, null, null, null, null],
  ];
  sheet.getRange("A52:F52").merge();
  sheet.getRange("A53:F53").merge();
  sheet.getRange("A54:F54").merge();
  sheet.getRange("A52:F52").format = { fill: "#D9EAF7", font: { bold: true, color: "#1F4E78" } };
  sheet.getRange("A53:F54").format = { fill: "#F7F9FB", font: { color: "#4F4F4F" }, wrapText: true };
  sheet.getRange("A52:F54").format.borders = { preset: "outside", style: "thin", color: "#B4C6E7" };
  return sheet;
}

const workbook = Workbook.create();
const readme = workbook.worksheets.add("README");
readme.showGridLines = false;
styleTitle(readme, "A1:F1", "Stage-II Five-Method Experiment Workbook");
readme.getRange("A3:B9").values = [
  ["Item", "Description"],
  ["Metric", "Best Q (normalized); lower is better"],
  ["Methods", "NS-P, PSP, GCP, GDP, and DQN"],
  ["Fixed Servers", "10 deployed servers; users = 100, 130, 150, 180"],
  ["Fixed Users", "130 users; deployed servers = 5, 10, 15, 20"],
  ["Uncertainty bars", "Not shown because the archived comparison values do not include independent repeated-run distributions for every method"],
  ["Source", "Original paper Excel values for NS-P/PSP/GCP/GDP; seed-42 DQN outputs normalized with the corresponding paper bounds"],
];
readme.getRange("A3:B3").format = { fill: "#D9EAF7", font: { bold: true, color: "#1F4E78" } };
readme.getRange("A4:A9").format = { font: { bold: true }, fill: "#F2F6FA" };
readme.getRange("A3:B9").format.borders = {
  outside: { style: "thin", color: "#A6A6A6" },
  insideHorizontal: { style: "thin", color: "#D9E2F3" },
};
readme.getRange("A:A").format.columnWidth = 22;
readme.getRange("B:B").format.columnWidth = 78;
readme.getRange("B4:B9").format.wrapText = true;

addExperimentSheet(
  workbook,
  "Fixed Servers",
  "Stage-II Best Q: 10 Servers with Increasing Users",
  fixedServers,
  axisBoundsFixedServers,
);
addExperimentSheet(
  workbook,
  "Fixed Users",
  "Stage-II Best Q: 130 Users with Increasing Servers",
  fixedUsers,
  axisBoundsFixedUsers,
);

const validation = workbook.worksheets.add("Validation");
validation.showGridLines = false;
styleTitle(validation, "A1:F1", "Result Validation");
validation.getRange("A3:F10").values = [
  ["Configuration", "PSP Q", "Best non-PSP evolutionary Q", "DQN Q", "PSP reduction", "PSP is lowest"],
  ["10_100", null, null, null, null, null],
  ["10_130", null, null, null, null, null],
  ["10_150", null, null, null, null, null],
  ["10_180", null, null, null, null, null],
  ["5_130", null, null, null, null, null],
  ["15_130", null, null, null, null, null],
  ["20_130", null, null, null, null, null],
];
validation.getRange("B4:F10").formulas = [
  ["='Fixed Servers'!C4", "=MIN('Fixed Servers'!B4,'Fixed Servers'!D4,'Fixed Servers'!E4)", "='Fixed Servers'!F4", "=(C4-B4)/C4", "=IF(B4=MIN(B4,C4,D4),1,0)"],
  ["='Fixed Servers'!C5", "=MIN('Fixed Servers'!B5,'Fixed Servers'!D5,'Fixed Servers'!E5)", "='Fixed Servers'!F5", "=(C5-B5)/C5", "=IF(B5=MIN(B5,C5,D5),1,0)"],
  ["='Fixed Servers'!C6", "=MIN('Fixed Servers'!B6,'Fixed Servers'!D6,'Fixed Servers'!E6)", "='Fixed Servers'!F6", "=(C6-B6)/C6", "=IF(B6=MIN(B6,C6,D6),1,0)"],
  ["='Fixed Servers'!C7", "=MIN('Fixed Servers'!B7,'Fixed Servers'!D7,'Fixed Servers'!E7)", "='Fixed Servers'!F7", "=(C7-B7)/C7", "=IF(B7=MIN(B7,C7,D7),1,0)"],
  ["='Fixed Users'!C4", "=MIN('Fixed Users'!B4,'Fixed Users'!D4,'Fixed Users'!E4)", "='Fixed Users'!F4", "=(C8-B8)/C8", "=IF(B8=MIN(B8,C8,D8),1,0)"],
  ["='Fixed Users'!C6", "=MIN('Fixed Users'!B6,'Fixed Users'!D6,'Fixed Users'!E6)", "='Fixed Users'!F6", "=(C9-B9)/C9", "=IF(B9=MIN(B9,C9,D9),1,0)"],
  ["='Fixed Users'!C7", "=MIN('Fixed Users'!B7,'Fixed Users'!D7,'Fixed Users'!E7)", "='Fixed Users'!F7", "=(C10-B10)/C10", "=IF(B10=MIN(B10,C10,D10),1,0)"],
];
validation.getRange("A3:F3").format = { fill: "#1F4E78", font: { bold: true, color: "#FFFFFF" }, wrapText: true };
validation.getRange("A4:A10").format = { fill: "#EAF2F8", font: { bold: true } };
validation.getRange("B4:D10").format.numberFormat = "0.0000";
validation.getRange("E4:E10").format.numberFormat = "0.00%";
validation.getRange("A3:F10").format.borders = {
  outside: { style: "thin", color: "#7F8C8D" },
  insideHorizontal: { style: "thin", color: "#D9E2F3" },
  insideVertical: { style: "thin", color: "#D9E2F3" },
};
validation.getRange("A:A").format.columnWidth = 16;
validation.getRange("B:B").format.columnWidth = 12;
validation.getRange("C:C").format.columnWidth = 28;
validation.getRange("D:D").format.columnWidth = 12;
validation.getRange("E:F").format.columnWidth = 17;
validation.getRange("A12:F13").values = [
  ["Check", "Expected", "Computed", null, null, null],
  ["Unique configurations with PSP lowest", 7, null, null, null, null],
];
validation.getRange("C13").formulas = [["=SUM(F4:F10)"]];
validation.getRange("A12:C12").format = { fill: "#D9EAF7", font: { bold: true, color: "#1F4E78" } };
validation.getRange("A12:C13").format.borders = { preset: "all", style: "thin", color: "#A6A6A6" };

await fs.mkdir(outputDir, { recursive: true });
await fs.mkdir(previewDir, { recursive: true });

for (const sheetName of ["README", "Fixed Servers", "Fixed Users", "Validation"]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1.25, format: "png" });
  await fs.writeFile(path.join(previewDir, `${sheetName.replaceAll(" ", "_")}.png`), new Uint8Array(await preview.arrayBuffer()));
}

const tableCheck = await workbook.inspect({
  kind: "table",
  range: "Validation!A3:F13",
  include: "values,formulas",
  tableMaxRows: 15,
  tableMaxCols: 8,
  maxChars: 5000,
});
await fs.writeFile(path.join(previewDir, "validation_inspect.ndjson"), tableCheck.ndjson, "utf8");

const errorCheck = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
await fs.writeFile(path.join(previewDir, "formula_error_scan.ndjson"), errorCheck.ndjson, "utf8");

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

console.log(JSON.stringify({ outputPath, previewDir }, null, 2));
