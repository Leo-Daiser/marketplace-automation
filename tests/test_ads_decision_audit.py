from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.ads_reporter import build_decision_audit  # noqa: E402


class AdsDecisionAuditTest(unittest.TestCase):
    def test_high_risk_campaign_has_explainable_signals(self) -> None:
        confidence, signals = build_decision_audit(
            action="reduce_bid_and_check_unit_economics",
            ctr=0.02,
            conversion_rate=0.02,
            drr=0.7,
            gross_profit=-1000,
            stock_units=50,
            target_drr=0.18,
        )
        self.assertEqual(confidence, "high")
        self.assertIn("negative_profit:-1000.00", signals)
        self.assertTrue(any(signal.startswith("drr_above_target") for signal in signals))

    def test_monitor_campaign_has_no_critical_signal(self) -> None:
        confidence, signals = build_decision_audit(
            action="monitor",
            ctr=0.03,
            conversion_rate=0.05,
            drr=0.12,
            gross_profit=5000,
            stock_units=80,
            target_drr=0.18,
        )
        self.assertEqual(confidence, "medium")
        self.assertEqual(signals, ["no_critical_signal"])

