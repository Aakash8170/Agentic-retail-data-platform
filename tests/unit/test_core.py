from pathlib import Path

from src.retail_pipeline.database import get_connection
from src.retail_pipeline.sql_runner import run_sql_files


def _create_minimal_raw_and_stage(conn):
    # reuse earlier staging setup: create raw tables and load minimal rows
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw")

    conn.execute(
        """
        CREATE TABLE raw.customers (
            customer_id VARCHAR,
            customer_unique_id VARCHAR,
            customer_zip_code_prefix VARCHAR,
            customer_city VARCHAR,
            customer_state VARCHAR
        );
        """
    )

    conn.execute(
        """
        INSERT INTO raw.customers VALUES
        ('c1', 'u1', '01234', 'city', 'SP');
        """
    )

    conn.execute(
        """
        CREATE TABLE raw.products (
            product_id VARCHAR,
            product_category_name VARCHAR,
            product_name_lenght VARCHAR,
            product_description_lenght VARCHAR,
            product_photos_qty VARCHAR,
            product_weight_g VARCHAR,
            product_length_cm VARCHAR,
            product_height_cm VARCHAR,
            product_width_cm VARCHAR
        );
        """
    )

    conn.execute(
        """
        INSERT INTO raw.products VALUES
        ('p1', 'cat', '10', '100', '1', '200', '10', '5', '5');
        """
    )

    conn.execute(
        """
        CREATE TABLE raw.sellers (
            seller_id VARCHAR,
            seller_zip_code_prefix VARCHAR,
            seller_city VARCHAR,
            seller_state VARCHAR
        );
        """
    )

    conn.execute(
        """
        INSERT INTO raw.sellers VALUES
        ('s1', '01234', 'seller_city', 'SP');
        """
    )

    conn.execute(
        """
        CREATE TABLE raw.category_translation (
            product_category_name VARCHAR,
            product_category_name_english VARCHAR
        );
        """
    )

    conn.execute(
        """
        INSERT INTO raw.category_translation VALUES
        ('cat', 'cat_en');
        """
    )

    conn.execute(
        """
        CREATE TABLE raw.orders (
            order_id VARCHAR,
            customer_id VARCHAR,
            order_status VARCHAR,
            order_purchase_timestamp VARCHAR,
            order_approved_at VARCHAR,
            order_delivered_carrier_date VARCHAR,
            order_delivered_customer_date VARCHAR,
            order_estimated_delivery_date VARCHAR
        );
        """
    )

    conn.execute(
        """
        INSERT INTO raw.orders (
            order_id,
            customer_id,
            order_status,
            order_purchase_timestamp,
            order_approved_at,
            order_delivered_carrier_date,
            order_delivered_customer_date,
            order_estimated_delivery_date
        ) VALUES (
            'o1',
            'c1',
            'delivered',
            '2020-01-01 10:00:00',
            NULL,
            NULL,
            NULL,
            '2020-01-05 00:00:00'
        );
        """
    )

    conn.execute(
        """
        CREATE TABLE raw.order_items (
            order_id VARCHAR,
            order_item_id VARCHAR,
            product_id VARCHAR,
            seller_id VARCHAR,
            shipping_limit_date VARCHAR,
            price VARCHAR,
            freight_value VARCHAR
        );
        """
    )

    conn.execute(
        """
        INSERT INTO raw.order_items VALUES
        ('o1', '1', 'p1', 's1', '2020-01-02 00:00:00', '10.0', '1.0');
        """
    )

    conn.execute(
        """
        CREATE TABLE raw.order_payments (
            order_id VARCHAR,
            payment_sequential VARCHAR,
            payment_type VARCHAR,
            payment_installments VARCHAR,
            payment_value VARCHAR
        );
        """
    )

    conn.execute(
        """
        INSERT INTO raw.order_payments VALUES
        ('o1', '1', 'credit_card', '1', '10.0');
        """
    )


