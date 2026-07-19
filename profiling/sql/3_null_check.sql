CREATE OR REPLACE TABLE profile.orders_nulls AS
SELECT
    COUNT(*) AS row_count,
    COUNT(*) - COUNT(order_id) AS order_id_nulls,
    COUNT(*) - COUNT(customer_id) AS customer_id_nulls,
    COUNT(*) - COUNT(order_status) AS order_status_nulls,
    COUNT(*) - COUNT(order_purchase_timestamp)
        AS purchase_timestamp_nulls,
    COUNT(*) - COUNT(order_approved_at)
        AS approved_timestamp_nulls,
    COUNT(*) - COUNT(order_delivered_carrier_date)
        AS carrier_timestamp_nulls,
    COUNT(*) - COUNT(order_delivered_customer_date)
        AS delivered_timestamp_nulls,
    COUNT(*) - COUNT(order_estimated_delivery_date)
        AS estimated_delivery_timestamp_nulls
FROM raw.orders;


CREATE OR REPLACE TABLE profile.products_nulls AS
SELECT
    COUNT(*) AS row_count,
    COUNT(*) - COUNT(product_id) AS product_id_nulls,
    COUNT(*) - COUNT(product_category_name) AS category_nulls,
    COUNT(*) - COUNT(product_weight_g) AS weight_nulls,
    COUNT(*) - COUNT(product_length_cm) AS length_nulls,
    COUNT(*) - COUNT(product_height_cm) AS height_nulls,
    COUNT(*) - COUNT(product_width_cm) AS width_nulls
FROM raw.products;