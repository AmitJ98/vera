# Testing Philosophy

Vera is built on the principle that AI features should be tested with the same rigor as
traditional software, but with techniques adapted for the probabilistic nature of Large Language
Models (LLMs).

## The Core Idea: "LLM-as-a-Judge"

While unit tests are great for deterministic code, they often struggle with natural language
generation or complex reasoning tasks. Vera combines two layers of tests/evaluation:

1. **Static Checks**: Programmatic verification using Python code. This is used for things that
   *can* be determined definitively, like SQL syntax validity, regex matching, or ensuring certain
   forbidden strings (like `DROP TABLE`) are absent.
2. **LLM-as-a-Judge**: Using a high-reasoning model (like Gemini 1.5 Pro) to test the output
   against human-readable specifications. This allows for nuanced grading of business logic, tone,
   and safety that a regex simply cannot capture.

## Evaluation and Test Specifications (Specs)

A key innovation in Vera is the use of structured Markdown "Specs" to guide the LLM Judge. These
specs are defined per feature and provide the context needed for an accurate evaluation.

### 1. Scoring Rubric (`scoring_rubric.md`)

The Rubric is the most important spec. It defines the specific metrics (e.g., Business Logic,
Efficiency, Accuracy) and a scale (typically 1-5) for each.

- **Why?**: It ensures the LLM Judge evaluates the feature consistently across different test cases
  and runs.

### 2. Safety & Hard Constraints (`safety_constraints.md`)

This file lists the "red lines" the feature must not cross.

- **Why?**: If a safety constraint is violated, the model should fail the test immediately,
  regardless of how good the rest of the output is.

### 3. Concept Definitions (`concept_definition.md`)

Defines domain-specific terms and business logic.

- **Why?**: To help the Judge understand the context. For example, what exactly qualifies as an "
  Active User" in your specific database schema?

### 4. Style & Formatting Guidelines (`style_guidelines.md`)

Defines expectations for the "look and feel" of the output.

- **Why?**: Checks for tone, markdown usage, or specific formatting requirements (e.g., "Always use
  snake_case for column aliases").

### 5. Additional Context (`additional_context.md`)

Any other relevant information that doesn't fit into the other categories, such as technical
constraints or user personas.

### 6. Golden Dataset (`golden_dataset.md`)

Provides examples of "perfect" inputs and outputs.

- **Why?**: LLMs perform much better at evaluation when they have "few-shot" examples of what
  success looks like.

## The Evaluation Workflow

1. **Execution**: The feature is run with the provided test case input.
2. **Static Tests**: The plugin's Python code runs programmatic checks on the output.
3. **LLM Evaluation**:
    - Vera gathers all the Spec files.
    - It constructs a comprehensive prompt for the Gemini Judge, including the specs, the test case
      input, and the actual feature output.
    - The Judge returns a structured evaluation (scores and reasoning) based on the specs.
4. **Reporting**: All results are aggregated into a single row in a CSV report.
