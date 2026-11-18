"""Historical backtesting and standard-library feature generation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite, sqrt
from statistics import pstdev
from typing import Iterable, Sequence


@dataclass(frozen=True)
class PriceBar:
    timestamp: datetime
    close: float

    def __post_init__(self) -> None:
        if not isfinite(self.close) or self.close <= 0:
            raise ValueError("close must be a finite positive number")
        if self.timestamp.tzinfo is None or self.timestamp.utcoffset() is None:
            raise ValueError("timestamp must be timezone-aware")


@dataclass(frozen=True)
class WalkForwardMetrics:
    observations: int
    mean_return: float
    annualized_sharpe: float
    maximum_drawdown: float
    accuracy: float
    total_cost: float = 0.0


def chronological_splits(
    length: int,
    train_size: int,
    test_size: int,
) -> Iterable[tuple[range, range]]:
    """Generate expanding chronological windows with disjoint sample indices."""
    if length < 1:
        raise ValueError("length must be positive")
    if train_size < 2 or test_size < 1:
        raise ValueError("invalid training or test window size")

    start = 0
    while start + train_size + test_size <= length:
        yield range(start, start + train_size), range(
            start + train_size,
            start + train_size + test_size,
        )
        start += test_size


def rolling_mean(values: Sequence[float], window: int) -> list[float | None]:
    if window < 1:
        raise ValueError("window must be positive")
    output: list[float | None] = [None] * len(values)
    total = 0.0
    for index, value in enumerate(values):
        total += value
        if index >= window:
            total -= values[index - window]
        if index + 1 >= window:
            output[index] = total / window
    return output


def features(close: Sequence[float]) -> list[list[float]]:
    """Build interpretable, close-time features; no feature uses a future close.

    Rows correspond to source close indices 20 onward. Callers must preserve this
    documented offset when aligning rows with labels.
    """
    if any(not isfinite(value) or value <= 0 for value in close):
        raise ValueError("close values must be finite and positive")
    if len(close) < 21:
        return []

    returns = [0.0] * len(close)
    for index in range(1, len(close)):
        returns[index] = close[index] / close[index - 1] - 1.0

    means_5 = rolling_mean(close, 5)
    means_20 = rolling_mean(close, 20)
    volatility_10: list[float | None] = [None] * len(close)
    for index in range(9, len(close)):
        volatility_10[index] = pstdev(returns[index - 9:index + 1])

    rows: list[list[float]] = []
    for index in range(20, len(close)):
        mean_5 = means_5[index]
        mean_20 = means_20[index]
        vol = volatility_10[index]
        assert mean_5 is not None and mean_20 is not None and vol is not None
        rows.append([
            returns[index],
            close[index] / mean_5 - 1.0,
            close[index] / mean_20 - 1.0,
            vol,
        ])
    return rows


@dataclass(frozen=True)
class SimpleLinearModel:
    """A deterministic diagonal ridge regression baseline."""

    weights: tuple[float, ...]
    bias: float

    @classmethod
    def fit(cls, rows: Sequence[Sequence[float]], targets: Sequence[float]) -> "SimpleLinearModel":
        if len(rows) != len(targets) or not rows:
            raise ValueError("training rows and targets must have equal, non-zero lengths")
        width = len(rows[0])
        if width == 0 or any(len(row) != width for row in rows):
            raise ValueError("all feature rows must have the same non-zero width")
        if any(not isfinite(value) for row in rows for value in row):
            raise ValueError("features must be finite")
        if any(not isfinite(target) for target in targets):
            raise ValueError("targets must be finite")

        means = [sum(row[column] for row in rows) / len(rows) for column in range(width)]
        target_mean = sum(targets) / len(targets)
        weights: list[float] = []
        for column, mean in enumerate(means):
            covariance = sum(
                (row[column] - mean) * (target - target_mean)
                for row, target in zip(rows, targets)
            )
            variance = sum((row[column] - mean) ** 2 for row in rows)
            ridge = 1e-6
            weights.append(covariance / (variance + ridge) if variance else 0.0)

        bias = target_mean - sum(weight * mean for weight, mean in zip(weights, means))
        return cls(tuple(weights), bias)

    def predict(self, row: Sequence[float]) -> float:
        if len(row) != len(self.weights):
            raise ValueError("feature width does not match model")
        if any(not isfinite(value) for value in row):
            raise ValueError("features must be finite")
        prediction = self.bias + sum(weight * value for weight, value in zip(self.weights, row))
        if not isfinite(prediction):
            raise ValueError("prediction is not finite")
        return prediction


def evaluate_model(
    bars: Sequence[PriceBar],
    train: range,
    test: range,
    threshold: float = 0.001,
    cost_bps: float = 0.0,
) -> tuple[SimpleLinearModel, WalkForwardMetrics]:
    """Evaluate next-bar returns on a chronological holdout.

    Indices refer to the close whose feature is used to predict its next close.
    A cost is charged for each unit of position turnover, including initial entry.
    Metrics assume one observation per trading session for Sharpe annualization.
    """
    if not isfinite(threshold) or threshold < 0:
        raise ValueError("threshold must be finite and non-negative")
    if not isfinite(cost_bps) or cost_bps < 0:
        raise ValueError("cost_bps must be finite and non-negative")
    if not train or not test:
        raise ValueError("train and test ranges must not be empty")
    if train.step <= 0 or test.step <= 0:
        raise ValueError("train and test ranges must move forward")
    if train.start < 0 or test.start < 0 or train.stop > len(bars) or test.stop > len(bars):
        raise ValueError("train/test indices exceed available bars")
    if train.stop > test.start:
        raise ValueError("training and test indices must be disjoint and chronological")
    if any(left.timestamp >= right.timestamp for left, right in zip(bars, bars[1:])):
        raise ValueError("bars must have strictly increasing timestamps")

    close = [bar.close for bar in bars]
    all_features = features(close)
    offset = 20

    train_rows: list[list[float]] = []
    train_targets: list[float] = []
    for index in train:
        feature_index = index - offset
        if index + 1 >= len(close) or feature_index < 0 or feature_index >= len(all_features):
            continue
        train_rows.append(all_features[feature_index])
        train_targets.append(close[index + 1] / close[index] - 1.0)

    if len(train_rows) < 10:
        raise ValueError("training window has fewer than 10 valid observations")

    model = SimpleLinearModel.fit(train_rows, train_targets)
    strategy_returns: list[float] = []
    correct = 0
    total_cost = 0.0
    previous_position = 0.0

    for index in test:
        feature_index = index - offset
        if index + 1 >= len(close) or feature_index < 0 or feature_index >= len(all_features):
            continue
        prediction = model.predict(all_features[feature_index])
        position = 1.0 if prediction > threshold else (-1.0 if prediction < -threshold else 0.0)
        actual = close[index + 1] / close[index] - 1.0
        cost = abs(position - previous_position) * cost_bps / 10_000.0
        strategy_returns.append(position * actual - cost)
        total_cost += cost
        previous_position = position
        correct += int((prediction >= 0) == (actual >= 0))

    if not strategy_returns:
        return model, WalkForwardMetrics(0, 0.0, 0.0, 0.0, 0.0, total_cost)

    mean = sum(strategy_returns) / len(strategy_returns)
    deviation = pstdev(strategy_returns) if len(strategy_returns) > 1 else 0.0
    sharpe = 0.0 if deviation == 0 else mean / deviation * sqrt(252)

    equity = 1.0
    peak = 1.0
    max_drawdown = 0.0
    for result in strategy_returns:
        equity *= 1.0 + result
        peak = max(peak, equity)
        max_drawdown = min(max_drawdown, equity / peak - 1.0)

    return model, WalkForwardMetrics(
        observations=len(strategy_returns),
        mean_return=mean,
        annualized_sharpe=sharpe,
        maximum_drawdown=max_drawdown,
        accuracy=correct / len(strategy_returns),
        total_cost=total_cost,
    )
