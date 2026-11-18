# Market Domino

Market Domino is an experimental, auditable research engine for mapping market scenarios and testing hypotheses over time. It is not a trading system and does not place orders.

## Current foundation

- A typed, versioned directed acyclic graph (DAG) for events, indicators, sectors, assets, and risks.
- Point-in-time filtering: scenario runs only use nodes and edges available at the requested timestamp.
- Edges must reference explicit hypotheses; draft/rejected edges are excluded from default propagation.
- Reproducible Monte Carlo scenario propagation with a fixed seed and bounded path expansion.
- Reports include impact intervals, directional shares, representative paths, evidence IDs, and a stable run ID.
- A small ML research baseline with chronological walk-forward evaluation, finite-data validation, and optional turnover costs.
- UTC-aware timestamps are required to reduce time-zone ambiguity.

**Important:** impact scores are normalized scenario scores, not estimated causal effects, price forecasts, probabilities of profit, or investment advice. A graph edge is a research hypothesis, not proof of causality. Causal interpretation requires an identification strategy, controls for confounding, and out-of-sample validation.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e ".[dev]"
python -m pytest
```

The core engine uses only the Python standard library. Tests use pytest-compatible `unittest` cases.

See [the machine-learning guide](docs/machine-learning.md) and [architecture notes](docs/architecture.md).
