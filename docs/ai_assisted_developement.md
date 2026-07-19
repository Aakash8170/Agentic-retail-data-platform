# AI-Assisted Development

## Policy

AI agents may assist with implementation, debugging, test generation,
documentation, and code review. All generated changes are reviewed and
validated by the project owner before being merged.

## How AI was used in this project

This repository was developed interactively with an AI assistant (Copilot
CLI runtime in VS Code). The agent helped with:

- Inspecting repository structure and proposing an implementation plan.
- Generating staging/core/mart SQL templates and a deterministic SQL runner.
- Writing a small Python orchestration entry point (pipeline.py).
- Creating focused unit tests and lightweight fixture data for CI.
- Iteratively fixing lint and test failures (Ruff and pytest).
- Drafting README and developer docs.

All generated code and documentation was reviewed and adjusted by a human
engineer. Any final commits include a Co-authored-by trailer acknowledging
Copilot's assistance.

## Interaction log (summary)

| Phase | Action by AI | Human review action |
|-------|--------------|---------------------|
| Plan | Proposed files and directories to add | Human approved and asked to implement staging SQL first |
| Implementation | Created sql_runner, staging/core/mart SQL files, pipeline CLI | Human reviewed SQL, adjusted for DuckDB compatibility and business rules |
| Tests | Generated unit tests for staging, core, marts, and pipeline | Human ran tests, iterated on fixes and edge cases |
| CI | Created GitHub Actions workflow and lightweight fixtures | Human validated CI locally and tuned workflow |

## Engineering rules followed by the agent

- Do not modify unrelated files without explicit instruction.
- Use explicit CAST/TRY_CAST and TRIM patterns in staging SQL to avoid
  binder errors when CSV types vary.
- Keep transformations idempotent (CREATE OR REPLACE TABLE).
- Run tests and linters and iterate until they pass locally.

## Review guidance

When reviewing changes created with AI assistance, pay attention to:
- Business logic and semantic correctness of SQL transformations.
- Any places where deterministic hashing or surrogate-key strategies were used.
- Error handling and validation messages.

This file documents the collaboration model and is intended to help future
reviewers understand the provenance of generated artifacts.