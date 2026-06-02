# Локальный n8n self-host

## Цель

Этот сценарий запускает n8n локально для демо без n8n Cloud, без Google Cloud и без реальных кабинетов маркетплейсов.

Демо-поток:

```text
Публичные CSV-ссылки Google Sheet
  -> n8n Code / HTTP Request nodes
  -> локальный Python API
  -> Telegram digest
  -> задачи в Notion
```

## Что нужно

- Docker Desktop.
- Python API проекта на порту `8000`.
- Telegram bot token и chat ID.
- Notion internal integration token и demo database ID.

## Запуск Python API

В PowerShell:

```powershell
cd marketplace-automation
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[api]"
$env:PYTHONPATH = ".\src"
uvicorn marketplace_automation.api:app --host 0.0.0.0 --port 8000
```

Проверка:

```powershell
curl http://localhost:8000/health
```

Ожидаемый ответ:

```json
{"status":"ok"}
```

## Запуск n8n

В другом PowerShell:

```powershell
cd .\integrations\n8n\self_host
docker info
docker compose up -d
```

Открыть:

```text
http://localhost:5678
```

Если Docker Desktop установлен, но не запущен:

```powershell
Start-Process -FilePath "C:\Program Files\Docker\Docker\Docker Desktop.exe"
```

Дождаться, пока команда вернет информацию о Docker engine:

```powershell
docker info
```

Первый запуск n8n может быть долгим, потому что Docker скачивает `n8nio/n8n`.
Если `docker compose up -d` вышел по таймауту во время скачивания образа, повторить:

```powershell
docker pull n8nio/n8n:latest
docker compose up -d
```

Проверка:

```powershell
docker compose ps
docker ps -a --filter name=marketplace-n8n
```

## Остановка n8n

```powershell
cd .\integrations\n8n\self_host
docker compose down
```

## Live-демо одной командой

Из корня проекта:

```powershell
$env:TELEGRAM_BOT_TOKEN = "..."
$env:TELEGRAM_CHAT_ID = "..."
$env:NOTION_TOKEN = "..."
$env:NOTION_DATABASE_ID = "..."
.\scripts\live_demo.ps1
```

Скрипт:

- проверяет Python API;
- запускает локальный n8n через Docker Compose;
- импортирует временную локальную копию workflow с токенами из env-переменных;
- выполняет workflow `no-cloud-marketplace-digest`;
- отправляет Telegram digest;
- создает или обновляет Notion задачи по `Task ID`.

Реальные токены берутся только из переменных окружения и не записываются в файлы репозитория.

## Workflow

Главный workflow:

```text
integrations/n8n/no_cloud_marketplace_digest.json
```

Он:

- читает публичные CSV tabs из демо Google Sheet;
- вызывает локальный Python API через `http://host.docker.internal:8000`;
- отправляет дайджест в Telegram через Telegram Bot API;
- создает или обновляет задачи в Notion;
- не требует Google OAuth и Google Cloud.

В workflow-файле репозитория намеренно лежат только плейсхолдеры:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
NOTION_TOKEN
NOTION_DATABASE_ID
```

## Проверенный статус

Проверено 2026-06-02:

- Python API отвечает `{"status":"ok"}`;
- workflow JSON валиден;
- публичный Google Sheet читается в `data/google_demo`;
- n8n контейнер `marketplace-n8n` работает на `http://localhost:5678`;
- workflow импортируется в локальный n8n;
- Telegram live-send работает после `/start` в диалоге с ботом;
- Notion live task creation работает в demo database;
- deduplication работает: повторный запуск обновляет 5 задач и создает 0 дублей;
- `scripts/live_demo.ps1` проходит как one-command live demo.

Особенность n8n 2.x: CLI execution нельзя запускать одновременно с основным server-контейнером, потому что занят task broker port. Для smoke-теста скрипт временно останавливает server-контейнер, запускает workflow одноразовым compose-контейнером и затем возвращает n8n UI обратно.

## Краткое описание контура

```text
n8n здесь используется как оркестратор, а не как место для бизнес-логики.
Python отвечает за проверяемую доменную логику: метрики рекламы, unit economics, обработку отзывов, конкурентный scoring и приоритизацию действий.
n8n читает таблицы, вызывает API и доставляет результат в Telegram и Notion.
```
