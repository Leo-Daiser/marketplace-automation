# Покрытие сценариев

## Цель

Проект должен работать не только на clean sample data. Он также должен показывать поведение pipeline на рискованных, подозрительных и операционно неудобных inputs.

## Сценарии

| Сценарий | Path | Назначение |
|---|---|---|
| Base sample | `data/sample/` | Основной demo dataset для README и preflight |
| Balanced growth | `data/scenarios/balanced_growth/` | Чистый operational scenario с profitable growth, low data-quality risk и normal P1 actions |
| Risk edge | `data/scenarios/risk_edge/` | Suspicious metrics, invalid review rating, zero-revenue spend и low-stock winner |

## Ожидаемое поведение balanced growth

Сценарий должен:

- генерировать все portfolio outputs без падения;
- не давать high/medium data quality findings;
- показывать zero risk campaigns в executive summary;
- сохранять gross profit after ads положительной;
- создавать normal P1/P2 operator actions без scaling blockers;
- сохранять columns action plan: severity, confidence, deadline и `blocks_scaling`.

## Ожидаемое поведение risk edge

Сценарий должен:

- генерировать все portfolio outputs без падения;
- создавать data quality findings;
- отмечать suspicious ads metrics, где clicks превышают impressions;
- отмечать invalid review rating вне диапазона 1-5;
- создавать support escalation для side-effect review;
- ограничивать spend для low-stock campaign;
- создавать action plan с P0/P1 actions.

## Ручной запуск

```powershell
cd "C:\Users\WORK\Documents\Work Projects\iqbiq-marketplace-automation-portfolio"
$env:PYTHONPATH = ".\src"
python -m marketplace_automation.cli run-all --data-dir .\data\scenarios\risk_edge --out-dir .\reports\risk_edge
python -m marketplace_automation.cli run-all --data-dir .\data\scenarios\balanced_growth --out-dir .\reports\balanced_growth
python -m marketplace_automation.cli data-quality --data-dir .\data\scenarios\risk_edge --out-dir .\reports\risk_edge
```

Открыть:

```text
reports/risk_edge/data_quality_report.md
reports/risk_edge/action_plan.md
reports/risk_edge/ads_decision_audit.csv
reports/balanced_growth/executive_summary.md
reports/balanced_growth/action_plan.md
reports/balanced_growth/data_quality_report.md
```
