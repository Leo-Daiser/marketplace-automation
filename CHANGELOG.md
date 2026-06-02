# Changelog

## 2026-06-02 - Portfolio hardening

### Added

- Decision audit trail for advertising recommendations.
- Data quality report for required columns, empty values and suspicious metrics.
- Scenario coverage for:
  - `data/scenarios/risk_edge`;
  - `data/scenarios/balanced_growth`.
- Regression snapshot tests for generated report structure.
- Operational action plan fields: severity, confidence, owner, deadline and scaling blocker.
- Portfolio case study in `docs/case_study.md`.
- Risk register in `docs/risk_register.md`.
- Repository readiness audit in `docs/repository_readiness_audit.md`.
- README dashboard screenshot in `docs/assets/ads_dashboard.png`.
- Screenshot helper script in `scripts/generate_screenshots.ps1`.
- GitHub Actions CI workflow in `.github/workflows/ci.yml`.

### Improved

- README now includes stronger demo artifacts and publication links.
- Backlog and sprint status now separate production readiness tasks from integration expansion.
- Preflight remains the main publication gate.

### Current quality gate

```text
Preflight passed.
35 tests OK.
```

## 2026-06-01 - Portfolio MVP

### Added

- Ads Performance Copilot for WB/Ozon-style advertising analytics.
- Review Response Agent with approval and compliance flags.
- Competitor SEO Monitor with opportunity scoring and content tasks.
- Consolidated portfolio orchestrator that generates:
  - `reports/executive_summary.md`;
  - `reports/action_plan.md`;
  - `reports/telegram_digest.txt`.
- Unit economics model for margin-aware ad decisions.
- Google Sheets adapter and CLI sync commands.
- Optional FastAPI boundary for n8n/Make-style automation.
- Telegram and Notion payload builders.
- Marketplace API adapter boundaries for WB/Ozon-style ads data.
- Demo walkthrough, video script, publication guide and capability matrix.

### Quality

- Synthetic sample data only.
- Deterministic core logic.
- Unit tests for core business behavior.
- `.gitignore` excludes secrets, private data and generated reports.
