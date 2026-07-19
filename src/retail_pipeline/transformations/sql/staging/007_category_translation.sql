CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.category_translation AS
SELECT
    NULLIF(TRIM(CAST(product_category_name AS VARCHAR)), '') AS product_category_name,
    NULLIF(TRIM(CAST(product_category_name_english AS VARCHAR)), '') AS product_category_name_english
FROM raw.category_translation;
