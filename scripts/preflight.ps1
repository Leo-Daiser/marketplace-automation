param(
    [string]$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
Set-Location $ProjectRoot
$env:PYTHONPATH = ".;.\src"

Write-Host "Запуск финальной проверки портфолио..."

python -m marketplace_automation.cli run-all --data-dir .\data\sample --out-dir .\reports
python -m unittest discover -s tests
python -m compileall -q .\src .\tests
python -m json.tool .\integrations\n8n\ads_report_to_telegram.json > $null
python -m json.tool .\integrations\n8n\review_agent_to_support.json > $null
python -m json.tool .\integrations\n8n\competitor_monitor_to_notion.json > $null
python -m json.tool .\integrations\n8n\no_cloud_marketplace_digest.json > $null

$dangerous = @(
    ".env",
    "service-account.json"
)

foreach ($path in $dangerous) {
    if (Test-Path $path) {
        throw "Перед публикацией найден опасный файл: $path"
    }
}

if (Test-Path ".\data\private") {
    throw "Найдена папка private data. Нельзя публиковать без проверки: data\private"
}

if (Test-Path ".\data\raw") {
    throw "Найдена папка raw data. Нельзя публиковать без проверки: data\raw"
}

Write-Host ""
Write-Host "Финальная проверка пройдена."
Write-Host "Ключевые артефакты:"
Write-Host "  $ProjectRoot\reports\executive_summary.md"
Write-Host "  $ProjectRoot\reports\action_plan.md"
Write-Host "  $ProjectRoot\reports\telegram_digest.txt"
Write-Host "  $ProjectRoot\reports\ads_dashboard.html"
