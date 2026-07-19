CREATE SCHEMA IF NOT EXISTS mart;

SET search_path='core';

CREATE OR REPLACE TABLE mart.product_performance AS
WITH
product_items AS (
    SELECT
        dp.product_id AS product_id,
        COUNT(DISTINCT fi.order_id) AS order_count,
        COUNT(*) AS units_sold,
        SUM(fi.price) AS item_revenue,
        SUM(fi.freight_value) AS freight_value,
        MIN(fi.order_id) AS sample_order_id,
        MIN(DATE(o.order_purchase_timestamp)) AS first_sale_date,
        MAX(DATE(o.order_purchase_timestamp)) AS last_sale_date
    FROM fact_order_items fi
    LEFT JOIN dim_product dp
      ON fi.product_key = dp.product_key
    LEFT JOIN fact_orders o
      ON fi.order_id = o.order_id
    GROUP BY dp.product_id
)
SELECT
    pi.product_id AS product_id,
    dp.product_key,
    dp.product_category_name,
    dp.product_category_name_english,
    pi.order_count,
    pi.units_sold,
    pi.item_revenue,
    pi.freight_value,
    NULLIF(pi.item_revenue, 0.0) / NULLIF(pi.units_sold, 0) AS average_item_price,
    pi.first_sale_date,
    pi.last_sale_date
FROM product_items pi
LEFT JOIN dim_product dp
  ON pi.product_id = dp.product_id;
