# ADR 0005: Logistic regression with a strict time split

**Status:** Accepted (Oct 2026)

## Context

Fraud data is time-ordered. A random train/test split leaks future
information into the past and inflates metrics. Model choice also sets the
floor for explainability and reproducibility.

## Decision

- Algorithm: LogisticRegression with one-hot encoded categoricals.
- Split: strict time split, 3 weeks train / 1 week test, no shuffling.
- Threshold: selected on the validation side, then frozen into metrics.
- All metrics (precision, recall, F1, chosen threshold, model version) are
  written to `reports/model_metrics.json`, including the unflattering ones.

## Consequences

- Good: metrics are trustworthy (no leakage) and reproducible.
- Good: fast to train, no GPU, explainable coefficients.
- Cost: a linear model may underfit complex patterns. Accepted for v1 and
  documented rather than hidden.
- Known limit: a single time split, no cross-validation. The retrain loop
  (ADR 0006) is the mechanism that keeps re-measuring instead.

## Alternatives considered

- Random split: rejected. Leakage.
- Gradient boosting / ensembles: heavier, no demonstrated gain at this
  scale, harder to explain.
