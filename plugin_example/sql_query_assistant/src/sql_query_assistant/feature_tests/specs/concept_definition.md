# Concept Definition: SQL Query Assistant

## Feature Overview

The **SQL Query Assistant** is a GenAI-powered feature designed to translate natural language
questions from non-technical users into syntactically correct and semantically accurate SQL queries.

## Core Capabilities

1. **Natural Language Understanding**: Interpret user intent (e.g., "Show me top-selling items") in
   the context of the specific database schema.
2. **Schema Awareness**: Utilize table and column metadata to construct valid joins and filters.
3. **Safety & Compliance**: Adhere to read-only constraints and avoid restricted operations.
4. **Error Handling**: Gracefully handle ambiguous requests by asking for clarification (simulated)
   or returning a relevant error message/fallback.

## Target Audience

- Data Analysts looking for quick query drafts.
- Business Users (PMs, Marketing) needing direct data access without SQL knowledge.
