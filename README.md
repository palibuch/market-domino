# Market Domino

Market Domino is an experimental, auditable research engine for mapping market scenarios and testing hypotheses over time. It is not a trading system and does not place orders.

## Current foundation

- A typed, versioned directed acyclic graph (DAG) for events, indicators, sectors, assets, and risks.
- Point-in-time filtering and reproducible scenario propagation.
- Explicit hypotheses and evidence references for graph edges.
- Chronological walk-forward ML baseline with validation and modeled transaction costs.
- One-step-ahead forecast diagnostics with a separate chronological residual-calibration segment, empirical directional frequency, conformal-style uncertainty interval, and baseline error reporting.
- A small deterministic neural regressor and chronological evaluation against linear and simple return baselines.
- UTC-aware timestamps and finite-value validation.

**Important:** scenario impacts are not causal estimates. Forecast frequencies and intervals are historical diagnostics, not guaranteed calibrated probabilities, price targets, investment advice, or a promise of performance.

## Research direction

The long-term ambition is a continuously learning research engine that builds and revises models, proposes falsifiable hypotheses, chooses experiments, examines counter-evidence, and learns from measured outcomes. The current code is only an early prototype; it is not autonomous, does not learn continuously in the background, and is not evidence of machine consciousness. See the [cognitive architecture and consciousness research plan](docs/consciousness-research.md).

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e ".[dev]"
python -m pytest
```

See [forecasting notes](docs/forecasting.md), [machine-learning guide](docs/machine-learning.md), [architecture notes](docs/architecture.md), and the [learning loop](docs/learning-loop.md).
