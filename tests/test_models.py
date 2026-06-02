from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.models import AdsDailyRow, CompetitorRow, ReviewRow  # noqa: E402


class ModelsTest(unittest.TestCase):
    def test_ads_daily_row_parses_numbers(self) -> None:
        row = AdsDailyRow.from_mapping(
            {
                "marketplace": "WB",
                "campaign_id": 10,
                "sku": 20,
                "impressions": "1000",
                "clicks": "50",
                "spend_rub": "1200.5",
                "orders": "7",
                "revenue_rub": "9000",
                "margin_rate": "0.4",
                "stock_units": "12",
                "ad_position": "3.5",
                "bid_rub": "40",
            }
        )
        self.assertEqual(row.campaign_id, "10")
        self.assertEqual(row.sku, "20")
        self.assertEqual(row.impressions, 1000)
        self.assertEqual(row.spend_rub, 1200.5)

    def test_review_row_parses_boolean(self) -> None:
        row = ReviewRow.from_mapping({"review_id": "R-1", "rating": "5", "has_photo": "true"})
        self.assertTrue(row.has_photo)
        self.assertEqual(row.rating, 5)

    def test_competitor_row_parses_positions(self) -> None:
        row = CompetitorRow.from_mapping(
            {
                "price_rub": "1590",
                "rating": "4.7",
                "reviews_count": "1200",
                "organic_position": "3",
                "ad_position": "1",
            }
        )
        self.assertEqual(row.price_rub, 1590.0)
        self.assertEqual(row.organic_position, 3)


if __name__ == "__main__":
    unittest.main()

