# ADR 0004: Keep deterministic rules alongside the ML model

**Status:** Accepted (Oct 2026)

## Context

Two of the four fraud typologies are context-dependent. Velocity means
"N transactions within a short window", which a per-row model structurally
cannot see. Risk teams also need explainable, immediate signals, not only a
probability.

## Decision

- Four deterministic rules flag silver rows during cleaning: velocity,
  night, round_amount, new_device.
- The ML model outputs a probability per row; the decision threshold is a
  business knob, tuned on validation data.
- Rules and model coexist. The dashboard and risk score consume rule flags
  (`mart_fraud_flags`, and `mart_user_risk` weights by typology).

## Consequences

- Good: explainable flags available immediately, no training needed.
- Good: the model handles the rest (amount/device/category patterns) with a
  probability instead of a hard yes/no.
- Cost: rule thresholds need maintenance and can overlap with model hits.
  Double counting is possible and documented; acceptable at this scale.
- Cost: velocity needs sorted history. Handled once in `clean_silver.py` so
  both the batch and the stream path share the same logic.

## Alternatives considered

- Model-only: rejected. Cannot see velocity, and unexplainable to risk ops.
- Rules-only: rejected. Rigid, no probability, no threshold flexibility.
