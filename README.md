Retail Data Pipeline
=====================

Overview
--------
This repository contains a small, self-contained retail data engineering pipeline implemented in Python and DuckDB. It ingests CSV source files (the Olist dataset by default), runs lightweight profiling SQL, materializes a staging layer, builds a core dimensional model (dimensions and facts), and produces business-facing marts. A small Python "sql runner" executes transformation SQL files in deterministic filename order.

This project was implemented as an educational and pragmatic example of a DuckDB-based ETL pipeline with strong engineering principles:

- Clear separation of ingestion, profiling, staging, core, and mart layers
- Explicit casting and trimming of raw data in the staging layer
- Deterministic SQL execution order
- Idempotent transformations (CREATE OR REPLACE TABLE)
- Focused unit tests and a lightweight CI workflow

Key features
------------
- Single-file DuckDB database (data/database/retail.duckdb by default)
- CLI entrypoint: python -m retail_pipeline.pipeline
- SQL-based transformations stored under src/retail_pipeline/transformations/sql/{staging,core,marts}
- Lightweight profiling (profiling/sql) with CSV report export (profiling/reports)
- Small test fixtures for fast CI and development (tests/fixtures/olist)

Quickstart (development)
------------------------
1. Create and activate a Python virtual environment (recommended):

   python -m venv .venv
   source .venv/bin/activate

2. Install the project and dev dependencies:

   python -m pip install --upgrade pip
   python -m pip install .[dev]

3. Run linting and tests:

   python -m ruff check .
   python -m pytest

4. Run the full pipeline against the bundled fixtures (fast):

   python -m retail_pipeline.pipeline \
     --raw-directory tests/fixtures/olist \
     --database /tmp/retail.duckdb \
     --profile-report-directory /tmp/profiling-reports

5. Run the pipeline against the real dataset (if present):

   python -m retail_pipeline.pipeline

   By default the pipeline reads CSVs from data/raw and uses data/database/retail.duckdb.

Repository layout
-----------------
- src/retail_pipeline/
  - database.py         -- DuckDB connection helper
  - ingestion/load_raw.py -- CSV ingestion into raw schema
  - profiling/run_profiles.py -- run profiling SQL and export reports
  - sql_runner.py       -- discover and execute SQL files in filename order
  - pipeline.py         -- CLI entrypoint orchestrating all stages
  - transformations/sql/
    - staging/
    - core/
    - marts/
- tests/                -- unit tests and lightweight fixtures
- tests/fixtures/olist/ -- small CSV fixtures used in CI
- profiling/sql/        -- SQL used to profile raw data
- data/database/        -- default DuckDB database path

Design & Conventions
--------------------
Staging layer
- SQL files under transformations/sql/staging create staging.* tables from raw.*.
- Staging SQL uses explicit CAST / TRY_CAST and TRIM patterns to handle mixed input types:
  - NULLIF(TRIM(CAST(col AS VARCHAR)), '') to convert empty strings to NULL
  - TRY_CAST(... AS TIMESTAMP/INTEGER/DOUBLE) for safe conversions
- Do not perform joins or aggregations in staging — staging should be a 1:1 mapping with defensive parsing.

Core layer
- Implements dimension and fact tables (dim_*, fact_*).
- Surrogate keys are deterministic (hash-based) to allow idempotent rebuilds.
- dim_date is built with a calendar range covering the observed event dates.

Marts
- Business-facing aggregations that read only from core (not raw or staging).
- Pre-aggregate facts where necessary to avoid fan-out and double-counting.

SQL runner
- The SQL runner executes SQL files in deterministic filename order inside a single DuckDB connection.
- Each SQL file may contain multiple statements and may use CREATE OR REPLACE TABLE.

Validation
- A final validation step checks that expected tables exist, are non-empty, core/mart grains are unique, and key resolution holds between facts and dimensions.
- The pipeline CLI runs this validation as a final step; validation failures raise clear errors.

Testing
-------
- Unit tests live under tests/ and cover staging, core, marts, pipeline behavior, and the SQL runner.
- A small set of CSV fixtures are under tests/fixtures/olist to enable a fast end-to-end test in CI.
- Tests use temporary DuckDB databases via pytest tmp_path and do not modify committed databases.

