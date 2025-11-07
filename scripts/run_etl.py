"""CLI entry-point to run the property normalization ETL."""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import ETLSettings
from src.pipeline.etl import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the 100x property ETL pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Execute transformations without loading into MySQL")
    parser.add_argument("--data-path", type=Path, help="Override path to the raw dataset")
    parser.add_argument("--field-config", type=Path, help="Override path to the field configuration workbook")
    parser.add_argument("--mysql-host", type=str, help="Override MySQL host")
    parser.add_argument("--mysql-port", type=int, help="Override MySQL port")
    parser.add_argument("--mysql-user", type=str, help="Override MySQL user")
    parser.add_argument("--mysql-password", type=str, help="Override MySQL password")
    parser.add_argument("--mysql-database", type=str, help="Override MySQL database name")
    parser.add_argument("--echo-sql", action="store_true", help="Enable SQLAlchemy echo for debugging queries")
    return parser.parse_args()


def build_settings(args: argparse.Namespace) -> ETLSettings:
    overrides: dict[str, object] = {}
    if args.data_path:
        overrides["data_path"] = args.data_path
    if args.field_config:
        overrides["field_config_path"] = args.field_config
    if args.mysql_host:
        overrides["mysql_host"] = args.mysql_host
    if args.mysql_port:
        overrides["mysql_port"] = args.mysql_port
    if args.mysql_user:
        overrides["mysql_user"] = args.mysql_user
    if args.mysql_password:
        overrides["mysql_password"] = args.mysql_password
    if args.mysql_database:
        overrides["mysql_database"] = args.mysql_database
    if args.echo_sql:
        overrides["echo_sql"] = True
    return ETLSettings(**overrides)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    args = parse_args()
    settings = build_settings(args)
    summary = run_pipeline(settings=settings, dry_run=args.dry_run)
    logging.info("Pipeline finished: %s", summary.as_dict())


if __name__ == "__main__":
    main()
