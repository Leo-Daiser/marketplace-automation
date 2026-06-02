from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.ads_reporter import build_campaign_report  # noqa: E402
from marketplace_automation.unit_economics import build_unit_economics  # noqa: E402


class UnitEconomicsTest(unittest.TestCase):
    def test_unit_economics_calculates_break_even_drr(self) -> None:
        models = build_unit_economics(
            [
                {
                    "sku": "SKU-1",
                    "marketplace": "WB",
                    "price_rub": "1000",
                    "cogs_rub": "400",
                    "marketplace_fee_rate": "0.2",
                    "logistics_rub": "80",
                    "storage_rub": "20",
                    "return_rate": "0.05",
                    "tax_rate": "0.06",
                    "target_profit_rate": "0.1",
                }
            ]
        )
        model = models[("SKU-1", "WB")]
        self.assertAlmostEqual(model["contribution_margin_rate"], 0.236)
        self.assertAlmostEqual(model["break_even_drr"], 0.236)
        self.assertAlmostEqual(model["target_drr"], 0.136)

    def test_ads_report_uses_unit_economics_margin(self) -> None:
        unit_models = build_unit_economics(
            [
                {
                    "sku": "SKU-1",
                    "marketplace": "WB",
                    "price_rub": "1000",
                    "cogs_rub": "400",
                    "marketplace_fee_rate": "0.2",
                    "logistics_rub": "80",
                    "storage_rub": "20",
                    "return_rate": "0.05",
                    "tax_rate": "0.06",
                    "target_profit_rate": "0.1",
                }
            ]
        )
        report = build_campaign_report(
            [
                {
                    "marketplace": "WB",
                    "campaign_id": "C-1",
                    "campaign_name": "Unit economics campaign",
                    "sku": "SKU-1",
                    "product_name": "Test",
                    "impressions": "1000",
                    "clicks": "100",
                    "spend_rub": "150",
                    "orders": "10",
                    "revenue_rub": "1000",
                    "margin_rate": "0.99",
                    "stock_units": "100",
                    "bid_rub": "10",
                }
            ],
            target_drr=0.18,
            unit_economics=unit_models,
        )
        self.assertEqual(report[0]["break_even_drr"], 0.236)
        self.assertEqual(report[0]["unit_target_drr"], 0.136)
        self.assertEqual(report[0]["gross_profit_rub"], 86.0)


if __name__ == "__main__":
    unittest.main()

