# Project 5 — Customer Churn & Retention Analytics (Advanced)

**Dataset:** Kaggle "Customer Churn Prediction Dataset" → save as `data/raw/churn_dataset.csv`
**Run:** edit the `CONFIG` cell in `churn_retention_analysis.ipynb` (column names), then run all cells.

## Segmentation rules (documented business logic)
| Segment | Rule |
|---|---|
| Churned | churn flag = 1 **or** inactive > 90 days |
| At Risk | not churned and inactive 31–90 days (if no recency column: model risk score ≥ 0.5) |
| Active | inactive ≤ 30 days |

## Outputs
`powerbi/customers_segmented.csv` (customer-level, incl. tenure/frequency/inactivity bands and risk score),
`churn_by_factor.csv`, `feature_importance.csv`, `segment_summary.csv`, charts in `outputs/`.

## Findings · Retention strategy
_Fill from `outputs/insights.md`: churn rate, highest-risk groups, top drivers, At-Risk count → targeted actions._

## Dashboard screenshot
`![dashboard](outputs/dashboard.png)`
