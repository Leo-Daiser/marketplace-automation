from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .ads_reporter import run_ads_report, summarize_campaigns
from .competitor_monitor import run_competitor_monitor
from .data_quality import run_data_quality_report
from .io_utils import markdown_table, money, parse_float, parse_int, read_csv, write_text
from .notifications import format_telegram_daily_digest
from .review_agent import run_review_agent
from .unit_economics import read_unit_economics, run_unit_economics_report


ACTION_LABELS = {
    "cap_spend_low_stock": "Ограничить расход до пополнения остатков",
    "pause_until_card_fix": "Поставить кампанию на паузу до исправления карточки",
    "fix_card_or_price_before_scaling": "Исправить карточку или цену перед масштабированием",
    "rewrite_creative_or_search_query": "Переписать креатив или поисковый запрос",
    "reduce_bid_and_check_unit_economics": "Снизить ставку и проверить unit economics",
    "scale_budget": "Аккуратно увеличить бюджет",
    "check_card_conversion": "Проверить конверсию карточки",
    "monitor": "Продолжить мониторинг",
}

AREA_LABELS = {
    "ads": "реклама",
    "reviews": "отзывы",
    "competitors": "конкуренты",
}

LEVEL_LABELS = {
    "critical": "критично",
    "high": "высокая",
    "medium": "средняя",
    "low": "низкая",
}

BOOLEAN_LABELS = {
    "yes": "да",
    "no": "нет",
}

TOPIC_LABELS = {
    "taste": "вкус",
    "effect": "эффект",
    "delivery": "доставка",
    "packaging": "упаковка",
    "price": "цена",
    "side_effect": "индивидуальная реакция",
    "other": "другое",
}


def run_portfolio_suite(data_dir: Path, out_dir: Path, target_drr: float = 0.18) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    data_quality_outputs = run_data_quality_report(data_dir, out_dir)
    unit_economics_path = data_dir / "unit_economics.csv"
    unit_economics = (
        read_unit_economics(unit_economics_path)
        if unit_economics_path.exists()
        else None
    )

    ads_outputs = run_ads_report(
        data_dir / "ads_daily.csv",
        out_dir,
        target_drr=target_drr,
        unit_economics=unit_economics,
    )
    unit_outputs = (
        {"unit_economics_csv": run_unit_economics_report(unit_economics_path, out_dir)}
        if unit_economics_path.exists()
        else {}
    )
    review_outputs = run_review_agent(data_dir / "reviews.csv", out_dir)
    competitor_outputs = run_competitor_monitor(
        competitors_path=data_dir / "competitors.csv",
        our_products_path=data_dir / "our_products.csv",
        keyword_plan_path=data_dir / "keyword_plan.csv",
        out_dir=out_dir,
    )

    ads_rows = read_csv(out_dir / "ads_campaign_report.csv")
    review_rows = read_csv(out_dir / "review_replies.csv")
    ticket_rows = read_csv(out_dir / "support_tickets.csv")
    opportunity_rows = read_csv(out_dir / "competitor_opportunities.csv")
    task_rows = read_csv(out_dir / "seo_content_tasks.csv")
    action_rows = build_action_items(
        ads_rows=ads_rows,
        review_rows=review_rows,
        ticket_rows=ticket_rows,
        opportunity_rows=opportunity_rows,
        task_rows=task_rows,
    )

    action_plan_path = out_dir / "action_plan.md"
    executive_summary_path = out_dir / "executive_summary.md"
    telegram_digest_path = out_dir / "telegram_digest.txt"
    write_text(
        action_plan_path,
        render_action_plan(action_rows),
    )
    write_text(
        executive_summary_path,
        render_executive_summary(
            ads_rows=ads_rows,
            review_rows=review_rows,
            ticket_rows=ticket_rows,
            opportunity_rows=opportunity_rows,
            task_rows=task_rows,
            target_drr=target_drr,
        ),
    )
    write_text(
        telegram_digest_path,
        format_telegram_daily_digest(
            ads_rows=ads_rows,
            ticket_rows=ticket_rows,
            opportunity_rows=opportunity_rows,
            action_rows=action_rows,
        ),
    )

    return {
        **{f"ads_{key}": value for key, value in ads_outputs.items()},
        **{f"data_quality_{key}": value for key, value in data_quality_outputs.items()},
        **unit_outputs,
        **{f"reviews_{key}": value for key, value in review_outputs.items()},
        **{f"competitors_{key}": value for key, value in competitor_outputs.items()},
        "portfolio_action_plan": action_plan_path,
        "portfolio_executive_summary": executive_summary_path,
        "portfolio_telegram_digest": telegram_digest_path,
    }


