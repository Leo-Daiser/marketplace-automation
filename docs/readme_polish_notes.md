# Заметки по polish README

## Сильные стороны текущего README

- Понятная цель проекта.
- Воспроизводимые команды.
- Ссылки на architecture, API, Google Sheets и marketplace adapters.
- Честные limitations.
- Рассказ для демо уже добавлен.

## Оставшийся визуальный polish

Скриншот ads dashboard лежит в `docs/assets/ads_dashboard.png`.

Использовать helper script, когда доступен Microsoft Edge, Chrome или Chromium:

```powershell
.\scripts\generate_screenshots.ps1
```

Если browser установлен вне PATH:

```powershell
.\scripts\generate_screenshots.ps1 -BrowserPath "C:\Program Files\Google\Chrome\Application\chrome.exe"
```

Рекомендуемые screenshots перед GitHub publication:

1. `reports/ads_dashboard.html`
2. `reports/action_plan.md`
3. `reports/executive_summary.md`
4. `reports/telegram_digest.txt`

Рекомендуемая folder:

```text
docs/assets/
```

README image links после появления screenshots:

```markdown
![Ads dashboard](docs/assets/ads_dashboard.png)
![Action plan](docs/assets/action_plan.png)
```

## Примеры manual screenshot commands

Если доступен Microsoft Edge:

```powershell
msedge --headless --disable-gpu --window-size=1440,1000 --screenshot=docs\assets\ads_dashboard.png reports\ads_dashboard.html
```

Если доступен Chrome:

```powershell
chrome --headless --disable-gpu --window-size=1440,1000 --screenshot=docs\assets\ads_dashboard.png reports\ads_dashboard.html
```

Не утверждать, что дополнительные screenshots включены, пока файлы реально не существуют.
