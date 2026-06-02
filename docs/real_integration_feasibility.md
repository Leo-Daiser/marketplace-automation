# Реалистичность живых интеграций

## Цель

Документ объясняет, какие интеграции можно показать с реальными токенами без дополнительных платных сервисов, а какие требуют реального seller account маркетплейса.

## Короткий ответ

| Интеграция | Можно показать без платной подписки? | Что все равно нужно |
|---|---:|---|
| Google Sheets | Да | Google Cloud project и Sheets API либо no-cloud вариант через public CSV/Apps Script |
| Telegram Bot API | Да | Telegram account и bot token из BotFather |
| Notion internal integration | Да | Notion workspace, internal integration token и shared database/page |
| n8n | Да, если self-hosted локально | Docker/npm setup или собственный сервер; cloud hosting стоит денег при always-on доступе |
| Ozon Seller API | Частично | Реальный Ozon seller account и Seller API key + Client ID |
| Ozon Performance API | Частично | Ozon Performance account/key; реальные ad data требуют рекламной активности |
| Wildberries API | Частично | Реальный WB seller account owner token с нужными scopes |

## Marketplace tokens

### Ozon

Официальная документация Ozon описывает Seller API через API key и Client ID, которые создаются в настройках seller account и передаются в Seller API requests.

Ozon Performance API отдельный. Он нужен для автоматизации рекламного кабинета: статистика рекламных каналов, добавление товаров в рекламу и оптимизация ставок. Performance API key создается через Settings -> API keys -> Performance API; лимит указан до 100 000 requests per day.

Вывод:

- Сам token не выглядит как отдельный платный API-продукт.
- Реальный доступ требует Ozon seller account.
- Реальная рекламная аналитика требует Ozon Performance account и кампаний со статистикой.
- Для портфолио корректно показывать adapters, fake-transport tests и synthetic data, пока клиент не дал credentials.

Источники:

- https://docs.ozon.com/global/api/intro/
- https://docs.ozon.com/global/api/perfomance-api/

### Wildberries

Официальная документация WB API описывает API для продавцов и автоматизации процессов магазина. WB FAQ указывает, что token создается в seller account через Profile -> API Integrations, owner может создать token, scopes выбираются отдельно, до 20 tokens на store.

Вывод:

- Сам token не выглядит как отдельный платный API-продукт.
- Реальный доступ требует seller account и owner/admin permission.
- Regular token expires after 180 days, поэтому production rollout должен учитывать token rotation или OAuth.
- Для портфолио synthetic data + adapter boundaries — честный вариант без seller cabinet.

Источники:

- https://dev.wildberries.ru/en/docs/openapi/api-information?locale=ru
- https://dev.wildberries.ru/en/faq

## Workflow и productivity integrations

### Google Sheets

Google Sheets API доступен без отдельной оплаты для стандартного использования, но с quotas. Официальные лимиты включают 300 read/write requests per minute per project и 60 read/write requests per minute per user per project. В проекте уже есть Google Sheets adapter и CLI pull/push commands.

Источник:

- https://developers.google.com/workspace/sheets/api/limits

### Telegram

Telegram Bot API позволяет делать программы, которые используют Telegram messages как interface. Telegram APIs доступны free of charge. Для демо нужны bot token и target chat/channel.

Источник:

- https://core.telegram.org/api

### Notion

Notion поддерживает internal API connections. Нужно создать internal connection в workspace settings и получить token. Для n8n page/database также нужно share with integration.

Источники:

- https://www.notion.com/en-gb/help/create-integrations-with-the-notion-api
- https://docs.n8n.io/integrations/builtin/credentials/notion/

### n8n

n8n имеет free self-hosted community edition. n8n Cloud платный после trial, но local/self-hosted demo можно сделать без оплаты n8n. Компромисс operational: self-hosting требует setup, security и maintenance.

Источник:

- https://docs.n8n.io/choose-n8n/

## Рекомендуемая demo strategy

Для interview/demo:

1. WB/Ozon оставить на synthetic data и объяснить, что реальные marketplace tokens требуют seller cabinet.
2. Показать real Telegram Bot API через dry-run digest, если есть bot token.
3. Показать Google Sheets через demo spreadsheet: service account или no-cloud public CSV/Apps Script.
4. Показать Notion task payloads через personal/demo workspace, если есть Notion internal token.
5. n8n запускать локально, если есть время на setup; иначе показывать importable workflow templates и API payloads.

## Честная формулировка для собеседования

```text
Я намеренно не добавлял WB/Ozon production credentials в портфолио.
По официальной документации реальные tokens создаются из seller accounts, поэтому без seller cabinet клиента я не могу честно показать live marketplace data.
Зато я показываю production boundary: adapters, table contracts, fake-transport tests, Google Sheets/Telegram/Notion payloads, n8n workflows и preflighted deterministic core.
Если команда даст read-only seller tokens, rollout path понятен: dry-run import, schema validation, decision audit, затем controlled delivery в Sheets/Telegram/Notion.
```

## Что сделает проект полностью подключенным

Минимальные no-cost demo tokens:

- Telegram bot token.
- Google service account JSON for a demo spreadsheet.
- Notion internal integration token for a demo page/database.

Marketplace production tokens:

- Ozon Seller API Client ID and API key.
- Ozon Performance API Client ID/secret if ad statistics are required.
- Wildberries API token with read-only analytics/advertising scopes.

Не коммитить эти токены. Использовать `.env`, локальный secret-файл или CI secrets.