def test_core_builds_dimensions_and_facts(tmp_path: Path) -> None:
    db_file = tmp_path / "core.duckdb"

    # create minimal raw data
    with get_connection(db_file) as conn:
        _create_minimal_raw_and_stage(conn)

    # run staging first
    staging_dir = Path("src/retail_pipeline/transformations/sql/staging")
    core_dir = Path("src/retail_pipeline/transformations/sql/core")

    run_sql_files(staging_dir, db_file)
    run_sql_files(core_dir, db_file)

    with get_connection(db_file) as conn:
        # check tables exist
        tables = conn.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'core' ORDER BY table_name
            """
        ).fetchall()

        table_names = {t[0] for t in tables}

        expected = {
            'dim_customer',
            'dim_product',
            'dim_seller',
            'dim_date',
            'fact_orders',
            'fact_order_items',
            'fact_payments',
        }

        assert expected.issubset(table_names)

        # ensure queries resolve to core schema by setting search_path
        conn.execute("SET search_path='core'")

        # dimension keys are unique and non-null
        cust_keys = conn.execute(
            """
            SELECT COUNT(*), COUNT(DISTINCT customer_key)
            FROM dim_customer
            """
        ).fetchone()
        assert cust_keys[0] == cust_keys[1]
        assert conn.execute(
            """
            SELECT COUNT(*)
            FROM dim_customer
            WHERE customer_key IS NULL
            """
        ).fetchone()[0] == 0

        prod_keys = conn.execute(
            """
            SELECT COUNT(*), COUNT(DISTINCT product_key)
            FROM dim_product
            """
        ).fetchone()
        assert prod_keys[0] == prod_keys[1]

        seller_keys = conn.execute(
            """
            SELECT COUNT(*), COUNT(DISTINCT seller_key)
            FROM dim_seller
            """
        ).fetchone()
        assert seller_keys[0] == seller_keys[1]

        # fact grains unique
        fo = conn.execute(
            """
            SELECT COUNT(*), COUNT(DISTINCT order_id)
            FROM fact_orders
            """
        ).fetchone()
        assert fo[0] == fo[1]

        foi = conn.execute(
            """
            SELECT COUNT(*), COUNT(DISTINCT (order_id, order_item_id))
            FROM fact_order_items
            """
        ).fetchone()
        assert foi[0] == foi[1]

        fp = conn.execute(
            """
            SELECT COUNT(*), COUNT(DISTINCT (order_id, payment_sequential))
            FROM fact_payments
            """
        ).fetchone()
        assert fp[0] == fp[1]

        # foreign keys resolve to dimensions
        fk_c = conn.execute(
            """
            SELECT COUNT(*)
            FROM fact_orders fo
            LEFT JOIN dim_customer dc
              ON fo.customer_key = dc.customer_key
            WHERE dc.customer_key IS NULL
            """
        ).fetchone()[0]
        assert fk_c == 0

        fk_p = conn.execute(
            """
            SELECT COUNT(*)
            FROM fact_order_items fi
            LEFT JOIN dim_product dp
              ON fi.product_key = dp.product_key
            WHERE dp.product_key IS NULL
            """
        ).fetchone()[0]
        assert fk_p == 0

        fk_s = conn.execute(
            """
            SELECT COUNT(*)
            FROM fact_order_items fi
            LEFT JOIN dim_seller ds
              ON fi.seller_key = ds.seller_key
            WHERE ds.seller_key IS NULL
            """
        ).fetchone()[0]
        assert fk_s == 0

        # dim_date covers all order purchase dates
        min_order_date = conn.execute(
            """
            SELECT MIN(DATE(order_purchase_timestamp))
            FROM staging.orders
            """
        ).fetchone()[0]
        max_order_date = conn.execute(
            """
            SELECT MAX(DATE(order_purchase_timestamp))
            FROM staging.orders
            """
        ).fetchone()[0]

        exists_min = conn.execute(
            """
            SELECT COUNT(*) FROM dim_date WHERE date = ?
            """,
            [min_order_date],
        ).fetchone()[0]
        exists_max = conn.execute(
            """
            SELECT COUNT(*) FROM dim_date WHERE date = ?
            """,
            [max_order_date],
        ).fetchone()[0]

        assert exists_min == 1
        assert exists_max == 1
