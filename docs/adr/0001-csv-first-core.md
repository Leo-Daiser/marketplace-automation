# ADR 0001: CSV-first deterministic core

## Статус

Принято.

## Контекст

Проект должен демонстрировать автоматизацию маркетплейсов, Google Sheets, n8n, AI-ready services и team workflows без доступа к real client tokens, private sales data и marketplace API credentials.

## Решение

Сначала строить core use cases вокруг documented CSV contracts. CSV напрямую соответствует Google Sheets exports и позже заменяется API adapters. Decision logic остается deterministic и covered by tests.

## Последствия

Плюсы:

- Проект запускается локально без secrets.
- Business logic тестируема.
- Google Sheets/n8n integration остается straightforward.
- Synthetic data безопасно демонстрирует edge cases.

Минусы:

- Это не доказывает direct WB/Ozon API usage.
- Real deployment все равно требует auth, pagination, retries и rate-limit handling.

## Follow-up

Добавить adapter interfaces для Google Sheets, WB и Ozon после стабилизации core use cases.
