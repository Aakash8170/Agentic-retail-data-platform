from pathlib import Path

import pytest

from src.retail_pipeline.ingestion.load_raw import validate_source_files


def test_validate_source_files_reports_missing_files(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        FileNotFoundError,
        match="Required source files are missing",
    ):
        validate_source_files(tmp_path)