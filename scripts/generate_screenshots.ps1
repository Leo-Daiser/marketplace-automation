param(
    [string]$BrowserPath = ""
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"

$ProjectRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$DashboardPath = Join-Path $ProjectRoot "reports\ads_dashboard.html"
$AssetsDir = Join-Path $ProjectRoot "docs\assets"
$ScreenshotPath = Join-Path $AssetsDir "ads_dashboard.png"
$TempDir = Join-Path $ProjectRoot "reports\screenshot_pages"

function Find-Browser {
    param([string]$ExplicitPath)

    if ($ExplicitPath -and (Test-Path $ExplicitPath)) {
        return (Resolve-Path $ExplicitPath).Path
    }

    foreach ($Name in @("msedge", "chrome", "chromium")) {
        $Found = & where.exe $Name 2>$null | Select-Object -First 1
        if ($Found) {
            return $Found
        }
    }

    $CommonPaths = @(
        "${env:ProgramFiles}\Microsoft\Edge\Application\msedge.exe",
        "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
    )
    foreach ($Path in $CommonPaths) {
        if ($Path -and (Test-Path $Path)) {
            return $Path
        }
    }

    return ""
}

if (-not (Test-Path $DashboardPath)) {
    Write-Host "reports\ads_dashboard.html не найден. Сначала генерирую демо-отчеты..."
    Push-Location $ProjectRoot
    try {
        $env:PYTHONPATH = ".\src"
        python -m marketplace_automation.cli run-all --data-dir .\data\sample --out-dir .\reports
    }
    finally {
        Pop-Location
    }
}

$ResolvedBrowser = Find-Browser -ExplicitPath $BrowserPath
if (-not $ResolvedBrowser) {
    Write-Host "Поддерживаемый browser executable не найден. Установи Microsoft Edge/Chrome или передай -BrowserPath."
    exit 2
}

New-Item -ItemType Directory -Force -Path $AssetsDir | Out-Null
New-Item -ItemType Directory -Force -Path $TempDir | Out-Null

& $ResolvedBrowser `
    --headless `
    --disable-gpu `
    --hide-scrollbars `
    --window-size=1440,1000 `
    "--screenshot=$ScreenshotPath" `
    "$DashboardPath"

for ($Attempt = 0; $Attempt -lt 20; $Attempt++) {
    if ((Test-Path $ScreenshotPath) -and ((Get-Item $ScreenshotPath).Length -gt 0)) {
        break
    }
    Start-Sleep -Milliseconds 250
}

if (-not (Test-Path $ScreenshotPath) -or ((Get-Item $ScreenshotPath).Length -eq 0)) {
    Write-Host "Screenshot не был создан: $ScreenshotPath"
    exit 1
}

function Convert-MarkdownLiteToHtml {
    param(
        [string]$SourcePath,
        [string]$Title
    )

    $Lines = Get-Content -Path $SourcePath -Encoding UTF8
    $Body = New-Object System.Collections.Generic.List[string]
    $InTable = $false

    foreach ($Line in $Lines) {
        if ($Line.Trim() -eq "") {
            if ($InTable) {
                $Body.Add("</tbody></table>")
                $InTable = $false
            }
            continue
        }

        if ($Line.StartsWith("# ")) {
            if ($InTable) {
                $Body.Add("</tbody></table>")
                $InTable = $false
            }
            $Body.Add("<h1>$([System.Net.WebUtility]::HtmlEncode($Line.Substring(2)))</h1>")
            continue
        }

        if ($Line.StartsWith("## ")) {
            if ($InTable) {
                $Body.Add("</tbody></table>")
                $InTable = $false
            }
            $Body.Add("<h2>$([System.Net.WebUtility]::HtmlEncode($Line.Substring(3)))</h2>")
            continue
        }

        if ($Line.StartsWith("- ")) {
            if ($InTable) {
                $Body.Add("</tbody></table>")
                $InTable = $false
            }
            $Body.Add("<p class='bullet'>$([System.Net.WebUtility]::HtmlEncode($Line.Substring(2)))</p>")
            continue
        }

        if ($Line.StartsWith("| ")) {
            $Cells = $Line.Trim("|").Split("|") | ForEach-Object { $_.Trim() }
            $IsSeparator = $true
            foreach ($Cell in $Cells) {
                if ($Cell -notmatch "^-+$") {
                    $IsSeparator = $false
                }
            }
            if ($IsSeparator) {
                continue
            }
            if (-not $InTable) {
                $Body.Add("<table><tbody>")
                $InTable = $true
                $Tag = "th"
            }
            else {
                $Tag = "td"
            }
            $EncodedCells = $Cells | ForEach-Object { "<$Tag>$([System.Net.WebUtility]::HtmlEncode($_))</$Tag>" }
            $Body.Add("<tr>$($EncodedCells -join '')</tr>")
            continue
        }

        if ($InTable) {
            $Body.Add("</tbody></table>")
            $InTable = $false
        }
        $Body.Add("<p>$([System.Net.WebUtility]::HtmlEncode($Line))</p>")
    }

    if ($InTable) {
        $Body.Add("</tbody></table>")
    }

    return @"
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>$Title</title>
<style>
  :root {
    color-scheme: light;
    --ink: #172033;
    --muted: #5d6678;
    --line: #d9dfeb;
    --accent: #2563eb;
    --bg: #f4f7fb;
    --panel: #ffffff;
  }
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: var(--bg);
    color: var(--ink);
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 19px;
    line-height: 1.5;
  }
  main {
    width: 1320px;
    margin: 0 auto;
    padding: 44px 52px 60px;
  }
  .surface {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 8px;
    box-shadow: 0 18px 42px rgba(23, 32, 51, 0.10);
    padding: 36px 40px;
  }
  h1 {
    margin: 0 0 22px;
    font-size: 36px;
    line-height: 1.15;
    color: var(--ink);
  }
  h2 {
    margin: 28px 0 14px;
    font-size: 24px;
    color: var(--accent);
  }
  p { margin: 8px 0; color: var(--muted); }
  .bullet::before {
    content: "";
    display: inline-block;
    width: 8px;
    height: 8px;
    margin-right: 10px;
    border-radius: 50%;
    background: var(--accent);
    vertical-align: 2px;
  }
  table {
    width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
    margin-top: 14px;
    font-size: 12px;
    line-height: 1.32;
  }
  th {
    text-align: left;
    background: #eef3ff;
    color: #24324b;
    border: 1px solid var(--line);
    padding: 8px 8px;
    font-weight: 700;
    overflow-wrap: anywhere;
    hyphens: auto;
  }
  td {
    border: 1px solid var(--line);
    padding: 8px 8px;
    vertical-align: top;
    overflow-wrap: anywhere;
    hyphens: auto;
  }
  tr:nth-child(even) td { background: #fafcff; }
</style>
</head>
<body><main><section class="surface">$($Body -join "`n")</section></main></body>
</html>
"@
}

function Convert-TextToHtml {
    param(
        [string]$SourcePath,
        [string]$Title
    )
    $Text = [System.Net.WebUtility]::HtmlEncode((Get-Content -Path $SourcePath -Raw -Encoding UTF8))
    return @"
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8">
<title>$Title</title>
<style>
  body {
    margin: 0;
    background: #f4f7fb;
    color: #172033;
    font-family: "Segoe UI", Arial, sans-serif;
  }
  main {
    width: 900px;
    margin: 0 auto;
    padding: 52px;
  }
  .phone {
    width: 760px;
    background: #ffffff;
    border: 1px solid #d9dfeb;
    border-radius: 8px;
    box-shadow: 0 18px 42px rgba(23, 32, 51, 0.10);
    padding: 32px;
  }
  .bar {
    font-size: 18px;
    font-weight: 700;
    color: #2563eb;
    margin-bottom: 18px;
  }
  pre {
    white-space: pre-wrap;
    margin: 0;
    font-family: Consolas, "Cascadia Mono", monospace;
    font-size: 17px;
    line-height: 1.48;
  }
</style>
</head>
<body><main><section class="phone"><div class="bar">Telegram-дайджест</div><pre>$Text</pre></section></main></body>
</html>
"@
}

function Save-Screenshot {
    param(
        [string]$HtmlPath,
        [string]$OutputPath,
        [string]$WindowSize
    )

    & $ResolvedBrowser `
        --headless `
        --disable-gpu `
        --hide-scrollbars `
        "--window-size=$WindowSize" `
        "--screenshot=$OutputPath" `
        "$HtmlPath"

    for ($Attempt = 0; $Attempt -lt 20; $Attempt++) {
        if ((Test-Path $OutputPath) -and ((Get-Item $OutputPath).Length -gt 0)) {
            break
        }
        Start-Sleep -Milliseconds 250
    }

    if (-not (Test-Path $OutputPath) -or ((Get-Item $OutputPath).Length -eq 0)) {
        Write-Host "Screenshot не был создан: $OutputPath"
        exit 1
    }
    Write-Host "Screenshot создан: $OutputPath"
}

$ExecutiveHtml = Join-Path $TempDir "executive_summary.html"
$ActionPlanHtml = Join-Path $TempDir "action_plan.html"
$TelegramHtml = Join-Path $TempDir "telegram_digest.html"

[System.IO.File]::WriteAllText($ExecutiveHtml, (Convert-MarkdownLiteToHtml -SourcePath (Join-Path $ProjectRoot "reports\executive_summary.md") -Title "Управленческая сводка"), [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText($ActionPlanHtml, (Convert-MarkdownLiteToHtml -SourcePath (Join-Path $ProjectRoot "reports\action_plan.md") -Title "Сводный план действий"), [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText($TelegramHtml, (Convert-TextToHtml -SourcePath (Join-Path $ProjectRoot "reports\telegram_digest.txt") -Title "Telegram digest"), [System.Text.UTF8Encoding]::new($false))

Write-Host "Screenshot создан: $ScreenshotPath"
Save-Screenshot -HtmlPath $ExecutiveHtml -OutputPath (Join-Path $AssetsDir "executive_summary.png") -WindowSize "1440,900"
Save-Screenshot -HtmlPath $ActionPlanHtml -OutputPath (Join-Path $AssetsDir "action_plan.png") -WindowSize "1440,1200"
Save-Screenshot -HtmlPath $TelegramHtml -OutputPath (Join-Path $AssetsDir "telegram_digest.png") -WindowSize "900,900"
