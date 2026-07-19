CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.order_payments AS
SELECT
    NULLIF(TRIM(CAST(order_id AS VARCHAR)), '') AS order_id,
    TRY_CAST(
        NULLIF(TRIM(CAST(payment_sequential AS VARCHAR)), '')
        AS INTEGER
    ) AS payment_sequential,
    NULLIF(TRIM(CAST(payment_type AS VARCHAR)), '') AS payment_type,
    TRY_CAST(
        NULLIF(TRIM(CAST(payment_installments AS VARCHAR)), '')
        AS INTEGER
    ) AS payment_installments,
    TRY_CAST(
        NULLIF(TRIM(CAST(payment_value AS VARCHAR)), '')
        AS DOUBLE
    ) AS payment_value
FROM raw.order_payments;
