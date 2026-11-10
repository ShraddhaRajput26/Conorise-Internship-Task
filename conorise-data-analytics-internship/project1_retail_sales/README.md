# Project 1 — Retail Sales Analysis (Beginner)

**Dataset:** Kaggle "Retail Sales Dataset" → save as `data/raw/retail_sales_dataset.csv`
**Files:** `retail_sales_analysis.ipynb` (main), `.py` (same code, jupytext format)
**Outputs:** `outputs/retail_sales_analysis.xlsx` (KPI + pivot tables), `outputs/retail_overview.png`,
`powerbi/retail_clean.csv` (load into Power BI), `outputs/insights.md`

## Business problem
_One paragraph: what the retailer wants to know (what sells, when, to whom)._

## Approach
1. Cleaning: duplicates, types, missing age (median), total-amount validation — see the *Cleaning_Log* sheet.
2. KPIs: revenue, transactions, units, AOV, revenue per customer.
3. Analysis: category, gender, age group, month (MoM growth + unusual-month flag), top/bottom.
4. Dashboard: Power BI page built from `powerbi/retail_clean.csv` (see `docs/POWERBI_GUIDE.md`).

## Data limitations (state these honestly)
The Kaggle file has no cost/profit and no region/product-name columns. Profit KPIs are skipped unless you set
`ASSUMED_COGS_PCT` (an explicit assumption). "Products" = product categories. Region analysis is replaced by
gender/age-group analysis.

## Key insights
_Paste/extend `outputs/insights.md` (use real numbers)._

## Recommendations
1. …  2. …  3. …

## Dashboard screenshot
`![dashboard](outputs/dashboard.png)`
