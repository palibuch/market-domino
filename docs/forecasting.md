# Market Domino: Forecast Research

`forecast_next(bars)` produces a one-step-ahead expected return, empirical direction frequency, and a 90% residual interval. It uses close-only features and chronologically separates model fitting from residual calibration. The latest bar's next-close label is never used.

```python
from market_domino.forecast import forecast_next

forecast = forecast_next(price_bars)
print(forecast.expected_return, forecast.probability_up)
print(forecast.lower_90, forecast.upper_90)
```

The model is deliberately an interpretable diagonal linear baseline shrunk toward the training median. Its residual interval and direction frequency are empirical diagnostics from one held-out chronological segment. They are **not guaranteed calibrated**, are sensitive to regime changes and sample size, and are not price targets or trading advice. The core library does not download data or place orders.

For credible evaluation, compare each forecast against zero-return and historical-mean baselines across repeated walk-forward windows, account for data publication times and market calendars, and report calibration / coverage by regime. Do not select a model by repeatedly inspecting the same holdout.
