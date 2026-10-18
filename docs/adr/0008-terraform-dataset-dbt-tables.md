# ADR 0008: Terraform owns the BigQuery dataset, dbt owns the tables

**Status:** Accepted (Oct 2026)

## Context

Two tools in this stack can create BigQuery objects: Terraform and dbt. When
both touch the same object, state and ownership conflict.

## Decision

Strict ownership split:

- **Terraform** (`terraform/main.tf`): creates the `qris_analytics` dataset.
  Nothing else. Tables are explicitly out of scope, with a comment saying so.
- **dbt** (`qris_analytics/`): creates and owns every table and view inside
  the dataset (staging view + 3 marts).
- **`pipeline/load_to_bq.py`**: loads only the silver table. No DDL beyond
  "create dataset if missing", purely for standalone convenience.
- **IAM** (service account, roles) and billing stay manual. Documented as the
  known gap instead of half-codified.

## Consequences

- Good: exactly one owner per object, so `terraform apply` and `dbt run`
  never fight over state.
- Good: bootstrap order is explicit: Terraform -> load silver -> dbt run.
- Cost: IAM is not reproducible from code yet. A reviewer with a fresh GCP
  project must create the service account by hand; the README says so.
- Known limit: dataset-only Terraform is intentionally minimal. A production
  version would add modules for IAM, budgets, and BigQuery reservations.

## Alternatives considered

- All objects in Terraform, including tables: dbt then fights Terraform for
  ownership on every run.
- All objects in one tool: Terraform cannot express the dbt DAG; dbt cannot
  reliably create the dataset before its first run.
