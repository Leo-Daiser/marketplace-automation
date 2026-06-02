# Проверка качества

Запускать перед отправкой ссылки на портфолио.

```powershell
cd "C:\Users\WORK\Documents\Work Projects\iqbiq-marketplace-automation-portfolio"
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli run-all --data-dir .\data\sample --out-dir .\reports
python -m unittest discover -s tests
python -m compileall -q .\src .\tests
python -m json.tool .\integrations\n8n\ads_report_to_telegram.json > $null
python -m json.tool .\integrations\n8n\review_agent_to_support.json > $null
python -m json.tool .\integrations\n8n\competitor_monitor_to_notion.json > $null
git status --short
```

Ожидаемый результат:

- все отчеты перегенерированы;
- unit tests проходят, сейчас 35 tests;
- `compileall` не выводит ошибок;
- JSON validation не выводит ошибок;
- `git status --short` показывает только осознанные project files.

Не публиковать, если:

- отчеты не перегенерируются;
- tests падают;
- в Git status появляется `.env`, token, private export или real customer dataset;
- README утверждает реальную API-интеграцию, которая только запланирована.
