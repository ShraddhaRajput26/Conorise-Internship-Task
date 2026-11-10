# %% [markdown]
# # Project 5 — Customer Churn & Retention Analytics (Advanced)
# **Goal:** build customer-level metrics, segment customers (Active / At Risk / Churned) with explicit
# business rules, run EDA to find churn drivers, and export tables for a Power BI dashboard.
#
# Dataset: Kaggle *Customer Churn Prediction Dataset* → save as `data/raw/churn_dataset.csv`
# and edit the **CONFIG** cell so the names match your file's columns.

# %%
from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, classification_report

sns.set_theme(style="whitegrid")
RAW = Path("data/raw/churn_dataset.csv")
if not RAW.exists():
    RAW = Path("data/sample/churn_sample.csv")
    print("⚠️  Real dataset not found – using SYNTHETIC sample. Results are not for submission.")
OUT, PBI = Path("outputs"), Path("powerbi")
OUT.mkdir(exist_ok=True); PBI.mkdir(exist_ok=True)

# %% [markdown]
# ## CONFIG — edit to match your dataset (names AFTER snake_case conversion)

# %%
CONFIG = {
    "id": "customer_id",
    "churn": "churn",                          # label column (Yes/No, 1/0, True/False)
    "tenure": "tenure_months",                 # months as a customer
    "frequency": "purchase_frequency",         # purchases/orders/logins per period (None if absent)
    "inactivity_days": "days_since_last_activity",  # None if the data has no recency field
}
# Business rules for segmentation (document these in the README!)
ACTIVE_MAX_DAYS = 30      # active   : inactive <= 30 days
CHURN_MIN_DAYS = 90       # churned  : churn flag = 1 OR inactive > 90 days
# At Risk = everyone in between (31–90 days inactive) – if no recency field, see cell 5 fallback.

# %% [markdown]
# ## 1. Load & clean

# %%
snake = lambda c: re.sub(r"[^a-z0-9]+", "_", c.strip().lower()).strip("_")
df = pd.read_csv(RAW)
df.columns = [snake(c) for c in df.columns]
log = {"rows_raw": len(df)}

df = df.drop_duplicates(subset=CONFIG["id"])
log["duplicate_ids_removed"] = log["rows_raw"] - len(df)

# churn label → 0/1
df["churn_flag"] = (df[CONFIG["churn"]].astype(str).str.strip().str.lower()
                    .map({"yes": 1, "1": 1, "true": 1, "no": 0, "0": 0, "false": 0}))
df = df.dropna(subset=["churn_flag"]); df["churn_flag"] = df["churn_flag"].astype(int)

# numeric: median-fill, categorical: mode-fill
num_cols = df.select_dtypes("number").columns.drop("churn_flag")
cat_cols = [c for c in df.select_dtypes("object").columns if c not in (CONFIG["id"], CONFIG["churn"])]
log["missing_numeric_filled"] = int(df[num_cols].isna().sum().sum())
df[num_cols] = df[num_cols].fillna(df[num_cols].median())
for c in cat_cols:
    df[c] = df[c].fillna(df[c].mode().iloc[0]).astype(str).str.strip()
log["rows_clean"] = len(df)
pd.Series(log, name="cleaning_log").to_frame()

# %% [markdown]
# ## 2. Customer-level metrics
# tenure bands, frequency bands and inactivity period are derived here.

# %%
df["tenure_band"] = pd.cut(df[CONFIG["tenure"]], [-1, 6, 12, 24, 48, 1000],
                           labels=["0-6m", "7-12m", "13-24m", "25-48m", "48m+"])
if CONFIG["frequency"]:
    df["frequency_band"] = pd.qcut(df[CONFIG["frequency"]], 4, duplicates="drop").astype(str)
if CONFIG["inactivity_days"]:
    df["inactivity_band"] = pd.cut(df[CONFIG["inactivity_days"]], [-1, 30, 60, 90, 10000],
                                   labels=["0-30d", "31-60d", "61-90d", "90d+"])
overall = df.churn_flag.mean()
print(f"Overall churn rate: {overall:.1%}")

# %% [markdown]
# ## 3. Segment: Active / At Risk / Churned

# %%
def segment(row):
    if row.churn_flag == 1:
        return "Churned"
    if CONFIG["inactivity_days"]:
        d = row[CONFIG["inactivity_days"]]
        if d > CHURN_MIN_DAYS: return "Churned"
        if d > ACTIVE_MAX_DAYS: return "At Risk"
        return "Active"
    return "Active"          # fallback – refined by model risk below if no recency field

df["segment"] = df.apply(segment, axis=1)
if not CONFIG["inactivity_days"]:   # no recency field → flag high-probability non-churners as At Risk
    pass  # (filled after the model in cell 6)
seg = df.segment.value_counts().rename_axis("segment").to_frame("customers")
seg["share_pct"] = (seg.customers / seg.customers.sum() * 100).round(1)
seg

