# Чеклист отправки портфолио

Использовать перед отправкой отклика.

## 1. Перегенерировать demo outputs

```powershell
cd "C:\Users\WORK\Documents\Work Projects\iqbiq-marketplace-automation-portfolio"
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli run-all --data-dir .\data\sample --out-dir .\reports
python -m unittest discover -s tests
python -m compileall -q .\src .\tests
```

Ожидаемый результат:

```text
35 tests OK
```

## 2. Проверить ключевые артефакты

Открыть файлы:

```text
reports/executive_summary.md
reports/action_plan.md
reports/telegram_digest.txt
reports/ads_dashboard.html
reports/review_replies.csv
reports/seo_content_tasks.csv
```

Проверить:

- `action_plan.md` содержит действия по рекламе, отзывам и конкурентам;
- `telegram_digest.txt` достаточно короткий для Telegram;
- `ads_dashboard.html` открывается локально;
- review replies содержат approval/compliance fields;
- generated files не содержат secrets или real client data.

## 3. Проверить безопасность репозитория

```powershell
git status --short
```

Не публиковать, если status содержит:

- `.env`;
- `service-account.json`;
- реальные WB/Ozon exports;
- private datasets;
- model weights;
- database dumps;
- large generated files.

## 4. Подготовить GitHub README

Перед публикацией:

- держать README практичным, без marketing-heavy подачи;
- добавить главную команду запуска;
- честно описать limitations;
- добавить ссылки на architecture и demo walkthrough;
- не утверждать real WB/Ozon production integration, если credentials не подключались.

## 5. Текст отклика

Использовать `docs/application_pitch.md` как базу.

Заменить placeholders:

```text
Ссылки на кейсы:
- GitHub repository URL
- README URL
- Demo artifacts/screenshots URL, если есть
```

## 6. Talking points для собеседования

Фокус:

- deterministic core logic;
- data contracts, совместимые с Google Sheets;
- n8n как orchestration layer, а не место хранения business logic;
- nutraceutical review compliance;
- unit economics и break-even ДРР;
- WB/Ozon adapters как integration boundaries;
- action plan как главный business artifact.

## 7. Ограничения, которые нужно сказать честно

```text
Это воспроизводимый portfolio prototype на synthetic data.
Реальный deployment требует client credentials, подтверждения endpoint versions,
rate limits, retries, credential storage и настройки approval workflow.
```

