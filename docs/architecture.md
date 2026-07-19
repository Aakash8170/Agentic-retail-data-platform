# Architecture Overview

This document describes the high-level architecture of the retail data
pipeline and how the repository maps onto runtime components.

## Layers and responsibilities

| Layer | Implementation location | Responsibility |
|-------|-------------------------|----------------|
| Raw ingestion | src/retail_pipeline/ingestion/load_raw.py | Read CSVs from data/raw/ and materialize raw.* tables in DuckDB using read_csv(auto_detect)
| Profiling | profiling/sql/ + src/retail_pipeline/profiling/run_profiles.py | Execute SQL checks against raw.* and export results to profiling/reports/
| Staging | src/retail_pipeline/transformations/sql/staging/ | Defensive parsing and normalization of raw data (CAST/TRY_CAST, TRIM, NULLIF). No aggregations.
| Core | src/retail_pipeline/transformations/sql/core/ | Build dimensional model: dim_* and fact_* tables with deterministic keys and documented grains
| Marts | src/retail_pipeline/transformations/sql/marts/ | Business-facing aggregated tables and pre-aggregations for reporting
| Orchestration | src/retail_pipeline/pipeline.py + src/retail_pipeline/sql_runner.py | Run stages in deterministic order and validate outputs

## Execution flow

1. Ingestion loads CSV files into `raw.*` tables (DuckDB `read_csv`).
2. Profiling SQL runs to produce quality reports (CSV export).
3. Staging SQL files are executed in filename order and produce `staging.*` tables.
4. Core SQL builds `core.dim_*` and `core.fact_*` tables.
5. Mart SQL materializes `mart.*` tables.
6. Final validation checks schema, non-empty tables, grain uniqueness, and FK resolution.

## Idempotency and determinism

- All transformations use `CREATE OR REPLACE TABLE` to ensure repeated
  runs are idempotent.
- SQL files are executed in deterministic filename order to ensure stable
  builds. Use numeric prefixes (e.g., `001_`) to control ordering.
- Deterministic surrogate keys (hash-based) are used so keys remain stable
  across re-runs without stateful sequences.

## Notes on scaling and extension

- This design is optimized for local and single-node DuckDB workloads.
- To scale to larger datasets, consider partitioned file formats (Parquet),
  and an orchestration framework (e.g., Airflow) if long-running orchestration
  and retry semantics are required.

## Component table (quick reference)

| Component | File/dir | Short description |
|-----------|----------|-------------------|
| DB connector | src/retail_pipeline/database.py | get_connection contextmanager (creates parent directories) |
| CSV loader | src/retail_pipeline/ingestion/load_raw.py | validate_source_files(), load_raw_tables() |
| SQL runner | src/retail_pipeline/sql_runner.py | discover_sql_files(), run_sql_files() |
| Profiling runner | src/retail_pipeline/profiling/run_profiles.py | discover + run profiling SQL and export reports |
| Pipeline CLI | src/retail_pipeline/pipeline.py | run_pipeline(), validate_database(), CLI entrypoint |
