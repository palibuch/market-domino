"""Holdout-calibrated forecast intervals for historical research.

This module makes one-step-ahead forecasts from close-only features. Its empirical
direction frequency is a historical diagnostic, not a promise of calibrated
future probabilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import ceil, isfinite
from statistics import median
from typing import Sequence

from .ml import PriceBar, SimpleLinearModel, features


@dataclass(frozen=True)
class Forecast:
    as_of: datetime
    expected_return: float
    probability_up: float
    lower_90: float
    upper_90: float
    calibration_observations: int
    baseline_return: float
    calibration_mae: float
    baseline_calibration_mae: float
    interval_method: str = "split-conformal absolute residual interval"
    disclaimer: str = (
        "Empirical holdout diagnostics only; not a calibrated probability, "
        "price target, trading signal, or investment advice."
    )


def _conformal_radius(absolute_residuals: Sequence[float], coverage: float) -> float:
    """Finite-sample split-conformal order statistic (exchangeability assumed)."""
    if not absolute_residuals:
        raise ValueError("at least one calibration residual is required")
    ordered = sorted(absolute_residuals)
    rank = min(len(ordered), ceil((len(ordered) + 1) * coverage))
    return ordered[rank - 1]


def forecast_next(
    bars: Sequence[PriceBar],
    *,
    calibration_fraction: float = 0.2,
    min_calibration_observations: int = 10,
) -> Forecast:
    """Forecast next close-to-close return using disjoint chronological data.

    Earliest labels train the model; a later holdout is used only to estimate
    absolute residuals and directional-frequency diagnostics. The latest close
    supplies the forecast feature row, but its unknown next-close label is never
    included in training or calibration.
    """
    if not isfinite(calibration_fraction) or not 0.1 <= calibration_fraction <= 0.5:
        raise ValueError("calibration_fraction must be between 0.1 and 0.5")
    if not isinstance(min_calibration_observations, int) or isinstance(min_calibration_observations, bool):
        raise ValueError("min_calibration_observations must be an integer")
    if min_calibration_observations < 5:
        raise ValueError("min_calibration_observations must be at least 5")
    if len(bars) < 22:
        raise ValueError("at least 22 bars are needed to build a forecast feature")
    if any(left.timestamp >= right.timestamp for left, right in zip(bars, bars[1:])):
        raise ValueError("bars must have strictly increasing timestamps")

    close = [bar.close for bar in bars]
    rows = features(close)
    # Row j represents source close index j + 20. The final row has no known
    # next-close target and is intentionally withheld from fitting/calibration.
    labeled_count = len(rows) - 1
    calibration_count = max(
        min_calibration_observations,
        ceil(labeled_count * calibration_fraction),
    )
    train_count = labeled_count - calibration_count
    if train_count < 10:
        raise ValueError("insufficient training data after reserving calibration observations")

    targets = [
        close[row_index + 21] / close[row_index + 20] - 1.0
        for row_index in range(labeled_count)
    ]
    train_targets = targets[:train_count]
    model = SimpleLinearModel.fit(rows[:train_count], train_targets)
    baseline = median(train_targets)

    def estimate(row: Sequence[float]) -> float:
        # A modest shrinkage toward a robust training-only baseline limits
        # overreaction from the intentionally small diagonal linear model.
        return 0.75 * model.predict(row) + 0.25 * baseline

    calibration_predictions = [
        estimate(row) for row in rows[train_count:labeled_count]
    ]
    calibration_targets = targets[train_count:labeled_count]
    residuals = [actual - predicted for actual, predicted in zip(
        calibration_targets, calibration_predictions
    )]
    if len(residuals) < min_calibration_observations:
        raise ValueError("not enough chronological calibration observations")

    point = estimate(rows[-1])
    probability_up = sum(point + residual > 0 for residual in residuals) / len(residuals)
    radius = _conformal_radius([abs(residual) for residual in residuals], 0.9)
    calibration_mae = sum(abs(residual) for residual in residuals) / len(residuals)
    baseline_mae = sum(abs(actual - baseline) for actual in calibration_targets) / len(residuals)

    return Forecast(
        as_of=bars[-1].timestamp,
        expected_return=point,
        probability_up=probability_up,
        lower_90=point - radius,
        upper_90=point + radius,
        calibration_observations=len(residuals),
        baseline_return=baseline,
        calibration_mae=calibration_mae,
        baseline_calibration_mae=baseline_mae,
    )
