CREATE SCHEMA IF NOT EXISTS core;

-- set search path to ensure unqualified references resolve to the core schema
SET search_path='core';

CREATE OR REPLACE TABLE dim_product AS
SELECT
    p.product_id,
    MIN(p.product_category_name) AS product_category_name,
    MIN(pt.product_category_name_english) AS product_category_name_english,
    MIN(p.product_name_lenght) AS product_name_lenght,
    MIN(p.product_description_lenght) AS product_description_lenght,
    MIN(p.product_photos_qty) AS product_photos_qty,
    MIN(p.product_weight_g) AS product_weight_g,
    MIN(p.product_length_cm) AS product_length_cm,
    MIN(p.product_height_cm) AS product_height_cm,
    MIN(p.product_width_cm) AS product_width_cm,
    hash(p.product_id) AS product_key
FROM staging.products p
LEFT JOIN staging.category_translation pt
  ON p.product_category_name = pt.product_category_name
GROUP BY p.product_id;
