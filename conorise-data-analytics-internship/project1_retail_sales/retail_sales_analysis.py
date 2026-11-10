# %% [markdown]
# # Project 1 — Retail Sales Analysis (Beginner)
# **Goal:** clean transaction data, build KPIs, analyse sales by category / customer group / month,
# find top & under-performers, spot seasonal trends, and produce recommendations.
#
# Dataset: Kaggle *Retail Sales Dataset* → save as `data/raw/retail_sales_dataset.csv`.
# If that file is missing the notebook falls back to the synthetic sample in `data/sample/`.

# %%
from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid")
RAW = Path("data/raw/retail_sales_dataset.csv")
USING_SAMPLE = not RAW.exists()
if USING_SAMPLE:
    RAW = Path("data/sample/retail_sales_sample.csv")
    print("⚠️  Real dataset not found – using SYNTHETIC sample. Results are not for submission.")
OUT, PBI = Path("outputs"), Path("powerbi")
OUT.mkdir(exist_ok=True); PBI.mkdir(exist_ok=True)

# Optional: the Kaggle file has NO cost column. Set a clearly-stated assumption (e.g. 0.60 = COGS is
# 60 % of revenue) to get profit KPIs, or leave None to skip profit KPIs.
ASSUMED_COGS_PCT = None

# %% [markdown]
# ## 1. Load & inspect

# %%
df = pd.read_csv(RAW)
print(df.shape)
df.head()

# %%
df.info()

# %% [markdown]
# ## 2. Clean & validate
# Steps: standard column names → remove duplicates → fix data types → handle missing values →
# validate `total_amount = quantity × price_per_unit` → flag outliers.

# %%
def snake(c):
    return re.sub(r"[^a-z0-9]+", "_", c.strip().lower()).strip("_")

df.columns = [snake(c) for c in df.columns]
log = {"rows_raw": len(df)}

df = df.drop_duplicates()
log["duplicates_removed"] = log["rows_raw"] - len(df)

