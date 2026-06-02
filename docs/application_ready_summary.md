# Сводка готовности к отклику

## Текущее состояние

Проект можно использовать как портфолио-кейс после финальной публикации в отдельный GitHub-репозиторий.

## Самые сильные артефакты

- `README.md`
- `CHANGELOG.md`
- `reports/action_plan.md`
- `reports/executive_summary.md`
- `reports/telegram_digest.txt`
- `docs/assets/ads_dashboard.png`
- `reports/ads_decision_audit.csv`
- `reports/data_quality_report.md`
- `docs/demo_recording_checklist.md`
- `docs/github_publication_guide.md`
- `docs/case_study.md`
- `docs/google_sheets_no_cloud_setup.md`
- `docs/n8n_self_host_setup.md`
- `docs/operator_sop.md`
- `docs/real_integration_feasibility.md`
- `docs/risk_register.md`
- `docs/repository_readiness_audit.md`
- `docs/submission_checklist.md`
- `docs/vacancy_fit_matrix.md`
- `docs/final_application_message.md`
- `docs/handoff.md`

## Что демонстрирует проект

- Аналитику рекламных кампаний по данным в стиле WB/Ozon.
- Unit economics и break-even ДРР.
- Классификацию отзывов и approval workflow для нутрицевтиков.
- Конкурентный SEO/content мониторинг.
- Google Sheets no-cloud режим через публичные CSV-ссылки.
- Локальный n8n self-host через Docker Compose.
- Live workflow: Google Sheet -> n8n -> Python API -> Telegram -> Notion.
- Отправку Telegram digest.
- Создание и обновление Notion задач без дублей.
- SOP для ежедневного использования action plan.
- Проверяемую бизнес-логику с unit-тестами.
- Проверку качества входных таблиц и подозрительных метрик.
- Scenario coverage для рискованных и нормальных входных данных.
- Risk register и ограничения production rollout.
- Repository readiness audit перед публикацией.

## Проверка

```powershell
cd "C:\Users\WORK\Documents\Work Projects\iqbiq-marketplace-automation-portfolio"
.\scripts\preflight.ps1
```

Ожидаемо:

```text
Финальная проверка пройдена.
35 tests OK.
```

## Что осталось перед GitHub

- Проверить финальный `.gitignore` и отсутствие секретов.
- Перезаписать скриншоты, если менялся внешний вид dashboard.
- Записать короткое демо по `docs/demo_recording_checklist.md`.
- Опубликовать проект в отдельный GitHub-репозиторий.
- После публикации перевыпустить demo-токены.
