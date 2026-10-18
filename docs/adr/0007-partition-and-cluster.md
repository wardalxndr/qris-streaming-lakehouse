# ADR 0007: Partition marts by day, cluster by the filter column, explain both

**Status:** Accepted (Oct 2026)

## Context

BigQuery bills by bytes scanned, and the dashboard always filters by date
range and groups by merchant or fraud type. Warehouse design must follow the
query pattern, not mimic the source table.

## Decision

In the dbt marts (`qris_analytics/models/`):

- `mart_fraud_flags`: partition by `day` (date), cluster by `fraud_type`.
- `mart_merchant_volume`: partition by `day`, cluster by `merchant_id`.
- `mart_user_risk`: intentionally NOT partitioned (it is a per-user snapshot,
  not a time series) and clustered by `user_id`.
- The rationale lives in a comment at the top of each model file, next to the
  config, so the "why" travels with the code.

## Consequences

- Good: date-filtered dashboard tiles prune partitions; per-merchant and
  per-type scans stay small.
- Good: each model states why it is shaped that way, so reviewers can check
  the reasoning instead of guessing. Proof screenshot:
  `docs/proof_partitioning.png`.
- Cost: the ~8 MB demo dataset does not need any of this. Partitioning is
  here to demonstrate the pattern, and the honest note says so.
- Known limit: `mart_user_risk` grows with users, not days. If it ever gets
  large, the fix is a different materialization strategy, not partitioning.

## Alternatives considered

- No partitioning: simpler, but the dashboards are date-filtered and the
  point is to show query-pattern-driven design.
- Partition everything, including the user snapshot: wrong tool for a
  non-time-series table.