df["date"] = pd.to_datetime(df["date"], errors="coerce")
for c in ["quantity", "price_per_unit", "total_amount", "age"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
log["bad_dates_dropped"] = int(df["date"].isna().sum())
df = df.dropna(subset=["date", "quantity", "price_per_unit"])

log["missing_age_filled_with_median"] = int(df["age"].isna().sum())
df["age"] = df["age"].fillna(df["age"].median())

# recompute total and compare with the supplied one
calc = df["quantity"] * df["price_per_unit"]
log["total_mismatches_fixed"] = int((calc != df["total_amount"]).sum())
df["total_amount"] = calc

df = df[(df.quantity > 0) & (df.price_per_unit > 0)]
for c in ["gender", "product_category"]:
    df[c] = df[c].astype(str).str.strip().str.title()

df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
df["month_name"] = df["date"].dt.month_name()
df["weekday"] = df["date"].dt.day_name()
df["age_group"] = pd.cut(df["age"], [0, 25, 35, 45, 55, 120],
                         labels=["<=25", "26-35", "36-45", "46-55", "56+"])
if ASSUMED_COGS_PCT is not None:
    df["profit"] = df["total_amount"] * (1 - ASSUMED_COGS_PCT)

log["rows_clean"] = len(df)
pd.Series(log, name="cleaning_log").to_frame()

# %% [markdown]
# ## 3. Core KPIs

# %%
kpi = {
    "Total revenue": df.total_amount.sum(),
    "Total transactions": df["transaction_id"].nunique(),
    "Units sold": df.quantity.sum(),
    "Average order value (AOV)": df.total_amount.mean(),
    "Unique customers": df["customer_id"].nunique(),
    "Revenue per customer": df.total_amount.sum() / df["customer_id"].nunique(),
}
if "profit" in df:
    kpi["Assumed profit"] = df.profit.sum()
kpi_df = pd.Series(kpi, name="value").round(2).to_frame()
kpi_df

# %% [markdown]
# ## 4. Sales by category, customer group and month

# %%
by_cat = (df.groupby("product_category")
            .agg(revenue=("total_amount", "sum"), units=("quantity", "sum"),
                 orders=("transaction_id", "count"), aov=("total_amount", "mean"))
            .sort_values("revenue", ascending=False).round(2))
by_cat["revenue_share_pct"] = (by_cat.revenue / by_cat.revenue.sum() * 100).round(1)
by_cat

# %%
by_gender = df.groupby("gender").agg(revenue=("total_amount", "sum"), aov=("total_amount", "mean")).round(2)
by_age = df.groupby("age_group", observed=True).agg(revenue=("total_amount", "sum"), aov=("total_amount", "mean")).round(2)
cat_gender = df.pivot_table(index="product_category", columns="gender", values="total_amount", aggfunc="sum")
display_tables = (by_gender, by_age, cat_gender)
by_gender, by_age

# %%
monthly = (df.groupby("month").agg(revenue=("total_amount", "sum"), orders=("transaction_id", "count"),
                                   units=("quantity", "sum")).round(2))
monthly["mom_growth_pct"] = (monthly.revenue.pct_change() * 100).round(1)
z = (monthly.mom_growth_pct - monthly.mom_growth_pct.mean()) / monthly.mom_growth_pct.std()
monthly["unusual_move"] = z.abs() > 1.5      # flag months whose growth is > 1.5 std-devs from normal
monthly

# %% [markdown]
# ## 5. Top & under-performers
# The Kaggle file only has *category* (no product name), so categories are the "products" here.
# If your file has a `product_name` column, change `PRODUCT_COL` below.

# %%
PRODUCT_COL = "product_name" if "product_name" in df.columns else "product_category"
prod = df.groupby(PRODUCT_COL).agg(revenue=("total_amount", "sum"), units=("quantity", "sum")).sort_values("revenue", ascending=False)
top, bottom = prod.head(5), prod.tail(5)
top, bottom

# %% [markdown]
# ## 6. Visualisations

# %%
fig, ax = plt.subplots(2, 2, figsize=(14, 9))
monthly.revenue.plot(ax=ax[0, 0], marker="o", title="Monthly revenue")
sns.barplot(x=by_cat.index, y=by_cat.revenue, ax=ax[0, 1]).set(title="Revenue by category", xlabel="")
sns.barplot(x=by_age.index.astype(str), y=by_age.revenue, ax=ax[1, 0]).set(title="Revenue by age group", xlabel="")
sns.heatmap(cat_gender, annot=True, fmt=".0f", cmap="Blues", ax=ax[1, 1]); ax[1, 1].set_title("Category × gender revenue")
plt.tight_layout(); plt.savefig(OUT / "retail_overview.png", dpi=150); plt.show()

# %% [markdown]
# ## 7. Auto-generated insights (edit & extend these with your own words)

# %%
best_m, worst_m = monthly.revenue.idxmax(), monthly.revenue.idxmin()
insights = [
    f"Total revenue is {kpi['Total revenue']:,.0f} across {kpi['Total transactions']:,} transactions (AOV {kpi['Average order value (AOV)']:,.0f}).",
    f"Top category: **{by_cat.index[0]}** ({by_cat.revenue_share_pct.iloc[0]}% of revenue); weakest: **{by_cat.index[-1]}** ({by_cat.revenue_share_pct.iloc[-1]}%).",
    f"Peak month {best_m:%b %Y} ({monthly.revenue.max():,.0f}); lowest month {worst_m:%b %Y} ({monthly.revenue.min():,.0f}).",
    f"Highest-spending age group: **{by_age.revenue.idxmax()}**; highest-AOV gender: **{by_gender.aov.idxmax()}**.",
    f"Unusual monthly swings: {', '.join(monthly.index[monthly.unusual_move].strftime('%b %Y')) or 'none detected'}.",
]
(OUT / "insights.md").write_text("\n".join(f"- {i}" for i in insights), encoding="utf-8")
print("\n".join(insights))

# %% [markdown]
# ## 8. Export for Excel & Power BI

# %%
df.to_csv(PBI / "retail_clean.csv", index=False)
with pd.ExcelWriter(OUT / "retail_sales_analysis.xlsx") as xw:
    kpi_df.to_excel(xw, "KPIs")
    by_cat.to_excel(xw, "By_Category")
    by_gender.to_excel(xw, "By_Gender")
    by_age.to_excel(xw, "By_AgeGroup")
    cat_gender.to_excel(xw, "Category_x_Gender")
    monthly.to_excel(xw, "Monthly_Trend")
    top.to_excel(xw, "Top_Products")
    bottom.to_excel(xw, "Bottom_Products")
    pd.Series(log, name="value").to_frame().to_excel(xw, "Cleaning_Log")
print("Saved outputs/ and powerbi/retail_clean.csv")

# %% [markdown]
# ## 9. Recommendations (write 3–5 in *finding → impact → action* format)
# 1. _e.g. Category X drives N % of revenue but falls in Q3 → protect it → run a Q3 bundle promotion._
# 2. …
# 3. …
