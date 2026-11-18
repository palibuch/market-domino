from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from market_domino.ml import PriceBar
from market_domino.neural_eval import evaluate_neural_walk_forward


class NeuralWalkForwardTests(unittest.TestCase):
    @staticmethod
    def sample_bars(count=120):
        start = datetime(2024, 1, 1, tzinfo=timezone.utc)
        close = 100.0
        bars = []
        for index in range(count):
            # Deterministic non-market data exercises training and evaluation;
            # it makes no claim about real-world predictability.
            close *= 1.0 + 0.0002 + 0.002 * ((index % 7) - 3) / 3
            bars.append(PriceBar(start + timedelta(days=index), close))
        return bars

    def test_evaluates_fresh_models_on_chronological_folds_and_baselines(self):
        report = evaluate_neural_walk_forward(
            self.sample_bars(), train_size=50, test_size=10, epochs=20, seed=13
        )
        self.assertEqual(len(report.folds), 6)
        self.assertEqual(report.observations, 60)
        for left, right in zip(report.folds, report.folds[1:]):
            self.assertLessEqual(left.test_stop, right.test_start)
            self.assertLess(left.train_stop, left.test_start)
        self.assertTrue(all(fold.observations == 10 for fold in report.folds))
        self.assertTrue(all(fold.model.training_mse >= 0 for fold in report.folds))
        for metric in (
            report.neural_mse,
            report.linear_mse,
            report.zero_mse,
            report.train_mean_mse,
            report.neural_mae,
            report.linear_mae,
        ):
            self.assertTrue(metric >= 0)

    def test_results_are_reproducible(self):
        bars = self.sample_bars()
        first = evaluate_neural_walk_forward(bars, train_size=50, test_size=10, epochs=12)
        second = evaluate_neural_walk_forward(bars, train_size=50, test_size=10, epochs=12)
        self.assertEqual(first, second)

    def test_rejects_unsorted_bars_and_insufficient_training(self):
        bars = self.sample_bars()
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            evaluate_neural_walk_forward([bars[1], bars[0]], train_size=1, test_size=1)
        with self.assertRaisesRegex(ValueError, "fewer than 10"):
            evaluate_neural_walk_forward(bars[:40], train_size=20, test_size=5)

    def test_requires_at_least_one_complete_fold(self):
        with self.assertRaisesRegex(ValueError, "no evaluable"):
            evaluate_neural_walk_forward(self.sample_bars(50), train_size=40, test_size=20)


if __name__ == "__main__":
    unittest.main()
