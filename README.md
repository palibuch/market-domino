# Market Domino

Market Domino is an experimental, auditable research engine for mapping market scenarios and testing hypotheses over time. It is not a trading system and does not place orders.

## Current foundation

- A typed, versioned directed acyclic graph (DAG) for events, indicators, sectors, assets, and risks.
- Point-in-time filtering and reproducible scenario propagation.
- Explicit hypotheses and evidence references for graph edges.
- Chronological walk-forward ML baseline with validation and modeled transaction costs.
- One-step-ahead forecast diagnostics with a separate chronological residual-calibration segment, empirical directional frequency, conformal-style uncertainty interval, and baseline error reporting.
- UTC-aware timestamps and finite-value validation.

**Important:** scenario impacts are not causal estimates. Forecast frequencies and intervals are historical diagnostics, not guaranteed calibrated probabilities, price targets, investment advice, or promises of future performance. Financial time series may violate the assumptions behind nominal interval coverage. No market-data download or live trading integration is included.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e ".[dev]"
python -m pytest
```

See [forecasting notes](docs/forecasting.md), [machine-learning guide](docs/machine-learning.md), and [architecture notes](docs/architecture.md).
