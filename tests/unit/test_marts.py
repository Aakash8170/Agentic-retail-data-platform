from pathlib import Path

from src.retail_pipeline.database import get_connection
from src.retail_pipeline.sql_runner import run_sql_files


def _create_minimal_raw(conn):
    conn.execute("CREATE SCHEMA IF NOT EXISTS raw")

    # customers
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
        ('c1', 'cu1', '01234', 'city1', 'SP'),
        ('c2', 'cu2', '01235', 'city2', 'SP');
        """
    )

    # products
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
        ('p1', 'cat', '10', '100', '1', '200', '10', '5', '5'),
        ('p2', 'cat', '5', '50', '1', '100', '5', '5', '2');
        """
    )

    # sellers
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

    # category translation
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

    # orders
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
        ) VALUES
        (
            'o1',
            'c1',
            'delivered',
            '2020-01-01 10:00:00',
            NULL,
            NULL,
            NULL,
            '2020-01-05 00:00:00'
        ),
        (
            'o2',
            'c2',
            'delivered',
            '2020-01-01 11:00:00',
            NULL,
            NULL,
            NULL,
            '2020-01-06 00:00:00'
        );
        """
    )

    # order_items
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
        ('o1', '1', 'p1', 's1', '2020-01-02 00:00:00', '10.0', '1.0'),
        ('o1', '2', 'p2', 's1', '2020-01-02 00:00:00', '20.0', '2.0'),
        ('o2', '1', 'p1', 's1', '2020-01-03 00:00:00', '15.0', '1.5');
        """
    )

    # order_payments
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
        ('o1', '1', 'credit_card', '1', '30.0'),
        ('o2', '1', 'credit_card', '1', '16.5');
        """
    )


def test_marts_build_correctly(tmp_path: Path) -> None:
    db_file = tmp_path / "marts.duckdb"

    with get_connection(db_file) as conn:
        _create_minimal_raw(conn)

    staging_dir = Path("src/retail_pipeline/transformations/sql/staging")
    core_dir = Path("src/retail_pipeline/transformations/sql/core")
    mart_dir = Path("src/retail_pipeline/transformations/sql/marts")

    run_sql_files(staging_dir, db_file)
    run_sql_files(core_dir, db_file)
    run_sql_files(mart_dir, db_file)

    with get_connection(db_file) as conn:
        tables = conn.execute(
            """
            SELECT table_name FROM information_schema.tables
            WHERE table_schema = 'mart' ORDER BY table_name
            """
        ).fetchall()

        table_names = {t[0] for t in tables}

        expected = {"daily_sales", "customer_summary", "product_performance"}
        assert expected.issubset(table_names)

        # set search_path to mart for simpler queries
        conn.execute("SET search_path='mart'")

        # grain uniqueness and non-null keys
        ds = conn.execute(
            """
            SELECT COUNT(*), COUNT(DISTINCT purchase_date)
            FROM daily_sales
            """
        ).fetchone()
        assert ds[0] == ds[1]

        cs = conn.execute(
            """
            SELECT COUNT(*), COUNT(DISTINCT customer_unique_id)
            FROM customer_summary
            """
        ).fetchone()
        assert cs[0] == cs[1]
        assert conn.execute(
            """
            SELECT COUNT(*)
            FROM customer_summary
            WHERE customer_unique_id IS NULL
            """
        ).fetchone()[0] == 0

        pp = conn.execute(
            """
            SELECT COUNT(*), COUNT(DISTINCT product_id)
            FROM product_performance
            """
        ).fetchone()
        assert pp[0] == pp[1]
        assert conn.execute(
            """
            SELECT COUNT(*)
            FROM product_performance
            WHERE product_id IS NULL
            """
        ).fetchone()[0] == 0

        # daily_sales reconcile with core facts
        total_item_revenue = conn.execute(
            """
            SELECT SUM(item_revenue)
            FROM daily_sales
            """
        ).fetchone()[0]
        core_item_revenue = conn.execute(
            """
            SELECT SUM(price)
            FROM core.fact_order_items
            """
        ).fetchone()[0]
        assert abs(total_item_revenue - core_item_revenue) < 1e-9

        total_payment_value = conn.execute(
            """
            SELECT SUM(payment_value)
            FROM daily_sales
            """
        ).fetchone()[0]
        core_payment_value = conn.execute(
            """
            SELECT SUM(payment_value)
            FROM core.fact_payments
            """
        ).fetchone()[0]
        assert abs(total_payment_value - core_payment_value) < 1e-9

        # customer_summary payments reconcile to core.fact_payments via orders
        cust_pay = conn.execute(
            """
            SELECT cs.customer_unique_id,
                   cs.payment_value,
                   SUM(fp.payment_value) AS core_total
            FROM mart.customer_summary cs
            LEFT JOIN core.dim_customer dc
              ON dc.customer_unique_id = cs.customer_unique_id
            LEFT JOIN core.fact_orders fo
              ON fo.customer_key = dc.customer_key
            LEFT JOIN core.fact_payments fp
              ON fo.order_id = fp.order_id
            GROUP BY cs.customer_unique_id, cs.payment_value
            """
        ).fetchall()

        for row in cust_pay:
            assert abs((row[1] or 0) - (row[2] or 0)) < 1e-9

        # product_performance item revenue reconciles to core.fact_order_items
        prod_rev = conn.execute(
            """
            SELECT pp.product_id, pp.item_revenue, COALESCE(ci.core_sum, 0) AS core_sum
            FROM mart.product_performance pp
            LEFT JOIN (
                SELECT product_id, SUM(price) AS core_sum
                FROM core.fact_order_items
                GROUP BY product_id
            ) ci ON pp.product_id = ci.product_id
            """
        ).fetchall()

        for row in prod_rev:
            assert abs((row[1] or 0) - (row[2] or 0)) < 1e-9
