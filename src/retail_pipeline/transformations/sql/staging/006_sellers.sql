CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.sellers AS
SELECT
    NULLIF(TRIM(CAST(seller_id AS VARCHAR)), '') AS seller_id,
    TRY_CAST(
        NULLIF(TRIM(CAST(seller_zip_code_prefix AS VARCHAR)), '')
        AS INTEGER
    ) AS seller_zip_code_prefix,
    NULLIF(TRIM(CAST(seller_city AS VARCHAR)), '') AS seller_city,
    NULLIF(TRIM(CAST(seller_state AS VARCHAR)), '') AS seller_state
FROM raw.sellers;
