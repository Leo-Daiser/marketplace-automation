# Архитектура

## Цель продукта

Проект является портфолио-системой автоматизации marketplace growth operations:

- ежедневный контроль рекламной эффективности WB/Ozon;
- работа с отзывами с compliance-ограничениями для БАДов;
- конкурентный SEO/content мониторинг;
- передача actionable результатов в Google Sheets, Telegram, Notion и n8n.

Система намеренно воспроизводится сначала на синтетических CSV-данных. Реальные API маркетплейсов вынесены в integration adapters и не смешаны с core business logic.

## Границы системы

```text
Marketplace APIs / Google Sheets / CSV
        |
        v
Ingestion adapters
        |
        v
Use cases
  - Ads Performance Copilot
  - Review Response Agent
  - Мониторинг конкурентов и SEO
        |
        v
Policy and decision layer
  - ad thresholds
  - review compliance
  - competitor scoring
        |
        v
Outputs
  - CSV tables
  - Markdown digests
  - HTML dashboard
  - JSON payloads
  - consolidated action plan
        |
        v
n8n / Telegram / Notion / Google Sheets
```

## Ключевые архитектурные решения

1. Core logic детерминирована и тестируема.
   LLM/no-code инструменты могут оркестрировать и готовить drafts, но решения по кампаниям, risk flags и compliance checks должны проверяться тестами.

2. Проект стартует от CSV contracts.
   CSV делает демо воспроизводимым и напрямую ложится на Google Sheets. API adapters можно подключать без переписывания use cases.

3. Сгенерированные outputs считаются операционными артефактами.
   Ревьюер должен открыть `reports/action_plan.md` и понять, что автоматизация рекомендует команде сделать сегодня.

4. Compliance является частью core logic.
   Для БАДов ответы на отзывы не должны содержать медицинских обещаний, диагнозов, гарантированного эффекта и небезопасных советов.

## Структура пакета

```text
marketplace_automation/
  ports.py                 границы протоколов для внешних систем
  adapters/                реализации CSV/Sheets/API adapters
  ads_reporter.py          метрики рекламы, решения по кампаниям, отчеты
  review_agent.py          классификация отзывов, drafts, support tickets
  competitor_monitor.py    конкурентный scoring, SEO/content backlog
  portfolio.py             orchestration трех кейсов и action plan
  api.py                   optional FastAPI boundary для n8n
  cli.py                   воспроизводимые локальные entrypoints
  io_utils.py              helpers для CSV/JSON/Markdown/HTML
  schemas.py               validation входных контрактов
  models.py                typed domain row objects для core inputs
```

## Контракты данных

Input contracts описаны в `docs/google_sheets_schema.md`. Output contracts:

- `ads_campaign_report.csv`
- `review_replies.csv`
- `support_tickets.csv`
- `competitor_opportunities.csv`
- `seo_content_tasks.csv`
- `action_plan.md`
- `executive_summary.md`

## Проверки качества

Перед показом проекта:

```powershell
cd "C:\Users\WORK\Documents\Work Projects\iqbiq-marketplace-automation-portfolio"
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli run-all --data-dir .\data\sample --out-dir .\reports
python -m unittest discover -s tests
python -m compileall -q .\src .\tests
python -m json.tool .\integrations\n8n\ads_report_to_telegram.json > $null
python -m json.tool .\integrations\n8n\review_agent_to_support.json > $null
python -m json.tool .\integrations\n8n\competitor_monitor_to_notion.json > $null
```

## Следующие архитектурные улучшения

- Глубже использовать typed domain models внутри report builders.
- Расширить CLI sync для Google Sheets adapter.
- Добавить smoke test FastAPI server.
- Добавить approval queue для ответов на отзывы перед публикацией.
- Расширить SKU unit-economics model: commissions, logistics, storage, returns, tax assumptions.
- Добавить дополнительные screenshots/demo assets для README.
