# Golden Dataset (Few-Shot Examples)

These examples represent high-quality Question-to-SQL pairs that the model should aspire to emulate.

## Example 1: Basic Selection
**Question**: "List all customers from France."
**SQL**:
```sql
SELECT *
FROM customers
WHERE country = 'France';
```

## Example 2: Aggregation
**Question**: "How many orders were placed in 2023?"
**SQL**:
```sql
SELECT COUNT(*)
FROM orders
WHERE order_date >= '2023-01-01' AND order_date <= '2023-12-31';
```

## Example 3: Join & Filtering
**Question**: "Show me the names of products that have been ordered at least once."
**SQL**:
```sql
SELECT DISTINCT p.product_name
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id;
```

## Example 4: Complex Multi-Table Join
**Question**: "What is the total revenue generated from customers in Germany?"
**SQL**:
```sql
SELECT SUM(o.total_amount)
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE c.country = 'Germany'
  AND o.status IN ('SHIPPED', 'DELIVERED');
```

## Example 5: Grouping & Ordering
**Question**: "Who are the top 5 customers by total spending?"
**SQL**:
```sql
SELECT c.first_name, c.last_name, SUM(o.total_amount) as total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.status NOT IN ('CANCELLED')
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_spent DESC
LIMIT 5;
```
