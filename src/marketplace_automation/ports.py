from __future__ import annotations

from typing import Any, Mapping, Protocol, Sequence


class TableReader(Protocol):
    """Reads tabular business data from CSV, Google Sheets or marketplace exports."""

    def read_table(self, table_name: str) -> list[dict[str, str]]:
        raise NotImplementedError


class TableWriter(Protocol):
    """Writes tabular outputs to CSV, Google Sheets or other tabular stores."""

    def write_table(
        self,
        table_name: str,
        rows: Sequence[Mapping[str, Any]],
        fieldnames: Sequence[str] | None = None,
    ) -> None:
        raise NotImplementedError


class Notifier(Protocol):
    """Sends operational digests to Telegram, email or Slack-like channels."""

    def send_message(self, channel: str, text: str) -> None:
        raise NotImplementedError


class TaskSink(Protocol):
    """Creates tasks in Notion, Jira, ClickUp or Google Sheets backlog."""

    def create_task(self, payload: Mapping[str, Any]) -> str:
        raise NotImplementedError


class MarketplaceAdsClient(Protocol):
    """Boundary for WB/Ozon ad statistics adapters."""

    def fetch_ads_daily(self, date_from: str, date_to: str) -> list[dict[str, Any]]:
        raise NotImplementedError

