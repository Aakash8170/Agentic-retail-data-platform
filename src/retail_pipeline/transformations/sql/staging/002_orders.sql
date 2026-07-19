CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.orders AS
SELECT
    NULLIF(TRIM(CAST(order_id AS VARCHAR)), '') AS order_id,
    NULLIF(TRIM(CAST(customer_id AS VARCHAR)), '') AS customer_id,
    NULLIF(TRIM(CAST(order_status AS VARCHAR)), '') AS order_status,
    TRY_CAST(
        NULLIF(TRIM(CAST(order_purchase_timestamp AS VARCHAR)), '')
        AS TIMESTAMP
    ) AS order_purchase_timestamp,
    TRY_CAST(
        NULLIF(TRIM(CAST(order_approved_at AS VARCHAR)), '')
        AS TIMESTAMP
    ) AS order_approved_at,
    TRY_CAST(
        NULLIF(TRIM(CAST(order_delivered_carrier_date AS VARCHAR)), '')
        AS TIMESTAMP
    ) AS order_delivered_carrier_date,
    TRY_CAST(
        NULLIF(TRIM(CAST(order_delivered_customer_date AS VARCHAR)), '')
        AS TIMESTAMP
    ) AS order_delivered_customer_date,
    TRY_CAST(
        NULLIF(TRIM(CAST(order_estimated_delivery_date AS VARCHAR)), '')
        AS TIMESTAMP
    ) AS order_estimated_delivery_date
FROM raw.orders;
