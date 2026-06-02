param(
    [string]$ProjectRoot = (Resolve-Path "$PSScriptRoot\..").Path,
    [string]$WorkflowId = "no-cloud-marketplace-digest",
    [string]$N8nComposeDir = (Join-Path $ProjectRoot "integrations\n8n\self_host"),
    [string]$WorkflowTemplate = (Join-Path $ProjectRoot "integrations\n8n\no_cloud_marketplace_digest.json")
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

function Require-Env {
    param([string]$Name)
    $value = [Environment]::GetEnvironmentVariable($Name, "Process")
    if ([string]::IsNullOrWhiteSpace($value)) {
        throw "Missing required environment variable: $Name"
    }
    return $value
}

function Test-HttpOk {
    param(
        [string]$Url,
        [int]$TimeoutSec = 5
    )
    try {
        $response = Invoke-WebRequest -UseBasicParsing -Uri $Url -TimeoutSec $TimeoutSec
        return ($response.StatusCode -ge 200 -and $response.StatusCode -lt 300)
    }
    catch {
        return $false
    }
}

Set-Location $ProjectRoot

$telegramBotToken = Require-Env "TELEGRAM_BOT_TOKEN"
$telegramChatId = Require-Env "TELEGRAM_CHAT_ID"
$notionToken = Require-Env "NOTION_TOKEN"
$notionDatabaseId = Require-Env "NOTION_DATABASE_ID"

Write-Host "Запуск live-демо автоматизации маркетплейсов..."

if (-not (Test-HttpOk "http://localhost:8000/health")) {
    Write-Host "Запускаю Python API на порту 8000..."
    $apiCommand = '$env:PYTHONPATH=''.;.\src''; python -m uvicorn marketplace_automation.api:app --host 0.0.0.0 --port 8000'
    Start-Process -FilePath powershell -ArgumentList @("-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", $apiCommand) -WorkingDirectory $ProjectRoot -WindowStyle Hidden
    Start-Sleep -Seconds 5
}

if (-not (Test-HttpOk "http://localhost:8000/health")) {
    throw "Python API не ответил на http://localhost:8000/health"
}

docker info *> $null

Set-Location $N8nComposeDir
docker compose up -d *> $null
Start-Sleep -Seconds 5

if (-not (Test-HttpOk "http://localhost:5678")) {
    throw "n8n не ответил на http://localhost:5678"
}

$localWorkflow = Join-Path $env:TEMP "marketplace_no_cloud_digest.local.json"
$workflowJson = Get-Content -Path $WorkflowTemplate -Raw
$workflowJson = $workflowJson.Replace("TELEGRAM_BOT_TOKEN", $telegramBotToken)
$workflowJson = $workflowJson.Replace("TELEGRAM_CHAT_ID", $telegramChatId)
$workflowJson = $workflowJson.Replace("NOTION_TOKEN", $notionToken)
$workflowJson = $workflowJson.Replace("NOTION_DATABASE_ID", $notionDatabaseId)
Set-Content -Path $localWorkflow -Value $workflowJson -Encoding UTF8

docker cp $localWorkflow "marketplace-n8n:/tmp/no_cloud_marketplace_digest.local.json" *> $null
docker exec marketplace-n8n n8n import:workflow --input=/tmp/no_cloud_marketplace_digest.local.json *> $null

docker stop marketplace-n8n *> $null
$executionOutput = docker compose run --rm --no-deps --entrypoint n8n n8n execute --id=$WorkflowId --rawOutput 2>&1
$exitCode = $LASTEXITCODE
docker start marketplace-n8n *> $null
Start-Sleep -Seconds 3

if ($exitCode -ne 0) {
    $executionText = $executionOutput -join "`n"
    Write-Host $executionText
    throw "Выполнение n8n workflow завершилось с ошибкой, код $exitCode"
}

$executionText = $executionOutput -join "`n"
$workflowSucceeded = $executionText -match '"status"\s*:\s*"success"'
$telegramSent = $executionText -match '"ok"\s*:\s*true'
$notionDeduped = $executionText -match '"created_notion_tasks"\s*:\s*0' -and $executionText -match '"updated_notion_tasks"\s*:\s*5'
$notionCreated = $executionText -match '"created_notion_tasks"\s*:\s*5'

Write-Host ""
Write-Host "Результат live-демо:"
Write-Host "  Workflow выполнен:        $workflowSucceeded"
Write-Host "  Telegram отправлен:       $telegramSent"
Write-Host "  Notion создал задачи:     $notionCreated"
Write-Host "  Notion обновил без дублей: $notionDeduped"
Write-Host ""
Write-Host "Открыть:"
Write-Host "  n8n:    http://localhost:5678/workflow/$WorkflowId"
Write-Host "  API:    http://localhost:8000/health"
Write-Host "  Notion: https://www.notion.so/$($notionDatabaseId.Replace('-', ''))"
Write-Host ""
Write-Host "Не коммитьте реальные токены. Скрипт прочитал их только из переменных окружения."
