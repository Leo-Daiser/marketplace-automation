from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.portfolio import run_portfolio_suite  # noqa: E402


class PortfolioSuiteTest(unittest.TestCase):
    def test_run_portfolio_suite_creates_operator_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = run_portfolio_suite(
                data_dir=ROOT / "data" / "sample",
                out_dir=Path(temp_dir),
                target_drr=0.18,
            )
            self.assertTrue(outputs["portfolio_action_plan"].exists())
            self.assertTrue(outputs["portfolio_executive_summary"].exists())
            self.assertTrue(outputs["portfolio_telegram_digest"].exists())
            action_plan = outputs["portfolio_action_plan"].read_text(encoding="utf-8")
            executive_summary = outputs["portfolio_executive_summary"].read_text(encoding="utf-8")
            telegram_digest = outputs["portfolio_telegram_digest"].read_text(encoding="utf-8")
            self.assertIn("Сводный план действий", action_plan)
            self.assertIn("Управленческая сводка", executive_summary)
            self.assertIn("IQBIQ: дайджест автоматизации маркетплейсов", telegram_digest)
            self.assertIn("реклама", action_plan)
            self.assertIn("отзывы", action_plan)
            self.assertIn("конкуренты", action_plan)


if __name__ == "__main__":
    unittest.main()
