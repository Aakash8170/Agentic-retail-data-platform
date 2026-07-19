CREATE SCHEMA IF NOT EXISTS mart;

-- Build daily sales metrics at purchase_date grain.
-- Read from core tables only. Pre-aggregate order-level items and payments
-- to avoid fan-out when rolling up to dates.
SET search_path='core';

CREATE OR REPLACE TABLE mart.daily_sales AS
WITH
items_per_order AS (
    SELECT
        order_id,
        COUNT(*) AS item_count,
        SUM(price) AS item_revenue,
        SUM(freight_value) AS freight_value
    FROM fact_order_items
    GROUP BY order_id
),
payments_per_order AS (
    SELECT
        order_id,
        SUM(payment_value) AS payment_value
    FROM fact_payments
    GROUP BY order_id
),
orders AS (
    SELECT
        fo.order_id,
        DATE(fo.order_purchase_timestamp) AS purchase_date,
        fo.purchase_date_key,
        fo.customer_key,
        fo.order_status,
        COALESCE(ipo.item_count, 0) AS item_count,
        COALESCE(ipo.item_revenue, 0.0) AS item_revenue,
        COALESCE(ipo.freight_value, 0.0) AS freight_value,
        COALESCE(pp.payment_value, 0.0) AS payment_value
    FROM fact_orders fo
    LEFT JOIN items_per_order ipo USING(order_id)
    LEFT JOIN payments_per_order pp USING(order_id)
)
SELECT
    purchase_date,
    purchase_date_key,
    COUNT(DISTINCT order_id) AS order_count,
    COUNT(DISTINCT customer_key) AS customer_count,
    SUM(CASE WHEN order_status = 'delivered' THEN 1 ELSE 0 END) AS delivered_order_count,
    SUM(item_count) AS item_count,
    SUM(item_revenue) AS item_revenue,
    SUM(freight_value) AS freight_value,
    SUM(payment_value) AS payment_value,
    NULLIF(SUM(payment_value), 0.0) / NULLIF(COUNT(DISTINCT order_id), 0) AS average_order_value
FROM orders
GROUP BY purchase_date, purchase_date_key;
