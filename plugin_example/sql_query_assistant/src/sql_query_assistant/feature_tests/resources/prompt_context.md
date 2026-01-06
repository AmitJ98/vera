# Database Schema

The database consists of the following tables:

## `customers`

- `customer_id` (INTEGER, PRIMARY KEY)
- `first_name` (VARCHAR)
- `last_name` (VARCHAR)
- `email` (VARCHAR)
- `country` (VARCHAR)
- `created_at` (TIMESTAMP)

## `products`

- `product_id` (INTEGER, PRIMARY KEY)
- `product_name` (VARCHAR)
- `category` (VARCHAR)
- `price` (DECIMAL)
- `stock_quantity` (INTEGER)

## `orders`

- `order_id` (INTEGER, PRIMARY KEY)
- `customer_id` (INTEGER, FOREIGN KEY -> customers.customer_id)
- `order_date` (TIMESTAMP)
- `status` (VARCHAR) -- 'PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED'
- `total_amount` (DECIMAL)

## `order_items`

- `item_id` (INTEGER, PRIMARY KEY)
- `order_id` (INTEGER, FOREIGN KEY -> orders.order_id)
- `product_id` (INTEGER, FOREIGN KEY -> products.product_id)
- `quantity` (INTEGER)
- `unit_price` (DECIMAL)

# Business Rules

1. Revenue = sum of `total_amount` or `quantity * unit_price`.
2. Completed orders are 'SHIPPED' or 'DELIVERED'.
3. Recent means last 30 days unless specified.

# Safety Restrictions

- Read-only access (**SELECT** only).
- No **DROP**, **DELETE**, **UPDATE**, **INSERT**.
- No system table access.