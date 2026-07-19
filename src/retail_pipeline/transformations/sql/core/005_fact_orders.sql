CREATE SCHEMA IF NOT EXISTS core;

-- set search path to ensure unqualified references resolve to the core schema
SET search_path='core';

CREATE OR REPLACE TABLE fact_orders AS
SELECT
    o.order_id,
    c.customer_key,
    -- derive purchase_date_key as YYYYMMDD integer
    (EXTRACT(YEAR FROM DATE(o.order_purchase_timestamp)) * 10000
     + EXTRACT(MONTH FROM DATE(o.order_purchase_timestamp)) * 100
     + EXTRACT(DAY FROM DATE(o.order_purchase_timestamp)))::INTEGER AS purchase_date_key,
    o.order_status,
    o.order_purchase_timestamp,
    o.order_approved_at,
    o.order_delivered_carrier_date,
    o.order_delivered_customer_date,
    o.order_estimated_delivery_date
FROM staging.orders o
LEFT JOIN dim_customer c
  ON o.customer_id = c.customer_id;
