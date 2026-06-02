from __future__ import annotations

import argparse
from pathlib import Path

from .adapters.csv_store import CsvTableStore
from .adapters.google_sheets import GoogleSheetsTableStore
from .adapters.google_sheets_no_cloud import (
    AppsScriptGoogleSheetsTableStore,
    AppsScriptSheetsConfig,
    PublicCsvGoogleSheetsTableStore,
    PublicCsvSheetsConfig,
)
from .ads_reporter import run_ads_report
from .competitor_monitor import run_competitor_monitor
from .data_quality import run_data_quality_report
from .portfolio import run_portfolio_suite
from .review_agent import run_review_agent
from .unit_economics import read_unit_economics


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="marketplace-automation",
        description="Портфолио-автоматизации для рекламы, отзывов и конкурентного SEO на маркетплейсах.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    ads = subparsers.add_parser("ads-report", help="Сгенерировать отчет по рекламе WB/Ozon.")
    ads.add_argument("--input", required=True, type=Path)
    ads.add_argument("--out-dir", required=True, type=Path)
    ads.add_argument("--target-drr", type=float, default=0.18)
    ads.add_argument("--unit-economics", type=Path)

    reviews = subparsers.add_parser("review-agent", help="Сгенерировать черновики ответов и обращения в поддержку.")
    reviews.add_argument("--input", required=True, type=Path)
    reviews.add_argument("--out-dir", required=True, type=Path)

    competitors = subparsers.add_parser("competitor-monitor", help="Сгенерировать SEO-возможности по конкурентам.")
    competitors.add_argument("--competitors", required=True, type=Path)
    competitors.add_argument("--our-products", required=True, type=Path)
    competitors.add_argument("--keyword-plan", required=True, type=Path)
    competitors.add_argument("--out-dir", required=True, type=Path)

    quality = subparsers.add_parser("data-quality", help="Сгенерировать отчет качества входных CSV-таблиц.")
    quality.add_argument("--data-dir", required=True, type=Path)
    quality.add_argument("--out-dir", required=True, type=Path)

    run_all = subparsers.add_parser("run-all", help="Запустить все портфолио-кейсы.")
    run_all.add_argument("--data-dir", required=True, type=Path)
    run_all.add_argument("--out-dir", required=True, type=Path)
    run_all.add_argument("--target-drr", type=float, default=0.18)

    sheets_pull = subparsers.add_parser("sheets-pull", help="Скачать вкладки Google Sheets в локальные CSV.")
    sheets_pull.add_argument("--spreadsheet-id", required=True)
    sheets_pull.add_argument("--service-account-file", required=True)
    sheets_pull.add_argument("--out-dir", required=True, type=Path)
    sheets_pull.add_argument("--tables", nargs="+", required=True)

    sheets_push = subparsers.add_parser("sheets-push", help="Загрузить локальные CSV во вкладки Google Sheets.")
    sheets_push.add_argument("--spreadsheet-id", required=True)
    sheets_push.add_argument("--service-account-file", required=True)
    sheets_push.add_argument("--data-dir", required=True, type=Path)
    sheets_push.add_argument("--tables", nargs="+", required=True)

    sheets_link_pull = subparsers.add_parser(
        "sheets-link-pull",
        help="Скачать публичные вкладки Google Sheets в CSV без Google Cloud.",
    )
    sheets_link_pull.add_argument("--spreadsheet-id", required=True)
    sheets_link_pull.add_argument("--out-dir", required=True, type=Path)
    sheets_link_pull.add_argument("--tables", nargs="+", required=True)

    sheets_webapp_push = subparsers.add_parser(
        "sheets-webapp-push",
        help="Загрузить CSV в Google Sheets через Apps Script web app.",
    )
    sheets_webapp_push.add_argument("--web-app-url", required=True)
    sheets_webapp_push.add_argument("--secret", required=True)
    sheets_webapp_push.add_argument("--data-dir", required=True, type=Path)
    sheets_webapp_push.add_argument("--tables", nargs="+", required=True)
    return parser


def print_outputs(outputs: dict[str, Path]) -> None:
    for name, path in outputs.items():
        print(f"артефакт {name}: {path}")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.command == "ads-report":
        unit_economics = (
            read_unit_economics(args.unit_economics)
            if args.unit_economics
            else None
        )
        outputs = run_ads_report(
            args.input,
            args.out_dir,
            target_drr=args.target_drr,
            unit_economics=unit_economics,
        )
        print_outputs(outputs)
        return 0

    if args.command == "review-agent":
        outputs = run_review_agent(args.input, args.out_dir)
        print_outputs(outputs)
        return 0

    if args.command == "competitor-monitor":
        outputs = run_competitor_monitor(
            competitors_path=args.competitors,
            our_products_path=args.our_products,
            keyword_plan_path=args.keyword_plan,
            out_dir=args.out_dir,
        )
        print_outputs(outputs)
        return 0

    if args.command == "data-quality":
        outputs = run_data_quality_report(args.data_dir, args.out_dir)
        print_outputs(outputs)
        return 0

    if args.command == "run-all":
        all_outputs = run_portfolio_suite(
            data_dir=args.data_dir,
            out_dir=args.out_dir,
            target_drr=args.target_drr,
        )
        print_outputs(all_outputs)
        return 0

    if args.command == "sheets-pull":
        sheets = GoogleSheetsTableStore.from_service_account_file(
            spreadsheet_id=args.spreadsheet_id,
            service_account_file=args.service_account_file,
        )
        csv_store = CsvTableStore(args.out_dir)
        for table_name in args.tables:
            csv_store.write_table(table_name, sheets.read_table(table_name))
            print(f"скачано: {table_name} -> {args.out_dir / (table_name + '.csv')}")
        return 0

    if args.command == "sheets-push":
        sheets = GoogleSheetsTableStore.from_service_account_file(
            spreadsheet_id=args.spreadsheet_id,
            service_account_file=args.service_account_file,
        )
        csv_store = CsvTableStore(args.data_dir)
        for table_name in args.tables:
            rows = csv_store.read_table(table_name)
            sheets.write_table(table_name, rows)
            print(f"загружено: {args.data_dir / (table_name + '.csv')} -> {table_name}")
        return 0

    if args.command == "sheets-link-pull":
        sheets = PublicCsvGoogleSheetsTableStore(
            PublicCsvSheetsConfig(spreadsheet_id=args.spreadsheet_id)
        )
        csv_store = CsvTableStore(args.out_dir)
        for table_name in args.tables:
            rows = sheets.read_table(table_name)
            csv_store.write_table(table_name, rows)
            print(f"скачано: {table_name} строк={len(rows)} -> {args.out_dir / (table_name + '.csv')}")
        return 0

    if args.command == "sheets-webapp-push":
        sheets = AppsScriptGoogleSheetsTableStore(
            AppsScriptSheetsConfig(
                web_app_url=args.web_app_url,
                secret=args.secret,
            )
        )
        csv_store = CsvTableStore(args.data_dir)
        for table_name in args.tables:
            rows = csv_store.read_table(table_name)
            response = sheets.write_table(table_name, rows)
            print(f"загружено: {args.data_dir / (table_name + '.csv')} -> {table_name} {response}")
        return 0

    parser.error(f"Неизвестная команда: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
