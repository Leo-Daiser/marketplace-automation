from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .io_utils import parse_bool, parse_float, parse_int


@dataclass(frozen=True)
class AdsDailyRow:
    date: str
    marketplace: str
    campaign_id: str
    campaign_name: str
    sku: str
    product_name: str
    impressions: int
    clicks: int
    spend_rub: float
    orders: int
    revenue_rub: float
    margin_rate: float
    stock_units: int
    ad_position: float
    bid_rub: float

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> "AdsDailyRow":
        return cls(
            date=str(row.get("date", "")),
            marketplace=str(row.get("marketplace", "")),
            campaign_id=str(row.get("campaign_id", "")),
            campaign_name=str(row.get("campaign_name", "")),
            sku=str(row.get("sku", "")),
            product_name=str(row.get("product_name", "")),
            impressions=parse_int(row.get("impressions")),
            clicks=parse_int(row.get("clicks")),
            spend_rub=parse_float(row.get("spend_rub")),
            orders=parse_int(row.get("orders")),
            revenue_rub=parse_float(row.get("revenue_rub")),
            margin_rate=parse_float(row.get("margin_rate")),
            stock_units=parse_int(row.get("stock_units")),
            ad_position=parse_float(row.get("ad_position")),
            bid_rub=parse_float(row.get("bid_rub")),
        )


@dataclass(frozen=True)
class ReviewRow:
    review_id: str
    date: str
    marketplace: str
    sku: str
    rating: int
    text: str
    has_photo: bool
    order_id: str = ""

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> "ReviewRow":
        return cls(
            review_id=str(row.get("review_id", "")),
            date=str(row.get("date", "")),
            marketplace=str(row.get("marketplace", "")),
            sku=str(row.get("sku", "")),
            rating=parse_int(row.get("rating")),
            text=str(row.get("text", "")),
            has_photo=parse_bool(row.get("has_photo")),
            order_id=str(row.get("order_id", "")),
        )


@dataclass(frozen=True)
class CompetitorRow:
    date: str
    marketplace: str
    keyword: str
    competitor_brand: str
    product_name: str
    sku: str
    price_rub: float
    rating: float
    reviews_count: int
    organic_position: int
    ad_position: int
    stock_status: str
    title: str
    bullets: str

    @classmethod
    def from_mapping(cls, row: Mapping[str, Any]) -> "CompetitorRow":
        return cls(
            date=str(row.get("date", "")),
            marketplace=str(row.get("marketplace", "")),
            keyword=str(row.get("keyword", "")),
            competitor_brand=str(row.get("competitor_brand", "")),
            product_name=str(row.get("product_name", "")),
            sku=str(row.get("sku", "")),
            price_rub=parse_float(row.get("price_rub")),
            rating=parse_float(row.get("rating")),
            reviews_count=parse_int(row.get("reviews_count")),
            organic_position=parse_int(row.get("organic_position")),
            ad_position=parse_int(row.get("ad_position")),
            stock_status=str(row.get("stock_status", "")),
            title=str(row.get("title", "")),
            bullets=str(row.get("bullets", "")),
        )

