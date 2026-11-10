# Conorise Infotech — Data Analytics Internship Projects

**Author:** _Your Name_ · **LinkedIn:** _link_ · **Period:** Nov 2026

| # | Project | Level | Tools | Folder |
|---|---------|-------|-------|--------|
| 1 | Retail Sales Analysis | Beginner | Python/Excel, Power BI | [`project1_retail_sales`](project1_retail_sales) |
| 3 | E-Commerce Customer & Sales Analytics | Intermediate | SQL, Power BI | [`project3_ecommerce_sql`](project3_ecommerce_sql) |
| 5 | Customer Churn & Retention Analytics | Advanced | Python, Power BI | [`project5_churn_retention`](project5_churn_retention) |

Each project contains: data cleaning → KPIs → analysis → visualisations → insights → recommendations,
plus export files ready to load into Power BI.

## Quick start
```bash
pip install -r requirements.txt
python tools/make_sample_data.py          # optional: synthetic data to test the pipelines
# 1. download each Kaggle dataset into projectX/data/raw/ (file names in each project README)
# 2. run:
cd project1_retail_sales   && jupyter nbconvert --to notebook --execute --inplace retail_sales_analysis.ipynb
cd ../project3_ecommerce_sql && python run_sql.py
cd ../project5_churn_retention && jupyter nbconvert --to notebook --execute --inplace churn_retention_analysis.ipynb
```
> Without a file in `data/raw/`, every pipeline silently falls back to **synthetic** sample data and prints a warning.
> Never publish insights produced from the sample data.

See [`docs/`](docs) for the Power BI build guide, LinkedIn post and video script templates, and the submission checklist.
