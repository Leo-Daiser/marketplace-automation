from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from io import StringIO
from typing import Any, Mapping, Protocol, Sequence
from urllib.parse import quote
from urllib.request import Request, urlopen


class TextHttpTransport(Protocol):
    def get_text(self, url: str) -> str:
        raise NotImplementedError

    def post_json(self, url: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        raise NotImplementedError


class UrllibTextTransport:
    def get_text(self, url: str) -> str:
        with urlopen(url, timeout=30) as response:
            return response.read().decode("utf-8-sig")

    def post_json(self, url: str, payload: Mapping[str, Any]) -> Mapping[str, Any]:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        request = Request(
            url,
            data=body,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        with urlopen(request, timeout=30) as response:
            text = response.read().decode("utf-8-sig")
        return json.loads(text) if text else {}


@dataclass(frozen=True)
class PublicCsvSheetsConfig:
    spreadsheet_id: str


class PublicCsvGoogleSheetsTableStore:
    """Reads public Google Sheets tabs via CSV links without Google Cloud credentials."""

    def __init__(
        self,
        config: PublicCsvSheetsConfig,
        transport: TextHttpTransport | None = None,
    ) -> None:
        self.config = config
        self.transport = transport or UrllibTextTransport()

    def read_table(self, table_name: str) -> list[dict[str, str]]:
        csv_text = self.transport.get_text(self._csv_url(table_name))
        if not csv_text.strip():
            return []
        reader = csv.DictReader(StringIO(csv_text))
        return [
            {str(key).strip(): value for key, value in row.items() if key is not None}
            for row in reader
        ]

    def _csv_url(self, table_name: str) -> str:
        encoded_sheet = quote(table_name, safe="")
        return (
            "https://docs.google.com/spreadsheets/d/"
            f"{self.config.spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
        )


@dataclass(frozen=True)
class AppsScriptSheetsConfig:
    web_app_url: str
    secret: str


class AppsScriptGoogleSheetsTableStore:
    """Writes rows to Google Sheets through an Apps Script web app endpoint."""

    def __init__(
        self,
        config: AppsScriptSheetsConfig,
        transport: TextHttpTransport | None = None,
    ) -> None:
        self.config = config
        self.transport = transport or UrllibTextTransport()

    def write_table(
        self,
        table_name: str,
        rows: Sequence[Mapping[str, Any]],
        fieldnames: Sequence[str] | None = None,
        mode: str = "replace",
    ) -> Mapping[str, Any]:
        materialized = [dict(row) for row in rows]
        if fieldnames is None:
            fieldnames = list(materialized[0].keys()) if materialized else []
        payload = {
            "secret": self.config.secret,
            "table": table_name,
            "mode": mode,
            "fieldnames": list(fieldnames),
            "rows": materialized,
        }
        response = self.transport.post_json(self.config.web_app_url, payload)
        if response.get("ok") is False:
            raise RuntimeError(f"Apps Script write failed: {response.get('error')}")
        return response
