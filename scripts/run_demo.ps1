param(
    [string]$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
Set-Location $ProjectRoot
$env:PYTHONPATH = ".\src"

python -m marketplace_automation.cli run-all --data-dir .\data\sample --out-dir .\reports
python -m unittest discover -s tests

Write-Host ""
Write-Host "Демо-отчеты:"
Write-Host "  $ProjectRoot\reports\ads_dashboard.html"
Write-Host "  $ProjectRoot\reports\ads_report.md"
Write-Host "  $ProjectRoot\reports\review_digest.md"
Write-Host "  $ProjectRoot\reports\competitor_digest.md"
