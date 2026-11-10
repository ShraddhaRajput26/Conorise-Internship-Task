-- 05_profitability.sql : high-revenue / low-profit products and what drives them
-- name: product_profitability
WITH p AS (
  SELECT product_id, product_name, category,
         SUM(revenue) AS revenue, SUM(profit) AS profit, SUM(quantity) AS units,
         ROUND(AVG(discount_pct) * 100, 1) AS avg_discount_pct,
         ROUND(100.0 * SUM(profit) / SUM(revenue), 2) AS margin_pct,
         ROUND(100.0 * SUM(CASE WHEN discount_pct >= 0.2 THEN 1 ELSE 0 END) / COUNT(*), 1) AS heavy_discount_line_pct
  FROM orders_clean GROUP BY product_id, product_name, category)
SELECT *,
       CASE WHEN revenue >= (SELECT AVG(revenue) FROM p)
             AND margin_pct < (SELECT 100.0 * SUM(profit) / SUM(revenue) FROM p) * 0.5
            THEN 'High revenue / low profit' ELSE 'OK' END AS flag
FROM p ORDER BY revenue DESC;

-- name: discount_vs_margin
SELECT CASE WHEN discount_pct = 0 THEN '0%' WHEN discount_pct <= 0.1 THEN '1-10%'
            WHEN discount_pct <= 0.2 THEN '11-20%' ELSE '>20%' END AS discount_band,
       COUNT(*) AS order_lines, ROUND(SUM(revenue), 2) AS revenue,
       ROUND(100.0 * SUM(profit) / SUM(revenue), 2) AS margin_pct
FROM orders_clean GROUP BY discount_band ORDER BY MIN(discount_pct);

-- name: loss_making_lines_by_category
SELECT category, COUNT(*) AS loss_lines, ROUND(SUM(profit), 2) AS total_loss
FROM orders_clean WHERE profit < 0 GROUP BY category ORDER BY total_loss;
