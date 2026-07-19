CREATE SCHEMA IF NOT EXISTS core;

-- set search path to ensure unqualified references resolve to the core schema
SET search_path='core';

CREATE OR REPLACE TABLE dim_seller AS
SELECT
    seller_id,
    MIN(seller_zip_code_prefix) AS seller_zip_code_prefix,
    MIN(seller_city) AS seller_city,
    MIN(seller_state) AS seller_state,
    hash(seller_id) AS seller_key
FROM staging.sellers
GROUP BY seller_id;
