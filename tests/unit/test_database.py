from pathlib import Path

from src.retail_pipeline.database import get_connection


def test_get_connection_creates_database(
    tmp_path: Path,
) -> None:
    database_path = tmp_path / "test.duckdb"

    with get_connection(database_path) as connection:
        result = connection.execute("SELECT 1").fetchone()

    assert result == (1,)
    assert database_path.exists()