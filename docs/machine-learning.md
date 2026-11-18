# Market Domino: Machine Learning Foundation

The initial model is an interpretable research baseline:

- close-time return, five-session and twenty-session moving-average deviations, and ten-session volatility,
- a deterministic diagonal linear regression fit on training windows only,
- chronological expanding-window walk-forward splits,
- next-session close-to-close labels,
- optional turnover costs expressed in basis points,
- return, annualized Sharpe, maximum drawdown, directional accuracy, and total modeled costs.

The implementation validates finite prices/features, aware timestamps, strictly increasing bars, and non-overlapping chronological train/test indices. Features use only closes available at their timestamp; each row maps to source close index 20 onward.

## Usage

```python
from datetime import datetime, timedelta, timezone

from market_domino.ml import PriceBar, chronological_splits, evaluate_model

now = datetime(2025, 1, 1, tzinfo=timezone.utc)
close = [100.0 * (1.001 ** i) for i in range(300)]
bars = [PriceBar(now + timedelta(days=i), value) for i, value in enumerate(close)]

for train, test in chronological_splits(len(bars), train_size=200, test_size=50):
    model, metrics = evaluate_model(bars, train, test, cost_bps=5.0)
    print(metrics)
```

## Limitations

This research module does not download data, provide calibrated probabilities, or trade. The diagonal regression fits each feature independently, so it is a deliberately simple baseline rather than a full multivariate estimator. Sharpe annualization assumes daily observations and does not account for missing sessions. The provided split helper does not itself enforce a purge/embargo for arbitrary labels; current next-bar labels are safe only when train/test indices are chronological and disjoint. Costs are a simple turnover penalty, not a market-impact or liquidity model. Backtest metrics do not establish predictive power or future performance.

## Next improvements

- Market data adapters with provenance and publication timestamps
- Explicit exchange calendars and missing-session policies
- Purged/embargoed splits for multi-session labels
- Multivariate regularized estimators and baseline comparisons
- Calibration and block-bootstrap uncertainty estimates
- Slippage, transaction-cost and liquidity sensitivity
- Repeated walk-forward runs across market regimes
