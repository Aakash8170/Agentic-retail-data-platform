# Project Instructions

This repository contains a retail data engineering pipeline.

## Engineering principles

- Prefer simple and readable implementations.
- Use Python type hints.
- Add docstrings to public functions.
- Use pathlib for file paths.
- Separate ingestion, validation, transformation, and orchestration logic.
- Never silently discard invalid records.
- Store invalid records in a quarantine area with an issue code.
- Make ingestion idempotent.
- Do not hardcode passwords, credentials, or local absolute paths.
- Read configuration from environment variables or configuration files.
- Add tests for new behavior.
- Keep SQL transformations understandable and documented.
- Explain assumptions before changing schemas or table grain.

## AI behavior

- Do not modify files unrelated to the requested task.
- Do not introduce a new dependency without explaining why.
- Do not mark a task complete unless relevant tests have been run.
- Report which files were changed.
- Ask before making architecture-wide changes.
- Do not invent business rules without documenting them.