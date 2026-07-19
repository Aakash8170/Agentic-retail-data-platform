from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import duckdb
from duckdb import DuckDBPyConnection

DEFAULT_DATABASE_PATH = Path("data/database/retail.duckdb")


@contextmanager
def get_connection(
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> Iterator[DuckDBPyConnection]:
    """Create and safely close a DuckDB connection."""

    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(str(database_path))

    try:
        yield connection
    finally:
        connection.close()