CREATE OR REPLACE TABLE profile.key_checks AS
SELECT
    'customers.customer_id' AS key_name,
    COUNT(*) AS row_count,
    COUNT(customer_id) AS non_null_count,
    COUNT(DISTINCT customer_id) AS distinct_count,
    COUNT(*) - COUNT(customer_id) AS null_count,
    COUNT(customer_id) - COUNT(DISTINCT customer_id) AS duplicate_count
FROM raw.customers

UNION ALL

SELECT
    'orders.order_id',
    COUNT(*),
    COUNT(order_id),
    COUNT(DISTINCT order_id),
    COUNT(*) - COUNT(order_id),
    COUNT(order_id) - COUNT(DISTINCT order_id)
FROM raw.orders

UNION ALL

SELECT
    'products.product_id',
    COUNT(*),
    COUNT(product_id),
    COUNT(DISTINCT product_id),
    COUNT(*) - COUNT(product_id),
    COUNT(product_id) - COUNT(DISTINCT product_id)
FROM raw.products

UNION ALL

SELECT
    'sellers.seller_id',
    COUNT(*),
    COUNT(seller_id),
    COUNT(DISTINCT seller_id),
    COUNT(*) - COUNT(seller_id),
    COUNT(seller_id) - COUNT(DISTINCT seller_id)
FROM raw.sellers;

CREATE OR REPLACE TABLE profile.composite_key_checks AS
SELECT
    'order_items.(order_id, order_item_id)' AS key_name,
    COUNT(*) AS row_count,
    COUNT(
        DISTINCT (order_id, order_item_id)
    ) AS distinct_count,
    COUNT(*) - COUNT(
        DISTINCT (order_id, order_item_id)
    ) AS duplicate_count
FROM raw.order_items

UNION ALL

SELECT
    'order_payments.(order_id, payment_sequential)',
    COUNT(*),
    COUNT(
        DISTINCT (order_id, payment_sequential)
    ),
    COUNT(*) - COUNT(
        DISTINCT (order_id, payment_sequential)
    )
FROM raw.order_payments;