CREATE SCHEMA IF NOT EXISTS mart;

SET search_path='core';

CREATE OR REPLACE TABLE mart.customer_summary AS
WITH
items_per_order AS (
    SELECT order_id, COUNT(*) AS item_count, SUM(price) AS item_revenue
    FROM fact_order_items
    GROUP BY order_id
),
payments_per_order AS (
    SELECT order_id, SUM(payment_value) AS payment_value
    FROM fact_payments
    GROUP BY order_id
),
orders AS (
    SELECT
        fo.order_id,
        DATE(fo.order_purchase_timestamp) AS purchase_date,
        fo.customer_key,
        fo.order_status,
        COALESCE(ipo.item_count, 0) AS item_count,
        COALESCE(ipo.item_revenue, 0.0) AS item_revenue,
        COALESCE(pp.payment_value, 0.0) AS payment_value
    FROM fact_orders fo
    LEFT JOIN items_per_order ipo USING(order_id)
    LEFT JOIN payments_per_order pp USING(order_id)
),
orders_with_cust AS (
    SELECT
        o.*,
        dc.customer_unique_id
    FROM orders o
    LEFT JOIN dim_customer dc
      ON o.customer_key = dc.customer_key
)
SELECT
    customer_unique_id,
    MIN(purchase_date) AS first_order_date,
    MAX(purchase_date) AS most_recent_order_date,
    COUNT(DISTINCT order_id) AS order_count,
    SUM(CASE WHEN order_status = 'delivered' THEN 1 ELSE 0 END) AS delivered_order_count,
    SUM(item_count) AS item_count,
    SUM(item_revenue) AS item_revenue,
    SUM(payment_value) AS payment_value,
    NULLIF(SUM(payment_value), 0.0) / NULLIF(COUNT(DISTINCT order_id), 0) AS average_order_value
FROM orders_with_cust
GROUP BY customer_unique_id;
