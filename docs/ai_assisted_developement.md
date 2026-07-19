# AI-Assisted Development

## Policy

AI agents may assist with implementation, debugging, test generation,
documentation, and code review. All generated changes are reviewed and
validated by the project owner.

## Entry 001: Repository structure review

### Goal

Review the proposed repository structure for separation of ingestion,
profiling, data quality, and transformation concerns.

### Agent

GitHub Copilot in VS Code.

### Prompt summary

Asked the agent to review the structure without modifying files.

### Useful suggestions

- Separate unit and integration tests.
- Keep pipeline configuration outside application code.
- Add a quarantine directory for invalid records.

### Rejected suggestions

- Adding Airflow before the initial ingestion pipeline existed.
- Introducing a cloud object store during the local development phase.

### Human validation

The final structure was simplified to reduce unnecessary dependencies.