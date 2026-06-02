# Передача проекта

## Статус

Портфолио-проект готов к показу после публикации на GitHub или локального демонстрационного запуска.

Последняя проверенная команда:

```powershell
.\scripts\preflight.ps1
```

Ожидаемый результат:

```text
Финальная проверка пройдена.
35 tests OK.
```

## Сначала открыть

1. `README.md`
2. `docs/project_status_summary.md`
3. `docs/capability_matrix.md`
4. `docs/project_demo_summary.md`
5. `docs/github_publication_guide.md`

## Демо-артефакты

Генерируются командами `run-all` / `preflight.ps1`:

```text
reports/executive_summary.md
reports/action_plan.md
reports/telegram_digest.txt
reports/ads_decision_audit.csv
reports/data_quality_report.md
reports/ads_dashboard.html
reports/review_replies.csv
reports/seo_content_tasks.csv
```

## Оставшиеся ручные задачи

1. Перенести проект в отдельный GitHub-репозиторий.
2. Запустить `.\scripts\preflight.ps1`.
3. Перегенерировать скриншоты, если доступен `msedge`, `chrome` или `chromium`.
4. Записать видео на 2-3 минуты по `docs/demo_video_script.md`.
5. Проверить публичные ссылки и screenshots.

## Что нельзя утверждать

- Что реальная production-интеграция WB/Ozon уже подключена.
- Что ответы на отзывы можно публиковать автоматически без ручного approval.
- Что sample-данные являются реальными клиентскими данными.
- Что проект готов к production без проверки rate limits, auth, retries и доступа к кабинетам маркетплейсов.

## Краткая формулировка проекта

```text
Я собрал воспроизводимый портфолио-кейс автоматизации маркетплейсов:
детерминированное Python-ядро, Google Sheets/n8n/Telegram/Notion интеграции,
WB/Ozon adapter boundaries, approval workflow для отзывов, unit economics
и ежедневный action plan для команды.
```

