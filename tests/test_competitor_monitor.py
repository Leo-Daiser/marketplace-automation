from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.competitor_monitor import build_competitor_report  # noqa: E402


class CompetitorMonitorTest(unittest.TestCase):
    def test_price_gap_creates_unit_economics_task(self) -> None:
        competitors = [
            {
                "keyword": "omega",
                "marketplace": "Ozon",
                "price_rub": "1000",
                "rating": "4.8",
                "reviews_count": "2000",
                "ad_position": "1",
                "title": "Omega premium capsules",
                "bullets": "epa dha fish oil",
            },
            {
                "keyword": "omega",
                "marketplace": "Ozon",
                "price_rub": "1100",
                "rating": "4.7",
                "reviews_count": "1500",
                "ad_position": "2",
                "title": "Omega 3 capsules",
                "bullets": "clean fish oil",
            },
        ]
        our_products = [
            {
                "sku": "SKU-1",
                "price_rub": "1500",
                "rating": "4.4",
                "reviews_count": "300",
            }
        ]
        keyword_plan = [
            {
                "keyword": "omega",
                "marketplace": "Ozon",
                "our_sku": "SKU-1",
                "priority": "high",
                "our_current_position": "20",
                "target_position": "5",
            }
        ]
        opportunities, tasks = build_competitor_report(competitors, our_products, keyword_plan)
        self.assertEqual(opportunities[0]["recommended_action"], "check_price_or_bundle")
        self.assertEqual(tasks[0]["task_type"], "unit_economics")
        self.assertGreater(opportunities[0]["opportunity_score"], 6)


if __name__ == "__main__":
    unittest.main()

