// Paste into script.google.com (Extensions > Apps Script from a new Google Sheet), then Deploy > New deployment > Web app:
// Execute as: Me, Who has access: Anyone. Copy the web app URL into the STUDY_WEBHOOK secret of the Streamlit app.
function doPost(e) {
  var data = JSON.parse(e.postData.contents);
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(data.sheet) || ss.insertSheet(data.sheet);
  var keys = Object.keys(data.row);
  if (sh.getLastRow() === 0) sh.appendRow(keys);
  sh.appendRow(keys.map(function (k) { return data.row[k]; }));
  return ContentService.createTextOutput("ok");
}
