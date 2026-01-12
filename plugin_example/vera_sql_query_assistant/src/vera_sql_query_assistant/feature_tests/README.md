# SQL Query Assistant - Feature Evaluation Guide

Welcome! This directory is the primary workspace for Product Managers and Domain Experts to define
and maintain the quality standards for the **SQL Query Assistant** feature.

## Overview

The goal of this feature is to accurately translate natural language into PostgreSQL queries. As a
contributor to this directory, you control the **Ground Truth** (what the AI should do) and the *
*Scoring Rubric** (how we judge if it succeeded), without needing to write any Python code.

## How to Contribute

### 1. Managing Test Cases

All test cases are defined in `test_cases.yaml`. Each test case consists of:

* **`id`**: A unique identifier.
* **`name`**: A short, descriptive name.
* **`description`**: What this test is specifically checking for (e.g., "Complex Joins").
* **`input`**:
    * `user_query`: The natural language prompt from the user.
    * `context_file_path`: (Optional) A reference to a file in the `resources/` folder containing
      database schema or background context.
* **`expected_output`**: The "Golden" SQL query or a textual refusal. If set to `~` (null), the
  engine relies entirely on the AI Judge's reasoning without a reference.
* **`tags`**: (Optional) Labels like `smoke` or `adversarial` to run specific subsets of tests using
  the `-t` flag in the CLI.

### 2. Modifying Evaluation Specifications (`specs/`)

The AI Judge uses the Markdown files in the `specs/` directory as its "constitution" during
evaluation.

* **`scoring_rubric.md`**: **Crucial.** Defines the 1-5 scales for Business Logic, Efficiency, etc.
  Update this to change the criteria for what constitutes a "5-star" response.
* **`safety_constraints.md`**: Defines hard rules the model must follow (e.g., "The model must never
  generate `DROP` or `DELETE` statements").
* **`style_guidelines.md`**: Defines formatting preferences (e.g., "Always use uppercase for SQL
  keywords").
* **`concept_definition.md`**: Defines domain-specific terms (e.g., what does "Active Customer" mean
  in our specific database context?).
* **`golden_dataset.md`**: Provides general examples of perfect query-to-answer pairs.

### 3. Adding Resources

If your test cases require specific database schemas, metadata, or long context descriptions, add
them as `.md` or `.txt` files in the `resources/` directory and reference them in `test_cases.yaml`
using the `context_file_path` field.

## Running the Evaluation

Once you've updated the test cases or specs, you can run the test from the project root using
the Vera CLI:

```bash
# Run all tests and save results to a folder named 'eval_results'
vera test --dst-dir ./eval_results
```

The output will be a CSV file in `./eval_results` where you can see the numerical scores and the *
*AI Judge's reasoning** for each test.
