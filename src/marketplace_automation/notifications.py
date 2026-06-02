from __future__ import annotations

from typing import Any, Mapping

from .ads_reporter import summarize_campaigns
from .io_utils import money, parse_float


TELEGRAM_LIMIT = 4096
AREA_LABELS = {
    "ads": "реклама",
    "reviews": "отзывы",
    "competitors": "конкуренты",
}


def format_telegram_daily_digest(
    *,
    ads_rows: list[Mapping[str, Any]],
    ticket_rows: list[Mapping[str, Any]],
    opportunity_rows: list[Mapping[str, Any]],
    action_rows: list[Mapping[str, Any]],
) -> str:
    ads_summary = summarize_campaigns(ads_rows)
    risk_campaigns = [
        row
        for row in ads_rows
        if row.get("recommended_action") not in {"monitor", "scale_budget"}
    ]
    high_opportunities = [
        row for row in opportunity_rows if parse_float(row.get("opportunity_score")) >= 6
    ]
    p0_actions = [row for row in action_rows if row.get("priority") == "P0"]
    lines = [
        "Дайджест автоматизации маркетплейсов",
        "",
        f"Расход на рекламу: {money(ads_summary['spend_rub'])}",
        f"Выручка: {money(ads_summary['revenue_rub'])}",
        f"ДРР: {ads_summary['drr'] * 100:.1f}%",
        f"Прибыль после рекламы: {money(ads_summary['gross_profit_rub'])}",
        "",
        f"Рисковые кампании: {len(risk_campaigns)}",
        f"Обращения в поддержку: {len(ticket_rows)}",
        f"Сильные возможности по конкурентам: {len(high_opportunities)}",
        f"Действия P0: {len(p0_actions)}",
        "",
        "Главные действия:",
    ]
    for action in p0_actions[:5]:
        area = str(action.get("area_label") or AREA_LABELS.get(str(action.get("area", "")), action.get("area", "")))
        lines.append(
            f"- [{area}] {action.get('action')} ({action.get('evidence')})"
        )
    return trim_for_telegram("\n".join(lines))


def trim_for_telegram(text: str, limit: int = TELEGRAM_LIMIT) -> str:
    if len(text) <= limit:
        return text
    suffix = "\n\n...обрезано"
    return text[: limit - len(suffix)].rstrip() + suffix
