from __future__ import annotations

import sys
import unittest
from pathlib import Path
from typing import Any, Mapping

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.adapters.google_sheets import (  # noqa: E402
    GoogleSheetsConfig,
    GoogleSheetsTableStore,
)


class FakeTransport:
    def __init__(self) -> None:
        self.last_get_url = ""
        self.last_put_url = ""
        self.last_put_json: Mapping[str, Any] = {}

    def get(self, url: str, headers: Mapping[str, str]) -> Mapping[str, Any]:
        self.last_get_url = url
        self.last_get_headers = headers
        return {
            "values": [
                ["sku", "orders"],
                ["SKU-1", "3"],
                ["SKU-2", "5"],
            ]
        }

    def put(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        self.last_put_url = url
        self.last_put_headers = headers
        self.last_put_json = json
        return {"updatedRows": len(json["values"])}


class GoogleSheetsAdapterTest(unittest.TestCase):
    def test_read_table_maps_first_row_to_headers(self) -> None:
        transport = FakeTransport()
        store = GoogleSheetsTableStore(
            GoogleSheetsConfig(spreadsheet_id="sheet-1", access_token="token-1"),
            transport=transport,
        )
        rows = store.read_table("ads_daily")
        self.assertEqual(rows[0], {"sku": "SKU-1", "orders": "3"})
        self.assertIn("ads_daily%21A1%3AZ10000", transport.last_get_url)
        self.assertEqual(transport.last_get_headers["Authorization"], "Bearer token-1")

    def test_write_table_sends_values_payload(self) -> None:
        transport = FakeTransport()
        store = GoogleSheetsTableStore(
            GoogleSheetsConfig(spreadsheet_id="sheet-1", access_token="token-1"),
            transport=transport,
        )
        store.write_table("support_tickets", [{"ticket_id": "T-1", "priority": "P1"}])
        self.assertIn("valueInputOption=RAW", transport.last_put_url)
        self.assertEqual(
            transport.last_put_json["values"],
            [["ticket_id", "priority"], ["T-1", "P1"]],
        )


if __name__ == "__main__":
    unittest.main()

