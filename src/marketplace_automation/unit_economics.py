from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from .io_utils import parse_float, read_csv, safe_div, write_csv
from .schemas import UNIT_ECONOMICS_REQUIRED, validate_rows


UNIT_ECONOMICS_COLUMNS = [
    "sku",
    "marketplace",
    "price_rub",
    "cogs_rub",
    "marketplace_fee_rub",
    "logistics_rub",
    "storage_rub",
    "expected_return_cost_rub",
    "tax_rub",
    "contribution_margin_before_ads_rub",
    "contribution_margin_rate",
    "break_even_drr",
    "target_drr",
]


def build_unit_economics(rows: list[Mapping[str, Any]]) -> dict[tuple[str, str], dict[str, Any]]:
    models: dict[tuple[str, str], dict[str, Any]] = {}
    for row in rows:
        sku = str(row.get("sku", "")).strip()
        marketplace = str(row.get("marketplace", "")).strip()
        price = parse_float(row.get("price_rub"))
        cogs = parse_float(row.get("cogs_rub"))
        marketplace_fee_rate = parse_float(row.get("marketplace_fee_rate"))
        logistics = parse_float(row.get("logistics_rub"))
        storage = parse_float(row.get("storage_rub"))
        return_rate = parse_float(row.get("return_rate"))
        tax_rate = parse_float(row.get("tax_rate"))
        target_profit_rate = parse_float(row.get("target_profit_rate"))

        marketplace_fee = price * marketplace_fee_rate
        expected_return_cost = logistics * return_rate
        tax = price * tax_rate
        contribution_margin = (
            price - cogs - marketplace_fee - logistics - storage - expected_return_cost - tax
        )
        contribution_margin_rate = safe_div(contribution_margin, price)
        break_even_drr = max(0.0, contribution_margin_rate)
        target_drr = max(0.0, contribution_margin_rate - target_profit_rate)
        models[(sku, marketplace)] = {
            "sku": sku,
            "marketplace": marketplace,
            "price_rub": round(price, 2),
            "cogs_rub": round(cogs, 2),
            "marketplace_fee_rub": round(marketplace_fee, 2),
            "logistics_rub": round(logistics, 2),
            "storage_rub": round(storage, 2),
            "expected_return_cost_rub": round(expected_return_cost, 2),
            "tax_rub": round(tax, 2),
            "contribution_margin_before_ads_rub": round(contribution_margin, 2),
            "contribution_margin_rate": round(contribution_margin_rate, 4),
            "break_even_drr": round(break_even_drr, 4),
            "target_drr": round(target_drr, 4),
        }
    return models


def read_unit_economics(path: Path) -> dict[tuple[str, str], dict[str, Any]]:
    rows = read_csv(path)
    validate_rows(
        rows,
        required_columns=UNIT_ECONOMICS_REQUIRED,
        dataset_name="unit_economics",
    )
    return build_unit_economics(rows)


def run_unit_economics_report(input_path: Path, out_dir: Path) -> Path:
    models = read_unit_economics(input_path)
    output_path = out_dir / "unit_economics_report.csv"
    write_csv(output_path, models.values(), UNIT_ECONOMICS_COLUMNS)
    return output_path