def render_executive_summary(
    *,
    ads_rows: list[Mapping[str, Any]],
    review_rows: list[Mapping[str, Any]],
    ticket_rows: list[Mapping[str, Any]],
    opportunity_rows: list[Mapping[str, Any]],
    task_rows: list[Mapping[str, Any]],
    target_drr: float,
) -> str:
    ads_summary = summarize_campaigns(ads_rows)
    risky_campaigns = [
        row
        for row in ads_rows
        if row.get("recommended_action") not in {"monitor", "scale_budget"}
    ]
    high_reviews = [row for row in review_rows if row.get("urgency") == "high"]
    high_opportunities = [
        row for row in opportunity_rows if parse_float(row.get("opportunity_score")) >= 6
    ]
    return "\n".join(
        [
            "# Управленческая сводка",
            "",
            "## Бизнес-срез",
            "",
            f"- Целевой ДРР: {target_drr * 100:.1f}%",
            f"- Расход на рекламу: {money(ads_summary['spend_rub'])}",
            f"- Выручка с рекламы: {money(ads_summary['revenue_rub'])}",
            f"- Общий ДРР: {ads_summary['drr'] * 100:.1f}%",
            f"- Прибыль после рекламы: {money(ads_summary['gross_profit_rub'])}",
            f"- Рисковые кампании: {len(risky_campaigns)}",
            f"- Обращения в поддержку по отзывам: {len(ticket_rows)}",
            f"- Срочные отзывы: {len(high_reviews)}",
            f"- Сильные возможности по конкурентам: {len(high_opportunities)}",
            f"- Создано SEO/content задач: {len(task_rows)}",
            "",
            "## Интерпретация",
            "",
            build_business_interpretation(
                ads_summary=ads_summary,
                risky_campaigns=risky_campaigns,
                high_reviews=high_reviews,
                high_opportunities=high_opportunities,
            ),
            "",
        ]
    )


def build_business_interpretation(
    *,
    ads_summary: Mapping[str, float],
    risky_campaigns: list[Mapping[str, Any]],
    high_reviews: list[Mapping[str, Any]],
    high_opportunities: list[Mapping[str, Any]],
) -> str:
    points: list[str] = []
    if ads_summary["drr"] > 0.25:
        points.append(
            "- Эффективность рекламы заметно хуже целевого ДРР. Перед масштабированием нужно перераспределить бюджет."
        )
    if risky_campaigns:
        points.append(
            "- Несколько кампаний требуют действий оператора: низкие остатки, убыточный расход или слабая конверсия."
        )
    if high_reviews:
        points.append(
            "- Срочные отзывы требуют ручного согласования до публикации ответа."
        )
    if high_opportunities:
        points.append(
            "- Разрывы с конкурентами достаточны, чтобы поставить SEO/content и unit-economics задачи в текущий спринт."
        )
    if not points:
        points.append("- Критичных рисков не найдено. Продолжать мониторинг и аккуратное масштабирование.")
    return "\n".join(points)


def render_action_plan(actions: list[Mapping[str, Any]]) -> str:
    display_rows = [action_plan_display_row(row) for row in actions]
    return "\n".join(
        [
            "# Сводный план действий",
            "",
            "Это ежедневная передача задач оператору по рекламе, отзывам и конкурентам.",
            "",
            "## На сегодня",
            "",
            markdown_table(
                display_rows,
                [
                    "приоритет",
                    "область",
                    "критичность",
                    "уверенность",
                    "ответственный",
                    "блокирует рост",
                    "срок",
                    "действие",
                    "подтверждение",
                    "следующая проверка",
                ],
            ),
            "",
            "## Правило работы",
            "",
            "- Действия P0 блокируют масштабирование до проверки.",
            "- Действия P1 нужно разобрать в течение рабочего дня.",
            "- Действия P2 остаются в backlog, если не повторяются три цикла подряд.",
            "",
        ]
    )


def action_plan_display_row(row: Mapping[str, Any]) -> dict[str, str]:
    return {
        "приоритет": str(row.get("priority", "")),
        "область": str(row.get("area_label") or AREA_LABELS.get(str(row.get("area", "")), row.get("area", ""))),
        "критичность": LEVEL_LABELS.get(str(row.get("severity", "")), str(row.get("severity", ""))),
        "уверенность": LEVEL_LABELS.get(str(row.get("confidence", "")), str(row.get("confidence", ""))),
        "ответственный": str(row.get("owner", "")),
        "блокирует рост": BOOLEAN_LABELS.get(str(row.get("blocks_scaling", "")), str(row.get("blocks_scaling", ""))),
        "срок": str(row.get("deadline", "")),
        "действие": str(row.get("action", "")),
        "подтверждение": str(row.get("evidence", "")),
        "следующая проверка": str(row.get("next_check", "")),
    }


