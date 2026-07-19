CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.order_items AS
SELECT
    NULLIF(TRIM(CAST(order_id AS VARCHAR)), '') AS order_id,
    TRY_CAST(
        NULLIF(TRIM(CAST(order_item_id AS VARCHAR)), '')
        AS INTEGER
    ) AS order_item_id,
    NULLIF(TRIM(CAST(product_id AS VARCHAR)), '') AS product_id,
    NULLIF(TRIM(CAST(seller_id AS VARCHAR)), '') AS seller_id,
    TRY_CAST(
        NULLIF(TRIM(CAST(shipping_limit_date AS VARCHAR)), '')
        AS TIMESTAMP
    ) AS shipping_limit_date,
    TRY_CAST(
        NULLIF(TRIM(CAST(price AS VARCHAR)), '')
        AS DOUBLE
    ) AS price,
    TRY_CAST(
        NULLIF(TRIM(CAST(freight_value AS VARCHAR)), '')
        AS DOUBLE
    ) AS freight_value
FROM raw.order_items;
