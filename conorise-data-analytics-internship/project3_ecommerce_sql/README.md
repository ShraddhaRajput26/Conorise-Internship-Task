# Project 3 — E-Commerce Customer & Sales Analytics (Intermediate)

**Dataset:** Kaggle "E-Commerce Dataset" → save as `data/raw/ecommerce_dataset.csv`
**Run:** edit `COLUMN_MAP` in `run_sql.py` to match your CSV's columns, then `python run_sql.py`.
(Uses SQLite — no server needed. The SQL is standard and ports to MySQL/Postgres with minor date-function changes.)

| SQL file | Purpose |
|---|---|
| `01_clean.sql` | dedupe, trim, type-cast, drop invalid rows, derive revenue/cost/profit |
| `02_kpis.sql` | revenue, profit, margin, orders, customers, AOV |
| `03_performance.sql` | by category, region, month (MoM with `LAG`), top products |
| `04_customers.sql` | customer metrics, new vs repeat, frequency bands, repeat rate |
| `05_profitability.sql` | high-revenue/low-profit flag, discount vs margin, loss lines |
| `06_analytical_dataset.sql` | `fact_orders` — the table you load in Power BI |

Every query marked `-- name: x` is exported to `powerbi/x.csv`.

## No cost column?
If your dataset has no cost, either (a) join a cost proxy, or (b) set `unit_cost = unit_price * 0.7` in `COLUMN_MAP`
preprocessing **and state it as an assumption**. If it has no discount, add `discount_pct = 0`.

## Business problem · Findings · Recommendations
_Fill in from `powerbi/*.csv`:_ which products earn revenue but little profit and why (discount depth?),
new vs repeat revenue mix, seasonality, regional gaps → 3–5 actions.

## Dashboard screenshot
`![dashboard](outputs/dashboard.png)`
