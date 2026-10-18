# Dashboard - QRIS Fraud Analytics (Looker Studio)

Live report: [QRIS Fraud Analytics](https://datastudio.google.com/reporting/a1e01ca3-4d6d-466e-b8d4-f32954e4b872/page/PvWAG)

Data source: BigQuery dataset `qris_analytics` (tables built by dbt). Looker
Studio reads the tables live, so refreshing = re-run the pipeline + `dbt run`.

## Tiles and design

| Tile | Question it answers | Backing mart | Why it is shaped that way |
|---|---|---|---|
| Daily fraud by type | Which fraud types spike on which days? | `mart_fraud_flags` | Partitioned by day (tiles filter date range), clustered by `fraud_type` (every view breaks down by type) |
| Top merchants by volume (leak watch) | Which merchants leak the most volume? | `mart_merchant_volume` | Partitioned by day, clustered by `merchant_id` (ranked bars per merchant) |
| High risk users | Which users need manual review first? | `mart_user_risk` | Per-user snapshot (not a time series), so clustered by `user_id` and intentionally not partitioned |

## Verified numbers

Checked against BigQuery directly (same numbers the tiles show):

- Payday spike (Sep 25): 631 flagged rows that day, split velocity 171,
  new_device 162, round_amount 159, night 139.
- Top merchants by volume: M009 203,126,627 / M000 199,946,822 /
  M018 195,552,471.
- High risk users: 39 with score >= 8 (7 at score 10, 6 at score 9, 26 at
  score 8), out of 1,615 scored users.

## Refreshing the dashboard

```powershell
python pipeline/run_pipeline.py                     # regenerate silver + marts (seed=42)
python pipeline/load_to_bq.py                       # silver -> BigQuery (needs GCP creds)
dbt run  --project-dir qris_analytics --profiles-dir "$env:USERPROFILE\.dbt"
```

One cosmetic note, recorded honestly: on exact score ties the dashboard's
user ordering is not alphabetical. The rows and totals are identical; only
the tie-break order differs.
