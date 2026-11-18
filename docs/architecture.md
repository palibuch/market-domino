# Architecture and engineering principles

## Scope

The first milestone is a deterministic, auditable scenario graph—not an autonomous trading agent. The engine is deliberately separate from data vendors, language models, broker APIs, and user interfaces.

## Core concepts

- **Node:** timestamped observation or conceptual entity, carrying provenance and data-quality confidence.
- **Hypothesis:** falsifiable research statement with creation time, explicit invalidation rule, status, and evidence references.
- **Edge:** versioned hypothesis about a directional relationship. `effect` is normalized to `[-1, 1]`; it is not a return coefficient. `effect_std` describes uncertainty used for scenario sampling; it is not automatically a statistically calibrated posterior.
- **Scenario:** a source shock propagated through active graph paths. Multiple path contributions are summed and bounded to `[-1, 1]` at each node.
- **As-of time:** every run filters observations, hypotheses, and edges by availability time to avoid using information from the future.

## Guardrails

1. Only confirmed edges are used by default. Testing edges require an explicit opt-in.
2. Rejected hypotheses cannot support edges.
3. Cycles are rejected. Feedback loops need a separately specified dynamic model; silently unrolling them would be misleading.
4. Each run is reproducible with a seed and receives a hash-based identifier.
5. A path expansion limit prevents accidental exponential work.
6. Scenario impact summaries must not be presented as causal estimates or forecasts without additional validation.
7. No execution or broker integration is part of this milestone.

## Current limitations

- Confidence values and edge effects are supplied by the research process; the engine does not estimate them from prices.
- Normal sampling is a pragmatic placeholder, not a calibrated Bayesian posterior.
- Path contributions are aggregated under a declared heuristic; correlated paths can double-count the same underlying evidence.
- Market regime changes, missing-data mechanisms, transaction costs, and survivorship bias are not modeled here.

## Next stages

1. Add immutable source records with publication time, retrieval time, license, and content hash.
2. Implement point-in-time dataset snapshots and tests against look-ahead leakage.
3. Add walk-forward evaluation with baselines, transaction-cost sensitivity, and purged time splits.
4. Estimate candidate edge stability with explicit confounder controls and multiple-testing correction.
5. Build API and visual graph only after the data model and test contracts stabilize.

## Review roles for collaborators

- **Causal inference reviewer:** challenge whether an edge can be interpreted causally and list confounders/identification assumptions.
- **Quant validation reviewer:** audit temporal splits, leakage, survivorship bias, and baseline comparisons.
- **Reliability reviewer:** inspect determinism, path explosion, malformed timestamps, and failure handling.
- **Data provenance reviewer:** verify source, publication timestamps, licensing, and reproducibility.

These roles are review checklists, not claims that independent agents or experts have reviewed the code.
