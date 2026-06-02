from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any, Mapping

from .io_utils import (
    markdown_table,
    money,
    parse_float,
    parse_int,
    read_csv,
    safe_div,
    write_csv,
    write_json,
    write_text,
)
from .models import CompetitorRow
from .schemas import (
    COMPETITORS_REQUIRED,
    KEYWORD_PLAN_REQUIRED,
    OUR_PRODUCTS_REQUIRED,
    validate_rows,
)


OPPORTUNITY_COLUMNS = [
    "keyword",
    "marketplace",
    "our_sku",
    "priority",
    "our_price_rub",
    "median_competitor_price_rub",
    "price_index",
    "our_rating",
    "avg_competitor_rating",
    "rating_gap",
    "our_reviews_count",
    "median_competitor_reviews",
    "review_gap",
    "our_current_position",
    "target_position",
    "position_gap",
    "ad_pressure",
    "opportunity_score",
    "recommended_action",
    "reason",
]

TASK_COLUMNS = [
    "task_id",
    "keyword",
    "our_sku",
    "priority",
    "owner",
    "impact",
    "due_in_days",
    "task_type",
    "title",
    "brief",
    "suggested_terms",
]

STOPWORDS = {
    "для",
    "и",
    "с",
    "на",
    "в",
    "по",
    "от",
    "без",
    "капсулы",
    "комплекс",
    "brand",
    "the",
    "and",
    "with",
}


