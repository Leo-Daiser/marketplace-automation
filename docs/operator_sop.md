# Регламент оператора

## Цель

SOP объясняет, как marketplace operations team должна использовать `action_plan.md` и связанные отчеты в ежедневном workflow.

## Роли

| Роль | Зона ответственности |
|---|---|
| Performance | ДРР, CPC, conversion, bid/budget decisions и stock-aware scaling |
| Support | Review replies, support tickets, delivery/package issues и manual approval cases |
| SEO/content | Competitor opportunities, keyword gaps и content backlog |
| Product/quality | Quality/rating gaps и possible product feedback loops |
| Owner/lead | P0 escalation, blocked scaling decisions и финальная проверка daily digest |

## Ежедневный workflow

1. Запустить автоматизацию.

```powershell
.\scripts\preflight.ps1
```

2. Открыть executive summary.

```text
reports/executive_summary.md
```

Использовать, чтобы понять статус дня: normal, risky или blocked.

3. Открыть consolidated action plan.

```text
reports/action_plan.md
```

Идти сверху вниз по priority.

4. Сначала разобрать P0 actions.

P0 означает, что scaling заблокирован до ручной проверки. Типовые причины:

- negative gross profit after ads;
- экстремально высокий ДРР;
- review compliance risk;
- delivery/package escalation;
- сильный competitor gap по high-priority SKU.

5. Назначить owners.

Каждая строка уже содержит:

- `area`;
- `owner`;
- `severity`;
- `confidence`;
- `blocks_scaling`;
- `deadline`;
- `evidence`;
- `next_check`.

6. Обновить рабочую доску.

Если используется Google Sheets:

- input tabs держать как source data;
- output tabs использовать для generated results;
- не редактировать generated output rows вручную, кроме отдельной manual tracking column.

Если используется Notion:

- создавать tasks из `seo_content_tasks`;
- сохранять generated evidence в body задачи;
- owner и deadline назначать вручную, если team capacity отличается от generated suggestion.

## Правила принятия решений

| Condition | Action |
|---|---|
| `blocks_scaling = yes` | Do not increase budget or bid before review |
| `priority = P0` | Same-day owner decision required |
| `priority = P1` | Handle during current workday |
| `priority = P2` | Add to backlog unless repeated |
| `confidence = low` | Verify source data before acting |
| Review has compliance flags | Keep reply in manual approval mode |

## Правила ответов на отзывы для БАДов

Не публиковать review replies автоматически для health/nutraceutical products.

Разрешено:

- поблагодарить клиента;
- попросить детали;
- предложить обратиться в поддержку маркетплейса по delivery/package issues;
- предложить консультацию специалиста/врача при индивидуальной реакции.

Запрещено:

- medical promises;
- diagnosis;
- guaranteed effect;
- treatment claims;
- unsafe dosage advice.

## Закрытие дня

В конце дня:

1. Посчитать закрытые P0/P1 actions.
2. Проверить, снята ли blocked scaling проблема.
3. Зафиксировать false positives или bad recommendations.
4. Менять thresholds только после повторяющихся evidence.
5. Сохранять raw inputs и generated outputs для audit.

## Формулировка для демо

```text
Автоматизация не просто генерирует reports.
Она задает daily operating procedure: input tables, quality checks, explainable decisions,
action ownership, escalation rules и четкую no-auto-publish policy для nutraceutical review replies.
```
