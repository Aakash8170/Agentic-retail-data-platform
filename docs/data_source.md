# Data Source
# Olist Source Data Inventory

## Dataset overview

The source data represents a Brazilian e-commerce marketplace. The
dataset contains customer, order, product, payment, seller, review,
geolocation, and product-category information.

Raw source files are stored locally under `data/raw/` and are not
committed to Git. The ingestion layer reads these CSVs with DuckDB's
read_csv(auto_detect) and materializes them into the `raw` schema.

## Source tables (mapping to raw schema)

| Source file | raw table | Expected grain | Candidate key | Main relationships |
|---|---:|---|---|---|
| `olist_customers_dataset.csv` | `raw.customers` | One row per customer record tied to an order | `customer_id` | Joins to `raw.orders` (order-level customer_id), maps to `staging.customers` |
| `olist_orders_dataset.csv` | `raw.orders` | One row per order | `order_id` | Joins to `raw.customers`, `raw.order_items`, `raw.order_payments`, `raw.order_reviews` |
| `olist_order_items_dataset.csv` | `raw.order_items` | One row per order item | `order_id`, `order_item_id` | Joins to `raw.orders`, `raw.products`, `raw.sellers` |
| `olist_order_payments_dataset.csv` | `raw.order_payments` | One row per payment record per order | `order_id`, `payment_sequential` | Joins to `raw.orders` |
| `olist_order_reviews_dataset.csv` | `raw.order_reviews` | One row per review | `review_id` | Joins to `raw.orders` |
| `olist_products_dataset.csv` | `raw.products` | One row per product | `product_id` | Joins to `raw.order_items` |
| `olist_sellers_dataset.csv` | `raw.sellers` | One row per seller | `seller_id` | Joins to `raw.order_items` |
| `olist_geolocation_dataset.csv` | `raw.geolocation` | One or more rows per postal code prefix | (none guaranteed) | Supports geographic enrichment of sellers/customers |
| `product_category_name_translation.csv` | `raw.category_translation` | One row per category translation | `product_category_name` | Joins to `raw.products` / `staging.products` |

## Important source-model observations

- `customer_id` vs `customer_unique_id`: use `customer_unique_id` for
  analytics-level customer identity; `customer_id` is order-scoped.

- Timestamps: orders include multiple lifecycle timestamps. Staging
  converts those to DuckDB TIMESTAMP via TRY_CAST so NULLs and empty
  strings are handled safely.

- Payments and items: payments are at the payment-row granularity and
  must be carefully aggregated to avoid double-counting when joining
  with order items — marts use pre-aggregation patterns.

- Geolocation: may contain multiple rows per postal prefix; define
  aggregation/deduplication rules before joining to transactional
  tables.

## Staging transformation patterns

Staging SQL follows a defensive parsing pattern to work with both CSVs
and typed DuckDB columns. Common patterns used in `transformations/sql/staging/*`:

- Convert empty strings to NULL and trim whitespace:

  ```sql
  NULLIF(TRIM(CAST(col AS VARCHAR)), '') AS col
  ```

- Safe numeric/timestamp parsing:

  ```sql
  TRY_CAST(NULLIF(TRIM(CAST(price AS VARCHAR)), '') AS DOUBLE) AS price
  TRY_CAST(NULLIF(TRIM(CAST(order_purchase_timestamp AS VARCHAR)), '') AS TIMESTAMP) AS order_purchase_timestamp
  ```

These patterns avoid DuckDB binder errors when the underlying CSVs use
mixed types and ensure staging tables have predictable column types.

## Using the fixtures

The tests/fixtures/olist small CSVs mirror the production filenames and
are intended for fast, deterministic CI runs. They include the minimal
set of data needed to exercise transformations, dim_date generation and
mart aggregations.

For full dataset processing, place the full Olist CSVs under `data/raw/`
matching the expected filenames.
