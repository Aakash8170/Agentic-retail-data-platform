# Project Requirements

## Business scenario

A retail company receives operational data about customers, products,
orders, order items, and payments.

The company needs a reliable analytical platform for sales reporting,
customer analysis, product performance, and payment reconciliation.

## Initial scope

The first version will process:

- Customers
- Products
- Orders
- Order items
- Payments

## Engineering capabilities

The project will demonstrate:

- Batch ingestion into DuckDB
- SQL-based profiling and CSV export
- Defensive staging layer with explicit CAST / TRY_CAST
- Dimensional modeling and fact/mart materialization
- Idempotent transformations (CREATE OR REPLACE TABLE)
- Automated testing and CI with GitHub Actions
- Deterministic SQL execution ordering

## Out of scope for the first version

- Real-time streaming
- Paid cloud infrastructure
- Machine learning
- Customer-facing application
- Production deployment