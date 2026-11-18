"""Chronological evaluation for the experimental neural learner.

This module deliberately evaluates regression forecasts rather than turning
outputs into positions. It fits fresh preprocessing and a fresh model inside
each training fold, and compares against simple baselines on identical test
observations. It does not fetch data or claim that synthetic performance
transfers to markets.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from statistics import fmean
from typing import Sequence

from .ml import PriceBar, SimpleLinearModel, chronological_splits, features
from .neural import NeuralRegressor


@dataclass(frozen=True)
class NeuralFoldResult:
    """Out-of-sample metrics for one chronological fold."""

    train_start: int
    train_stop: int
    test_start: int
    test_stop: int
    observations: int
    neural_mse: float
    linear_mse: float
    zero_mse: float
    train_mean_mse: float
    neural_mae: float
    linear_mae: float
    neural_predictions: tuple[float, ...]
    actual_targets: tuple[float, ...]
    model: NeuralRegressor


@dataclass(frozen=True)
class NeuralWalkForwardReport:
    """Fold results and equal-observation aggregate errors."""

    folds: tuple[NeuralFoldResult, ...]
    observations: int
    neural_mse: float
    linear_mse: float
    zero_mse: float
    train_mean_mse: float
    neural_mae: float
    linear_mae: float
    neural_beats_linear: bool
    disclaimer: str = (
        "Historical out-of-sample diagnostics only; not evidence of future market edge, "
        "a calibrated probability, or investment advice."
    )


def evaluate_neural_walk_forward(
    bars: Sequence[PriceBar],
    *,
    train_size: int,
    test_size: int,
    hidden_units: int = 8,
    epochs: int = 300,
    learning_rate: float = 0.03,
    l2: float = 1e-4,
    seed: int = 42,
) -> NeuralWalkForwardReport:
    """Fit and compare neural and linear regressors over expanding time folds.

    Row ``i`` uses information through close ``i`` to estimate the return from
    close ``i`` to close ``i+1``. Training labels are therefore available by
    the first test close. Each fold fits its own models using training rows
    only. Linear, zero-return, and training-mean baselines use the exact same
    test timestamps. This is diagnostic evaluation, not a trading backtest.
    """
    if len(bars) < 2:
        raise ValueError("at least two bars are required")
    if any(left.timestamp >= right.timestamp for left, right in zip(bars, bars[1:])):
        raise ValueError("bars must have strictly increasing timestamps")
    if train_size < 2 or test_size < 1:
        raise ValueError("invalid training or test window size")

    close = [bar.close for bar in bars]
    all_features = features(close)
    offset = 20
    fold_results: list[NeuralFoldResult] = []

    for train_indices, test_indices in chronological_splits(len(bars) - 1, train_size, test_size):
        train_rows: list[list[float]] = []
        train_targets: list[float] = []
        for index in train_indices:
            feature_index = index - offset
            if 0 <= feature_index < len(all_features):
                train_rows.append(all_features[feature_index])
                train_targets.append(close[index + 1] / close[index] - 1.0)
        if len(train_rows) < 10:
            raise ValueError("training window has fewer than 10 valid observations")

        test_rows: list[list[float]] = []
        test_targets: list[float] = []
        for index in test_indices:
            feature_index = index - offset
            if 0 <= feature_index < len(all_features):
                test_rows.append(all_features[feature_index])
                test_targets.append(close[index + 1] / close[index] - 1.0)
        if not test_rows:
            continue

        neural = NeuralRegressor.fit(
            train_rows,
            train_targets,
            hidden_units=hidden_units,
            epochs=epochs,
            learning_rate=learning_rate,
            l2=l2,
            seed=seed,
        )
        linear = SimpleLinearModel.fit(train_rows, train_targets)
        training_mean = fmean(train_targets)
        neural_predictions = tuple(neural.predict(row) for row in test_rows)
        linear_predictions = tuple(linear.predict(row) for row in test_rows)
        count = len(test_targets)
        neural_mse = fmean((prediction - actual) ** 2 for prediction, actual in zip(neural_predictions, test_targets))
        linear_mse = fmean((prediction - actual) ** 2 for prediction, actual in zip(linear_predictions, test_targets))
        zero_mse = fmean(actual**2 for actual in test_targets)
        mean_mse = fmean((training_mean - actual) ** 2 for actual in test_targets)
        neural_mae = fmean(abs(prediction - actual) for prediction, actual in zip(neural_predictions, test_targets))
        linear_mae = fmean(abs(prediction - actual) for prediction, actual in zip(linear_predictions, test_targets))
        fold_results.append(NeuralFoldResult(
            train_start=train_indices.start,
            train_stop=train_indices.stop,
            test_start=test_indices.start,
            test_stop=test_indices.stop,
            observations=count,
            neural_mse=neural_mse,
            linear_mse=linear_mse,
            zero_mse=zero_mse,
            train_mean_mse=mean_mse,
            neural_mae=neural_mae,
            linear_mae=linear_mae,
            neural_predictions=neural_predictions,
            actual_targets=tuple(test_targets),
            model=neural,
        ))

    if not fold_results:
        raise ValueError("no evaluable walk-forward folds")
    observations = sum(fold.observations for fold in fold_results)
    if observations == 0:
        raise ValueError("walk-forward folds contain no labeled test observations")

    def aggregate(field: str) -> float:
        return sum(getattr(fold, field) * fold.observations for fold in fold_results) / observations

    neural_mse = aggregate("neural_mse")
    linear_mse = aggregate("linear_mse")
    values = (neural_mse, linear_mse, aggregate("zero_mse"), aggregate("train_mean_mse"))
    if any(not isfinite(value) for value in values):
        raise ValueError("evaluation produced non-finite metrics")
    return NeuralWalkForwardReport(
        folds=tuple(fold_results),
        observations=observations,
        neural_mse=neural_mse,
        linear_mse=linear_mse,
        zero_mse=values[2],
        train_mean_mse=values[3],
        neural_mae=aggregate("neural_mae"),
        linear_mae=aggregate("linear_mae"),
        neural_beats_linear=neural_mse < linear_mse,
    )
