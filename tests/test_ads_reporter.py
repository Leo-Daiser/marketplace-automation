from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.ads_reporter import build_campaign_report  # noqa: E402


class AdsReporterTest(unittest.TestCase):
    def test_campaign_with_clicks_and_no_revenue_is_paused(self) -> None:
        rows = [
            {
                "marketplace": "WB",
                "campaign_id": "C-1",
                "campaign_name": "Bad broad query",
                "sku": "SKU-1",
                "product_name": "Test product",
                "impressions": "5000",
                "clicks": "30",
                "spend_rub": "900",
                "orders": "0",
                "revenue_rub": "0",
                "margin_rate": "0.45",
                "stock_units": "100",
                "bid_rub": "30",
            }
        ]
        report = build_campaign_report(rows, target_drr=0.18)
        self.assertEqual(report[0]["recommended_action"], "pause_until_card_fix")
        self.assertEqual(report[0]["bid_delta_pct"], -100)

    def test_profitable_low_drr_campaign_is_scale_candidate(self) -> None:
        rows = [
            {
                "marketplace": "Ozon",
                "campaign_id": "C-2",
                "campaign_name": "Good exact query",
                "sku": "SKU-2",
                "product_name": "Good product",
                "impressions": "10000",
                "clicks": "400",
                "spend_rub": "8000",
                "orders": "40",
                "revenue_rub": "80000",
                "margin_rate": "0.5",
                "stock_units": "150",
                "bid_rub": "20",
            }
        ]
        report = build_campaign_report(rows, target_drr=0.18)
        self.assertEqual(report[0]["recommended_action"], "scale_budget")
        self.assertAlmostEqual(report[0]["drr"], 0.1)


if __name__ == "__main__":
    unittest.main()

