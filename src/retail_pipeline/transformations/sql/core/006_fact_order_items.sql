CREATE SCHEMA IF NOT EXISTS core;

-- set search path to ensure unqualified references resolve to the core schema
SET search_path='core';

CREATE OR REPLACE TABLE fact_order_items AS
SELECT
    oi.order_id,
    oi.order_item_id,
    p.product_id AS product_id,
    p.product_key,
    s.seller_key,
    oi.price,
    oi.freight_value,
    oi.shipping_limit_date
FROM staging.order_items oi
LEFT JOIN dim_product p
  ON oi.product_id = p.product_id
LEFT JOIN dim_seller s
  ON oi.seller_id = s.seller_id;
