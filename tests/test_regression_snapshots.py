from __future__ import annotations

import csv
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.portfolio import run_portfolio_suite  # noqa: E402


def read_header(path: Path) -> set[str]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return set(next(csv.reader(handle)))


class RegressionSnapshotTest(unittest.TestCase):
    def test_portfolio_suite_preserves_report_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            outputs = run_portfolio_suite(
                data_dir=ROOT / "data" / "sample",
                out_dir=Path(temp_dir),
                target_drr=0.18,
            )

            required_outputs = [
                "portfolio_action_plan",
                "portfolio_executive_summary",
                "portfolio_telegram_digest",
                "ads_csv",
                "ads_audit_csv",
                "data_quality_markdown",
                "reviews_replies",
                "competitors_tasks",
            ]
            for output_name in required_outputs:
                self.assertIn(output_name, outputs)
                self.assertTrue(outputs[output_name].exists(), output_name)

            self.assertSetEqual(
                {
                    "decision_confidence",
                    "decision_signals",
                    "break_even_drr",
                    "unit_target_drr",
                    "risk_level",
                },
                read_header(outputs["ads_csv"])
                & {
                    "decision_confidence",
                    "decision_signals",
                    "break_even_drr",
                    "unit_target_drr",
                    "risk_level",
                },
            )
            self.assertSetEqual(
                {"decision_confidence", "decision_signals", "next_step"},
                read_header(outputs["ads_audit_csv"])
                & {"decision_confidence", "decision_signals", "next_step"},
            )
            self.assertSetEqual(
                {"approval_status", "compliance_flags", "manual_review_required"},
                read_header(outputs["reviews_replies"])
                & {"approval_status", "compliance_flags", "manual_review_required"},
            )
            self.assertSetEqual(
                {"owner", "impact", "due_in_days"},
                read_header(outputs["competitors_tasks"]) & {"owner", "impact", "due_in_days"},
            )

            self.assertIn(
                "# Сводный план действий",
                outputs["portfolio_action_plan"].read_text(encoding="utf-8"),
            )
            action_plan = outputs["portfolio_action_plan"].read_text(encoding="utf-8")
            for column_name in ["критичность", "уверенность", "блокирует рост", "срок"]:
                self.assertIn(column_name, action_plan)
            self.assertIn(
                "# Управленческая сводка",
                outputs["portfolio_executive_summary"].read_text(encoding="utf-8"),
            )
            self.assertIn(
                "Дайджест автоматизации маркетплейсов",
                outputs["portfolio_telegram_digest"].read_text(encoding="utf-8"),
            )
            self.assertIn(
                "# Отчет качества данных",
                outputs["data_quality_markdown"].read_text(encoding="utf-8"),
            )


if __name__ == "__main__":
    unittest.main()
