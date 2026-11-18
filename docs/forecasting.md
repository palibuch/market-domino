# Market Domino: Forecast Research

`forecast_next(bars)` produces a one-step-ahead expected return, an empirical direction frequency, and a symmetric 90% split-conformal residual interval. It uses close-only features and chronologically separates model fitting from residual calibration. The latest bar's unknown next-close label is never used.

```python
from market_domino.forecast import forecast_next

forecast = forecast_next(price_bars)
print(forecast.expected_return, forecast.probability_up)
print(forecast.lower_90, forecast.upper_90)
print(forecast.calibration_mae, forecast.baseline_calibration_mae)
```

The model is an interpretable diagonal linear baseline shrunk toward the training median. The conformal interval uses a finite-sample order statistic of absolute residuals; its nominal coverage depends on exchangeability/stability assumptions that financial time series commonly violate. The direction frequency is an empirical holdout diagnostic and is **not guaranteed calibrated**. Both may be unreliable under regime shifts or small samples. Baseline MAE is reported for comparison, not for model selection on a repeatedly reused holdout.

For credible evaluation, compare forecasts against zero-return and historical-mean baselines across repeated walk-forward windows, account for publication times and market calendars, and report interval coverage and calibration by regime. Do not select a model by repeatedly inspecting the same holdout. No data downloads or orders are made by this module.
