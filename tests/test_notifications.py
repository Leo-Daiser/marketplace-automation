from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.notifications import (  # noqa: E402
    format_telegram_daily_digest,
    trim_for_telegram,
)


class NotificationsTest(unittest.TestCase):
    def test_format_telegram_daily_digest_contains_business_signals(self) -> None:
        text = format_telegram_daily_digest(
            ads_rows=[
                {
                    "spend_rub": "100",
                    "revenue_rub": "400",
                    "gross_profit_rub": "80",
                    "impressions": "1000",
                    "clicks": "100",
                    "orders": "10",
                    "recommended_action": "reduce_bid_and_check_unit_economics",
                }
            ],
            ticket_rows=[{"ticket_id": "T-1"}],
            opportunity_rows=[{"opportunity_score": "7.0"}],
            action_rows=[
                {
                    "priority": "P0",
                    "area": "ads",
                    "action": "reduce bid",
                    "evidence": "DRR 25%",
                }
            ],
        )
        self.assertIn("ДРР: 25.0%", text)
        self.assertIn("Обращения в поддержку: 1", text)
        self.assertIn("[реклама] reduce bid", text)

    def test_trim_for_telegram_limits_text(self) -> None:
        text = trim_for_telegram("x" * 5000, limit=100)
        self.assertLessEqual(len(text), 100)
        self.assertTrue(text.endswith("...обрезано"))


if __name__ == "__main__":
    unittest.main()
