import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = process.env.DQN_SOURCE_XLSX;
const outputDir = process.env.DQN_OUTPUT_DIR ?? String.raw`D:\pythonProject\output\spreadsheet_dqn`;
const paperCsv = process.env.DQN_PAPER_CSV ?? String.raw`D:\pythonProject\output\csv\dqn_control_bestq_paper_aligned.csv`;
const rerunCsv = process.env.DQN_RERUN_CSV ?? String.raw`D:\pythonProject\output\csv\dqn_control_bestq_full_rerun.csv`;
if (!inputPath) throw new Error("DQN_SOURCE_XLSX must point to the original workbook.");

await fs.mkdir(outputDir, { recursive: true });

function parseCsv(text) {
  const lines = text.trim().split(/\r?\n/);
  const headers = lines[0].split(",");
  return lines.slice(1).map((line) => {
    const cells = line.split(",");
    return Object.fromEntries(headers.map((header, index) => [header, cells[index]]));
  });
}

function getDqnValue(rows, config) {
  const row = rows.find((item) => item.Config === config && item.Method === "DQN");
  if (!row) throw new Error(`Missing DQN value for ${config}`);
  return Number(row.BestQ);
}

function writeDqnBlock(sheet, labelCell, valueCell, copyFrom, value) {
  sheet.getRange(`${labelCell}:${valueCell}`).copyFrom(sheet.getRange(copyFrom), "all");
  sheet.getRange(labelCell).values = [["DQN"]];
  sheet.getRange(valueCell).values = [[value]];
  sheet.getRange(valueCell).format.numberFormat = "0.0000";
}

const paperRows = parseCsv(await fs.readFile(paperCsv, "utf8"));
const rerunRows = parseCsv(await fs.readFile(rerunCsv, "utf8"));
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));
const fixedServers = workbook.worksheets.getItem("Sheet1");
const fixedUsers = workbook.worksheets.getItem("Sheet1 (2)");

writeDqnBlock(fixedServers, "F9", "F10", "E9:E10", getDqnValue(paperRows, "10_100"));
writeDqnBlock(fixedServers, "Z9", "Z10", "Y9:Y10", getDqnValue(paperRows, "10_130"));
writeDqnBlock(fixedServers, "F26", "F27", "E26:E27", getDqnValue(paperRows, "10_150"));
writeDqnBlock(fixedServers, "Z26", "Z27", "Y26:Y27", getDqnValue(paperRows, "10_180"));
writeDqnBlock(fixedUsers, "F9", "F10", "E9:E10", getDqnValue(paperRows, "5_130"));
writeDqnBlock(fixedUsers, "Z9", "Z10", "Y9:Y10", getDqnValue(paperRows, "10_130"));
writeDqnBlock(fixedUsers, "F26", "F27", "E26:E27", getDqnValue(paperRows, "15_130"));
writeDqnBlock(fixedUsers, "Z26", "Z27", "Y26:Y27", getDqnValue(paperRows, "20_130"));

const summary = workbook.worksheets.getOrAdd("DQN_summary");
summary.getRange("A1:E1").values = [["Config", "Method", "BestQ", "Source", "FigureSet"]];
summary.getRange("A1:E1").format = {
  fill: "#D9EAF7",
  font: { bold: true, color: "#000000" },
  borders: { preset: "all", style: "thin", color: "#A6A6A6" },
};
const paperValues = paperRows.map((row) => [row.Config, row.Method, Number(row.BestQ), row.Source, "paper_aligned"]);
const rerunValues = rerunRows.map((row) => [row.Config, row.Method, Number(row.BestQ), row.Source, "full_rerun"]);
const allValues = [...paperValues, ...rerunValues];
summary.getRangeByIndexes(1, 0, allValues.length, 5).values = allValues;
summary.getRangeByIndexes(1, 2, allValues.length, 1).format.numberFormat = "0.0000";
summary.getRange("A1:E1").format.rowHeight = 24;
summary.getRange("A:E").format.autofitColumns();
summary.freezePanes.freezeRows(1);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan before DQN workbook export",
});
await fs.writeFile(path.join(outputDir, "workbook_error_scan.ndjson"), errors.ndjson, "utf8");

const output = await SpreadsheetFile.exportXlsx(workbook);
const outPath = path.join(outputDir, "change_color_stage2_user_with_DQN.xlsx");
await output.save(outPath);
console.log(`Saved ${outPath}`);
