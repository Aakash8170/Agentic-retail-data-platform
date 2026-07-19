CREATE OR REPLACE TABLE profile.business_rule_checks AS
SELECT
    'non_positive_item_price' AS check_name,
    COUNT(*) AS failure_count
FROM raw.order_items
WHERE price <= 0

UNION ALL

SELECT
    'negative_freight_value',
    COUNT(*)
FROM raw.order_items
WHERE freight_value < 0

UNION ALL

SELECT
    'negative_payment_value',
    COUNT(*)
FROM raw.order_payments
WHERE payment_value < 0

UNION ALL

SELECT
    'negative_payment_installments',
    COUNT(*)
FROM raw.order_payments
WHERE payment_installments < 0

UNION ALL

SELECT
    'delivered_order_missing_delivery_timestamp',
    COUNT(*)
FROM raw.orders
WHERE order_status = 'delivered'
  AND order_delivered_customer_date IS NULL

UNION ALL

SELECT
    'delivery_before_purchase',
    COUNT(*)
FROM raw.orders
WHERE order_delivered_customer_date IS NOT NULL
  AND order_delivered_customer_date < order_purchase_timestamp

UNION ALL

SELECT
    'carrier_handoff_before_purchase',
    COUNT(*)
FROM raw.orders
WHERE order_delivered_carrier_date IS NOT NULL
  AND order_delivered_carrier_date < order_purchase_timestamp;