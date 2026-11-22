// Google Sheet logger for the PixelSense study.
// 1. Create a new Google Sheet, then Extensions > Apps Script. Paste this whole file (replace everything).
// 2. Deploy > New deployment > type: Web app. Execute as: Me. Who has access: Anyone. Deploy and copy the Web app URL (ends in /exec).
// 3. In Streamlit Cloud: your app > Settings > Secrets, add:   STUDY_WEBHOOK = "https://script.google.com/macros/s/XXXX/exec"
// 4. Test: open the /exec URL in a browser. It should say "PixelSense logger is running".
// If you change this script later, use Deploy > Manage deployments > Edit > New version, otherwise the old code keeps running.
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);                       // several participants can submit at the same moment
  try {
    var data = JSON.parse(e.postData.contents);
    var ss = SpreadsheetApp.getActiveSpreadsheet();
    var sh = ss.getSheetByName(data.sheet) || ss.insertSheet(data.sheet);
    var keys = Object.keys(data.row);
    if (sh.getLastRow() === 0) sh.appendRow(keys);
    sh.appendRow(keys.map(function (k) { return data.row[k]; }));
    return ContentService.createTextOutput("ok");
  } finally {
    lock.releaseLock();
  }
}
function doGet() {
  return ContentService.createTextOutput("PixelSense logger is running");
}