def build_competitor_report(
    competitor_rows: list[Mapping[str, Any]],
    our_product_rows: list[Mapping[str, Any]],
    keyword_plan_rows: list[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    our_products = {str(row.get("sku", "")).strip(): row for row in our_product_rows}
    competitors_by_key: dict[tuple[str, str], list[CompetitorRow]] = defaultdict(list)
    for row in competitor_rows:
        competitor = CompetitorRow.from_mapping(row)
        key = (competitor.keyword.strip(), competitor.marketplace.strip())
        competitors_by_key[key].append(competitor)

    opportunities: list[dict[str, Any]] = []
    tasks: list[dict[str, Any]] = []
    for plan in keyword_plan_rows:
        keyword = str(plan.get("keyword", "")).strip()
        marketplace = str(plan.get("marketplace", "")).strip()
        our_sku = str(plan.get("our_sku", "")).strip()
        priority = str(plan.get("priority", "medium")).strip().lower()
        our_product = our_products.get(our_sku, {})
        competitors = competitors_by_key.get((keyword, marketplace), [])
        if not competitors:
            continue
        opportunity = evaluate_keyword(
            keyword=keyword,
            marketplace=marketplace,
            priority=priority,
            our_sku=our_sku,
            our_product=our_product,
            plan=plan,
            competitors=competitors,
        )
        opportunities.append(opportunity)
        tasks.append(build_content_task(opportunity, competitors))
    opportunities.sort(key=lambda row: row["opportunity_score"], reverse=True)
    tasks.sort(key=lambda row: row["priority"])
    return opportunities, tasks


def evaluate_keyword(
    *,
    keyword: str,
    marketplace: str,
    priority: str,
    our_sku: str,
    our_product: Mapping[str, Any],
    plan: Mapping[str, Any],
    competitors: list[CompetitorRow],
) -> dict[str, Any]:
    competitor_prices = [row.price_rub for row in competitors if row.price_rub > 0]
    competitor_ratings = [row.rating for row in competitors if row.rating > 0]
    competitor_reviews = [row.reviews_count for row in competitors]
    competitor_ad_positions = [row.ad_position for row in competitors]

    median_price = median(competitor_prices) if competitor_prices else 0.0
    avg_rating = safe_div(sum(competitor_ratings), len(competitor_ratings))
    median_reviews = median(competitor_reviews) if competitor_reviews else 0
    ad_pressure = sum(1 for position in competitor_ad_positions if 0 < position <= 5)

    our_price = parse_float(our_product.get("price_rub"))
    our_rating = parse_float(our_product.get("rating"))
    our_reviews = parse_int(our_product.get("reviews_count"))
    our_current_position = parse_int(plan.get("our_current_position"))
    target_position = parse_int(plan.get("target_position"), 5)
    position_gap = max(0, our_current_position - target_position)
    price_index = safe_div(our_price, median_price)
    rating_gap = max(0.0, avg_rating - our_rating)
    review_gap = max(0, int(median_reviews - our_reviews))
    priority_weight = {"high": 3.0, "medium": 2.0, "low": 1.0}.get(priority, 2.0)
    opportunity_score = (
        priority_weight
        + min(position_gap / 8, 3)
        + min(review_gap / 500, 3)
        + min(ad_pressure / 2, 2)
        + (1.5 if price_index > 1.12 else 0)
        + (1.0 if rating_gap >= 0.15 else 0)
    )
    action, reason = recommend_keyword_action(
        price_index=price_index,
        review_gap=review_gap,
        rating_gap=rating_gap,
        position_gap=position_gap,
        ad_pressure=ad_pressure,
    )
    return {
        "keyword": keyword,
        "marketplace": marketplace,
        "our_sku": our_sku,
        "priority": priority,
        "our_price_rub": round(our_price, 2),
        "median_competitor_price_rub": round(median_price, 2),
        "price_index": round(price_index, 3),
        "our_rating": round(our_rating, 2),
        "avg_competitor_rating": round(avg_rating, 2),
        "rating_gap": round(rating_gap, 2),
        "our_reviews_count": our_reviews,
        "median_competitor_reviews": int(median_reviews),
        "review_gap": review_gap,
        "our_current_position": our_current_position,
        "target_position": target_position,
        "position_gap": position_gap,
        "ad_pressure": ad_pressure,
        "opportunity_score": round(opportunity_score, 2),
        "recommended_action": action,
        "reason": reason,
    }


def recommend_keyword_action(
    *,
    price_index: float,
    review_gap: int,
    rating_gap: float,
    position_gap: int,
    ad_pressure: int,
) -> tuple[str, str]:
    if price_index > 1.12:
        return "check_price_or_bundle", "Наша цена заметно выше медианы конкурентов."
    if rating_gap >= 0.2:
        return "investigate_quality_gap", "Рейтинг конкурентов достаточно выше, чтобы влиять на конверсию."
    if review_gap >= 500:
        return "increase_review_collection", "У конкурентов сильное преимущество по социальному доказательству."
    if position_gap >= 6:
        return "rewrite_title_and_seo", "Органическая позиция далека от целевой."
    if ad_pressure >= 3:
        return "test_search_ad_campaign", "Конкуренты занимают верхние рекламные позиции."
    return "monitor", "Критичный конкурентный разрыв не найден."


def build_content_task(
    opportunity: Mapping[str, Any],
    competitors: list[CompetitorRow],
) -> dict[str, Any]:
    keyword = str(opportunity["keyword"])
    terms = extract_suggested_terms(competitors)
    action = str(opportunity["recommended_action"])
    if action == "check_price_or_bundle":
        task_type = "unit_economics"
        owner = "growth/performance"
        impact = "margin_and_conversion"
        due_in_days = 2
        title = f"Проверить цену, комплект или промо для '{keyword}'"
    elif action == "increase_review_collection":
        task_type = "review_growth"
        owner = "support/retention"
        impact = "social_proof"
        due_in_days = 5
        title = f"Подготовить механику роста отзывов для '{keyword}'"
    elif action == "investigate_quality_gap":
        task_type = "quality_analysis"
        owner = "product/quality"
        impact = "conversion_and_rating"
        due_in_days = 3
        title = f"Разобрать разрыв рейтинга по '{keyword}'"
    else:
        task_type = "seo_content"
        owner = "seo/content"
        impact = "organic_visibility"
        due_in_days = 4
        title = f"Переписать заголовок и буллеты для '{keyword}'"
    brief = (
        f"Ключ: {keyword}. Действие: {action}. "
        f"Разрыв позиции: {opportunity['position_gap']}. Разрыв отзывов: {opportunity['review_gap']}. "
        f"Использовать термины конкурентов аккуратно, без копирования точных заголовков."
    )
    return {
        "task_id": f"SEO-{slugify(keyword)}",
        "keyword": keyword,
        "our_sku": opportunity["our_sku"],
        "priority": opportunity["priority"],
        "owner": owner,
        "impact": impact,
        "due_in_days": due_in_days,
        "task_type": task_type,
        "title": title,
        "brief": brief,
        "suggested_terms": ", ".join(terms),
    }


def extract_suggested_terms(competitors: list[CompetitorRow], limit: int = 10) -> list[str]:
    counter: Counter[str] = Counter()
    for row in competitors:
        text = f"{row.title} {row.bullets}".lower()
        for token in re.findall(r"[a-zа-я0-9]+", text, flags=re.IGNORECASE):
            token = token.strip().lower()
            if len(token) >= 4 and token not in STOPWORDS:
                counter[token] += 1
    return [term for term, _ in counter.most_common(limit)]


def slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Zа-яА-Я0-9]+", "-", value.strip().lower())
    return cleaned.strip("-")[:50]


def render_competitor_digest(
    opportunities: list[Mapping[str, Any]],
    tasks: list[Mapping[str, Any]],
) -> str:
    top_opportunities = opportunities[:8]
    top_tasks = tasks[:8]
    columns = [
        "keyword",
        "marketplace",
        "our_sku",
        "opportunity_score",
        "recommended_action",
        "reason",
    ]
    task_columns = [
        "task_id",
        "priority",
        "owner",
        "impact",
        "due_in_days",
        "task_type",
        "title",
        "suggested_terms",
    ]
    high_score = sum(1 for row in opportunities if parse_float(row["opportunity_score"]) >= 6)
    return "\n".join(
        [
            "# Дайджест конкурентного SEO-мониторинга",
            "",
            f"- Обработано ключей: {len(opportunities)}",
            f"- Сильные возможности: {high_score}",
            f"- Создано content/SEO задач: {len(tasks)}",
            "",
            "## Главные возможности",
            "",
            markdown_table(top_opportunities, columns),
            "",
            "## SEO/content backlog",
            "",
            markdown_table(top_tasks, task_columns),
            "",
            "## Бюджетный сигнал",
            "",
            f"Максимальное ценовое давление по ключам: {money(max((parse_float(row['our_price_rub']) for row in opportunities), default=0))}",
            "",
        ]
    )


def run_competitor_monitor(
    competitors_path: Path,
    our_products_path: Path,
    keyword_plan_path: Path,
    out_dir: Path,
) -> dict[str, Path]:
    competitor_rows = read_csv(competitors_path)
    our_product_rows = read_csv(our_products_path)
    keyword_plan_rows = read_csv(keyword_plan_path)
    validate_rows(
        competitor_rows,
        required_columns=COMPETITORS_REQUIRED,
        dataset_name="competitors",
    )
    validate_rows(
        our_product_rows,
        required_columns=OUR_PRODUCTS_REQUIRED,
        dataset_name="our_products",
    )
    validate_rows(
        keyword_plan_rows,
        required_columns=KEYWORD_PLAN_REQUIRED,
        dataset_name="keyword_plan",
    )
    opportunities, tasks = build_competitor_report(
        competitor_rows,
        our_product_rows,
        keyword_plan_rows,
    )
    opportunities_path = out_dir / "competitor_opportunities.csv"
    tasks_path = out_dir / "seo_content_tasks.csv"
    digest_path = out_dir / "competitor_digest.md"
    json_path = out_dir / "competitor_monitor_payload.json"
    write_csv(opportunities_path, opportunities, OPPORTUNITY_COLUMNS)
    write_csv(tasks_path, tasks, TASK_COLUMNS)
    write_text(digest_path, render_competitor_digest(opportunities, tasks))
    write_json(json_path, {"opportunities": opportunities, "tasks": tasks})
    return {
        "opportunities": opportunities_path,
        "tasks": tasks_path,
        "digest": digest_path,
        "json": json_path,
    }
