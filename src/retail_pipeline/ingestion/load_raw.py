from __future__ import annotations

import argparse
from pathlib import Path

from retail_pipeline.database import DEFAULT_DATABASE_PATH, get_connection

RAW_DATA_DIRECTORY = Path("data/raw")

SOURCE_FILES = {
    "customers": "olist_customers_dataset.csv",
    "geolocation": "olist_geolocation_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "orders": "olist_orders_dataset.csv",
    "products": "olist_products_dataset.csv",
    "sellers": "olist_sellers_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}


def validate_source_files(raw_directory: Path) -> None:
    """Raise an error when one or more required source files are missing."""

    missing_files = [
        filename
        for filename in SOURCE_FILES.values()
        if not (raw_directory / filename).is_file()
    ]

    if missing_files:
        formatted_files = "\n".join(
            f"- {filename}" for filename in missing_files
        )
        raise FileNotFoundError(
            f"Required source files are missing:\n{formatted_files}"
        )


def load_raw_tables(
    raw_directory: Path = RAW_DATA_DIRECTORY,
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> None:
    """Load all Olist CSV files into DuckDB raw tables."""

    validate_source_files(raw_directory)

    with get_connection(database_path) as connection:
        connection.execute("CREATE SCHEMA IF NOT EXISTS raw")

        for table_name, filename in SOURCE_FILES.items():
            source_path = (raw_directory / filename).resolve()

            connection.execute(
                f"""
                CREATE OR REPLACE TABLE raw.{table_name} AS
                SELECT *
                FROM read_csv(
                    ?,
                    header = true,
                    auto_detect = true,
                    sample_size = -1
                )
                """,
                [str(source_path)],
            )

            row_count = connection.execute(
                f"SELECT COUNT(*) FROM raw.{table_name}"
            ).fetchone()[0]

            print(f"Loaded raw.{table_name}: {row_count:,} rows")


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load Olist CSV files into DuckDB."
    )
    parser.add_argument(
        "--raw-directory",
        type=Path,
        default=RAW_DATA_DIRECTORY,
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE_PATH,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    load_raw_tables(
        raw_directory=args.raw_directory,
        database_path=args.database,
    )


if __name__ == "__main__":
    main()