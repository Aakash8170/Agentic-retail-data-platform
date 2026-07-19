from __future__ import annotations

import argparse
from pathlib import Path

from retail_pipeline.database import DEFAULT_DATABASE_PATH, get_connection
from retail_pipeline.ingestion.load_raw import (
    RAW_DATA_DIRECTORY,
    SOURCE_FILES,
    load_raw_tables,
)
from retail_pipeline.profiling.run_profiles import (
    DEFAULT_PROFILE_DIRECTORY,
    DEFAULT_REPORT_DIRECTORY,
    run_profiles,
)
from retail_pipeline.sql_runner import run_sql_files


STAGING_SQL_DIR = Path("src/retail_pipeline/transformations/sql/staging")
CORE_SQL_DIR = Path("src/retail_pipeline/transformations/sql/core")
MART_SQL_DIR = Path("src/retail_pipeline/transformations/sql/marts")


def run_pipeline(
    raw_directory: Path = RAW_DATA_DIRECTORY,
    database_path: Path = DEFAULT_DATABASE_PATH,
    profile_sql_directory: Path = DEFAULT_PROFILE_DIRECTORY,
    profile_report_directory: Path = DEFAULT_REPORT_DIRECTORY,
) -> None:
    """Run pipeline stages 1-5 in order (raw -> profiling -> staging -> core -> marts).

    Final validation is provided by validate_database and may be run
    independently in tests or by callers.
    """

    # 1: raw ingestion
    print("[1/6] Loading raw data")
    load_raw_tables(raw_directory=raw_directory, database_path=database_path)

    # 2: profiling
    print("[2/6] Running profiling")
    run_profiles(
        sql_directory=profile_sql_directory,
        report_directory=profile_report_directory,
        database_path=database_path,
    )

    # 3: staging
    print("[3/6] Running staging transformations")
    run_sql_files(STAGING_SQL_DIR, database_path)

    # 4: core
    print("[4/6] Running core transformations")
    run_sql_files(CORE_SQL_DIR, database_path)

    # 5: marts
    print("[5/6] Running mart transformations")
    run_sql_files(MART_SQL_DIR, database_path)

    # 6: validation
    print("[6/6] Running validation")
    validate_database(database_path)

    print("Pipeline completed successfully.")


def _fetch_table_names(connection, schema: str) -> set[str]:
    rows = connection.execute(
        """
        SELECT table_name FROM information_schema.tables
        WHERE table_schema = ? ORDER BY table_name
        """,
        [schema],
    ).fetchall()
    return {r[0] for r in rows}


