# Сценарий демо-видео

Целевая длина: 2-3 минуты.

## 0:00-0:20 Проблема

Текст:

```text
Этот проект автоматизирует marketplace growth operations для бренда нутрицевтиков:
отчетность по рекламе, workflow обработки отзывов, competitor SEO monitoring и team handoff.
Цель не просто посчитать метрики, а выдать ежедневный action plan для performance, support и SEO/content owners.
```

Показать:

- repository root;
- `README.md`;
- `docs/architecture.md`.

## 0:20-0:45 Архитектура

Текст:

```text
Core logic детерминирована и покрыта тестами.
CSV используется как Google Sheets-compatible demo contract.
External systems изолированы за adapters: Google Sheets, WB/Ozon API, Telegram, Notion и n8n.
```

Показать:

- `src/marketplace_automation/`;
- `adapters/`;
- `ports.py`;
- `schemas.py`;
- `models.py`.

## 0:45-1:10 Запуск suite

Команда:

```powershell
cd marketplace-automation
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli run-all --data-dir .\data\sample --out-dir .\reports
```

Текст:

```text
Одна команда регенерирует все reports из sample marketplace data.
Sample data синтетические, поэтому repo безопасен для публикации.
```

Показать вывод терминала.

## 1:10-1:40 Бизнес-результаты

Открыть:

```text
reports/executive_summary.md
reports/action_plan.md
reports/telegram_digest.txt
reports/ads_dashboard.html
```

Текст:

```text
Самый сильный output — action plan.
Он приоритизирует risky campaigns, support tickets и competitor gaps с owners и evidence.
Это artifact, которым оператор может пользоваться в течение дня.
```

## 1:40-2:10 Интеграции

Показать:

```text
docs/google_sheets_adapter.md
docs/marketplace_api_adapters.md
docs/n8n_import_validation.md
integrations/n8n/
```

Текст:

```text
В проекте есть Google Sheets sync commands, WB/Ozon adapter interfaces,
n8n workflow templates, Telegram formatting и Notion task payload builders.
Workflows остаются тонкими, потому что business decisions остаются в Python.
```

## 2:10-2:30 Проверка качества

Команда:

```powershell
python -m unittest discover -s tests
```

Текст:

```text
Важные business rules покрыты tests: ad decisions, review compliance,
competitor scoring, adapters, API routes и integration payloads.
```

Показать:

```text
35 tests OK
```

## 2:30-2:50 Ограничения

Текст:

```text
Это portfolio prototype, а не production deployment.
Реальный deployment требует client credentials, endpoint version confirmation,
retry policies, rate limits и approval flow setup в инструментах клиента.
```

## 2:50-3:00 Завершение

Текст:

```text
На paid test stage я бы подключил реальные Sheets/WB/Ozon data клиента,
развернул daily digest workflow и сначала внедрил две автоматизации:
ads daily action plan и review support workflow.
```
