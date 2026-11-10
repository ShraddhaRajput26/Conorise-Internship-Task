"""Generate SYNTHETIC sample data so every pipeline can be tested before you
drop in the real Kaggle files. Sample data is NOT for submission results.

Usage:  python tools/make_sample_data.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
rng = np.random.default_rng(42)


def retail():
    n = 1000
    dates = pd.to_datetime("2023-01-01") + pd.to_timedelta(rng.integers(0, 365, n), unit="D")
    cats = rng.choice(["Beauty", "Clothing", "Electronics"], n, p=[0.3, 0.35, 0.35])
    price = rng.choice([25, 30, 50, 300, 500], n)
    qty = rng.integers(1, 5, n)
    df = pd.DataFrame({
        "Transaction ID": np.arange(1, n + 1),
        "Date": dates.strftime("%Y-%m-%d"),
        "Customer ID": [f"CUST{i:03d}" for i in rng.integers(1, 300, n)],
        "Gender": rng.choice(["Male", "Female"], n),
        "Age": rng.integers(18, 65, n),
        "Product Category": cats,
        "Quantity": qty,
        "Price per Unit": price,
    })
    df["Total Amount"] = df["Quantity"] * df["Price per Unit"]
    # inject dirt so the cleaning step has work to do
    df.loc[rng.choice(n, 8, replace=False), "Age"] = np.nan
    df = pd.concat([df, df.sample(5, random_state=1)])
    df.to_csv(ROOT / "project1_retail_sales/data/sample/retail_sales_sample.csv", index=False)


def ecommerce():
    n = 6000
    products = pd.DataFrame({
        "product_id": [f"P{i:03d}" for i in range(1, 41)],
        "category": rng.choice(["Electronics", "Home", "Fashion", "Sports", "Toys"], 40),
        "unit_price": rng.integers(10, 400, 40),
    })
    products["unit_cost"] = (products.unit_price * rng.uniform(0.55, 0.9, 40)).round(2)
    products["product_name"] = "Product " + products.product_id
    idx = rng.integers(0, 40, n)
    p = products.iloc[idx].reset_index(drop=True)
    month_w = np.array([1, 1, 1.1, 1.1, 1.2, 1.2, 1.1, 1.2, 1.3, 1.5, 2.2, 2.0])
    month = rng.choice(np.arange(1, 13), n, p=month_w / month_w.sum())
    dates = pd.to_datetime("2023-01-01") + pd.to_timedelta((month - 1) * 30 + rng.integers(0, 28, n), unit="D")
    disc = rng.choice([0, 0.05, 0.1, 0.2, 0.3], n, p=[0.4, 0.2, 0.2, 0.12, 0.08])
    # make some products discount-heavy => high revenue / low profit
    heavy = p.product_id.isin(products.product_id[:5])
    disc = np.where(heavy, rng.choice([0.2, 0.3, 0.4], n), disc)
    df = pd.DataFrame({
        "order_id": [f"O{i:05d}" for i in range(1, n + 1)],
        "order_date": dates.strftime("%Y-%m-%d"),
        "customer_id": [f"C{i:04d}" for i in (rng.pareto(1.5, n) * 300).astype(int) % 1500 + 1],
        "product_id": p.product_id, "product_name": p.product_name, "category": p.category,
        "region": rng.choice(["North", "South", "East", "West"], n, p=[.3, .25, .2, .25]),
        "quantity": rng.integers(1, 5, n), "unit_price": p.unit_price,
        "discount_pct": disc, "unit_cost": p.unit_cost,
    })
    df.loc[rng.choice(n, 30, replace=False), "region"] = None
    df = pd.concat([df, df.sample(20, random_state=2)])
    df.to_csv(ROOT / "project3_ecommerce_sql/data/sample/ecommerce_sample.csv", index=False)


def churn():
    n = 3000
    tenure = rng.integers(1, 72, n)
    contract = rng.choice(["Month-to-month", "One year", "Two year"], n, p=[.55, .25, .2])
    tickets = rng.poisson(1.5, n)
    freq = rng.poisson(6, n)
    monthly = rng.normal(65, 25, n).clip(15, 150).round(2)
    inactive = rng.integers(0, 150, n)
    z = (-1.2 + 1.3 * (contract == "Month-to-month") - 0.03 * tenure + 0.25 * tickets
         + 0.008 * monthly + 0.012 * inactive - 0.08 * freq)
    churn = (rng.random(n) < 1 / (1 + np.exp(-z))).astype(int)
    df = pd.DataFrame({
        "customer_id": [f"CU{i:05d}" for i in range(1, n + 1)],
        "gender": rng.choice(["Male", "Female"], n), "contract": contract,
        "payment_method": rng.choice(["Card", "UPI", "Bank transfer", "Cash"], n),
        "tenure_months": tenure, "purchase_frequency": freq,
        "monthly_charges": monthly, "support_tickets": tickets,
        "days_since_last_activity": inactive, "churn": np.where(churn == 1, "Yes", "No"),
    })
    df.loc[rng.choice(n, 40, replace=False), "monthly_charges"] = np.nan
    df.to_csv(ROOT / "project5_churn_retention/data/sample/churn_sample.csv", index=False)


if __name__ == "__main__":
    retail(); ecommerce(); churn()
    print("Sample data written to each project's data/sample/ folder.")
