from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.adapters.csv_store import CsvTableStore  # noqa: E402


class CsvTableStoreTest(unittest.TestCase):
    def test_write_and_read_table(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = CsvTableStore(Path(temp_dir))
            store.write_table("demo", [{"sku": "SKU-1", "orders": 3}])
            rows = store.read_table("demo")
            self.assertEqual(rows, [{"sku": "SKU-1", "orders": "3"}])


if __name__ == "__main__":
    unittest.main()

