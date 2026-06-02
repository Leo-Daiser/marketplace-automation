# 03 Мониторинг конкурентов и SEO

## Задача

Автоматизировать сбор и анализ конкурентов по приоритетным запросам: цена, рейтинг, отзывы, рекламное давление и SEO/content разрывы.

## Что делает

- агрегирует конкурентов по ключевой фразе;
- считает ценовой индекс;
- считает разрыв по отзывам и рейтингу;
- оценивает рекламное давление;
- формирует SEO/content задачи;
- готовит дайджест для команды.

## Вход

- `data/sample/competitors.csv`
- `data/sample/our_products.csv`
- `data/sample/keyword_plan.csv`

## Выход

- `reports/competitor_opportunities.csv`
- `reports/seo_content_tasks.csv`
- `reports/competitor_digest.md`

## Запуск

```powershell
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli competitor-monitor --competitors .\data\sample\competitors.csv --our-products .\data\sample\our_products.csv --keyword-plan .\data\sample\keyword_plan.csv --out-dir .\reports
```

## Критерии готовности

- видно, где карточка проигрывает конкурентам;
- SEO-задачи формируются не вручную, а по данным;
- результат можно передать в Notion/Sheets как backlog.
