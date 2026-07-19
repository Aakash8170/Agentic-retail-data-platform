CREATE SCHEMA IF NOT EXISTS staging;

CREATE OR REPLACE TABLE staging.products AS
SELECT
    NULLIF(TRIM(CAST(product_id AS VARCHAR)), '') AS product_id,
    NULLIF(TRIM(CAST(product_category_name AS VARCHAR)), '') AS product_category_name,
    TRY_CAST(
        NULLIF(TRIM(CAST(product_name_lenght AS VARCHAR)), '')
        AS INTEGER
    ) AS product_name_lenght,
    TRY_CAST(
        NULLIF(TRIM(CAST(product_description_lenght AS VARCHAR)), '')
        AS INTEGER
    ) AS product_description_lenght,
    TRY_CAST(
        NULLIF(TRIM(CAST(product_photos_qty AS VARCHAR)), '')
        AS INTEGER
    ) AS product_photos_qty,
    TRY_CAST(
        NULLIF(TRIM(CAST(product_weight_g AS VARCHAR)), '')
        AS INTEGER
    ) AS product_weight_g,
    TRY_CAST(
        NULLIF(TRIM(CAST(product_length_cm AS VARCHAR)), '')
        AS INTEGER
    ) AS product_length_cm,
    TRY_CAST(
        NULLIF(TRIM(CAST(product_height_cm AS VARCHAR)), '')
        AS INTEGER
    ) AS product_height_cm,
    TRY_CAST(
        NULLIF(TRIM(CAST(product_width_cm AS VARCHAR)), '')
        AS INTEGER
    ) AS product_width_cm
FROM raw.products;
