# Сценарий демонстрации

## Цель

Показать проект как operator-facing систему автоматизации, а не набор отдельных scripts.

Демо отвечает на четыре вопроса:

1. Какие кампании остановить, ограничить или масштабировать?
2. Какие отзывы требуют manual approval или support escalation?
3. Какие конкурентные gaps превратить в SEO/content/unit-economics tasks?
4. Что команде делать сегодня?

## 1. Запуск полного сценария

```powershell
cd "C:\Users\WORK\Documents\Work Projects\iqbiq-marketplace-automation-portfolio"
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli run-all --data-dir .\data\sample --out-dir .\reports
```

Ожидаемые generated files:

```text
reports/ads_dashboard.html
reports/ads_campaign_report.csv
reports/review_replies.csv
reports/support_tickets.csv
reports/competitor_opportunities.csv
reports/seo_content_tasks.csv
reports/executive_summary.md
reports/action_plan.md
reports/telegram_digest.txt
```

## 2. Открыть executive summary

Открыть:

```text
reports/executive_summary.md
```

Что показывает:

- spend/revenue/ДРР на уровне бизнеса;
- число рисковых кампаний;
- число обращений по отзывам;
- число сильных competitor opportunities;
- короткую управленческую интерпретацию.

Пример сигнала из sample data:

```text
Общий ДРР выше цели, несколько кампаний требуют действий оператора,
ответы на отзывы требуют approval, а competitor gaps обосновывают SEO/content tasks.
```

## 3. Открыть consolidated action plan

Открыть:

```text
reports/action_plan.md
```

Что показывает:

- единый prioritized operator handoff по рекламе, отзывам и конкурентам;
- owners: performance, support, SEO/content;
- evidence для каждого действия;
- next check timing.

Это самый сильный portfolio artifact: он показывает автоматизацию, которая превращает raw marketplace data в работу для команды.

## 4. Открыть ads dashboard

Открыть:

```text
reports/ads_dashboard.html
```

Что показывает:

- HTML dashboard без внешних сервисов;
- CTR, CPC, CR, ДРР, ROAS и gross profit;
- unit economics fields: break-even DRR и target DRR per SKU/marketplace;
- `profit_status`, `risk_level`, `next_step`;
- campaign-level actions: `scale_budget`, `cap_spend_low_stock`, `reduce_bid_and_check_unit_economics`.

## 5. Проверить review workflow

Открыть:

```text
reports/review_replies.csv
reports/support_tickets.csv
reports/review_digest.md
```

Что показывает:

- review topic classification;
- support escalation;
- manual approval status;
- nutraceutical compliance flags;
- отсутствие auto-publishing рискованных health-related replies.

## 6. Проверить competitor workflow

Открыть:

```text
reports/competitor_opportunities.csv
reports/seo_content_tasks.csv
reports/competitor_digest.md
```

Что показывает:

- price index;
- rating gap;
- review gap;
- ad pressure;
- SEO/content backlog с owner, impact и due date guidance.

## 7. Объяснить n8n integration

Открыть:

```text
integrations/n8n/ads_report_to_telegram.json
integrations/n8n/review_agent_to_support.json
integrations/n8n/competitor_monitor_to_notion.json
```

Объяснение:

- n8n читает Google Sheets или webhook payloads;
- n8n вызывает optional FastAPI boundary;
- Python core производит deterministic decisions;
- n8n отправляет Telegram digests, добавляет support tickets или создает Notion tasks.

## 8. Quality gate

Перед публикацией portfolio link запустить:

```powershell
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli run-all --data-dir .\data\sample --out-dir .\reports
python -m unittest discover -s tests
python -m compileall -q .\src .\tests
```

Ожидаемый результат:

```text
35 tests OK
```

## Рассказ для собеседования

Короткая версия:

```text
Я собрал воспроизводимый suite автоматизации маркетплейсов для рекламы, отзывов и competitor SEO.
Core logic детерминирована и покрыта тестами, а n8n/Sheets/Telegram/Notion используются как integration boundaries.
Самый сильный output — consolidated action plan: он превращает raw marketplace tables в приоритетные tasks для performance, support и SEO/content owners.
```

Техническая версия:

```text
Архитектура разделяет ingestion contracts, business decisions, compliance policies, output rendering и integration adapters.
CSV используется как Google Sheets-compatible contract для demo.
Те же use cases вызываются через CLI или optional FastAPI endpoints, поэтому n8n может оркестрировать workflow без дублирования business logic.
```
