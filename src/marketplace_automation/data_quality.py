from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .io_utils import markdown_table, parse_float, parse_int, read_csv, write_csv, write_text
from .schemas import (
    ADS_DAILY_REQUIRED,
    COMPETITORS_REQUIRED,
    KEYWORD_PLAN_REQUIRED,
    OUR_PRODUCTS_REQUIRED,
    REVIEWS_REQUIRED,
    UNIT_ECONOMICS_REQUIRED,
)


QUALITY_COLUMNS = [
    "dataset",
    "severity",
    "check",
    "field",
    "row_number",
    "message",
]


def build_data_quality_report(data_dir: Path) -> list[dict[str, Any]]:
    checks: list[dict[str, Any]] = []
    dataset_specs = [
        ("ads_daily", data_dir / "ads_daily.csv", ADS_DAILY_REQUIRED),
        ("reviews", data_dir / "reviews.csv", REVIEWS_REQUIRED),
        ("competitors", data_dir / "competitors.csv", COMPETITORS_REQUIRED),
        ("our_products", data_dir / "our_products.csv", OUR_PRODUCTS_REQUIRED),
        ("keyword_plan", data_dir / "keyword_plan.csv", KEYWORD_PLAN_REQUIRED),
        ("unit_economics", data_dir / "unit_economics.csv", UNIT_ECONOMICS_REQUIRED),
    ]
    for dataset, path, required_columns in dataset_specs:
        if not path.exists():
            checks.append(issue(dataset, "high", "file_exists", "", "", f"Не найден файл: {path.name}"))
            continue
        rows = read_csv(path)
        checks.extend(check_required_columns(dataset, rows, required_columns))
        checks.extend(check_empty_required_values(dataset, rows, required_columns))
        if dataset == "ads_daily":
            checks.extend(check_ads_suspicious_metrics(rows))
        if dataset == "reviews":
            checks.extend(check_review_suspicious_values(rows))
        if dataset == "unit_economics":
            checks.extend(check_unit_economics_values(rows))
    if not checks:
        checks.append(issue("all", "info", "quality_gate", "", "", "Проблем качества данных не найдено."))
    return checks


def check_required_columns(
    dataset: str,
    rows: list[Mapping[str, Any]],
    required_columns: set[str],
) -> list[dict[str, Any]]:
    if not rows:
        return [issue(dataset, "high", "not_empty", "", "", "Датасет пустой.")]
    missing = sorted(required_columns - set(rows[0].keys()))
    return [
        issue(dataset, "high", "required_column", column, "", f"Не найдена обязательная колонка: {column}")
        for column in missing
    ]


def check_empty_required_values(
    dataset: str,
    rows: list[Mapping[str, Any]],
    required_columns: set[str],
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    available_required = required_columns & set(rows[0].keys()) if rows else set()
    for row_index, row in enumerate(rows, start=2):
        for column in available_required:
            if str(row.get(column, "")).strip() == "":
                issues.append(
                    issue(dataset, "medium", "required_value", column, row_index, "Обязательное значение пустое.")
                )
    return issues


def check_ads_suspicious_metrics(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for row_index, row in enumerate(rows, start=2):
        impressions = parse_int(row.get("impressions"))
        clicks = parse_int(row.get("clicks"))
        orders = parse_int(row.get("orders"))
        spend = parse_float(row.get("spend_rub"))
        revenue = parse_float(row.get("revenue_rub"))
        if clicks > impressions:
            issues.append(issue("ads_daily", "high", "metric_range", "clicks", row_index, "Кликов больше, чем показов."))
        if orders > clicks and clicks > 0:
            issues.append(issue("ads_daily", "medium", "metric_range", "orders", row_index, "Заказов больше, чем кликов."))
        if spend < 0 or revenue < 0:
            issues.append(issue("ads_daily", "high", "metric_range", "spend/revenue", row_index, "Отрицательное денежное значение."))
    return issues


def check_review_suspicious_values(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for row_index, row in enumerate(rows, start=2):
        rating = parse_int(row.get("rating"))
        if rating < 1 or rating > 5:
            issues.append(issue("reviews", "high", "rating_range", "rating", row_index, "Оценка должна быть от 1 до 5."))
        if len(str(row.get("text", "")).strip()) < 5:
            issues.append(issue("reviews", "medium", "text_length", "text", row_index, "Текст отзыва слишком короткий."))
    return issues


def check_unit_economics_values(rows: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    rate_fields = ["marketplace_fee_rate", "return_rate", "tax_rate", "target_profit_rate"]
    for row_index, row in enumerate(rows, start=2):
        price = parse_float(row.get("price_rub"))
        cogs = parse_float(row.get("cogs_rub"))
        if price <= 0:
            issues.append(issue("unit_economics", "high", "price_range", "price_rub", row_index, "Цена должна быть положительной."))
        if cogs < 0:
            issues.append(issue("unit_economics", "high", "cogs_range", "cogs_rub", row_index, "Себестоимость не может быть отрицательной."))
        for field in rate_fields:
            value = parse_float(row.get(field))
            if value < 0 or value > 1:
                issues.append(issue("unit_economics", "high", "rate_range", field, row_index, "Доля должна быть от 0 до 1."))
    return issues


def issue(
    dataset: str,
    severity: str,
    check: str,
    field: str,
    row_number: int | str,
    message: str,
) -> dict[str, Any]:
    return {
        "dataset": dataset,
        "severity": severity,
        "check": check,
        "field": field,
        "row_number": row_number,
        "message": message,
    }


def render_data_quality_markdown(rows: list[Mapping[str, Any]]) -> str:
    high = sum(1 for row in rows if row.get("severity") == "high")
    medium = sum(1 for row in rows if row.get("severity") == "medium")
    info = sum(1 for row in rows if row.get("severity") == "info")
    display_rows = [data_quality_display_row(row) for row in rows]
    return "\n".join(
        [
            "# Отчет качества данных",
            "",
            f"- Высокая критичность: {high}",
            f"- Средняя критичность: {medium}",
            f"- Info: {info}",
            "",
            markdown_table(
                display_rows,
                ["датасет", "критичность", "проверка", "поле", "строка", "сообщение"],
            ),
            "",
        ]
    )


def data_quality_display_row(row: Mapping[str, Any]) -> dict[str, str]:
    return {
        "датасет": str(row.get("dataset", "")),
        "критичность": str(row.get("severity", "")),
        "проверка": str(row.get("check", "")),
        "поле": str(row.get("field", "")),
        "строка": str(row.get("row_number", "")),
        "сообщение": str(row.get("message", "")),
    }


def run_data_quality_report(data_dir: Path, out_dir: Path) -> dict[str, Path]:
    rows = build_data_quality_report(data_dir)
    csv_path = out_dir / "data_quality_report.csv"
    markdown_path = out_dir / "data_quality_report.md"
    write_csv(csv_path, rows, QUALITY_COLUMNS)
    write_text(markdown_path, render_data_quality_markdown(rows))
    return {"csv": csv_path, "markdown": markdown_path}
