import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(scriptDir, "..");
const templatePath = process.argv[2] ?? path.join(
  repoRoot,
  "data",
  "paper_archive",
  "stage2_original_paper_template.xlsx",
);
const dataPath = path.join(repoRoot, "output", "csv", "stage2_bestq_original_with_dqn.json");
const outputDir = path.join(repoRoot, "output", "spreadsheet_dqn");
const outputPath = path.join(outputDir, "stage2_five_method_comparison_original_paper.xlsx");

const payload = JSON.parse(await fs.readFile(dataPath, "utf8"));
const methods = payload.methods;
const colors = ["#79B8E8", "#F05A5A", "#43B86B", "#E5B84B", "#8A6CC2"];

function valueBy(config, method) {
  const value = payload.values?.[config]?.[method];
  if (typeof value !== "number") {
    throw new Error(`Missing Best Q for ${config}/${method}`);
  }
  return value;
}

function sweepRow(config, label) {
  return [label, ...methods.map((method) => valueBy(config, method))];
}

const fixedServers = [
  sweepRow("10_100", "100"),
  sweepRow("10_130", "130"),
  sweepRow("10_150", "150"),
  sweepRow("10_180", "180"),
];

const fixedUsers = [
  sweepRow("5_130", "5"),
  sweepRow("10_130", "10"),
  sweepRow("15_130", "15"),
  sweepRow("20_130", "20"),
];

await fs.mkdir(outputDir, { recursive: true });
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(templatePath));

for (const name of ["Sheet1", "Sheet1 (2)"]) {
  const preview = await workbook.render({
    sheetName: name,
    autoCrop: "all",
    scale: 1.2,
    format: "png",
  });
  const safeName = name.replaceAll(" ", "_").replaceAll("(", "").replaceAll(")", "");
  await fs.writeFile(
    `${outputDir}/source_${safeName}_preview.png`,
    new Uint8Array(await preview.arrayBuffer()),
  );
}

