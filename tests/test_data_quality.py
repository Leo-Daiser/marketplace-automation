from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.data_quality import (  # noqa: E402
    check_ads_suspicious_metrics,
    check_review_suspicious_values,
    check_unit_economics_values,
)


class DataQualityTest(unittest.TestCase):
    def test_ads_quality_detects_clicks_above_impressions(self) -> None:
        issues = check_ads_suspicious_metrics(
            [{"impressions": "10", "clicks": "11", "orders": "1", "spend_rub": "0", "revenue_rub": "0"}]
        )
        self.assertEqual(issues[0]["check"], "metric_range")
        self.assertEqual(issues[0]["severity"], "high")

    def test_reviews_quality_detects_invalid_rating(self) -> None:
        issues = check_review_suspicious_values([{"rating": "6", "text": "valid text"}])
        self.assertEqual(issues[0]["field"], "rating")

    def test_unit_economics_detects_invalid_rate(self) -> None:
        issues = check_unit_economics_values(
            [{
                "price_rub": "100",
                "cogs_rub": "50",
                "marketplace_fee_rate": "1.2",
                "return_rate": "0.1",
                "tax_rate": "0.1",
                "target_profit_rate": "0.1",
            }]
        )
        self.assertEqual(issues[0]["field"], "marketplace_fee_rate")

