# Матрица возможностей

Документ связывает функциональные блоки проекта с конкретными артефактами репозитория.

## Операционные сценарии

| Сценарий | Подтверждение в проекте |
|---|---|
| Рекламная аналитика маркетплейсов | `src/marketplace_automation/ads_reporter.py`, `reports/ads_dashboard.html`, `reports/ads_decision_audit.csv` |
| Учет unit economics | `src/marketplace_automation/unit_economics.py`, `data/sample/unit_economics.csv`, `tests/test_unit_economics.py` |
| Обработка отзывов | `src/marketplace_automation/review_agent.py`, `reports/review_replies.csv`, `reports/support_tickets.csv` |
| Контроль compliance для health-категорий | `tests/test_review_agent.py`, поля `approval_status`, `compliance_flags`, `manual_review_required` |
| Мониторинг конкурентов | `src/marketplace_automation/competitor_monitor.py`, `reports/competitor_opportunities.csv` |
| SEO/content backlog | `reports/seo_content_tasks.csv`, `src/marketplace_automation/notion_payloads.py` |
| Сводный action plan | `src/marketplace_automation/portfolio.py`, `reports/action_plan.md` |
| Управленческая сводка | `reports/executive_summary.md`, `docs/assets/executive_summary.png` |

## Интеграции

| Интеграция | Как реализована |
|---|---|
| CSV / Google Sheets contracts | `src/marketplace_automation/adapters/csv_store.py`, `docs/google_sheets_schema.md` |
| Google Sheets без Google Cloud | `src/marketplace_automation/adapters/google_sheets_no_cloud.py`, `integrations/google_apps_script/sheets_web_app.gs` |
| n8n orchestration | `integrations/n8n/no_cloud_marketplace_digest.json`, `integrations/n8n/self_host/docker-compose.yml` |
| Telegram digest | `src/marketplace_automation/notifications.py`, `reports/telegram_digest.txt` |
| Notion tasks | `src/marketplace_automation/notion_payloads.py`, `tests/test_notion_payloads.py` |
| API layer | `src/marketplace_automation/api.py`, `docs/api.md` |
| Marketplace API boundary | `src/marketplace_automation/adapters/marketplace_api.py`, `docs/marketplace_api_adapters.md` |

## Качество

| Контроль | Где смотреть |
|---|---|
| Unit tests | `tests/` |
| Regression snapshots | `tests/test_regression_snapshots.py` |
| Scenario coverage | `data/scenarios/`, `docs/scenario_coverage.md` |
| Data validation | `src/marketplace_automation/schemas.py`, `src/marketplace_automation/data_quality.py` |
| Preflight | `scripts/preflight.ps1`, `docs/quality_gate.md` |
| Repository readiness | `docs/repository_readiness_audit.md`, `.gitignore` |

## Что демонстрирует проект

- Умение держать бизнес-логику отдельно от no-code orchestration.
- Проверяемую обработку рекламных, review и competitor данных.
- Аккуратную работу с integration boundaries без публикации токенов и приватных данных.
- Операционный output в формате отчетов, задач и дайджестов, а не только сырых таблиц.
