# Описание проекта

Портфолио-проект по автоматизации marketplace operations.

## Кратко

Репозиторий содержит воспроизводимый контур:

- рекламная аналитика с учетом unit economics;
- review-response workflow с ручным approval для рискованных случаев;
- конкурентный SEO/content мониторинг;
- общий action plan для команды;
- Google Sheets, n8n, Telegram, Notion и API boundaries;
- tests, regression snapshots, scenario coverage и preflight.

## Технический акцент

Бизнес-логика вынесена в Python:

- расчеты CTR, CPC, CR, ДРР, ROAS и прибыли после рекламы;
- break-even ДРР по SKU;
- decision audit trail по рекламным кампаниям;
- compliance flags для отзывов;
- competitor opportunity scoring;
- payload builders для Telegram и Notion.

n8n используется как orchestration layer: читает таблицы, вызывает локальный API и доставляет результат в Telegram/Notion.

## Ссылки внутри проекта

- `README.md`
- `docs/case_study.md`
- `docs/architecture.md`
- `docs/capability_matrix.md`
- `docs/demo_walkthrough.md`
- `docs/n8n_self_host_setup.md`
- `docs/google_sheets_no_cloud_setup.md`
