import fs from "node:fs/promises";
import path from "node:path";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const dir = "D:/scam-detector/outputs/01a1f88b-8092-7493-9320-64f6cf99cc36/test-cases";
const results = [];
for (let sprint=1; sprint<=5; sprint++) {
  const file = path.join(dir, `C1SE.06_TestCase_Sprint${sprint}_v1.0.xlsx`);
  const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(file));
  wb.recalculate();
  const sheets = await wb.inspect({kind:"sheet",include:"id,name",maxChars:4000});
  const summary = await wb.inspect({kind:"table",range:"'Sprint Report'!A1:H20",include:"values,formulas",tableMaxRows:22,tableMaxCols:10,maxChars:8000});
  const errors = await wb.inspect({kind:"match",searchTerm:"#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",options:{useRegex:true,maxResults:100},maxChars:4000});
  results.push({sprint,file,size:(await fs.stat(file)).size,sheets:sheets.records.map(r=>r.name),summary:summary.ndjson,errors:errors.ndjson});
}
await fs.writeFile(path.join(dir,"verification.json"),JSON.stringify(results,null,2),"utf8");
console.log(JSON.stringify(results.map(r=>({sprint:r.sprint,size:r.size,sheetCount:r.sheets.length,sheets:r.sheets,errors:r.errors})),null,2));
