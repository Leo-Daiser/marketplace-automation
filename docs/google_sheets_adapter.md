# Google Sheets adapter

## Цель

Проект оставляет CSV как default demo storage, но тот же table contract можно использовать с Google Sheets.

Если Google Cloud/service accounts недоступны, использовать no-cloud setup:

```text
docs/google_sheets_no_cloud_setup.md
```

Adapter реализован в:

```text
src/marketplace_automation/adapters/google_sheets.py
```

Он поддерживает:

- чтение sheet, где первая строка содержит headers;
- запись rows обратно через Google Sheets Values API;
- service account auth как optional dependency;
- fake transport tests без real credentials.

No-cloud adapter реализован в:

```text
src/marketplace_automation/adapters/google_sheets_no_cloud.py
```

Он поддерживает:

- чтение public Google Sheets tabs через CSV links;
- запись output rows через Google Apps Script web app;
- fake transport tests без real credentials.

## Установка optional dependencies

```powershell
cd marketplace-automation
pip install -e ".[sheets]"
```

## Использование service account

```python
from marketplace_automation.adapters.google_sheets import GoogleSheetsTableStore

store = GoogleSheetsTableStore.from_service_account_file(
    spreadsheet_id="YOUR_SPREADSHEET_ID",
    service_account_file="service-account.json",
)

ads_rows = store.read_table("ads_daily")
store.write_table("support_tickets", [{"ticket_id": "T-1", "priority": "P1"}])
```

## Нужные spreadsheet tabs

Входные tabs:

- `ads_daily`
- `reviews`
- `competitors`
- `our_products`
- `keyword_plan`
- `unit_economics`

Выходные tabs:

- `ads_campaign_report`
- `review_replies`
- `support_tickets`
- `competitor_opportunities`
- `seo_content_tasks`
- `unit_economics_report`

Column contracts описаны в `docs/google_sheets_schema.md`.

## CLI sync

Скачать выбранные tabs в CSV:

```powershell
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli sheets-pull `
  --spreadsheet-id "YOUR_SPREADSHEET_ID" `
  --service-account-file ".\service-account.json" `
  --out-dir .\data\sample `
  --tables ads_daily reviews competitors our_products keyword_plan unit_economics
```

Загрузить generated output CSV files обратно в Google Sheets:

```powershell
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli sheets-push `
  --spreadsheet-id "YOUR_SPREADSHEET_ID" `
  --service-account-file ".\service-account.json" `
  --data-dir .\reports `
  --tables ads_campaign_report review_replies support_tickets competitor_opportunities seo_content_tasks unit_economics_report
```

## Security notes

- Не коммитить `service-account.json`.
- Share spreadsheet with service account email.
- Выдавать только минимально нужный доступ.
- Использовать отдельную spreadsheet для demo data.
