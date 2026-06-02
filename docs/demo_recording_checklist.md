# Чеклист записи демо

## Цель

Записать короткое портфолио-демо, которое показывает, что проект не является набором разрозненных скриптов:

```text
Google Sheet -> n8n -> Python API -> Telegram digest -> Notion tasks
```

Рекомендуемая длина: 2-4 минуты.

## Перед записью

- Перевыпустить demo-токены, если они где-то светились.
- Не показывать `.env`, временный workflow JSON, password manager, n8n credential details и историю команд с токенами.
- Запустить Docker Desktop.
- Проверить Python API:

```powershell
curl http://localhost:8000/health
```

- Открыть n8n:

```text
http://localhost:5678/workflow/no-cloud-marketplace-digest
```

- Открыть demo Google Sheet и Notion database.

## Сценарий записи

1. Показать README и объяснить кейс одной фразой:

```text
Это портфолио-кейс автоматизации операций маркетплейса: реклама, отзывы и конкурентный SEO.
```

2. Показать входные вкладки Google Sheet:

```text
ads_daily, reviews, competitors, our_products, keyword_plan, unit_economics
```

3. Показать n8n workflow:

```text
Ручной запуск -> Python API -> Telegram -> Notion
```

4. Запустить live-демо:

```powershell
.\scripts\live_demo.ps1
```

5. Показать результат в терминале:

```text
Workflow выполнен:        True
Telegram отправлен:       True
Notion обновил без дублей: True
```

6. Показать Telegram digest.

7. Показать Notion database с задачами.

8. Показать один сгенерированный отчет:

```text
reports/action_plan.md
reports/ads_dashboard.html
```

9. Завершить архитектурной мыслью:

```text
n8n оркестрирует процесс. Python отвечает за проверяемую бизнес-логику и тесты.
```

## Что нельзя утверждать

- Не заявлять, что подключен production API маркетплейсов, если реальные кабинеты продавца не подключены.
- Не заявлять, что ответы на отзывы по health-категориям можно публиковать без ручного согласования.
- Не заявлять, что это уже production deployment.

## Корректная сильная формулировка

```text
Это production-like портфолио-демо с проверяемой доменной логикой, live no-code orchestration и реальными side effects в Telegram и Notion.
```
