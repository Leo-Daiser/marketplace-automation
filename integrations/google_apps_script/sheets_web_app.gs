const SECRET = 'CHANGE_ME_TO_YOUR_SECRET';

function doGet() {
  return jsonResponse({
    ok: true,
    service: 'marketplace-automation-sheets-web-app',
  });
}

function doPost(e) {
  try {
    const payload = JSON.parse(e.postData.contents || '{}');
    if (payload.secret !== SECRET) {
      return jsonResponse({ ok: false, error: 'unauthorized' });
    }

    const tableName = String(payload.table || '').trim();
    if (!tableName) {
      return jsonResponse({ ok: false, error: 'table is required' });
    }

    const mode = String(payload.mode || 'replace').trim();
    const rows = Array.isArray(payload.rows) ? payload.rows : [];
    const fieldnames = Array.isArray(payload.fieldnames) ? payload.fieldnames : inferFieldnames(rows);

    const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
    const sheet = spreadsheet.getSheetByName(tableName) || spreadsheet.insertSheet(tableName);

    if (mode === 'replace') {
      sheet.clearContents();
    }

    if (fieldnames.length === 0) {
      return jsonResponse({ ok: true, table: tableName, rows: 0, columns: 0 });
    }

    const values = [fieldnames].concat(rows.map((row) => fieldnames.map((field) => stringifyCell(row[field]))));
    const startRow = mode === 'append' && sheet.getLastRow() > 0 ? sheet.getLastRow() + 1 : 1;
    const valuesToWrite = mode === 'append' && sheet.getLastRow() > 0 ? values.slice(1) : values;

    if (valuesToWrite.length > 0) {
      sheet.getRange(startRow, 1, valuesToWrite.length, fieldnames.length).setValues(valuesToWrite);
    }

    return jsonResponse({
      ok: true,
      table: tableName,
      rows: rows.length,
      columns: fieldnames.length,
      mode: mode,
    });
  } catch (error) {
    return jsonResponse({
      ok: false,
      error: String(error && error.message ? error.message : error),
    });
  }
}

function inferFieldnames(rows) {
  if (!rows.length) {
    return [];
  }
  return Object.keys(rows[0]);
}

function stringifyCell(value) {
  if (value === null || value === undefined) {
    return '';
  }
  if (typeof value === 'object') {
    return JSON.stringify(value);
  }
  return String(value);
}

function jsonResponse(payload) {
  return ContentService
    .createTextOutput(JSON.stringify(payload))
    .setMimeType(ContentService.MimeType.JSON);
}
