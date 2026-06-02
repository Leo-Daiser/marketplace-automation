# Схема Google Sheets

Практическая схема таблиц для переноса MVP в Google Sheets/n8n.

## ads_daily

| Колонка | Тип | Значение |
|---|---:|---|
| date | date | День статистики |
| marketplace | string | `WB` или `Ozon` |
| campaign_id | string | ID рекламной кампании |
| campaign_name | string | Название кампании |
| sku | string | SKU товара |
| product_name | string | Название товара |
| impressions | int | Показы |
| clicks | int | Клики |
| spend_rub | float | Расход на рекламу |
| orders | int | Заказы |
| revenue_rub | float | Выручка |
| margin_rate | float | Валовая маржа до рекламы |
| stock_units | int | Остатки |
| ad_position | float | Средняя рекламная позиция |
| bid_rub | float | Ставка |

## reviews

| Колонка | Тип | Значение |
|---|---:|---|
| review_id | string | ID отзыва |
| date | date | Дата |
| marketplace | string | Маркетплейс |
| sku | string | SKU |
| rating | int | Оценка 1-5 |
| text | string | Текст отзыва |
| has_photo | bool | Есть ли фото |
| order_id | string | ID заказа |

## competitors

| Колонка | Тип | Значение |
|---|---:|---|
| date | date | Дата сбора |
| marketplace | string | Маркетплейс |
| keyword | string | Поисковая фраза |
| competitor_brand | string | Бренд конкурента |
| product_name | string | Название товара |
| sku | string | SKU/артикул конкурента |
| price_rub | float | Цена |
| rating | float | Рейтинг |
| reviews_count | int | Количество отзывов |
| organic_position | int | Органическая позиция |
| ad_position | int | Рекламная позиция, 0 если нет рекламы |
| stock_status | string | `in_stock`, `low_stock`, `out_of_stock` |
| title | string | Заголовок карточки |
| bullets | string | Ключевые тезисы карточки |

## Выходные листы

Рекомендуемые листы для результата:

- `ads_campaign_report`
- `review_replies`
- `support_tickets`
- `competitor_opportunities`
- `seo_content_tasks`

## unit_economics

| Колонка | Тип | Значение |
|---|---:|---|
| sku | string | SKU товара |
| product_name | string | Название товара |
| marketplace | string | `WB` или `Ozon` |
| price_rub | float | Цена продажи |
| cogs_rub | float | Себестоимость товара |
| marketplace_fee_rate | float | Комиссия маркетплейса, доля от цены |
| logistics_rub | float | Логистика на заказ |
| storage_rub | float | Оценка хранения/операционных затрат на заказ |
| return_rate | float | Ожидаемая доля возвратов/невыкупов |
| tax_rate | float | Налоговая ставка от цены |
| target_profit_rate | float | Целевая прибыль после рекламы, доля от цены |

Расчетные поля:

- `contribution_margin_before_ads_rub`
- `contribution_margin_rate`
- `break_even_drr`
- `target_drr`