CI
--
A GitHub Actions workflow (.github/workflows/ci.yml) runs on pushes and PRs targeting main. The workflow sets up Python 3.11, installs the project (including dev extras), runs ruff and pytest, and executes the lightweight end-to-end pipeline against the fixture CSVs. Profiling reports from the CI run are uploaded as an artifact.

Extending the project
---------------------
- Adding a new staging/core/mart transformation:
  1. Add a new SQL file to the appropriate folder with a filename prefix that sorts in the desired order (e.g., 001_..., 002_...).
  2. Use CREATE OR REPLACE TABLE and keep the transformation idempotent.
  3. Add tests that create minimal raw tables and assert the expected outcome.

- Adding profiling checks:
  1. Add SQL files to profiling/sql/. They will be executed by the profiling stage and exported to profiling/reports.

Troubleshooting
---------------
- If the pipeline fails during validation, examine the printed error message — validate_database raises descriptive ValueError messages.
- For SQL binder errors (ambiguous column names), inspect transformations to ensure aliases are qualified (e.g., fi.order_id vs o.order_id).
- Use the tests/fixtures/olist dataset to reproduce issues quickly.

Contact / Authors
-----------------
This repository was created with the assistance of an AI-powered helper during an interactive session. For questions about the implementation or to request changes, open an issue or a pull request.

License
-------
This project follows the license of the original dataset and your organisation's policies. No license file is included by default.

Repository file tree (git-style)
--------------------------------
Below is a compact representation of the repository layout. Use this as a quick map when navigating the codebase.

```
.
├── .github/
│   └── workflows/ci.yml                # CI workflow
├── data/
│   └── database/retail.duckdb          # default DuckDB database (generated)
├── profiling/
│   ├── sql/                            # profiling SQL checks
│   └── reports/                        # exported profiling CSVs
├── src/
│   └── retail_pipeline/
│       ├── database.py                 # DuckDB connection helper
│       ├── ingestion/load_raw.py       # CSV ingestion into raw schema
│       ├── profiling/run_profiles.py   # run profiling SQL and export reports
│       ├── sql_runner.py               # discover and execute SQL files
│       ├── pipeline.py                 # CLI entrypoint (runs full pipeline)
│       └── transformations/
│           └── sql/
│               ├── staging/            # staging SQL files
│               ├── core/               # dimensional model SQL files
│               └── marts/              # mart SQL files
├── tests/                              # unit tests and small fixtures
│   └── fixtures/olist/                  # lightweight CSV fixtures for CI
└── README.md
```

Stage summary
-------------
The pipeline executes these stages in order. The table maps a stage to its primary implementation location.

| Stage | Purpose | Primary files / directories |
|-------|---------|----------------------------|
| 1. Raw ingestion | Read CSVs into raw schema | src/retail_pipeline/ingestion/load_raw.py (data/raw/)
| 2. Profiling | Run SQL checks and export reports | profiling/sql/ + src/retail_pipeline/profiling/run_profiles.py
| 3. Staging | Defensive parsing & normalization | src/retail_pipeline/transformations/sql/staging/
| 4. Core | Dimensions & facts (dim_/fact_) | src/retail_pipeline/transformations/sql/core/
| 5. Marts | Business-facing aggregates | src/retail_pipeline/transformations/sql/marts/
| 6. Validation | Structural & referential checks | src/retail_pipeline/pipeline.py (validate_database)

Common commands
---------------
| Action | Command |
|--------|---------|
| Run pipeline (defaults) | python -m retail_pipeline.pipeline |
| Run pipeline with fixtures | python -m retail_pipeline.pipeline --raw-directory tests/fixtures/olist --database /tmp/retail.duckdb --profile-report-directory /tmp/profiling-reports |
| Lint | python -m ruff check . |
| Run unit tests | python -m pytest |

Notes on repo changes
---------------------
- Documentation files were consolidated into README.md. If you prefer a separate docs/ directory (for GitHub Pages or mkdocs), the README content can be split into multiple pages.

If you'd like the repository tree expanded or a machine-readable manifest (e.g., CODEOWNERS, or a CONTRIBUTING.md), tell me where you'd like it and I will add it.
