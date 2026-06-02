# Граница API

API опционален. Он показывает, как n8n/Make/Google Sheets могут вызывать ту же бизнес-логику по HTTP.

## Установка

```powershell
cd "C:\Users\WORK\Documents\Work Projects\iqbiq-marketplace-automation-portfolio"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[api]"
```

## Запуск

```powershell
$env:PYTHONPATH = ".\src"
uvicorn marketplace_automation.api:app --reload --port 8000
```

## Проверка health

В другом окне PowerShell:

```powershell
curl http://localhost:8000/health
```

Ожидаемый результат:

```json
{"status":"ok"}
```

## Endpoints API

| Метод | Path | Назначение |
|---|---|---|
| GET | `/health` | Базовая проверка доступности |
| POST | `/ads/report` | Собрать отчет по рекламным кампаниям из строк |
| POST | `/reviews/drafts` | Классифицировать отзывы, создать черновики и обращения |
| POST | `/competitors/opportunities` | Создать конкурентные opportunities и SEO-задачи |
| POST | `/integrations/telegram/digest` | Собрать готовый текст Telegram digest |
| POST | `/integrations/notion/tasks` | Собрать payload задач для Notion |

## Endpoints для integration payloads

Telegram digest:

```powershell
curl -X POST http://localhost:8000/integrations/telegram/digest `
  -H "Content-Type: application/json" `
  -d "{\"ads_rows\":[],\"review_rows\":[],\"ticket_rows\":[],\"opportunity_rows\":[],\"task_rows\":[]}"
```

Notion task payloads:

```powershell
curl -X POST http://localhost:8000/integrations/notion/tasks `
  -H "Content-Type: application/json" `
  -d "{\"tasks\":[{\"task_id\":\"SEO-demo\",\"title\":\"Rewrite card\",\"priority\":\"high\"}]}"
```

## Production notes

- Перед реальным использованием поставить API за auth.
- Добавить ограничения размера запросов.
- Добавить structured logging.
- Retries/rate-limit handling держать во внешних API adapters, а не в core use cases.
- Ответы на отзывы держать в approval mode; для БАДов нельзя auto-publish без ручной проверки.
