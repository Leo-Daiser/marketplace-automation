from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.notion_payloads import build_notion_task_payload  # noqa: E402


class NotionPayloadsTest(unittest.TestCase):
    def test_build_notion_task_payload_maps_task_fields(self) -> None:
        payload = build_notion_task_payload(
            {
                "task_id": "SEO-omega",
                "keyword": "омега 3",
                "our_sku": "SKU-OMEGA",
                "priority": "high",
                "owner": "seo/content",
                "impact": "organic_visibility",
                "due_in_days": "4",
                "task_type": "seo_content",
                "title": "Rewrite omega card",
                "brief": "Improve title and bullets.",
                "suggested_terms": "epa, dha",
            }
        )
        self.assertEqual(payload["title"], "Rewrite omega card")
        self.assertEqual(payload["properties"]["Priority"]["select"], "high")
        self.assertEqual(payload["properties"]["Due In Days"]["number"], 4)
        self.assertIn("Рекомендуемые термины: epa, dha", payload["content"])


if __name__ == "__main__":
    unittest.main()
