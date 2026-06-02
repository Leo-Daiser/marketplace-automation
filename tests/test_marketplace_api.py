from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.adapters.marketplace_api import (  # noqa: E402
    OzonAdsClient,
    OzonAdsConfig,
    WildberriesAdsClient,
    WildberriesAdsConfig,
    normalize_ozon_ads_row,
    normalize_wb_ads_row,
)


class FakeMarketplaceTransport:
    def __init__(self) -> None:
        self.last_url = ""
        self.last_headers: Mapping[str, str] = {}
        self.last_params: Mapping[str, Any] = {}
        self.last_json: Mapping[str, Any] = {}

    def get(self, url: str, headers: Mapping[str, str], params: Mapping[str, Any]) -> Mapping[str, Any]:
        self.last_url = url
        self.last_headers = headers
        self.last_params = params
        return {"rows": [{"advertId": 11, "nmId": 22, "views": 100, "clicks": 5, "sum": 200}]}

    def post(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        self.last_url = url
        self.last_headers = headers
        self.last_json = json
        return {"result": [{"campaign_id": 7, "sku": "SKU-1", "views": 200, "clicks": 10, "moneySpent": 300}]}


class MarketplaceApiTest(unittest.TestCase):
    def test_normalize_wb_ads_row(self) -> None:
        row = normalize_wb_ads_row({"advertId": 10, "nmId": 20, "views": "1000", "clicks": "50", "sum": "1200"})
        self.assertEqual(row["marketplace"], "WB")
        self.assertEqual(row["campaign_id"], "10")
        self.assertEqual(row["sku"], "20")
        self.assertEqual(row["impressions"], 1000)
        self.assertEqual(row["spend_rub"], 1200.0)

    def test_normalize_ozon_ads_row(self) -> None:
        row = normalize_ozon_ads_row({"campaign_id": 3, "offer_id": "O-1", "views": "500", "moneySpent": "700"})
        self.assertEqual(row["marketplace"], "Ozon")
        self.assertEqual(row["campaign_id"], "3")
        self.assertEqual(row["sku"], "O-1")
        self.assertEqual(row["impressions"], 500)
        self.assertEqual(row["spend_rub"], 700.0)

    def test_wb_client_uses_auth_and_dates(self) -> None:
        transport = FakeMarketplaceTransport()
        client = WildberriesAdsClient(WildberriesAdsConfig(api_token="wb-token"), transport)
        rows = client.fetch_ads_daily("2026-05-01", "2026-05-31")
        self.assertIn("/adv/v2/fullstats", transport.last_url)
        self.assertEqual(transport.last_headers["Authorization"], "wb-token")
        self.assertEqual(transport.last_params["dateFrom"], "2026-05-01")
        self.assertEqual(rows[0]["marketplace"], "WB")

    def test_ozon_client_uses_headers_and_dates(self) -> None:
        transport = FakeMarketplaceTransport()
        client = OzonAdsClient(OzonAdsConfig(client_id="cid", api_key="key"), transport)
        rows = client.fetch_ads_daily("2026-05-01", "2026-05-31")
        self.assertIn("/performance/v1/statistics", transport.last_url)
        self.assertEqual(transport.last_headers["Client-Id"], "cid")
        self.assertEqual(transport.last_headers["Api-Key"], "key")
        self.assertEqual(transport.last_json["date_from"], "2026-05-01")
        self.assertEqual(rows[0]["marketplace"], "Ozon")


if __name__ == "__main__":
    unittest.main()

