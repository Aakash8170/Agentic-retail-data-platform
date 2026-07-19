CREATE SCHEMA IF NOT EXISTS core;

-- set search path to ensure unqualified references resolve to the core schema
SET search_path='core';

-- dim_date: one row per calendar date covering min->max order purchase dates
CREATE OR REPLACE TABLE dim_date AS
WITH RECURSIVE bounds AS (
    SELECT
        MIN(DATE(order_purchase_timestamp)) AS min_date,
        MAX(DATE(order_purchase_timestamp)) AS max_date
    FROM staging.orders
),
dates(dt) AS (
    SELECT min_date FROM bounds
    UNION ALL
    SELECT dt + INTERVAL '1 day' FROM dates, bounds WHERE dt < bounds.max_date
)
SELECT
    dt AS date,
    (EXTRACT(YEAR FROM dt) * 10000
     + EXTRACT(MONTH FROM dt) * 100
     + EXTRACT(DAY FROM dt))::INTEGER AS date_key,
    EXTRACT(YEAR FROM dt)::INTEGER AS year,
    EXTRACT(QUARTER FROM dt)::INTEGER AS quarter,
    EXTRACT(MONTH FROM dt)::INTEGER AS month,
    CASE EXTRACT(MONTH FROM dt)
        WHEN 1 THEN 'January'
        WHEN 2 THEN 'February'
        WHEN 3 THEN 'March'
        WHEN 4 THEN 'April'
        WHEN 5 THEN 'May'
        WHEN 6 THEN 'June'
        WHEN 7 THEN 'July'
        WHEN 8 THEN 'August'
        WHEN 9 THEN 'September'
        WHEN 10 THEN 'October'
        WHEN 11 THEN 'November'
        WHEN 12 THEN 'December'
    END AS month_name,
    EXTRACT(WEEK FROM dt)::INTEGER AS week,
    EXTRACT(DAY FROM dt)::INTEGER AS day,
    CASE EXTRACT(DOW FROM dt)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_name,
    CASE WHEN EXTRACT(DOW FROM dt) IN (0,6) THEN TRUE ELSE FALSE END AS is_weekend
FROM dates;
