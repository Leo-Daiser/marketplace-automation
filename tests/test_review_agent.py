from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.review_agent import (  # noqa: E402
    BANNED_MEDICAL_CLAIMS,
    build_support_ticket,
    classify_review,
)


class ReviewAgentTest(unittest.TestCase):
    def test_side_effect_review_becomes_high_priority_ticket(self) -> None:
        classified = classify_review(
            {
                "review_id": "R-1",
                "date": "2026-05-24",
                "marketplace": "WB",
                "sku": "SKU-1",
                "rating": "1",
                "text": "После приема стало плохо и болит голова.",
                "has_photo": "false",
            }
        )
        ticket = build_support_ticket(classified)
        self.assertEqual(classified["topic"], "side_effect")
        self.assertEqual(classified["urgency"], "high")
        self.assertIsNotNone(ticket)
        self.assertEqual(ticket["priority"], "P1")

    def test_reply_does_not_contain_banned_medical_claims(self) -> None:
        classified = classify_review(
            {
                "review_id": "R-2",
                "rating": "5",
                "text": "Отличный продукт, понравился формат.",
                "has_photo": "false",
            }
        )
        reply = classified["reply_draft"].lower()
        for claim in BANNED_MEDICAL_CLAIMS:
            self.assertNotIn(claim, reply)

    def test_positive_packaging_review_does_not_create_ticket(self) -> None:
        classified = classify_review(
            {
                "review_id": "R-3",
                "rating": "5",
                "text": "Упаковка красивая, все пришло целым.",
                "has_photo": "true",
            }
        )
        ticket = build_support_ticket(classified)
        self.assertEqual(classified["sentiment"], "positive")
        self.assertEqual(classified["needs_support_ticket"], "false")
        self.assertIsNone(ticket)


if __name__ == "__main__":
    unittest.main()
