from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from marketplace_automation.schemas import (  # noqa: E402
    SchemaValidationError,
    validate_rows,
)


class SchemaValidationTest(unittest.TestCase):
    def test_missing_required_column_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(SchemaValidationError, "missing required columns: sku"):
            validate_rows(
                [{"date": "2026-05-24"}],
                required_columns={"date", "sku"},
                dataset_name="demo",
            )

    def test_empty_required_value_raises_clear_error(self) -> None:
        with self.assertRaisesRegex(SchemaValidationError, "empty required values"):
            validate_rows(
                [{"date": "2026-05-24", "sku": ""}],
                required_columns={"date", "sku"},
                dataset_name="demo",
            )


if __name__ == "__main__":
    unittest.main()

