# Architecture Decision Records (ADR)

Short documents that record **why** the pipeline is built this way, not just what it does.
Each ADR states the context, the decision, the honest downsides, and the alternatives that were rejected.

| # | Decision | Status |
|---|---|---|
| [0001](0001-two-ingestion-paths.md) | Two ingestion paths: Kafka stream + seeded batch lakehouse | Accepted |
| [0002](0002-local-kafka-at-least-once.md) | Local dockerized Kafka with at-least-once and dedup on read | Accepted |
| [0003](0003-seeded-artifacts-and-ci-repro-gate.md) | Commit seed-42 artifacts and gate CI on exact reproduction | Accepted |
| [0004](0004-rules-alongside-model.md) | Keep deterministic rules alongside the ML model | Accepted |
| [0005](0005-simple-model-time-split.md) | Logistic regression with a strict time split | Accepted |
| [0006](0006-champion-challenger-retrain-gate.md) | Champion/challenger retraining with an F1 gate and a never-delete registry | Accepted |
| [0007](0007-partition-and-cluster.md) | Partition marts by day, cluster by the filter column, explain both | Accepted |
| [0008](0008-terraform-dataset-dbt-tables.md) | Terraform owns the BigQuery dataset, dbt owns the tables | Accepted |

Format is intentionally lightweight (context / decision / consequences / alternatives),
inspired by the ADR practice used in production teams.
