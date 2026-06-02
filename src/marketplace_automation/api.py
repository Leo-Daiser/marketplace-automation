from __future__ import annotations

from typing import Any

from .ads_reporter import build_campaign_report
from .competitor_monitor import build_competitor_report
from .notion_payloads import build_notion_task_payload
from .notifications import format_telegram_daily_digest
from .portfolio import build_action_items
from .review_agent import build_support_ticket, classify_review


def create_app() -> Any:
    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise RuntimeError(
            "FastAPI является optional dependency. Установи его командой: pip install -e .[api]"
        ) from exc

    app = FastAPI(title="API автоматизации маркетплейсов", version="0.1.0")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/ads/report")
    def ads_report(payload: dict[str, Any]) -> dict[str, Any]:
        rows = payload.get("rows", [])
        target_drr = float(payload.get("target_drr", 0.18))
        return {"rows": build_campaign_report(rows, target_drr=target_drr)}

    @app.post("/reviews/drafts")
    def review_drafts(payload: dict[str, Any]) -> dict[str, Any]:
        rows = payload.get("rows", [])
        replies = [classify_review(row) for row in rows]
        tickets = [
            ticket
            for ticket in (build_support_ticket(row) for row in replies)
            if ticket is not None
        ]
        return {"replies": replies, "tickets": tickets}

    @app.post("/competitors/opportunities")
    def competitor_opportunities(payload: dict[str, Any]) -> dict[str, Any]:
        opportunities, tasks = build_competitor_report(
            payload.get("competitors", []),
            payload.get("our_products", []),
            payload.get("keyword_plan", []),
        )
        return {"opportunities": opportunities, "tasks": tasks}

    @app.post("/integrations/telegram/digest")
    def telegram_digest(payload: dict[str, Any]) -> dict[str, str]:
        ads_rows = payload.get("ads_rows", [])
        review_rows = payload.get("review_rows", [])
        ticket_rows = payload.get("ticket_rows", [])
        opportunity_rows = payload.get("opportunity_rows", [])
        task_rows = payload.get("task_rows", [])
        action_rows = payload.get("action_rows") or build_action_items(
            ads_rows=ads_rows,
            review_rows=review_rows,
            ticket_rows=ticket_rows,
            opportunity_rows=opportunity_rows,
            task_rows=task_rows,
        )
        return {
            "text": format_telegram_daily_digest(
                ads_rows=ads_rows,
                ticket_rows=ticket_rows,
                opportunity_rows=opportunity_rows,
                action_rows=action_rows,
            )
        }

    @app.post("/integrations/notion/tasks")
    def notion_tasks(payload: dict[str, Any]) -> dict[str, Any]:
        tasks = payload.get("tasks", [])
        return {"tasks": [build_notion_task_payload(task) for task in tasks]}

    return app


try:
    app = create_app()
except RuntimeError:
    app = None
