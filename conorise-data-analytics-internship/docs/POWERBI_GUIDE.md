# Power BI build guide (Power BI Desktop, Windows; or app.powerbi.com for web)

Get Data → Text/CSV → load the CSV(s) from each project's `powerbi/` folder → Transform Data (check types) → Close & Apply.
Save as `projectX/dashboard/<name>.pbix` and export a PNG/PDF screenshot to `outputs/dashboard.png`.

## Project 1 — table `retail_clean`
```DAX
Total Revenue = SUM(retail_clean[total_amount])
Transactions  = DISTINCTCOUNT(retail_clean[transaction_id])
Units Sold    = SUM(retail_clean[quantity])
AOV           = DIVIDE([Total Revenue],[Transactions])
Revenue LM    = CALCULATE([Total Revenue], DATEADD(retail_clean[date], -1, MONTH))
MoM %         = DIVIDE([Total Revenue]-[Revenue LM],[Revenue LM])
```
Layout: 4 KPI cards · line (month × revenue) · bar (category) · column (age group) · slicers: category, gender, month.

## Project 3 — load `fact_orders`
```DAX
Revenue = SUM(fact_orders[revenue])
Profit  = SUM(fact_orders[profit])
Margin %= DIVIDE([Profit],[Revenue])
Orders  = DISTINCTCOUNT(fact_orders[order_id])
Customers = DISTINCTCOUNT(fact_orders[customer_id])
AOV = DIVIDE([Revenue],[Orders])
Repeat Customers % = DIVIDE(CALCULATE(DISTINCTCOUNT(fact_orders[customer_id]), fact_orders[customer_type]="Repeat"),[Customers])
```
Pages: (1) Overview KPIs + monthly trend + region map/bar; (2) Products — scatter Revenue vs Margin % (size = units) to expose
high-revenue/low-profit items, bar of discount band vs margin; (3) Customers — new vs returning revenue, frequency bands.

## Project 5 — load `customers_segmented`, `churn_by_factor`, `feature_importance`
```DAX
Customers  = COUNTROWS(customers_segmented)
Churn Rate = DIVIDE(CALCULATE(COUNTROWS(customers_segmented), customers_segmented[churn_flag]=1),[Customers])
At Risk    = CALCULATE([Customers], customers_segmented[segment]="At Risk")
Avg Risk Score = AVERAGE(customers_segmented[churn_risk_score])
```
Pages: KPI cards + segment donut · churn % by contract/tenure band (clustered bars) · feature importance bar · table of top-risk customers (filter risk score ≥ 0.7).

## Dashboard checklist
Title · consistent colours · max ~6 visuals/page · every chart titled · slicers work · tooltip/drill-down enabled.
