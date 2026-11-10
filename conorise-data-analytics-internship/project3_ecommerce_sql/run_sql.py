"""Load the raw e-commerce CSV into SQLite, run every sql/*.sql file in order, and
export each named SELECT as a CSV for Power BI / Excel.

Usage:  python run_sql.py
SQL files use markers:   -- name: <output_name>
Statements after a marker are exported to powerbi/<output_name>.csv if they are a SELECT;
otherwise they are simply executed (CREATE TABLE ... etc.).
"""
from pathlib import Path
import re
import sqlite3
import pandas as pd

HERE = Path(__file__).parent
RAW = HERE / "data/raw/ecommerce_dataset.csv"
if not RAW.exists():
    RAW = HERE / "data/sample/ecommerce_sample.csv"
    print("⚠️  Real dataset not found – using SYNTHETIC sample. Results are not for submission.")

# --- Map YOUR Kaggle column names to the names the SQL expects --------------------------
# left = column in your CSV, right = column name used in sql/*.sql.  Edit the left side.
COLUMN_MAP = {
    "order_id": "order_id", "order_date": "order_date", "customer_id": "customer_id",
    "product_id": "product_id", "product_name": "product_name", "category": "category",
    "region": "region", "quantity": "quantity", "unit_price": "unit_price",
    "discount_pct": "discount_pct",   # fraction 0-1; create it as 0 if the dataset has none
    "unit_cost": "unit_cost",         # cost per unit; if missing, see README "No cost column?"
}

PBI = HERE / "powerbi"; PBI.mkdir(exist_ok=True)
con = sqlite3.connect(HERE / "outputs/ecommerce.db")
df = pd.read_csv(RAW).rename(columns={k: v for k, v in COLUMN_MAP.items() if k in pd.read_csv(RAW, nrows=0).columns})
df.to_sql("orders_raw", con, if_exists="replace", index=False)
print(f"Loaded {len(df):,} rows into orders_raw")

for sql_file in sorted((HERE / "sql").glob("*.sql")):
    print(f"\n▶ {sql_file.name}")
    blocks = re.split(r"^-- name:\s*(\S+)\s*$", sql_file.read_text(encoding="utf-8"), flags=re.M)
    # blocks = [preamble, name1, sql1, name2, sql2, ...]
    if blocks[0].strip():
        con.executescript(blocks[0])
    for name, sql in zip(blocks[1::2], blocks[2::2]):
        sql = sql.strip()
        if not sql:
            continue
        body = "\n".join(l for l in sql.splitlines() if not l.strip().startswith("--")).strip().upper()
        if body.startswith(("SELECT", "WITH")):
            out = pd.read_sql_query(sql.rstrip(";"), con)
            out.to_csv(PBI / f"{name}.csv", index=False)
            print(f"   {name}.csv  ({len(out)} rows)")
        else:
            con.executescript(sql)
            print(f"   executed {name}")
con.commit(); con.close()
print("\nDone. CSVs for Power BI are in powerbi/")
