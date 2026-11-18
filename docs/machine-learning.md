# Market Domino: Machine Learning Foundation

The first model is intentionally small and interpretable:

- `rolling_mean` and momentum features use only prior closes,
- training targets are next-bar close-to-close returns,
- features are recomputed from chronological history,
- the model is a ridge-like univariate linear fit,
- walk-forward windows have explicit train/test ranges,
- tests reject naive timestamps,
- metrics include accuracy, Sharpe ratio, and maximum drawdown.

## Scope

This is an experimental research module. It does not download market data, connect to a broker, infer prices, or perform live trading. Performance is not proof of predictive accuracy.

## Usage

```python
from datetime import datetime, timedelta, timezone

from market_domino.ml import PriceBar, chronological_splits, evaluate_model

now = datetime(2025, 1, 1, tzinfo=timezone.utc)
close = [100.0 * (1.001 ** i) for i in range(300)]
bars = [PriceBar(now + timedelta(days=i), value) for i, value in enumerate(close)]

for train, test in chronological_splits(len(bars), train_size=200, test_size=50):
    model, metrics = evaluate_model(bars, train, test)
    print(metrics)
```

## Next improvements

- Market data adapters with provenance and publication timestamps
- Purged/embargoed splits
- Scikit-learn integration behind a protocol interface
- Calibration and probability estimates
- Baseline comparisons and block bootstrap tests
- Transaction-cost and slippage sensitivity
- Repeated walk-forward runs across market regimes
