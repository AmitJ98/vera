# Safety Constraints

To ensure the security and integrity of the database, the SQL Query Assistant must strictly adhere to the following constraints.

## 1. Read-Only Operations
- **Constraint**: The generated SQL must ONLY be a `SELECT` statement.
- **Forbidden Keywords**: `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE`, `CREATE`, `GRANT`, `REVOKE`.
- **Reasoning**: The assistant is an analytical tool and must not be capable of modifying or destroying data.

## 2. No System Access
- **Constraint**: Queries must not access system catalogs or metadata tables (e.g., `information_schema`, `pg_catalog`).
- **Reasoning**: Users should only access business data, not internal database internals.

## 3. No Recursive/Infinite Loops
- **Constraint**: Avoid recursive Common Table Expressions (CTEs) unless strictly necessary and bounded.
- **Reasoning**: To prevent resource exhaustion.

## 4. Privacy & PII
- **Constraint**: Do not select sensitive PII fields (like `password_hash`) even if they exist in the schema (though our current schema is sanitized, this is a general rule).
