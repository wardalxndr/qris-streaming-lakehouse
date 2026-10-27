# ADR 0003: Commit seed-42 artifacts and gate CI on exact reproduction

**Status:** Accepted (Oct 2026)

## Context

"Works on my machine" is the default failure mode of pipeline repos. This
project also needs stable fraud metrics so numbers in docs and on the
dashboard can be trusted (e.g. 39 high-risk users).

## Decision

- The generator is fully seeded: `seed=42`, 100k events, ~2% fraud. Since
  Oct 27, 2026 it also injects ~1% dirty rows (300 duplicates, 350 bad
  amounts, 200 bad timestamps) so the quality gate is exercised, not idle.
- Outputs (`data/*.csv`, `reports/*.json`) are committed to the repo.
- CI (`.github/workflows/ci.yml`) re-runs the pipeline on a clean checkout
  and fails if the regenerated files differ from the committed ones:
  `git diff --ignore-cr-at-eol --exit-code`.
- `--ignore-cr-at-eol` because dev machines use `core.autocrlf=true` (CRLF
  worktree, LF blobs); the gate compares content, not checkout style.

## Consequences

- Good: one command proves end-to-end reproducibility on any machine.
- Good: CI catches silent behavior drift. A change that moves a metric fails
  the build until the new artifact is intentionally recommitted.
- Cost: ~10 MB of data in the repo. Fine at this size; DVC/LFS would be the
  answer at 100x.
- Cost: intentional output changes require recommitting artifacts in the same
  change. That is the point, but it must be explained to contributors.
- Known limit: a pure line-ending change would slip through the gate.
  Accepted: content identity is what matters here.

## Alternatives considered

- DVC / Git LFS: extra tooling for a 10 MB dataset.
- Regenerate in CI without committing outputs: no baseline to diff against,
  so drift stays invisible.
