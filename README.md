# Market Domino

Market Domino is an experimental, auditable research engine for mapping market scenarios and testing hypotheses over time. It is not a trading system and does not place orders.

## Current foundation

- A typed, versioned directed acyclic graph (DAG) for events, indicators, sectors, assets, and risks.
- Point-in-time filtering: scenario runs only use nodes and edges available at the requested timestamp.
- Edges must reference explicit hypotheses; draft/rejected edges are excluded from default propagation.
- Reproducible Monte Carlo scenario propagation with a fixed seed and bounded path expansion.
- Reports include impact intervals, directional shares, representative paths, evidence IDs, and a stable run ID.
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

## Minimal example

```python
from datetime import datetime, timezone
from market_domino import Hypothesis, MarketDominoEngine, MarketEdge, MarketNode

now = datetime.now(timezone.utc)
engine = MarketDominoEngine()
engine.add_node(MarketNode("rates", "Funding costs", "indicator", "demo", now))
engine.add_node(MarketNode("sector", "Technology sector", "sector", "demo", now))
engine.add_hypothesis(Hypothesis(
    "h-rates-tech", "Funding costs may affect technology valuations",
    "Reject if effect reverses in two walk-forward windows", now,
    status="confirmed",
))
engine.add_edge(MarketEdge(
    "rates", "sector", "h-rates-tech", effect=-0.4, confidence=0.7,
    observed_at=now, valid_from=now, lag_sessions=5, effect_std=0.08,
    evidence_ids=("source-record-001",), evidence_count=80, status="confirmed",
))
result = engine.propagate("rates", shock=0.5, as_of=now, draws=2000, seed=17)
for impact in result.impacts:
    print(impact.node_name, impact.median_impact, impact.lower_90, impact.upper_90)
```

## Repository map

```text
market_domino/causal.py  validated graph model and scenario propagation
 tests/test_causal.py   point-in-time, cycle, reproducibility, and validation tests
docs/architecture.md    design boundaries and next engineering stages
```

## Development status

This is an early research prototype. It does not fetch market data, infer causal structure, backtest a tradable strategy, or connect to a broker. No live-trading capability is included. See [the architecture notes](docs/architecture.md) before extending it.
