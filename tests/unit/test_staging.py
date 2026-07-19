from pathlib import Path

from src.retail_pipeline.database import get_connection
from src.retail_pipeline.sql_runner import run_sql_files


def _create_minimal_raw_tables(connection):
    connection.execute("CREATE SCHEMA IF NOT EXISTS raw")

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS raw.customers (
            customer_id VARCHAR,
            customer_unique_id VARCHAR,
            customer_zip_code_prefix VARCHAR,
            customer_city VARCHAR,
            customer_state VARCHAR
        );
        """
    )

    connection.execute(
        """
        INSERT INTO raw.customers VALUES
        (' c1 ', ' u1 ', '01234', ' city ', 'SP'),
        ('c2', '', '', '', NULL);
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS raw.orders (
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

    connection.execute(
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
            ' o1 ',
            ' c1 ',
            'delivered',
            '2018-01-01 00:00:00',
            '',
            '',
            '',
            '2018-01-05 00:00:00'
        );
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS raw.order_items (
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

    connection.execute(
        """
        INSERT INTO raw.order_items VALUES
        (' o1 ', '1', 'p1', 's1', '2018-01-02 00:00:00', '10.5', '2.0');
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS raw.order_payments (
            order_id VARCHAR,
            payment_sequential VARCHAR,
            payment_type VARCHAR,
            payment_installments VARCHAR,
            payment_value VARCHAR
        );
        """
    )

    connection.execute(
        """
        INSERT INTO raw.order_payments VALUES
        (' o1 ', '1', 'credit_card', '1', '10.5');
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS raw.products (
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

    connection.execute(
        """
        INSERT INTO raw.products VALUES
        (' p1 ', ' category ', '10', '100', '1', '200', '10', '5', '5');
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS raw.sellers (
            seller_id VARCHAR,
            seller_zip_code_prefix VARCHAR,
            seller_city VARCHAR,
            seller_state VARCHAR
        );
        """
    )

    connection.execute(
        """
        INSERT INTO raw.sellers VALUES
        (' s1 ', '01234', ' city ', 'SP');
        """
    )

    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS raw.category_translation (
            product_category_name VARCHAR,
            product_category_name_english VARCHAR
        );
        """
    )

    connection.execute(
        """
        INSERT INTO raw.category_translation VALUES
        (' category ', ' category_en ');
        """
    )


def test_run_staging_creates_tables(tmp_path: Path) -> None:
    db_file = tmp_path / "test.duckdb"

    # prepare a temporary database with minimal raw tables
    with get_connection(db_file) as conn:
        _create_minimal_raw_tables(conn)

    # run staging SQL files (directory inside package)
    sql_dir = Path("src/retail_pipeline/transformations/sql/staging")
    run_sql_files(sql_dir, db_file)

    # verify staging tables and data transformations
    with get_connection(db_file) as conn:
        customers = conn.execute(
            """
            SELECT customer_id,
                   customer_zip_code_prefix,
                   customer_city
            FROM staging.customers
            ORDER BY customer_id
            """
        ).fetchall()

        # first row trimmed, zip cast to integer, city trimmed
        assert customers[0][0] == 'c1'
        assert customers[0][1] == 1234
        assert customers[0][2] == 'city'

        # The second row should remain, while blank values become NULL.
        second = conn.execute(
            """
            SELECT customer_unique_id,
                   customer_zip_code_prefix,
                   customer_city
            FROM staging.customers
            WHERE customer_id = 'c2'
            """
        ).fetchone()
        assert second[0] is None
        assert second[1] is None
        assert second[2] is None

        # verify orders timestamp cast
        order_row = conn.execute(
            """
            SELECT order_id,
                   order_purchase_timestamp,
                   order_estimated_delivery_date
            FROM staging.orders
            WHERE order_id = 'o1'
            """
        ).fetchone()

        assert order_row[0] == 'o1'
        assert order_row[1] is not None
        assert order_row[2] is not None


def test_run_staging_with_typed_raw_tables(tmp_path: Path) -> None:
    """Ensure staging SQL works when raw tables have native typed columns.

    This creates raw tables where timestamps and numeric columns are native
    DuckDB types (TIMESTAMP, INTEGER, DOUBLE) and verifies the staging
    transformations still run without binder errors and produce expected
    values.
    """

    db_file = tmp_path / "typed.duckdb"

    with get_connection(db_file) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")

        # customers with integer zip code
        conn.execute(
            """
            CREATE TABLE raw.customers (
                customer_id VARCHAR,
                customer_unique_id VARCHAR,
                customer_zip_code_prefix INTEGER,
                customer_city VARCHAR,
                customer_state VARCHAR
            );
            """
        )

        conn.execute(
            """
            INSERT INTO raw.customers VALUES
            ('t1', 'tu1', 54321, 'typed city', 'SP');
            """
        )

        # orders with native TIMESTAMP columns
        conn.execute(
            """
            CREATE TABLE raw.orders (
                order_id VARCHAR,
                customer_id VARCHAR,
                order_status VARCHAR,
                order_purchase_timestamp TIMESTAMP,
                order_approved_at TIMESTAMP,
                order_delivered_carrier_date TIMESTAMP,
                order_delivered_customer_date TIMESTAMP,
                order_estimated_delivery_date TIMESTAMP
            );
            """
        )

        conn.execute(
            """
            INSERT INTO raw.orders VALUES
            ('to1', 't1', 'delivered',
             '2019-01-01 12:00:00'::TIMESTAMP,
             NULL, NULL, NULL,
             '2019-01-05 12:00:00'::TIMESTAMP);
            """
        )

        # order_items with native numeric types
        conn.execute(
            """
            CREATE TABLE raw.order_items (
                order_id VARCHAR,
                order_item_id INTEGER,
                product_id VARCHAR,
                seller_id VARCHAR,
                shipping_limit_date TIMESTAMP,
                price DOUBLE,
                freight_value DOUBLE
            );
            """
        )

        conn.execute(
            """
            INSERT INTO raw.order_items VALUES
            ('to1', 1, 'tp1', 'ts1', '2019-01-02 00:00:00'::TIMESTAMP, 12.34, 1.23);
            """
        )

        # order_payments with native numeric types
        conn.execute(
            """
            CREATE TABLE raw.order_payments (
                order_id VARCHAR,
                payment_sequential INTEGER,
                payment_type VARCHAR,
                payment_installments INTEGER,
                payment_value DOUBLE
            );
            """
        )

        conn.execute(
            """
            INSERT INTO raw.order_payments VALUES
            ('to1', 1, 'credit_card', 1, 12.34);
            """
        )

        # create minimal remaining raw tables referenced by staging
        conn.execute(
            """
            CREATE TABLE raw.products (
                product_id VARCHAR,
                product_category_name VARCHAR,
                product_name_lenght INTEGER,
                product_description_lenght INTEGER,
                product_photos_qty INTEGER,
                product_weight_g INTEGER,
                product_length_cm INTEGER,
                product_height_cm INTEGER,
                product_width_cm INTEGER
            );
            """
        )

        conn.execute(
            """
            INSERT INTO raw.products VALUES
            ('tp1', 'tcat', 10, 100, 1, 200, 10, 5, 5);
            """
        )

        conn.execute(
            """
            CREATE TABLE raw.sellers (
                seller_id VARCHAR,
                seller_zip_code_prefix INTEGER,
                seller_city VARCHAR,
                seller_state VARCHAR
            );
            """
        )

        conn.execute(
            """
            INSERT INTO raw.sellers VALUES
            ('ts1', 12345, 'sellers city', 'SP');
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
            ('tcat', 'tcat_en');
            """
        )

    # run staging SQL files
    sql_dir = Path("src/retail_pipeline/transformations/sql/staging")
    run_sql_files(sql_dir, db_file)

    # verify staging results
    with get_connection(db_file) as conn:
        customer = conn.execute(
            "SELECT customer_id, customer_zip_code_prefix FROM staging.customers "
            "WHERE customer_id = 't1'"
        ).fetchone()

        assert customer[0] == 't1'
        assert customer[1] == 54321

        order = conn.execute(
            "SELECT order_id, order_purchase_timestamp, order_estimated_delivery_date "
            "FROM staging.orders WHERE order_id = 'to1'"
        ).fetchone()

        assert order[0] == 'to1'
        assert order[1] is not None
        assert order[2] is not None

        item = conn.execute(
            "SELECT order_item_id, price, freight_value FROM staging.order_items "
            "WHERE order_id = 'to1'"
        ).fetchone()

        assert item[0] == 1
        assert abs(item[1] - 12.34) < 1e-9
        assert abs(item[2] - 1.23) < 1e-9
