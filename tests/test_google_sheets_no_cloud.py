from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.adapters.google_sheets_no_cloud import (  # noqa: E402
    AppsScriptGoogleSheetsTableStore,
    AppsScriptSheetsConfig,
    PublicCsvGoogleSheetsTableStore,
    PublicCsvSheetsConfig,
)


class FakeTextTransport:
    def __init__(self, csv_text: str = "") -> None:
        self.csv_text = csv_text
        self.requested_urls: list[str] = []
        self.posted_payloads: list[Mapping[str, Any]] = []

    def get_text(self, url: str) -> str:
        self.requested_urls.append(url)
        return self.csv_text

    def post_json(self, url: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        self.requested_urls.append(url)
        self.posted_payloads.append(payload)
        return {"ok": True, "rows": len(payload.get("rows", []))}


class GoogleSheetsNoCloudTest(unittest.TestCase):
    def test_public_csv_store_reads_rows_without_credentials(self) -> None:
        transport = FakeTextTransport(
            "sku ,orders ,revenue_rub \nSKU-ENERGY-GUM,12,22800\n"
        )
        store = PublicCsvGoogleSheetsTableStore(
            PublicCsvSheetsConfig(spreadsheet_id="sheet-id"),
            transport=transport,
        )

        rows = store.read_table("ads_daily")

        self.assertEqual([{"sku": "SKU-ENERGY-GUM", "orders": "12", "revenue_rub": "22800"}], rows)
        self.assertIn("sheet-id", transport.requested_urls[0])
        self.assertIn("sheet=ads_daily", transport.requested_urls[0])

    def test_apps_script_store_posts_rows_with_secret(self) -> None:
        transport = FakeTextTransport()
        store = AppsScriptGoogleSheetsTableStore(
            AppsScriptSheetsConfig(web_app_url="https://script.google.com/demo", secret="secret"),
            transport=transport,
        )

        response = store.write_table(
            "support_tickets",
            [{"ticket_id": "T-1", "priority": "P1"}],
        )

        self.assertEqual({"ok": True, "rows": 1}, response)
        payload = transport.posted_payloads[0]
        self.assertEqual("secret", payload["secret"])
        self.assertEqual("support_tickets", payload["table"])
        self.assertEqual(["ticket_id", "priority"], payload["fieldnames"])


if __name__ == "__main__":
    unittest.main()
