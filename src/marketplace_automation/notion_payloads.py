from __future__ import annotations

from typing import Any, Mapping


def build_notion_task_payload(task: Mapping[str, Any]) -> dict[str, Any]:
    """Build a Notion-compatible task payload without binding to a specific client."""

    title = str(task.get("title") or task.get("task_id") or "Задача по маркетплейсу")
    priority = str(task.get("priority") or "medium")
    owner = str(task.get("owner") or "unassigned")
    task_type = str(task.get("task_type") or "general")
    return {
        "title": title,
        "properties": {
            "Task ID": {"rich_text": str(task.get("task_id", ""))},
            "Priority": {"select": priority},
            "Owner": {"select": owner},
            "Task Type": {"select": task_type},
            "Impact": {"select": str(task.get("impact", "unknown"))},
            "SKU": {"rich_text": str(task.get("our_sku", ""))},
            "Keyword": {"rich_text": str(task.get("keyword", ""))},
            "Due In Days": {"number": _optional_int(task.get("due_in_days"))},
        },
        "content": [
            str(task.get("brief", "")),
            f"Рекомендуемые термины: {task.get('suggested_terms', '')}",
        ],
    }


def _optional_int(value: Any) -> int | None:
    if value in {None, ""}:
        return None
    return int(value)
