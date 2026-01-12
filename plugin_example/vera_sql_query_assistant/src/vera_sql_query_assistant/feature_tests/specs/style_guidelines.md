# Style Guidelines

Generated SQL should follow these stylistic conventions for readability and maintainability.

## 1. Case
- **Keywords**: Use UPPERCASE for all SQL keywords (e.g., `SELECT`, `FROM`, `WHERE`, `AS`).
- **Identifiers**: Use `snake_case` for table and column names (as defined in schema).

## 2. Formatting
- Place the first keyword of each clause on a new line.
- Indent subsequent lines in a clause by 4 spaces.
- **Example**:
  ```sql
  SELECT
      product_name,
      price
  FROM products
  WHERE price > 100;
  ```

## 3. Aliasing
- Use short, meaningful aliases for tables in joins (e.g., `c` for `customers`, `o` for `orders`).
- Always qualify column names with table aliases when joining to avoid ambiguity.

## 4. Specificity
- Avoid `SELECT *` in production queries; listing specific columns is preferred unless the user asks for "all details".