function styleTitle(sheet, range, title) {
  sheet.getRange(range).merge();
  sheet.getRange(range).values = [[title]];
  sheet.getRange(range).format = {
    fill: "#1F4E79",
    font: { bold: true, color: "#FFFFFF", size: 15 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
}

function styleTable(sheet, range, headerRange) {
  sheet.getRange(range).format.borders = {
    preset: "all",
    style: "thin",
    color: "#C9D2DC",
  };
  sheet.getRange(headerRange).format = {
    fill: "#D9EAF7",
    font: { bold: true, color: "#1F1F1F" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    borders: { preset: "all", style: "thin", color: "#9EB6CE" },
  };
}

function addSweepSheet(name, title, firstHeader, rows, axisTitle) {
  const sheet = workbook.worksheets.add(name);
  sheet.showGridLines = false;
  styleTitle(sheet, "A1:F1", title);
  sheet.getRange("A3:F7").values = [[firstHeader, ...methods], ...rows];
  styleTable(sheet, "A3:F7", "A3:F3");
  sheet.getRange("B4:F7").format.numberFormat = "0.0000";
  sheet.getRange("A3:F7").format.rowHeight = 24;
  sheet.getRange("A3:A11").format.columnWidth = 18;
  sheet.getRange("B3:F11").format.columnWidth = 13;
  sheet.getRange("A9:F11").merge();
  sheet.getRange("A9:F11").values = [[
    "Best Q is the minimum equally weighted normalized cost-delay score; lower is better. The four evolutionary values reproduce the original paper workbook, and DQN uses the archived seed-42 evaluation protocol.",
  ]];
  sheet.getRange("A9:F11").format = {
    fill: "#F2F6FA",
    font: { color: "#3F4A54", italic: true, size: 10 },
    wrapText: true,
    verticalAlignment: "top",
    borders: { preset: "outside", style: "thin", color: "#C9D2DC" },
  };

  const chart = sheet.charts.add("bar", sheet.getRange("A3:F7"));
  chart.title = title;
  chart.titleTextStyle.fontSize = 13;
  chart.hasLegend = true;
  chart.xAxis = { axisType: "textAxis", textStyle: { fontSize: 10 } };
  chart.yAxis = {
    numberFormatCode: "0.00",
    min: 0.18,
    max: 0.75,
    textStyle: { fontSize: 10 },
  };
  chart.xAxis.title.text = axisTitle;
  chart.yAxis.title.text = "Best Q (lower is better)";
  chart.setPosition("H2", "S23");
  chart.series.items.forEach((series, index) => {
    if (index < colors.length) {
      series.fill = colors[index];
      series.line = { color: "#333333", width: 0.75 };
    }
  });
  return sheet;
}

const fixedServersSheet = addSweepSheet(
  "DQN Fixed Servers",
  "Stage II: 10 Servers, Increasing Users",
  "Number of users",
  fixedServers,
  "Number of users",
);

const fixedUsersSheet = addSweepSheet(
  "DQN Fixed Users",
  "Stage II: 130 Users, Increasing Servers",
  "Number of servers",
  fixedUsers,
  "Number of servers",
);

const metrics = workbook.worksheets.add("Representative Metrics");
metrics.showGridLines = false;
styleTitle(metrics, "A1:E1", "Representative Pareto Metrics: 10 Servers / 130 Users");
metrics.getRange("A3:E8").values = [
  ["Method", "HV", "IGD", "Best Q", "Interpretation"],
  ["NS-P", 0.8191, 0.0785, valueBy("10_130", "NS-P"), "Population method"],
  ["PSP", 0.9470, 0.0016, valueBy("10_130", "PSP"), "Population method"],
  ["GCP", 0.8596, 0.0492, valueBy("10_130", "GCP"), "Population method"],
  ["GDP", 0.8945, 0.0326, valueBy("10_130", "GDP"), "Population method"],
  ["DQN", null, null, valueBy("10_130", "DQN"), "Five preference-conditioned solutions"],
];
styleTable(metrics, "A3:E8", "A3:E3");
metrics.getRange("B4:D8").format.numberFormat = "0.0000";
metrics.getRange("A3:A13").format.columnWidth = 14;
metrics.getRange("B3:D13").format.columnWidth = 12;
metrics.getRange("E3:E13").format.columnWidth = 46;
metrics.getRange("A10:E13").merge();
metrics.getRange("A10:E13").values = [[
  "HV: higher is better. IGD: lower is better. Best Q: lower is better. HV and IGD are not assigned to DQN because its five independently trained preference points do not have the same population density as the 50-solution evolutionary populations.",
]];
metrics.getRange("A10:E13").format = {
  fill: "#F2F6FA",
  font: { color: "#3F4A54", size: 10 },
  wrapText: true,
  verticalAlignment: "top",
  borders: { preset: "outside", style: "thin", color: "#C9D2DC" },
};

const audit = workbook.worksheets.add("DQN Data Audit");
audit.showGridLines = false;
styleTitle(audit, "A1:F1", "Stage-II Five-Method Data Audit");
const auditRows = payload.records.map((row) => [
  row.Config,
  row.Method,
  row.BestQ,
  row.ProtocolSeed,
  row.NormalizationClass,
  row.Source,
]);
audit.getRange(`A3:F${auditRows.length + 3}`).values = [
  ["Configuration", "Method", "Best Q", "Seed", "Evidence class", "Source"],
  ...auditRows,
];
styleTable(audit, `A3:F${auditRows.length + 3}`, "A3:F3");
audit.getRange(`C4:C${auditRows.length + 3}`).format.numberFormat = "0.000000";
audit.getRange(`A3:A${auditRows.length + 3}`).format.columnWidth = 18;
audit.getRange(`B3:B${auditRows.length + 3}`).format.columnWidth = 12;
audit.getRange(`C3:D${auditRows.length + 3}`).format.columnWidth = 14;
audit.getRange(`E3:E${auditRows.length + 3}`).format.columnWidth = 24;
audit.getRange(`F3:F${auditRows.length + 3}`).format.columnWidth = 58;
audit.freezePanes.freezeRows(3);

const summaryRow = auditRows.length + 5;
audit.getRange(`A${summaryRow}:F${summaryRow + 2}`).merge();
audit.getRange(`A${summaryRow}:F${summaryRow + 2}`).values = [[
  `Validation: PSP has the lowest Best Q in all ${payload.summary.configuration_count} distinct configurations. Relative to the strongest non-PSP evolutionary method, the reduction ranges from ${payload.summary.minimum_reduction_pct.toFixed(2)}% to ${payload.summary.maximum_reduction_pct.toFixed(2)}% and averages ${payload.summary.mean_reduction_pct.toFixed(2)}%.`,
]];
audit.getRange(`A${summaryRow}:F${summaryRow + 2}`).format = {
  fill: "#E2F0D9",
  font: { color: "#274E13", size: 10, bold: true },
  wrapText: true,
  verticalAlignment: "top",
  borders: { preset: "outside", style: "thin", color: "#70AD47" },
};

for (const [sheet, fileName] of [
  [fixedServersSheet, "excel_fixed_servers_preview.png"],
  [fixedUsersSheet, "excel_fixed_users_preview.png"],
  [metrics, "excel_metrics_preview.png"],
  [audit, "excel_audit_preview.png"],
]) {
  const preview = await workbook.render({
    sheetName: sheet.name,
    autoCrop: "all",
    scale: 1.6,
    format: "png",
  });
  await fs.writeFile(`${outputDir}/${fileName}`, new Uint8Array(await preview.arrayBuffer()));
}

const keyCheck = await workbook.inspect({
  kind: "table",
  sheetId: "DQN Fixed Servers",
  range: "A3:F7",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 8,
});
process.stdout.write(`${keyCheck.ndjson}\n`);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
process.stdout.write(`${errors.ndjson}\n`);

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
process.stdout.write(`Saved ${outputPath}\n`);
