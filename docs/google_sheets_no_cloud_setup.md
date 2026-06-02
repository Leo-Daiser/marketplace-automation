# Google Sheets без Google Cloud

## Цель

Этот вариант нужен для регионов или аккаунтов, где Google Cloud/service account недоступны или неудобны.

Проект все равно может использовать Google Sheets как демо-интерфейс:

- входные листы читаются через публичные CSV-ссылки;
- выходные листы записываются через Google Apps Script web app;
- Google Cloud Console и service account JSON не нужны.

## Текущая демо-таблица

```text
https://docs.google.com/spreadsheets/d/1GlrDyHe7haN22Z1fU0JPbWfbh0bgEswAqBZNwE3-apc/edit?usp=sharing
```

Spreadsheet ID:

```text
1GlrDyHe7haN22Z1fU0JPbWfbh0bgEswAqBZNwE3-apc
```

Текущий статус:

- входные листы заполнены из `data/sample`;
- выходные листы заполнены из `reports/google_demo_from_sheet`;
- чтение публичного CSV проверено;
- `run-all` на `data/google_demo` проверен.

## Нужные листы

Входные листы:

- `ads_daily`
- `reviews`
- `competitors`
- `our_products`
- `keyword_plan`
- `unit_economics`

Выходные листы:

- `ads_campaign_report`
- `review_replies`
- `support_tickets`
- `competitor_opportunities`
- `seo_content_tasks`
- `unit_economics_report`

Контракты колонок описаны в `docs/google_sheets_schema.md`.

## Шаг 1. Заполнить входные листы

Скопировать содержимое локальных CSV-файлов в одноименные листы Google Sheet:

```text
data/sample/ads_daily.csv
data/sample/reviews.csv
data/sample/competitors.csv
data/sample/our_products.csv
data/sample/keyword_plan.csv
data/sample/unit_economics.csv
```

Первая строка должна быть строкой заголовков.

## Шаг 2. Включить чтение по ссылке

Для каждого входного листа можно выбрать один из вариантов:

- открыть таблицу в режиме `Anyone with the link can view`;
- либо использовать `File -> Share -> Publish to web` и опубликовать нужные листы как CSV.

Проект читает листы по такому URL-шаблону:

```text
https://docs.google.com/spreadsheets/d/<SPREADSHEET_ID>/gviz/tq?tqx=out:csv&sheet=<TAB_NAME>
```

## Шаг 3. Добавить Apps Script writer

В Google Sheet:

1. Открыть `Extensions -> Apps Script`.
2. Удалить стандартный код.
3. Вставить код из:

```text
integrations/google_apps_script/sheets_web_app.gs
```

4. Заменить строку:

```javascript
const SECRET = 'CHANGE_ME_TO_YOUR_SECRET';
```

Пример:

```javascript
const SECRET = 'demo-local-secret-123';
```

5. Нажать `Deploy -> New deployment`.
6. Тип: `Web app`.
7. Execute as: `Me`.
8. Who has access: `Anyone with the link`.
9. Нажать `Deploy`.
10. Скопировать `/exec` Web App URL.

Секрет нельзя публиковать в GitHub.

## Шаг 4. Скачать входные листы в локальные CSV

```powershell
cd marketplace-automation
$env:PYTHONPATH = ".\src"

python -m marketplace_automation.cli sheets-link-pull `
  --spreadsheet-id "1GlrDyHe7haN22Z1fU0JPbWfbh0bgEswAqBZNwE3-apc" `
  --out-dir .\data\google_demo `
  --tables ads_daily reviews competitors our_products keyword_plan unit_economics
```

## Шаг 5. Запустить portfolio pipeline

```powershell
python -m marketplace_automation.cli run-all `
  --data-dir .\data\google_demo `
  --out-dir .\reports\google_demo
```

## Шаг 6. Загрузить результаты обратно в Google Sheets

```powershell
$env:GOOGLE_SHEETS_WEBAPP_URL = "PASTE_APPS_SCRIPT_WEB_APP_EXEC_URL"
$env:GOOGLE_SHEETS_WEBAPP_SECRET = "demo-local-secret-123"

python -m marketplace_automation.cli sheets-webapp-push `
  --web-app-url $env:GOOGLE_SHEETS_WEBAPP_URL `
  --secret $env:GOOGLE_SHEETS_WEBAPP_SECRET `
  --data-dir .\reports\google_demo `
  --tables ads_campaign_report review_replies support_tickets competitor_opportunities seo_content_tasks unit_economics_report
```

## Что это доказывает в портфолио

- Google Sheets можно использовать без Google Cloud service account.
- Входные данные можно вести вручную в таблице.
- Результаты можно возвращать обратно в листы.
- n8n может оркестрировать тот же flow через HTTP Request nodes.
- Секреты остаются вне Git.

## Текущее ограничение

Это demo-grade интеграция. Для production лучше Google Cloud/service account или более строгий auth layer. Apps Script с shared secret приемлем для контролируемого портфолио-демо, но не для чувствительных production-данных.
