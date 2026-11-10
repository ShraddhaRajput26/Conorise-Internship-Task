-- 06_analytical_dataset.sql : the fact table you load into Power BI
-- name: fact_orders
SELECT o.*,
       c.customer_type,
       c.first_order,
       CASE WHEN o.order_date = c.first_order THEN 'New' ELSE 'Returning' END AS new_or_returning
FROM orders_clean o
JOIN (SELECT customer_id,
             MIN(order_date) AS first_order,
             CASE WHEN COUNT(DISTINCT order_id) > 1 THEN 'Repeat' ELSE 'One-time' END AS customer_type
      FROM orders_clean GROUP BY customer_id) c USING (customer_id);
