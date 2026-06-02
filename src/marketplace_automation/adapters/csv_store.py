from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping, Sequence

from marketplace_automation.io_utils import read_csv, write_csv


class CsvTableStore:
    """Simple local adapter that mirrors the Google Sheets table contract."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def read_table(self, table_name: str) -> list[dict[str, str]]:
        return read_csv(self._path(table_name))

    def write_table(
        self,
        table_name: str,
        rows: Sequence[Mapping[str, Any]],
        fieldnames: Sequence[str] | None = None,
    ) -> None:
        write_csv(self._path(table_name), rows, fieldnames)

    def _path(self, table_name: str) -> Path:
        if not table_name.endswith(".csv"):
            table_name = f"{table_name}.csv"
        return self.root / table_name

