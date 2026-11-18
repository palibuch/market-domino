"""Small deterministic neural baseline for point-in-time market research.

This is an experimental, single-hidden-layer multilayer perceptron. It is a
teachable, auditable starting point, not a general reasoning system or a claim
of market predictability. Callers must provide only the chronological training
fold; this module does not split data or fetch market information.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt, tanh
import random
from typing import Sequence


@dataclass(frozen=True)
class NeuralRegressor:
    """Immutable tanh MLP for small numeric regression tasks.

    Inputs and targets are standardized using training-fold statistics. The
    fitted statistics are retained so predictions can be made in original
    units. All tuples are immutable, making a fitted model reproducible and
    straightforward to serialize in a future versioned format.
    """

    input_mean: tuple[float, ...]
    input_scale: tuple[float, ...]
    hidden_weights: tuple[tuple[float, ...], ...]
    hidden_biases: tuple[float, ...]
    output_weights: tuple[float, ...]
    output_bias: float
    target_mean: float
    target_scale: float
    training_mse: float

    @classmethod
    def fit(
        cls,
        rows: Sequence[Sequence[float]],
        targets: Sequence[float],
        *,
        hidden_units: int = 8,
        epochs: int = 300,
        learning_rate: float = 0.03,
        l2: float = 1e-4,
        seed: int = 42,
    ) -> NeuralRegressor:
        """Fit by deterministic full-batch gradient descent.

        The caller is responsible for chronological splitting and must pass
        training observations only. No shuffling or implicit split is done.
        ``training_mse`` is a diagnostic on the supplied training fold, not an
        estimate of out-of-sample performance.
        """
        if not rows or len(rows) != len(targets):
            raise ValueError("training rows and targets must have equal, non-zero lengths")
        width = len(rows[0])
        if width == 0 or any(len(row) != width for row in rows):
            raise ValueError("all feature rows must have the same non-zero width")
        if any(not isfinite(value) for row in rows for value in row):
            raise ValueError("features must be finite")
        if any(not isfinite(value) for value in targets):
            raise ValueError("targets must be finite")
        if not isinstance(hidden_units, int) or isinstance(hidden_units, bool) or hidden_units < 1:
            raise ValueError("hidden_units must be a positive integer")
        if not isinstance(epochs, int) or isinstance(epochs, bool) or epochs < 1:
            raise ValueError("epochs must be a positive integer")
        if not isfinite(learning_rate) or learning_rate <= 0:
            raise ValueError("learning_rate must be finite and positive")
        if not isfinite(l2) or l2 < 0:
            raise ValueError("l2 must be finite and non-negative")
        if not isinstance(seed, int) or isinstance(seed, bool):
            raise ValueError("seed must be an integer")

        count = len(rows)
        input_mean = tuple(sum(row[column] for row in rows) / count for column in range(width))
        input_scale = tuple(
            max(sqrt(sum((row[column] - input_mean[column]) ** 2 for row in rows) / count), 1e-12)
            for column in range(width)
        )
        target_mean = sum(targets) / count
        target_scale = max(sqrt(sum((target - target_mean) ** 2 for target in targets) / count), 1e-12)
        normalized_rows = [
            [(value - input_mean[column]) / input_scale[column] for column, value in enumerate(row)]
            for row in rows
        ]
        normalized_targets = [(target - target_mean) / target_scale for target in targets]

        rng = random.Random(seed)
        limit = sqrt(6.0 / (width + hidden_units))
        hidden_weights = [
            [rng.uniform(-limit, limit) for _ in range(width)] for _ in range(hidden_units)
        ]
        hidden_biases = [0.0] * hidden_units
        output_weights = [rng.uniform(-limit, limit) for _ in range(hidden_units)]
        output_bias = 0.0

        for _ in range(epochs):
            grad_hidden_weights = [[0.0] * width for _ in range(hidden_units)]
            grad_hidden_biases = [0.0] * hidden_units
            grad_output_weights = [0.0] * hidden_units
            grad_output_bias = 0.0
            for row, target in zip(normalized_rows, normalized_targets):
                hidden = [
                    tanh(hidden_biases[h] + sum(w * x for w, x in zip(hidden_weights[h], row)))
                    for h in range(hidden_units)
                ]
                prediction = output_bias + sum(w * value for w, value in zip(output_weights, hidden))
                error_gradient = 2.0 * (prediction - target) / count
                grad_output_bias += error_gradient
                for h, activation in enumerate(hidden):
                    grad_output_weights[h] += error_gradient * activation
                    hidden_gradient = error_gradient * output_weights[h] * (1.0 - activation**2)
                    grad_hidden_biases[h] += hidden_gradient
                    for column, value in enumerate(row):
                        grad_hidden_weights[h][column] += hidden_gradient * value

            for h in range(hidden_units):
                grad_output_weights[h] += l2 * output_weights[h]
                output_weights[h] -= learning_rate * grad_output_weights[h]
                hidden_biases[h] -= learning_rate * grad_hidden_biases[h]
                for column in range(width):
                    grad_hidden_weights[h][column] += l2 * hidden_weights[h][column]
                    hidden_weights[h][column] -= learning_rate * grad_hidden_weights[h][column]
            output_bias -= learning_rate * grad_output_bias

        model = cls(
            input_mean=input_mean,
            input_scale=input_scale,
            hidden_weights=tuple(tuple(row) for row in hidden_weights),
            hidden_biases=tuple(hidden_biases),
            output_weights=tuple(output_weights),
            output_bias=output_bias,
            target_mean=target_mean,
            target_scale=target_scale,
            training_mse=0.0,
        )
        predictions = [model.predict(row) for row in rows]
        mse = sum((prediction - target) ** 2 for prediction, target in zip(predictions, targets)) / count
        if not isfinite(mse):
            raise ValueError("training produced a non-finite loss")
        return cls(**{**model.__dict__, "training_mse": mse})

    def predict(self, row: Sequence[float]) -> float:
        """Predict one target in the original target units."""
        if len(row) != len(self.input_mean):
            raise ValueError("feature width does not match model")
        if any(not isfinite(value) for value in row):
            raise ValueError("features must be finite")
        normalized = [
            (value - self.input_mean[column]) / self.input_scale[column]
            for column, value in enumerate(row)
        ]
        hidden = [
            tanh(bias + sum(weight * value for weight, value in zip(weights, normalized)))
            for weights, bias in zip(self.hidden_weights, self.hidden_biases)
        ]
        prediction = self.output_bias + sum(
            weight * activation for weight, activation in zip(self.output_weights, hidden)
        )
        result = self.target_mean + self.target_scale * prediction
        if not isfinite(result):
            raise ValueError("prediction is not finite")
        return result
