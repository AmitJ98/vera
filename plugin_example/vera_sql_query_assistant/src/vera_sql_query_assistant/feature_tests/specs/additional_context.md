# Additional Context: E-Commerce Schema & Business Rules

## Database Schema

The database consists of four related tables representing a standard e-commerce system.

### `customers`
Stores customer registration and profile information.
- `customer_id` (INTEGER, PRIMARY KEY): Unique ID.
- `first_name` (VARCHAR): First name.
- `last_name` (VARCHAR): Last name.
- `email` (VARCHAR): Unique email address.
- `country` (VARCHAR): User's country of residence.
- `created_at` (TIMESTAMP): Account creation date.

### `products`
Catalog of available items.
- `product_id` (INTEGER, PRIMARY KEY): Unique ID.
- `product_name` (VARCHAR): Name of the product.
- `category` (VARCHAR): Product category (e.g., 'Electronics', 'Books').
- `price` (DECIMAL): Unit price.
- `stock_quantity` (INTEGER): Current inventory count.

### `orders`
Transactional records of customer purchases.
- `order_id` (INTEGER, PRIMARY KEY): Unique ID.
- `customer_id` (INTEGER, FOREIGN KEY): Links to `customers`.
- `order_date` (TIMESTAMP): Date and time of order.
- `status` (VARCHAR): Order status ('PENDING', 'SHIPPED', 'DELIVERED', 'CANCELLED').
- `total_amount` (DECIMAL): Total value of the order (pre-calculated).

### `order_items`
Line items for each order.
- `item_id` (INTEGER, PRIMARY KEY): Unique ID.
- `order_id` (INTEGER, FOREIGN KEY): Links to `orders`.
- `product_id` (INTEGER, FOREIGN KEY): Links to `products`.
- `quantity` (INTEGER): Number of units purchased.
- `unit_price` (DECIMAL): Price per unit at the time of purchase.

## Business Rules & Logic

1.  **Revenue Calculation**:
    - Revenue is generally summed from `orders.total_amount` for completed orders.
    - If calculating from line items, it is `SUM(quantity * unit_price)`.
2.  **Order Status**:
    - Only 'SHIPPED' and 'DELIVERED' orders are considered "completed" sales for revenue reporting unless specified otherwise.
    - 'CANCELLED' orders should be excluded from revenue sums.
3.  **Time Logic**:
    - "Recent" usually implies the last 30 days unless a specific date range is given.
    - Fiscal year starts Jan 1st.
4.  **Customer Location**:
    - Analysis by location uses `customers.country`.
