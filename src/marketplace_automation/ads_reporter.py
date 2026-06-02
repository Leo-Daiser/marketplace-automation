from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .io_utils import (
    html_report,
    markdown_table,
    money,
    parse_float,
    parse_int,
    pct,
    read_csv,
    safe_div,
    write_csv,
    write_json,
    write_text,
)
from .models import AdsDailyRow
from .schemas import ADS_DAILY_REQUIRED, validate_rows


ADS_COLUMNS = [
    "marketplace",
    "campaign_id",
    "campaign_name",
    "sku",
    "product_name",
    "impressions",
    "clicks",
    "spend_rub",
    "orders",
    "revenue_rub",
    "ctr",
    "cpc_rub",
    "conversion_rate",
    "drr",
    "roas",
    "gross_profit_rub",
    "break_even_drr",
    "unit_target_drr",
    "profit_status",
    "risk_level",
    "stock_units",
    "avg_bid_rub",
    "bid_delta_pct",
    "recommended_action",
    "decision_confidence",
    "decision_signals",
    "next_step",
    "reason",
]

ADS_AUDIT_COLUMNS = [
    "marketplace",
    "campaign_id",
    "campaign_name",
    "sku",
    "risk_level",
    "recommended_action",
    "decision_confidence",
    "decision_signals",
    "reason",
    "next_step",
]

ACTION_LABELS = {
    "cap_spend_low_stock": "Ограничить расход из-за низких остатков",
    "pause_until_card_fix": "Пауза до исправления карточки",
    "fix_card_or_price_before_scaling": "Исправить карточку или цену перед масштабированием",
    "rewrite_creative_or_search_query": "Переписать креатив или поисковый запрос",
    "reduce_bid_and_check_unit_economics": "Снизить ставку и проверить unit economics",
    "scale_budget": "Аккуратно увеличить бюджет",
    "check_card_conversion": "Проверить конверсию карточки",
    "monitor": "Мониторить",
}

PROFIT_STATUS_LABELS = {
    "loss_after_ads": "убыток после рекламы",
    "profitable_but_inefficient": "прибыль есть, эффективность слабая",
    "within_target": "в целевом диапазоне",
    "watch": "наблюдать",
}

RISK_LEVEL_LABELS = {
    "high": "высокий",
    "medium": "средний",
    "low": "низкий",
    "opportunity": "возможность",
}


