# Data Source
# Olist Source Data Inventory

## Dataset overview

The source data represents a Brazilian e-commerce marketplace. The
dataset contains customer, order, product, payment, seller, review,
geolocation, and product-category information.

Raw source files are stored locally under `data/raw/` and are not
committed to Git.

## Source tables

| Source file | Expected grain | Candidate key | Main relationships |
|---|---|---|---|
| `olist_customers_dataset.csv` | One row per order-specific customer record | `customer_id` | Joins to orders |
| `olist_orders_dataset.csv` | One row per order | `order_id` | Joins to customers, items, payments, and reviews |
| `olist_order_items_dataset.csv` | One row per order item | `order_id`, `order_item_id` | Joins to orders, products, and sellers |
| `olist_order_payments_dataset.csv` | One row per payment sequence | `order_id`, `payment_sequential` | Joins to orders |
| `olist_order_reviews_dataset.csv` | One row per review record | `review_id`, possibly combined with `order_id` | Joins to orders |
| `olist_products_dataset.csv` | One row per product | `product_id` | Joins to order items |
| `olist_sellers_dataset.csv` | One row per seller | `seller_id` | Joins to order items |
| `olist_geolocation_dataset.csv` | One row per geolocation record | No guaranteed unique key | Supports geographic enrichment |
| `product_category_name_translation.csv` | One row per product-category translation | `product_category_name` | Joins to products |

## Important source-model observations

### Customers

The source contains both `customer_id` and `customer_unique_id`.

`customer_id` identifies the customer record used for a particular
order. The same real customer may have different `customer_id` values
across orders.

`customer_unique_id` is the better identifier for customer-level
analytics.

### Orders

The orders table contains the order lifecycle, including purchase,
approval, carrier delivery, customer delivery, and estimated delivery
timestamps.

### Order items

An order may contain multiple order items. The expected grain is one
row per `order_id` and `order_item_id`.

### Payments

An order can have multiple payment records. Therefore, `order_id`
alone is not expected to be unique in the payments source.

### Reviews

Review IDs may not always behave as a simple one-row-per-order key.
Uniqueness and relationship behavior must be confirmed through profiling.

### Geolocation

The geolocation source may contain multiple rows for the same postal
code prefix. It should not be joined directly to transactional tables
without first defining a deduplication or aggregation rule.