def validate_database(database_path: Path) -> None:
    """Validate that required tables exist, are non-empty, and facts have correct grain.

    Raises a ValueError with a clear message when validation fails.
    """

    expected_staging = {
        "customers",
        "orders",
        "order_items",
        "order_payments",
        "products",
        "sellers",
        "category_translation",
    }
    expected_core = {
        "dim_customer",
        "dim_product",
        "dim_seller",
        "dim_date",
        "fact_orders",
        "fact_order_items",
        "fact_payments",
    }
    expected_mart = {"daily_sales", "customer_summary", "product_performance"}

    with get_connection(database_path) as conn:
        # existence checks
        staging_tables = _fetch_table_names(conn, "staging")
        missing = expected_staging - staging_tables
        if missing:
            raise ValueError(f"Missing staging tables: {sorted(missing)}")

        core_tables = _fetch_table_names(conn, "core")
        missing = expected_core - core_tables
        if missing:
            raise ValueError(f"Missing core tables: {sorted(missing)}")

        mart_tables = _fetch_table_names(conn, "mart")
        missing = expected_mart - mart_tables
        if missing:
            raise ValueError(f"Missing mart tables: {sorted(missing)}")

        # not empty checks
        for schema, tables in (
            ("staging", expected_staging),
            ("core", expected_core),
            ("mart", expected_mart),
        ):
            for table in tables:
                count = conn.execute(
                    f"SELECT COUNT(*) FROM {schema}.{table}"
                ).fetchone()[0]
                if count == 0:
                    raise ValueError(f"Table {schema}.{table} is empty")

        # core fact grains
        # fact_orders: order_id unique
        fo_counts = conn.execute(
            "SELECT COUNT(*), COUNT(DISTINCT order_id)"
            " FROM core.fact_orders"
        ).fetchone()
        if fo_counts[0] != fo_counts[1]:
            raise ValueError("core.fact_orders has duplicate order_id rows")

        # fact_order_items: (order_id, order_item_id) unique
        foi_counts = conn.execute(
            "SELECT COUNT(*), COUNT(DISTINCT (order_id, order_item_id))"
            " FROM core.fact_order_items"
        ).fetchone()
        if foi_counts[0] != foi_counts[1]:
            raise ValueError(
                "core.fact_order_items has duplicate (order_id, order_item_id) rows"
            )

        # fact_payments: (order_id, payment_sequential) unique
        fp_counts = conn.execute(
            "SELECT COUNT(*), COUNT(DISTINCT (order_id, payment_sequential))"
            " FROM core.fact_payments"
        ).fetchone()
        if fp_counts[0] != fp_counts[1]:
            raise ValueError(
                "core.fact_payments has duplicate (order_id, payment_sequential) rows"
            )

        # mart grains
        ds_counts = conn.execute(
            "SELECT COUNT(*), COUNT(DISTINCT purchase_date)"
            " FROM mart.daily_sales"
        ).fetchone()
        if ds_counts[0] != ds_counts[1]:
            raise ValueError("mart.daily_sales has duplicate purchase_date rows")

        cs_counts = conn.execute(
            "SELECT COUNT(*), COUNT(DISTINCT customer_unique_id)"
            " FROM mart.customer_summary"
        ).fetchone()
        if cs_counts[0] != cs_counts[1]:
            raise ValueError("mart.customer_summary has duplicate customer_unique_id rows")

        pp_counts = conn.execute(
            "SELECT COUNT(*), COUNT(DISTINCT product_id)"
            " FROM mart.product_performance"
        ).fetchone()
        if pp_counts[0] != pp_counts[1]:
            raise ValueError("mart.product_performance has duplicate product_id rows")

        # foreign keys
        # fact_orders.customer_key -> dim_customer.customer_key
        missing_fk = conn.execute(
            """
            SELECT COUNT(*)
            FROM core.fact_orders fo
            LEFT JOIN core.dim_customer dc ON fo.customer_key = dc.customer_key
            WHERE dc.customer_key IS NULL
            """
        ).fetchone()[0]
        if missing_fk != 0:
            raise ValueError(
                "core.fact_orders.customer_key does not resolve to core.dim_customer"
            )

        # fact_order_items.product_key -> dim_product.product_key
        missing_fk = conn.execute(
            """
            SELECT COUNT(*)
            FROM core.fact_order_items fi
            LEFT JOIN core.dim_product dp ON fi.product_key = dp.product_key
            WHERE dp.product_key IS NULL
            """
        ).fetchone()[0]
        if missing_fk != 0:
            raise ValueError(
                "core.fact_order_items.product_key does not resolve to core.dim_product"
            )

        # fact_order_items.seller_key -> dim_seller.seller_key
        missing_fk = conn.execute(
            """
            SELECT COUNT(*)
            FROM core.fact_order_items fi
            LEFT JOIN core.dim_seller ds ON fi.seller_key = ds.seller_key
            WHERE ds.seller_key IS NULL
            """
        ).fetchone()[0]
        if missing_fk != 0:
            raise ValueError(
                "core.fact_order_items.seller_key does not resolve to core.dim_seller"
            )

        # fact_payments.order_id -> fact_orders.order_id
        missing_fk = conn.execute(
            """
            SELECT COUNT(*)
            FROM core.fact_payments fp
            LEFT JOIN core.fact_orders fo ON fp.order_id = fo.order_id
            WHERE fo.order_id IS NULL
            """
        ).fetchone()[0]
        if missing_fk != 0:
            raise ValueError(
                "core.fact_payments.order_id does not resolve to core.fact_orders"
            )

    return None


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the retail pipeline end-to-end")

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
    parser.add_argument(
        "--profile-sql-directory",
        type=Path,
        default=DEFAULT_PROFILE_DIRECTORY,
    )
    parser.add_argument(
        "--profile-report-directory",
        type=Path,
        default=DEFAULT_REPORT_DIRECTORY,
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    try:
        run_pipeline(
            raw_directory=args.raw_directory,
            database_path=args.database,
            profile_sql_directory=args.profile_sql_directory,
            profile_report_directory=args.profile_report_directory,
        )
    except Exception as exc:  # pragma: no cover - error paths exercised by tests
        print(f"Pipeline failed: {exc}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
