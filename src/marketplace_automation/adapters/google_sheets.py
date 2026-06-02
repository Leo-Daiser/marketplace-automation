from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence
from urllib.parse import quote


class HttpTransport(Protocol):
    def get(self, url: str, headers: Mapping[str, str]) -> Mapping[str, Any]:
        raise NotImplementedError

    def put(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        raise NotImplementedError


@dataclass(frozen=True)
class GoogleSheetsConfig:
    spreadsheet_id: str
    access_token: str
    default_range: str = "A1:Z10000"


class RequestsTransport:
    def __init__(self) -> None:
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError(
                "Google Sheets adapter requires optional dependency: pip install -e .[sheets]"
            ) from exc
        self._requests = requests

    def get(self, url: str, headers: Mapping[str, str]) -> Mapping[str, Any]:
        response = self._requests.get(url, headers=dict(headers), timeout=30)
        response.raise_for_status()
        return response.json()

    def put(
        self,
        url: str,
        *,
        headers: Mapping[str, str],
        json: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        response = self._requests.put(url, headers=dict(headers), json=json, timeout=30)
        response.raise_for_status()
        return response.json()


class GoogleSheetsTableStore:
    """Google Sheets Values API adapter for the same table contract as CSV files."""

    def __init__(
        self,
        config: GoogleSheetsConfig,
        transport: HttpTransport | None = None,
    ) -> None:
        self.config = config
        self.transport = transport or RequestsTransport()

    @classmethod
    def from_service_account_file(
        cls,
        *,
        spreadsheet_id: str,
        service_account_file: str,
        scopes: Sequence[str] | None = None,
    ) -> "GoogleSheetsTableStore":
        try:
            from google.auth.transport.requests import Request
            from google.oauth2 import service_account
        except ImportError as exc:
            raise RuntimeError(
                "Service account auth requires optional dependency: pip install -e .[sheets]"
            ) from exc

        scopes = scopes or ["https://www.googleapis.com/auth/spreadsheets"]
        credentials = service_account.Credentials.from_service_account_file(
            service_account_file,
            scopes=list(scopes),
        )
        credentials.refresh(Request())
        return cls(
            GoogleSheetsConfig(
                spreadsheet_id=spreadsheet_id,
                access_token=credentials.token,
            )
        )

    def read_table(self, table_name: str) -> list[dict[str, str]]:
        payload = self.transport.get(
            self._values_url(table_name),
            headers=self._headers(),
        )
        values = payload.get("values", [])
        if not values:
            return []
        headers = [str(header).strip() for header in values[0]]
        rows: list[dict[str, str]] = []
        for values_row in values[1:]:
            row = {
                header: str(values_row[index]) if index < len(values_row) else ""
                for index, header in enumerate(headers)
            }
            rows.append(row)
        return rows

    def write_table(
        self,
        table_name: str,
        rows: Sequence[Mapping[str, Any]],
        fieldnames: Sequence[str] | None = None,
    ) -> None:
        materialized = list(rows)
        if fieldnames is None:
            fieldnames = list(materialized[0].keys()) if materialized else []
        values = [list(fieldnames)]
        values.extend(
            [str(row.get(fieldname, "")) for fieldname in fieldnames]
            for row in materialized
        )
        self.transport.put(
            self._values_url(table_name, query="?valueInputOption=RAW"),
            headers=self._headers(),
            json={
                "range": self._a1_range(table_name),
                "majorDimension": "ROWS",
                "values": values,
            },
        )

    def _headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json",
        }

    def _values_url(self, table_name: str, query: str = "") -> str:
        encoded_range = quote(self._a1_range(table_name), safe="")
        return (
            "https://sheets.googleapis.com/v4/spreadsheets/"
            f"{self.config.spreadsheet_id}/values/{encoded_range}{query}"
        )

    def _a1_range(self, table_name: str) -> str:
        if "!" in table_name:
            return table_name
        return f"{table_name}!{self.config.default_range}"

