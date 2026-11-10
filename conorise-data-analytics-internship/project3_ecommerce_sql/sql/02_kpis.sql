-- 02_kpis.sql : headline KPIs
-- name: kpi_summary
SELECT
  ROUND(SUM(revenue), 2)                        AS total_revenue,
  ROUND(SUM(profit), 2)                         AS total_profit,
  ROUND(100.0 * SUM(profit) / SUM(revenue), 2)  AS profit_margin_pct,
  COUNT(DISTINCT order_id)                      AS total_orders,
  COUNT(DISTINCT customer_id)                   AS total_customers,
  SUM(quantity)                                 AS units_sold,
  ROUND(SUM(revenue) / COUNT(DISTINCT order_id), 2) AS avg_order_value,
  ROUND(1.0 * COUNT(DISTINCT order_id) / COUNT(DISTINCT customer_id), 2) AS orders_per_customer
FROM orders_clean;
