# 01 Помощник по рекламным кампаниям

## Задача

Автоматизировать ежедневную отчетность по рекламе WB/Ozon и быстро находить кампании, где нужно менять ставки, бюджет или карточку товара.

## Что считает

- CTR;
- CPC;
- конверсию;
- ДРР;
- ROAS;
- валовую прибыль после рекламы;
- рекомендации по кампаниям.

## Вход

`data/sample/ads_daily.csv`

## Выход

- `reports/ads_campaign_report.csv`
- `reports/ads_report.md`
- `reports/ads_dashboard.html`

## Запуск

```powershell
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli ads-report --input .\data\sample\ads_daily.csv --out-dir .\reports --target-drr 0.18
```

## Критерии готовности

- отчет генерируется без ручной обработки таблиц;
- рискованные кампании видны отдельно;
- рекомендации объясняют причину действия;
- результат можно отправить в Telegram или Google Sheets.
