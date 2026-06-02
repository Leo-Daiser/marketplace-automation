# Гайд публикации на GitHub

## Цель

Опубликовать репозиторий как чистый портфолио-кейс без утечки secrets и generated noise.

## 1. Запустить quality gate

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

Ожидаемый результат:

```text
35 tests OK
```

## 2. Проверить generated files

Сгенерированные отчеты игнорируются, кроме `reports/.gitkeep`.

Не добавлять принудительно:

```text
reports/*.csv
reports/*.json
reports/*.md
reports/*.html
reports/*.txt
```

Они воспроизводимы и не должны коммититься, кроме осознанно подготовленного demo snapshot в `docs/assets`.

## 3. Проверить secrets

Запустить:

```powershell
git status --short
```

Не коммитить:

```text
.env
.env.*
service-account.json
data/raw/
data/private/
*.xlsx
*.xls
*.sqlite
*.db
```

## 4. Описание репозитория

```text
Портфолио автоматизации маркетплейсов: аналитика рекламы WB/Ozon, review-response agent, competitor SEO monitor, Google Sheets/n8n/Telegram/Notion integrations.
```

## 5. Короткий tagline README

```text
Детерминированное Python-ядро + Google Sheets/n8n integration layer для marketplace growth operations.
```

## 6. Первый commit message

```text
Build marketplace automation portfolio
```

## 7. Git commands

Запускать только после ручной проверки файлов:

```powershell
git add iqbiq-marketplace-automation-portfolio
git status --short
git commit -m "Build marketplace automation portfolio MVP"
```

Если проект лежит внутри родительского repo, лучше перенести его в отдельный GitHub repository перед публикацией.

## 8. Что отправить в отклике

Использовать:

- GitHub repository URL;
- `README.md`;
- `docs/demo_walkthrough.md`;
- `docs/application_pitch.md`;
- короткое видео по `docs/demo_video_script.md`, если успеешь записать.

## 9. Честная формулировка ограничения

```text
Проект использует synthetic CSV data для безопасной воспроизводимости.
Реальный deployment требует client credentials, подтверждения WB/Ozon endpoint versions,
retry/rate-limit policies и настройки approval workflows в инструментах клиента.
```

