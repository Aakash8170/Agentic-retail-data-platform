CREATE SCHEMA IF NOT EXISTS profile;

CREATE OR REPLACE TABLE profile.row_counts AS
SELECT 'customers' AS table_name, COUNT(*) AS row_count
FROM raw.customers

UNION ALL

SELECT 'geolocation', COUNT(*)
FROM raw.geolocation

UNION ALL

SELECT 'order_items', COUNT(*)
FROM raw.order_items

UNION ALL

SELECT 'order_payments', COUNT(*)
FROM raw.order_payments

UNION ALL

SELECT 'order_reviews', COUNT(*)
FROM raw.order_reviews

UNION ALL

SELECT 'orders', COUNT(*)
FROM raw.orders

UNION ALL

SELECT 'products', COUNT(*)
FROM raw.products

UNION ALL

SELECT 'sellers', COUNT(*)
FROM raw.sellers

UNION ALL

SELECT 'category_translation', COUNT(*)
FROM raw.category_translation;