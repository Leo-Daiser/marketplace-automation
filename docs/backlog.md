# Бэклог

## Текущий sprint

Цель: довести проект до уровня сильного portfolio case, а не набора отдельных scripts.

Статус: основные задачи закрыты.

## Закрытые блоки

| Блок | Статус | Что сделано |
|---|---|---|
| Архитектура | готово | Описаны границы системы, adapters, API boundary, n8n orchestration и quality gates |
| Рекламная аналитика | готово | CTR, CPC, CR, ДРР, ROAS, прибыль после рекламы, risk level, confidence и audit trail |
| Unit economics | готово | Себестоимость, комиссия, логистика, хранение, возвраты, налог, break-even ДРР |
| Review agent | готово | Классификация отзывов, safe reply drafts, support tickets, manual approval и compliance flags |
| Competitor monitor | готово | Price/rating/review gaps, ad pressure, SEO/content tasks, owner и due date |
| Google Sheets | готово | Service-account adapter, no-cloud public CSV reader, Apps Script writer и CLI sync |
| Telegram | готово | Formatter и live-send через локальный n8n workflow |
| Notion | готово | Task payload builder, live task upsert и deduplication по `Task ID` |
| n8n | готово | Self-host setup, importable workflows, no-cloud live workflow и one-command demo |
| Тесты | готово | 35 unit tests, regression snapshots, scenario coverage, preflight script |
| Документация | готово | README, case study, risk register, publication checklist, publication guide, demo checklist |
| Repository cleanup | готово | `.gitignore`, generated artifacts, secret scan и русские user-facing тексты проверены |

## Что осталось перед GitHub

| Приоритет | Задача | Зачем |
|---|---|---|
| P0 | Перенести проект в отдельный repository | Сейчас folder виден как untracked inside parent workspace |
| P0 | Запустить `.\scripts\preflight.ps1` после переноса | Подтвердить clean checkout behavior |
| P0 | Проверить `git status --short` | Не допустить секреты, reports и локальный мусор |
| P1 | Записать короткое demo video | Упростить проверку проекта |
| P1 | Проверить публичные ссылки и screenshots | Подготовить репозиторий к показу |

## Критерии готовности

- Команда из README запускается из clean checkout.
- Reports генерируются из sample data.
- Tests проходят.
- Secrets и real customer data не коммитятся.
- Проект объясняет business value, architecture и limitations.
- `action_plan.md` достаточно конкретен, чтобы оператор мог действовать.
