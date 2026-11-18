"""Holdout-calibrated forecast intervals for historical research.

This module makes one-step-ahead forecasts from close-only features. Its empirical
probabilities are diagnostics from a chronological calibration holdout, not
promises of calibrated future probabilities.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import ceil, isfinite
from statistics import median
from typing import Sequence

from .ml import PriceBar, SimpleLinearModel, features


@dataclass(frozen=True)
class Forecast:
    as_of: object
    expected_return: float
    probability_up: float
    lower_90: float
    upper_90: float
    calibration_observations: int
    baseline_return: float
    disclaimer: str = (
        "Empirical holdout diagnostics only; not a calibrated probability, "
        "price target, trading signal, or investment advice."
    )


def _quantile(values: Sequence[float], q: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    low = int(position)
    high = min(low + 1, len(ordered) - 1)
    fraction = position - low
    return ordered[low] * (1.0 - fraction) + ordered[high] * fraction


def forecast_next(
    bars: Sequence[PriceBar],
    *,
    calibration_fraction: float = 0.2,
    min_calibration_observations: int = 10,
) -> Forecast:
    """Forecast the next close-to-close return using a chronological holdout.

    The linear model is trained on the earliest labeled observations. A later,
    disjoint calibration segment supplies empirical residuals for the interval
    and direction-frequency diagnostics. No calibration labels are used to fit
    the model. The latest close is used only as the forecast feature row.
    """
    if not 0.1 <= calibration_fraction <= 0.5:
        raise ValueError("calibration_fraction must be between 0.1 and 0.5")
    if min_calibration_observations < 5:
        raise ValueError("min_calibration_observations must be at least 5")
    if len(bars) < 22:
        raise ValueError("at least 22 bars are needed to build a forecast feature")
    if any(left.timestamp >= right.timestamp for left, right in zip(bars, bars[1:])):
        raise ValueError("bars must have strictly increasing timestamps")

    close = [bar.close for bar in bars]
    rows = features(close)
    # Feature row j represents source close index j + 20. The last row has no
    # known next-close label and must never enter fitting or calibration.
    labeled_count = len(rows) - 1
    calibration_count = max(min_calibration_observations, ceil(labeled_count * calibration_fraction))
    train_count = labeled_count - calibration_count
    if train_count < 10:
        raise ValueError("insufficient training data after reserving calibration observations")

    targets: list[float] = []
    for row_index in range(labeled_count):
        source_index = row_index + 20
        targets.append(close[source_index + 1] / close[source_index] - 1.0)

    model = SimpleLinearModel.fit(rows[:train_count], targets[:train_count])
    baseline = median(targets[:train_count])

    def ensemble(row: Sequence[float]) -> float:
        # Shrink an unstable small-sample fit toward the training-only median.
        return 0.75 * model.predict(row) + 0.25 * baseline

    residuals = [
        actual - ensemble(row)
        for row, actual in zip(rows[train_count:labeled_count], targets[train_count:labeled_count])
    ]
    if len(residuals) < min_calibration_observations:
        raise ValueError("not enough chronological calibration observations")

    point = ensemble(rows[-1])
    probability_up = sum(point + residual > 0 for residual in residuals) / len(residuals)
    return Forecast(
        as_of=bars[-1].timestamp,
        expected_return=point,
        probability_up=probability_up,
        lower_90=point + _quantile(residuals, 0.05),
        upper_90=point + _quantile(residuals, 0.95),
        calibration_observations=len(residuals),
        baseline_return=baseline,
    )
