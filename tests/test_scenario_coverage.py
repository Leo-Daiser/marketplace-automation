from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.data_quality import build_data_quality_report  # noqa: E402
from marketplace_automation.portfolio import run_portfolio_suite  # noqa: E402


class ScenarioCoverageTest(unittest.TestCase):
    def test_balanced_growth_scenario_generates_clean_operator_outputs(self) -> None:
        scenario_dir = ROOT / "data" / "scenarios" / "balanced_growth"
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = run_portfolio_suite(scenario_dir, Path(temp_dir))
            self.assertTrue(outputs["portfolio_action_plan"].exists())
            self.assertTrue(outputs["portfolio_executive_summary"].exists())
            issues = build_data_quality_report(scenario_dir)
            high_or_medium_issues = [
                issue for issue in issues if issue["severity"] in {"high", "medium"}
            ]
            self.assertEqual([], high_or_medium_issues)
            action_plan = outputs["portfolio_action_plan"].read_text(encoding="utf-8")
            executive_summary = outputs["portfolio_executive_summary"].read_text(encoding="utf-8")
            self.assertIn("блокирует рост", action_plan)
            self.assertIn("Рисковые кампании: 0", executive_summary)
            self.assertIn("Прибыль после рекламы", executive_summary)

    def test_risk_edge_scenario_generates_outputs_and_quality_findings(self) -> None:
        scenario_dir = ROOT / "data" / "scenarios" / "risk_edge"
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = run_portfolio_suite(scenario_dir, Path(temp_dir))
            self.assertTrue(outputs["portfolio_action_plan"].exists())
            self.assertTrue(outputs["ads_audit_csv"].exists())
            issues = build_data_quality_report(scenario_dir)
            high_issues = [issue for issue in issues if issue["severity"] == "high"]
            self.assertGreaterEqual(len(high_issues), 2)
            self.assertTrue(any(issue["field"] == "clicks" for issue in high_issues))
            self.assertTrue(any(issue["field"] == "rating" for issue in high_issues))
