-- 01_clean.sql : build a clean, validated order-line table from orders_raw
-- name: build_orders_clean
DROP TABLE IF EXISTS orders_clean;
CREATE TABLE orders_clean AS
SELECT DISTINCT
    TRIM(order_id)                                   AS order_id,
    DATE(order_date)                                 AS order_date,
    strftime('%Y-%m', order_date)                    AS order_month,
    TRIM(customer_id)                                AS customer_id,
    TRIM(product_id)                                 AS product_id,
    TRIM(product_name)                               AS product_name,
    COALESCE(NULLIF(TRIM(category), ''), 'Unknown')  AS category,
    COALESCE(NULLIF(TRIM(region), ''), 'Unknown')    AS region,
    CAST(quantity AS INTEGER)                        AS quantity,
    CAST(unit_price AS REAL)                         AS unit_price,
    COALESCE(CAST(discount_pct AS REAL), 0)          AS discount_pct,
    CAST(unit_cost AS REAL)                          AS unit_cost,
    -- derived money columns
    ROUND(quantity * unit_price * (1 - COALESCE(discount_pct, 0)), 2)      AS revenue,
    ROUND(quantity * unit_cost, 2)                                          AS cost,
    ROUND(quantity * unit_price * (1 - COALESCE(discount_pct, 0))
          - quantity * unit_cost, 2)                                        AS profit
FROM orders_raw
WHERE order_id IS NOT NULL
  AND customer_id IS NOT NULL
  AND DATE(order_date) IS NOT NULL
  AND quantity > 0
  AND unit_price > 0;

-- name: data_quality_report
SELECT
  (SELECT COUNT(*) FROM orders_raw)                                  AS raw_rows,
  (SELECT COUNT(*) FROM orders_clean)                                AS clean_rows,
  (SELECT COUNT(*) FROM orders_raw WHERE region IS NULL OR TRIM(region) = '') AS missing_region_rows,
  (SELECT COUNT(*) FROM orders_clean WHERE profit < 0)               AS loss_making_lines;
