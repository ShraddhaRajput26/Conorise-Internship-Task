-- 03_performance.sql : by product, category, region, time
-- name: revenue_by_category
SELECT category,
       ROUND(SUM(revenue), 2) AS revenue, ROUND(SUM(profit), 2) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 2) AS margin_pct,
       COUNT(DISTINCT order_id) AS orders
FROM orders_clean GROUP BY category ORDER BY revenue DESC;

-- name: revenue_by_region
SELECT region,
       ROUND(SUM(revenue), 2) AS revenue, ROUND(SUM(profit), 2) AS profit,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 2) AS margin_pct,
       COUNT(DISTINCT order_id) AS orders
FROM orders_clean GROUP BY region ORDER BY revenue DESC;

-- name: monthly_trend
WITH m AS (
  SELECT order_month, SUM(revenue) AS revenue, SUM(profit) AS profit,
         COUNT(DISTINCT order_id) AS orders
  FROM orders_clean GROUP BY order_month)
SELECT order_month, ROUND(revenue, 2) AS revenue, ROUND(profit, 2) AS profit, orders,
       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY order_month))
             / LAG(revenue) OVER (ORDER BY order_month), 1) AS revenue_mom_pct
FROM m ORDER BY order_month;

-- name: top_products
SELECT product_id, product_name, category,
       ROUND(SUM(revenue), 2) AS revenue, ROUND(SUM(profit), 2) AS profit,
       SUM(quantity) AS units,
       RANK() OVER (ORDER BY SUM(revenue) DESC) AS revenue_rank
FROM orders_clean GROUP BY product_id, product_name, category
ORDER BY revenue DESC LIMIT 20;
