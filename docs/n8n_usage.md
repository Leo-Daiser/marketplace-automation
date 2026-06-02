# Использование n8n

## Цель

Шаблоны в `integrations/n8n/` нужны как демонстрация того, как MVP переносится в low-code среду.

## Как использовать

1. Поднять локально Python API или запускать CLI по расписанию.
2. Импортировать workflow JSON в n8n.
3. Заменить placeholder credentials:
   - Google Sheets OAuth/service account;
   - Telegram bot token;
   - Notion token;
   - HTTP endpoint Python API.
4. Проверить workflow на sample-таблицах.
5. После проверки подключить реальные таблицы клиента.

Импорт и проверка workflow описаны в `docs/n8n_import_validation.md`.

Для демо без Google Cloud используй:

```text
integrations/n8n/no_cloud_marketplace_digest.json
```

Он читает Google Sheets через публичные CSV-ссылки и вызывает локальный Python API.

## Важное ограничение

Для БАДов нельзя генерировать медицинские обещания в ответах на отзывы. Ответы должны:

- благодарить за обратную связь;
- уточнять детали проблемы;
- предлагать обратиться к врачу при индивидуальной реакции;
- не обещать лечение, диагноз, гарантированный эффект.