# %% [markdown]
# ## 4. EDA — what is associated with churn?

# %%
cats = [c for c in cat_cols if df[c].nunique() <= 12] + [c for c in ["tenure_band", "frequency_band", "inactivity_band"] if c in df]
rows = []
for c in cats:
    t = df.groupby(c, observed=True).churn_flag.agg(["mean", "count"]).reset_index()
    t.columns = ["value", "churn_rate", "customers"]; t.insert(0, "factor", c); rows.append(t)
churn_by_factor = pd.concat(rows); churn_by_factor["churn_rate"] = (churn_by_factor.churn_rate * 100).round(1)
churn_by_factor.sort_values("churn_rate", ascending=False).head(10)

# %%
n = min(len(cats), 6)
fig, axes = plt.subplots(2, 3, figsize=(16, 8)); axes = axes.ravel()
for ax, c in zip(axes, cats[:n]):
    r = df.groupby(c, observed=True).churn_flag.mean() * 100
    sns.barplot(x=r.index.astype(str), y=r.values, ax=ax, color="#4C78A8")
    ax.axhline(overall * 100, ls="--", c="red", lw=1); ax.set_title(f"Churn % by {c}"); ax.set_xlabel("")
    ax.tick_params(axis="x", rotation=20)
plt.tight_layout(); plt.savefig(OUT / "churn_by_factor.png", dpi=150); plt.show()

# %%
numeric_for_corr = df[list(num_cols) + ["churn_flag"]].corr()["churn_flag"].drop("churn_flag").sort_values()
numeric_for_corr.plot.barh(title="Correlation with churn", figsize=(7, 4)); plt.tight_layout()
plt.savefig(OUT / "churn_correlation.png", dpi=150); plt.show()

# %% [markdown]
# ## 5. Feature importance (Random Forest) — evidence for risk factors

# %%
X = pd.get_dummies(df[list(num_cols) + cat_cols], drop_first=True)
y = df.churn_flag
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
rf = RandomForestClassifier(n_estimators=300, random_state=42, class_weight="balanced", n_jobs=-1).fit(Xtr, ytr)
auc = roc_auc_score(yte, rf.predict_proba(Xte)[:, 1])
print(f"ROC-AUC on hold-out: {auc:.3f}")
print(classification_report(yte, rf.predict(Xte)))
imp = pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)
imp.sort_values().plot.barh(title="Top churn indicators", figsize=(7, 5)); plt.tight_layout()
plt.savefig(OUT / "feature_importance.png", dpi=150); plt.show()

# %%
df["churn_risk_score"] = rf.predict_proba(X)[:, 1].round(3)
if not CONFIG["inactivity_days"]:
    df.loc[(df.segment == "Active") & (df.churn_risk_score >= 0.5), "segment"] = "At Risk"

# %% [markdown]
# ## 6. Auto-generated insights (edit with your own words)

# %%
worst = churn_by_factor[churn_by_factor.customers >= 30].sort_values("churn_rate", ascending=False).iloc[0]
best = churn_by_factor[churn_by_factor.customers >= 30].sort_values("churn_rate").iloc[0]
seg = df.segment.value_counts(normalize=True).mul(100).round(1)
insights = [
    f"Overall churn rate is {overall:.1%}; model ROC-AUC {auc:.2f}.",
    f"Highest-churn group: **{worst.factor} = {worst.value}** at {worst.churn_rate}% ({int(worst.customers)} customers).",
    f"Lowest-churn group: **{best.factor} = {best.value}** at {best.churn_rate}%.",
    f"Top predictive features: {', '.join(imp.index[:3])}.",
    "Segments: " + ", ".join(f"{k} {v}%" for k, v in seg.items()) + ".",
]
(OUT / "insights.md").write_text("\n".join(f"- {i}" for i in insights), encoding="utf-8")
print("\n".join(insights))

# %% [markdown]
# ## 7. Export for Power BI

# %%
seg_summary = df.groupby("segment").agg(customers=(CONFIG["id"], "count"),
                                        avg_tenure=(CONFIG["tenure"], "mean"),
                                        avg_risk=("churn_risk_score", "mean")).round(2)
df.to_csv(PBI / "customers_segmented.csv", index=False)
churn_by_factor.to_csv(PBI / "churn_by_factor.csv", index=False)
imp.rename("importance").to_frame().to_csv(PBI / "feature_importance.csv")
seg_summary.to_csv(PBI / "segment_summary.csv")
seg_summary

# %% [markdown]
# ## 8. Retention recommendations (finding → evidence → action)
# 1. _e.g. Month-to-month customers churn at X % vs Y % on annual plans → offer a discount to switch to annual._
# 2. _At Risk segment = N customers; trigger a win-back email at 30 days inactive._
# 3. _Customers with ≥ 3 support tickets churn more → proactive outreach after the 2nd ticket._
