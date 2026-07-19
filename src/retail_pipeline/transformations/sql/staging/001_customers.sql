CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.customers AS
SELECT
    NULLIF(TRIM(CAST(customer_id AS VARCHAR)), '') AS customer_id,
    NULLIF(TRIM(CAST(customer_unique_id AS VARCHAR)), '') AS customer_unique_id,
    TRY_CAST(
        NULLIF(TRIM(CAST(customer_zip_code_prefix AS VARCHAR)), '')
        AS INTEGER
    ) AS customer_zip_code_prefix,
    NULLIF(TRIM(CAST(customer_city AS VARCHAR)), '') AS customer_city,
    NULLIF(TRIM(CAST(customer_state AS VARCHAR)), '') AS customer_state
FROM raw.customers;
