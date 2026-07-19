CREATE OR REPLACE TABLE profile.relationship_checks AS
SELECT
    'orders_without_customer' AS check_name,
    COUNT(*) AS failure_count
FROM raw.orders AS orders
LEFT JOIN raw.customers AS customers
    ON orders.customer_id = customers.customer_id
WHERE customers.customer_id IS NULL

UNION ALL

SELECT
    'order_items_without_order',
    COUNT(*)
FROM raw.order_items AS items
LEFT JOIN raw.orders AS orders
    ON items.order_id = orders.order_id
WHERE orders.order_id IS NULL

UNION ALL

SELECT
    'order_items_without_product',
    COUNT(*)
FROM raw.order_items AS items
LEFT JOIN raw.products AS products
    ON items.product_id = products.product_id
WHERE products.product_id IS NULL

UNION ALL

SELECT
    'order_items_without_seller',
    COUNT(*)
FROM raw.order_items AS items
LEFT JOIN raw.sellers AS sellers
    ON items.seller_id = sellers.seller_id
WHERE sellers.seller_id IS NULL

UNION ALL

SELECT
    'payments_without_order',
    COUNT(*)
FROM raw.order_payments AS payments
LEFT JOIN raw.orders AS orders
    ON payments.order_id = orders.order_id
WHERE orders.order_id IS NULL;