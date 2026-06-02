# Чеклист публикации

Использовать перед публикацией или демонстрацией репозитория.

## 1. Проверить рабочее дерево

```powershell
git status --short
```

В репозиторий не должны попасть:

- `.env`;
- реальные токены Telegram, Notion, Google, marketplace API;
- `service-account.json`;
- приватные таблицы, выгрузки и коммерческие данные;
- generated reports из `reports/`, кроме `reports/.gitkeep`;
- локальные данные n8n из `integrations/n8n/self_host/n8n_data/`.

## 2. Запустить проверки

```powershell
$env:PYTHONPATH = ".\src"
python -m unittest discover -s tests
.\scripts\preflight.ps1
```

Ожидаемый результат:

```text
35 tests OK
Финальная проверка пройдена.
```

## 3. Проверить публичные материалы

Открыть:

- `README.md`;
- `docs/case_study.md`;
- `docs/architecture.md`;
- `docs/capability_matrix.md`;
- `docs/demo_walkthrough.md`;
- `docs/risk_register.md`;
- `docs/project_status_summary.md`.

Проверить:

- все формулировки нейтральные;
- не заявлено подключение production API без реальных credentials;
- ограничения описаны прямо;
- ссылки в README ведут на существующие файлы;
- screenshots в `docs/assets/` отображаются.

## 4. Проверить демо-артефакты

Сгенерировать отчеты:

```powershell
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli run-all --data-dir .\data\sample --out-dir .\reports
```

Открыть:

- `reports/executive_summary.md`;
- `reports/action_plan.md`;
- `reports/telegram_digest.txt`;
- `reports/ads_dashboard.html`;
- `reports/ads_decision_audit.csv`.

## 5. Проверить live-контур

Если есть локальные токены:

```powershell
$env:TELEGRAM_BOT_TOKEN = "..."
$env:TELEGRAM_CHAT_ID = "..."
$env:NOTION_TOKEN = "..."
$env:NOTION_DATABASE_ID = "..."
.\scripts\live_demo.ps1
```

Если токенов нет, достаточно показать dry-run отчеты и n8n workflow template.

## 6. Финальная проверка ссылок

```powershell
rg -n "docs/" README.md docs
```

Все ссылки в README и документах должны указывать на существующие файлы.
