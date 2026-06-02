from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol

from marketplace_automation.io_utils import parse_float, parse_int


class JsonHttpTransport(Protocol):
    def get(self, url: str, headers: Mapping[str, str], params: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError

    def post(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        raise NotImplementedError


@dataclass(frozen=True)
class WildberriesAdsConfig:
    api_token: str
    base_url: str = "https://advert-api.wildberries.ru"


@dataclass(frozen=True)
class OzonAdsConfig:
    client_id: str
    api_key: str
    base_url: str = "https://api-seller.ozon.ru"


class RequestsJsonTransport:
    def __init__(self) -> None:
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("Marketplace adapters require optional dependency: pip install requests") from exc
        self._requests = requests

    def get(self, url: str, headers: Mapping[str, str], params: Mapping[str, Any]) -> Mapping[str, Any]:
        response = self._requests.get(url, headers=dict(headers), params=dict(params), timeout=30)
        response.raise_for_status()
        return response.json()

    def post(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        response = self._requests.post(url, headers=dict(headers), json=json, timeout=30)
        response.raise_for_status()
        return response.json()


class WildberriesAdsClient:
    def __init__(
        self,
        config: WildberriesAdsConfig,
        transport: JsonHttpTransport | None = None,
    ) -> None:
        self.config = config
        self.transport = transport or RequestsJsonTransport()

    def fetch_ads_daily(self, date_from: str, date_to: str) -> list[dict[str, Any]]:
        payload = self.transport.get(
            f"{self.config.base_url}/adv/v2/fullstats",
            headers={"Authorization": self.config.api_token},
            params={"dateFrom": date_from, "dateTo": date_to},
        )
        return [normalize_wb_ads_row(row) for row in payload.get("rows", payload.get("data", []))]


class OzonAdsClient:
    def __init__(
        self,
        config: OzonAdsConfig,
        transport: JsonHttpTransport | None = None,
    ) -> None:
        self.config = config
        self.transport = transport or RequestsJsonTransport()

    def fetch_ads_daily(self, date_from: str, date_to: str) -> list[dict[str, Any]]:
        payload = self.transport.post(
            f"{self.config.base_url}/performance/v1/statistics",
            headers={
                "Client-Id": self.config.client_id,
                "Api-Key": self.config.api_key,
                "Content-Type": "application/json",
            },
            json={"date_from": date_from, "date_to": date_to},
        )
        return [normalize_ozon_ads_row(row) for row in payload.get("rows", payload.get("result", []))]


def normalize_wb_ads_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "date": row.get("date", ""),
        "marketplace": "WB",
        "campaign_id": str(row.get("advertId", row.get("campaign_id", ""))),
        "campaign_name": row.get("campaignName", row.get("campaign_name", "")),
        "sku": str(row.get("nmId", row.get("sku", ""))),
        "product_name": row.get("name", row.get("product_name", "")),
        "impressions": parse_int(row.get("views", row.get("impressions"))),
        "clicks": parse_int(row.get("clicks")),
        "spend_rub": parse_float(row.get("sum", row.get("spend_rub"))),
        "orders": parse_int(row.get("orders")),
        "revenue_rub": parse_float(row.get("sum_price", row.get("revenue_rub"))),
        "margin_rate": parse_float(row.get("margin_rate"), 0.0),
        "stock_units": parse_int(row.get("stock_units")),
        "ad_position": parse_float(row.get("position", row.get("ad_position"))),
        "bid_rub": parse_float(row.get("cpm", row.get("bid_rub"))),
    }


def normalize_ozon_ads_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "date": row.get("date", ""),
        "marketplace": "Ozon",
        "campaign_id": str(row.get("campaign_id", "")),
        "campaign_name": row.get("campaign_name", ""),
        "sku": str(row.get("sku", row.get("offer_id", ""))),
        "product_name": row.get("product_name", row.get("title", "")),
        "impressions": parse_int(row.get("views", row.get("impressions"))),
        "clicks": parse_int(row.get("clicks")),
        "spend_rub": parse_float(row.get("moneySpent", row.get("spend_rub"))),
        "orders": parse_int(row.get("orders")),
        "revenue_rub": parse_float(row.get("revenue", row.get("revenue_rub"))),
        "margin_rate": parse_float(row.get("margin_rate"), 0.0),
        "stock_units": parse_int(row.get("stock_units")),
        "ad_position": parse_float(row.get("ad_position")),
        "bid_rub": parse_float(row.get("bid", row.get("bid_rub"))),
    }