def build_action_items(
    *,
    ads_rows: list[Mapping[str, Any]],
    review_rows: list[Mapping[str, Any]],
    ticket_rows: list[Mapping[str, Any]],
    opportunity_rows: list[Mapping[str, Any]],
    task_rows: list[Mapping[str, Any]],
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    actions.extend(build_ads_actions(ads_rows))
    actions.extend(build_review_actions(review_rows, ticket_rows))
    actions.extend(build_competitor_actions(opportunity_rows, task_rows))
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    return sorted(actions, key=lambda row: (priority_order.get(row["priority"], 9), row["area"]))


def build_ads_actions(ads_rows: list[Mapping[str, Any]]) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for row in ads_rows:
        action = str(row.get("recommended_action", ""))
        if action == "scale_budget":
            continue
        drr = parse_float(row.get("drr"))
        gross_profit = parse_float(row.get("gross_profit_rub"))
        priority = "P0" if gross_profit < 0 or drr > 0.5 else "P1"
        actions.append(
            {
                "priority": priority,
                "area": "ads",
                "area_label": "реклама",
                "severity": "critical" if priority == "P0" else "high",
                "confidence": str(row.get("decision_confidence") or "medium"),
                "owner": "performance",
                "blocks_scaling": "yes" if priority == "P0" else "no",
                "deadline": "сегодня",
                "action": f"{ACTION_LABELS.get(action, action)}: {row.get('campaign_name')} / {row.get('sku')}",
                "evidence": f"ДРР {drr * 100:.1f}%, прибыль {money(gross_profit)}",
                "next_check": "следующее ежедневное обновление рекламы",
            }
        )
    return actions[:6]


def build_review_actions(
    review_rows: list[Mapping[str, Any]],
    ticket_rows: list[Mapping[str, Any]],
) -> list[dict[str, str]]:
    actions: list[dict[str, str]] = []
    for ticket in ticket_rows:
        priority = "P0" if ticket.get("priority") == "P1" else "P1"
        actions.append(
            {
                "priority": priority,
                "area": "reviews",
                "area_label": "отзывы",
                "severity": "critical" if priority == "P0" else "high",
                "confidence": "high",
                "owner": "support",
                "blocks_scaling": "yes" if priority == "P0" else "no",
                "deadline": "сегодня",
                "action": f"Проверить обращение {ticket.get('ticket_id')} по SKU {ticket.get('sku')}",
                "evidence": str(ticket.get("reason", "")),
                "next_check": "после ручного согласования",
            }
        )
    low_rating_without_ticket = [
        row
        for row in review_rows
        if parse_int(row.get("rating")) <= 3 and row.get("needs_support_ticket") != "true"
    ]
    for row in low_rating_without_ticket[:3]:
        actions.append(
            {
                "priority": "P2",
                "area": "reviews",
                "area_label": "отзывы",
                "severity": "medium",
                "confidence": "medium",
                "owner": "content",
                "blocks_scaling": "no",
                "deadline": "на этой неделе",
                "action": f"Разобрать отзыв с низкой оценкой {row.get('review_id')} для контентных выводов",
                "evidence": f"Тема {TOPIC_LABELS.get(str(row.get('topic', '')), row.get('topic'))}, оценка {row.get('rating')}",
                "next_check": "еженедельный разбор отзывов",
            }
        )
    return actions[:8]


def build_competitor_actions(
    opportunity_rows: list[Mapping[str, Any]],
    task_rows: list[Mapping[str, Any]],
) -> list[dict[str, str]]:
    task_by_keyword = {str(row.get("keyword")): row for row in task_rows}
    actions: list[dict[str, str]] = []
    for row in opportunity_rows:
        score = parse_float(row.get("opportunity_score"))
        if score < 6:
            continue
        task = task_by_keyword.get(str(row.get("keyword")), {})
        actions.append(
            {
                "priority": "P1" if score < 9 else "P0",
                "area": "competitors",
                "area_label": "конкуренты",
                "severity": "critical" if score >= 9 else "high",
                "confidence": "high" if score >= 8 else "medium",
                "owner": "seo/content",
                "blocks_scaling": "no",
                "deadline": "на этой неделе" if score < 9 else "сегодня",
                "action": str(task.get("title") or row.get("recommended_action")),
                "evidence": f"Оценка {score:.1f}; {row.get('reason')}",
                "next_check": "следующее еженедельное обновление конкурентов",
            }
        )
    return actions[:6]
