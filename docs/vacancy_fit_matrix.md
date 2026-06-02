# Матрица соответствия вакансии

## Цель

Матрица связывает требования вакансии IQBIQ с конкретными артефактами репозитория. Использовать при подготовке отклика или собеседования.

## Обязанности

| Обязанность из вакансии | Подтверждение в проекте |
|---|---|
| Автоматизация отчетности по рекламе WB/Ozon | `src/marketplace_automation/ads_reporter.py`, `reports/ads_campaign_report.csv`, `reports/ads_dashboard.html` |
| Анализ ставок, CTR, CPC, конверсий, заказов, ДРР | `ads_reporter.py`, `data/sample/ads_daily.csv`, `reports/ads_report.md` |
| AI-агенты для аналитики, отзывов, SEO и контента | `review_agent.py`, `competitor_monitor.py`, `portfolio.py` |
| Автоматизация ответов на отзывы | `review_agent.py`, `reports/review_replies.csv`, `reports/support_tickets.csv` |
| Подготовка обращений в поддержку | `build_support_ticket`, `reports/support_tickets.csv` |
| Сбор и анализ конкурентов | `competitor_monitor.py`, `data/sample/competitors.csv`, `reports/competitor_opportunities.csv` |
| Автоматизация таблиц и учета | `adapters/google_sheets.py`, `scripts/preflight.ps1`, `docs/google_sheets_schema.md` |
| Интеграции Google Sheets, Telegram, Notion, API | `adapters/google_sheets.py`, `notifications.py`, `notion_payloads.py`, `api.py` |
| Инструкции и регламенты | `docs/demo_walkthrough.md`, `docs/submission_checklist.md`, `docs/github_publication_guide.md` |

## Требования

| Требование вакансии | Подтверждение в проекте |
|---|---|
| AI / no-code / low-code automation | n8n templates в `integrations/n8n/`, API boundary в `api.py` |
| Make / n8n / Google Sheets / API | n8n templates, Google Sheets adapter, FastAPI endpoints |
| Python или JavaScript basics | Python package в `src/marketplace_automation`, CLI и tests |
| Понимание e-commerce и ads analytics | ДРР, ROAS, unit economics, break-even ДРР, campaign recommendations |
| Умение разбираться в процессах и доводить до результата | `reports/action_plan.md`, `reports/executive_summary.md`, `docs/sprint_review_2026-06-01.md` |

## Преимущества

| Преимущество из вакансии | Подтверждение в проекте |
|---|---|
| Wildberries/Ozon experience | WB/Ozon sample data и `adapters/marketplace_api.py` |
| AI agents | deterministic review/SEO agents с optional API boundaries |
| Ads, SEO, content или reporting automation cases | три отдельных project cases в `projects/` |
| Marketplace unit economics | `unit_economics.py`, `data/sample/unit_economics.csv`, `reports/unit_economics_report.csv` |

## Формулировка для отклика

```text
Я подготовил портфолио-кейс автоматизации маркетплейсов, близкий к вашему процессу:
WB/Ozon-style ads reporting с ДРР/ROAS/unit economics,
review-response workflow с approval и compliance flags,
competitor SEO monitoring, Google Sheets/n8n/Telegram/Notion integration boundaries
и consolidated daily action plan для performance, support и SEO/content owners.
```

## Честные ограничения

```text
Кейс использует synthetic data для безопасной публикации.
Реальный production rollout требует ваших WB/Ozon credentials, подтверждения endpoint versions,
real Google Sheets/n8n credentials и approval rules от команды.
```
