# Реестр рисков

## Цель

Документ фиксирует известные риски и production-readiness gaps. Он нужен для ревью портфолио и планирования реального rollout с marketplace, Google Sheets, n8n, Telegram и Notion integrations.

## Сводка

| Область | Текущий риск | Текущее состояние |
|---|---|---|
| Качество данных | Средний | Schema validation и data quality report реализованы, но реальные выгрузки требуют client-specific проверок |
| Marketplace APIs | Высокий | Adapter boundaries есть; реальный доступ WB/Ozon требует seller account tokens |
| Credentials и secrets | Высокий | `.env.example` описывает значения; реальные secrets нельзя коммитить |
| Review compliance | Средний | Deterministic flags и manual approval есть; legal/tone-of-voice rules требуют бизнес-согласования |
| Точность решений | Средний | Unit economics и audit trail есть; thresholds нужно калибровать на реальной марже и конверсии |
| Operations | Средний | Reports и action plan есть; scheduling, ownership и escalation rules настраиваются под команду |
| Observability | Средний | Local preflight есть; production logging, alerting и failed-run handling не реализованы |

## Детальные риски

| ID | Риск | Влияние | Mitigation | Статус |
|---|---|---|---|---|
| R-001 | Synthetic sample data может не совпасть с реальными marketplace exports | Реальные таблицы могут иметь лишние колонки, пропуски или другие названия | Провести dry-run mapping на anonymized real exports перед production | Open |
| R-002 | Версии WB/Ozon API endpoints могут отличаться от assumptions adapter | Импорт рекламы может упасть или неверно нормализовать поля | Подтвердить актуальные docs в кабинете клиента и добавить endpoint-specific fixtures | Open |
| R-011 | Реальные WB/Ozon tokens нельзя получить без owner/admin seller account | Live marketplace demo невозможно показать только на публичных данных | Для портфолио использовать synthetic data; read-only seller tokens запрашивать только на rollout | Open |
| R-003 | API rate limits и временные 429/5xx не обработаны в production mode | Scheduled jobs могут падать или давать неполные отчеты | Добавить retry/backoff, per-marketplace rate limits и failed-run notifications | Open |
| R-004 | Credentials могут утечь при коммите service account files или tokens | Security incident и exposure репозитория | Использовать `.env`, secret manager или CI secrets; держать `service-account.json` вне Git | Open |
| R-005 | Ответы на отзывы в категории БАДов могут создать unsafe claims | Compliance и reputation risk | Оставить manual approval workflow; запретить auto-publishing до согласования legal/tone rules | Partially mitigated |
| R-006 | Advertising thresholds могут быть неверными для реальной SKU economics | Неверные bid/budget recommendations | Калибровать target DRR, break-even DRR и margin assumptions на реальных finance data | Partially mitigated |
| R-007 | Action plan может перегрузить операторов большим числом P0/P1 | Команда начнет игнорировать automation output | Добавить owner capacity limits и escalation rules после наблюдения реального использования | Open |
| R-008 | Concurrent edits в Google Sheets могут перезаписать ручные изменения | Потеря manual edits или stale outputs | Разделить input/output tabs, timestamps и append-only audit tabs для критичных outputs | Open |
| R-009 | n8n/Telegram/Notion могут уведомить команду по unreviewed drafts | Путаница или небезопасные operational decisions | Разделить dry-run и production channels; требовать approval перед delivery | Open |
| R-010 | Local preflight не заменяет production monitoring | Failures могут остаться незамеченными после deployment | Добавить scheduled health checks, structured logs и alerting для failed runs | Open |

## Чеклист безопасной публикации

Перед публикацией репозитория:

- `.env` не закоммичен;
- `service-account.json` не закоммичен;
- реальные WB/Ozon exports не закоммичены;
- приватные client data не попали в reports;
- generated files либо осознанно включены, либо исключены `.gitignore`;
- README и docs не утверждают live production integration там, где ее нет.

## Чеклист production readiness

Перед реальным rollout:

1. Подтвердить source tables и версии API endpoints.
2. Прогнать pipeline на anonymized real exports.
3. Настроить ДРР, margin и inventory thresholds с business owner.
4. Утвердить review reply templates и compliance rules.
5. Добавить retries, rate limits и secret handling для external APIs.
6. Включить dry-run notifications перед production Telegram/Notion delivery.
7. Минимум один business cycle отслеживать false positives и missed risks.

## Честный текущий статус

Проект готов как portfolio case и technical prototype. Это еще не production deployment. Детерминированное ядро, tests, data contracts и reports реализованы; реальный rollout требует client credentials, подтверждения endpoints, калибровки и operational monitoring.
