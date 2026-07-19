from __future__ import annotations

from pathlib import Path

from .database import get_connection


def discover_sql_files(sql_directory: Path) -> list[Path]:
    """Return SQL files in filename order from sql_directory.

    Raises when the directory does not exist or contains no .sql files.
    """

    if not sql_directory.is_dir():
        raise NotADirectoryError(f"SQL directory not found: {sql_directory}")

    sql_files = sorted(sql_directory.glob("*.sql"))

    if not sql_files:
        raise FileNotFoundError(f"No SQL files found in: {sql_directory}")

    return sql_files


def run_sql_files(sql_directory: Path, database_path: Path) -> None:
    """Execute every SQL file found in sql_directory against database_path.

    Files are run in deterministic filename order. The function opens a
    single DuckDB connection and runs each SQL file sequentially.
    """

    sql_files = discover_sql_files(sql_directory)

    with get_connection(database_path) as conn:
        for sql_file in sql_files:
            sql = sql_file.read_text(encoding="utf-8")
            # Execute the SQL script. Each file may contain multiple statements.
            conn.execute(sql)


__all__ = ["discover_sql_files", "run_sql_files"]
