# Marketplace API adapters

## Цель

Проект использует CSV/Google Sheets для воспроизводимого демо, но реальная WB/Ozon integration должна быть изолирована за adapters.

Реализованный файл:

```text
src/marketplace_automation/adapters/marketplace_api.py
```

## Что реализовано

- `WildberriesAdsClient`
- `OzonAdsClient`
- request headers/date payloads;
- normalization к общему `ads_daily` contract;
- fake-transport tests без real API keys.

## Нормализованный output

Оба adapters возвращают rows, совместимые с `ads_daily`:

```text
date
marketplace
campaign_id
campaign_name
sku
product_name
impressions
clicks
spend_rub
orders
revenue_rub
margin_rate
stock_units
ad_position
bid_rub
```

## Пример использования

```python
from marketplace_automation.adapters.marketplace_api import (
    OzonAdsClient,
    OzonAdsConfig,
    WildberriesAdsClient,
    WildberriesAdsConfig,
)

wb = WildberriesAdsClient(WildberriesAdsConfig(api_token="WB_API_TOKEN"))
ozon = OzonAdsClient(OzonAdsConfig(client_id="OZON_CLIENT_ID", api_key="OZON_API_KEY"))

rows = []
rows.extend(wb.fetch_ads_daily("2026-05-01", "2026-05-31"))
rows.extend(ozon.fetch_ads_daily("2026-05-01", "2026-05-31"))
```

## Что еще нужно для production

- Подтвердить точные WB/Ozon endpoint versions в client environment.
- Добавить pagination, если endpoint возвращает paginated data.
- Добавить retry/backoff для 429/5xx.
- Добавить request logging с redacted secrets.
- Добавить per-marketplace rate limits.
- Сохранять raw API responses отдельно от normalized tables для audit.
