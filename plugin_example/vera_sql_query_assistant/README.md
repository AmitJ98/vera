# SQL Query Assistant Plugin for Vera

This repository contains the **SQL Query Assistant** plugin for the **Vera** AI test engine.

## Overview

The SQL Query Assistant is a feature designed to translate natural language questions into
executable SQL queries (PostgreSQL dialect). This plugin allows developers to test the
performance, safety, and accuracy of the assistant using Vera's automated tests framework.

## Purpose

The main purpose of this plugin is to provide a structured way to:

1. **Simulate Feature Execution**: Generate SQL queries based on natural language input and provided
   schema context.
2. **Verify via Static Checks**: Perform programmatic checks on the generated SQL (e.g., ensuring no
   destructive commands like `DROP` or `DELETE` are present).
3. **Evaluate via LLM-as-a-Judge**: Use high-reasoning models to score the generated SQL against
   business logic, efficiency, and syntax correctness.

## Technical Architecture

The plugin is structured as follows:

* `src/sql_query_assistant/plugin_impl.py`: The entry point for Vera. It implements the required
  hooks to load test cases, run the feature, and trigger tests and evaluation.
* `src/sql_query_assistant/core/data_models.py`: Defines the Pydantic models for inputs (
  `SqlQueryInput`), outputs (`SqlQueryOutput`), and the final report row (`SqlQueryRow`).
* `src/sql_query_assistant/core/static_checks.py`: Contains the Python logic for programmatic
  tests of the SQL output.
* `src/sql_query_assistant/core/generate_sql.py`: A mock/wrapper for the actual SQL generation
  logic.
* `src/sql_query_assistant/feature_tests/`: Contains the datasets and specifications used
  during tests.

## For Developers: How to Contribute

Developers contributing to the **code** of this plugin should focus on the following areas:

### 1. Modifying the Execution Logic

If the way the SQL is generated needs to change (e.g., switching to a different internal model or
adding pre-processing steps), update the `run_feature` hook in `plugin_impl.py` or the logic in
`core/generate_sql.py`.

### 2. Adding New Evaluation Metrics

To add a new metric (e.g., "SQL Dialect Compliance"):

1. Update `LlmChecksColumn` or `StaticChecksColumn` in `core/data_models.py`.
2. Update `SqlQueryRow` to include the new field and its CSV alias.
3. Modify `SqlQueryRow.calculate_final_score()` to incorporate the new metric into the weighted
   average.
4. Update the corresponding test hook in `plugin_impl.py`.

### 3. Enhancing Static Checks

Modify `core/static_checks.py` to add more robust programmatic verification, such as checking for
table existence against a schema or validating syntax using a SQL parser.

## Installation

To install this plugin in editable mode for development:

```bash
uv pip install -e .
```
