from __future__ import annotations

import argparse
from pathlib import Path

from retail_pipeline.database import DEFAULT_DATABASE_PATH, get_connection

DEFAULT_PROFILE_DIRECTORY = Path("profiling/sql")
DEFAULT_REPORT_DIRECTORY = Path("profiling/reports")


def discover_sql_files(sql_directory: Path) -> list[Path]:
    """Return profiling SQL files in filename order."""

    if not sql_directory.is_dir():
        raise NotADirectoryError(
            f"Profiling SQL directory not found: {sql_directory}"
        )

    sql_files = sorted(sql_directory.glob("*.sql"))

    if not sql_files:
        raise FileNotFoundError(
            f"No SQL files found in: {sql_directory}"
        )

    return sql_files


def export_profile_tables(
    report_directory: Path,
    database_path: Path,
) -> None:
    """Export every profile schema table to CSV."""

    report_directory.mkdir(parents=True, exist_ok=True)

    with get_connection(database_path) as connection:

        tables = connection.execute(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='profile'
            ORDER BY table_name
            """
        ).fetchall()

        for (table_name,) in tables:

            output_file = (
                report_directory / f"{table_name}.csv"
            ).resolve()

            connection.execute(
                f"""
                COPY profile.{table_name}
                TO '{output_file.as_posix()}'
                (HEADER, DELIMITER ',');
                """
            )

            print(f"Exported {output_file.name}")


def run_profiles(
    sql_directory: Path = DEFAULT_PROFILE_DIRECTORY,
    report_directory: Path = DEFAULT_REPORT_DIRECTORY,
    database_path: Path = DEFAULT_DATABASE_PATH,
) -> None:
    """Run SQL profiling and export reports."""

    sql_files = discover_sql_files(sql_directory)

    with get_connection(database_path) as connection:

        for sql_file in sql_files:

            print(f"Running {sql_file.name}")

            sql = sql_file.read_text(encoding="utf-8")

            connection.execute(sql)

    export_profile_tables(
        report_directory=report_directory,
        database_path=database_path,
    )


def parse_arguments() -> argparse.Namespace:

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--sql-directory",
        type=Path,
        default=DEFAULT_PROFILE_DIRECTORY,
    )

    parser.add_argument(
        "--report-directory",
        type=Path,
        default=DEFAULT_REPORT_DIRECTORY,
    )

    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE_PATH,
    )

    return parser.parse_args()


def main() -> None:

    args = parse_arguments()

    run_profiles(
        sql_directory=args.sql_directory,
        report_directory=args.report_directory,
        database_path=args.database,
    )


if __name__ == "__main__":
    main()