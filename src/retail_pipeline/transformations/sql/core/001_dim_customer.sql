CREATE SCHEMA IF NOT EXISTS core;

-- set search path to ensure unqualified references resolve to the core schema
SET search_path='core';

CREATE OR REPLACE TABLE dim_customer AS
SELECT
    customer_id,
    MIN(customer_unique_id) AS customer_unique_id,
    MIN(customer_city) AS customer_city,
    MIN(customer_state) AS customer_state,
    -- deterministic surrogate key based on business key
    hash(customer_id) AS customer_key
FROM staging.customers
GROUP BY customer_id;
