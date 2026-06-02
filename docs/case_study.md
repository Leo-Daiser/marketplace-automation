# Кейс портфолио

## Контекст

Проект моделирует операционный workflow для роста e-commerce бренда на маркетплейсах. Задача не только в расчете рекламных метрик, а в превращении разрозненных таблиц в ежедневные решения для performance, support и SEO/content.

Кейс намеренно воспроизводится на синтетических данных. Реальные WB/Ozon credentials, доступы Google Sheets и production-workflow n8n считаются внешними интеграциями, а бизнес-логика остается детерминированной и тестируемой.

## Бизнес-проблема

У marketplace-команд обычно повторяются одни и те же проблемы:

- кампании оцениваются по CTR, CPC и ДРР без достаточного контекста unit economics;
- ответы на отзывы могут создавать compliance-риск в категории health/nutraceutical;
- мониторинг конкурентов дает наблюдения, но не превращает их в приоритетные SEO/content задачи;
- ежедневная отчетность часто заканчивается дашбордом, а не конкретными next actions.

Целевой workflow:

1. Прочитать таблицы рекламы, отзывов, конкурентов, keyword plan и unit economics.
2. Проверить контракты таблиц и подозрительные значения.
3. Рассчитать метрики, риски и рекомендуемые действия.
4. Сгенерировать отчеты, дайджесты и task payloads.
5. Собрать единый action plan для операторов.

## Реализованное решение

В репозитории три связанных кейса автоматизации:

| Область | Что реализовано | Основной результат |
|---|---|---|
| Ads Performance Copilot | CTR, CPC, CR, ДРР, ROAS, прибыль после рекламы, риск, confidence и next step | `reports/ads_campaign_report.csv`, `reports/ads_decision_audit.csv`, `reports/ads_dashboard.html` |
| Review Response Agent | Классификация отзывов, безопасные drafts, manual approval и support tickets | `reports/review_replies.csv`, `reports/support_tickets.csv`, `reports/review_digest.md` |
| Мониторинг конкурентов и SEO | Разрывы по цене, рейтингу, отзывам и рекламному давлению, затем SEO/content задачи | `reports/competitor_opportunities.csv`, `reports/seo_content_tasks.csv` |

Portfolio orchestrator объединяет три области в:

- `reports/executive_summary.md` — управленческий статус;
- `reports/action_plan.md` — ежедневный handoff для оператора;
- `reports/telegram_digest.txt` — компактный дайджест автоматизации.

## Архитектурные решения

### Сначала детерминированное ядро

Логика реализована в Python, а не спрятана внутри no-code сценария. Это делает решения проверяемыми: ДРР-пороги, margin risks, compliance flags и competitor scores можно валидировать без внешних сервисов.

### Контракты совместимы с CSV и Google Sheets

Демо начинается с CSV, потому что такой запуск воспроизводим из чистого checkout и напрямую соответствует листам Google Sheets. Те же table contracts используются API adapters и n8n workflow.

### Integration boundaries вместо ложных production claims

В проекте есть Google Sheets, Telegram, Notion, API и marketplace adapter boundaries, но нет утверждения, что подключены production-токены маркетплейсов. Это честнее и лучше выглядит для controlled rollout.

### Отчеты как операционные артефакты

Самый сильный output — не график, а `reports/action_plan.md`: он назначает priority, severity, confidence, owner, deadline и статус блокировки масштабирования.

## Пример результата на sample-данных

Текущий sample-run дает:

| Метрика | Результат |
|---|---|
| Целевой ДРР | 18.0% |
| Расход на рекламу | 251 920 руб. |
| Выручка рекламы | 860 330 руб. |
| Общий ДРР | 29.3% |
| Прибыль после рекламы | -2 365 руб. |
| Рисковые кампании | 4 |
| Обращения по отзывам | 5 |
| Срочные отзывы | 4 |
| Сильные конкурентные opportunities | 4 |
| Создано SEO/content задач | 5 |

Интерпретация: кабинет нельзя масштабировать вслепую. Несколько кампаний убыточны или плохо конвертируют, отзывы требуют ручного approval, а конкурентные разрывы достаточны для SEO/content задач в текущем sprint.

## Качество и укрепление

Проект усилен дальше базового MVP:

- schema validation блокирует отсутствующие и пустые обязательные колонки;
- data quality report показывает пустые значения и подозрительные метрики;
- unit economics участвует в рекламных решениях;
- рекомендации по рекламе имеют decision audit trail;
- ответы на отзывы содержат approval и compliance flags;
- edge-case сценарии лежат в `data/scenarios/risk_edge`;
- regression snapshot tests защищают структуру generated reports;
- preflight script запускает генерацию отчетов, tests, compile check и JSON validation.

Текущий quality gate:

```powershell
cd marketplace-automation
.\scripts\preflight.ps1
```

Ожидаемый результат:

```text
Финальная проверка пройдена.
35 tests OK.
```

## План production rollout

Следующий production-этап:

1. Подтвердить реальные WB/Ozon source tables и версии API endpoints.
2. Сопоставить текущие CSV contracts с реальными листами Google Sheets.
3. Добавить credentials через environment variables или secret manager.
4. Несколько дней прогнать pipeline в dry-run mode.
5. Проверить false positives в рекламных решениях, review compliance flags и competitor tasks.
6. Только после этого включать автоматическую доставку в Telegram/Notion/n8n для команды.

## Известные ограничения

- Данные синтетические и не являются реальным клиентским датасетом.
- Marketplace API adapters — это integration boundaries, а не live production clients.
- Ответы на отзывы используют deterministic templates; LLM provider можно добавить позже после согласования tone of voice и юридических ограничений.
- Дополнительные screenshots можно сгенерировать на машине с доступным browser executable.

## Почему кейс полезен

Кейс закрывает типовые задачи marketplace operations:

- аналитика рекламы маркетплейсов;
- решения по ДРР, ROAS, конверсии и прибыльности;
- workflow ответов на отзывы с support escalation;
- конкурентный и SEO/content мониторинг;
- Google Sheets, n8n, Telegram, Notion и API integration boundaries;
- documented quality gates и rollout limitations.

Проект не позиционируется как готовый production deployment. Это сильный технический prototype, который показывает, как production-система должна быть структурирована, протестирована и безопасно выведена в работу.
