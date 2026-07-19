from __future__ import annotations

from pathlib import Path

import pytest

from retail_pipeline import pipeline


def test_run_pipeline_calls_stages_in_order(monkeypatch, tmp_path: Path) -> None:
    calls: list[str] = []

    def fake_load_raw_tables(raw_directory, database_path):
        calls.append("load_raw")

    def fake_run_profiles(sql_directory, report_directory, database_path):
        calls.append("profiles")

    def fake_run_sql_files(sql_dir, database_path):
        # differentiate staging/core/marts by sql_dir name
        calls.append(str(sql_dir))

    monkeypatch.setattr(pipeline, "load_raw_tables", fake_load_raw_tables)
    monkeypatch.setattr(pipeline, "run_profiles", fake_run_profiles)
    monkeypatch.setattr(pipeline, "run_sql_files", fake_run_sql_files)

    def fake_validate(db_path):
        calls.append("validate")

    monkeypatch.setattr(pipeline, "validate_database", fake_validate)

    # run
    db_file = tmp_path / "test.db"
    pipeline.run_pipeline(
        raw_directory=Path("/tmp/raw"),
        database_path=db_file,
        profile_sql_directory=Path("/tmp/prof_sql"),
        profile_report_directory=Path("/tmp/prof_reports"),
    )

    assert calls[0] == "load_raw"
    assert calls[1] == "profiles"
    # next three must be the staging/core/marts directories in that order
    assert "transformations/sql/staging" in calls[2]
    assert "transformations/sql/core" in calls[3]
    assert "transformations/sql/marts" in calls[4]
    # validation must be last
    assert calls[5] == "validate"


def test_main_exits_nonzero_when_stage_fails(monkeypatch):
    def fail_run_pipeline(*args, **kwargs):
        raise RuntimeError("simulated failure")

    monkeypatch.setattr(pipeline, "run_pipeline", fail_run_pipeline)

    with pytest.raises(SystemExit) as excinfo:
        pipeline.main([])

    assert excinfo.value.code == 1


def test_validate_database_raises_on_missing_tables(tmp_path: Path):
    # create an empty DuckDB file with only a subset of required tables
    db_file = tmp_path / "validate.duckdb"

    from retail_pipeline.database import get_connection

    with get_connection(db_file) as conn:
        conn.execute("CREATE SCHEMA IF NOT EXISTS raw")
        conn.execute(
            "CREATE TABLE raw.customers (customer_id VARCHAR);"
        )
        conn.execute("INSERT INTO raw.customers VALUES ('c1');")

    with pytest.raises(ValueError) as excinfo:
        pipeline.validate_database(db_file)

    msg = str(excinfo.value)
    assert (
        "Missing staging tables" in msg
        or "Missing core tables" in msg
    )
