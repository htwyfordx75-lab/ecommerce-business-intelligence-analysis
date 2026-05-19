import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# ============================================
# LOAD DATASETS
# ============================================

customers = pd.read_csv("data/olist_customers_dataset.csv")
orders = pd.read_csv("data/olist_orders_dataset.csv")
order_items = pd.read_csv("data/olist_order_items_dataset.csv")
payments = pd.read_csv("data/olist_order_payments_dataset.csv")
products = pd.read_csv("data/olist_products_dataset.csv")

# ============================================
# DATA CLEANING & FEATURE ENGINEERING
# ============================================

# Convert date columns to datetime
orders["order_purchase_timestamp"] = pd.to_datetime(
    orders["order_purchase_timestamp"]
)

orders["order_delivered_customer_date"] = pd.to_datetime(
    orders["order_delivered_customer_date"]
)

# Calculate delivery time in days
orders["delivery_days"] = (
    orders["order_delivered_customer_date"]
    - orders["order_purchase_timestamp"]
).dt.days

# Extract purchase month
orders["purchase_month"] = (
    orders["order_purchase_timestamp"]
    .dt.month
)

# ============================================
# SQLITE CONNECTION
# ============================================

conn = sqlite3.connect("ecommerce.db")

# ============================================
# SEND DATAFRAMES TO SQL
# ============================================

customers.to_sql("customers", conn, if_exists="replace", index=False)
orders.to_sql("orders", conn, if_exists="replace", index=False)
order_items.to_sql("order_items", conn, if_exists="replace", index=False)
payments.to_sql("payments", conn, if_exists="replace", index=False)
products.to_sql("products", conn, if_exists="replace", index=False)

# ============================================
# ANALYSIS 1 — TOP PRODUCT CATEGORIES BY REVENUE
# ============================================

query = """
SELECT
    products.product_category_name,
    SUM(order_items.price) AS revenue
FROM order_items

JOIN products
ON order_items.product_id = products.product_id

GROUP BY products.product_category_name
ORDER BY revenue DESC
LIMIT 10;
"""

result = pd.read_sql_query(query, conn)

print("\nTop Product Categories by Revenue")
print(result)

plt.figure(figsize=(12,6))

plt.bar(
    result["product_category_name"],
    result["revenue"]
)

plt.xlabel("Product Category")
plt.ylabel("Revenue")
plt.title("Top Product Categories by Revenue")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig("screenshots/top_product_categories.png")

plt.show()

# ============================================
# ANALYSIS 2 — TOP REVENUE GENERATING STATES
# ============================================

query = """
SELECT
    customers.customer_state,
    SUM(payments.payment_value) AS revenue
FROM customers

JOIN orders
ON customers.customer_id = orders.customer_id

JOIN payments
ON orders.order_id = payments.order_id

GROUP BY customers.customer_state
ORDER BY revenue DESC
LIMIT 10;
"""

result = pd.read_sql_query(query, conn)

print("\nTop Revenue Generating States")
print(result)

plt.figure(figsize=(12,6))

plt.bar(
    result["customer_state"],
    result["revenue"]
)

plt.xlabel("State")
plt.ylabel("Revenue")
plt.title("Top Revenue Generating States")

plt.tight_layout()

plt.savefig("screenshots/top_revenue_states.png")

plt.show()

# ============================================
# ANALYSIS 3 — DELIVERY PERFORMANCE BY STATE
# ============================================

query = """
SELECT
    customers.customer_state,
    AVG(orders.delivery_days) AS avg_delivery_days
FROM customers

JOIN orders
ON customers.customer_id = orders.customer_id

WHERE orders.delivery_days IS NOT NULL

GROUP BY customers.customer_state
ORDER BY avg_delivery_days DESC
LIMIT 10;
"""

result = pd.read_sql_query(query, conn)

print("\nStates With Longest Delivery Times")
print(result)

plt.figure(figsize=(12,6))

plt.bar(
    result["customer_state"],
    result["avg_delivery_days"]
)

plt.xlabel("State")
plt.ylabel("Average Delivery Days")
plt.title("States With Longest Delivery Times")

plt.tight_layout()

plt.savefig("screenshots/delivery_days_by_state.png")

plt.show()

# ============================================
# ANALYSIS 4 — REVENUE BY PAYMENT METHOD
# ============================================

query = """
SELECT
    payment_type,
    SUM(payment_value) AS revenue
FROM payments

GROUP BY payment_type
ORDER BY revenue DESC;
"""

result = pd.read_sql_query(query, conn)

print("\nRevenue by Payment Method")
print(result)

plt.figure(figsize=(10,6))

plt.bar(
    result["payment_type"],
    result["revenue"]
)

plt.xlabel("Payment Type")
plt.ylabel("Revenue")
plt.title("Revenue by Payment Method")

plt.tight_layout()

plt.savefig("screenshots/revenue_by_payment_method.png")

plt.show()

# ============================================
# ANALYSIS 5 — MONTHLY REVENUE TREND
# ============================================

query = """
SELECT
    purchase_month,
    SUM(payments.payment_value) AS revenue
FROM orders

JOIN payments
ON orders.order_id = payments.order_id

GROUP BY purchase_month
ORDER BY purchase_month;
"""

result = pd.read_sql_query(query, conn)

print("\nMonthly Revenue Trend")
print(result)

plt.figure(figsize=(12,6))

plt.plot(
    result["purchase_month"],
    result["revenue"],
    marker="o"
)

plt.xlabel("Month")
plt.ylabel("Revenue")
plt.title("Monthly Revenue Trend")

plt.xticks(result["purchase_month"])

plt.tight_layout()

plt.savefig("screenshots/monthly_revenue_trend.png")

plt.show()

# ============================================
# ANALYSIS 6 — ORDERS PER MONTH
# ============================================

query = """
SELECT
    purchase_month,
    COUNT(order_id) AS total_orders
FROM orders

GROUP BY purchase_month
ORDER BY purchase_month;
"""

result = pd.read_sql_query(query, conn)

print("\nOrders Per Month")
print(result)

plt.figure(figsize=(12,6))

plt.bar(
    result["purchase_month"],
    result["total_orders"]
)

plt.xlabel("Month")
plt.ylabel("Number of Orders")
plt.title("Orders Per Month")

plt.xticks(result["purchase_month"])

plt.tight_layout()

plt.savefig("screenshots/orders_per_month.png")

plt.show()

# ============================================
# CLOSE CONNECTION
# ============================================

conn.close()