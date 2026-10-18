# ADR 0002: Local dockerized Kafka with at-least-once and dedup on read

**Status:** Accepted (Oct 2026)

## Context

Streaming needs a broker. Managed options (Confluent Cloud, Pub/Sub) require
accounts and credentials before anything can be demoed, and none of that adds
learning value at this stage. Delivery guarantees also need a stance:
exactly-once across a CSV sink is not achievable without transactions.

## Decision

- Single-node KRaft Kafka broker in Docker Compose
  (`docker-compose.kafka.yml`), topic `qris-txns` with 3 partitions created
  on startup.
- Producer: `acks=all` with retries, i.e. at-least-once.
- Consumer: writes raw events; dedup and validation happen in silver on
  `transaction_id`, so replays are idempotent.

## Consequences

- Good: zero cloud setup, works offline, mirrors production semantics
  (partitions, consumer groups, offsets).
- Good: idempotent silver means at-least-once is safe: duplicates become
  data quality facts, not corruption. Proven by the Kafka E2E test.
- Cost: no exactly-once. A duplicate delivery is deduplicated, not prevented.
- Cost: single broker, no replication, no HA (accepted for a local demo).
- Known limit: consumer offsets live in the container; `docker compose down -v`
  resets consumption state.

## Alternatives considered

- Kafka transactions / exactly-once semantics: overkill for a CSV sink.
- Confluent Cloud / Pub/Sub: better production answer, worse demo answer.
- Redpanda: viable, but Kafka itself is the transferable skill.
