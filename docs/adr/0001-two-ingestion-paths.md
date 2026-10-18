# ADR 0001: Two ingestion paths, Kafka stream + seeded batch lakehouse

**Status:** Accepted (Oct 2026)

## Context

The interesting claim of this project is real-time fraud detection. But a
reviewer must be able to verify the pipeline without installing Docker, and
time-series fraud metrics must be stable enough to compare run to run. A
Kafka-only design fails both: it is environment-heavy and not deterministic.

## Decision

Ship two interchangeable ingestion paths that converge on the same silver
schema:

1. **Batch (canonical):** `pipeline/gen_qris.py` (seed=42) -> bronze CSV ->
   `pipeline/clean_silver.py` -> silver CSV. This path produces the committed
   artifacts and everything downstream (gold marts, model, forecast, dbt).
2. **Stream (proof):** local Kafka via `docker-compose.kafka.yml`, with
   `pipeline/produce.py` and `pipeline/consume.py` reusing the same
   validation logic. The Spark Structured Streaming job
   (`spark/spark_streaming_job.py`) is a runnable reference, not a required
   path.

## Consequences

- Good: reviewers reproduce the full pipeline with one command, no Docker.
- Good: the streaming claim is backed by a real test: consumer stopped during
  produce, then caught up 100,000/100,000 with 0 duplicates and 0 lost.
- Cost: two code paths must stay consistent. Mitigated: both call the same
  `clean_silver` rules, so drift is a bug, not a feature.
- Known limit: the Spark path needs PySpark + Java, and on Windows also
  winutils.exe/HADOOP_HOME. Documented in the README; CI runs on Linux.

## Alternatives considered

- Kafka-only: rejected. Reviewer friction, no deterministic artifacts.
- Cloud Pub/Sub + Dataflow: rejected for the demo. Credentials needed just to
  start, and always-on streaming cost (see the Cost section in the README).
- Batch-only: rejected. Loses the real-time story that motivates the project.
