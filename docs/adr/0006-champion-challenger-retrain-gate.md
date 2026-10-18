# ADR 0006: Champion/challenger retraining with an F1 gate and a never-delete registry

**Status:** Accepted (Oct 2026)

## Context

Fraud drifts, so a one-shot model rots. But blind retraining can ship a worse
model, and labels arrive late in production: you learn that a transaction was
fraud two days after the fact.

## Decision

Three scheduled steps (`pipeline/score.py`, `pipeline/reconcile.py`,
`pipeline/retrain.py`, chained in the Airflow DAG):

1. **Score:** the champion model stamps `model_version` on every silver row.
2. **Reconcile:** replays delayed labels (default 2 days) and reports
   precision/recall/F1 + drift flags to `reports/reconcile_metrics.json`.
   Always exits 0: monitoring, not a gate.
3. **Retrain:** a challenger trains on the newest 21-day window, tests on the
   newest week, and is promoted only if F1 >= champion F1 + 0.005.
   `reports/model_registry.json` is the source of truth. Old models are never
   deleted.

## Consequences

- Good: promotion is evidence-based. The first run honestly recorded
  "challenger tied champion, correctly NOT promoted".
- Good: rollback is trivial, every version stays in the registry.
- Cost: the 0.005 margin is a chosen constant. Too strict biases toward
  staleness, too loose allows noise promotions.
- Known limit: labels are simulated with delay. The mechanics (versioning,
  gate, registry) are the production pattern; the timing is not real.
- Known limit: no automatic rollback trigger yet. Reconcile flags drift, a
  human decides.

## Alternatives considered

- Retrain and replace unconditionally: can ship regressions.
- Manual retraining: no cadence, rots quietly.
- Shadow scoring without promotion: no path to improve.
