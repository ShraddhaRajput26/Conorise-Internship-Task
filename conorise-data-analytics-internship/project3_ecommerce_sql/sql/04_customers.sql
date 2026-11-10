-- 04_customers.sql : customer-level metrics, new vs repeat, purchase frequency
-- name: customer_metrics
SELECT customer_id,
       COUNT(DISTINCT order_id)             AS orders,
       ROUND(SUM(revenue), 2)               AS lifetime_revenue,
       ROUND(SUM(profit), 2)                AS lifetime_profit,
       ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
       MIN(order_date)                      AS first_order,
       MAX(order_date)                      AS last_order,
       CASE WHEN COUNT(DISTINCT order_id) > 1 THEN 'Repeat' ELSE 'One-time' END AS customer_type
FROM orders_clean GROUP BY customer_id;

-- name: new_vs_repeat_by_month
WITH firsts AS (SELECT customer_id, MIN(order_month) AS first_month FROM orders_clean GROUP BY customer_id)
SELECT o.order_month,
       COUNT(DISTINCT CASE WHEN o.order_month = f.first_month THEN o.customer_id END) AS new_customers,
       COUNT(DISTINCT CASE WHEN o.order_month > f.first_month THEN o.customer_id END) AS returning_customers,
       ROUND(SUM(CASE WHEN o.order_month = f.first_month THEN o.revenue ELSE 0 END), 2) AS new_customer_revenue,
       ROUND(SUM(CASE WHEN o.order_month > f.first_month THEN o.revenue ELSE 0 END), 2) AS returning_revenue
FROM orders_clean o JOIN firsts f USING (customer_id)
GROUP BY o.order_month ORDER BY o.order_month;

-- name: purchase_frequency_distribution
WITH c AS (SELECT customer_id, COUNT(DISTINCT order_id) AS orders FROM orders_clean GROUP BY customer_id)
SELECT CASE WHEN orders = 1 THEN '1 order' WHEN orders = 2 THEN '2 orders'
            WHEN orders BETWEEN 3 AND 4 THEN '3-4 orders' ELSE '5+ orders' END AS frequency_band,
       COUNT(*) AS customers
FROM c GROUP BY frequency_band ORDER BY MIN(orders);

-- name: repeat_rate
SELECT ROUND(100.0 * SUM(CASE WHEN n > 1 THEN 1 ELSE 0 END) / COUNT(*), 2) AS repeat_customer_pct
FROM (SELECT customer_id, COUNT(DISTINCT order_id) AS n FROM orders_clean GROUP BY customer_id);
