import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = process.env.DQN_SOURCE_XLSX;
const outputDir = process.env.DQN_OUTPUT_DIR ?? String.raw`D:\pythonProject\output\spreadsheet_dqn`;
if (!inputPath) throw new Error("DQN_SOURCE_XLSX must point to the original workbook.");

await fs.mkdir(outputDir, { recursive: true });
const workbook = await SpreadsheetFile.importXlsx(await FileBlob.load(inputPath));

async function logInspect(name, opts) {
  const result = await workbook.inspect(opts);
  await fs.writeFile(path.join(outputDir, `${name}.ndjson`), result.ndjson, "utf8");
}

await logInspect("workbook_summary", {
  kind: "workbook,sheet,table,drawing",
  maxChars: 12000,
  tableMaxRows: 12,
  tableMaxCols: 16,
});

for (const sheetName of ["Sheet1", "Sheet1 (2)"]) {
  await logInspect(`${sheetName}_region`, {
    kind: "region",
    sheetId: sheetName,
    range: "A1:Z34",
    maxChars: 20000,
    tableMaxRows: 34,
    tableMaxCols: 26,
  });
  await logInspect(`${sheetName}_styles`, {
    kind: "computedStyle",
    sheetId: sheetName,
    range: "A1:Z34",
    maxChars: 12000,
  });
  await logInspect(`${sheetName}_drawings`, {
    kind: "drawing",
    sheetId: sheetName,
    maxChars: 12000,
  });
  const image = await workbook.render({
    sheetName,
    range: "A1:AE34",
    scale: 1,
    format: "png",
  });
  await fs.writeFile(
    path.join(outputDir, `${sheetName}_original.png`),
    new Uint8Array(await image.arrayBuffer()),
  );
}
