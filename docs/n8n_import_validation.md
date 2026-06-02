# Проверка импорта n8n

## Цель

Сделать n8n-часть портфолио проверяемой без доступа к чужому private n8n instance.

В репозитории есть workflow templates:

```text
integrations/n8n/ads_report_to_telegram.json
integrations/n8n/review_agent_to_support.json
integrations/n8n/competitor_monitor_to_notion.json
```

## Статическая validation

Запустить:

```powershell
cd marketplace-automation
python -m json.tool .\integrations\n8n\ads_report_to_telegram.json > $null
python -m json.tool .\integrations\n8n\review_agent_to_support.json > $null
python -m json.tool .\integrations\n8n\competitor_monitor_to_notion.json > $null
```

Ожидаемый результат: нет вывода и код выхода 0.

## Чеклист ручного импорта

1. Открыть n8n.
2. Импортировать один JSON workflow.
3. Заменить placeholder credentials:
   - `REPLACE_ME`;
   - `GOOGLE_SHEET_ID`;
   - `TELEGRAM_CHAT_ID`;
   - `NOTION_DATABASE_ID`.
4. Проверить, что у каждого node валидные credentials.
5. Запустить Python API локально, если workflow использует HTTP Request:

```powershell
$env:PYTHONPATH = ".\src"
uvicorn marketplace_automation.api:app --reload --port 8000
```

6. Запустить workflow вручную на sample data.
7. Подтвердить, что output записан в ожидаемый Google Sheet, Telegram chat или Notion database.

## Проверки по workflow

| Workflow | Проверка |
|---|---|
| `ads_report_to_telegram.json` | Telegram message содержит spend, revenue, ДРР и число risk campaigns |
| `review_agent_to_support.json` | Tickets создаются только для high-risk или non-positive delivery/packaging cases |
| `competitor_monitor_to_notion.json` | Notion task title и priority создаются из первого task payload |

## Известные ограничения

- Templates намеренно используют placeholders вместо real credentials.
- Competitor workflow перед production требует real `our_products` и `keyword_plan` inputs в n8n.
- Review workflow должен оставаться approval-based; нельзя auto-publish nutraceutical replies.

## Production hardening

- Добавить n8n error workflow для failed HTTP calls.
- Добавить retry policy для Google Sheets и Notion writes.
- Хранить credentials только в n8n credentials storage.
- Добавить dead-letter Google Sheet tab для payloads, которые не прошли validation.