def build_campaign_report(
    rows: list[Mapping[str, Any]],
    target_drr: float = 0.18,
    unit_economics: Mapping[tuple[str, str], Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    unit_economics = unit_economics or {}
    campaigns: dict[tuple[str, str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        daily = AdsDailyRow.from_mapping(row)
        key = (
            daily.marketplace.strip(),
            daily.campaign_id.strip(),
            daily.campaign_name.strip(),
            daily.sku.strip(),
            daily.product_name.strip(),
        )
        unit_model = unit_economics.get((key[3], key[0]))
        campaign = campaigns.setdefault(
            key,
            {
                "marketplace": key[0],
                "campaign_id": key[1],
                "campaign_name": key[2],
                "sku": key[3],
                "product_name": key[4],
                "impressions": 0,
                "clicks": 0,
                "spend_rub": 0.0,
                "orders": 0,
                "revenue_rub": 0.0,
                "gross_margin_rub": 0.0,
                "stock_units": None,
                "bid_rub_sum": 0.0,
                "row_count": 0,
                "break_even_drr": parse_float(unit_model.get("break_even_drr")) if unit_model else 0.0,
                "unit_target_drr": parse_float(unit_model.get("target_drr")) if unit_model else 0.0,
            },
        )
        margin_rate = parse_float(
            unit_model.get("contribution_margin_rate") if unit_model else daily.margin_rate
        )

        campaign["impressions"] += daily.impressions
        campaign["clicks"] += daily.clicks
        campaign["spend_rub"] += daily.spend_rub
        campaign["orders"] += daily.orders
        campaign["revenue_rub"] += daily.revenue_rub
        campaign["gross_margin_rub"] += daily.revenue_rub * margin_rate
        campaign["stock_units"] = (
            daily.stock_units
            if campaign["stock_units"] is None
            else min(campaign["stock_units"], daily.stock_units)
        )
        campaign["bid_rub_sum"] += daily.bid_rub
        campaign["row_count"] += 1

    report_rows: list[dict[str, Any]] = []
    for campaign in campaigns.values():
        ctr = safe_div(campaign["clicks"], campaign["impressions"])
        cpc = safe_div(campaign["spend_rub"], campaign["clicks"])
        conversion_rate = safe_div(campaign["orders"], campaign["clicks"])
        drr = safe_div(campaign["spend_rub"], campaign["revenue_rub"])
        roas = safe_div(campaign["revenue_rub"], campaign["spend_rub"])
        gross_profit = campaign["gross_margin_rub"] - campaign["spend_rub"]
        effective_target_drr = campaign["unit_target_drr"] or target_drr
        avg_bid = safe_div(campaign["bid_rub_sum"], campaign["row_count"])
        stock_units = campaign["stock_units"] or 0
        action, reason, bid_delta = recommend_campaign(
            impressions=campaign["impressions"],
            clicks=campaign["clicks"],
            spend=campaign["spend_rub"],
            orders=campaign["orders"],
            revenue=campaign["revenue_rub"],
            ctr=ctr,
            conversion_rate=conversion_rate,
            drr=drr,
            gross_profit=gross_profit,
            stock_units=stock_units,
            target_drr=effective_target_drr,
        )
        profit_status = classify_profit_status(gross_profit, drr, effective_target_drr)
        risk_level = classify_risk_level(
            action=action,
            drr=drr,
            gross_profit=gross_profit,
            stock_units=stock_units,
        )
        decision_confidence, decision_signals = build_decision_audit(
            action=action,
            ctr=ctr,
            conversion_rate=conversion_rate,
            drr=drr,
            gross_profit=gross_profit,
            stock_units=stock_units,
            target_drr=effective_target_drr,
        )
        report_rows.append(
            {
                "marketplace": campaign["marketplace"],
                "campaign_id": campaign["campaign_id"],
                "campaign_name": campaign["campaign_name"],
                "sku": campaign["sku"],
                "product_name": campaign["product_name"],
                "impressions": campaign["impressions"],
                "clicks": campaign["clicks"],
                "spend_rub": round(campaign["spend_rub"], 2),
                "orders": campaign["orders"],
                "revenue_rub": round(campaign["revenue_rub"], 2),
                "ctr": round(ctr, 4),
                "cpc_rub": round(cpc, 2),
                "conversion_rate": round(conversion_rate, 4),
                "drr": round(drr, 4),
                "roas": round(roas, 2),
                "gross_profit_rub": round(gross_profit, 2),
                "break_even_drr": round(campaign["break_even_drr"], 4),
                "unit_target_drr": round(campaign["unit_target_drr"], 4),
                "profit_status": profit_status,
                "risk_level": risk_level,
                "stock_units": stock_units,
                "avg_bid_rub": round(avg_bid, 2),
                "bid_delta_pct": bid_delta,
                "recommended_action": action,
                "decision_confidence": decision_confidence,
                "decision_signals": "; ".join(decision_signals),
                "next_step": build_next_step(action, bid_delta),
                "reason": reason,
            }
        )
    return sorted(report_rows, key=lambda item: (item["drr"], -item["gross_profit_rub"]), reverse=True)


def recommend_campaign(
    *,
    impressions: int,
    clicks: int,
    spend: float,
    orders: int,
    revenue: float,
    ctr: float,
    conversion_rate: float,
    drr: float,
    gross_profit: float,
    stock_units: int,
    target_drr: float,
) -> tuple[str, str, int]:
    if stock_units <= 10 and spend > 0:
        return "cap_spend_low_stock", "Низкие остатки могут сжечь рекламный бюджет без возможности отгрузки.", -20
    if spend >= 300 and revenue <= 0 and clicks >= 20:
        return "pause_until_card_fix", "Реклама дала клики, но не дала заказов.", -100
    if drr > target_drr * 1.4 and conversion_rate < 0.025:
        return "fix_card_or_price_before_scaling", "ДРР выше цели, а конверсия слабая.", -20
    if impressions >= 1000 and ctr < 0.01:
        return "rewrite_creative_or_search_query", "CTR ниже 1% на достаточном объеме показов.", -10
    if gross_profit < 0 and spend > 0:
        return "reduce_bid_and_check_unit_economics", "Кампания убыточна после рекламного расхода.", -15
    if drr <= target_drr * 0.75 and orders >= 5 and stock_units > 20:
        return "scale_budget", "ДРР заметно ниже цели, остатки позволяют масштабирование.", 10
    if ctr >= 0.025 and conversion_rate < 0.03:
        return "check_card_conversion", "Качество трафика приемлемое, но заказов мало.", 0
    return "monitor", "Метрики близки к целевому диапазону.", 0


def classify_profit_status(gross_profit: float, drr: float, target_drr: float) -> str:
    if gross_profit < 0:
        return "loss_after_ads"
    if drr > target_drr * 1.25:
        return "profitable_but_inefficient"
    if drr <= target_drr:
        return "within_target"
    return "watch"


def classify_risk_level(
    *,
    action: str,
    drr: float,
    gross_profit: float,
    stock_units: int,
) -> str:
    if action == "pause_until_card_fix" or gross_profit < 0 or drr > 0.5:
        return "high"
    if stock_units <= 10 or action in {
        "cap_spend_low_stock",
        "fix_card_or_price_before_scaling",
        "reduce_bid_and_check_unit_economics",
    }:
        return "medium"
    if action == "scale_budget":
        return "opportunity"
    return "low"


def build_next_step(action: str, bid_delta: int) -> str:
    steps = {
        "cap_spend_low_stock": "Ограничить расход до пополнения остатков; уведомить ответственного за поставки.",
        "pause_until_card_fix": "Поставить кампанию на паузу и проверить конверсию карточки перед перезапуском.",
        "fix_card_or_price_before_scaling": "Проверить цену, заголовок, rich content и отзывы до повышения ставки.",
        "rewrite_creative_or_search_query": "Переписать связку запроса/креатива; бюджет пока держать ограниченным.",
        "reduce_bid_and_check_unit_economics": "Снизить ставку и проверить маржу, комиссию и логистику.",
        "scale_budget": "Аккуратно увеличить бюджет и проверить остатки плюс ДРР на следующем обновлении.",
        "check_card_conversion": "Проверить блокеры конверсии карточки: цену, рейтинг, контент и доставку.",
        "monitor": "Без срочных изменений; оставить кампанию в ежедневном мониторинге.",
    }
    step = steps.get(action, "Нужна ручная проверка.")
    if bid_delta:
        step = f"{step} Рекомендуемое изменение ставки: {bid_delta}%."
    return step


def build_decision_audit(
    *,
    action: str,
    ctr: float,
    conversion_rate: float,
    drr: float,
    gross_profit: float,
    stock_units: int,
    target_drr: float,
) -> tuple[str, list[str]]:
    signals: list[str] = []
    if drr > target_drr * 1.4:
        signals.append(f"drr_above_target:{drr:.4f}>{target_drr:.4f}")
    if gross_profit < 0:
        signals.append(f"negative_profit:{gross_profit:.2f}")
    if conversion_rate < 0.025:
        signals.append(f"low_conversion:{conversion_rate:.4f}")
    if ctr < 0.01:
        signals.append(f"low_ctr:{ctr:.4f}")
    if stock_units <= 10:
        signals.append(f"low_stock:{stock_units}")
    if action == "scale_budget":
        signals.append("scale_candidate")
    if not signals:
        signals.append("no_critical_signal")

    high_confidence_actions = {
        "pause_until_card_fix",
        "reduce_bid_and_check_unit_economics",
        "cap_spend_low_stock",
        "scale_budget",
    }
    if action in high_confidence_actions and len(signals) >= 2:
        confidence = "high"
    elif action == "monitor":
        confidence = "medium"
    else:
        confidence = "medium" if signals else "low"
    return confidence, signals


def summarize_campaigns(report_rows: list[Mapping[str, Any]]) -> dict[str, float]:
    spend = sum(parse_float(row.get("spend_rub")) for row in report_rows)
    revenue = sum(parse_float(row.get("revenue_rub")) for row in report_rows)
    orders = sum(parse_int(row.get("orders")) for row in report_rows)
    profit = sum(parse_float(row.get("gross_profit_rub")) for row in report_rows)
    clicks = sum(parse_int(row.get("clicks")) for row in report_rows)
    impressions = sum(parse_int(row.get("impressions")) for row in report_rows)
    return {
        "spend_rub": spend,
        "revenue_rub": revenue,
        "orders": orders,
        "gross_profit_rub": profit,
        "ctr": safe_div(clicks, impressions),
        "drr": safe_div(spend, revenue),
        "roas": safe_div(revenue, spend),
    }


def render_ads_markdown(report_rows: list[Mapping[str, Any]], target_drr: float) -> str:
    summary = summarize_campaigns(report_rows)
    risk_rows = [
        row
        for row in report_rows
        if row["recommended_action"] not in {"monitor", "scale_budget"}
    ][:8]
    scale_rows = [
        row for row in report_rows if row["recommended_action"] == "scale_budget"
    ][:5]
    compact_columns = [
        "маркетплейс",
        "кампания",
        "sku",
        "расход",
        "выручка",
        "ДРР",
        "прибыль",
        "статус_прибыли",
        "риск",
        "рекомендация",
        "следующий_шаг",
        "причина",
    ]
    report_display_rows = [ads_display_row(row) for row in report_rows]
    risk_display_rows = [ads_display_row(row) for row in risk_rows]
    scale_display_rows = [ads_display_row(row) for row in scale_rows]
    return "\n".join(
        [
            "# Отчет по рекламным кампаниям",
            "",
            f"- Целевой ДРР: {pct(target_drr)}",
            f"- Расход: {money(summary['spend_rub'])}",
            f"- Выручка: {money(summary['revenue_rub'])}",
            f"- Заказы: {int(summary['orders'])}",
            f"- Общий ДРР: {pct(summary['drr'])}",
            f"- ROAS: {summary['roas']:.2f}",
            f"- Прибыль после рекламы: {money(summary['gross_profit_rub'])}",
            "",
            "## Рисковые кампании",
            "",
            markdown_table(risk_display_rows, compact_columns),
            "",
            "## Кандидаты на масштабирование",
            "",
            markdown_table(scale_display_rows, compact_columns),
            "",
            "## Все кампании",
            "",
            markdown_table(report_display_rows, compact_columns),
            "",
        ]
    )


def ads_display_row(row: Mapping[str, Any]) -> dict[str, str]:
    return {
        "маркетплейс": str(row.get("marketplace", "")),
        "кампания": str(row.get("campaign_name", "")),
        "sku": str(row.get("sku", "")),
        "расход": money(parse_float(row.get("spend_rub"))),
        "выручка": money(parse_float(row.get("revenue_rub"))),
        "ДРР": pct(parse_float(row.get("drr"))),
        "прибыль": money(parse_float(row.get("gross_profit_rub"))),
        "статус_прибыли": PROFIT_STATUS_LABELS.get(str(row.get("profit_status", "")), str(row.get("profit_status", ""))),
        "риск": RISK_LEVEL_LABELS.get(str(row.get("risk_level", "")), str(row.get("risk_level", ""))),
        "рекомендация": ACTION_LABELS.get(str(row.get("recommended_action", "")), str(row.get("recommended_action", ""))),
        "следующий_шаг": str(row.get("next_step", "")),
        "причина": str(row.get("reason", "")),
    }


def run_ads_report(
    input_path: Path,
    out_dir: Path,
    target_drr: float = 0.18,
    unit_economics: Mapping[tuple[str, str], Mapping[str, Any]] | None = None,
) -> dict[str, Path]:
    rows = read_csv(input_path)
    validate_rows(rows, required_columns=ADS_DAILY_REQUIRED, dataset_name="ads_daily")
    report_rows = build_campaign_report(
        rows,
        target_drr=target_drr,
        unit_economics=unit_economics,
    )
    summary = summarize_campaigns(report_rows)

    csv_path = out_dir / "ads_campaign_report.csv"
    audit_path = out_dir / "ads_decision_audit.csv"
    markdown_path = out_dir / "ads_report.md"
    html_path = out_dir / "ads_dashboard.html"
    json_path = out_dir / "ads_summary.json"

    write_csv(csv_path, report_rows, ADS_COLUMNS)
    write_csv(audit_path, report_rows, ADS_AUDIT_COLUMNS)
    write_text(markdown_path, render_ads_markdown(report_rows, target_drr))
    write_json(json_path, {"summary": summary, "rows": report_rows})
    write_text(
        html_path,
        html_report(
            title="Помощник по рекламным кампаниям",
            subtitle="Отчет по кампаниям WB/Ozon: ДРР, ROAS, прибыль и рекомендации по действиям.",
            cards=[
                ("Расход", money(summary["spend_rub"])),
                ("Выручка", money(summary["revenue_rub"])),
                ("Заказы", str(int(summary["orders"]))),
                ("ДРР", pct(summary["drr"])),
                ("ROAS", f"{summary['roas']:.2f}"),
                ("Прибыль после рекламы", money(summary["gross_profit_rub"])),
            ],
            table_rows=report_rows,
            columns=ADS_COLUMNS,
        ),
    )
    return {
        "csv": csv_path,
        "audit_csv": audit_path,
        "markdown": markdown_path,
        "html": html_path,
        "json": json_path,
    }
