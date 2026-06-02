from __future__ import annotations

from typing import Any, Mapping


ADS_DAILY_REQUIRED = {
    "date",
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
    "margin_rate",
    "stock_units",
    "bid_rub",
}

REVIEWS_REQUIRED = {
    "review_id",
    "date",
    "marketplace",
    "sku",
    "rating",
    "text",
    "has_photo",
}

COMPETITORS_REQUIRED = {
    "date",
    "marketplace",
    "keyword",
    "competitor_brand",
    "product_name",
    "sku",
    "price_rub",
    "rating",
    "reviews_count",
    "organic_position",
    "ad_position",
    "stock_status",
    "title",
    "bullets",
}

OUR_PRODUCTS_REQUIRED = {
    "sku",
    "product_name",
    "price_rub",
    "rating",
    "reviews_count",
    "stock_units",
    "margin_rate",
}

KEYWORD_PLAN_REQUIRED = {
    "keyword",
    "marketplace",
    "our_sku",
    "priority",
    "our_current_position",
    "target_position",
}

UNIT_ECONOMICS_REQUIRED = {
    "sku",
    "product_name",
    "marketplace",
    "price_rub",
    "cogs_rub",
    "marketplace_fee_rate",
    "logistics_rub",
    "storage_rub",
    "return_rate",
    "tax_rate",
    "target_profit_rate",
}


class SchemaValidationError(ValueError):
    """Raised when a table does not match the expected input contract."""


def validate_rows(
    rows: list[Mapping[str, Any]],
    *,
    required_columns: set[str],
    dataset_name: str,
) -> None:
    if not rows:
        raise SchemaValidationError(f"{dataset_name}: input table is empty.")

    available = set(rows[0].keys())
    missing = sorted(required_columns - available)
    if missing:
        raise SchemaValidationError(
            f"{dataset_name}: missing required columns: {', '.join(missing)}."
        )

    empty_required_rows: list[int] = []
    for index, row in enumerate(rows, start=2):
        if any(str(row.get(column, "")).strip() == "" for column in required_columns):
            empty_required_rows.append(index)
    if empty_required_rows:
        preview = ", ".join(str(row_number) for row_number in empty_required_rows[:5])
        raise SchemaValidationError(
            f"{dataset_name}: empty required values at CSV rows: {preview}."
        )
